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

    def test_manufacturer_encode(self):
        intval = meterbus.aux.manufacturer_id("WEP")
        h1, h2 = meterbus.manufacturer_encode(intval, 2)
        hexstr = "{0:02X}{1:02X}".format(h1, h2)
        self.assertEqual(hexstr, "B05C")

    def test_invalid_manufacturer_length(self):
        intval = meterbus.aux.manufacturer_id("J")
        falseVal = meterbus.manufacturer_encode(intval, 2)
        self.assertEqual(falseVal, None)

    def test_invalid_manufacturer_string(self):
        intval = meterbus.aux.manufacturer_id("@@@")
        falseVal = meterbus.manufacturer_encode(intval, 2)
        self.assertEqual(falseVal, None)

    def test_invalid_manufacturer_string_unicode(self):
        intval = meterbus.aux.manufacturer_id(u"ÖÖÖ")
        self.assertEqual(False, intval)

    def test_is_primary_true(self):
        self.assertEqual(True, meterbus.is_primary_address(1))

    def test_is_primary_false(self):
        self.assertEqual(False, meterbus.is_primary_address(256))

    def test_is_primary_false_str(self):
        self.assertEqual(False, meterbus.is_primary_address("A"))

    def test_is_secondary_true(self):
        self.assertEqual(True,
            meterbus.is_secondary_address("00000001B05CFF1B"))

    def test_is_secondary_false(self):
        self.assertEqual(False, meterbus.is_secondary_address(0))

    def test_is_secondary_hex_invalid(self):
        self.assertEqual(False,
            meterbus.is_secondary_address("HELLOWORLD000000"))

    def test_is_secondary_length_invalid(self):
        self.assertEqual(False,
            meterbus.is_secondary_address("0000"))

    def test_is_secondary_invalid_none(self):
        self.assertEqual(False,
            meterbus.is_secondary_address(None))

    def test_inter_char_timeout(self):
        opts = {
            300: 0.12,
            600: 0.60,
            1200: 0.4,
            2400: 0.2,
            4800: 0.2,
            9600: 0.1,
            19200: 0.1,
            38400: 0.1,
        }
        for key, val in opts.items():
            self.assertEqual(
                meterbus.inter_byte_timeout(key), val)

if __name__ == '__main__':
    unittest.main()
