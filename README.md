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

Version 2 decoder API
---------------------

The v2 decoder work-in-progress provides a structured, diagnostics-first API for decoding M-Bus frames without using the older object model directly.

The v2 package has no runtime dependencies. It is byte-oriented: read a complete M-Bus frame with whatever transport you use, then pass those bytes to the decoder. Serial, sockets, HTTP gateways, and files are transport concerns outside the core package.

```python
from meterbus.api import decode
from meterbus.export import to_json

result = decode(bytes.fromhex("E5"))
print(result.ok)
print(to_json(result))
```

The same decoder can be used from the command line:

```shell
python -m meterbus.cli.decode "E5"
pymeterbus-decode "E5"
```

See [docs/v2-usage.md](docs/v2-usage.md) for practical CLI examples, Python API usage, export views, diagnostics, fixed/variable data notes, and compact/format frame expansion.

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
- Communication with M-Bus devices through caller-provided transports such as serial adapters, sockets, or gateways.
- As a debugging tool to decode M-Bus frames.

Currently, the library can decode M-Bus frames. It does presently **NOT** support encoding and transmission of M-Bus frames, such as *control* frames.

However, if the need arises, I might implement missing pieces on a request basis.


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
