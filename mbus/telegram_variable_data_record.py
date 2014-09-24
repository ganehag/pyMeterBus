from dif_telegram_field import DIFTelegramField
from vif_telegram_field import VIFTelegramField
from telegram_data_field import TelegramDataField

class TelegramVariableDataRecord(object):
	def __init__(self):
		self._dif       = DIFTelegramField()
		self._difes     = []

		self._vif       = VIFTelegramField()
		self._vifes     = []

		self._dataField = TelegramDataField()

	def parse(self):
		self.dif = DIFTelegramField()
		self.dif.parse()
		self.vif = VIFTelegramField()
		self.vif.setParent(self)

		self.dataField = TelegramDataField()
		self.dataField.setParent(self)
		self.dataField.parse()

	@property
	def dif(self):
	    return self._dif
	@dif.setter
	def dif(self, value):
	    self._dif = value

	@property
	def vif(self):
	    return self._vif
	@vif.setter
	def vif(self, value):
	    self._vif = value

	@property
	def difes(self):
	    return self._difes
	@difes.setter
	def difes(self, value):
	    self._difes = value
	
	@property
	def vifes(self):
	    return self._vifes
	@vifes.setter
	def vifes(self, value):
	    self._vifes = value
	
	
	@property
	def dataField(self):
	    return self._dataField
	@dataField.setter
	def dataField(self, value):
	    self._dataField = value

	def debug(self):
		print "VARIABLE DATA RECORD:"

		self.dif.debug()

		for item in self.difes:
			item.debug()

		self.vif.debug()

		for item in self.vifes:
			item.debug()

		self.dataField.debug()

		print "=================================================="