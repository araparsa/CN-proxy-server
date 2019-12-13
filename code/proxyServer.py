# -*- coding: utf-8 -*-
# @Author: arman
# @Date:   2019-12-04 14:51:12
# @Last Modified by:   arman
# @Last Modified time: 2019-12-12 18:49:40

import socket
import signal
import json 
import threading 
from handlers.requestHandler import RequestHandler
from handlers.logHandler import LogHandler 
from handlers.cacheHandler import CacheHandler 
from handlers.privacyHandler import PrivacyHandler
from parsers.httpParser import HttpParser

CONFIG_FILE = "./../files/config.json"
HOST_NAME = "0.0.0.0"

class ProxyServer():
	"""docstring for ProxyServer"""
	
	def __init__(self):
		self.parseConfigFile()
		self.logHandler = LogHandler(self.config["logging"])
		self.cache = []
		self.cacheHandler = CacheHandler(self.config["caching"], self.cache)
		self.privacyHandler = PrivacyHandler()
		signal.signal(signal.SIGINT, self.shutdown)
		
		#Create a TCP socket
		self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.logHandler.log("Creating server socket...")

		# Re-use the socket
		self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		# bind the socket to local host, and a port   
		# print(self.config['port'])
		self.serverSocket.bind((HOST_NAME, self.config['port']))
		self.logHandler.log("Binding socket to port " + str(self.config['port']) + "...")
		
		self.serverSocket.listen() # become a server socket
		self.logHandler.log("Listening for incoming requests...\n")

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
			self.logHandler.log("Accepted a request from client!")
			d = threading.Thread(name=clientAddress[0] + str(clientAddress[1]), 
							target = self.proxyThread, args=(clientSocket, clientAddress))
			d.setDaemon(True)
			d.start()
	
	# def sendResponseToClient(self, response, clientSocket):
	# 	# print("in function")
	# 	dataHeader = HttpParser.getHeader(response)
	# 	self.logHandler.log("Proxy sent response to client with headers:\n" + dataHeader.decode(errors="ignore").rstrip("\r\n"))
	# 	try:
	# 		clientSocket.sendall(response) # send to browser/client
	# 	except:
	# 		pass

	# def recieveDataFromWebServer(self, serverSocket, clientSocket):
	# 	while 1:
	# 		# receive data from web server
	# 		try:
	# 			data = serverSocket.recv(2048)
	# 			if (len(data) > 0):
	# 				# dataHeader = HttpParser.getHeader(data)
	# 				# self.logHandler.log("Server sent response to proxy with headers:\n" + dataHeader.decode(errors="ignore").rstrip("\r\n"))
	# 				clientSocket.sendall(data)
	# 				# self.logHandler.log("proxy sent response to client with headers:\n" + dataHeader.decode(errors="ignore").rstrip("\r\n"))
	# 			else:
	# 				break
	# 		except:
	# 			pass
	# 	return

	def sendReqToWebServer(self, request, clientSocket):
		# print("sending to web server")
		port, webServer = RequestHandler.getWebServerSocketInfo(request)
		reqForWebServer = RequestHandler.prepareForWebServer(request)
		# reqUrl = HttpParser.getUrl(request)
		serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		serverSocket.settimeout(1000)
		serverSocket.connect((webServer, port))
		self.logHandler.log("Proxy opening connection to server " + webServer + "[ip-address]" + "... Connection opened.")
		serverSocket.sendall(reqForWebServer)
		self.logHandler.log("Proxy sent request to server with headers:\n" + 
				"\n".join(HttpParser.decode(reqForWebServer)).rstrip("\r\n"))	

		while 1:
			# receive data from web server
			try:
				data = serverSocket.recv(2048)
				if (len(data) > 0):
					# dataHeader = HttpParser.getHeader(data)
					# self.logHandler.log("Server sent response to proxy with headers:\n" + dataHeader.decode(errors="ignore").rstrip("\r\n"))
					clientSocket.sendall(data)
					# self.logHandler.log("proxy sent response to client with headers:\n" + dataHeader.decode(errors="ignore").rstrip("\r\n"))
				else:
					break
			except:
				pass
		# return	
		return serverSocket			
		
	def checkFreshness(self, request, date):
		# print("in check")
		# print(date)
		request = HttpParser.addIfModified(request, date)
		# print("after")
		serverSocket = self.sendReqToWebServer(request)
		serverResponse = self.recieveDataFromWebServer(serverSocket)
		if (HttpParser.isModified(serverResponse)):
			return serverResponse
		else:
			return None

	def proxyThread(self, clientSocket, clientAddress):
		# get the request from browser
		# print("in proxy thread!!")
		try:
			# print("in try")
			incomingRequest = clientSocket.recv(2048) 
			print(incomingRequest)
			incomingRequest = self.privacyHandler.setPrivacy(self.config["privacy"], incomingRequest)
			# print("hello")
			self.logHandler.log("Client sent request to proxy with headers:")
			self.logHandler.log("connect to [] from localhost [] 58449\n")
			self.logHandler.log("\n----------------------------------------------------------------------\n" + incomingRequest.decode("utf-8").rstrip("\r\n") + 
					"\n----------------------------------------------------------------------\n")
			# isNoCache = HttpParser.noCache(incomingRequest)
			isNoCache = False
			if (isNoCache):
				# print("is nocache!!!")
				serverSocket = self.sendReqToWebServer(incomingRequest, clientSocket)
				data = self.recieveDataFromWebServer(serverSocket, clientSocket)
				# self.cacheHandler.saveInCache(HttpParser.getUrl(incomingRequest), data)
				self.sendResponseToClient(data, clientSocket)

			else:
				# print(incomingRequest)
				# print("not pragma no cache")
				# cacheHit, cacheResponse = self.cacheHandler.checkInCache(HttpParser.getUrl(incomingRequest))
				cacheHit = False
				cacheResponse = None
				# print(cacheHit)
				# print(cacheResponse)
				# print(cacheResponse)
				if (cacheHit): # cache item is fresh 
					clientSocket.sendall(cacheResponse)
				else:
					if (cacheResponse == None): # not in cache
						# print("not in cache")
						# print(incomingRequest)
						serverSocket = self.sendReqToWebServer(incomingRequest, clientSocket)
						# print("before data")
						# data = self.recieveDataFromWebServer(serverSocket, clientSocket)
						# print("after data")
						# print(data)
						# self.cacheHandler.saveInCache(HttpParser.getUrl(incomingRequest), data)
						# print("after")
						# self.sendResponseToClient(data, clientSocket)
						# print("after send")
					else: # item in cache, check for freshness
						# print("in cache!!")
						data = self.checkFreshness(incomingRequest, cacheResponse)
						# print("after data freshness")
						if (data == None): # is fresh
							# print("is fresh")
							self.sendResponseToClient(cacheResponse, clientSocket)
							self.cacheHandler.hit(HttpParser.getUrl(incomingRequest), cacheResponse)
						else: # not fresh
							# print("not fresh")
							self.sendResponseToClient(data, clientSocket)
							self.cacheHandler.hit(HttpParser.getUrl(incomingRequest), data)	
		except:
			pass 
	

def main():
	server = ProxyServer()  
	server.handleIncomingRequests()

if __name__ == '__main__':
	main()
