# Getting started with pyMeterBus v2

This guide is for people who need to get M-Bus data decoded, not for people who want to study the internals of the library.

The short version is this:

1. Get one complete M-Bus frame as bytes or hex.
2. Give that frame to pyMeterBus.
3. Read the JSON output.
4. If decoding fails, keep the raw frame and look at the diagnostics.

pyMeterBus v2 does not talk to meters by itself. It decodes bytes you already have.

## What you need

You need Python 3.11 or newer.

Check your Python version:

```shell
python --version
```

If that prints Python 3.11, 3.12, 3.13, or newer, you are fine.

## Install

For normal install from PyPI:

```shell
python -m pip install pyMeterBus
```

For v2 prerelease testing:

```shell
python -m pip install --pre pyMeterBus
```

If you are working from a git checkout:

```shell
python -m pip install -e .
```

## First test

Run this:

```shell
pymeterbus-decode E5
```

You should see JSON similar to this:

```json
{"diagnostics":[],"frame":{"diagnostics":[],"kind":"ack","raw":"E5"},"ok":true,"raw":"E5","telegram":null}
```

`E5` is a simple M-Bus acknowledgement frame. It does not contain meter readings. It is only a quick check that the command is installed and working.

## Decode a hex string

If you have a telegram as hex text, run:

```shell
pymeterbus-decode "68 03 03 68 08 01 72 7B 16"
```

For easier reading, add indentation:

```shell
pymeterbus-decode --indent 2 "68 03 03 68 08 01 72 7B 16"
```

If you only want decoded records, use:

```shell
pymeterbus-decode --view records --indent 2 "$HEX"
```

Replace `$HEX` with your actual hex string.

## Decode a binary file

If your meter frame is stored in a binary file, convert it to hex first:

```shell
pymeterbus-decode --indent 2 "$(xxd -p -c 999999 frame.blob)"
```

That command reads `frame.blob`, turns it into one long hex string, and passes it to pyMeterBus.

## Decode from Python

Use this pattern if you are writing a small script:

```python
from meterbus import decode
from meterbus.export import to_json
from meterbus.model import DecodeMode

raw = bytes.fromhex("E5")
result = decode(raw, mode=DecodeMode.LENIENT)

print(to_json(result, indent=2))
```

For real data, replace `E5` with your frame.

## Which mode should I use?

Use `strict` when you want bad frames to fail loudly:

```shell
pymeterbus-decode --mode strict --indent 2 "$HEX"
```

Use `lenient` when decoding real meter data collected in the field:

```shell
pymeterbus-decode --mode lenient --indent 2 "$HEX"
```

Use `compat` only when you are migrating older workflows and want compatibility-oriented lenient behavior:

```shell
pymeterbus-decode --mode compat --indent 2 "$HEX"
```

For most practical use, start with `lenient`.

## How to read the result

The output has a few important fields:

```json
{
  "ok": true,
  "diagnostics": [],
  "frame": {},
  "telegram": {}
}
```

`ok` tells you whether the decode was clean enough for the selected mode.

`diagnostics` tells you what pyMeterBus did not like or could not understand.

`frame` is the outer M-Bus frame.

`telegram` is the application data inside the frame. Meter readings, if decoded, live there.

If `ok` is false, do not throw the raw data away. Keep the raw frame and diagnostics.

## Common problems

### Invalid start byte

This usually means the data you gave pyMeterBus is not a complete wired M-Bus frame.

Valid wired M-Bus frames usually start with one of these bytes:

- `E5` for acknowledgement.
- `10` for short frame.
- `68` for long or control frame.

If your data starts with something else, it may be wireless M-Bus, encrypted data, or a payload from an aggregator that removed the normal frame wrapper.

pyMeterBus v2 will not silently guess missing headers.

### Length mismatch

The frame says it has one length, but the actual data has another length.

Common causes:

- The frame was cut off.
- Two frames were joined together.
- The transport reader stopped too early or too late.
- An aggregator changed the data.

### Checksum mismatch

The frame structure looks like wired M-Bus, but the checksum does not match.

Common causes:

- Corrupted data.
- Wrong frame boundary.
- Missing or extra bytes.
- The data is not actually a wired M-Bus frame.

### No records decoded

Some frames are valid but do not contain decoded meter records.

Common causes:

- The frame is an ACK, short frame, or control frame.
- The telegram type is not implemented yet.
- The data is manufacturer-specific.
- The data is encrypted.

## Serial adapters

pyMeterBus does not include serial communication helpers. This is intentional.

Use your preferred serial library or tool to read a complete frame, then pass the bytes to pyMeterBus.

If you use Python and `pyserial`, install it yourself:

```shell
python -m pip install pyserial
```

Then read bytes with your own transport code and call:

```python
result = decode(raw_bytes)
```

See [serial transport example](serial-transport.md) for a longer example.

## Aggregators and headerless payloads

Some gateways or aggregators return data that looks like an M-Bus payload but does not include the normal wired M-Bus frame start, length, checksum, or stop byte.

pyMeterBus v2 does not treat those as valid wired M-Bus frames.

That is deliberate. Guessing missing headers can hide real data problems.

Handle aggregator-specific wrapping before calling the core decoder. If the aggregator has a documented format, write a small adapter that turns the aggregator payload into a complete frame or calls a future dedicated payload decoder.

## Upgrading from old pyMeterBus code

v2 is not a drop-in replacement for the old object model.

Old code may have expected things like serial helpers, legacy classes, or `meterbus.load()`. Those are not part of the v2 root API.

Start with this import:

```python
from meterbus import decode
```

Then decode complete frame bytes:

```python
result = decode(raw_bytes)
```

For a fuller migration explanation, read [v1 to v2 migration guide](migration-v1-to-v2.md).

## What to include when asking for help

When something does not decode, include:

- The raw hex string.
- The command you ran.
- The full JSON output.
- Whether the data came from serial, a file, a gateway, or an aggregator.
- Whether the meter data may be wireless or encrypted.

Do not only say "it does not work". The raw frame and diagnostics are what make the problem solvable.

## Quick command list

Install prerelease:

```shell
python -m pip install --pre pyMeterBus
```

Check the CLI works:

```shell
pymeterbus-decode E5
```

Decode hex:

```shell
pymeterbus-decode --mode lenient --indent 2 "$HEX"
```

Decode a binary file:

```shell
pymeterbus-decode --mode lenient --indent 2 "$(xxd -p -c 999999 frame.blob)"
```

Decode only records:

```shell
pymeterbus-decode --mode lenient --view records --indent 2 "$HEX"
```
