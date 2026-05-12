from __future__ import annotations

import pytest

from meterbus.api import decode
from meterbus.codec import DataInformationParseError, parse_dif
from meterbus.model import DataEncoding, FunctionType
from tests.helpers.fixtures import load_hex_fixture


def test_parse_plain_integer_dif():
    result = parse_dif(bytes([0x04]))
    dif = result.data_information

    assert result.consumed == 1
    assert result.data_length == 4
    assert result.has_extension is False
    assert result.is_special_function is False
    assert dif.raw == b"\x04"
    assert dif.data_encoding is DataEncoding.INTEGER
    assert dif.function is FunctionType.INSTANTANEOUS_VALUE
    assert dif.storage_number == 0
    assert dif.tariff is None
    assert dif.subunit is None
    assert dif.extension_bytes == b""


def test_parse_dif_function_bits():
    assert parse_dif(bytes([0x14])).data_information.function is FunctionType.MAXIMUM_VALUE
    assert parse_dif(bytes([0x24])).data_information.function is FunctionType.MINIMUM_VALUE
    assert parse_dif(bytes([0x34])).data_information.function is FunctionType.VALUE_DURING_ERROR_STATE


def test_parse_data_encodings_and_lengths():
    assert parse_dif(bytes([0x00])).data_information.data_encoding is DataEncoding.NO_DATA
    assert parse_dif(bytes([0x05])).data_information.data_encoding is DataEncoding.REAL
    assert parse_dif(bytes([0x09])).data_information.data_encoding is DataEncoding.BCD
    assert parse_dif(bytes([0x0D])).data_information.data_encoding is DataEncoding.VARIABLE_LENGTH
    assert parse_dif(bytes([0x0F])).data_information.data_encoding is DataEncoding.SPECIAL_FUNCTION
    assert parse_dif(bytes([0x0D])).data_length is None
    assert parse_dif(bytes([0x0E])).data_length == 6


def test_parse_dife_extension_metadata():
    result = parse_dif(bytes([0x84, 0x51]))
    dif = result.data_information

    assert result.consumed == 2
    assert result.data_length == 4
    assert result.has_extension is True
    assert dif.raw == b"\x84\x51"
    assert dif.extension_bytes == b"\x51"
    assert dif.storage_number == 3
    assert dif.tariff == 1
    assert dif.subunit == 1


def test_parse_multiple_dife_extension_bytes():
    result = parse_dif(bytes([0x84, 0x81, 0x22]))
    dif = result.data_information

    assert result.consumed == 3
    assert dif.extension_bytes == b"\x81\x22"
    assert dif.storage_number == 69
    assert dif.tariff == 8
    assert dif.subunit == 0


def test_parse_special_function_dif():
    result = parse_dif(bytes([0x0F]))

    assert result.consumed == 1
    assert result.data_length == 0
    assert result.is_special_function is True
    assert result.data_information.data_encoding is DataEncoding.SPECIAL_FUNCTION


def test_parse_first_dif_from_long_fixture_undecoded_data():
    telegram = decode(load_hex_fixture("frames/long_basic.hex").data).telegram

    result = parse_dif(telegram.undecoded_data)
    dif = result.data_information

    assert result.consumed == 1
    assert result.data_length == 4
    assert dif.raw == b"\x0C"
    assert dif.data_encoding is DataEncoding.BCD
    assert dif.function is FunctionType.INSTANTANEOUS_VALUE
    assert dif.storage_number == 0


def test_parse_dif_accepts_input_sequence_types():
    assert parse_dif(bytearray([0x04])).data_information.raw == b"\x04"
    assert parse_dif(memoryview(b"\x04")).data_information.raw == b"\x04"
    assert parse_dif([0x04]).data_information.raw == b"\x04"
    assert parse_dif((0x04,)).data_information.raw == b"\x04"


def test_parse_dif_rejects_empty_input():
    with pytest.raises(DataInformationParseError, match="empty input"):
        parse_dif(b"")


def test_parse_dif_rejects_missing_dife():
    with pytest.raises(DataInformationParseError, match="DIFE byte is missing"):
        parse_dif(bytes([0x84]))


def test_parse_dif_rejects_unsupported_input_type():
    with pytest.raises(TypeError, match="unsupported DIF input type"):
        parse_dif(object())
