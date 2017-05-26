import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import unittest
import meterbus
from meterbus.exceptions import *


class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.frame = "\x68\x53\x53\x68\x08\x05\x72\x34\x08\x00\x54\x96\x15\x32" \
                     "\x00\xf2\x00\x00\x00\x01\xfd\x1b\x00\x02\xfc\x03\x48\x52" \
                     "\x25\x74\xd4\x11\x22\xfc\x03\x48\x52\x25\x74\xc8\x11\x12" \
                     "\xfc\x03\x48\x52\x25\x74\xb4\x16\x02\x65\xd0\x08\x22\x65" \
                     "\x70\x08\x12\x65\x23\x09\x01\x72\x18\x42\x65\xe4\x08\x82" \
                     "\x01\x65\xdd\x08\x0c\x78\x34\x08\x00\x54\x03\xfd\x0f\x00" \
                     "\x00\x04\x1f\x5d\x16"

    def test_record_count(self):
        tele = meterbus.load(self.frame)
        self.assertEqual(len(tele.body.bodyPayload.records), 13)

    # Values
    def test_record1_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[0].parsed_value, 0)

    def test_record2_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(float(records[1].parsed_value), 45.64, 5)

    def test_record3_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(float(records[2].parsed_value), 45.52, 5)

    def test_record4_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(float(records[3].parsed_value), 58.12, 5)

    def test_record5_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(float(records[4].parsed_value), 22.56, 5)

    def test_record6_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(float(records[5].parsed_value), 21.6, 5)

    def test_record7_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(float(records[6].parsed_value), 23.39, 5)

    def test_record8_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[7].parsed_value, 86400)

    def test_record9_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(float(records[8].parsed_value), 22.76, 5)

    def test_record10_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertAlmostEqual(float(records[9].parsed_value), 22.69, 5)

    def test_record11_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[10].parsed_value, 54000834)

    def test_record12_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[11].parsed_value, 262144)

    def test_record13_value(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[12].parsed_value, None)

    # Units
    def test_record1_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[0].unit, "none")

    def test_record2_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[1].unit, "%RH")

    def test_record3_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[2].unit, "%RH")

    def test_record4_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[3].unit, "%RH")

    def test_record5_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[4].unit, "C")

    def test_record6_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[5].unit, "C")

    def test_record7_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[6].unit, "C")

    def test_record8_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[7].unit, "seconds")

    def test_record9_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[8].unit, "C")

    def test_record10_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[9].unit, "C")

    def test_record11_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[10].unit, "none")

    def test_record12_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[11].unit, "none")

    def test_record13_unit(self):
        tele = meterbus.load(list(map(ord, self.frame)))
        records = tele.body.bodyPayload.records
        self.assertEqual(records[12].unit, None)

if __name__ == '__main__':
    unittest.main()
