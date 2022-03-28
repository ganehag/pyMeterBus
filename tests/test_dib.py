# -*- coding: utf-8 -*-

from meterbus.exceptions import *
import meterbus
import unittest
import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')


class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.dib_empty = meterbus.DataInformationBlock()
        self.dib0 = meterbus.DataInformationBlock([0x0C])
        self.dib7 = meterbus.DataInformationBlock([0x2F])
        self.dib8 = meterbus.DataInformationBlock([0x0F])
        self.dib9 = meterbus.DataInformationBlock([0x1F])
        self.dib10 = meterbus.DataInformationBlock(
            [0xDA, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x7F])
        self.dib10.parse_dife()

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

    def test_dib9_storage_number(self):
        self.assertEqual(self.dib9.storage_number, 0)

    def test_dib9_tariff(self):
        self.assertEqual(self.dib9.tariff, None)

    def test_dib9_device(self):
        self.assertEqual(self.dib9.device, None)

    def test_dib10_last_dife_extension_bit(self):
        self.assertEqual(self.dib10.has_extension_bit, False)

    def test_dib10_device(self):
        self.assertEqual(self.dib10.device, 1023)

    def test_dib10_storage_number(self):
        self.assertEqual(self.dib10.storage_number, 2199023255551)

    def test_dib10_tariff(self):
        self.assertEqual(self.dib10.tariff, 1048575)


if __name__ == '__main__':
    unittest.main()
