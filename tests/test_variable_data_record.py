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
        self.frame2 = "\x68\xD8\xD8\x68\x08\x00\x72\x92\x03\x00\x64\x96\x15" \
                      "\x14\x31\x04\x00\x00\x00\x0C\x78\x92\x03\x00\x64\x0D" \
                      "\xFD\x0F\x05\x33\x2E\x36\x2E\x31\x0D\x7C\x03\x79\x65" \
                      "\x6B\x10\x0A\xB3\xED\x14\xCD\x07\x58\xD7\xBA\xDE\x3B" \
                      "\x38\xB2\xE6\x96\x0C\x01\x7C\x03\x6F\x6D\x77\x04\x01" \
                      "\x7C\x03\x65\x73\x77\x00\x02\x7C\x03\x74\x69\x77\x3C" \
                      "\x00\x02\x7C\x03\x73\x69\x77\x3C\x00\x01\x7C\x03\x6D" \
                      "\x69\x77\x01\x02\x7C\x03\x65\x67\x61\xA0\x05\x04\x7C" \
                      "\x03\x66\x69\x77\xFF\xFF\xFF\xFF\x01\x7C\x03\x69\x63" \
                      "\x77\x01\x01\x7C\x03\x6F\x6D\x74\x00\x01\x7C\x03\x66" \
                      "\x64\x74\x03\x01\x7C\x03\x64\x63\x6C\x00\x01\x7C\x03" \
                      "\x6E\x61\x6C\x00\x01\x7C\x03\x65\x6C\x73\x05\x0A\xFD" \
                      "\x16\x00\x00\x04\xFD\x0B\x00\x00\x00\x00\x02\x7C\x03" \
                      "\x61\x66\x77\x00\x00\x01\x7C\x03\x66\x69\x61\x01\x04" \
                      "\x7C\x03\x63\x72\x72\xB3\x02\x00\x00\x01\x7C\x03\x61" \
                      "\x74\x73\x00\x01\x7C\x03\x6D\x61\x63\x00\x01\x7C\x03" \
                      "\x6D\x61\x6D\x00\x01\x7C\x03\x66\x63\x69\x01\x1F\x3A" \
                      "\x16"

        self.frame = meterbus.load(self.frame)
        self.frame2 = meterbus.load(self.frame2)

    def test_datafield_set(self):
        tvdr = meterbus.TelegramVariableDataRecord()
        field = meterbus.TelegramField()
        tvdr.dataField = field
        self.assertIs(tvdr.dataField, field)

    def test_vif_mult_oxfc_0x78(self):
        t = meterbus.TelegramVariableDataRecord()
        t.vib.parts = [0xFC, 0x78]
        mult, _, _ = t._parse_vifx()
        self.assertEqual(mult, 0.001)

    def test_vif_mult_oxfc_0x7B(self):
        t = meterbus.TelegramVariableDataRecord()
        t.vib.parts = [0xFC, 0x7B]
        mult, _, _ = t._parse_vifx()
        self.assertEqual(mult, 1.0)

    def test_vif_mult_oxfc_0x7D(self):
        t = meterbus.TelegramVariableDataRecord()
        t.vib.parts = [0xFC, 0x7D]
        mult, _, _ = t._parse_vifx()
        self.assertEqual(mult, 1.0)

    def test_parsed_value_invalid_data_len(self):
        t = meterbus.TelegramVariableDataRecord()
        t.dib.parts = [0x04]
        t.vib.parts = [0xFC, 0x74]
        t.vib.customVIF = meterbus.TelegramField([0x48, 0x52, 0x25])
        t.dataField = meterbus.TelegramField([0xD4, 0x11])
        self.assertEqual(t.parsed_value, None)

    def test_more_records_follow_true(self):
        # Check the last record
        self.assertEqual(
            self.frame.records[-1].more_records_follow,
            True)

    def test_more_records_follow_false(self):
        # Check the second to last record
        self.assertEqual(
            self.frame.records[-2].more_records_follow,
            False)

    def test_verify_function(self):
        self.assertEqual(
            self.frame.records[-1].function, 6)

    def test_verify_float_value(self):
        self.assertEqual(
            self.frame.records[2].value, 45.52)

    def test_verify_str_value(self):
        self.assertEqual(
            self.frame2.records[1].value, "1.6.3")

    def test_verify_ustr_value(self):
        self.assertEqual(
            "0A B3 ED 14 CD 07 58 D7 BA DE 3B 38 B2 E6 96 0C",
            self.frame2.records[2].value)

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

    def test_json_value_str(self):
        key = "0A B3 ED 14 CD 07 58 D7 BA DE 3B 38 B2 E6 96 0C"
        record = json.loads(self.frame2.records[2].to_JSON())
        self.assertEqual(
            record['value'],
            key
        )

if __name__ == '__main__':
    unittest.main()
