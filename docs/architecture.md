# pyMeterBus 2.0 architecture

This document defines the intended architecture for a pyMeterBus 2.0 rewrite.

The goal of 2.0 is not merely to reorganize the existing code. The goal is to create a clean, typed, testable Python reference implementation of the M-Bus protocol that can later guide other implementations, including a possible Zig/WASM core.

The Python implementation should be treated as an executable specification.

## Goals

1. Preserve useful existing pyMeterBus behavior.
2. Separate protocol decoding from transport, CLI, logging, JSON export, and compatibility concerns.
3. Support strict and lenient decoding.
4. Preserve unknown or unsupported bytes instead of discarding them.
5. Build a golden fixture corpus from existing tests and real telegrams.
6. Keep a compatibility layer for `meterbus.load(data)`.
7. Keep the core model portable enough to translate to Zig later.

## Non-goals for the first 2.0 alpha

The first alpha does not need to implement every M-Bus feature. In particular, it does not need full slave support, full fixed-data telegram support, all extended VIF codes, every manufacturer quirk, Zig bindings, WASM bindings, or a perfect replacement for every legacy helper.

The alpha should prove the architecture and preserve current core decoding behavior.

## Core rule

The protocol core must not know about serial ports.

Core protocol code may transform bytes into structured models and structured models into bytes. It must not import pySerial, configure logging, open files, parse CLI arguments, sleep, retry, or talk to devices.

Transport code may depend on the core. The core must not depend on transport code.

## Package layout

Suggested long-term layout:

```text
meterbus/
  __init__.py

  model/
    __init__.py
    enums.py
    errors.py
    diagnostics.py
    frame.py
    telegram.py
    record.py
    value.py
    address.py

  codec/
    __init__.py
    decoder.py
    encoder.py
    frame_decoder.py
    frame_encoder.py
    application_decoder.py
    variable_data.py
    fixed_data.py
    dib.py
    vib.py
    crc.py
    primitives.py

  tables/
    __init__.py
    dif.py
    vif.py
    vif_extensions.py
    manufacturers.py
    media.py
    units.py

  extensions/
    __init__.py
    base.py
    registry.py
    generic.py

  transport/
    __init__.py
    base.py
    serial.py
    rfc2217.py
    session.py

  export/
    __init__.py
    dict.py
    json.py

  compat/
    __init__.py
    v1.py

  cli/
    __init__.py
    main.py
    decode.py
    request.py
    scan.py
```

For the first alpha, prefer implementing only the model, frame decoder, variable-data decoder, export layer, fixture loader, and compatibility wrapper.

## Public API

The 2.0 public API should be small:

```python
import meterbus

result = meterbus.decode(data)
telegram = meterbus.decode_one(data)
legacy = meterbus.load(data)
```

`decode(data)` returns a structured `DecodeResult`.

`decode_one(data)` returns a `Telegram` or raises `DecodeError`.

`load(data)` is a compatibility wrapper for existing users. It should issue a deprecation warning once the 2.0 API is stable.

Avoid exporting all internal protocol classes from `meterbus.__init__`. Only stable public types should be exported.

## Decode modes

Three decode modes are expected:

```text
STRICT
  Malformed input, checksum mismatch, length mismatch, or unsupported required structures fail.

LENIENT
  Best-effort decoding. Unknown bytes and malformed regions are preserved with diagnostics.

COMPAT
  Legacy-friendly mode used by `meterbus.load(data)` and migration tests.
```

## Parsing stages

Decoding should be staged:

```text
raw bytes
  -> Frame
  -> Telegram/ApplicationData
  -> DataRecord objects
  -> export views, if requested
```

Frame parsing must not decode every record. Record parsing must not know about serial transport.

## Frame decoding

Frame detection should be direct byte inspection rather than trial-and-error over model classes.

Expected frame starts:

```text
0xE5 -> ACK frame
0x10 -> short frame
0x68 -> control or long frame
other -> invalid/unknown frame
```

For `0x68`, inspect the length fields:

```text
68 L L 68 C A CI ... CS 16
```

If `L == 3`, it is a control frame. If `L > 3`, it is a long frame. If `L < 3`, it is invalid.

All frame objects must preserve raw bytes and checksum status.

## Diagnostics

Decoders should not silently swallow failures. They should return diagnostics.

Diagnostics should include severity, code, message, optional byte offset, and optional context.

Example diagnostic codes:

```text
empty_input
unsupported_input_type
invalid_start_byte
invalid_length
length_mismatch
checksum_mismatch
unknown_ci_field
unknown_dif
unknown_vif
unsupported_variable_data_record
manufacturer_specific_data
trailing_bytes
more_records_follow
```

## Unknown data policy

Unknown data is not an error by itself.

A decoder may fail in strict mode when a required structure is malformed, but lenient mode must preserve unknown or unsupported bytes whenever possible.

No decoder may discard bytes without either representing them in the model or reporting them in diagnostics.

## Numeric values

Scaled protocol values should use `Decimal` internally, not binary float. Export code may provide compatibility modes for float-like legacy output, but the core model should avoid floating-point artifacts.

## Export

Core objects should not primarily own JSON formatting.

Preferred API:

```python
from meterbus.export import to_dict, to_json

payload = to_dict(telegram)
text = to_json(telegram, indent=2)
```

Compatibility export may mimic v1 output where useful.

## Transport

Transport should sit above the codec layer.

```python
class ByteTransport(Protocol):
    def write(self, data: bytes) -> int: ...
    def read(self, size: int) -> bytes: ...
```

A future `MBusClient` may provide:

```python
client.ping(address)
client.request_user_data(address)
client.select_secondary(address)
```

Frame construction belongs in the encoder, not in the transport.

## Extension system

Manufacturer-specific behavior should be isolated behind extension hooks.

```python
class Extension(Protocol):
    name: str
    def supports(self, context: DecodeContext) -> bool: ...
    def decode_record(self, raw: bytes, context: DecodeContext) -> DataRecord | None: ...
```

Core table-driven decoding should run first. Extensions may decode otherwise unknown data.

## Future Zig/WASM core

Do not implement Zig or WASM in the first Python 2.0 alpha. The Python implementation should instead produce a stable model and fixture corpus.

Future non-Python implementations should be able to consume the same fixtures and produce equivalent normalized output.

Portable choices:

- enums
- integers
- byte arrays
- strings
- arrays/lists
- nullable fields
- explicit diagnostics
- JSON-compatible export trees

Avoid model choices that depend on Python-specific mutation, monkeypatching, lazy parsing through properties, or exceptions as ordinary control flow.

## First alpha acceptance criteria

The first alpha is useful when:

1. Existing ACK, short, control, and long frame examples decode.
2. Existing variable data examples decode.
3. Unknown data is preserved.
4. Strict and lenient modes exist.
5. The core has no serial dependency.
6. The core has no global debug state.
7. JSON/dict export works.
8. `meterbus.load(data)` exists as a compatibility wrapper.
9. Fixture files exist and are easy to extend.
10. Architecture and data model docs exist.
