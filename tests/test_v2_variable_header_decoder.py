from __future__ import annotations

import pytest

from meterbus.api import decode
from meterbus.codec import decode_variable_data_header
from meterbus.model import ApplicationKind, DecodeMode, VariableDataHeader, VariableDataTelegram
from tests.helpers.fixtures import load_hex_fixture


def test_decode_variable_data_header_from_long_frame_payload():
    payload = load_hex_fixture("frames/long_basic.hex").data[7:-2]

    header = decode_variable_data_header(payload[:12])

    assert isinstance(header, VariableDataHeader)
    assert header.identification_number == "00000021"
    assert header.manufacturer == "WEP"
    assert header.manufacturer_raw == b"\xB0\x5C"
    assert header.version == 2
    assert header.medium == 0x1B
    assert header.access_number == 0x12
    assert header.status == 0
    assert header.signature == b"\x00\x00"
    assert header.raw == payload[:12]


def test_decode_variable_data_header_rejects_wrong_length():
    with pytest.raises(ValueError, match="exactly 12 bytes"):
        decode_variable_data_header(b"\x00")


def test_decode_long_variable_data_frame_returns_header_only_telegram():
    raw = load_hex_fixture("frames/long_basic.hex").data

    result = decode(raw)

    assert result.ok is True
    assert isinstance(result.telegram, VariableDataTelegram)
    assert result.telegram.application_kind is ApplicationKind.VARIABLE_DATA
    assert result.telegram.frame is result.frame
    assert result.telegram.header.identification_number == "00000021"
    assert result.telegram.header.manufacturer == "WEP"
    assert result.telegram.records == ()
    assert result.telegram.raw_application_data == result.frame.payload[12:]
    assert result.telegram.undecoded_data == result.frame.payload[12:]


def test_decode_short_frame_still_has_no_telegram():
    result = decode(load_hex_fixture("frames/short.hex").data)

    assert result.ok is True
    assert result.telegram is None


def test_truncated_variable_data_header_fails_in_strict_mode():
    raw = bytearray(load_hex_fixture("frames/control.hex").data)
    raw[6] = 0x72

    result = decode(bytes(raw), mode=DecodeMode.STRICT)

    assert result.ok is False
    assert result.telegram is None
    assert result.diagnostics[0].code == "truncated_variable_data_header"
