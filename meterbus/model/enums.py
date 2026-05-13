"""Core enums for the pyMeterBus 2.0 model layer."""

from __future__ import annotations

from enum import Enum


class StrEnum(str, Enum):
    """String-valued enum with stable JSON-friendly values."""

    def __str__(self) -> str:
        return self.value


class DecodeMode(StrEnum):
    STRICT = "strict"
    LENIENT = "lenient"
    COMPAT = "compat"


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"


class FrameKind(StrEnum):
    ACK = "ack"
    SHORT = "short"
    CONTROL = "control"
    LONG = "long"
    WIRELESS = "wireless"
    UNKNOWN = "unknown"


class ApplicationKind(StrEnum):
    NONE = "none"
    VARIABLE_DATA = "variable_data"
    FIXED_DATA = "fixed_data"
    COMPACT_DATA = "compact_data"
    FORMAT_DATA = "format_data"
    MANUFACTURER_SPECIFIC = "manufacturer_specific"
    ENCRYPTED = "encrypted"
    UNKNOWN = "unknown"


class ValueType(StrEnum):
    NONE = "none"
    INTEGER = "integer"
    DECIMAL = "decimal"
    STRING = "string"
    BINARY = "binary"
    DATE = "date"
    DATETIME = "datetime"
    UNKNOWN = "unknown"


class DataEncoding(StrEnum):
    NO_DATA = "no_data"
    INTEGER = "integer"
    BCD = "bcd"
    REAL = "real"
    VARIABLE_LENGTH = "variable_length"
    SPECIAL_FUNCTION = "special_function"
    UNKNOWN = "unknown"


class FunctionType(StrEnum):
    INSTANTANEOUS_VALUE = "instantaneous_value"
    MAXIMUM_VALUE = "maximum_value"
    MINIMUM_VALUE = "minimum_value"
    VALUE_DURING_ERROR_STATE = "value_during_error_state"
    SPECIAL_FUNCTION = "special_function"
    UNKNOWN = "unknown"


class Direction(StrEnum):
    MASTER_TO_SLAVE = "master_to_slave"
    SLAVE_TO_MASTER = "slave_to_master"
    UNKNOWN = "unknown"


class ControlFunction(StrEnum):
    SND_NKE = "snd_nke"
    SND_UD = "snd_ud"
    REQ_UD1 = "req_ud1"
    REQ_UD2 = "req_ud2"
    RSP_UD = "rsp_ud"
    UNKNOWN = "unknown"
