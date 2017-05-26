import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import unittest
import meterbus
from meterbus.exceptions import *


class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.frame = "\x68\x3d\x3d\x68\x08\x0b\x72\x21\x00\x00\x00\xb0\x5c\x02" \
                     "\x1b\x12\x00\x00\x00\x0c\x78\x49\x04\x00\x64\x02\x75\x0a" \
                     "\x00\x01\xfd\x71\x1e\x2f\x2f\x0a\x66\x20\x02\x0a\xfb\x1a" \
                     "\x31\x05\x02\xfd\x97\x1d\x00\x00\x2f\x2f\x2f\x2f\x2f\x2f" \
                     "\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\x2f\xdd\x16"

    def test_record_count(self):
        tele = meterbus.load(self.frame)
        self.assertEqual(len(tele.body.bodyPayload.records), 6)

    # Value
    def test_record1_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[0].parsed_value, 64000449)

    def test_record2_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[1].parsed_value, 600)

    def test_record3_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[2].parsed_value, -70)

    def test_record4_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[3].parsed_value, 22)

    def test_record5_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(records[4].parsed_value, 53.1, 5)

    def test_record6_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[5].parsed_value, 0)

    # Unit
    def test_record1_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[0].unit, "none")

    def test_record2_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[1].unit, "seconds")

    def test_record3_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[2].unit, "dBm")

    def test_record4_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[3].unit, "C")

    def test_record5_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[4].unit, "%")

    def test_record6_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[5].unit, "none")

if __name__ == '__main__':
    unittest.main()
