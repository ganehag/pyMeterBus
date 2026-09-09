"""DIF/DIFE parser for pyMeterBus 2.0.

This module only parses the Data Information Block metadata. It does not parse
VIF bytes and does not decode record values.
"""

from __future__ import annotations

from dataclasses import dataclass

from meterbus.model import DataEncoding, DataInformation, FunctionType


_DATA_LENGTH_BY_LOW_NIBBLE = {
    0x0: 0,
    0x1: 1,
    0x2: 2,
    0x3: 3,
    0x4: 4,
    0x5: 4,
    0x6: 6,
    0x7: 8,
    0x8: 0,
    0x9: 1,
    0xA: 2,
    0xB: 3,
    0xC: 4,
    0xD: None,
    0xE: 6,
    0xF: 0,
}


@dataclass(frozen=True)
class DataInformationParseResult:
    """Parsed DIF/DIFE metadata plus cursor information."""

    data_information: DataInformation
    consumed: int
    data_length: int | None
    has_extension: bool
    is_special_function: bool


class DataInformationParseError(ValueError):
    """Raised when a DIF/DIFE block is malformed."""


def parse_dif(data: bytes | bytearray | memoryview | list[int] | tuple[int, ...]) -> DataInformationParseResult:
    """Parse one DIF/DIFE block from the start of `data`."""

    raw = _normalize_input(data)
    return _parse_dif_at(raw, 0)


def _parse_dif_at(raw: bytes, start: int) -> DataInformationParseResult:
    """Parse one DIF/DIFE block at `start` without copying the input suffix."""

    if start >= len(raw):
        raise DataInformationParseError("cannot parse DIF from empty input")

    dif = raw[start]
    low_nibble = dif & 0x0F
    extension_bytes: list[int] = []
    offset = start + 1

    while dif & 0x80:
        if offset >= len(raw):
            raise DataInformationParseError("DIF extension bit set but DIFE byte is missing")
        dife = raw[offset]
        extension_bytes.append(dife)
        offset += 1
        if not dife & 0x80:
            break
        if len(extension_bytes) >= 10:
            raise DataInformationParseError("too many DIFE extension bytes")

    data_information = DataInformation(
        raw=raw[start:offset],
        data_encoding=_decode_data_encoding(low_nibble),
        function=_decode_function(dif),
        storage_number=_decode_storage_number(dif, extension_bytes),
        tariff=_decode_tariff(extension_bytes) if extension_bytes else None,
        subunit=_decode_subunit(extension_bytes) if extension_bytes else None,
        extension_bytes=bytes(extension_bytes),
    )

    return DataInformationParseResult(
        data_information=data_information,
        consumed=offset - start,
        data_length=_DATA_LENGTH_BY_LOW_NIBBLE[low_nibble],
        has_extension=bool(extension_bytes),
        is_special_function=low_nibble == 0x0F,
    )


def _normalize_input(data: bytes | bytearray | memoryview | list[int] | tuple[int, ...]) -> bytes:
    if isinstance(data, bytes):
        return data
    if isinstance(data, bytearray):
        return bytes(data)
    if isinstance(data, memoryview):
        return data.tobytes()
    if isinstance(data, (list, tuple)):
        return bytes(data)
    raise TypeError(f"unsupported DIF input type: {type(data).__name__}")


def _decode_data_encoding(low_nibble: int) -> DataEncoding:
    if low_nibble == 0x0:
        return DataEncoding.NO_DATA
    if 0x1 <= low_nibble <= 0x4 or 0x6 <= low_nibble <= 0x7:
        return DataEncoding.INTEGER
    if low_nibble == 0x5:
        return DataEncoding.REAL
    if 0x9 <= low_nibble <= 0xC or low_nibble == 0xE:
        return DataEncoding.BCD
    if low_nibble == 0xD:
        return DataEncoding.VARIABLE_LENGTH
    if low_nibble == 0xF:
        return DataEncoding.SPECIAL_FUNCTION
    return DataEncoding.UNKNOWN


def _decode_function(dif: int) -> FunctionType:
    function_bits = (dif >> 4) & 0x03
    if function_bits == 0:
        return FunctionType.INSTANTANEOUS_VALUE
    if function_bits == 1:
        return FunctionType.MAXIMUM_VALUE
    if function_bits == 2:
        return FunctionType.MINIMUM_VALUE
    if function_bits == 3:
        return FunctionType.VALUE_DURING_ERROR_STATE
    return FunctionType.UNKNOWN


def _decode_storage_number(dif: int, extension_bytes: list[int]) -> int:
    storage_number = (dif >> 6) & 0x01
    for index, dife in enumerate(extension_bytes):
        storage_number |= (dife & 0x0F) << (1 + 4 * index)
    return storage_number


def _decode_tariff(extension_bytes: list[int]) -> int:
    tariff = 0
    for index, dife in enumerate(extension_bytes):
        tariff |= ((dife >> 4) & 0x03) << (2 * index)
    return tariff


def _decode_subunit(extension_bytes: list[int]) -> int:
    subunit = 0
    for index, dife in enumerate(extension_bytes):
        subunit |= ((dife >> 6) & 0x01) << index
    return subunit
