from mbus_h import *
from mbus_telegram import *
from exceptions import *

class MBusShortFrame(MBusTelegram):
	def __init__(self, dbuf=None):
		self.type      = MBUS_FRAME_TYPE_SHORT
		self.base_size = MBUS_FRAME_BASE_SIZE_SHORT

	def compute_crc(self):
		return (self.control + self.address) % 256

	def check_crc(self):
		return self.compute_crc() == self.checksum

	@staticmethod
	def parse(data):
		if data and len(data) != MBUS_FRAME_BASE_SIZE_SHORT:
			raise MBusFrameDecodeError("Invalid M-Bus length")

		if data[0] != MBUS_FRAME_SHORT_START:
			raise MBusFrameDecodeError("Wrong start byte")

		base_frame = MBusShortFrame()

		base_frame.type      = MBUS_FRAME_TYPE_SHORT
		base_frame.base_size = MBUS_FRAME_BASE_SIZE_SHORT

		base_frame.start1   = data[0]
		base_frame.control  = data[1]
		base_frame.address  = data[2]
		base_frame.checksum = data[3]
		base_frame.stop     = data[4]

		if not base_frame.check_crc():
			raise MBusFrameCRCError(base_frame.compute_crc(), base_frame.checksum)

		return base_frame
