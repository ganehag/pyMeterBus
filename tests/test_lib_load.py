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
        pass

    def test_load_empty(self):
        with self.assertRaises(MBusFrameDecodeError):
            meterbus.load("INVALID_DATA")

if __name__ == '__main__':
    unittest.main()
