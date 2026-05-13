from __future__ import annotations

from meterbus.codec.crc import checksum, crc16_en13757, crc16_en13757_bytes


def test_mbus_checksum_low_byte_sum_is_unchanged():
    assert checksum(bytes.fromhex("08 0B 72 21 00")) == 0xA6


def test_crc16_en13757_empty_data_is_complemented_initial_value():
    assert crc16_en13757(b"") == 0xFFFF


def test_crc16_en13757_standard_check_value():
    assert crc16_en13757(b"123456789") == 0xC2B7


def test_crc16_en13757_accepts_bytearray_and_memoryview():
    data = bytearray(b"123456789")

    assert crc16_en13757(data) == 0xC2B7
    assert crc16_en13757(memoryview(data)) == 0xC2B7


def test_crc16_en13757_bytes_uses_requested_byte_order():
    assert crc16_en13757_bytes(b"123456789") == bytes.fromhex("C2 B7")
    assert crc16_en13757_bytes(b"123456789", byteorder="little") == bytes.fromhex("B7 C2")
