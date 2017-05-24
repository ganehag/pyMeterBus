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


def ping_address(ser, address, retries=5):
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
        description='Request data over serial M-Bus for devices.')
    parser.add_argument('-d', action='store_true',
                        help='Enable verbose debug')
    parser.add_argument('-b', '--baudrate',
                        type=int, default=2400,
                        help='Serial bus baudrate')
    parser.add_argument('-a', '--address',
                        type=str, default=meterbus.ADDRESS_BROADCAST_REPLY,
                        help='Primary or secondary address')
    parser.add_argument('-r', '--retries',
                        type=int, default=5,
                        help='Number of ping retries for each address')
    parser.add_argument('device', type=str, help='Serial device or URI')

    args = parser.parse_args()

    meterbus.debug(args.d)

    address = None

    try:
        address = int(args.address)
        if not (0 <= address <= 254):
            address = args.address
    except ValueError:
        address = args.address

    try:
        ibt = meterbus.inter_byte_timeout(args.baudrate)
        with serial.serial_for_url(args.device,
                           args.baudrate, 8, 'E', 1,
                           inter_byte_timeout=ibt,
                           timeout=1) as ser:
            frame = None

            if meterbus.is_primary_address(address):
                ping_address(ser, meterbus.ADDRESS_NETWORK_LAYER, 0)
                ping_address(ser, meterbus.ADDRESS_NETWORK_LAYER, 0)

                meterbus.send_request_frame_multi(ser, address)
                frame = meterbus.load(
                    meterbus.recv_frame(ser, meterbus.FRAME_DATA_LENGTH))

            elif meterbus.is_secondary_address(address):
                meterbus.send_select_frame(ser, address)
                frame = meterbus.load(meterbus.recv_frame(ser, 1))
                assert isinstance(frame, meterbus.TelegramACK)

                frame = None
                # ping_address(ser, meterbus.ADDRESS_NETWORK_LAYER, 0)

                req = meterbus.send_request_frame_multi(
                          ser, meterbus.ADDRESS_NETWORK_LAYER)

                time.sleep(0.3)

                frame = meterbus.load(
                    meterbus.recv_frame(ser, meterbus.FRAME_DATA_LENGTH))

                while frame.more_records_follow:
                    # toogle FCB on and off
                    req.header.cField.parts[0] ^= meterbus.CONTROL_MASK_FCB

                    req = meterbus.send_request_frame_multi(
                              ser, meterbus.ADDRESS_NETWORK_LAYER, req)

                    time.sleep(0.3)

                    another_frame = meterbus.load(
                        meterbus.recv_frame(ser, meterbus.FRAME_DATA_LENGTH))
                    frame += another_frame

            if frame is not None:
                print(frame.to_JSON())

    except serial.serialutil.SerialException as e:
        print(e)
