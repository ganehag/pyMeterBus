from mbus_h import *
from mbus_telegram import *
from exceptions import *

class MBusACKFrame(MBusTelegram):
	@staticmethod
	def parse(data):
		if data and len(data) < MBUS_FRAME_BASE_SIZE_ACK:
			raise MBusFrameDecodeError("Invalid M-Bus length")

		if data[0] != MBUS_FRAME_ACK_START:
			raise MBusFrameDecodeError("Wrong start byte")

		return MBusACKFrame()

	def __init__(self, dbuf=None):
		self.type      = MBUS_FRAME_TYPE_ACK
		self.base_size = MBUS_FRAME_BASE_SIZE_ACK