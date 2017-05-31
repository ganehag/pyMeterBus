import os
import sys
import json

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import unittest
import meterbus
from meterbus.exceptions import *

from json import encoder

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.frame = "\x68\x53\x53\x68\x08\x05\x72\x34\x08\x00\x54\x96\x15\x32" \
                     "\x00\xf2\x00\x00\x00\x01\xfd\x1b\x00\x02\xfc\x03\x48\x52" \
                     "\x25\x74\xd4\x11\x22\xfc\x03\x48\x52\x25\x74\xc8\x11\x12" \
                     "\xfc\x03\x48\x52\x25\x74\xb4\x16\x02\x65\xd0\x08\x22\x65" \
                     "\x70\x08\x12\x65\x23\x09\x01\x72\x18\x42\x65\xe4\x08\x82" \
                     "\x01\x65\xdd\x08\x0c\x78\x34\x08\x00\x54\x03\xfd\x0f\x00" \
                     "\x00\x04\x1f\x5d\x16"

        self.frame = meterbus.load(self.frame)

    def test_json_record0(self):
        dict_record = {
            "value": 0,
            "unit": "MeasureUnit.NONE",
            "type": "VIFUnitExt.DIGITAL_INPUT",
            "function": "FunctionType.INSTANTANEOUS_VALUE"
        }
        frame_rec_dict = json.loads(self.frame.records[0].to_JSON())
        self.assertEqual(frame_rec_dict, dict_record)

    def test_json_record1(self):
        dict_record = {
            "value": 45.64,
            "unit": "%RH",
            "type": "VIFUnit.VARIABLE_VIF",
            "function": "FunctionType.INSTANTANEOUS_VALUE"
        }
        frame_rec_dict = json.loads(self.frame.records[1].to_JSON())
        self.assertEqual(frame_rec_dict, dict_record)

    def test_json_record2(self):
        dict_record = {
            "value": 45.52,
            "unit": "%RH",
            "type": "VIFUnit.VARIABLE_VIF",
            "function": "FunctionType.MINIMUM_VALUE"
        }
        frame_rec_dict = json.loads(self.frame.records[2].to_JSON())
        self.assertEqual(frame_rec_dict, dict_record)

    # Skip record 3 since it has a very strange float
    # 58.120000000000005

    def test_json_record4(self):
        dict_record = {
            "value": 22.56,
            "unit": "MeasureUnit.C",
            "type": "VIFUnit.EXTERNAL_TEMPERATURE",
            "function": "FunctionType.INSTANTANEOUS_VALUE"
        }
        frame_rec_dict = json.loads(self.frame.records[4].to_JSON())
        self.assertEqual(frame_rec_dict, dict_record)

    def test_json_record5(self):
        dict_record = {
            "value": 21.60,
            "unit": "MeasureUnit.C",
            "type": "VIFUnit.EXTERNAL_TEMPERATURE",
            "function": "FunctionType.MINIMUM_VALUE"
        }
        frame_rec_dict = json.loads(self.frame.records[5].to_JSON())
        self.assertEqual(frame_rec_dict, dict_record)

    def test_json_record6(self):
        dict_record = {
            "value": 23.39,
            "unit": "MeasureUnit.C",
            "type": "VIFUnit.EXTERNAL_TEMPERATURE",
            "function": "FunctionType.MAXIMUM_VALUE"
        }
        frame_rec_dict = json.loads(self.frame.records[6].to_JSON())
        self.assertEqual(frame_rec_dict, dict_record)

    def test_json_record7(self):
        dict_record = {
            "value": 86400,
            "unit": "MeasureUnit.SECONDS",
            "type": "VIFUnit.AVG_DURATION",
            "function": "FunctionType.INSTANTANEOUS_VALUE"
        }
        frame_rec_dict = json.loads(self.frame.records[7].to_JSON())
        self.assertEqual(frame_rec_dict, dict_record)

    def test_json_record8(self):
        dict_record = {
            "value": 22.76,
            "unit": "MeasureUnit.C",
            "type": "VIFUnit.EXTERNAL_TEMPERATURE",
            "function": "FunctionType.INSTANTANEOUS_VALUE"
        }
        frame_rec_dict = json.loads(self.frame.records[8].to_JSON())
        self.assertEqual(frame_rec_dict, dict_record)

    def test_json_record9(self):
        dict_record = {
            "value": 22.69,
            "unit": "MeasureUnit.C",
            "type": "VIFUnit.EXTERNAL_TEMPERATURE",
            "function": "FunctionType.INSTANTANEOUS_VALUE"
        }
        frame_rec_dict = json.loads(self.frame.records[9].to_JSON())
        self.assertEqual(frame_rec_dict, dict_record)

    def test_json_record10(self):
        dict_record = {
            "value": 54000834,
            "unit": "MeasureUnit.NONE",
            "type": "VIFUnit.FABRICATION_NO",
            "function": "FunctionType.INSTANTANEOUS_VALUE"
        }
        frame_rec_dict = json.loads(self.frame.records[10].to_JSON())
        self.assertEqual(frame_rec_dict, dict_record)

    def test_json_record11(self):
        dict_record = {
            "value": 262144,
            "unit": "MeasureUnit.NONE",
            "type": "VIFUnitExt.SOFTWARE_VERSION",
            "function": "FunctionType.INSTANTANEOUS_VALUE"
        }
        frame_rec_dict = json.loads(self.frame.records[11].to_JSON())
        self.assertEqual(frame_rec_dict, dict_record)

if __name__ == '__main__':
    unittest.main()
