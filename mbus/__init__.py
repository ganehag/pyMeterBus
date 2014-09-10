###
#
# pyMBus
# --------------------------------------
#
###
from mbus_h import *
from mbus_c import *
from exceptions import *
from mbus_ackframe import *
from mbus_shortframe import *
from mbus_longframe import *
from mbus_controlframe import *

def parseb(data):
	if not data:
		raise MBusFrameDecodeError("No data in M-Bus frame")

	# print "Attempting to parse binary data [size = {0}]".format(len(data))
	# for c in data:
	# 	print hex(int(ord(c))), "",
	# print ""

	idata = map(ord, list(data))
	#frame = None

	for Frame in [MBusACKFrame, MBusShortFrame, MBusControlFrame, MBusLongFrame]:
		try:
			return Frame.parse(idata)

		except MBusFrameDecodeError, e:
			pass

#
#	for case in switch(int(ord(data[0]))):
#		if case(MBUS_FRAME_ACK_START):
#			frame = MBusACKFrame(data)
#			break
#
#		if case(MBUS_FRAME_SHORT_START):
#			frame = MBusShortFrame(data)
#			break
#
#		if case(MBUS_FRAME_LONG_START):
#			frame = MBusLongFrame(data)
#			break
#
#		if case():
#			raise MBusFrameDecodeError("Invalid M-Bus frame start")
#			# print 
#			# return None # Should cast exception
#
	#return frame
	raise MBusFrameDecodeError("Failed to identify frame")