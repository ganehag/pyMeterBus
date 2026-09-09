"""Application telegram decoder for pyMeterBus 2.0."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from meterbus.model import (
    CompactDataTelegram,
    DecodeMode,
    DecodeResult,
    Diagnostic,
    FixedDataCounter,
    FixedDataHeader,
    FixedDataMediumUnit,
    FixedDataTelegram,
    FixedDataUnit,
    FormatDataTelegram,
    LongFrame,
    Severity,
    UnknownRecord,
    VariableDataHeader,
    VariableDataTelegram,
)

from .format_descriptor import decode_format_descriptors
from .frame_decoder import FrameDecoder
from .record import DataRecordDecodeError, _decode_record_at

_VARIABLE_DATA_CI_MODE_1 = 0x72
_VARIABLE_DATA_CI_MODE_2 = 0x76
_FIXED_DATA_CI_MODE_1 = 0x73
_FIXED_DATA_CI_MODE_2 = 0x77
_COMPACT_DATA_CI_NO_HEADER = 0x79
_COMPACT_DATA_CI_SHORT_HEADER = 0x7B
_COMPACT_DATA_CI_LONG_HEADER = 0x73
_FORMAT_DATA_CI_NO_HEADER = 0x69
_FORMAT_DATA_CI_SHORT_HEADER = 0x6A
_FORMAT_DATA_CI_LONG_HEADER = 0x6B
_VARIABLE_DATA_HEADER_LENGTH = 12
_FIXED_DATA_HEADER_LENGTH = 8
_FIXED_DATA_COUNTER_LENGTH = 4
_FIXED_DATA_MINIMUM_LENGTH = _FIXED_DATA_HEADER_LENGTH + (2 * _FIXED_DATA_COUNTER_LENGTH)
_WIRELESS_SHORT_DATA_HEADER_LENGTH = 6
_WIRELESS_LONG_DATA_HEADER_LENGTH = 14
_FORMAT_LENGTH_FIELD_LENGTH = 1
_FORMAT_SIGNATURE_LENGTH = 2
_FULL_FRAME_CRC_LENGTH = 2
_FILLER_BYTE = 0x2F
_MANUFACTURER_SPECIFIC_DATA = 0x0F
_MANUFACTURER_SPECIFIC_DATA_MORE_RECORDS = 0x1F

_FIXED_DATA_MEDIA = {
    0x0: "other",
    0x1: "oil",
    0x2: "electricity",
    0x3: "gas",
    0x4: "heat",
    0x5: "steam",
    0x6: "hot_water",
    0x7: "water",
    0x8: "heat_cost_allocator",
    0x9: "reserved",
    0xA: "gas_mode_2",
    0xB: "heat_mode_2",
    0xC: "hot_water_mode_2",
    0xD: "water_mode_2",
    0xE: "heat_cost_allocator_mode_2",
    0xF: "reserved",
}

_FIXED_DATA_UNIT_SPECS: dict[int, tuple[str, str | None, Decimal | None]] = {
    0x00: ("h_m_s", None, None),
    0x01: ("d_m_y", None, None),
    0x02: ("Wh", "Wh", Decimal("1")),
    0x03: ("Wh_10", "Wh", Decimal("10")),
    0x04: ("Wh_100", "Wh", Decimal("100")),
    0x05: ("kWh", "kWh", Decimal("1")),
    0x06: ("kWh_10", "kWh", Decimal("10")),
    0x07: ("kWh_100", "kWh", Decimal("100")),
    0x08: ("MWh", "MWh", Decimal("1")),
    0x09: ("MWh_10", "MWh", Decimal("10")),
    0x0A: ("MWh_100", "MWh", Decimal("100")),
    0x0B: ("kJ", "kJ", Decimal("1")),
    0x0C: ("kJ_10", "kJ", Decimal("10")),
    0x0D: ("kJ_100", "kJ", Decimal("100")),
    0x0E: ("MJ", "MJ", Decimal("1")),
    0x0F: ("MJ_10", "MJ", Decimal("10")),
    0x10: ("MJ_100", "MJ", Decimal("100")),
    0x11: ("GJ", "GJ", Decimal("1")),
    0x12: ("GJ_10", "GJ", Decimal("10")),
    0x13: ("GJ_100", "GJ", Decimal("100")),
    0x14: ("W", "W", Decimal("1")),
    0x15: ("W_10", "W", Decimal("10")),
    0x16: ("W_100", "W", Decimal("100")),
    0x17: ("kW", "kW", Decimal("1")),
    0x18: ("kW_10", "kW", Decimal("10")),
    0x19: ("kW_100", "kW", Decimal("100")),
    0x1A: ("MW", "MW", Decimal("1")),
    0x1B: ("MW_10", "MW", Decimal("10")),
    0x1C: ("MW_100", "MW", Decimal("100")),
    0x1D: ("kJ_h", "kJ/h", Decimal("1")),
    0x1E: ("kJ_h_10", "kJ/h", Decimal("10")),
    0x1F: ("kJ_h_100", "kJ/h", Decimal("100")),
    0x20: ("MJ_h", "MJ/h", Decimal("1")),
    0x21: ("MJ_h_10", "MJ/h", Decimal("10")),
    0x22: ("MJ_h_100", "MJ/h", Decimal("100")),
    0x23: ("GJ_h", "GJ/h", Decimal("1")),
    0x24: ("GJ_h_10", "GJ/h", Decimal("10")),
    0x25: ("GJ_h_100", "GJ/h", Decimal("100")),
    0x26: ("ml", "ml", Decimal("1")),
    0x27: ("ml_10", "ml", Decimal("10")),
    0x28: ("ml_100", "ml", Decimal("100")),
    0x29: ("l", "l", Decimal("1")),
    0x2A: ("l_10", "l", Decimal("10")),
    0x2B: ("l_100", "l", Decimal("100")),
    0x2C: ("m3", "m^3", Decimal("1")),
    0x2D: ("m3_10", "m^3", Decimal("10")),
    0x2E: ("m3_100", "m^3", Decimal("100")),
    0x2F: ("ml_h", "ml/h", Decimal("1")),
    0x30: ("ml_h_10", "ml/h", Decimal("10")),
    0x31: ("ml_h_100", "ml/h", Decimal("100")),
    0x32: ("l_h", "l/h", Decimal("1")),
    0x33: ("l_h_10", "l/h", Decimal("10")),
    0x34: ("l_h_100", "l/h", Decimal("100")),
    0x35: ("m3_h", "m^3/h", Decimal("1")),
    0x36: ("m3_h_10", "m^3/h", Decimal("10")),
    0x37: ("m3_h_100", "m^3/h", Decimal("100")),
    0x38: ("degC_0_001", "degC", Decimal("0.001")),
    0x39: ("heat_cost_allocator_units", "HCA", Decimal("1")),
    0x3A: ("reserved", None, None),
    0x3B: ("reserved", None, None),
    0x3C: ("reserved", None, None),
    0x3D: ("reserved", None, None),
    0x3E: ("same_but_historic", None, None),
    0x3F: ("without_units", None, None),
}


@dataclass(frozen=True)
class TelegramDecoder:
    """Decode application-level telegrams from frame envelopes."""

    frame_decoder: FrameDecoder = FrameDecoder()

    def decode(
        self,
        data: bytes | bytearray | memoryview | list[int] | tuple[int, ...],
        mode: DecodeMode = DecodeMode.STRICT,
    ) -> DecodeResult:
        frame_result = self.frame_decoder.decode(data, mode=mode)
        if frame_result.frame is None or not frame_result.ok:
            return DecodeResult(
                ok=frame_result.ok,
                telegram=None,
                frame=frame_result.frame,
                diagnostics=frame_result.diagnostics,
                raw=frame_result.raw,
            )

        frame = frame_result.frame
        if not isinstance(frame, LongFrame):
            return DecodeResult(
                ok=frame_result.ok,
                telegram=None,
                frame=frame,
                diagnostics=frame_result.diagnostics,
                raw=frame_result.raw,
            )

        if frame.ci in (_VARIABLE_DATA_CI_MODE_1, _VARIABLE_DATA_CI_MODE_2):
            return _decode_variable_data_result(frame_result, mode)
        if frame.ci in (_FIXED_DATA_CI_MODE_1, _FIXED_DATA_CI_MODE_2):
            return _decode_fixed_data_result(frame_result, mode)
        if frame.ci in (_COMPACT_DATA_CI_NO_HEADER, _COMPACT_DATA_CI_SHORT_HEADER):
            return _decode_compact_data_result(frame_result)
        if frame.ci in (_FORMAT_DATA_CI_NO_HEADER, _FORMAT_DATA_CI_SHORT_HEADER, _FORMAT_DATA_CI_LONG_HEADER):
            return _decode_format_data_result(frame_result)

        return DecodeResult(ok=frame_result.ok, telegram=None, frame=frame, diagnostics=frame_result.diagnostics, raw=frame_result.raw)


def _decode_variable_data_result(frame_result: DecodeResult, mode: DecodeMode) -> DecodeResult:
    frame = frame_result.frame
    assert isinstance(frame, LongFrame)
    diagnostics = list(frame_result.diagnostics)

    if len(frame.payload) < _VARIABLE_DATA_HEADER_LENGTH:
        diagnostics.append(Diagnostic(severity=Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR, code="truncated_variable_data_header", message="Variable data telegram is too short to contain a complete header.", context={"expected_minimum_length": _VARIABLE_DATA_HEADER_LENGTH, "actual_length": len(frame.payload)}))
        return DecodeResult(ok=False, telegram=None, frame=frame, diagnostics=tuple(diagnostics), raw=frame_result.raw)

    header = decode_variable_data_header(frame.payload[:_VARIABLE_DATA_HEADER_LENGTH])
    application_data = frame.payload[_VARIABLE_DATA_HEADER_LENGTH:]
    records, undecoded_data, more_records_follow, record_diagnostics = _decode_records(application_data, mode, lsb_order=frame.ci == _VARIABLE_DATA_CI_MODE_1)
    diagnostics.extend(record_diagnostics)
    telegram = VariableDataTelegram(frame=frame, diagnostics=tuple(diagnostics), header=header, records=tuple(records), more_records_follow=more_records_follow, raw_application_data=application_data, undecoded_data=undecoded_data)
    return DecodeResult(ok=not any(diagnostic.severity is Severity.FATAL for diagnostic in diagnostics), telegram=telegram, frame=frame, diagnostics=tuple(diagnostics), raw=frame_result.raw)


def _decode_fixed_data_result(frame_result: DecodeResult, mode: DecodeMode) -> DecodeResult:
    frame = frame_result.frame
    assert isinstance(frame, LongFrame)
    diagnostics = list(frame_result.diagnostics)

    if len(frame.payload) < _FIXED_DATA_MINIMUM_LENGTH:
        diagnostics.append(Diagnostic(severity=Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR, code="truncated_fixed_data_telegram", message="Fixed data telegram is too short to contain its header and two counters.", context={"expected_minimum_length": _FIXED_DATA_MINIMUM_LENGTH, "actual_length": len(frame.payload)}))
        return DecodeResult(ok=False, telegram=None, frame=frame, diagnostics=tuple(diagnostics), raw=frame_result.raw)

    lsb_order = frame.ci == _FIXED_DATA_CI_MODE_1
    header = decode_fixed_data_header(frame.payload[:_FIXED_DATA_HEADER_LENGTH], lsb_order=lsb_order)
    counter_data = frame.payload[_FIXED_DATA_HEADER_LENGTH:_FIXED_DATA_MINIMUM_LENGTH]
    counter_1_unit = header.medium_unit.counter_1_unit if header.medium_unit is not None else None
    counter_2_unit = header.medium_unit.counter_2_unit if header.medium_unit is not None else None
    counters = (
        _decode_fixed_data_counter(1, counter_data[:_FIXED_DATA_COUNTER_LENGTH], lsb_order=lsb_order, unit=counter_1_unit),
        _decode_fixed_data_counter(2, counter_data[_FIXED_DATA_COUNTER_LENGTH:], lsb_order=lsb_order, unit=counter_2_unit, historic_unit=counter_1_unit),
    )
    undecoded_data = frame.payload[_FIXED_DATA_MINIMUM_LENGTH:]
    telegram = FixedDataTelegram(frame=frame, diagnostics=tuple(diagnostics), header=header, counters=counters, raw_application_data=frame.payload, undecoded_data=undecoded_data)
    return DecodeResult(ok=not any(diagnostic.severity is Severity.FATAL for diagnostic in diagnostics), telegram=telegram, frame=frame, diagnostics=tuple(diagnostics), raw=frame_result.raw)


def _decode_compact_data_result(frame_result: DecodeResult) -> DecodeResult:
    frame = frame_result.frame
    assert isinstance(frame, LongFrame)
    data_header_length = _wireless_data_header_length(frame.ci)
    compact_payload = frame.payload[data_header_length:]
    format_signature = compact_payload[:_FORMAT_SIGNATURE_LENGTH] if len(compact_payload) >= _FORMAT_SIGNATURE_LENGTH else None
    full_frame_crc_end = _FORMAT_SIGNATURE_LENGTH + _FULL_FRAME_CRC_LENGTH
    full_frame_crc = compact_payload[_FORMAT_SIGNATURE_LENGTH:full_frame_crc_end] if len(compact_payload) >= full_frame_crc_end else None
    compact_data = compact_payload[full_frame_crc_end:] if len(compact_payload) >= full_frame_crc_end else b""
    diagnostic = Diagnostic(severity=Severity.WARNING, code="compact_frame_template_required", message="Compact M-Bus frame expansion requires a matching format or full-frame template.", context={"ci": frame.ci, "data_header_length": data_header_length})
    telegram = CompactDataTelegram(frame=frame, diagnostics=(diagnostic,), raw_application_data=frame.payload, format_signature=format_signature, full_frame_crc=full_frame_crc, compact_data=compact_data)
    return DecodeResult(ok=True, telegram=telegram, frame=frame, diagnostics=frame_result.diagnostics + (diagnostic,), raw=frame_result.raw)


def _decode_format_data_result(frame_result: DecodeResult) -> DecodeResult:
    frame = frame_result.frame
    assert isinstance(frame, LongFrame)
    data_header_length = _wireless_data_header_length(frame.ci)
    format_payload = frame.payload[data_header_length:]
    length_field = format_payload[0] if len(format_payload) >= _FORMAT_LENGTH_FIELD_LENGTH else None
    format_signature_end = _FORMAT_LENGTH_FIELD_LENGTH + _FORMAT_SIGNATURE_LENGTH
    format_signature = format_payload[_FORMAT_LENGTH_FIELD_LENGTH:format_signature_end] if len(format_payload) >= format_signature_end else None
    format_data = format_payload[format_signature_end:] if len(format_payload) >= format_signature_end else b""
    descriptor_result = decode_format_descriptors(format_data)
    diagnostics = frame_result.diagnostics + descriptor_result.diagnostics
    telegram = FormatDataTelegram(
        frame=frame,
        diagnostics=descriptor_result.diagnostics,
        raw_application_data=frame.payload,
        length_field=length_field,
        format_signature=format_signature,
        format_data=format_data,
        descriptors=descriptor_result.descriptors,
        undecoded_data=descriptor_result.undecoded_data,
    )
    return DecodeResult(ok=not any(diagnostic.severity is Severity.FATAL for diagnostic in diagnostics), telegram=telegram, frame=frame, diagnostics=diagnostics, raw=frame_result.raw)


def _wireless_data_header_length(ci: int) -> int:
    if ci in (_COMPACT_DATA_CI_SHORT_HEADER, _FORMAT_DATA_CI_SHORT_HEADER):
        return _WIRELESS_SHORT_DATA_HEADER_LENGTH
    if ci == _FORMAT_DATA_CI_LONG_HEADER:
        return _WIRELESS_LONG_DATA_HEADER_LENGTH
    return 0


def decode_variable_data_header(raw: bytes) -> VariableDataHeader:
    if len(raw) != _VARIABLE_DATA_HEADER_LENGTH:
        raise ValueError("variable data header must be exactly 12 bytes")
    return VariableDataHeader(identification_number=_decode_bcd_identification(raw[0:4], lsb_order=True), manufacturer=_decode_manufacturer(raw[4:6], lsb_order=True), manufacturer_raw=raw[4:6], version=raw[6], medium=raw[7], access_number=raw[8], status=raw[9], signature=raw[10:12], raw=raw)


def decode_fixed_data_header(raw: bytes, *, lsb_order: bool = True) -> FixedDataHeader:
    if len(raw) != _FIXED_DATA_HEADER_LENGTH:
        raise ValueError("fixed data header must be exactly 8 bytes")
    medium_unit_raw = raw[6:8]
    return FixedDataHeader(identification_number=_decode_bcd_identification(raw[0:4], lsb_order=lsb_order), access_number=raw[4], status=raw[5], medium_unit_raw=medium_unit_raw, medium_unit=decode_fixed_data_medium_unit(medium_unit_raw), raw=raw)


def decode_fixed_data_medium_unit(raw: bytes) -> FixedDataMediumUnit:
    if len(raw) != 2:
        raise ValueError("fixed data medium/unit field must be exactly 2 bytes")
    first, second = raw
    counter_1_code = first & 0x3F
    counter_2_code = second & 0x3F
    medium_code = ((second & 0xC0) >> 4) | ((first & 0xC0) >> 6)
    return FixedDataMediumUnit(raw=raw, medium_code=medium_code, medium=_FIXED_DATA_MEDIA[medium_code], counter_1_unit=_fixed_data_unit(counter_1_code), counter_2_unit=_fixed_data_unit(counter_2_code))


def _fixed_data_unit(code: int) -> FixedDataUnit:
    label, symbol, multiplier = _FIXED_DATA_UNIT_SPECS[code]
    return FixedDataUnit(code=code, label=label, symbol=symbol, multiplier=multiplier)


def _decode_fixed_data_counter(index: int, raw: bytes, *, lsb_order: bool, unit: FixedDataUnit | None, historic_unit: FixedDataUnit | None = None) -> FixedDataCounter:
    if len(raw) != _FIXED_DATA_COUNTER_LENGTH:
        raise ValueError("fixed data counters must be exactly 4 bytes")
    value = _decode_bcd_decimal(raw, lsb_order=lsb_order)
    scaling_unit = historic_unit if unit is not None and unit.label == "same_but_historic" else unit
    scaled_value = value * scaling_unit.multiplier if scaling_unit is not None and scaling_unit.multiplier is not None else None
    return FixedDataCounter(index=index, raw=raw, value=value, unit=unit, scaled_value=scaled_value)


def _decode_records(application_data: bytes, mode: DecodeMode, *, lsb_order: bool):
    records = []
    diagnostics: list[Diagnostic] = []
    offset = 0
    more_records_follow = False
    while offset < len(application_data):
        if application_data[offset] == _FILLER_BYTE:
            return records, application_data[offset:], more_records_follow, diagnostics
        if application_data[offset] in (_MANUFACTURER_SPECIFIC_DATA, _MANUFACTURER_SPECIFIC_DATA_MORE_RECORDS):
            reason = "manufacturer_specific_data"
            if application_data[offset] == _MANUFACTURER_SPECIFIC_DATA_MORE_RECORDS:
                reason = "manufacturer_specific_data_more_records_follow"
                more_records_follow = True
            records.append(UnknownRecord(raw=application_data[offset:], reason=reason))
            return records, b"", more_records_follow, diagnostics
        try:
            result = _decode_record_at(application_data, offset, lsb_order=lsb_order)
        except DataRecordDecodeError as exc:
            diagnostic = Diagnostic(severity=Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR, code="record_decode_error", message=str(exc), offset=_VARIABLE_DATA_HEADER_LENGTH + offset)
            diagnostics.append(diagnostic)
            if mode is DecodeMode.STRICT:
                return records, application_data[offset:], more_records_follow, diagnostics
            records.append(_preserve_unknown_record(application_data[offset:], str(exc), diagnostic))
            return records, b"", more_records_follow, diagnostics
        if result.consumed <= 0:
            diagnostic = Diagnostic(severity=Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR, code="record_decoder_did_not_advance", message="Record decoder did not consume any bytes.", offset=_VARIABLE_DATA_HEADER_LENGTH + offset)
            diagnostics.append(diagnostic)
            if mode is DecodeMode.STRICT:
                return records, application_data[offset:], more_records_follow, diagnostics
            records.append(_preserve_unknown_record(application_data[offset:], diagnostic.message, diagnostic))
            return records, b"", more_records_follow, diagnostics
        records.append(result.record)
        offset += result.consumed
    return records, b"", more_records_follow, diagnostics


def _preserve_unknown_record(raw: bytes, reason: str, diagnostic: Diagnostic) -> UnknownRecord:
    return UnknownRecord(raw=raw, reason=reason, diagnostics=(diagnostic,))


def _decode_bcd_identification(raw: bytes, *, lsb_order: bool) -> str:
    ordered = reversed(raw) if lsb_order else raw
    digits: list[str] = []
    for byte in ordered:
        digits.append(f"{byte >> 4:X}")
        digits.append(f"{byte & 0x0F:X}")
    return "".join(digits)


def _decode_bcd_decimal(raw: bytes, *, lsb_order: bool) -> Decimal:
    ordered = reversed(raw) if lsb_order else raw
    digits: list[str] = []
    for byte in ordered:
        high = byte >> 4
        low = byte & 0x0F
        if high > 9 or low > 9:
            raise ValueError("BCD value contains non-decimal nibble")
        digits.append(str(high))
        digits.append(str(low))
    return Decimal("".join(digits).lstrip("0") or "0")


def _decode_manufacturer(raw: bytes, *, lsb_order: bool = True) -> str:
    manufacturer_raw = raw if lsb_order else bytes(reversed(raw))
    value = manufacturer_raw[0] | (manufacturer_raw[1] << 8)
    return "".join(chr(((value >> shift) & 0x1F) + 64) for shift in (10, 5, 0))


def decode_telegram(data: bytes | bytearray | memoryview | list[int] | tuple[int, ...], mode: DecodeMode = DecodeMode.STRICT) -> DecodeResult:
    return TelegramDecoder().decode(data, mode=mode)
