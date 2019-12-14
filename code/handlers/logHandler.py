# -*- coding: utf-8 -*-
# @Author: arman
# @Date:   2019-12-06 19:43:54
# @Last Modified by:   arman
# @Last Modified time: 2019-12-14 20:23:55
from datetime import datetime as time 
from parsers.httpParser import HttpParser 

_DIVIDER = "\n=======================================================\n"

class LogHandler():
	"""docstring for Log"""
	def __init__(self, config):
		self.startLogging(config)

	def log(self, message):
		f = open(self.logFile, "a")
		f.write(time.now().strftime("[%d/%b/%Y:%H:%M:%S] ") + message + "\n")
		f.close()

	def startLogging(self, config):

		if (not config["enable"]):
			print("Logging is not enable, so there is not any log file for the server activities! set it to enable if you want to have log file.\n")
			return 
		else:
			if (config["logFile"] != ""):
				self.logFile = "./../files/" + config["logFile"]
				
			else:
				self.logFile = "./../files/logFile.log"

			self.log("Proxy launched")

	def logCreateSocket(self):
		self.log("Creating server socket...")

	def logBindSocket(self, port):
		self.log("Binding socket to port " + str(port) + "...")

	def logListen(self):
		self.log("Listening for incoming requests...\n")

	def logAcceptClientRequest(self):
		self.log("Accepted a request from client!")

	def logBlockOutOfChargeClient(self):
		self.log("Connection closed by proxy server due to out of charge client!")

	def logClientRequestToProxy(self, message):
		header = HttpParser.getHeader(message)
		if header == None:
			return
		header = header.decode(errors="ignore").rstrip("\r\n")
		self.log("Client sent request to proxy with headers:\n")
		self.log(_DIVIDER + header + _DIVIDER)	

	def logRestriction(self, status):
		if status == -1:
			self.log("Webpage is in black list! Proxy server blocked the connection!")
		elif status!=0:
			self.log("Webpage is restricted! Proxy server restricted the connection with " + str(status/1000) + " seconds delay")

	def logPrivacy(self):
		self.log("Privacy set for the connection!")

	def logSaveInCache(self):
		self.log("Saving response in cache...")

	def logSaveDone(self):
		self.log("Saving done!")

	def logOpenConnectionToWebServer(self, webServer, ip):
		self.log("Proxy opening connection to server " + webServer + " [" + str(ip) + "]" + "... Connection opened.")

	def logProxySentRequestToWebServer(self, message):
		header = HttpParser.getHeader(message)
		if header == None:
			return
		header = header.decode(errors="ignore").rstrip("\r\n")
		self.log(" Proxy sent request to server with headers:\n")
		self.log(_DIVIDER + header + _DIVIDER)	

	def logRecieveDataFromWebServer(self, message):
		header = HttpParser.getHeader(message)
		if header == None:
			return
		# print("got header")
		# print(header)
		header = header.decode(errors="ignore").rstrip("\r\n")
		self.log("Server sent response to proxy with headers:\n")
		self.log(_DIVIDER + header + _DIVIDER)	
		# print("logged")

	def logProxySendDataToClient(self, message):
		header = HttpParser.getHeader(message)
		if header == None:
			return
		header = header.decode(errors="ignore").rstrip("\r\n")
		self.log("Proxy sent response to client with headers:\n")
		self.log(_DIVIDER + header + _DIVIDER)	

	def logBlockSendingDataToOutOfChargeClient(self):
		self.log("Client does not have enough charge to recieve the object!")

	def logCacheIsFresh(self):
		self.log("Object is in cache and is fresh. Sending from cache to client...")

	def logSendFromCache(self):
		self.log("Object sent to client from cache!")

	def logNotInCache(self):
		self.log("Object is not in cache. Forwarding the request to web server.")

	def logCheckForFreshness(self):
		self.log("Object is in cache. Checking for freshness...")

	def logModified(self):
		self.log("Object is modified. Sending the new version from web server to client.")
