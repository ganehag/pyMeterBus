import decimal
import json
import unittest

import meterbus


class TestDecimalScaling(unittest.TestCase):
    def test_reported_heat_meter_frame(self):
        # Recorded telegram from #34, referenced by the precision report #41.
        frame = meterbus.load(bytes.fromhex(
            '684d4d680800722654832277040904360000000c7826548322040649350000'
            '0c14490508000b2d0000000b3b0000000a5a18060a5e89020b61883200'
            '046d0d0c2c310227c80309fd0e2209fd0f470f00008d16'))
        decoded = json.loads(frame.to_JSON(), parse_float=decimal.Decimal)
        expected = {2: '805.49', 5: '61.8', 6: '28.9', 7: '32.88'}
        for index, value in expected.items():
            with self.subTest(index=index):
                self.assertEqual(frame.records[index].parsed_value,
                                 decimal.Decimal(value))
                self.assertEqual(decoded['body']['records'][index]['value'],
                                 decimal.Decimal(value))

    def test_integer_scaling_is_exact(self):
        for raw, vif, expected in [
            (80549, 0x14, '805.49'),
            (-99, 0x2A, '-9.9'),
            (0, 0x14, '0'),
        ]:
            with self.subTest(raw=raw):
                record = meterbus.TelegramVariableDataRecord()
                record.dib.parts = [0x04]  # Signed 32-bit integer
                record.vib.parts = [vif]
                record.dataField = meterbus.TelegramField(
                    list(raw.to_bytes(4, 'little', signed=True)))
                self.assertEqual(record.parsed_value, decimal.Decimal(expected))

    def test_integral_multiplier_retains_integer_result(self):
        record = meterbus.TelegramVariableDataRecord()
        record.dib.parts = [0x04]
        record.vib.parts = [0x06]  # 1000 Wh
        record.dataField = meterbus.TelegramField([0x49, 0x35, 0, 0])
        self.assertEqual(record.parsed_value, 13641000)
        self.assertIsInstance(record.parsed_value, int)
