from __future__ import annotations

from decimal import Decimal

import meterbus.codec.compact as compact_codec
from meterbus.api import decode
from meterbus.codec.compact import expand_compact_telegram
from meterbus.codec.crc import crc16_en13757_bytes
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


def _full_frame_crc_for_recovered_data(recovered_application_data: bytes) -> bytes:
    return crc16_en13757_bytes(recovered_application_data)


def test_expand_compact_telegram_accepts_raw_descriptors_without_signature_or_crc_check():
    fmt = decode(_format_frame(bytes.fromhex("02 03 04 05"))).telegram
    compact = decode(_compact_frame(bytes.fromhex("34 12 78 56 34 12"), signature=b"\xAA\xBB", crc=b"\x00\x00")).telegram

    assert isinstance(fmt, FormatDataTelegram)
    assert isinstance(compact, CompactDataTelegram)

    result = expand_compact_telegram(compact, fmt.descriptors)

    assert result.diagnostics == ()
    assert result.undecoded_data == b""
    assert result.recovered_application_data == bytes.fromhex("02 03 34 12 04 05 78 56 34 12")
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


def test_expand_compact_telegram_checks_matching_format_signature_and_full_frame_crc():
    format_data = bytes.fromhex("02 03")
    compact_data = bytes.fromhex("34 12")
    recovered_application_data = bytes.fromhex("02 03 34 12")
    full_frame_crc = _full_frame_crc_for_recovered_data(recovered_application_data)
    fmt = decode(_format_frame(format_data, signature=b"\x12\x34")).telegram
    compact = decode(_compact_frame(compact_data, signature=b"\x12\x34", crc=full_frame_crc)).telegram

    assert isinstance(fmt, FormatDataTelegram)
    assert isinstance(compact, CompactDataTelegram)

    result = expand_compact_telegram(compact, fmt)

    assert result.diagnostics == ()
    assert result.recovered_application_data == recovered_application_data
    assert len(result.records) == 1
    assert result.records[0].value.value == 4660
    assert result.undecoded_data == b""


def test_expand_compact_telegram_reports_full_frame_crc_mismatch():
    fmt = decode(_format_frame(bytes.fromhex("02 03"), signature=b"\x12\x34")).telegram
    compact = decode(_compact_frame(bytes.fromhex("34 12"), signature=b"\x12\x34", crc=b"\x00\x00")).telegram

    assert isinstance(fmt, FormatDataTelegram)
    assert isinstance(compact, CompactDataTelegram)

    result = expand_compact_telegram(compact, fmt)

    assert len(result.records) == 1
    assert result.undecoded_data == b""
    assert result.recovered_application_data == bytes.fromhex("02 03 34 12")
    assert result.diagnostics[-1].code == "compact_full_frame_crc_mismatch"
    assert result.diagnostics[-1].context["transmitted_full_frame_crc"] == b"\x00\x00"
    assert result.diagnostics[-1].context["calculated_full_frame_crc"] == _full_frame_crc_for_recovered_data(bytes.fromhex("02 03 34 12"))


def test_expand_compact_telegram_rejects_mismatched_format_signature_before_crc_validation():
    fmt = decode(_format_frame(bytes.fromhex("02 03"), signature=b"\x12\x34")).telegram
    compact = decode(_compact_frame(bytes.fromhex("34 12"), signature=b"\xAA\xBB", crc=b"\x00\x00")).telegram

    assert isinstance(fmt, FormatDataTelegram)
    assert isinstance(compact, CompactDataTelegram)

    result = expand_compact_telegram(compact, fmt)

    assert result.records == ()
    assert result.undecoded_data == bytes.fromhex("34 12")
    assert result.recovered_application_data == b""
    assert result.diagnostics[-1].code == "compact_format_signature_mismatch"
    assert result.diagnostics[-1].context["compact_format_signature"] == b"\xAA\xBB"
    assert result.diagnostics[-1].context["template_format_signature"] == b"\x12\x34"


def test_expand_compact_telegram_applies_vif_scaling():
    fmt = decode(_format_frame(bytes.fromhex("02 00"))).telegram
    compact_data = bytes.fromhex("34 12")
    full_frame_crc = _full_frame_crc_for_recovered_data(bytes.fromhex("02 00 34 12"))
    compact = decode(_compact_frame(compact_data, crc=full_frame_crc)).telegram

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


def test_expand_compact_telegram_preserves_extra_value_bytes_without_crc_validation():
    fmt = decode(_format_frame(bytes.fromhex("02 03"))).telegram
    compact = decode(_compact_frame(bytes.fromhex("34 12 AA BB"))).telegram

    assert isinstance(fmt, FormatDataTelegram)
    assert isinstance(compact, CompactDataTelegram)

    result = expand_compact_telegram(compact, fmt)

    assert result.diagnostics == ()
    assert len(result.records) == 1
    assert result.records[0].value.value == 4660
    assert result.undecoded_data == bytes.fromhex("AA BB")
    assert result.recovered_application_data == bytes.fromhex("02 03 34 12")


def test_expand_compact_telegram_preserves_truncated_value_tail_without_crc_validation():
    fmt = decode(_format_frame(bytes.fromhex("02 03 04 05"))).telegram
    compact = decode(_compact_frame(bytes.fromhex("34 12 78 56"))).telegram

    assert isinstance(fmt, FormatDataTelegram)
    assert isinstance(compact, CompactDataTelegram)

    result = expand_compact_telegram(compact, fmt)

    assert len(result.records) == 1
    assert result.records[0].value.value == 4660
    assert result.undecoded_data == bytes.fromhex("78 56")
    assert result.recovered_application_data == bytes.fromhex("02 03 34 12")
    assert result.diagnostics[-1].code == "compact_value_decode_error"
    assert result.diagnostics[-1].context["descriptor_index"] == 2


def test_expand_compact_data_passes_shared_buffer_with_offsets(monkeypatch):
    fmt = decode(_format_frame(bytes.fromhex("02 03 04 05"))).telegram
    compact_data = bytes.fromhex("34 12 78 56 34 12")
    offsets = []
    decode_value_at = compact_codec._decode_value_at

    def observe_offset(raw, offset, *args, **kwargs):
        assert raw is compact_data
        offsets.append(offset)
        return decode_value_at(raw, offset, *args, **kwargs)

    monkeypatch.setattr(compact_codec, "_decode_value_at", observe_offset)

    result = compact_codec.expand_compact_data(compact_data, fmt.descriptors)

    assert result.diagnostics == ()
    assert offsets == [0, 2]
