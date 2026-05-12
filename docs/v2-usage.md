# pyMeterBus v2 usage

The v2 API is a structured decoder path built around explicit results, diagnostics, and deterministic export helpers.

It does not replace the older `meterbus.load()` object model yet. Use it when you want a predictable decode result, JSON output, and clear diagnostics.

## Decode a frame

```python
from meterbus.api import decode

raw = bytes.fromhex("E5")
result = decode(raw)

assert result.ok is True
assert result.frame.kind.value == "ack"
assert result.telegram is None
```

`decode()` always returns a `DecodeResult`. It does not raise for ordinary decode failures. Check `result.ok` and inspect `result.diagnostics`.

## Decode modes

```python
from meterbus.api import decode
from meterbus.model import DecodeMode

result = decode(bytes.fromhex("10 40 0B 00 16"), mode=DecodeMode.LENIENT)
```

Supported modes are:

- `DecodeMode.STRICT`: fail on malformed frames or record errors.
- `DecodeMode.LENIENT`: preserve partially decoded data where possible.
- `DecodeMode.COMPAT`: preserve partially decoded data where possible for compatibility-oriented workflows.

In lenient and compat modes, undecodable records can be preserved as `UnknownRecord` values with diagnostics instead of discarding the whole telegram.

## Export to dictionaries

```python
from meterbus.api import decode
from meterbus.export import to_dict

result = decode(bytes.fromhex("E5"))
payload = to_dict(result)

assert payload["ok"] is True
assert payload["frame"]["kind"] == "ack"
```

`to_dict()` produces JSON-friendly Python values. Bytes are rendered as uppercase hex strings, enums are rendered as their protocol-facing values, and diagnostics are rendered as dictionaries.

## Export to JSON

```python
from meterbus.api import decode
from meterbus.export import to_json

result = decode(bytes.fromhex("E5"))
print(to_json(result))
print(to_json(result, indent=2))
```

`to_json()` wraps `to_dict()` and emits deterministic JSON with stable key ordering.

## Decode from the command line

During development or from a checkout:

```shell
python -m meterbus.cli.decode "E5"
python -m meterbus.cli.decode --indent 2 "E5"
python -m meterbus.cli.decode --mode lenient "10 40 0B 00 16"
```

After installation, the package entry point is:

```shell
pymeterbus-decode "E5"
pymeterbus-decode --indent 2 "E5"
pymeterbus-decode --mode lenient "10 40 0B 00 16"
```

Exit codes:

- `0`: decode completed and `DecodeResult.ok` is true.
- `1`: decode completed and `DecodeResult.ok` is false.
- `2`: invalid CLI input, such as malformed hex.

The CLI writes the JSON decode result to stdout. CLI input errors are written to stderr.

## Variable-data telegrams

For long frames carrying CI `0x72`, the v2 decoder parses the variable-data header and then decodes records until it reaches filler bytes or an undecodable record.

```python
from meterbus.api import decode

raw = bytes.fromhex(
    "68 3D 3D 68 08 0B 72 21 00 00 00 B0 5C 02 1B "
    "12 00 00 00 0C 78 49 04 00 64 02 75 0A 00 "
    "01 FD 71 1E 2F 2F 0A 66 20 02 0A FB 1A 31 "
    "05 02 FD 97 1D 00 00 2F 2F 2F 2F 2F 2F 2F "
    "2F 2F 2F 2F 2F 2F 2F 2F DD 16"
)

result = decode(raw)
telegram = result.telegram

assert result.ok is True
assert telegram.header.manufacturer == "WEP"
assert len(telegram.records) == 3
```

The decoder preserves both the original application bytes and the trailing undecoded bytes:

```python
telegram.raw_application_data
telegram.undecoded_data
```

## Notes

The v2 API is intentionally boring: decode first, inspect diagnostics, export with `to_dict()` or `to_json()`. Protocol coverage will continue to grow in small tested slices.
