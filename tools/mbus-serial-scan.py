#!/usr/bin/python

import argparse
import serial
import time

try:
    import meterbus
except ImportError:
    import sys
    sys.path.append('../')
    import meterbus


def ping_address(address, retries=5):
    for i in range(0, retries + 1):
        meterbus.send_ping_frame(ser, address)
        try:
            frame = meterbus.load(meterbus.recv_frame(ser, 1))
            if isinstance(frame, meterbus.TelegramACK):
                return True
        except meterbus.MBusFrameDecodeError:
            pass

    return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Scan serial M-Bus for devices.')
    parser.add_argument('-d', action='store_true',
                        help='Enable verbose debug')
    parser.add_argument('-b', '--baudrate',
                        type=int, default=2400,
                        help='Serial bus baudrate')
    parser.add_argument('-r', '--retries',
                        type=int, default=5,
                        help='Number of ping retries for each address')
    parser.add_argument('device', type=str, help='Serial device or URI')

    args = parser.parse_args()

    meterbus.debug(args.d)

    try:
        with serial.serial_for_url(args.device,
                           args.baudrate, 8, 'E', 1, timeout=1) as ser:
            for address in range(0, meterbus.MAX_PRIMARY_SLAVES + 1):
                if ping_address(address, args.retries):
                    print(
                        "Found a M-Bus device at address {0}".format(address)
                    )
    except serial.serialutil.SerialException as e:
        print(e)
