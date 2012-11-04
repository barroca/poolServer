#!/usr/bin/python
# -*- coding: utf-8 -*-
import time 
import datetime

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.template
from threading import Lock
import bisect

from tornado.options import define, options
define("port", default=9999, help="run on the given port", type=int)

#this class stores a vote
class Vote:
	def __init__(self, vote1 =0, vote2=0, total=0, origin="", timeStamp=None):
		print "init vote"
		self.vote1 = vote1
		self.vote2 = vote2
		self.total = total
		#origin stores the random value used to identify where the vote came from
		self.origin = origin
		if(timeStamp == None):
			print "None"
			self.timeStamp = time.time()
		else:
			print timeStamp
			self.timeStamp = timeStamp
	#function to compare 2 Votes
	def __cmp__(self,other):
		a=0.0
		b=0.0
		try:
			a=self.timeStamp
		except:
			a=-1.0
		try:
			 b= other.timeStamp
		except:
			b=-1.0
		return cmp(a,b)
		
	
#this class is used to control values that have been sent.
class Control:
	def __init__(self):
		#keep track on values sent to send just delta votes 
		self.part1Sent=0
		self.part2Sent=0
		self.totalSent=0
		self.lock = Lock()
		self.scheduler = None
		self.ioLoop = None
#start time of process
		self.startTime = time.time()
		


class Statistics:
	def __init__(self):
		#list of votes received, used to get time statitics
		self.votes = []
		#count of last hour votes
		self.lastHourVotes = 0
		#helper values for last hour votes
		self.fistVoteTime = 0
		self.firsVoteValue = 0
		self.firstVoteIndex = -1
		self.lastVoteIndex = -1

		self.lock = Lock()
		#total of votes so far
		self.total =0
		self.vote1 = 0
		self.vote2 = 0
		
		#used to check if all different vote servers have sent their result
		self.servers = {}
		
		self.endVoting = 0
		#total at the end of voting
		self.endTotal = 0
		self.endVote1 = 0
		self.endVote2 = 0

	def addVote(self,vote):
		try:	
			self.lock.acquire()
			#check if we have add one value
			if(self.firstVoteIndex != -1):
				#check if the firstVote is older more than 1 hour from vote to be inserted
				while(vote.timeStamp-3600 > self.firstVoteTime and self.firstVoteIndex < self.lastVoteIndex):
					nextVote = self.votes[self.firstVoteIndex+1]
					self.lastHourVotes-=self.firstVoteValue
					self.firstVoteTime = nextVote.timeStamp
					self.firstVoteValue = nextVote.total
					self.firstVoteIndex += 1
				self.lastHourVotes+=vote.total
				self.lastVoteIndex = len(self.votes)
				self.votes.append(vote)
			else:
				#add the first value
				self.firstVoteIndex = 0
				self.lastVoteIndex = 0
				self.firstVoteValue = vote.total
				self.firstVoteTime = vote.timeStamp
				self.votes.append(vote)
				self.lastHourVotes +=vote.total
			self.total+=vote.total
			self.vote1+=vote.vote1
			self.vote2+=vote.vote2
			self.servers[vote.origin] = False
		except:
			print "houston we got a problem"
		finally:		
			self.lock.release()
	#get votes within a period of time		
	def getVotes(self,startTime = 0, endTime = 0):
		totalVotes = 0
		myList = []
		try:
			self.lock.acquire()
			if (startTime >= endTime or len(self.votes) == 0):
				return 0
		
			v1 = Vote(0,0,0,0,startTime)
			#use bisect to Find leftmost value greater than startTime
			startIndex = bisect.bisect_right(self.votes,v1)
			v2 = Vote(0,0,0,0,endTime)
			#Find rightmost value less than endTime
			endIndex = bisect.bisect_left(self.votes,v2)
			if (startIndex < 0 or endIndex > len(self.votes) or startIndex >= endIndex):
				return 0
			#get list
			myList = self.votes[startIndex:endIndex]
		finally:
			self.lock.release()
		#sum the values 
		for item in (myList):
			totalVotes +=item.total
		return totalVotes


	def getTotal(self):
		if (self.endVoting == len(self.servers)):
			return self.endTotal
		else:
			return self.total	

	def getVote1(self):			
		if (self.endVoting == len(self.servers)):
			return self.endVote1
		else:
			return self.vote1
	
	def getVote2(self):			
		if (self.endVoting == len(self.servers)):
			return self.endVote2
		else:
			return self.vote2


	def addEndVote(self,vote):
		try:
			self.lock.acquire()
			if (self.servers.has_key(vote.origin)):
				if(self.servers[vote.origin]==False):
					self.servers[vote.origin] = True
					self.endVoting +=1
					self.endTotal +=vote.total
					self.endVote1 +=vote.vote1
					self.endVote2 +=vote.vote2
				else:
					print "error, duplicated id, ignoring totalization vote"
			else:
				"first result received from this server is the end, please check if it's ok"
				self.servers[vote.origin] = True
				self.endVoting +=1
				self.endTotal +=vote.total
				self.endVote1 +=vote.vote1
				self.endVote2 +=vote.vote2
		finally:
			self.lock.release()
	

class StatisticsHandler(tornado.web.RequestHandler):
	'''if user get page show default voting page'''
	def get(self):
		loader = tornado.template.Loader("./templates")
		self.write(loader.load("stats.html").generate(total=myStats.getTotal(),vote1=myStats.getVote1(),vote2=myStats.getVote2(),lasthour = myStats.lastHourVotes))


class DateHandler(tornado.web.RequestHandler):
	'''if user get page show default voting page'''
	def get(self):
		loader = tornado.template.Loader("./templates")
		start = float(self.get_argument('startdate'))
		end = float(self.get_argument('enddate'))
		value = myStats.getVotes(start,end)
		self.write(loader.load("date.html").generate(startdate=start,enddate=end,count=value))


class PublishHandler(tornado.web.RequestHandler):
	'''if user get page show default voting page'''
	def get(self):
		loader = tornado.template.Loader("./templates")
		self.write(loader.load("empty.html").generate())
	def post(self):
		loader = tornado.template.Loader("./templates")
		total = int(self.get_argument('total'))
		part1 = int(self.get_argument('part1'))
		part2 = int(self.get_argument('part2'))
		end = int(self.get_argument('end'))
		myId = str(self.get_argument('id'))
		print total
		print part1
		print part2
		print end
		print myId
		vote = Vote(part1,part2,total,myId,time.time())
		if (end == 0):
			myStats.addVote(vote)
		else:
			myStats.addEndVote(vote)
		self.write("OK, vote received")

			
			
class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		loader = tornado.template.Loader("./templates")
		self.write(loader.load("empty.html").generate())



#page handlres
handlers=[ (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': './static'}),
            (r'/publish', PublishHandler),
            (r'/statistics', StatisticsHandler),
	    (r'/getDate', DateHandler),
	    (r'/', IndexHandler) ] 
	

#votes count class
myControl = Control()
myStats = Statistics()

if __name__ == "__main__":

	tornado.options.parse_config_file("./server.conf")
	tornado.options.parse_command_line()
	app = tornado.web.Application(handlers)
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(options.port)
	myControl.ioLoop =tornado.ioloop.IOLoop.instance()
	myControl.ioLoop.start()
