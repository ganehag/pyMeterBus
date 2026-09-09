"""Decode result model for pyMeterBus 2.0."""

from __future__ import annotations

from dataclasses import dataclass

from .diagnostics import Diagnostic
from .frame import Frame
from .telegram import Telegram


@dataclass(frozen=True)
class DecodeResult:
    """Aggregate result returned by non-throwing decode APIs.

    ``ok`` means that no fatal diagnostic was produced in the selected decode
    mode. Recoverable error or warning diagnostics may still be present.
    ``diagnostics`` contains the ordered aggregate from every decode stage.
    """

    ok: bool
    telegram: Telegram | None
    frame: Frame | None
    diagnostics: tuple[Diagnostic, ...]
    raw: bytes
