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
        pass

    def year_to_tuple_int(self, year):
        hundred = None
        if year > 127 and year < 1900:
            return 0, 0
        elif year >= 1900 and year <= 2200:
            hundred = ((year - 1900) // 100) << 6
            year = year % 100

        year = year << 1
        v1 = (year & 0xE) << 4
        v2 = year & 0xF0
        return v1, v2, hundred

    def test_get_time_with_seconds(self):
        self.assertEqual(
            meterbus.DateCalculator.getTimeWithSeconds(45, 23, 1),
            "01:23:45"
        )

    def test_get_time(self):
        self.assertEqual(
            meterbus.DateCalculator.getTime(23, 1),
            "01:23"
        )

    def test_get_date(self):
        self.assertEqual(
            meterbus.DateCalculator.getDate(14, 10, None),
            "2000-10-14"
        )

    def test_get_datetime(self):
        self.assertEqual(
            meterbus.DateCalculator.getDateTime(23, 1, 141, 9, False),
            "2004-09-13T01:23"
        )

    def test_get_datetime(self):
        self.assertEqual(
            meterbus.DateCalculator.getDateTimeWithSeconds(
                45, 23, 1, 141, 9, False),
            "2004-09-13T01:23:45"
        )

    def test_get_seconds(self):
        self.assertEqual(
            meterbus.DateCalculator.getSeconds(237),
            45,
        )

    def test_get_minutes(self):
        self.assertEqual(
            meterbus.DateCalculator.getMinutes(235),
            43,
        )

    def test_get_hour(self):
        self.assertEqual(
            meterbus.DateCalculator.getHour(255),
            31,
        )

    def test_get_day(self):
        self.assertEqual(
            meterbus.DateCalculator.getDay(50),
            18,
        )

    def test_get_month(self):
        self.assertEqual(
            meterbus.DateCalculator.getMonth(20),
            4,
        )

    def test_get_year_1981(self):
        v1, v2, _ = self.year_to_tuple_int(81)
        self.assertEqual(
            meterbus.DateCalculator.getYear(v1, v2, 0, False),
            1981,
        )

    def test_get_year_2080(self):
        v1, v2, _ = self.year_to_tuple_int(80)
        self.assertEqual(
            meterbus.DateCalculator.getYear(v1, v2, 0, False),
            2080,
        )

    def test_get_year_range(self):
        for year in range(1900, 2200):
            v1, v2, v3 = self.year_to_tuple_int(year)
            self.assertEqual(
                meterbus.DateCalculator.getYear(
                    v1, v2, v3, (v3 is not None)),
                year,
            )

if __name__ == '__main__':
    unittest.main()
