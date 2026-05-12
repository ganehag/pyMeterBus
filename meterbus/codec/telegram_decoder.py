"""Application telegram decoder for pyMeterBus 2.0.

This decoder recognizes variable-data telegrams carried by long frames with
CI 0x72 or 0x76, and fixed-data telegrams carried by long frames with CI 0x73
or 0x77.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from meterbus.model import (
    DecodeMode,
    DecodeResult,
    Diagnostic,
    FixedDataCounter,
    FixedDataHeader,
    FixedDataMediumUnit,
    FixedDataTelegram,
    FixedDataUnit,
    LongFrame,
    Severity,
    UnknownRecord,
    VariableDataHeader,
    VariableDataTelegram,
)

from .frame_decoder import FrameDecoder
from .record import DataRecordDecodeError, decode_record

_VARIABLE_DATA_CI_MODE_1 = 0x72
_VARIABLE_DATA_CI_MODE_2 = 0x76
_FIXED_DATA_CI_MODE_1 = 0x73
_FIXED_DATA_CI_MODE_2 = 0x77
_VARIABLE_DATA_HEADER_LENGTH = 12
_FIXED_DATA_HEADER_LENGTH = 8
_FIXED_DATA_COUNTER_LENGTH = 4
_FIXED_DATA_MINIMUM_LENGTH = _FIXED_DATA_HEADER_LENGTH + (2 * _FIXED_DATA_COUNTER_LENGTH)
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

_FIXED_DATA_UNITS = {
    0x00: "h_m_s",
    0x01: "d_m_y",
    0x02: "Wh",
    0x03: "Wh_10",
    0x04: "Wh_100",
    0x05: "kWh",
    0x06: "kWh_10",
    0x07: "kWh_100",
    0x08: "MWh",
    0x09: "MWh_10",
    0x0A: "MWh_100",
    0x0B: "kJ",
    0x0C: "kJ_10",
    0x0D: "kJ_100",
    0x0E: "MJ",
    0x0F: "MJ_10",
    0x10: "MJ_100",
    0x11: "GJ",
    0x12: "GJ_10",
    0x13: "GJ_100",
    0x14: "W",
    0x15: "W_10",
    0x16: "W_100",
    0x17: "kW",
    0x18: "kW_10",
    0x19: "kW_100",
    0x1A: "MW",
    0x1B: "MW_10",
    0x1C: "MW_100",
    0x1D: "kJ_h",
    0x1E: "kJ_h_10",
    0x1F: "kJ_h_100",
    0x20: "MJ_h",
    0x21: "MJ_h_10",
    0x22: "MJ_h_100",
    0x23: "GJ_h",
    0x24: "GJ_h_10",
    0x25: "GJ_h_100",
    0x26: "ml",
    0x27: "ml_10",
    0x28: "ml_100",
    0x29: "l",
    0x2A: "l_10",
    0x2B: "l_100",
    0x2C: "m3",
    0x2D: "m3_10",
    0x2E: "m3_100",
    0x2F: "ml_h",
    0x30: "ml_h_10",
    0x31: "ml_h_100",
    0x32: "l_h",
    0x33: "l_h_10",
    0x34: "l_h_100",
    0x35: "m3_h",
    0x36: "m3_h_10",
    0x37: "m3_h_100",
    0x38: "degC_0_001",
    0x39: "heat_cost_allocator_units",
    0x3A: "reserved",
    0x3B: "reserved",
    0x3C: "reserved",
    0x3D: "reserved",
    0x3E: "same_but_historic",
    0x3F: "without_units",
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

        return DecodeResult(
            ok=frame_result.ok,
            telegram=None,
            frame=frame,
            diagnostics=frame_result.diagnostics,
            raw=frame_result.raw,
        )


def _decode_variable_data_result(frame_result: DecodeResult, mode: DecodeMode) -> DecodeResult:
    frame = frame_result.frame
    assert isinstance(frame, LongFrame)

    diagnostics = list(frame_result.diagnostics)
    if len(frame.payload) < _VARIABLE_DATA_HEADER_LENGTH:
        diagnostics.append(
            Diagnostic(
                severity=Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR,
                code="truncated_variable_data_header",
                message="Variable data telegram is too short to contain a complete header.",
                context={
                    "expected_minimum_length": _VARIABLE_DATA_HEADER_LENGTH,
                    "actual_length": len(frame.payload),
                },
            )
        )
        return DecodeResult(
            ok=False,
            telegram=None,
            frame=frame,
            diagnostics=tuple(diagnostics),
            raw=frame_result.raw,
        )

    header = decode_variable_data_header(frame.payload[:_VARIABLE_DATA_HEADER_LENGTH])
    application_data = frame.payload[_VARIABLE_DATA_HEADER_LENGTH:]
    records, undecoded_data, more_records_follow, record_diagnostics = _decode_records(
        application_data,
        mode,
        lsb_order=frame.ci == _VARIABLE_DATA_CI_MODE_1,
    )
    diagnostics.extend(record_diagnostics)

    telegram = VariableDataTelegram(
        frame=frame,
        diagnostics=tuple(diagnostics),
        header=header,
        records=tuple(records),
        more_records_follow=more_records_follow,
        raw_application_data=application_data,
        undecoded_data=undecoded_data,
    )
    return DecodeResult(
        ok=not any(diagnostic.severity is Severity.FATAL for diagnostic in diagnostics),
        telegram=telegram,
        frame=frame,
        diagnostics=tuple(diagnostics),
        raw=frame_result.raw,
    )


def _decode_fixed_data_result(frame_result: DecodeResult, mode: DecodeMode) -> DecodeResult:
    frame = frame_result.frame
    assert isinstance(frame, LongFrame)

    diagnostics = list(frame_result.diagnostics)
    if len(frame.payload) < _FIXED_DATA_MINIMUM_LENGTH:
        diagnostics.append(
            Diagnostic(
                severity=Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR,
                code="truncated_fixed_data_telegram",
                message="Fixed data telegram is too short to contain its header and two counters.",
                context={
                    "expected_minimum_length": _FIXED_DATA_MINIMUM_LENGTH,
                    "actual_length": len(frame.payload),
                },
            )
        )
        return DecodeResult(
            ok=False,
            telegram=None,
            frame=frame,
            diagnostics=tuple(diagnostics),
            raw=frame_result.raw,
        )

    lsb_order = frame.ci == _FIXED_DATA_CI_MODE_1
    header = decode_fixed_data_header(frame.payload[:_FIXED_DATA_HEADER_LENGTH], lsb_order=lsb_order)
    counter_data = frame.payload[_FIXED_DATA_HEADER_LENGTH:_FIXED_DATA_MINIMUM_LENGTH]
    counters = (
        _decode_fixed_data_counter(1, counter_data[:_FIXED_DATA_COUNTER_LENGTH], lsb_order=lsb_order),
        _decode_fixed_data_counter(2, counter_data[_FIXED_DATA_COUNTER_LENGTH:], lsb_order=lsb_order),
    )
    undecoded_data = frame.payload[_FIXED_DATA_MINIMUM_LENGTH:]

    telegram = FixedDataTelegram(
        frame=frame,
        diagnostics=tuple(diagnostics),
        header=header,
        counters=counters,
        raw_application_data=frame.payload,
        undecoded_data=undecoded_data,
    )
    return DecodeResult(
        ok=not any(diagnostic.severity is Severity.FATAL for diagnostic in diagnostics),
        telegram=telegram,
        frame=frame,
        diagnostics=tuple(diagnostics),
        raw=frame_result.raw,
    )


def decode_variable_data_header(raw: bytes) -> VariableDataHeader:
    """Decode the fixed 12-byte variable data header."""

    if len(raw) != _VARIABLE_DATA_HEADER_LENGTH:
        raise ValueError("variable data header must be exactly 12 bytes")

    return VariableDataHeader(
        identification_number=_decode_bcd_identification(raw[0:4], lsb_order=True),
        manufacturer=_decode_manufacturer(raw[4:6], lsb_order=True),
        manufacturer_raw=raw[4:6],
        version=raw[6],
        medium=raw[7],
        access_number=raw[8],
        status=raw[9],
        signature=raw[10:12],
        raw=raw,
    )


def decode_fixed_data_header(raw: bytes, *, lsb_order: bool = True) -> FixedDataHeader:
    """Decode the fixed 8-byte fixed-data response header."""

    if len(raw) != _FIXED_DATA_HEADER_LENGTH:
        raise ValueError("fixed data header must be exactly 8 bytes")

    medium_unit_raw = raw[6:8]
    return FixedDataHeader(
        identification_number=_decode_bcd_identification(raw[0:4], lsb_order=lsb_order),
        access_number=raw[4],
        status=raw[5],
        medium_unit_raw=medium_unit_raw,
        medium_unit=decode_fixed_data_medium_unit(medium_unit_raw),
        raw=raw,
    )


def decode_fixed_data_medium_unit(raw: bytes) -> FixedDataMediumUnit:
    """Decode the fixed-data Medium/Unit field.

    The Medium/Unit field is always transmitted least-significant byte first.
    The low six bits of byte 1 are counter 1's unit. The low six bits of byte 2
    are counter 2's unit. The high two bits of both bytes form the 4-bit medium
    code, with byte 2 contributing the two most significant bits.
    """

    if len(raw) != 2:
        raise ValueError("fixed data medium/unit field must be exactly 2 bytes")

    first, second = raw
    counter_1_code = first & 0x3F
    counter_2_code = second & 0x3F
    medium_code = ((second & 0xC0) >> 4) | ((first & 0xC0) >> 6)

    return FixedDataMediumUnit(
        raw=raw,
        medium_code=medium_code,
        medium=_FIXED_DATA_MEDIA[medium_code],
        counter_1_unit=FixedDataUnit(counter_1_code, _FIXED_DATA_UNITS[counter_1_code]),
        counter_2_unit=FixedDataUnit(counter_2_code, _FIXED_DATA_UNITS[counter_2_code]),
    )


def _decode_fixed_data_counter(index: int, raw: bytes, *, lsb_order: bool) -> FixedDataCounter:
    if len(raw) != _FIXED_DATA_COUNTER_LENGTH:
        raise ValueError("fixed data counters must be exactly 4 bytes")
    return FixedDataCounter(index=index, raw=raw, value=_decode_bcd_decimal(raw, lsb_order=lsb_order))


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
            result = decode_record(application_data[offset:], lsb_order=lsb_order)
        except DataRecordDecodeError as exc:
            diagnostic = Diagnostic(
                severity=Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR,
                code="record_decode_error",
                message=str(exc),
                offset=_VARIABLE_DATA_HEADER_LENGTH + offset,
            )
            diagnostics.append(diagnostic)
            if mode is DecodeMode.STRICT:
                return records, application_data[offset:], more_records_follow, diagnostics
            preserved = _preserve_unknown_record(application_data[offset:], str(exc), diagnostic)
            records.append(preserved)
            return records, b"", more_records_follow, diagnostics

        if result.consumed <= 0:
            diagnostic = Diagnostic(
                severity=Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR,
                code="record_decoder_did_not_advance",
                message="Record decoder did not consume any bytes.",
                offset=_VARIABLE_DATA_HEADER_LENGTH + offset,
            )
            diagnostics.append(diagnostic)
            if mode is DecodeMode.STRICT:
                return records, application_data[offset:], more_records_follow, diagnostics
            preserved = _preserve_unknown_record(application_data[offset:], diagnostic.message, diagnostic)
            records.append(preserved)
            return records, b"", more_records_follow, diagnostics

        records.append(result.record)
        offset += result.consumed

    return records, b"", more_records_follow, diagnostics


def _preserve_unknown_record(raw: bytes, reason: str, diagnostic: Diagnostic) -> UnknownRecord:
    return UnknownRecord(
        raw=raw,
        reason=reason,
        diagnostics=(diagnostic,),
    )


def _decode_bcd_identification(raw: bytes, *, lsb_order: bool) -> str:
    """Decode a BCD identification number using the telegram's byte order."""

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
    """Decode a two-byte EN 13757 manufacturer code."""

    manufacturer_raw = raw if lsb_order else bytes(reversed(raw))
    value = manufacturer_raw[0] | (manufacturer_raw[1] << 8)
    return "".join(
        chr(((value >> shift) & 0x1F) + 64)
        for shift in (10, 5, 0)
    )


def decode_telegram(
    data: bytes | bytearray | memoryview | list[int] | tuple[int, ...],
    mode: DecodeMode = DecodeMode.STRICT,
) -> DecodeResult:
    """Decode one application telegram."""

    return TelegramDecoder().decode(data, mode=mode)
