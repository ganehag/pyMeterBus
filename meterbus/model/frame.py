"""Frame value objects for pyMeterBus 2.0."""

from __future__ import annotations

from dataclasses import dataclass

from .address import PrimaryAddress
from .diagnostics import Diagnostic
from .enums import ControlFunction, Direction, FrameKind


@dataclass(frozen=True)
class ControlField:
    """Decoded M-Bus control field metadata."""

    raw: int
    direction: Direction | None = None
    function: ControlFunction | None = None
    fcb: bool | None = None
    fcv: bool | None = None

    def __post_init__(self) -> None:
        if not 0 <= self.raw <= 255:
            raise ValueError("control field must fit in one byte")


@dataclass(frozen=True, init=False)
class Frame:
    """Base frame model preserving raw bytes and diagnostics."""

    kind: FrameKind
    raw: bytes
    checksum: int | None
    checksum_valid: bool | None
    diagnostics: tuple[Diagnostic, ...]


@dataclass(frozen=True)
class AckFrame(Frame):
    """Single-byte ACK frame."""

    raw: bytes = b"\xE5"
    checksum: int | None = None
    checksum_valid: bool | None = None
    diagnostics: tuple[Diagnostic, ...] = ()
    kind: FrameKind = FrameKind.ACK


@dataclass(frozen=True)
class ShortFrame(Frame):
    """Short frame: 10 C A CS 16."""

    raw: bytes = b""
    checksum: int | None = None
    checksum_valid: bool | None = None
    diagnostics: tuple[Diagnostic, ...] = ()
    control: ControlField = ControlField(raw=0)
    address: PrimaryAddress = PrimaryAddress(0)
    kind: FrameKind = FrameKind.SHORT


@dataclass(frozen=True)
class ControlFrame(Frame):
    """Control frame with length 3."""

    raw: bytes = b""
    checksum: int | None = None
    checksum_valid: bool | None = None
    diagnostics: tuple[Diagnostic, ...] = ()
    length: int = 3
    control: ControlField = ControlField(raw=0)
    address: PrimaryAddress = PrimaryAddress(0)
    ci: int = 0
    kind: FrameKind = FrameKind.CONTROL


@dataclass(frozen=True)
class LongFrame(Frame):
    """Long frame carrying application payload bytes."""

    raw: bytes = b""
    checksum: int | None = None
    checksum_valid: bool | None = None
    diagnostics: tuple[Diagnostic, ...] = ()
    length: int = 0
    control: ControlField = ControlField(raw=0)
    address: PrimaryAddress = PrimaryAddress(0)
    ci: int = 0
    payload: bytes = b""
    kind: FrameKind = FrameKind.LONG
