# -*- coding: utf-8 -*-
# @Author: arman
# @Date:   2019-12-04 14:51:12
# @Last Modified by:   arman
# @Last Modified time: 2019-12-06 20:54:57

import socket
import signal
import json 
import threading 
from request import Request
from log import Log 

CONFIG_FILE = "./../files/config.json"
HOST_NAME = "0.0.0.0"

class ProxyServer():
	"""docstring for ProxyServer"""
	
	def __init__(self):
		self.parseConfigFile()
		self.logHandler = Log(self.config)
		self.logHandler.startLogging()
		signal.signal(signal.SIGINT, self.shutdown)
		
		#Create a TCP socket
		self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.logHandler.log("Creating server socket...")

		# Re-use the socket
		self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		# bind the socket to local host, and a port   
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
		
	def proxyThread(self, clientSocket, clientAddress):
		# get the request from browser
		incomingRequest = clientSocket.recv(2048) 
		self.logHandler.log("Client sent request to proxy with headers:" + incomingRequest.decode("utf-8"))
		request = Request(incomingRequest)
		port, webServer = request.getWebServerSocketInfo()
		# print(request.requestLines)
		request.prepareForWebServer()
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		s.settimeout(10000)
		s.connect((webServer, port))
		self.logHandler.log("Proxy opening connection to server " + webServer + "[ip-address]" + "... Connection opened.")
		s.sendall(str.encode(request.joinRequest()))
		self.logHandler.log("Proxy sent request to server with headers:" + "<headers>")

		while 1:
			# receive data from web server
			data = s.recv(2048)
			self.logHandler.log("Server sent response to proxy with headers:" + "<headers>")
			if (len(data) > 0):
				clientSocket.send(data) # send to browser/client
				self.logHandler.log("Proxy sent response to client with headers:" + "<headers>")
			else:
				break

def main():
	server = ProxyServer()  
	server.handleIncomingRequests()

if __name__ == '__main__':
	main()
