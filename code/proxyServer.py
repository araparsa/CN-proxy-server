# -*- coding: utf-8 -*-
# @Author: arman
# @Date:   2019-12-04 14:51:12
# @Last Modified by:   arman
# @Last Modified time: 2019-12-12 18:49:40

import socket
import signal
import json 
import threading 
import time
from handlers.requestHandler import RequestHandler
from handlers.logHandler import LogHandler 
from handlers.cacheHandler import CacheHandler 
from handlers.privacyHandler import PrivacyHandler
from handlers.restrictionHandler import RestrictionHandler
from handlers.accountingHandler import AccountingHandler
from parsers.httpParser import HttpParser

CONFIG_FILE = "./../files/config.json"
HOST_NAME = "127.0.0.1"

class ProxyServer():
	"""docstring for ProxyServer"""
	
	def __init__(self):
		self.parseConfigFile()
		# self.logHandler = LogHandler(self.config["logging"])
		self.cacheHandler = CacheHandler(self.config["caching"])
		self.privacyHandler = PrivacyHandler(self.config["privacy"])
		self.restrictionHandler = RestrictionHandler(self.config["restriction"])
		self.accountingHandler = AccountingHandler(self.config["accounting"])

		signal.signal(signal.SIGINT, self.shutdown)
		
		#Create a TCP socket
		self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# self.logHandler.log("Creating server socket...")

		# Re-use the socket
		self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		# bind the socket to local host, and a port
		self.serverSocket.bind((HOST_NAME, self.config['port']))
		# self.logHandler.log("Binding socket to port " + str(self.config['port']) + "...")
		
		self.serverSocket.listen() # become a server socket
		# self.logHandler.log("Listening for incoming requests...\n")

	def shutdown(self, event, frame):
		self.serverSocket.close()
		exit()
			
	def parseConfigFile(self):
		with open(CONFIG_FILE, 'r') as f:
			self.config = json.load(f)

	def handleIncomingRequests(self):
		while True:
			# Establish the connection
			(clientSocket, clientAddress) = self.serverSocket.accept() 
			if(self.accountingHandler.hasCharge(clientAddress[0])):
				pass
			else:
				continue
			# self.logHandler.log("Accepted a request from client!")
			d = threading.Thread(name=clientAddress[0] + str(clientAddress[1]), 
							target = self.proxyThread, args=(clientSocket, clientAddress))
			d.setDaemon(True)
			d.start()
	
	def sendResponseToClient(self, response, clientSocket):
		# self.logHandler.log("Proxy sent response to client with headers:\n" + dataHeader.decode(errors="ignore").rstrip("\r\n"))
		for item in response:
			clientSocket.send(item)

	def getResponseFromServer(self, serverSocket, clientIP):
		firstTime = True
		fullData = []
		while 1:
			# receive data from web server
			data = serverSocket.recv(200000)
			if (len(data) > 0):
				if(self.accountingHandler.hasEnoughCharge(clientIP, len(data)) == False):
					return None
				fullData.append(data)
			else:
				break
		return fullData

	def sendReqToWebServer(self, request):
		port, webServer = RequestHandler.getWebServerSocketInfo(request)
		reqForWebServer = RequestHandler.prepareForWebServer(request)
		serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		serverSocket.settimeout(10)
		serverSocket.connect((webServer, port))
		# self.logHandler.log("Proxy opening connection to server " + webServer + "[ip-address]" + "... Connection opened.")
		serverSocket.sendall(reqForWebServer)
		# self.logHandler.log("Proxy sent request to server with headers:\n" + 
				# "\n".join(HttpParser.decode(reqForWebServer)).rstrip("\r\n"))	

		return serverSocket			
		
	def checkFreshness(self, request, date, clientIP):
		request = HttpParser.addIfModified(request, date)

		serverSocket = self.sendReqToWebServer(request)

		response = self.getResponseFromServer(serverSocket, clientIP)
		if(response == [] or response == None): #empty response or not enouph charge
			return ""
		else:
			if (HttpParser.isModified(response[0])):
				return response
			else:
				return None

	def handleRequest(self, clientSocket, clientAddress, incomingRequest):
		cacheHit, cacheResponse, cacheDate = self.cacheHandler.checkInCache(HttpParser.getUrl(incomingRequest))

		if (cacheHit): # cache item is fresh 
			self.sendResponseToClient(cacheResponse, clientSocket)
		else:
			if (cacheResponse == None): # not in cache
				serverSocket = self.sendReqToWebServer(incomingRequest)

				response = self.getResponseFromServer(serverSocket, clientAddress[0])
				if(response == [] or response == None): #empty response or not enouph charge
					return
				else:
					self.sendResponseToClient(response, clientSocket)

				isNoCache = HttpParser.noCache(HttpParser.getHeader(response[0]))
				if(not isNoCache): # pragma no cache in response header
					self.cacheHandler.saveInCache(HttpParser.getUrl(incomingRequest), response)

			else: # item in cache, check for freshness
				response = self.checkFreshness(incomingRequest, cacheDate, clientAddress[0])

				if (response == None): # is fresh
					self.sendResponseToClient(cacheResponse, clientSocket)
					self.cacheHandler.hit(HttpParser.getUrl(incomingRequest), cacheResponse)

				elif(response == ""): # response is empty
					return

				else: # not fresh
					self.sendResponseToClient(response, clientSocket)
					self.cacheHandler.hit(HttpParser.getUrl(incomingRequest), response)	

	def proxyThread(self, clientSocket, clientAddress):
		# get the request from browser
		try:
			incomingRequest = clientSocket.recv(200000) 
			if(len(incomingRequest) <= 0):
				return

			restriction = self.restrictionHandler.checkForRestriction(HttpParser.getHost(incomingRequest))
			if restriction == -1:
				return
			elif restriction == 0:
				pass
			else:
				time.sleep(restriction/1000)

			incomingRequest = self.privacyHandler.setPrivacy(incomingRequest)

			self.handleRequest(clientSocket, clientAddress, incomingRequest)
			# self.logHandler.log("Client sent request to proxy with headers:")
			# self.logHandler.log("connect to [] from localhost [] 58449\n")
			# self.logHandler.log("\n----------------------------------------------------------------------\n" + incomingRequest.decode("utf-8").rstrip("\r\n") + 
					# "\n----------------------------------------------------------------------\n")
		except:
			pass 
	

def main():
	server = ProxyServer()  
	server.handleIncomingRequests()

if __name__ == '__main__':
	main()
