# -*- coding: utf-8 -*-
# @Author: arman
# @Date:   2019-12-06 19:43:54
# @Last Modified by:   arman
# @Last Modified time: 2019-12-08 22:22:44
from datetime import datetime as time 

class LogHandler():
	"""docstring for Log"""
	def __init__(self, config):
		self.config = config

	def log(self, message):
		f = open(self.logFile, "a")
		f.write(time.now().strftime("[%d/%b/%Y:%H:%M:%S] ") + message + "\n")
		f.close()

	def startLogging(self):
		# print(self.config["logging"]["enable"], self.config["logging"]["logFile"])
		logConfig = self.config["logging"]
		if (not logConfig["enable"]):
			print("Logging is not enable, so there is not any log file for the server activities! set it to enable if you want to have log file.\n")
			return 
		else:
			if (logConfig["logFile"] != ""):
				print("log file exists already")
				self.logFile = "./../files/" + logConfig["logFile"]
				
			else:
				print("creating log file...")
				f = open("./../files/logFile.log", "w")
				f.close()
				self.logFile = "./../files/logFile.log"

			self.log("Proxy launched")