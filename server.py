#!/usr/bin/python
# -*- coding: utf-8 -*-
import time 
import datetime

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.template
import urllib
import random
from recaptcha.client import captcha
from threading import Lock

from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)
define("enddate", default=1, help="run server until enddate", type=int)
define("mainserverurl", default="localhost", help="URL of the main server that sum the votes", type=str)
define("mainserverport", default=9999, help="Port to connect with the main server", type=int)
define("updateinterval", default=60, help="Interval, in seconds, which this server should send data to main server", type=int)

'''
Public key: 6LdOVtgSAAAAAG6ou3vioD8BwSHU-6D516RfYfGV
Private key: 6LdOVtgSAAAAAGqL3bP8X75Nk809MJiARDht8HPP 
'''
recaptcha_key='6LdOVtgSAAAAAGqL3bP8X75Nk809MJiARDht8HPP'

'''Count votes '''
class Votes:
	def __init__(self):
		self.part1=0
		self.part2=0
		self.total=0

		self.running=True
		
		'''
Since we will need to do simple operations, we will use simple-locks. 
We have chosen only one lock because we need to have the total votes consistent with the sum on part1 and part2.
		'''
		self.lock = Lock()
#vote for candidate 1
	def vote1(self):
		self.lock.acquire()
		try:
			self.part1+=1
			self.total+=1
		finally:
			'''
			If something went wrong, just release to lock.
			'''
    			self.lock.release() 
#vote for candidate 2
	def vote2(self):
		self.lock.acquire()
		try:
			self.part2+=1
			self.total+=1
		finally:
			'''
			If something went wrong, just release to lock.
			'''
    			self.lock.release() 
#read data 
	def get1(self):
		return self.part1
	def get2(self):
		return self.part2
	def getTotal(self):
		return self.total
	def getPercent(self,value,tot):
		#return percentage of a value in terms of total number of votes
		if(tot !=0):
			return round((float(value)/float(tot))*100.0)
		else:
			return 50.0
	def get1percent(self):
		return self.getPercent(self.part1,self.total)
	def get2percent(self):
		return self.getPercent(self.part2,self.total)
	
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
#myRandom is used to create uniq contact to mainServer, we can use the ip or url as this variable.
		self.myRandom = random.random()
		




'''Handle user requests'''
class IndexHandler(tornado.web.RequestHandler):
	'''if user get page show default voting page'''
	def get(self):
		loader = tornado.template.Loader("./templates")
		if myVotes.running:
			self.write(loader.load("index.html").generate(failMessage=""))
		else:
			self.write(loader.load("ended.html").generate(v1=int(myVotes.get1percent()),v2=int(myVotes.get2percent())))
	'''
if user post something check responses and show according page
the page javascript check if the user fill all the values
	'''
	def post(self):
		loader = tornado.template.Loader("./templates")
		if myVotes.running:
			challenge = self.get_argument('recaptcha_challenge_field')
			response = self.get_argument('recaptcha_response_field')
			vote  = self.get_argument('vote')
	
			'''check captcha'''
 			checkCaptchaResponse = captcha.submit( challenge, response, recaptcha_key, self.request.remote_ip)
			if checkCaptchaResponse.is_valid:  
				'''only update votes on valid answers'''
				if(vote == "1"):
					myVotes.vote1()
				if(vote == "2"):
					myVotes.vote2()
				self.write(loader.load("vote.html").generate(v=vote,v1=int(myVotes.get1percent()),v2=int(myVotes.get2percent())))
		 	else:
				'''if captcha is not valid show the default page with error message'''
				self.write(loader.load("index.html").generate(failMessage="Erro validando código, tente novamente"))
		else:
			self.write(loader.load("ended.html").generate(v1=int(myVotes.get1percent()),v2=int(myVotes.get2percent())))



#page handlres
handlers=[ (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': './static'}),
            (r'/', IndexHandler) ]
#votes count class
myVotes = Votes()
myControl = Control()

def endVoting():
	myVotes.running=False
	#get lock to prevent other 
	myVotes.lock.acquire()
	if sendData(myVotes.getTotal(),myVotes.get1(),myVotes.get2()):
		print "We have sent our result to the server"
	else:
		print "Problem sending data to the server"
	myVotes.lock.release()
	print "Ending vote server"
	#tornado.ioloop.IOLoop.instance().stop()
	myControl.scheduler.stop()
	
def sendData(total,part1,part2):
	end = 1
	if myVotes.running:
		end = 0
	params = {"total": total, "part1": part1, "part2": part2, "end": end, "id": myControl.myRandom}
	print params
	query = urllib.urlencode(params)
	url = "http://%s:%d/publish" % (options.mainserverurl, options.mainserverport)
	ret = False
	try:
		f = urllib.urlopen(url, query)
		contents = f.read()
		f.close()
		print contents
		ret = True
	except IOError:
		print "Problem sending data"
		ret = False
		
	return ret

def sendPartial():
	myVotes.lock.acquire()
	totalNow =myVotes.getTotal()
	part1Now =myVotes.get1()
	part2Now = myVotes.get2()  
	myVotes.lock.release()
	myControl.lock.acquire()
	#send only votes received on last updateinterval
	if sendData(totalNow-myControl.totalSent,part1Now-myControl.part1Sent,part2Now-myControl.part2Sent):
	#store total votes of this interval for next sendPartial
	
		myControl.part1Sent=part1Now
		myControl.part2Sent=part2Now
		myControl.totalSent=totalNow
	myControl.lock.release()

if __name__ == "__main__":

	tornado.options.parse_config_file("./server.conf")
	tornado.options.parse_command_line()
	app = tornado.web.Application(handlers)
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(options.port)
	myControl.ioLoop =tornado.ioloop.IOLoop.instance()
	myControl.ioLoop.add_timeout(options.enddate,endVoting)
	myControl.scheduler = tornado.ioloop.PeriodicCallback(sendPartial,(options.updateinterval*1000))
	myControl.scheduler.start()
	if options.enddate > myControl.startTime:
		myControl.ioLoop.start()
	else:
		print "End Date of server is lower than starttime, exiting."
