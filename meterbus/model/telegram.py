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
class FixedDataHeader:
    """Fixed data response header fields plus raw bytes."""

    identification_number: str
    access_number: int
    status: int
    medium_unit_raw: bytes
    raw: bytes


@dataclass(frozen=True)
class FixedDataCounter:
    """One fixed data counter value."""

    index: int
    raw: bytes
    value: Decimal


@dataclass(frozen=True)
class FixedDataTelegram(Telegram):
    """Fixed data telegram with the two fixed counters."""

    header: FixedDataHeader | None = None
    counters: tuple[FixedDataCounter, ...] = ()
    raw_application_data: bytes = b""
    undecoded_data: bytes = b""
    application_kind: ApplicationKind = ApplicationKind.FIXED_DATA
