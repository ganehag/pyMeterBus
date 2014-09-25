from mbus_h import *
from mbus_telegram import *
from exceptions import *

class MBusControlFrame(MBusTelegram):
	def __init__(self, dbuf=None):
		self.base_size = MBUS_FRAME_BASE_SIZE_CONTROL
		return

	def compute_crc(self):
		return (self.control + self.address + self.control_information) % 256
		
	def check_crc(self):
		return self.compute_crc() == self.checksum
		
	@staticmethod
	def parse(data):
		if data and len(data) < MBUS_FRAME_BASE_SIZE_CONTROL:
			raise MBusFrameDecodeError("Invalid M-Bus length")

		if data[0] != MBUS_FRAME_CONTROL_START:
			raise MBusFrameDecodeError("Wrong start byte")

		base_frame = MBusControlFrame()

		base_frame.type                = MBUS_FRAME_TYPE_CONTROL
		base_frame.base_size           = MBUS_FRAME_BASE_SIZE_CONTROL

		base_frame.start1              = data[0]
		base_frame.length1             = data[1]
		base_frame.length2             = data[2]
		base_frame.start2              = data[3]
		base_frame.control             = data[4]
		base_frame.address             = data[5]
		base_frame.control_information = data[6]
		base_frame.checksum            = data[7]
		base_frame.stop                = data[8]

		if base_frame.length1 > 3 or base_frame.length1 != base_frame.length2:
			raise MBusFrameDecodeError("Invalid M-Bus length1 value")

		if not base_frame.check_crc():
			raise MBusFrameCRCError(base_frame.compute_crc(), base_frame.checksum)

		return base_frame
