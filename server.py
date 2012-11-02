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
define("duration", default=100000, help="run server for period of seconds", type=int)
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
	


'''Handle user requests'''
class IndexHandler(tornado.web.RequestHandler):
	'''if user get page show default voting page'''
	def get(self):
		loader = tornado.template.Loader("./templates")
		print myVotes.running
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
#start time of process
startTime = time.time()
#Timed out?
running = True
#myRandom is used to create uniq contact to mainServer, we can use the ip or url as this variable.
myRandom = random.random()
def endVoting():
	myVotes.running=False
	#get lock to prevent other 
	myVotes.lock.aquire()
	sendData(myVotes.getTotal(),myVotes.get1(),myVotes.get2())
	
def sendData(total,part1,part2):
	end = 0
	if myVotes.running:
		end = 1
	params = {"total": total, "part1": part1, "part2": part2, "end": end, "id": myRandom}
	query = urllib.urlencode(params)
	url = "http://%s:%d/publish" % (options.mainserverurl, options.mainserverport)
	f = urllib.urlopen(url, query)
	contents = f.read()
	f.close()
	print contents

def sendPartial():
	sendData(myVotes.getTotal(),myVotes.get1(),myVotes.get2())
	
if __name__ == "__main__":

	tornado.options.parse_config_file("./server.conf")
	tornado.options.parse_command_line()
	app = tornado.web.Application(handlers)
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(options.port)
	myIoLoop =tornado.ioloop.IOLoop.instance()
	myIoLoop.add_timeout(startTime+(options.duration),endVoting)
	tornado.ioloop.PeriodicCallback(sendPartial,(options.updateinterval*1000)).start()
	myIoLoop.start()
