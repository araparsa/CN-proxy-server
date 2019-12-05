# -*- coding: utf-8 -*-
# @Author: arman
# @Date:   2019-12-04 17:04:52
# @Last Modified by:   arman
# @Last Modified time: 2019-12-04 19:25:48

class Request():
	def __init__(self, request):
		self.requestLines = request.decode("utf-8").split('\n')  
	
	def getRequest(self):
		return "\n".join(self.requestLines)

	def getWebServerSocketInfo(self):
		url = self.requestLines[0].split(' ')[1]
		http_pos = url.find("://") # find pos of ://
		if (http_pos==-1):
			temp = url
		else:
			temp = url[(http_pos+3):] # get the rest of url

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

	def prepareForWebServer(self):
		firstLine = self.requestLines[0].replace("HTTP/1.1", "HTTP/1.0") #change version of http
		http_pos = firstLine.find("://") # find pos of ://
		# delete http:// if exists
		first_space_pos = firstLine.find(" ")
		if (http_pos==-1):
			firstLine = firstLine
		else:
			firstLine = firstLine.replace(firstLine[first_space_pos+1:http_pos+3], "")
		url = firstLine.split(" ")[1] #get url 
		slash_pos = url.find("/")

		if(slash_pos == -1):
			firstLine = firstLine.replace(url, "/")

		else:
			firstLine = firstLine.replace(url, url[slash_pos:])

		self.requestLines[0] = firstLine

		for i, requestLine in enumerate(self.requestLines):
			if(requestLine[0:16] == "Proxy-Connection"):
				del self.requestLines[i]
				break
		# print(self.requestLines)