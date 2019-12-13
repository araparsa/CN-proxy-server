class AccountingHandler():
	"""docstring for RestrictionHandler"""
	def __init__(self, config):
		self.getAccountingHosts(config)

	def getAccountingHosts(self, config):
		self.accountingHosts = config["users"]
		for item in self.accountingHosts:
			item["volume"] = int(item["volume"])

	def hasCharge(self, clientIP):
		for item in self.accountingHosts:
			if clientIP == item["IP"]:
				if item["volume"] > 0:
					return True
				else:
					return False
		return False

	def hasEnoughCharge(self, clientIP, length):
		for item in self.accountingHosts:
			if clientIP == item["IP"]:
				if item["volume"] > length:
					item["volume"] = item["volume"] - length
					return True
				else:
					return False
		return False
