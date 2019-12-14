# -*- coding: utf-8 -*-
# @Author: arman
# @Date:   2019-12-04 14:51:12
# @Last Modified by:   arman
# @Last Modified time: 2019-12-14 19:53:50

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
		self.logHandler = LogHandler(self.config["logging"])
		self.cacheHandler = CacheHandler(self.config["caching"])
		self.privacyHandler = PrivacyHandler(self.config["privacy"])
		self.restrictionHandler = RestrictionHandler(self.config["restriction"])
		self.accountingHandler = AccountingHandler(self.config["accounting"])

		signal.signal(signal.SIGINT, self.shutdown)
		
		#Create a TCP socket
		self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.logHandler.logCreateSocket()

		# Re-use the socket
		self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		# bind the socket to local host, and a port
		self.serverSocket.bind((HOST_NAME, self.config['port']))
		self.logHandler.logBindSocket(self.config['port'])
		self.serverSocket.listen() # become a server socket
		self.logHandler.logListen()

	def shutdown(self, event, frame):
		self.serverSocket.close()
		exit()
			
	def parseConfigFile(self):
		with open(CONFIG_FILE, 'r') as f:
			self.config = json.load(f)

	def handleIncomingRequests(self):
		while True:
			(clientSocket, clientAddress) = self.serverSocket.accept() 
			self.logHandler.logAcceptClientRequest()
			if(self.accountingHandler.hasCharge(clientAddress[0])):
				pass
			else:
				continue
			d = threading.Thread(name=clientAddress[0] + str(clientAddress[1]), 
							target = self.proxyThread, args=(clientSocket, clientAddress))
			d.setDaemon(True)
			d.start()
	
	def sendResponseToClient(self, response, clientSocket):
		self.logHandler.logProxySendDataToClient(response)
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
					self.logHandler.logBlockSendingDataToOutOfChargeClient()
					return None
				self.logHandler.logRecieveDataFromWebServer(data)
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
		serverIp = socket.gethostbyname(webServer)
		self.logHandler.logOpenConnectionToWebServer(webServer, serverIp)
		serverSocket.sendall(reqForWebServer)
		self.logHandler.logProxySentRequestToWebServer(reqForWebServer)

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
			self.logHandler.logCacheIsFresh()
			self.sendResponseToClient(cacheResponse, clientSocket)
			self.logHandler.logSendFromCache()
		else:
			if (cacheResponse == None): # not in cache
				self.logHandler.logNotInCache()
				serverSocket = self.sendReqToWebServer(incomingRequest)

				response = self.getResponseFromServer(serverSocket, clientAddress[0])
				isNoCache = HttpParser.noCache(HttpParser.getHeader(response[0]))
				if(not isNoCache): # pragma no cache in response header
					self.logHandler.logSaveInCache()
					self.cacheHandler.saveInCache(HttpParser.getUrl(incomingRequest), response)
					self.logHandler.logSaveDone()
					
				if(response == [] or response == None): #empty response or not enough charge
					return
				else:
					self.sendResponseToClient(response, clientSocket)

				

			else: # item in cache, check for freshness
				self.logHandler.logCheckForFreshness()
				response = self.checkFreshness(incomingRequest, cacheDate, clientAddress[0])

				if (response == None): # is fresh
					self.logHandler.logCacheIsFresh()
					self.logHandler.logSendFromCache()
					self.sendResponseToClient(cacheResponse, clientSocket)
					self.cacheHandler.hit(HttpParser.getUrl(incomingRequest), cacheResponse)

				elif(response == ""): # response is empty
					return

				else: # not fresh
					self.logHandler.logModified()
					self.sendResponseToClient(response, clientSocket)
					self.cacheHandler.hit(HttpParser.getUrl(incomingRequest), response)	

	def proxyThread(self, clientSocket, clientAddress):
		# get the request from browser
		try:
			incomingRequest = clientSocket.recv(200000) 
			if(len(incomingRequest) <= 0):
				return
			self.logHandler.logClientRequestToProxy(incomingRequest)

			restriction = self.restrictionHandler.checkForRestriction(HttpParser.getHost(incomingRequest))
			self.logHandler.logRestriction(restriction)
			if restriction == -1:
				return
			elif restriction == 0:
				pass
			else:
				time.sleep(restriction/1000)

			incomingRequest = self.privacyHandler.setPrivacy(incomingRequest)
			self.logHandler.logPrivacy()
			self.handleRequest(clientSocket, clientAddress, incomingRequest)

		except:
			pass 
	

def main():
	server = ProxyServer()  
	server.handleIncomingRequests()

if __name__ == '__main__':
	main()
