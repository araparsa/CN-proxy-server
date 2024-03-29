# -*- coding: utf-8 -*-
# @Author: arman
# @Date:   2019-12-09 13:49:10
# @Last Modified by:   arman
# @Last Modified time: 2019-12-14 19:44:58
import datetime 

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

	def changeAcceptEncoding(message):
		reqStr = HttpParser.decode(message)
		for i in range(len(reqStr)) :
			if reqStr[i].split(' ')[0] == 'Accept-Encoding:' :
				reqStr[i] = 'Accept-Encoding: identity'
				break
		return HttpParser.encode(reqStr)


	def changeConnection(message):
		reqStr = HttpParser.decode(message)
		for i in range(len(reqStr)) :
			if reqStr[i].split(' ')[0] == 'Connection:' :
				reqStr[i] = 'Connection: Close'
				break

		return HttpParser.encode(reqStr)

	def getUrl(message):
		messageLines = HttpParser.decode(message)
		try:
			url= (messageLines[0].split(" ")[1]) #get url 
			return (url)
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

	def getExpireDate(message):
		messageLines = HttpParser.decode(message)
		for line in messageLines:
			if line[0:7] == "Expires":
				dateStr = line[9:-1]
				date = datetime.datetime.strptime(dateStr, "%a, %d %b %Y %H:%M:%S %Z")
				return(date)
		return ""

	def addIfModified(message, date):
		messageLines = HttpParser.decode(message)
		ifDateStr = "If-Modified-Since: " + date.strftime("%a, %d %b %Y %H:%M:%S ") + "GMT\r"
		messageLines.insert(2, ifDateStr)
		return HttpParser.encode(messageLines)

	def isModified(message):
		header = HttpParser.getHeader(message)
		headerLines = HttpParser.decode(header)
		if (headerLines[0].find("200")>0):
			return True
		elif (headerLines[0].find("304")>0):
			return False
		else:
			return True

	def getUserAgent(message):
		messageLines = HttpParser.decode(message)
		for i, line in enumerate(messageLines):
			if len(line)>9 and line[0:10] == "User-Agent":
				return line[12:-1], i

	def replaceUserAgent(message, newAgent):
		messageLines = HttpParser.decode(message)
		oldAgent, i = HttpParser.getUserAgent(message)
		messageLines[i] = messageLines[i].replace(oldAgent, newAgent)
		return HttpParser.encode(messageLines)

	def getHost(message):
		messageLines = HttpParser.decode(message)
		for line in messageLines:
			if line[0:4] == "Host":
				return line[6:-1] 