"""Checksum helpers for M-Bus frames."""

from __future__ import annotations


def checksum(data: bytes) -> int:
    """Return the M-Bus checksum for a sequence of bytes.

    M-Bus frame checksum is the low byte of the sum over the frame-specific
    checksum range.
    """

    return sum(data) & 0xFF
