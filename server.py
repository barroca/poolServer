#!/usr/bin/python
# -*- coding: utf-8 -*-
import time 
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.template
from recaptcha.client import captcha

from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)
define("duration", default=100000, help="run server for period of seconds", type=int)
tornado.options.parse_command_line()
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
	def vote1(self):
		self.part1+=1
		self.total+=1
	def vote2(self):
		self.part2+=1
		self.total+=1
	def get1(self):
		return self.part1
	def get2(self):
		return self.part2
	def getTotal(self):
		return self.total
	def getPercent(self,value):
		if(self.total !=0):
			return round((float(value)/float(self.total))*100.0)
		else:
			return 50.0
	def get1percent(self):
		return self.getPercent(self.part1)
	def get2percent(self):
		return self.getPercent(self.part2)
	


'''Handle user requests'''
class IndexHandler(tornado.web.RequestHandler):
	'''if user get page show default voting page'''
	def get(self):
		loader = tornado.template.Loader("./templates")
		self.write(loader.load("index.html").generate(failMessage=""))

	'''
if user post something check responses and show according page
the page javascript check if the user fill all the values
	'''
	def post(self):
		challenge = self.get_argument('recaptcha_challenge_field')
		response = self.get_argument('recaptcha_response_field')
		vote  = self.get_argument('vote')

		'''check captcha'''
 		checkCaptchaResponse = captcha.submit( challenge, response, recaptcha_key, self.request.remote_ip)
		if checkCaptchaResponse.is_valid:  

			loader = tornado.template.Loader("./templates")
			'''only update votes on valid answers'''
			if(vote == "1"):
				myVotes.vote1()
			if(vote == "2"):
				myVotes.vote2()
			self.write(loader.load("vote.html").generate(v=vote,v1=int(myVotes.get1percent()),v2=int(myVotes.get2percent())))
	 	else:
			'''if captcha is not valid show the default page with error message'''
			loader = tornado.template.Loader("./templates")
			self.write(loader.load("index.html").generate(failMessage="Erro validando código, tente novamente"))


handlers=[ (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': './static'}),
            (r'/', IndexHandler) ]
myVotes = Votes()
startTime = time.localtime()
print options.duration 
if __name__ == "__main__":
	tornado.options.parse_command_line()
	app = tornado.web.Application(handlers)
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
