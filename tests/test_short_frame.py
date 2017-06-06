# -*- coding: utf-8 -*-

import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import unittest
import meterbus
from meterbus.exceptions import *


class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.frame = "\x10\x08\x0b\x13\x16"

    def test_load_string(self):
        frame = meterbus.TelegramShort(self.frame)
        self.assertEqual(list(frame), list(bytearray(self.frame, 'ascii')))

    def test_load_crc_error(self):
        frame_data = list(self.frame)
        frame_data[-2] = '\xFF'

        with self.assertRaises(MBusFrameCRCError):
            meterbus.TelegramShort(frame_data)

    def test_frame_header_setter(self):
        frame = meterbus.TelegramShort(self.frame)
        hdr = meterbus.TelegramHeader()
        frame.header = hdr
        self.assertIs(frame.header, hdr)

    def test_frame_crc(self):
        frame = meterbus.TelegramShort(self.frame)
        self.assertEqual(frame.check_crc(), True)

if __name__ == '__main__':
    unittest.main()
