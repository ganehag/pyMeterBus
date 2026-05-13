# Serial transport example

pyMeterBus v2 does not depend on `pyserial` and does not open serial ports itself. This is intentional. The decoder accepts complete M-Bus frame bytes; your application owns the transport.

A real wired M-Bus serial application usually needs more than a passive frame reader. In the common request/response flow, the application must send request frames, handle ACKs, handle adapter echo, retry, and sometimes collect multiple replies. This guide shows a practical pattern while keeping those transport concerns outside the pyMeterBus runtime package.

## Install pyserial in your application

If your application talks to a meter through a serial adapter, install `pyserial` in that application environment:

```shell
python -m pip install pyserial
```

pyMeterBus itself does not require it.

## What pyMeterBus does and does not do

pyMeterBus v2 decodes received frame bytes:

```python
from meterbus.api import decode

result = decode(raw_response_frame)
```

Your application is responsible for transport behavior:

- opening the serial port;
- choosing baud rate, parity, stop bits, timeout, and inter-byte timeout;
- sending request frames;
- optionally discarding echoed bytes from adapters that echo transmitted data;
- reading complete response frames;
- retrying if a meter does not answer;
- selecting secondary-addressed meters;
- collecting multi-reply responses when a telegram says more records follow.

This separation keeps the core package dependency-free without pretending serial M-Bus is simpler than it is.

## Basic frame builders

The examples below build the common wired M-Bus request frames used by many simple collection tools. They are included here as application-side example code, not as pyMeterBus runtime API.

```python
from __future__ import annotations

ADDRESS_BROADCAST_REPLY = 0xFE
ADDRESS_NETWORK_LAYER = 0xFD

CONTROL_DIR_M2S = 0x40
CONTROL_SND_NKE = 0x40
CONTROL_REQ_UD2 = 0x5B
CONTROL_SND_UD = 0x53
CONTROL_FCB = 0x20
CONTROL_FCV = 0x10

CI_SELECT_SLAVE = 0x52


class MBusTransportError(Exception):
    """Raised when serial transport cannot send or receive a complete frame."""


def checksum(data: bytes) -> int:
    return sum(data) & 0xFF


def short_frame(control: int, address: int) -> bytes:
    body = bytes([control & 0xFF, address & 0xFF])
    return b"\x10" + body + bytes([checksum(body), 0x16])


def long_frame(control: int, address: int, payload: bytes) -> bytes:
    body = bytes([control & 0xFF, address & 0xFF]) + payload
    length = len(body)
    return bytes([0x68, length, length, 0x68]) + body + bytes([checksum(body), 0x16])


def snd_nke(address: int) -> bytes:
    """Initialize/reset communication state for a primary-addressed meter."""

    return short_frame(CONTROL_SND_NKE, address)


def req_ud2(address: int) -> bytes:
    """Request class 2 user data from a primary-addressed meter."""

    return short_frame(CONTROL_REQ_UD2, address)


def req_ud2_multi(address: int, *, fcb: bool = True) -> bytes:
    """Request user data with FCV set, suitable for multi-reply collection."""

    control = CONTROL_REQ_UD2 | CONTROL_FCV
    if fcb:
        control |= CONTROL_FCB
    return short_frame(control, address)


def select_secondary(secondary_address: str) -> bytes:
    """Build an application select frame for a secondary address.

    secondary_address is a 16-character hex string:
    ID(4 bytes BCD), manufacturer(2 bytes), version(1 byte), medium(1 byte).
    The byte order follows the legacy pyMeterBus select-frame layout.
    """

    clean = secondary_address.replace(" ", "").upper()
    if len(clean) != 16:
        raise ValueError("secondary address must contain 16 hex characters")

    data = bytearray([CI_SELECT_SLAVE, 0, 0, 0, 0, 0, 0, 0, 0])

    # Identification number, reversed by byte pairs.
    data[4] = int(clean[0:2], 16)
    data[3] = int(clean[2:4], 16)
    data[2] = int(clean[4:6], 16)
    data[1] = int(clean[6:8], 16)

    # Manufacturer, low byte then high byte.
    manufacturer = int(clean[8:12], 16)
    data[5] = (manufacturer >> 8) & 0xFF
    data[6] = manufacturer & 0xFF

    # Version and medium.
    data[7] = int(clean[12:14], 16)
    data[8] = int(clean[14:16], 16)

    return long_frame(CONTROL_SND_UD | CONTROL_FCB, ADDRESS_NETWORK_LAYER, bytes(data))
```

## Reading complete response frames

This reader collects exactly one complete response frame. It handles ACK, short, control, and long frame boundaries. It does not interpret meter values; pyMeterBus does that after the bytes are collected.

```python
from __future__ import annotations

from collections.abc import Callable


def read_exact(read: Callable[[int], bytes], size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = size
    while remaining:
        chunk = read(remaining)
        if not chunk:
            raise MBusTransportError(f"transport timed out while waiting for {remaining} byte(s)")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def read_mbus_frame(read: Callable[[int], bytes]) -> bytes:
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

    remainder = read_exact(read, length_1 + 2)
    frame = start + header_tail + remainder

    if frame[-1] != 0x16:
        raise MBusTransportError(f"expected stop byte 16, got {frame[-1]:02X}")

    return frame
```

## Serial helper class

This helper keeps echo handling, writes, frame reads, and ACK checks in one place. It is application code. Copy it into your project and adjust it for your adapter and meters.

```python
from __future__ import annotations

import time
from dataclasses import dataclass

from meterbus.api import decode
from meterbus.model import DecodeMode


@dataclass
class SerialMBusClient:
    serial_port: object
    read_echo: bool = False
    mode: DecodeMode = DecodeMode.LENIENT

    def write_frame(self, frame: bytes) -> None:
        self.serial_port.write(frame)
        if self.read_echo:
            echo = self.serial_port.read(len(frame))
            if echo != frame:
                raise MBusTransportError(
                    f"unexpected serial echo: expected {frame.hex(' ').upper()}, got {echo.hex(' ').upper()}"
                )

    def read_raw_frame(self) -> bytes:
        return read_mbus_frame(self.serial_port.read)

    def read_decoded_frame(self):
        raw = self.read_raw_frame()
        return decode(raw, mode=self.mode)

    def send_and_read(self, frame: bytes):
        self.write_frame(frame)
        return self.read_decoded_frame()

    def ping_primary(self, address: int, *, retries: int = 3, delay: float = 0.5) -> bool:
        for _ in range(retries + 1):
            try:
                result = self.send_and_read(snd_nke(address))
            except MBusTransportError:
                time.sleep(delay)
                continue

            if result.frame is not None and result.frame.kind.value == "ack":
                return True

            time.sleep(delay)

        return False

    def request_primary_once(self, address: int, *, retries: int = 3):
        if not self.ping_primary(address, retries=retries):
            raise MBusTransportError(f"meter at primary address {address} did not acknowledge SND_NKE")

        return self.send_and_read(req_ud2(address))
```

## Use with pyserial

Many wired M-Bus installations use `2400 8E1`, but your meter, adapter, or gateway may require different settings. Check the device documentation.

```python
from __future__ import annotations

import serial

from meterbus.export import ExportView, to_json


with serial.serial_for_url(
    "/dev/ttyUSB0",
    baudrate=2400,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_ONE,
    timeout=1.0,
    inter_byte_timeout=0.05,
) as ser:
    client = SerialMBusClient(ser, read_echo=False)
    result = client.request_primary_once(1)

print(to_json(result, view=ExportView.RECORDS, indent=2))
```

Use `serial.serial_for_url(...)` if you want to support normal devices such as `/dev/ttyUSB0` as well as URL transports such as RFC 2217.

## Secondary addressing

Secondary addressing is a two-step flow:

1. send an application select frame to the network-layer address (`0xFD`), and
2. request user data from the network-layer address.

Some applications first ping `0xFD` or a broadcast address to check that the bus is alive. The exact strategy can vary by adapter and installation.

```python
def request_secondary_once(client: SerialMBusClient, secondary_address: str):
    select_result = client.send_and_read(select_secondary(secondary_address))
    if select_result.frame is None or select_result.frame.kind.value != "ack":
        raise MBusTransportError("secondary select did not return ACK")

    return client.send_and_read(req_ud2(ADDRESS_NETWORK_LAYER))
```

Secondary selection details are device-sensitive. Treat this as a starting point, not as a universal production driver.

## Multi-reply readout

Some meters split records across multiple replies. In that case the request uses FCV/FCB, and the application toggles FCB while the decoded telegram says more records follow.

```python
def request_primary_multi(client: SerialMBusClient, address: int, *, retries: int = 3):
    if not client.ping_primary(address, retries=retries):
        raise MBusTransportError(f"meter at primary address {address} did not acknowledge SND_NKE")

    fcb = True
    result = client.send_and_read(req_ud2_multi(address, fcb=fcb))
    results = [result]

    while getattr(result.telegram, "more_records_follow", False):
        fcb = not fcb
        result = client.send_and_read(req_ud2_multi(address, fcb=fcb))
        results.append(result)

    return results
```

The v2 decoder currently returns separate decoded results. If your application wants one combined logical reading, combine the decoded records in application code after checking diagnostics for every reply.

## Transport errors versus decode diagnostics

Keep these separate:

- transport errors mean your application did not receive a complete frame or did not receive the expected ACK;
- decode diagnostics mean pyMeterBus received bytes and found protocol issues, unsupported data, or malformed content.

```python
try:
    result = client.request_primary_once(1)
except MBusTransportError as exc:
    print(f"serial transport failed: {exc}")
else:
    if not result.ok:
        print("frame decoded with errors", result.diagnostics)
```

## Why this is not built into pyMeterBus

Keeping serial I/O outside the package has practical benefits:

- pyMeterBus stays dependency-free for users who decode files, HTTP gateway payloads, sockets, or test fixtures.
- Applications can choose `pyserial`, async transports, RFC 2217, vendor SDKs, or gateway APIs without the decoder caring.
- Protocol decoding remains deterministic and easy to test.
- Transport timeouts, retries, addressing, polling policy, echo handling, and multi-reply collection stay in application code where they belong.

The boundary is simple: your application performs serial communication and collects complete M-Bus frame bytes; pyMeterBus decodes the received frame bytes.
