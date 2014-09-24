from telegram_header import TelegramHeader
from telegram_body import TelegramBody

class Telegram(object):
	def __init__(self, header=None, body=None):
		if header:
			self._header = header
		else:
			self._header = TelegramHeader()
		if body:
			self._body = body
		else:
			self._body   = TelegramBody()

	@property
	def header(self):
		return self._header
	@header.setter
	def header(self, value):
		self._header = TelegramHeader()
		self._header.createTelegramHeader(value)

	@property
	def body(self):
		return self._body
	@body.setter
	def body(self, value):
		self._body = TelegramBody()
		self._body.createTelegramBody(value)
	
	def createTelegram(self, tgr):
		telegram = tgr
		if isinstance(tgr, basestring):
			telegram = tgr.split(" ")

		headerLength = self.header.headerLength
		firstHeader  = telegram[0:headerLength]

		# ??? juggeling, copy CRC and stopByte into header... juck!
		resultHeader = firstHeader + telegram[-2:] 

		self.header.createTelegramHeader(resultHeader)
		self.body.createTelegramBody(telegram[headerLength:-2])

	def parse(self):
		self.body.parse()

	def debug(self):
		self.header.debug()
		self.body.debug()