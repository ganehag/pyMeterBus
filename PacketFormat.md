# Packet formats

##### ACK

**size = 1 byte**

| Byte  | Identifier | Value |
|-------|------------|-------|
| byte1 | ack        | 0xE5  |


##### SHORT

**size = 5 byte**

| Byte  | Identifier | Value |
|-------|------------|-------|
| byte1 | start      | 0x10  |
| byte2 | control    | ...   |
| byte3 | address    | ...   |
| byte4 | chksum     | ...   |
| byte5 | stop       | 0x16  |


##### CONTROL

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


##### LONG

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


## Control Information field

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