"""Error hierarchy for pyMeterBus 2.0."""

from __future__ import annotations

from .diagnostics import Diagnostic


class MeterBusError(Exception):
    """Base class for pyMeterBus 2.0 errors."""


class DecodeError(MeterBusError):
    """Raised by strict convenience APIs when decoding fails."""

    def __init__(self, message: str, diagnostics: tuple[Diagnostic, ...] = ()) -> None:
        super().__init__(message)
        self.diagnostics = diagnostics


class EncodeError(MeterBusError):
    """Raised when a model object cannot be encoded."""


class ChecksumError(DecodeError):
    """Raised when a frame checksum is invalid in strict mode."""


class LengthError(DecodeError):
    """Raised when frame length fields are invalid in strict mode."""


class UnsupportedFeatureError(MeterBusError):
    """Raised when a requested feature is intentionally not implemented."""
