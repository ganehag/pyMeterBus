Meter-Bus for Python
====================
[![Build status](https://github.com/ganehag/pyMeterBus/actions/workflows/run-test.yml/badge.svg)](https://github.com/ganehag/pyMeterBus/actions/workflows/run-test.yml) [![codecov](https://codecov.io/gh/ganehag/pyMeterBus/branch/master/graph/badge.svg?token=gHfokXGQ70)](https://codecov.io/gh/ganehag/pyMeterBus)
[![pypi](https://img.shields.io/pypi/pyversions/pyMeterBus)](https://pypi.org/project/pyMeterBus/)
[![GitHub issues](https://img.shields.io/github/issues/ganehag/pyMeterBus.svg)](https://github.com/ganehag/pyMeterBus/issues)
[![GitHub issues](https://img.shields.io/github/issues-closed/ganehag/pyMeterBus.svg)](https://github.com/ganehag/pyMeterBus/issues/?q=is%3Aissue+is%3Aclosed)
[![PyPI Status](https://img.shields.io/pypi/v/pyMeterBus.svg)](https://pypi.python.org/pypi/pyMeterBus/)

About
-----

[M-Bus](http://www.m-bus.com/) (Meter-Bus) is a European standard (EN 13757-2 physical and link layer, EN 13757-3 application layer) for the remote reading of gas or electricity meters. M-Bus is also usable for other types of consumption meters. The M-Bus interface is made for communication on two wires, making it very cost-effective.

Python version
--------------

I've decided only to support active Python version. Thus, any EOL version is not supported.

Current State (2025)
-------------

I’m still active, but as with most side projects, this one often takes a back seat.

If you have improvements that could benefit the project, feel free to submit a pull request. If it’s a good fit, I’ll be happy to merge it.

Current State (2022)
-------------

The library works, but it lacks proper documentation. Well, it lacks any documentation, to be honest.

The implementation is currently under ~~heavy~~ development. Its original intended use case was particular, as a library to aid in decoding M-Bus telegrams sent over HTTP, and might thus not suit everyone.

Still, it is a generic library and supports several different use cases.

- Decoding of re-encoded M-Bus frames sent from an Elvaco Wireless M-Bus master over HTTP.
- Communicating with M-Bus devices over RS-232 serial.
- Communication with M-Bus devices over RFC 2217.
- As a debugging tool to decode M-Bus frames.

Currently, only the *variable data structures* are implemented. The library can only decode M-Bus frames. It does presently **NOT** support encoding and transmission of M-Bus frames, such as *control* frames.

However, if the need arises, I might implement missing pieces on a request basis.


Tools
-----

You can find a set of utilities in the `tools` folder.

* mbus-serial-request-data.py
* mbus-serial-request-data-multi-reply.py
* mbus-serial-scan.py
* mbus-serial-scan-secondary.py

These tools can communicate over a serial device `/dev/ttyX` or even over RFC2217 using the format `rfc2217://host:port`.

Suppose you are using `ser2net` as an RFC2217 server. You need to configure it the following way:

```
2000:telnet:0:/dev/ttySX:2400 remctl banner
```

Known Issues
------------
* Missing: Fixed data structure parsing.
* Missing: Encoding to M-Bus frames.
* Missing: Slave configuration.
* Missing: Extended VIF codes.


What works
----------

* Querying an M-Bus device over serial.
* Parsing of a complete telegram.
* Parsing of just the *Used Data* segment.
* Generating a basic JSON structure from the telegram/user-data/records.


Basic API documentation
-----------------------

#### meterbus.load(data)
* data[str]: M-Bus frame data

Returns an object of either type *WTelegramSndNr, TelegramACK, TelegramShort, TelegramControl* or *TelegramLong*. If an error occurs, it will raise an *MBusFrameDecodeError*.

#### meterbus.debug(state)
* state[bool]: set the global debug state

Produces debug messages to stdout.

#### meterbus.send_ping_frame(ser, address)
* ser[pySerial connection]: an open pySerial object
* address: The target's primary address

Sends a PING frame to *address* over the serial connection *ser*.

#### meterbus.recv_frame(ser, length)
* ser[pySerial connection]: an open pySerial object
* length: The minimum length of the reply. An ACK frame is one (1) byte.

Reads an entire frame and returns the unparsed data.

#### meterbus.send_request_frame_multi(ser, address, req)
* ser[pySerial connection]: an open pySerial object
* address: The target's primary address

If *req* is None, build a new *request* frame using *address* and send it.

#### meterbus.send_select_frame(ser, secondary_address)
* ser[pySerial connection]: an open pySerial object
* secondary_address[str]: A target using secondary address format

Sends a select frame with the supplied secondary address.

#### meterbus.XXX
More to come...


Code examples
-------------

### Decode the value of a single record (record 3)
```python
#!/usr/bin/python

import meterbus

data = "\x68\x6A\x6A\x68\x08\x01\x72\x43\x53\x93\x07\x65" \
       "\x32\x10\x04\xCA\x00\x00\x00\x0C\x05\x14\x00\x00" \
       "\x00\x0C\x13\x13\x20\x00\x00\x0B\x22\x01\x24\x03" \
       "\x04\x6D\x12\x0B\xD3\x12\x32\x6C\x00\x00\x0C\x78" \
       "\x43\x53\x93\x07\x06\xFD\x0C\xF2\x03\x01\x00\xF6" \
       "\x01\x0D\xFD\x0B\x05\x31\x32\x4D\x46\x57\x01\xFD" \
       "\x0E\x00\x4C\x05\x14\x00\x00\x00\x4C\x13\x13\x20" \
       "\x00\x00\x42\x6C\xBF\x1C\x0F\x37\xFD\x17\x00\x00" \
       "\x00\x00\x00\x00\x00\x00\x02\x7A\x25\x00\x02\x78" \
       "\x25\x00\x3A\x16"

telegram = meterbus.load(data)
print telegram.records[3].parsed_value
```

```shell
~$ 2014-02-19T11:18
```

### Request a frame over Serial and dump it in JSON format
```python
#!/usr/bin/python

import serial
import meterbus

address = 254

with serial.Serial('/dev/ttyACM0', 2400, 8, 'E', 1, 0.5) as ser:
  meterbus.send_ping_frame(ser, address)
  frame = meterbus.load(meterbus.recv_frame(ser, 1))
  assert isinstance(frame, meterbus.TelegramACK)

  meterbus.send_request_frame(ser, address)
  frame = meterbus.load(meterbus.recv_frame(ser, meterbus.FRAME_DATA_LENGTH))
  assert isinstance(frame, meterbus.TelegramLong)

  print(frame.to_JSON())
```

M-Bus Packet Format
-------------------

| Single Character | Short Frame | Control Frame | Long Frame             |
|------------------|-------------|---------------|------------------------|
| E5h              | Start 10h   | Start 68h     | Start 68h              |
|                  | C Field     | L Field = 3   | L Field                |
|                  | A Field     | L Field = 3   | L Field                |
|                  | Check Sum   | Start 68h     | Start 68h              |
|                  | Stop 16h    | C Field       | C Field                |
|                  |             | A Field       | A Field                |
|                  |             | CI Field      | CI Field               |
|                  |             | Check Sum     | User Data (0-252 Byte) |
|                  |             | Stop 16h      | Check Sum              |
|                  |             |               | Stop 16h               |



License
-------
Please see the [LICENSE](LICENSE) file
