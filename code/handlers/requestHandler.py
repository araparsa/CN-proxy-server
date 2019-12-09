# -*- coding: utf-8 -*-
# @Author: arman
# @Date:   2019-12-04 17:04:52
# @Last Modified by:   arman
# @Last Modified time: 2019-12-09 13:18:58

class RequestHandler():
	def __init__(self, request):
		self.requestLines = request.decode("utf-8").split('\n')  

	def joinRequest(self):
		return "\n".join(self.requestLines)

	def getWebServerSocketInfo(self):
		url = self.requestLines[0].split(' ')[1]
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

	def removeHttpFromUrl(self):
		http_pos = self.requestLines[0].find("://") # find pos of ://
		# delete http:// if exists
		first_space_pos = self.requestLines[0].find(" ")
		if (http_pos!=-1):
			print("before: ", self.requestLines[0])
			self.requestLines[0] = self.requestLines[0].replace(self.requestLines[0][first_space_pos+1:http_pos+3], "")
			print("after: ", self.requestLines[0])
	
	def changeHttpVersion(self):
		self.requestLines[0] = self.requestLines[0].replace("HTTP/1.1", "HTTP/1.0") #change version of http
	
	def getUrl(self):
		return self.requestLines[0].split(" ")[1] #get url 

	def getContent(self, url):

		slash_pos = url.find("/")

		if(slash_pos == -1):
			content = "/"
		else:
			content = url[slash_pos:]

		return content

	def prepareForWebServer(self):
		self.changeHttpVersion()
		self.removeHttpFromUrl()
		url = self.getUrl()
		content = self.getContent(url)
		self.requestLines[0] = self.requestLines[0].replace(url, content)
		for i, requestLine in enumerate(self.requestLines):
			if(requestLine[0:16] == "Proxy-Connection"):
				del self.requestLines[i]
				break