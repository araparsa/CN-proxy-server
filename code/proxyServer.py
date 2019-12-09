# -*- coding: utf-8 -*-
# @Author: arman
# @Date:   2019-12-04 14:51:12
# @Last Modified by:   arman
# @Last Modified time: 2019-12-09 19:42:46

import socket
import signal
import json 
import threading 
from handlers.requestHandler import RequestHandler
from handlers.logHandler import LogHandler 
from handlers.cacheHandler import CacheHandler 
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
		# self.__clients = {}

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
	
	def sendReqToWebServer(self, request, clientSocket):
		port, webServer = RequestHandler.getWebServerSocketInfo(request)
		reqForWebServer = RequestHandler.prepareForWebServer(request)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		s.settimeout(1000)
		s.connect((webServer, port))
		self.logHandler.log("Proxy opening connection to server " + webServer + "[ip-address]" + "... Connection opened.")
		s.sendall(reqForWebServer)
		self.logHandler.log("Proxy sent request to server with headers:\n" + 
				"\n".join(HttpParser.decode(reqForWebServer)).rstrip("\r\n"))
		
		while 1:
			# receive data from web server
			try:
				data = s.recv(1024)
				if (len(data) > 0):
					dataHeader = HttpParser.getHeader(data)
					if dataHeader != None:
						self.logHandler.log("Server sent response to proxy with headers:\n" + dataHeader.decode(errors="ignore").rstrip("\r\n"))
						self.cacheHandler.saveInCache(data, HttpParser.getUrl(data), HttpParser.noCache(dataHeader))
						self.logHandler.log("Proxy sent response to client with headers:\n" + dataHeader.decode(errors="ignore").rstrip("\r\n"))
					clientSocket.send(data) # send to browser/client
				else:
					break
			except:
				pass
				
	
	def proxyThread(self, clientSocket, clientAddress):
		# get the request from browser
		try:
			incomingRequest = clientSocket.recv(1024) 
			self.logHandler.log("Client sent request to proxy with headers:")
			self.logHandler.log("connect to [] from localhost [] 58449\n")
			self.logHandler.log("\n----------------------------------------------------------------------\n" + incomingRequest.decode("utf-8").rstrip("\r\n") + 
					"\n----------------------------------------------------------------------\n")

			self.sendReqToWebServer(incomingRequest, clientSocket)
		except:
			pass 
	

def main():
	server = ProxyServer()  
	server.handleIncomingRequests()

if __name__ == '__main__':
	main()
