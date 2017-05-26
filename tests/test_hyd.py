import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import unittest
import meterbus
from meterbus.exceptions import *


class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.frame = "\x68\x54\x54\x68\x08\x4e\x72\x78\x75\x01\x51\x24\x23\x20" \
                     "\x04\x46\x70\x00\x00\x0c\x06\x00\x00\x00\x00\x8c\x10\x06" \
                     "\x00\x00\x00\x00\x0c\x13\x43\x94\x36\x01\x8c\x20\x13\x00" \
                     "\x00\x00\x00\x8c\x40\x13\x48\x00\x00\x00\x8c\x80\x40\x13" \
                     "\x12\x00\x00\x00\x02\xfd\x17\x10\x00\x3b\x3b\xbd\xeb\xdd" \
                     "\x3c\x2b\xbd\xeb\xdd\xdd\x0a\x5a\x74\x01\x0a\x5e\x72\x01" \
                     "\x0a\x62\x01\x00\x6b\x16"

    def test_record_count(self):
        tele = meterbus.load(self.frame)
        self.assertEqual(len(tele.body.bodyPayload.records), 12)

    # Value
    def test_record1_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[0].parsed_value, 0)

    def test_record2_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[1].parsed_value, 0)

    def test_record3_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(records[2].parsed_value, 1369.443, 3)

    def test_record4_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[3].parsed_value, 0)

    def test_record5_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(float(records[4].parsed_value), 0.048, 3)

    def test_record6_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(float(records[5].parsed_value), 0.012, 3)

    def test_record7_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(float(records[6].parsed_value), 16, 1)

    def test_record8_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(float(records[7].parsed_value), 1445.223, 3)

    def test_record9_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(float(records[8].parsed_value), 144445223.0, 1)

    def test_record10_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(float(records[9].parsed_value), 17.4, 1)

    def test_record11_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(float(records[10].parsed_value), 17.2, 1)

    def test_record12_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(float(records[11].parsed_value), 0.1, 1)

    # Unit
    def test_record1_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[0].unit, "WH")

    def test_record2_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[1].unit, "WH")

    def test_record3_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[2].unit, "m^3")

    def test_record4_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[3].unit, "m^3")

    def test_record5_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[4].unit, "m^3")

    def test_record6_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[5].unit, "m^3")

    def test_record7_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[6].unit, "none")

    def test_record8_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[7].unit, "m^3/h")

    def test_record9_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[8].unit, "W")

    def test_record10_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[9].unit, "C")

    def test_record11_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[10].unit, "C")

    def test_record12_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[11].unit, "K")


if __name__ == '__main__':
    unittest.main()
