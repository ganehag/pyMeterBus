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
    FixedDataTelegram,
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

    return FixedDataHeader(
        identification_number=_decode_bcd_identification(raw[0:4], lsb_order=lsb_order),
        access_number=raw[4],
        status=raw[5],
        medium_unit_raw=raw[6:8],
        raw=raw,
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
