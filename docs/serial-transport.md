# Serial transport example

pyMeterBus v2 does not depend on `pyserial` and does not open serial ports itself. This is intentional. The decoder accepts complete M-Bus frame bytes; your application owns the transport.

This guide shows one way to read complete frames from a serial port and pass them to pyMeterBus. It is an example pattern, not a required dependency.

## Install pyserial in your application

If your application talks to a meter through a serial adapter, install `pyserial` in that application environment:

```shell
python -m pip install pyserial
```

pyMeterBus itself does not require it.

## M-Bus frame boundaries

The byte reader needs to collect exactly one complete M-Bus frame before calling `decode()`.

The basic frame forms are:

| Frame type | Start byte | Length rule |
| --- | --- | --- |
| ACK | `E5` | one byte |
| Short frame | `10` | five bytes total |
| Control frame | `68` | length byte must be `03`, full frame length is `6 + length` |
| Long frame | `68` | full frame length is `6 + length` |

For `0x68` frames, the first four bytes are:

```text
68 L L 68
```

The two length bytes must match. The stop byte at the end should be `16`.

## Minimal frame reader

This reader only does transport framing. It does not interpret meter values. After it returns bytes, pyMeterBus validates and decodes the frame.

```python
from __future__ import annotations

from collections.abc import Callable


class MBusTransportError(Exception):
    """Raised when a complete M-Bus frame cannot be read from the transport."""


def read_exact(read: Callable[[int], bytes], size: int) -> bytes:
    """Read exactly size bytes from a byte transport."""

    chunks: list[bytes] = []
    remaining = size
    while remaining:
        chunk = read(remaining)
        if not chunk:
            raise MBusTransportError(f"transport ended while waiting for {remaining} byte(s)")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def read_mbus_frame(read: Callable[[int], bytes]) -> bytes:
    """Read one complete M-Bus frame from a byte transport.

    The read callable should behave like serial.read(size): it returns up to size bytes
    and returns b"" on timeout or end-of-stream.
    """

    start = read_exact(read, 1)

    if start == b"\xE5":
        return start

    if start == b"\x10":
        return start + read_exact(read, 4)

    if start != b"\x68":
        raise MBusTransportError(f"unexpected M-Bus start byte: {start.hex(' ').upper()}")

    header_tail = read_exact(read, 3)
    length_1 = header_tail[0]
    length_2 = header_tail[1]
    repeated_start = header_tail[2]

    if length_1 != length_2:
        raise MBusTransportError(f"M-Bus length bytes differ: {length_1} != {length_2}")
    if repeated_start != 0x68:
        raise MBusTransportError(f"expected repeated start 68, got {repeated_start:02X}")

    # We already read 68 L L 68. The remaining bytes are:
    # C, A, optional CI/user data according to L, checksum, stop.
    remainder = read_exact(read, length_1 + 2)
    frame = start + header_tail + remainder

    if frame[-1] != 0x16:
        raise MBusTransportError(f"expected stop byte 16, got {frame[-1]:02X}")

    return frame
```

## Use with pyserial

```python
from __future__ import annotations

import serial

from meterbus.api import decode
from meterbus.export import ExportView, to_json
from meterbus.model import DecodeMode

from serial_transport import read_mbus_frame


with serial.Serial(
    port="/dev/ttyUSB0",
    baudrate=2400,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_ONE,
    timeout=1.0,
) as ser:
    raw = read_mbus_frame(ser.read)

result = decode(raw, mode=DecodeMode.LENIENT)
print(to_json(result, view=ExportView.RECORDS, indent=2))
```

Many wired M-Bus installations use `2400 8E1`, but your meter, adapter, or gateway may require different settings. Check the device documentation.

## Reading repeatedly

For collection services, keep transport errors separate from decode diagnostics. Transport errors mean the application did not receive a complete frame. Decode diagnostics mean pyMeterBus received a frame and found protocol issues or unsupported data.

```python
from __future__ import annotations

import time

import serial

from meterbus.api import decode
from meterbus.model import DecodeMode

from serial_transport import MBusTransportError, read_mbus_frame


with serial.Serial("/dev/ttyUSB0", 2400, 8, "E", 1, timeout=1.0) as ser:
    while True:
        try:
            raw = read_mbus_frame(ser.read)
        except MBusTransportError as exc:
            print(f"transport error: {exc}")
            time.sleep(1.0)
            continue

        result = decode(raw, mode=DecodeMode.LENIENT)
        if not result.ok:
            print("decode failed", result.diagnostics)
            continue

        for record in getattr(result.telegram, "records", ()):
            print(record.vif.kind, record.value.value)
```

## Request/response applications

pyMeterBus v2 currently decodes frames. It does not build or transmit M-Bus request frames for you.

If your application sends request frames, keep that code in the application transport layer. Once a response frame is received, pass the complete response bytes to `decode()`.

## Why this is not built into pyMeterBus

Keeping serial I/O outside the package has practical benefits:

- pyMeterBus stays dependency-free for users who decode files, HTTP gateway payloads, sockets, or test fixtures.
- Applications can choose `pyserial`, async transports, RFC 2217, vendor SDKs, or gateway APIs without the decoder caring.
- Protocol decoding remains deterministic and easy to test.
- Transport timeouts, retries, addressing, and polling policy stay in application code where they belong.

The boundary is simple: collect complete M-Bus frame bytes however you want, then call `decode(raw)`.
