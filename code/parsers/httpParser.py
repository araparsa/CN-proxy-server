# -*- coding: utf-8 -*-
# @Author: arman
# @Date:   2019-12-09 13:49:10
# @Last Modified by:   arman
# @Last Modified time: 2019-12-09 19:35:15

class HttpParser:
	"""docstring for HttpParser"""

	def decode(message):
		return (message.decode(errors="ignore").split('\n'))  

	def encode(lines):
		return (str.encode("\n".join(lines)))
	
	def removeHttpFromMessage(message):
		messageLines = HttpParser.decode(message)
		http_pos = messageLines[0].find("://") # find pos of ://
		# delete http:// if exists
		first_space_pos = messageLines[0].find(" ")
		if (http_pos==-1):
			pass
		else:
			messageLines[0] = messageLines[0].replace(messageLines[0][first_space_pos+1:http_pos+3], "")
		return (HttpParser.encode(messageLines))

	def changeHttpVersion(message):
		messageLines = HttpParser.decode(message)
		messageLines[0] = messageLines[0].replace("HTTP/1.1", "HTTP/1.0") #change version of http
		return (HttpParser.encode(messageLines))

	def getUrl(message):
		messageLines = HttpParser.decode(message)
		try:
			return (messageLines[0].split(" ")[1]) #get url 
		except:
			pass

	def getContent(message):
		url = HttpParser.getUrl(message)
		slash_pos = url.find("/")

		if(slash_pos == -1):
			content = "/"
		else:
			content = url[slash_pos:]

		return content

	def replaceUrl(message):
		url = HttpParser.getUrl(message)
		content = HttpParser.getContent(message)
		messageLines = HttpParser.decode(message)
		messageLines[0] = messageLines[0].replace(url, content)
		return (HttpParser.encode(messageLines))

	def removeProxyHeader(message):
		messageLines = HttpParser.decode(message)
		for i, line in enumerate(messageLines):
			if(line[0:16] == "Proxy-Connection"):
				del messageLines[i]
				break
		return (HttpParser.encode(messageLines))

	def getHeader(message):
		rByte = b'\r'[0]
		nByte = b'\n'[0]
		for i in range(len(message)):
			if i<=len(message) - 4 and message[i]==rByte and message[i+1]==nByte and message[i+2]==rByte and message[i+3]==nByte:
				return message[:i+2] 

	def noCache(message):
		messageLines = HttpParser.decode(message)
		for line in messageLines:
			if "Pragma: no-cache" in line:
				return True
		return False
