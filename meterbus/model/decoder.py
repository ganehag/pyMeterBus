"""Decode result model for pyMeterBus 2.0."""

from __future__ import annotations

from dataclasses import dataclass

from .diagnostics import Diagnostic
from .frame import Frame
from .telegram import Telegram


@dataclass(frozen=True)
class DecodeResult:
    """Result returned by non-throwing decode APIs."""

    ok: bool
    telegram: Telegram | None
    frame: Frame | None
    diagnostics: tuple[Diagnostic, ...]
    raw: bytes
