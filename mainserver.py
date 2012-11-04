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
define("port", default=9999, help="run on the given port", type=int)


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
	
class VoteTime:
	def __init__(self):
			
	

class StatisticsHandler(tornado.web.RequestHandler):
	'''if user get page show default voting page'''
	def get(self):
		self.write("Stats")


'''Handle user requests'''
class IndexHandler(tornado.web.RequestHandler):
	'''if user get page show default voting page'''
	def get(self):
		loader = tornado.template.Loader("./templates")
		self.write(loader.load("empty.html").generate())
	def post(self):
		loader = tornado.template.Loader("./templates")
		if myVotes.running:
			total = self.get_argument('total')
			part1 = self.get_argument('part1')
			part2 = self.get_argument('part2')
			end = self.get_argument('end')
			myId = self.get_argument('id')
			self.write(total)
			self.write(part1)
			self.write(part2)
			self.write(end)
			self.write(myId)
			print(total)
			



#page handlres
handlers=[ (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': './static'}),
            (r'/publish', IndexHandler),
            (r'/stat', StatisticsHandler) ] 
#votes count class
myVotes = Votes()
#start time of process
startTime = time.time()
#Timed out?
running = True
	
	
if __name__ == "__main__":

	tornado.options.parse_config_file("./server.conf")
	tornado.options.parse_command_line()
	app = tornado.web.Application(handlers)
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(options.port)
	myIoLoop =tornado.ioloop.IOLoop.instance()
	myIoLoop.start()
