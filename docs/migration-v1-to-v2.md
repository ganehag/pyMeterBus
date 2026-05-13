# Migrating from pyMeterBus v1 to v2

pyMeterBus v2 is a breaking rewrite. It is not a drop-in replacement for the legacy object model, serial helpers, wireless telegram classes, or `meterbus.load()`.

The v2 design is deliberately smaller: callers provide complete M-Bus frame bytes, and pyMeterBus decodes those bytes into structured results, diagnostics, and JSON-friendly exports.

## Recommended upgrade shape

Before upgrading production code, isolate the place where your application reads bytes from a meter or gateway. Keep that transport code in your application. Replace only the parsing step with the v2 decode API.

Old applications often mixed these responsibilities:

1. open a serial connection;
2. request or read a frame;
3. parse the frame;
4. interpret records;
5. export values.

In v2, pyMeterBus owns only steps 3 to 5. Your application owns transport, retries, timeouts, serial configuration, sockets, files, and gateway-specific behavior.

## Imports

### Decode API

Prefer one of these imports:

```python
from meterbus import decode
```

or:

```python
from meterbus.api import decode, decode_one, decode_one_frame
```

`decode()` is the safest general-purpose entry point. It returns a `DecodeResult` instead of raising for normal protocol diagnostics.

```python
from meterbus import decode

result = decode(bytes.fromhex("E5"))
if result.ok:
    print(result.frame)
else:
    print(result.diagnostics)
```

Use `decode_one_frame()` or `decode_one()` only when raising `DecodeError` on decode failure is the behavior you want.

### Export API

Use the export package for dictionaries and JSON:

```python
from meterbus import decode
from meterbus.export import ExportView, to_dict, to_json

result = decode(raw)
full_payload = to_dict(result)
records_payload = to_dict(result, view=ExportView.RECORDS)
json_payload = to_json(result, indent=2)
```

The root package intentionally does not expose every helper. Keep export imports explicit.

## Removed or intentionally unavailable APIs

The following legacy APIs are not part of the v2 root API:

| Legacy pattern | v2 replacement |
| --- | --- |
| `meterbus.load(...)` | `meterbus.decode(raw)` once your application has complete frame bytes |
| root-level legacy telegram classes | structured models under `meterbus.model` |
| bundled serial helpers | application-owned transport; see `docs/serial-transport.md` |
| legacy serial console scripts | `pymeterbus-decode` for decoding supplied hex only |
| wireless-specific telegram classes | currently unsupported or preserved through diagnostics where possible |
| implicit compact-frame state/cache | explicit compact expansion using a matching format template |

Do not reintroduce the legacy object model into the v2 root API. If a compatibility wrapper is added later, it should be deliberate, documented, and tested as a separate compatibility layer.

## Serial transport

v1-era code may have used pyMeterBus to open serial ports or request data directly. v2 does not install `pyserial` and does not perform serial I/O.

Recommended shape:

```python
from meterbus import decode
from meterbus.model import DecodeMode

raw = read_complete_mbus_frame_from_your_transport()
result = decode(raw, mode=DecodeMode.LENIENT)
```

Use your own serial, socket, HTTP gateway, file, or test fixture code to produce `raw`. The decoder should see one complete frame at a time.

## Decode results and diagnostics

v2 favors explicit diagnostics over guessed values. A decode can return a frame or partial telegram together with warnings or errors. Application code should inspect:

```python
result.ok
result.diagnostics
result.frame
result.telegram
```

Use strict mode for validation and tests. Use lenient mode when ingesting real-world meter data where manufacturer-specific records, filler bytes, malformed tails, or unsupported extensions may appear.

```python
from meterbus import decode
from meterbus.model import DecodeMode

strict_result = decode(raw, mode=DecodeMode.STRICT)
lenient_result = decode(raw, mode=DecodeMode.LENIENT)
```

`compat` mode is compatibility-oriented lenient behavior. Treat it as an ingestion aid, not as a promise that v1 object shapes or legacy parsed values are recreated.

## JSON and dictionary exports

Do not serialize v2 dataclasses directly as your long-term interchange format. Use `to_dict()` or `to_json()` so your application gets stable, JSON-friendly values.

```python
from meterbus.export import ExportView, to_json

print(to_json(result, view=ExportView.FULL))
print(to_json(result, view=ExportView.SUMMARY))
print(to_json(result, view=ExportView.RECORDS))
```

Use `FULL` while debugging decoder behavior. Use `RECORDS` when feeding readings into another system.

## Compact and format frames

v2 does not maintain hidden compact-frame template state. Compact expansion is explicit: provide the matching format frame or descriptors at the call site.

From the CLI:

```shell
pymeterbus-decode \
  --compact-template "$(xxd -p -c 999999 format-frame.blob)" \
  --indent 2 \
  "$(xxd -p -c 999999 compact-frame.blob)"
```

This is intentional. Hidden state makes batch decoding and long-running services harder to reason about.

## CLI migration

The supported v2 console command is:

```shell
pymeterbus-decode E5
```

It decodes hex supplied by the caller. It does not scan serial buses, send request frames, or own transport.

Exit codes:

| Code | Meaning |
| --- | --- |
| `0` | decode completed and `DecodeResult.ok` is true |
| `1` | decode completed with errors or compact expansion failed |
| `2` | invalid CLI input, such as malformed hex |

## Packaging changes

The default v2 install is dependency-free:

```shell
python -m pip install pyMeterBus
```

It does not install `pyserial`, YAML libraries, crypto packages, or `simplejson`. Add transport or integration dependencies in your own application.

## Practical migration checklist

- Identify where your current code obtains complete M-Bus frame bytes.
- Move serial, socket, gateway, retry, and timeout behavior into application code if it is not already there.
- Replace the old parse call with `decode(raw)`.
- Use `result.ok` and `result.diagnostics` instead of assuming every frame fully decodes.
- Replace direct legacy object serialization with `to_dict()` or `to_json()`.
- Run strict mode in tests and lenient mode for real-world ingestion where appropriate.
- Add raw frame fixtures for every device type you rely on.
- Compare v1 and v2 outputs for your real fixtures and document any intentional differences before upgrading production pipelines.

## When not to upgrade yet

Delay a production upgrade if your application depends on legacy serial helpers, `meterbus.load()`, wireless-specific legacy classes, or manufacturer-specific records that are not yet represented well enough by v2 diagnostics and exports.

In that case, keep using the v1 branch/package line for production while adding v2 fixtures that capture the behavior you need.
