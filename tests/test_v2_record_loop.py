from __future__ import annotations

from decimal import Decimal

from meterbus.api import decode
from meterbus.codec.format_descriptor import decode_format_descriptors
from meterbus.codec.telegram_decoder import _decode_records
from meterbus.model import DecodeMode
from tests.helpers.fixtures import load_hex_fixture


_EXPECTED_UNDECODED_AFTER_FILLER = bytes.fromhex(
    "2F 2F 0A 66 20 02 0A FB 1A 31 05 02 FD 97 1D 00 00 "
    "2F 2F 2F 2F 2F 2F 2F 2F 2F 2F 2F 2F 2F 2F 2F"
)


class _NoSuffixSlices(bytes):
    def __getitem__(self, key):
        if isinstance(key, slice) and key.stop is None:
            raise AssertionError("decoder copied an unbounded input suffix")
        return super().__getitem__(key)


def test_variable_data_record_loop_decodes_records_until_filler():
    result = decode(load_hex_fixture("frames/long_basic.hex").data)
    telegram = result.telegram

    assert result.ok is True
    assert len(telegram.records) == 3
    assert telegram.undecoded_data == _EXPECTED_UNDECODED_AFTER_FILLER

    first, second, third = telegram.records

    assert first.raw == bytes.fromhex("0C 78 49 04 00 64")
    assert first.vif.kind == "fabrication_number"
    assert first.value.value == Decimal("64000449")

    assert second.raw == bytes.fromhex("02 75 0A 00")
    assert second.vif.kind == "manufacturer"
    assert second.value.value == 10

    assert third.raw == bytes.fromhex("01 FD 71 1E")
    assert third.vif.kind == "dimensionless"
    assert third.value.value == 30


def test_record_loop_keeps_full_raw_application_data():
    result = decode(load_hex_fixture("frames/long_basic.hex").data)
    telegram = result.telegram

    assert telegram.raw_application_data == result.frame.payload[12:]
    assert telegram.raw_application_data.startswith(telegram.records[0].raw)
    assert telegram.raw_application_data.endswith(telegram.undecoded_data)


def test_record_loop_advances_offsets_without_copying_input_suffixes():
    application_data = _NoSuffixSlices(bytes([0x01, 0x80, 0x00, 0xFF]) * 4)

    records, undecoded_data, more_records_follow, diagnostics = _decode_records(
        application_data,
        DecodeMode.STRICT,
        lsb_order=True,
    )

    assert len(records) == 4
    assert undecoded_data == b""
    assert more_records_follow is False
    assert diagnostics == []


def test_format_descriptor_loop_advances_offsets_without_copying_input_suffixes():
    format_data = _NoSuffixSlices(bytes([0x01, 0x80, 0x00]) * 4)

    result = decode_format_descriptors(format_data)

    assert len(result.descriptors) == 4
    assert result.undecoded_data == b""
    assert result.diagnostics == ()
