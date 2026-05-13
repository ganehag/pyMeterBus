"""Telegram model for pyMeterBus 2.0."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .diagnostics import Diagnostic
from .enums import ApplicationKind
from .frame import Frame
from .record import DataRecord, UnknownRecord


@dataclass(frozen=True)
class Telegram:
    """Base application-level telegram."""

    frame: Frame
    application_kind: ApplicationKind
    diagnostics: tuple[Diagnostic, ...] = ()


@dataclass(frozen=True)
class VariableDataHeader:
    """Variable data header fields plus raw bytes."""

    identification_number: str | None
    manufacturer: str | None
    manufacturer_raw: bytes
    version: int | None
    medium: int | None
    access_number: int | None
    status: int | None
    signature: bytes
    raw: bytes


@dataclass(frozen=True)
class VariableDataTelegram(Telegram):
    """Variable data telegram with decoded records."""

    header: VariableDataHeader | None = None
    records: tuple[DataRecord | UnknownRecord, ...] = ()
    more_records_follow: bool = False
    raw_application_data: bytes = b""
    undecoded_data: bytes = b""
    application_kind: ApplicationKind = ApplicationKind.VARIABLE_DATA


@dataclass(frozen=True)
class FixedDataUnit:
    """Fixed data unit code from the low six bits of a medium/unit byte."""

    code: int
    label: str
    symbol: str | None = None
    multiplier: Decimal | None = None


@dataclass(frozen=True)
class FixedDataMediumUnit:
    """Decoded fixed data medium/unit field."""

    raw: bytes
    medium_code: int
    medium: str
    counter_1_unit: FixedDataUnit
    counter_2_unit: FixedDataUnit


@dataclass(frozen=True)
class FixedDataHeader:
    """Fixed data response header fields plus raw bytes."""

    identification_number: str
    access_number: int
    status: int
    medium_unit_raw: bytes
    medium_unit: FixedDataMediumUnit | None
    raw: bytes


@dataclass(frozen=True)
class FixedDataCounter:
    """One fixed data counter value."""

    index: int
    raw: bytes
    value: Decimal
    unit: FixedDataUnit | None = None
    scaled_value: Decimal | None = None


@dataclass(frozen=True)
class FixedDataTelegram(Telegram):
    """Fixed data telegram with the two fixed counters."""

    header: FixedDataHeader | None = None
    counters: tuple[FixedDataCounter, ...] = ()
    raw_application_data: bytes = b""
    undecoded_data: bytes = b""
    application_kind: ApplicationKind = ApplicationKind.FIXED_DATA


@dataclass(frozen=True)
class CompactDataTelegram(Telegram):
    """Compact M-Bus frame shell.

    Compact records require a matching format/full-frame template before they
    can be expanded safely. This model intentionally preserves the payload
    without guessing record boundaries.
    """

    raw_application_data: bytes = b""
    format_signature: bytes | None = None
    full_frame_crc: bytes | None = None
    compact_data: bytes = b""
    application_kind: ApplicationKind = ApplicationKind.COMPACT_DATA


@dataclass(frozen=True)
class FormatDataTelegram(Telegram):
    """Format M-Bus frame shell.

    A later decoder can turn the raw format payload into record descriptors.
    This first-pass model only recognizes and preserves the format frame.
    """

    raw_application_data: bytes = b""
    length_field: int | None = None
    format_signature: bytes | None = None
    format_data: bytes = b""
    application_kind: ApplicationKind = ApplicationKind.FORMAT_DATA
