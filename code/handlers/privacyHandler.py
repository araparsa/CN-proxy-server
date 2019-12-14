# -*- coding: utf-8 -*-
# @Author: arman
# @Date:   2019-12-12 18:44:48
# @Last Modified by:   arman
# @Last Modified time: 2019-12-12 19:11:35
from parsers.httpParser import HttpParser

class PrivacyHandler():
	"""docstring for PrivacyHandler"""
	def __init__(self, config):
		self.config = config
	
	def setPrivacy(self, request):
		if (self.config["enable"] == False):
			return request
		return HttpParser.replaceUserAgent(request, self.config["userAgent"])	