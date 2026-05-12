"""Decoded value model for pyMeterBus 2.0."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from .enums import ValueType


@dataclass(frozen=True)
class Unit:
    """A protocol unit label.

    This is deliberately small for the model layer. Table-driven VIF decoding
    can later decide which canonical unit labels are emitted.
    """

    name: str
    symbol: str | None = None


@dataclass(frozen=True)
class DecodedValue:
    """A decoded record value plus its original raw bytes."""

    raw: bytes
    value: Any | None
    type: ValueType
    unit: Unit | None = None
    scaled: bool = False


NumberValue = int | Decimal
