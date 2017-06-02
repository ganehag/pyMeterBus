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

    def test_debug_default_value(self):
        self.assertEqual(meterbus.g.debug, False)

    def test_debug_set_true(self):
        meterbus.debug(True)
        self.assertEqual(meterbus.g.debug, True)

if __name__ == '__main__':
    unittest.main()
