# -*- coding: utf-8 -*-
# @Author: arman
# @Date:   2019-12-08 22:25:52
# @Last Modified by:   arman
# @Last Modified time: 2019-12-09 19:30:17

import os 
# from logHandler import LogHandler
from parsers.httpParser import HttpParser

PATH = "./../cache/"
_TIME = 0
_KEY = 1
_RESPONSE = 2

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

	# def noCache(self, response):

	def timerUp(self):
		for item in self.cache:
			item[_TIME] += 1

	def saveMessage(self, key, message):	
		self.timerUp()
		self.cache.append([0, key, message])

	def LRUReplace(self, cKey, message):
		lru = max(self.cache, key = lambda x: x[0])
		for item in self.cache:
			if (item[_TIME] == lru):
				self.cache.remove(item)
		self.saveMessage(cKey, message)

	def saveInCache(self, key, message, noCache):
		
		if (noCache):
			return 
		if(not self.cacheEnable):
			return 

		if (len(self.cache) < 200):
			self.saveMessage(key, message)
		else:
			self.LRUReplace(key, message)
		print(len(self.cache))

	def hit(content):
		for item in self.cache:
			if(item[_KEY] == content):
				item[_TIME] = 0 
		self.timerUp()

	def checkInCache(self, content):
		print("cache: " + content)
		for item in self.cache:
			if(content in item):
				self.hit(content)
				return "Hit", self.cache[item, 2]
		# cache miss occured
		return "Miss", []
	
