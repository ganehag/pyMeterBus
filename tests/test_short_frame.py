# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
from builtins import (bytes, str, open, super, range,
                      zip, round, input, int, pow, object)

import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import unittest
import meterbus
from meterbus.exceptions import *

def char2int(val):
    if type(val) == int:
        return val
    return ord(val)

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.frame = "\x10\x08\x0b\x13\x16"
        self.frame_bytes = b"\x10\x08\x0b\x13\x16"

    def test_load_string(self):
        frame = meterbus.TelegramShort(self.frame)
        frame_bytes = list(map(char2int, list(self.frame_bytes)))
        self.assertEqual(list(frame), frame_bytes)

    def test_load_bytes(self):
        frame = meterbus.TelegramShort(self.frame_bytes)
        frame_bytes = list(map(char2int, list(self.frame_bytes)))
        self.assertEqual(list(frame), frame_bytes)

    def test_load_crc_error(self):
        frame_data = list(map(char2int, list(self.frame_bytes)))
        frame_data[-2] = 255

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
