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
        self.frame = "\x68\x05\x05\x68\x08\x00\x78\x0f\x00\x8f\x16"

    def test_record_count(self):
        tele = meterbus.load(self.frame)
        self.assertEqual(len(tele.body.bodyPayload.records), 1)

    # Value
    def test_record1_value(self):
        tele = meterbus.load(self.frame)
        records = tele.records
        self.assertEqual(records[0].parsed_value, '00')

if __name__ == '__main__':
    unittest.main()
