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

def init_slaves(ser):
    if False == ping_address(ser, meterbus.ADDRESS_NETWORK_LAYER, 0):
        return ping_address(ser, meterbus.ADDRESS_BROADCAST_NOREPLY, 0)
    else:
        return True

    return False

def mbus_scan_secondary_address_range(ser, pos, mask):
    # F character is a wildcard
    if mask[pos].upper() == 'F':
        l_start, l_end = 0, 9
    else:
        if pos < 15:
            mbus_scan_secondary_address_range(ser, pos+1, mask)
        else:
            l_start = l_end = ord(mask[pos]) - ord('0')

    if mask[pos].upper() == 'F' or pos == 15:
       for i in range(l_start, l_end+1):  # l_end+1 is to include l_end val
           new_mask = (mask[:pos] + "{0:1X}".format(i) + mask[pos+1:]).upper()
           val, match, manufacturer = mbus_probe_secondary_address(ser, new_mask)
           if val == True:
               print("Device found with id {0} ({1}), using mask {2}".format(
                   match, manufacturer, new_mask))
           elif val == False:  # Collision
               mbus_scan_secondary_address_range(ser, pos+1, new_mask)

def mbus_probe_secondary_address(ser, mask):
    # False -> Collison
    # None -> No reply
    # True -> Single reply
    meterbus.send_select_frame(ser, mask)
    try:
        frame = meterbus.load(meterbus.recv_frame(ser, 1))
    except meterbus.MBusFrameDecodeError as e:
        frame = e.value

    if isinstance(frame, meterbus.TelegramACK):
        meterbus.send_request_frame(ser, meterbus.ADDRESS_NETWORK_LAYER)
        time.sleep(0.5)

        frame = None
        try:
            frame = meterbus.load(
                meterbus.recv_frame(ser))
        except meterbus.MBusFrameDecodeError:
            pass

        if isinstance(frame, meterbus.TelegramLong):
            return True, frame.secondary_address, frame.manufacturer

        return None, None, None

    return frame, None, None

def main(args):
    try:
        with serial.serial_for_url(args.device,
                           args.baudrate, 8, 'E', 1, timeout=1) as ser:

            # Ensure we are at the beginning of the records
            init_slaves(ser)

            mbus_scan_secondary_address_range(ser, 0, args.address)

    except serial.serialutil.SerialException as e:
        print(e)

if __name__ == '__main__':
    def sec_addr_valid(string):
        if False == meterbus.is_secondary_address(string):
            raise argparse.ArgumentTypeError("Not a valid secondary address mask")
        return string

    parser = argparse.ArgumentParser(
        description='Scan serial M-Bus for devices.')
    parser.add_argument('-d', action='store_true',
                        help='Enable verbose debug')
    parser.add_argument('-b', '--baudrate',
                        type=int, default=2400,
                        help='Serial bus baudrate')
    parser.add_argument('-a', '--address',
                        type=sec_addr_valid, default="FFFFFFFFFFFFFFFF",
                        help='Secondary address mask')
    parser.add_argument('-r', '--retries',
                        type=int, default=5,
                        help='Number of ping retries for each address')
    parser.add_argument('device', type=str, help='Serial device or URI')

    args = parser.parse_args()

    meterbus.debug(args.d)

    main(args)
