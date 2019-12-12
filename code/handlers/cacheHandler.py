# -*- coding: utf-8 -*-
# @Author: arman
# @Date:   2019-12-08 22:25:52
# @Last Modified by:   arman
# @Last Modified time: 2019-12-12 18:25:17

import os 
# from datetime import datetime as time
from time import gmtime, mktime 
from datetime import datetime
# from logHandler import LogHandler
from parsers.httpParser import HttpParser

PATH = "./../cache/"
# _TIME = 0
# _KEY = 1
# _RESPONSE = 2

class CacheHandler():
	"""docstring for CacheHandler"""
	def __init__(self, config, cache):
		self.setParams(config)
		self.cache = cache

	def setParams(self, config):
		self.cacheEnable = False
		if (config["enable"]):
			self.cacheEnable = True
		self.cacheSize = config["size"]


	def remove(self, key):
		for i, item in enumerate(self.cache):
			if item.key == key:
				index = i 
				break
		self.cache.remove(index)

	def saveNewMessage(self, key, message):	
		gmtDatetime = datetime.fromtimestamp(mktime(gmtime()))
		item = cacheItem(key, gmtDatetime, HttpParser.getExpireDate(HttpParser.getHeader(message)), message)
		self.cache.append(item)		
	
	def LRUReplace(self, key, message):
		
		self.cache.remove(0)
		self.saveNewMessage(key, message)

	def saveInCache(self, key, message):

		if(not self.cacheEnable):
			return 

		if (len(self.cache) < 200):
			self.saveNewMessage(key, message)
		else:
			self.LRUReplace(key, message)
		
		# print(len(self.cache))

	def hit(self, key, message):
		self.remove(key)
		self.saveNewMessage(self, key, message)

	def checkInCache(self, key):
		print("check in cache " + key)
		for i, item in enumerate(self.cache):
			print(i)
			if(item.key == key):
				print("exp date")
				print(item.expireDate)
				if (item.expireDate != "" and item.expireDate < gmtime()):
					print("r here")
					return True, item.content
				print("r heree")
				return False, item.saveDate
		print("r hereee")
		return False, None
	
class cacheItem():
	"""docstring for cacheItem"""
	def __init__(self, key, saveDate, expireDate, content):
		self.key = key 
		self.saveDate = saveDate
		self.expireDate = expireDate
		self.content = content
		