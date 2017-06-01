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
        self.dib_empty = meterbus.DataInformationBlock()
        self.dib0 = meterbus.DataInformationBlock([0x0C])
        self.dib7 = meterbus.DataInformationBlock([0x2F])
        self.dib8 = meterbus.DataInformationBlock([0x0F])
        self.dib9 = meterbus.DataInformationBlock([0x1F])

        self.frame = "\x68\x53\x53\x68\x08\x05\x72\x34\x08\x00\x54\x96\x15\x32" \
                     "\x00\xf2\x00\x00\x00\x01\xfd\x1b\x00\x02\xfc\x03\x48\x52" \
                     "\x25\x74\xd4\x11\x22\xfc\x03\x48\x52\x25\x74\xc8\x11\x12" \
                     "\xfc\x03\x48\x52\x25\x74\xb4\x16\x02\x65\xd0\x08\x22\x65" \
                     "\x70\x08\x12\x65\x23\x09\x01\x72\x18\x42\x65\xe4\x08\x82" \
                     "\x01\x65\xdd\x08\x0c\x78\x34\x08\x00\x54\x03\xfd\x0f\x00" \
                     "\x00\x04\x1f\x5d\x16"

        self.frame = "\x68\x64\x64\x68\x08\x01\x76\x15\x53\x11\x11\x00\x00\x52" \
                     "\x04\x0A\x10\x00\x00\x02\x6C\x23\x12\x3C\x0F\x00\x58\x53" \
                     "\x40\xBC\x20\x0F\x00\x00\x00\x00\x3C\x15\x03\x79\x71\x68" \
                     "\x8C\x10\x13\x00\x00\x00\x00\x8C\x20\x13\x00\x00\x00\x00" \
                     "\x8C\x30\x13\x00\x00\x00\x00\x8C\x40\x13\x00\x00\x00\x00" \
                     "\x3A\x3D\x02\x63\x3A\x2E\x01\x07\x0A\x5A\x04\x25\x0A\x5E" \
                     "\x03\x89\x0C\x22\x00\x03\x80\x71\x3C\x22\x00\x02\x90\x80" \
                     "\x04\x7E\x00\x00\x3A\x12\x2C\x16"

        self.frame = "\x68\x54\x54\x68\x08\x4e\x72\x78\x75\x01\x51\x24\x23\x20" \
                     "\x04\x46\x70\x00\x00\x0c\x06\x00\x00\x00\x00\x8c\x10\x06" \
                     "\x00\x00\x00\x00\x0c\x13\x43\x94\x36\x01\x8c\x20\x13\x00" \
                     "\x00\x00\x00\x8c\x40\x13\x48\x00\x00\x00\x8c\x80\x40\x13" \
                     "\x12\x00\x00\x00\x02\xfd\x17\x10\x00\x3b\x3b\xbd\xeb\xdd" \
                     "\x3c\x2b\xbd\xeb\xdd\xdd\x0a\x5a\x74\x01\x0a\x5e\x72\x01" \
                     "\x0a\x62\x01\x00\x6b\x16"

        self.frame = meterbus.load(self.frame)

    def test_empty_dib_has_extension_bit(self):
        self.assertEqual(self.dib_empty.has_extension_bit, False)

    def test_empty_dib_has_lvar_bit(self):
        self.assertEqual(self.dib_empty.has_lvar_bit, False)

    def test_empty_dib_is_eoud(self):
        self.assertEqual(self.dib_empty.is_eoud, False)

    def test_empty_dib_more_records_follow(self):
        self.assertEqual(self.dib_empty.more_records_follow, False)

    def test_empty_dib_is_variable_length(self):
        self.assertEqual(self.dib_empty.is_variable_length, False)

    def test_dib0_has_extension_bit(self):
        self.assertEqual(self.dib0.has_extension_bit, False)

    def test_dib0_has_lvar_bit(self):
        self.assertEqual(self.dib0.has_lvar_bit, False)

    def test_dib0_is_eoud(self):
        self.assertEqual(self.dib0.is_eoud, False)

    def test_dib0_is_variable_length(self):
        self.assertEqual(self.dib0.is_variable_length, False)

    def test_dib0_function_type(self):
        self.assertEqual(self.dib0.function_type,
                         meterbus.FunctionType.INSTANTANEOUS_VALUE)

    def test_dib7_function_type(self):
        self.assertEqual(self.dib7.function_type,
                         meterbus.FunctionType.SPECIAL_FUNCTION_FILL_BYTE)

    def test_dib8_function_type(self):
        self.assertEqual(self.dib8.function_type,
                         meterbus.FunctionType.SPECIAL_FUNCTION)

    def test_dib9_more_records_follow(self):
        self.assertEqual(self.dib9.more_records_follow, True)

    def test_dib9_function_type(self):
        self.assertEqual(self.dib9.function_type,
                         meterbus.FunctionType.MORE_RECORDS_FOLLOW)

if __name__ == '__main__':
    unittest.main()
