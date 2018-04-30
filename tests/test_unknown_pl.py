import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import decimal
import unittest
import meterbus
from meterbus.exceptions import *


class TestSequenceFunctions(unittest.TestCase):
    """Unknown device"""

    def setUp(self):
        self.frame = "\x68\x64\x64\x68\x08\x01\x76\x15\x53\x11\x11\x00\x00\x52" \
                     "\x04\x0A\x10\x00\x00\x02\x6C\x23\x12\x3C\x0F\x00\x58\x53" \
                     "\x40\xBC\x20\x0F\x00\x00\x00\x00\x3C\x15\x03\x79\x71\x68" \
                     "\x8C\x10\x13\x00\x00\x00\x00\x8C\x20\x13\x00\x00\x00\x00" \
                     "\x8C\x30\x13\x00\x00\x00\x00\x8C\x40\x13\x00\x00\x00\x00" \
                     "\x3A\x3D\x02\x63\x3A\x2E\x01\x07\x0A\x5A\x04\x25\x0A\x5E" \
                     "\x03\x89\x0C\x22\x00\x03\x80\x71\x3C\x22\x00\x02\x90\x80" \
                     "\x04\x7E\x00\x00\x3A\x12\x2C\x16"

    def test_record_count(self):
        tele = meterbus.load(self.frame)
        self.assertEqual(len(tele.body.bodyPayload.records), 15)

    # Value
    def test_record1_value(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[0].parsed_value, "2016-03-18")

    def test_record2_value(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[1].parsed_value, 5853400000000)

    def test_record3_value(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[2].parsed_value, 0)

    def test_record4_value(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(float(records[3].parsed_value), 379716.8, 5)

    def test_record5_value(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[4].parsed_value, 0)

    def test_record6_value(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[5].parsed_value, 0)

    def test_record7_value(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[6].parsed_value, 0)

    def test_record8_value(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[7].parsed_value, 0)

    def test_record9_value(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[8].parsed_value, 26.3)

    def test_record10_value(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[9].parsed_value, 107000)

    def test_record11_value(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[10].parsed_value, 42.5)

    def test_record12_value(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(float(records[11].parsed_value), 38.9, 5)

    def test_record13_value(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[12].parsed_value, 137055600)

    def test_record14_value(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[13].parsed_value, 104688000)

    def test_record15_value(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[14].parsed_value, 14866)


    # Unit
    def test_record1_unit(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[0].unit, "date")

    def test_record2_unit(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[1].unit, "J")

    def test_record3_unit(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[2].unit, "J")

    def test_record4_unit(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[3].unit, "m^3")

    def test_record5_unit(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[4].unit, "m^3")

    def test_record6_unit(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[5].unit, "m^3")

    def test_record7_unit(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[6].unit, "m^3")

    def test_record8_unit(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[7].unit, "m^3")

    def test_record9_unit(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[8].unit, "m^3/h")

    def test_record10_unit(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[9].unit, "W")

    def test_record11_unit(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[10].unit, "C")

    def test_record12_unit(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[11].unit, "C")

    def test_record13_unit(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[12].unit, "seconds")

    def test_record14_unit(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[13].unit, "seconds")

    def test_record15_unit(self):
        tele = meterbus.load(self.frame)
        records = tele.body.bodyPayload.records
        self.assertEqual(records[14].unit, "none")

if __name__ == '__main__':
    unittest.main()
