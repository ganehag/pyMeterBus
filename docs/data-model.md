# pyMeterBus 2.0 data model

This document defines the proposed data model for pyMeterBus 2.0.

The model should be explicit, immutable where practical, easy to serialize, and portable enough to translate to a future Zig implementation.

## General rules

1. Model objects should be plain data, not parsers.
2. Decoders should construct model objects.
3. Encoders should consume model objects.
4. Model objects should preserve raw bytes where useful.
5. Unknown data must be represented, not silently discarded.
6. Scaled numeric values should use `Decimal` internally.
7. Public objects should use clear names, not implementation terms like `parts`.

## DecodeResult

```python
@dataclass(frozen=True, slots=True)
class DecodeResult:
    ok: bool
    telegram: Telegram | None
    frame: Frame | None
    diagnostics: tuple[Diagnostic, ...]
    raw: bytes
```

`decode(data)` returns `DecodeResult`.

`decode_one(data)` returns `Telegram` or raises `DecodeError`.

`ok` means that the selected decode mode produced no fatal diagnostic. A lenient or compat result can therefore be usable and have `ok=True` while still carrying error or warning diagnostics.

Diagnostics are owned by the layer that produced them: `frame.diagnostics` contains frame-envelope issues and `telegram.diagnostics` contains application- and record-level issues. `DecodeResult.diagnostics` is the ordered aggregate across all stages.

## Diagnostics

```python
class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"

@dataclass(frozen=True, slots=True)
class Diagnostic:
    severity: Severity
    code: str
    message: str
    offset: int | None = None
    context: Mapping[str, object] = field(default_factory=dict)
```

Diagnostics should be serializable and stable enough to test.

## Decode modes

```python
class DecodeMode(Enum):
    STRICT = "strict"
    LENIENT = "lenient"
    COMPAT = "compat"
```

Strict mode should fail on malformed protocol data. Lenient mode should preserve partial and unknown data. Compat mode should preserve old user-facing behavior where practical.

## Frames

```python
class FrameKind(Enum):
    ACK = "ack"
    SHORT = "short"
    CONTROL = "control"
    LONG = "long"
    WIRELESS = "wireless"
    UNKNOWN = "unknown"

@dataclass(frozen=True, slots=True)
class Frame:
    kind: FrameKind
    raw: bytes
    checksum: int | None
    checksum_valid: bool | None
    diagnostics: tuple[Diagnostic, ...] = ()
```

### ACK frame

```python
@dataclass(frozen=True, slots=True)
class AckFrame(Frame):
    kind: FrameKind = FrameKind.ACK
```

### Short frame

```python
@dataclass(frozen=True, slots=True)
class ShortFrame(Frame):
    control: ControlField
    address: PrimaryAddress
```

Layout:

```text
10 C A CS 16
```

### Control frame

```python
@dataclass(frozen=True, slots=True)
class ControlFrame(Frame):
    length: int
    control: ControlField
    address: PrimaryAddress
    ci: int
```

Layout:

```text
68 03 03 68 C A CI CS 16
```

### Long frame

```python
@dataclass(frozen=True, slots=True)
class LongFrame(Frame):
    length: int
    control: ControlField
    address: PrimaryAddress
    ci: int
    payload: bytes
```

Layout:

```text
68 L L 68 C A CI PAYLOAD CS 16
```

## Addresses

```python
@dataclass(frozen=True, slots=True)
class PrimaryAddress:
    value: int

@dataclass(frozen=True, slots=True)
class SecondaryAddress:
    identification_number: str
    manufacturer: str | None
    manufacturer_raw: bytes
    version: int
    medium: int
```

Validation should live in constructors/helpers, not scattered through transport code.

## Control field

```python
@dataclass(frozen=True, slots=True)
class ControlField:
    raw: int
    direction: Direction | None
    function: ControlFunction | None
    fcb: bool | None = None
    fcv: bool | None = None
```

The exact enum members should be introduced alongside encoder/decoder work.

## Telegrams

```python
class ApplicationKind(Enum):
    NONE = "none"
    VARIABLE_DATA = "variable_data"
    FIXED_DATA = "fixed_data"
    MANUFACTURER_SPECIFIC = "manufacturer_specific"
    ENCRYPTED = "encrypted"
    UNKNOWN = "unknown"

@dataclass(frozen=True, slots=True)
class Telegram:
    frame: Frame
    application_kind: ApplicationKind
    diagnostics: tuple[Diagnostic, ...] = ()
```

## VariableDataTelegram

```python
@dataclass(frozen=True, slots=True)
class VariableDataTelegram(Telegram):
    header: VariableDataHeader
    records: tuple[DataRecord | UnknownRecord, ...]
    more_records_follow: bool
    raw_application_data: bytes
    undecoded_data: bytes = b""
```

## VariableDataHeader

```python
@dataclass(frozen=True, slots=True)
class VariableDataHeader:
    identification_number: str | None
    manufacturer: str | None
    manufacturer_raw: bytes
    version: int | None
    medium: int | None
    access_number: int | None
    status: int | None
    signature: bytes
    raw: bytes
```

The header should preserve both interpreted and raw fields.

## Data records

```python
@dataclass(frozen=True, slots=True)
class DataRecord:
    raw: bytes
    dif: DataInformation
    vif: ValueInformation
    value: DecodedValue
    function: FunctionType | None
    storage_number: int | None
    tariff: int | None
    subunit: int | None
    more_records_follow: bool
    diagnostics: tuple[Diagnostic, ...] = ()
```

## UnknownRecord

```python
@dataclass(frozen=True, slots=True)
class UnknownRecord:
    raw: bytes
    reason: str
    diagnostics: tuple[Diagnostic, ...] = ()
```

Unknown records are valid lenient-mode output.

## DataInformation

```python
@dataclass(frozen=True, slots=True)
class DataInformation:
    raw: bytes
    data_encoding: DataEncoding
    function: FunctionType
    storage_number: int
    tariff: int | None
    subunit: int | None
    extension_bytes: bytes = b""
```

## ValueInformation

```python
@dataclass(frozen=True, slots=True)
class ValueInformation:
    raw: bytes
    unit: Unit | None
    kind: str | None
    multiplier: Decimal
    extension_bytes: bytes = b""
    custom_vif: bytes | None = None
    enhancement: str | None = None
```

## DecodedValue

```python
class ValueType(Enum):
    NONE = "none"
    INTEGER = "integer"
    DECIMAL = "decimal"
    STRING = "string"
    BINARY = "binary"
    DATE = "date"
    DATETIME = "datetime"
    UNKNOWN = "unknown"

@dataclass(frozen=True, slots=True)
class DecodedValue:
    raw: bytes
    value: object | None
    type: ValueType
    unit: Unit | None
    scaled: bool
```

## Export expectations

Core objects should be exportable to a stable dict structure.

A 2.0 export should include:

- raw bytes as hex strings;
- frame kind;
- checksum status;
- application kind;
- decoded header fields;
- decoded records;
- diagnostics;
- unknown or undecoded bytes.

A compatibility export may produce v1-style record dictionaries.

## Decimal policy

Scaled numeric values should use `Decimal` internally. This avoids binary floating-point artifacts in values such as `58.120000000000005`.

JSON export should explicitly choose one of these modes:

```python
class JsonNumberMode(Enum):
    STRING = "string"
    FLOAT = "float"
    NATIVE = "native"
```

The exact default may be decided later, but the core model must not depend on float for scaled protocol values.

## Compatibility aliases

Compatibility wrappers may expose old names such as `TelegramACK`, `TelegramShort`, `TelegramControl`, `TelegramLong`, and `TelegramVariableDataRecord` if needed. They should adapt new model objects rather than force the new design to inherit old internals.
