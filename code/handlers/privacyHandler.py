# -*- coding: utf-8 -*-
# @Author: arman
# @Date:   2019-12-12 18:44:48
# @Last Modified by:   arman
# @Last Modified time: 2019-12-12 19:11:35
from parsers.httpParser import HttpParser

class PrivacyHandler():
	"""docstring for PrivacyHandler"""
	
	def setPrivacy(self, config, request):
		if (config["enable"] == False):
			return request
		return HttpParser.replaceUserAgent(request, config["userAgent"])	