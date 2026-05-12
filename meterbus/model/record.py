"""Data record model for pyMeterBus 2.0."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .diagnostics import Diagnostic
from .enums import DataEncoding, FunctionType
from .value import DecodedValue, Unit


@dataclass(frozen=True)
class DataInformation:
    """Data Information Block metadata."""

    raw: bytes
    data_encoding: DataEncoding
    function: FunctionType
    storage_number: int
    tariff: int | None = None
    subunit: int | None = None
    extension_bytes: bytes = b""


@dataclass(frozen=True)
class ValueInformation:
    """Value Information Block metadata."""

    raw: bytes
    unit: Unit | None
    kind: str | None
    multiplier: Decimal
    extension_bytes: bytes = b""
    custom_vif: bytes | None = None
    enhancement: str | None = None


@dataclass(frozen=True)
class DataRecord:
    """A decoded variable data record."""

    raw: bytes
    dif: DataInformation
    vif: ValueInformation
    value: DecodedValue
    function: FunctionType | None
    storage_number: int | None
    tariff: int | None = None
    subunit: int | None = None
    more_records_follow: bool = False
    diagnostics: tuple[Diagnostic, ...] = ()


@dataclass(frozen=True)
class UnknownRecord:
    """A record whose bytes were preserved but not decoded."""

    raw: bytes
    reason: str
    diagnostics: tuple[Diagnostic, ...] = ()
