"""Checksum and CRC helpers for M-Bus frames."""

from __future__ import annotations

_EN_13757_CRC_POLYNOMIAL = 0x3D65
_EN_13757_CRC_INITIAL = 0x0000
_EN_13757_CRC_XOROUT = 0xFFFF
_CRC_WIDTH_MASK = 0xFFFF
_CRC_TOP_BIT = 0x8000


def checksum(data: bytes) -> int:
    """Return the M-Bus checksum for a sequence of bytes.

    M-Bus frame checksum is the low byte of the sum over the frame-specific
    checksum range.
    """

    return sum(data) & 0xFF


def crc16_en13757(data: bytes | bytearray | memoryview) -> int:
    """Return the EN 13757 CRC-16 value for `data`.

    EN 13757-3 Annex G uses this CRC for both the Format Signature and the
    Full-Frame-CRC. The polynomial is::

        x^16 + x^13 + x^12 + x^11 + x^10 + x^8 + x^6 + x^5 + x^2 + 1

    which corresponds to 0x3D65. The initial value is 0 and the final CRC is
    complemented.
    """

    crc = _EN_13757_CRC_INITIAL
    for byte in bytes(data):
        crc ^= byte << 8
        for _ in range(8):
            if crc & _CRC_TOP_BIT:
                crc = ((crc << 1) ^ _EN_13757_CRC_POLYNOMIAL) & _CRC_WIDTH_MASK
            else:
                crc = (crc << 1) & _CRC_WIDTH_MASK
    return crc ^ _EN_13757_CRC_XOROUT


def crc16_en13757_bytes(data: bytes | bytearray | memoryview, *, byteorder: str = "big") -> bytes:
    """Return the EN 13757 CRC-16 as two bytes.

    The numeric CRC is independent of byte order. Callers must choose the byte
    order required by the specific frame field they are serializing or
    comparing.
    """

    return crc16_en13757(data).to_bytes(2, byteorder)
