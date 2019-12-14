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

class CacheHandler():
	"""docstring for CacheHandler"""
	def __init__(self, config):
		self.setParams(config)
		self.cache = []

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
		del self.cache[i]

	def saveNewMessage(self, key, message):	
		gmtDatetime = datetime.fromtimestamp(mktime(gmtime()))
		item = cacheItem(key, gmtDatetime, HttpParser.getExpireDate(HttpParser.getHeader(message[0])), message)
		self.cache.append(item)	
	
	def LRUReplace(self, key, message):
		del self.cache[0]		
		self.saveNewMessage(key, message)

	def saveInCache(self, key, message):
		if(not self.cacheEnable):
			return 

		if (len(self.cache) < self.cacheSize):
			self.saveNewMessage(key, message)
		else:
			self.LRUReplace(key, message)


	def hit(self, key, response):
		self.remove(key)
		isNoCache = HttpParser.noCache(HttpParser.getHeader(response[0]))
		if(not isNoCache): # pragma no cache in response header
			self.saveNewMessage(self, key, response)

	def checkInCache(self, key):
		for i, item in enumerate(self.cache):
			if(item.key == key):
				if (item.expireDate != "" and item.expireDate > datetime.fromtimestamp(mktime(gmtime()))):
					return True, item.content, None
				return False, item.content, item.saveDate
		return False, None, None
	
class cacheItem():
	"""docstring for cacheItem"""
	def __init__(self, key, saveDate, expireDate, content):
		self.key = key 
		self.saveDate = saveDate
		self.expireDate = expireDate
		self.content = content
		