from __future__ import annotations

from meterbus.api import decode
from meterbus.model import DecodeMode, Severity, UnknownRecord


def _checksum(data: bytes) -> int:
    return sum(data) & 0xFF


def _long_variable_frame(application_data: bytes) -> bytes:
    payload = bytes.fromhex("21 00 00 00 B0 5C 02 1B 12 00 00 00") + application_data
    body = bytes([0x08, 0x0B, 0x72]) + payload
    return bytes([0x68, len(body), len(body), 0x68]) + body + bytes([_checksum(body), 0x16])


def test_strict_mode_keeps_record_decode_failure_fatal():
    result = decode(_long_variable_frame(bytes([0x02, 0x78, 0x01])), mode=DecodeMode.STRICT)

    assert result.ok is False
    assert result.diagnostics[-1].severity is Severity.FATAL
    assert result.diagnostics[-1].code == "record_decode_error"
    assert result.telegram.records == ()
    assert result.telegram.undecoded_data == bytes([0x02, 0x78, 0x01])


def test_lenient_mode_preserves_undecodable_record_as_unknown_record():
    result = decode(_long_variable_frame(bytes([0x02, 0x78, 0x01])), mode=DecodeMode.LENIENT)

    assert result.ok is True
    assert result.diagnostics[-1].severity is Severity.ERROR
    assert result.diagnostics[-1].code == "record_decode_error"
    assert result.telegram.undecoded_data == b""
    assert len(result.telegram.records) == 1

    record = result.telegram.records[0]
    assert isinstance(record, UnknownRecord)
    assert record.raw == bytes([0x02, 0x78, 0x01])
    assert record.reason == "not enough bytes for value"
    assert record.diagnostics == (result.diagnostics[-1],)


def test_compat_mode_preserves_undecodable_record_as_unknown_record():
    result = decode(_long_variable_frame(bytes([0x01, 0xFD])), mode=DecodeMode.COMPAT)

    assert result.ok is True
    assert result.diagnostics[-1].severity is Severity.ERROR
    assert result.diagnostics[-1].code == "record_decode_error"
    assert result.telegram.undecoded_data == b""
    assert len(result.telegram.records) == 1

    record = result.telegram.records[0]
    assert isinstance(record, UnknownRecord)
    assert record.raw == bytes([0x01, 0xFD])
    assert record.reason == "VIF extension bit set but VIFE byte is missing"


def test_lenient_mode_preserves_good_records_before_unknown_record():
    application_data = bytes([0x02, 0x75, 0x0A, 0x00, 0x02, 0x78, 0x01])

    result = decode(_long_variable_frame(application_data), mode=DecodeMode.LENIENT)

    assert result.ok is True
    assert len(result.telegram.records) == 2
    assert result.telegram.records[0].value.value == 10
    assert isinstance(result.telegram.records[1], UnknownRecord)
    assert result.telegram.records[1].raw == bytes([0x02, 0x78, 0x01])
    assert result.telegram.undecoded_data == b""
