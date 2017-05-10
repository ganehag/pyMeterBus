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


M-Bus Packet Format
-------------------

##### ACK Frame

**size = 1 byte**

| Byte  | Identifier | Value |
|-------|------------|-------|
| byte1 | ack        | 0xE5  |


##### SHORT Frame

**size = 5 byte**

| Byte  | Identifier | Value |
|-------|------------|-------|
| byte1 | start      | 0x10  |
| byte2 | control    | ...   |
| byte3 | address    | ...   |
| byte4 | chksum     | ...   |
| byte5 | stop       | 0x16  |


##### CONTROL Frame

**size = 9 byte**

| Byte  | Identifier | Value |
|-------|------------|-------|
| byte1 | start1     | 0x68  |
| byte2 | length1    | ...   |
| byte3 | length2    | ...   |
| byte4 | start2     | 0x68  |
| byte5 | control    | ...   |
| byte6 | address    | ...   |
| byte7 | ctl.info   | ...   |
| byte8 | chksum     | ...   |
| byte9 | stop       | 0x16  |


##### LONG Frame

**size = N >= 9 byte**

| Byte    | Identifier | Value |
|---------|------------|-------|
| byte1   | start1     | 0x68  |
| byte2   | length1    | ...   |
| byte3   | length2    | ...   |
| byte4   | start2     | 0x68  |
| byte5   | control    | ...   |
| byte6   | address    | ...   |
| byte7   | ctl.info   | ...   |
| byte8   | data       | ...   |
| ...     | ...        | ...   |
| byteN-1 | chksum     | ...   |
| byteN   | stop       | 0x16  |


Control Information field
-------------------------

| Mode 1     | Mode 2 | Application                                 |  Definition in     |
|------------|--------|---------------------------------------------|--------------------|
| 51h        | 55h    | data send                                   | EN1434-3           |
| 52h        | 56h    | selection of slaves                         | Usergroup July 93  |
| 50h        |        | application reset                           | Usergroup March 94 |
| 54h        |        | synronize action                            | suggestion         |
| B8h        |        | set baudrate to 300 baud                    | Usergroup July 93  |
| B9h        |        | set baudrate to 600 baud                    | Usergroup July 93  |
| BAh        |        | set baudrate to 1200 baud                   | Usergroup July 93  |
| BBh        |        | set baudrate to 2400 baud                   | Usergroup July 93  |
| BCh        |        | set baudrate to 4800 baud                   | Usergroup July 93  |
| BDh        |        | set baudrate to 9600 baud                   | Usergroup July 93  |
| BEh        |        | set baudrate to 19200 baud                  | suggestion         |
| BFh        |        | set baudrate to 38400 baud                  | suggestion         |
| B1h        |        | request readout of complete RAM content     | Techem suggestion  |
| B2h        |        | send user data (not standardized RAM write) | Techem suggestion  |
| B3h        |        | initialize test calibration mode            | Usergroup July 93  |
| B4h        |        | EEPROM read                                 | Techem suggestion  |
| B6h        |        | start software test                         | Techem suggestion  |
| 90h to 97h |        | codes used for hashing                      | longer recommended |
| ...        | ...    | ...                                         | ...                |
| 70h        |        | report of general application errors        | Usergroup March 94 |
| 71h        |        | report of alarm status                      | Usergroup March 94 |
| 72h        | 76h    | variable data respond                       | EN1434-3           |
| 73h        | 77h    | fixed data respond                          | EN1434-3           |


Examples
-------
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

~$ 19.2.2014 11:18
```

```python
#!/usr/bin/python

import serial
import meterbus

with serial.Serial('/dev/ttyUSB0', 2400, 8, 'E', 1, 1) as ser:
  meterbus.send_ping_frame(ser, 254)
  meterbus.recv_frame(ser, 1)
  meterbus.send_request_frame(ser, 254)
  frame = meterbus.load(meterbus.recv_frame(ser, 250))
  print(frame.to_JSON())
```


License
-------
Please see the [LICENSE](LICENSE) file


