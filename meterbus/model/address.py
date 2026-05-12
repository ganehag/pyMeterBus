"""Address value objects for pyMeterBus 2.0."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PrimaryAddress:
    """Primary M-Bus address.

    The model keeps validation intentionally small for now. Stricter policy can
    be added by encoder/decoder work without changing callers that already pass
    valid addresses.
    """

    value: int

    def __post_init__(self) -> None:
        if not 0 <= self.value <= 255:
            raise ValueError("primary address must fit in one byte")


@dataclass(frozen=True)
class SecondaryAddress:
    """Secondary address fields from a variable data header."""

    identification_number: str
    manufacturer: str | None
    manufacturer_raw: bytes
    version: int
    medium: int
