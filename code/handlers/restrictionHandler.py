class RestrictionHandler():
	"""docstring for RestrictionHandler"""
	def __init__(self, config):
		self.getRestrictedHosts(config)

	def getRestrictedHosts(self, config):
		if not config["enable"]:
			return 
		self.restrictedHosts = config["targets"]

	def checkForRestriction(self, host):
		for item in self.restrictedHosts:
			if host == item["URL"]:
				if item["type"] == "BLOCK":
					return -1
				else:
					return int(item["delay"]) 
		return 0