# -*- coding: utf-8 -*-
# @Author: arman
# @Date:   2019-12-08 22:25:52
# @Last Modified by:   arman
# @Last Modified time: 2019-12-09 13:37:49

import os 
# from logHandler import LogHandler

PATH = "./../cache/"
_TIME = 0
_CONTENT = 1
_RESPONSE = 2

class CacheHandler():
	"""docstring for CacheHandler"""
	def __init__(self, config, cache):
		self.setParams(config)
		self.cache = cache

	def setParams(self, config):
		cacheConfig = config["caching"]
		self.cacheEnable = False
		if (cacheConfig["enable"]):
			self.cacheEnable = True
		self.cacheSize = cacheConfig["size"]

	# def noCache(self, response):

	def timerUp(self):
		for item in self.cache:
			item[_TIME] += 1

	def saveContent(self, content, response):	
		self.timerUp()
		self.cache.append((0, content, response))

	def LRUReplace(self, content, response):
		lru = max(self.cache, key = lambda x: x[0])
		for item in self.cache:
			if (item[_TIME] == lru):
				self.cache.remove(item)
		self.saveContent(lru, response)

	def handleResponseCache(self, content, response):
		if(not self.cacheEnable):
			return 
		if (self.noCache(response)):
			return 

		if (len(self.cache) < 200):
			self.saveContent(response)
		else:
			self.LRUReplace(response)

	def hit(content):
		for item in self.cache:
			if(item[_CONTENT] == content):
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
	
