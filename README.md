Meter-Bus for Python
====================

About
-----

[M-Bus](http://www.m-bus.com/) (Meter-Bus) is a European standard (EN 13757-2 physical and link layer, EN 13757-3 application layer) for the remote reading of gas or electricity meters. M-Bus is also usable for other types of consumption meters. The M-Bus interface is made for communication on two wires, making it very cost effective.

Current State
-------------

This implementation is currently under heavy development. It is targeted at a very specific solution. Thus only the *variable data structure* is implemented. However the missing pieces will be implemented in the future.

Known Issues
------------
* Missing: Single Character frame, Short frame, Control frame.
* Missing: Fixed data structure parsing.
* Missing: Encoding to M-Bus frames.
* Missing: Slave configuration.
* Missing: Interface code (Serial, TCP/IP)
* Missing: Extended VIF codes.

What works
----------

* Parsing of complete telegram.
* Parsing of just Used Data segment.
* Generation of basic JSON structure from telegram/user-data/record.

Example
-------

    #!/usr/bin/env python
    import mbus

    data = "\x68\x6A\x6A\x68\x08\x01\x72\x43\x53\x93\x07\x65\x32\x10\x04\xCA\x00\x00\x00\x0C\x05\x14\x00\x00\x00\x0C\x13\x13\x20\x00\x00\x0B\x22\x01\x24\x03\x04\x6D\x12\x0B\xD3\x12\x32\x6C\x00\x00\x0C\x78\x43\x53\x93\x07\x06\xFD\x0C\xF2\x03\x01\x00\xF6\x01\x0D\xFD\x0B\x05\x31\x32\x4D\x46\x57\x01\xFD\x0E\x00\x4C\x05\x14\x00\x00\x00\x4C\x13\x13\x20\x00\x00\x42\x6C\xBF\x1C\x0F\x37\xFD\x17\x00\x00\x00\x00\x00\x00\x00\x00\x02\x7A\x25\x00\x02\x78\x25\x00\x3A\x16"

    tgr = Telegram()
    tgr.createTelegram(map(ord, data))
    tgr.parse()

    print tgr.to_JSON() # structure is not set in stone


License
-------
Please see the [LICENSE](LICENSE) file


