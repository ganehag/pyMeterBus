from __future__ import annotations

from decimal import Decimal

from meterbus.api import decode
from meterbus.codec.compact import expand_compact_telegram
from meterbus.model import CompactDataTelegram, FormatDataTelegram


def _checksum(data: bytes) -> int:
    return sum(data) & 0xFF


def _long_application_frame(payload: bytes, *, ci: int) -> bytes:
    body = bytes([0x08, 0x0B, ci]) + payload
    return bytes([0x68, len(body), len(body), 0x68]) + body + bytes([_checksum(body), 0x16])


def _format_frame(format_data: bytes, *, signature: bytes = b"\x12\x34") -> bytes:
    return _long_application_frame(bytes([0x00]) + signature + format_data, ci=0x69)


def _compact_frame(compact_data: bytes, *, signature: bytes = b"\x12\x34", crc: bytes = b"\xAB\xCD") -> bytes:
    return _long_application_frame(signature + crc + compact_data, ci=0x79)


def test_expand_compact_telegram_accepts_raw_descriptors_without_signature_check():
    fmt = decode(_format_frame(bytes.fromhex("02 03 04 05"))).telegram
    compact = decode(_compact_frame(bytes.fromhex("34 12 78 56 34 12"), signature=b"\xAA\xBB")).telegram

    assert isinstance(fmt, FormatDataTelegram)
    assert isinstance(compact, CompactDataTelegram)

    result = expand_compact_telegram(compact, fmt.descriptors)

    assert result.diagnostics == ()
    assert result.undecoded_data == b""
    assert len(result.records) == 2
    assert result.records[0].raw == bytes.fromhex("02 03 34 12")
    assert result.records[0].vif.kind == "energy"
    assert result.records[0].value.value == 4660
    assert result.records[0].value.unit.symbol == "Wh"
    assert result.records[1].raw == bytes.fromhex("04 05 78 56 34 12")
    assert result.records[1].vif.kind == "energy"
    assert result.records[1].vif.multiplier == Decimal("100")
    assert result.records[1].value.value == Decimal("30541989600")
    assert result.records[1].value.scaled is True


def test_expand_compact_telegram_checks_matching_format_signature_when_template_is_format_telegram():
    fmt = decode(_format_frame(bytes.fromhex("02 03"), signature=b"\x12\x34")).telegram
    compact = decode(_compact_frame(bytes.fromhex("34 12"), signature=b"\x12\x34")).telegram

    assert isinstance(fmt, FormatDataTelegram)
    assert isinstance(compact, CompactDataTelegram)

    result = expand_compact_telegram(compact, fmt)

    assert result.diagnostics == ()
    assert len(result.records) == 1
    assert result.records[0].value.value == 4660
    assert result.undecoded_data == b""


def test_expand_compact_telegram_rejects_mismatched_format_signature():
    fmt = decode(_format_frame(bytes.fromhex("02 03"), signature=b"\x12\x34")).telegram
    compact = decode(_compact_frame(bytes.fromhex("34 12"), signature=b"\xAA\xBB")).telegram

    assert isinstance(fmt, FormatDataTelegram)
    assert isinstance(compact, CompactDataTelegram)

    result = expand_compact_telegram(compact, fmt)

    assert result.records == ()
    assert result.undecoded_data == bytes.fromhex("34 12")
    assert result.diagnostics[-1].code == "compact_format_signature_mismatch"
    assert result.diagnostics[-1].context["compact_format_signature"] == b"\xAA\xBB"
    assert result.diagnostics[-1].context["template_format_signature"] == b"\x12\x34"


def test_expand_compact_telegram_applies_vif_scaling():
    fmt = decode(_format_frame(bytes.fromhex("02 00"))).telegram
    compact = decode(_compact_frame(bytes.fromhex("34 12"))).telegram

    assert isinstance(fmt, FormatDataTelegram)
    assert isinstance(compact, CompactDataTelegram)

    result = expand_compact_telegram(compact, fmt)

    assert result.diagnostics == ()
    assert len(result.records) == 1
    assert result.records[0].vif.kind == "energy"
    assert result.records[0].vif.unit.symbol == "Wh"
    assert result.records[0].vif.multiplier == Decimal("0.001")
    assert result.records[0].value.value == Decimal("4.660")
    assert result.records[0].value.scaled is True


def test_expand_compact_telegram_preserves_extra_value_bytes():
    fmt = decode(_format_frame(bytes.fromhex("02 03"))).telegram
    compact = decode(_compact_frame(bytes.fromhex("34 12 AA BB"))).telegram

    assert isinstance(fmt, FormatDataTelegram)
    assert isinstance(compact, CompactDataTelegram)

    result = expand_compact_telegram(compact, fmt)

    assert result.diagnostics == ()
    assert len(result.records) == 1
    assert result.records[0].value.value == 4660
    assert result.undecoded_data == bytes.fromhex("AA BB")


def test_expand_compact_telegram_preserves_truncated_value_tail():
    fmt = decode(_format_frame(bytes.fromhex("02 03 04 05"))).telegram
    compact = decode(_compact_frame(bytes.fromhex("34 12 78 56"))).telegram

    assert isinstance(fmt, FormatDataTelegram)
    assert isinstance(compact, CompactDataTelegram)

    result = expand_compact_telegram(compact, fmt)

    assert len(result.records) == 1
    assert result.records[0].value.value == 4660
    assert result.undecoded_data == bytes.fromhex("78 56")
    assert result.diagnostics[-1].code == "compact_value_decode_error"
    assert result.diagnostics[-1].context["descriptor_index"] == 2
