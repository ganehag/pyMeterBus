import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import mbus
import unittest
from mbus.exceptions import *

from mbus.telegram_body import TelegramBodyPayload

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.ack_frame     = "\xE5"
        self.short_frame   = "\x10\x08\x0b\x13\x16"
        self.control_frame = "\x68\x03\x03\x68\x08\x0b\x72\x85\x16"
        self.long_frame    = "\x68\x3d\x3d\x68\x08\x0b\x72\x21\x00\x00\x00\xb0\x5c\x02\x1b\x12\x00\x00\x00\x0c\x78\x49\x04\x00\x64\x02\x75\x0a\x00\x01\xfd\x71\x1e\x2f\x2f\x0a\x66\x20\x02\x0a\xfb\x1a\x31\x05\x02\xfd\x97\x1d\x00\x00\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\xdd\x16"

        self.payload = "\x0C\x05\x14\x00\x00\x00\x0C\x13\x13\x20\x00\x00\x0B\x22\x01\x24\x03\x04\x6D\x12\x0B\xD3\x12\x32\x6C\x00\x00\x0C\x78\x43\x53\x93\x07\x06\xFD\x0C\xF2\x03\x01\x00\xF6\x01\x0D\xFD\x0B\x05\x31\x32\x4D\x46\x57\x01\xFD\x0E\x00\x4C\x05\x14\x00\x00\x00\x4C\x13\x13\x20\x00\x00\x42\x6C\xBF\x1C\x0F\x37\xFD\x17\x00\x00\x00\x00\x00\x00\x00\x00\x02\x7A\x25\x00\x02\x78\x25\x00"

    def test_parse_payload(self):
        tBody = TelegramBodyPayload(self.payload)
        tBody.parse()
        # tBody.debug()

        self.assertEquals(len(tBody.records), 12)

    # def test_single_proper(self):
    #     data = None
    #     try:
    #         data = mbus.parseb(self.ack_frame)
    #     except MBusError, e:
    #         pass

    #     print data.__class__.__name__

    #     self.assertIsInstance(data, mbus.MBusACKFrame)

    # def test_short_proper(self):
    #     data = None
    #     try:
    #         data = mbus.parseb(self.short_frame)
    #     except MBusError, e:
    #         pass

    #     self.assertIsInstance(data, mbus.MBusShortFrame)

    # def test_control_proper(self):
    #     data = None
    #     try:
    #         data = mbus.parseb(self.control_frame)
    #     except MBusError, e:
    #         pass

    #     self.assertIsInstance(data, mbus.MBusControlFrame)

    # def test_long_proper(self):
    #     data = None
    #     try:
    #         data = mbus.parseb(self.long_frame)
    #     except MBusError, e:
    #         pass

    #     self.assertIsInstance(data, mbus.MBusLongFrame)

    # def test_short_invalid_crc(self):
    #     data = None
    #     frame = self.short_frame[:-2] + "\x00" + self.short_frame[-1]
    #     self.assertRaises(mbus.MBusFrameCRCError, mbus.parseb, (frame))

    # def test_control_invalid_crc(self):
    #     data = None
    #     frame = self.control_frame[:-2] + "\x00" + self.control_frame[-1]
    #     self.assertRaises(mbus.MBusFrameCRCError, mbus.parseb, (frame))

    # def test_long_invalid_crc(self):
    #     data = None
    #     frame = self.long_frame[:-2] + "\x00" + self.long_frame[-1]
    #     self.assertRaises(mbus.MBusFrameCRCError, mbus.parseb, (frame))


#if __name__ == '__main__':
#    unittest.main()
