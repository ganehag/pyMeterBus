import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import unittest
import meterbus
from meterbus.exceptions import *


class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.frame = "\x2e\x44\x09\x07\x55\x62\x09\x00\x07\x0c\x7a\x13\x10\x20" \
                     "\x05\x9e\x41\x56\x1b\x48\x5f\x19\x3b\x31\x63\xb2\x8a\xea" \
                     "\x22\x66\x22\xe7\x1e\x86\x56\x50\x12\x32\x98\x76\xdc\xc0" \
                     "\x7d\xe0\xdd\x85\x5b"
        meterbus.add_wmbus_encryption_key(bytes.fromhex("00096255"), bytes.fromhex("CB6ABFAA8D2247B59127D3B839CF34B4"))

    def test_is_encrypted(self):
        tele = meterbus.load(self.frame)
        self.assertTrue(tele.is_encrypted)

    def test_record_count(self):
        tele = meterbus.load(self.frame)
        self.assertEqual(len(tele.records), 3)

    # Value
    def test_record1_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.records
        self.assertEqual(records[0].parsed_value, 0)

    def test_record2_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.records
        self.assertEqual(records[1].parsed_value, '2020-04-21T10:16')

    def test_record3_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.records
        self.assertAlmostEqual(float(records[2].parsed_value), 0.071)

    # Unit
    def test_record1_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.records
        self.assertEqual(records[0].unit, "Wh")

    def test_record2_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.records
        self.assertEqual(records[1].unit, "date time")

    def test_record3_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.records
        self.assertEqual(records[2].unit, "m^3")


if __name__ == '__main__':
    unittest.main()
