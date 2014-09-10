import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import random
import mbus
import unittest
from mbus.exceptions import *

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.ack_frame     = "\xE5"
        self.short_frame   = "\x10\x08\x0b\x13\x16"
        self.control_frame = "\x68\x03\x03\x68\x08\x0b\x72\x85\x16"
        self.long_frame    = "\x68\x3d\x3d\x68\x08\x0b\x72\x21\x00\x00\x00\xb0\x5c\x02\x1b\x12\x00\x00\x00\x0c\x78\x49\x04\x00\x64\x02\x75\x0a\x00\x01\xfd\x71\x1e\x2f\x2f\x0a\x66\x20\x02\x0a\xfb\x1a\x31\x05\x02\xfd\x97\x1d\x00\x00\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\xdd\x16"

    def test_single_proper(self):
        data = None
        try:
            data = mbus.parseb(self.ack_frame)
        except MBusError, e:
            pass

        print data.__class__.__name__

        self.assertIsInstance(data, mbus.MBusACKFrame)

    def test_short_proper(self):
        data = None
        try:
            data = mbus.parseb(self.short_frame)
        except MBusError, e:
            pass

        self.assertIsInstance(data, mbus.MBusShortFrame)

    def test_control_proper(self):
        data = None
        try:
            data = mbus.parseb(self.control_frame)
        except MBusError, e:
            pass

        self.assertIsInstance(data, mbus.MBusControlFrame)

    def test_long_proper(self):
        data = None
        try:
            data = mbus.parseb(self.long_frame)
        except MBusError, e:
            pass

        self.assertIsInstance(data, mbus.MBusLongFrame)

    def test_short_invalid_crc(self):
        data = None
        frame = self.short_frame[:-2] + "\x00" + self.short_frame[-1]
        self.assertRaises(mbus.MBusFrameCRCError, mbus.parseb, (frame))

    def test_control_invalid_crc(self):
        data = None
        frame = self.control_frame[:-2] + "\x00" + self.control_frame[-1]
        self.assertRaises(mbus.MBusFrameCRCError, mbus.parseb, (frame))

    def test_long_invalid_crc(self):
        data = None
        frame = self.long_frame[:-2] + "\x00" + self.long_frame[-1]
        self.assertRaises(mbus.MBusFrameCRCError, mbus.parseb, (frame))


#if __name__ == '__main__':
#    unittest.main()
