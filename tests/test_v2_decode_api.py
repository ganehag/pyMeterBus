from __future__ import annotations

from decimal import Decimal

import pytest

import meterbus
from meterbus.api import decode, decode_one, decode_one_frame
from meterbus.codec.telegram_decoder import decode_fixed_data_medium_unit
from meterbus.export import to_dict
from meterbus.model import DecodeError, DecodeMode, DecodeResult, FixedDataTelegram, FrameKind, ShortFrame, VariableDataTelegram
from tests.helpers.fixtures import load_hex_fixture


def _checksum(data: bytes) -> int:
    return sum(data) & 0xFF


def _long_variable_frame(application_data: bytes, *, ci: int = 0x72) -> bytes:
    payload = bytes.fromhex("21 00 00 00 B0 5C 02 1B 12 00 00 00") + application_data
    body = bytes([0x08, 0x0B, ci]) + payload
    return bytes([0x68, len(body), len(body), 0x68]) + body + bytes([_checksum(body), 0x16])


def _long_fixed_frame(payload: bytes, *, ci: int = 0x73) -> bytes:
    body = bytes([0x08, 0x0B, ci]) + payload
    return bytes([0x68, len(body), len(body), 0x68]) + body + bytes([_checksum(body), 0x16])


def test_decode_returns_decode_result_with_frame_but_no_telegram_for_short_frame():
    raw = load_hex_fixture("frames/short.hex").data

    result = decode(raw)

    assert isinstance(result, DecodeResult)
    assert result.ok is True
    assert isinstance(result.frame, ShortFrame)
    assert result.frame.kind is FrameKind.SHORT
    assert result.telegram is None
    assert result.raw == raw
    assert result.diagnostics == ()


def test_decode_returns_variable_data_telegram_with_records_for_long_frame():
    raw = load_hex_fixture("frames/long_basic.hex").data

    result = decode(raw)

    assert result.ok is True
    assert isinstance(result.telegram, VariableDataTelegram)
    assert result.telegram.header.identification_number == "00000021"
    assert result.telegram.header.manufacturer == "WEP"
    assert result.telegram.header.version == 2
    assert result.telegram.header.medium == 0x1B
    assert result.telegram.header.access_number == 0x12
    assert result.telegram.header.status == 0
    assert len(result.telegram.records) == 3
    assert result.telegram.records[0].vif.kind == "fabrication_number"
    assert result.telegram.records[1].vif.kind == "manufacturer"
    assert result.telegram.records[2].vif.kind == "dimensionless"
    assert result.telegram.raw_application_data == result.frame.payload[12:]
    assert result.telegram.undecoded_data.startswith(b"\x2F\x2F")


def test_decode_variable_data_mode_1_reverses_lvar_text_characters():
    result = decode(_long_variable_frame(bytes([0x0D, 0xFD, 0x11, 0x03]) + b"ABC"))

    assert result.ok is True
    assert result.frame.ci == 0x72
    assert result.telegram.records[0].vif.kind == "customer"
    assert result.telegram.records[0].value.raw == b"ABC"
    assert result.telegram.records[0].value.value == "CBA"


def test_decode_variable_data_mode_2_keeps_lvar_text_character_order():
    result = decode(_long_variable_frame(bytes([0x0D, 0xFD, 0x11, 0x03]) + b"ABC", ci=0x76))

    assert result.ok is True
    assert result.frame.ci == 0x76
    assert result.telegram.records[0].vif.kind == "customer"
    assert result.telegram.records[0].value.raw == b"ABC"
    assert result.telegram.records[0].value.value == "ABC"


def test_decode_fixed_data_mode_1_telegram():
    payload = bytes.fromhex("21 00 00 00 12 00 2C 01 49 04 00 64 32 10 00 00")

    result = decode(_long_fixed_frame(payload, ci=0x73))

    assert result.ok is True
    assert isinstance(result.telegram, FixedDataTelegram)
    assert result.telegram.application_kind == "fixed_data"
    assert result.telegram.header.identification_number == "00000021"
    assert result.telegram.header.access_number == 0x12
    assert result.telegram.header.status == 0
    assert result.telegram.header.medium_unit_raw == bytes.fromhex("2C 01")
    assert result.telegram.header.medium_unit.medium == "other"
    assert result.telegram.header.medium_unit.counter_1_unit.label == "m3"
    assert result.telegram.header.medium_unit.counter_2_unit.label == "d_m_y"
    assert result.telegram.counters[0].index == 1
    assert result.telegram.counters[0].raw == bytes.fromhex("49 04 00 64")
    assert result.telegram.counters[0].value == Decimal("64000449")
    assert result.telegram.counters[1].index == 2
    assert result.telegram.counters[1].raw == bytes.fromhex("32 10 00 00")
    assert result.telegram.counters[1].value == Decimal("1032")
    assert result.telegram.undecoded_data == b""


def test_decode_fixed_data_mode_2_telegram_keeps_byte_order():
    payload = bytes.fromhex("00 00 00 21 12 00 2C 01 64 00 04 49 00 00 10 32")

    result = decode(_long_fixed_frame(payload, ci=0x77))

    assert result.ok is True
    assert isinstance(result.telegram, FixedDataTelegram)
    assert result.telegram.header.identification_number == "00000021"
    assert result.telegram.counters[0].value == Decimal("64000449")
    assert result.telegram.counters[1].value == Decimal("1032")


def test_decode_fixed_data_medium_unit_from_spec_example():
    medium_unit = decode_fixed_data_medium_unit(bytes.fromhex("E9 7E"))

    assert medium_unit.raw == bytes.fromhex("E9 7E")
    assert medium_unit.medium_code == 0x07
    assert medium_unit.medium == "water"
    assert medium_unit.counter_1_unit.code == 0x29
    assert medium_unit.counter_1_unit.label == "l"
    assert medium_unit.counter_2_unit.code == 0x3E
    assert medium_unit.counter_2_unit.label == "same_but_historic"


def test_decode_fixed_data_medium_unit_mode_2_medium_code():
    medium_unit = decode_fixed_data_medium_unit(bytes.fromhex("EA BE"))

    assert medium_unit.medium_code == 0x0A
    assert medium_unit.medium == "gas_mode_2"
    assert medium_unit.counter_1_unit.label == "l_10"
    assert medium_unit.counter_2_unit.label == "same_but_historic"


def test_decode_fixed_data_medium_unit_rejects_wrong_length():
    with pytest.raises(ValueError, match="medium/unit field must be exactly 2 bytes"):
        decode_fixed_data_medium_unit(b"\x00")


def test_decode_fixed_data_preserves_trailing_bytes():
    payload = bytes.fromhex("21 00 00 00 12 00 2C 01 49 04 00 64 32 10 00 00 AA BB")

    result = decode(_long_fixed_frame(payload, ci=0x73))

    assert result.ok is True
    assert isinstance(result.telegram, FixedDataTelegram)
    assert result.telegram.undecoded_data == b"\xAA\xBB"


def test_decode_fixed_data_rejects_truncated_payload():
    payload = bytes.fromhex("21 00 00 00 12 00 2C 01 49 04")

    result = decode(_long_fixed_frame(payload, ci=0x73), mode=DecodeMode.STRICT)

    assert result.ok is False
    assert result.telegram is None
    assert result.diagnostics[-1].code == "truncated_fixed_data_telegram"


def test_fixed_data_telegram_exports_to_dict():
    payload = bytes.fromhex("21 00 00 00 12 00 E9 7E 01 00 00 00 35 01 00 00")

    exported = to_dict(decode(_long_fixed_frame(payload, ci=0x73)).telegram)

    assert exported["application_kind"] == "fixed_data"
    assert exported["header"]["identification_number"] == "00000021"
    assert exported["header"]["medium_unit"]["medium"] == "water"
    assert exported["header"]["medium_unit"]["counter_1_unit"]["label"] == "l"
    assert exported["header"]["medium_unit"]["counter_2_unit"]["label"] == "same_but_historic"
    assert exported["counters"][0]["value"] == "1"
    assert exported["counters"][1]["value"] == "135"


def test_decode_is_exposed_from_meterbus_package_root():
    raw = load_hex_fixture("frames/ack.hex").data

    result = meterbus.decode(raw)

    assert result.ok is True
    assert result.frame.kind is FrameKind.ACK


def test_decode_one_frame_returns_frame_or_raises_decode_error():
    raw = load_hex_fixture("frames/short.hex").data

    frame = decode_one_frame(raw)

    assert isinstance(frame, ShortFrame)

    with pytest.raises(DecodeError) as exc_info:
        decode_one_frame(b"\x00")

    assert exc_info.value.diagnostics[0].code == "invalid_start_byte"


def test_decode_one_frame_supports_lenient_mode():
    raw = bytearray(load_hex_fixture("frames/short.hex").data)
    raw[3] = 0x00

    frame = decode_one_frame(bytes(raw), mode=DecodeMode.LENIENT)

    assert isinstance(frame, ShortFrame)
    assert frame.checksum_valid is False


def test_decode_one_returns_variable_data_telegram():
    raw = load_hex_fixture("frames/long_basic.hex").data

    telegram = decode_one(raw)

    assert isinstance(telegram, VariableDataTelegram)
    assert telegram.header.identification_number == "00000021"
    assert len(telegram.records) == 3


def test_decode_one_raises_when_no_application_telegram_is_available():
    raw = load_hex_fixture("frames/short.hex").data

    with pytest.raises(DecodeError) as exc_info:
        decode_one(raw)

    assert str(exc_info.value) == "application telegram decoding is not available for this frame"


def test_decode_preserves_frame_decoder_errors_in_decode_result():
    result = decode(b"")

    assert result.ok is False
    assert result.frame is None
    assert result.telegram is None
    assert result.diagnostics[0].code == "empty_input"
