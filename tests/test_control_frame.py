# -*- coding: utf-8 -*-

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
        self.frame = "\x68\x03\x03\x68\x08\x0b\x72\x85\x16"
        self.frame_bytes = b"\x68\x03\x03\x68\x08\x0b\x72\x85\x16"

    def test_load_control_frame_str(self):
        frame = meterbus.TelegramControl(self.frame)
        self.assertEqual(list(frame), list(map(char2int, list(self.frame_bytes))))

    def test_load_control_frame_bytes(self):
        frame = meterbus.TelegramControl(self.frame_bytes)
        self.assertEqual(list(frame), list(map(char2int, list(self.frame_bytes))))

    def test_frame_header_setter(self):
        frame = meterbus.TelegramControl(self.frame)
        hdr = meterbus.TelegramHeader()
        frame.header = hdr
        self.assertIs(frame.header, hdr)

    def test_frame_body_setter(self):
        frame = meterbus.TelegramControl(self.frame)
        body = meterbus.TelegramBody()
        frame.body = body
        self.assertIs(frame.body, body)

if __name__ == '__main__':
    unittest.main()
