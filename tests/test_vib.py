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
        self.vib_empty = meterbus.ValueInformationBlock()
        self.vib0 = meterbus.ValueInformationBlock([0xFD, 0x1B])

    def test_empty_vib_has_extension_bit(self):
        self.assertEqual(self.vib_empty.has_extension_bit, False)

    def test_empty_vib_without_extension_bit(self):
        self.assertEqual(self.vib_empty.without_extension_bit, False)

    def test_empty_vib_has_lvar_bit(self):
        self.assertEqual(self.vib_empty.has_lvar_bit, False)

    def test_vib0_has_extension_bit(self):
        self.assertEqual(self.vib0.has_extension_bit, False)

    def test_vib0_without_extension_bit(self):
        self.assertEqual(self.vib0.without_extension_bit, False)

    def test_vib0_has_lvar_bit(self):
        self.assertEqual(self.vib0.has_lvar_bit, False)

    def test_custom_vib_setter_getter(self):
        vib = meterbus.ValueInformationBlock()
        vib.customVIF = [0x65]
        self.assertEqual(vib.customVIF, [0x65])

if __name__ == '__main__':
    unittest.main()
