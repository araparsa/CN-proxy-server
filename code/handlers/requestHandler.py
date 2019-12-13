# -*- coding: utf-8 -*-
# @Author: arman
# @Date:   2019-12-04 17:04:52
# @Last Modified by:   arman
# @Last Modified time: 2019-12-09 18:09:27
from parsers.httpParser import HttpParser 

class RequestHandler:
	# def __init__(self, request):
	# 	self.requestLines = request.decode("utf-8").split('\n')  

	# def joinRequest(self):
	# 	return "\n".join(self.requestLines)

	def getWebServerSocketInfo(request):
		url = HttpParser.getUrl(request)
		http_pos = url.find("://") # find pos of ://
		if (http_pos==-1):
			temp = url
		else:
			temp = url[(http_pos+3):] # get the rest of url
		# print(self.requestLines)
		port_pos = temp.find(":") # find the port pos (if any)

		# find end of web server
		webserver_pos = temp.find("/")
		if webserver_pos == -1:
			webserver_pos = len(temp)

		webserver = ""
		port = -1
		if (port_pos==-1 or webserver_pos < port_pos): 
			# default port 
			port = 80 
			webserver = temp[:webserver_pos] 
		else: # specific port 
			port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
			webserver = temp[:port_pos] 
		return port, webserver 

	def prepareForWebServer(request):
		# print(request)
		request = HttpParser.changeHttpVersion(request)
		# print(request)
		request = HttpParser.removeHttpFromMessage(request)
		# print(request)
		# url = HttpParser.getUrl(request)
		request = HttpParser.changeAcceptEncoding(request)

		request = HttpParser.changeConnection(request)
		# content = HttpParser.getContent(request)
		request = HttpParser.replaceUrl(request)
		# print(request)
		request = HttpParser.removeProxyHeader(request)
		# print(request)
		return request 