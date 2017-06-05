import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import unittest
import meterbus
from meterbus.exceptions import *


class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.invalid_frame = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        self.ack_frame = b"\xE5"
        self.short_frame = b"\x10\x08\x0b\x13\x16"
        self.control_frame = b"\x68\x03\x03\x68\x08\x0b\x72\x85\x16"
        self.long_frame = (b"\x68\x3d\x3d\x68\x08\x0b\x72\x21\x00\x00\x00\xb0\x5c\x02"
                           b"\x1b\x12\x00\x00\x00\x0c\x78\x49\x04\x00\x64\x02\x75\x0a"
                           b"\x00\x01\xfd\x71\x1e\x2f\x2f\x0a\x66\x20\x02\x0a\xfb\x1a"
                           b"\x31\x05\x02\xfd\x97\x1d\x00\x00\x2f\x2f\x2f\x2f\x2f\x2f"
                           b"\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\xdd\x16")

    def test_ack_frame(self):
        tele = meterbus.load(self.ack_frame)
        self.assertIsInstance(tele, meterbus.TelegramACK)

    def test_short_frame(self):
        tele = meterbus.load(self.short_frame)
        self.assertIsInstance(tele, meterbus.TelegramShort)

    def test_control_frame(self):
        tele = meterbus.load(self.control_frame)
        self.assertIsInstance(tele, meterbus.TelegramControl)

    def test_long_frame(self):
        tele = meterbus.load(self.long_frame)
        self.assertIsInstance(tele, meterbus.TelegramLong)

    def test_ack_parse_fail(self):
        with self.assertRaises(FrameMismatch):
            # Give it the wrong frame
            meterbus.TelegramACK.parse(list(self.invalid_frame))

    def test_short_parse_fail(self):
        with self.assertRaises(FrameMismatch):
            # Give it the wrong frame
            meterbus.TelegramShort.parse(list(self.invalid_frame))

    def test_control_parse_fail(self):
        with self.assertRaises(FrameMismatch):
            # Give it the wrong frame
            meterbus.TelegramControl.parse(list(self.invalid_frame))

    def test_long_parse_fail(self):
        with self.assertRaises(FrameMismatch):
            # Give it the wrong frame
            meterbus.TelegramLong.parse(list(self.invalid_frame))

    def test_ack_parse_empty(self):
        with self.assertRaises(MBusFrameDecodeError):
            meterbus.TelegramACK.parse([])

    def test_short_parse_empty(self):
        with self.assertRaises(MBusFrameDecodeError):
            meterbus.TelegramShort.parse([])

    def test_control_parse_empty(self):
        with self.assertRaises(MBusFrameDecodeError):
            meterbus.TelegramControl.parse([])

    def test_long_parse_empty(self):
        with self.assertRaises(MBusFrameDecodeError):
            meterbus.TelegramLong.parse([])

    def test_ack_parse_none(self):
        with self.assertRaises(MBusFrameDecodeError):
            meterbus.TelegramACK.parse(None)

    def test_short_parse_none(self):
        with self.assertRaises(MBusFrameDecodeError):
            meterbus.TelegramShort.parse(None)

    def test_control_parse_none(self):
        with self.assertRaises(MBusFrameDecodeError):
            meterbus.TelegramControl.parse(None)

    def test_long_parse_none(self):
        with self.assertRaises(MBusFrameDecodeError):
            meterbus.TelegramLong.parse(None)

if __name__ == '__main__':
    unittest.main()
