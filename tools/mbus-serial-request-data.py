#!/usr/bin/python

from __future__ import print_function

import argparse
import serial
import time
import os
import stat
import simplejson as json
import yaml

from decimal import Decimal

try:
    import meterbus
except ImportError:
    import sys
    sys.path.append('../')
    import meterbus


def ping_address(ser, address, retries=5, read_echo=False):
    for i in range(0, retries + 1):
        meterbus.send_ping_frame(ser, address, read_echo)
        try:
            frame = meterbus.load(meterbus.recv_frame(ser, 1))
            if isinstance(frame, meterbus.TelegramACK):
                return True
        except meterbus.MBusFrameDecodeError as e:
            pass

        time.sleep(0.5)

    return False

def do_reg_file(args):
    with open(args.device, 'rb') as f:
        frame = meterbus.load(f.read())
        if frame is not None:
            print(frame.to_JSON())

def do_char_dev(args):
    address = None

    try:
        address = int(args.address)
        if not (0 <= address <= 254):
            address = args.address
    except ValueError:
        address = args.address.upper()

    try:
        ibt = meterbus.inter_byte_timeout(args.baudrate)
        with serial.serial_for_url(args.device,
                           args.baudrate, 8, 'E', 1,
                           inter_byte_timeout=ibt,
                           timeout=1) as ser:
            frame = None

            if meterbus.is_primary_address(address):
                if ping_address(ser, address, args.retries, args.echofix):
                    meterbus.send_request_frame(ser, address, read_echo=args.echofix)
                    frame = meterbus.load(
                        meterbus.recv_frame(ser, meterbus.FRAME_DATA_LENGTH))
                else:
                    print("no reply")

            elif meterbus.is_secondary_address(address):
                if ping_address(ser, meterbus.ADDRESS_NETWORK_LAYER, args.retries, args.echofix):
                    meterbus.send_select_frame(ser, address, args.echofix)
                    try:
                        frame = meterbus.load(meterbus.recv_frame(ser, 1))
                    except meterbus.MBusFrameDecodeError as e:
                        frame = e.value

                    # Ensure that the select frame request was handled by the slave
                    assert isinstance(frame, meterbus.TelegramACK)

                    frame = None

                    meterbus.send_request_frame(
                        ser, meterbus.ADDRESS_NETWORK_LAYER, read_echo=args.echofix)

                    time.sleep(0.3)

                    frame = meterbus.load(
                        meterbus.recv_frame(ser, meterbus.FRAME_DATA_LENGTH))
                else:
                    print("no reply")

            if frame is not None and args.output != 'dump':
                recs = []
                for rec in frame.records:
                    recs.append({
                        'value': rec.value,
                        'unit': rec.unit
                    })

                ydata = {
                    'manufacturer': frame.body.bodyHeader.manufacturer_field.decodeManufacturer,
                    'identification': ''.join(map('{:02x}'.format, frame.body.bodyHeader.id_nr)),
                    'access_no': frame.body.bodyHeader.acc_nr_field.parts[0],
                    'medium':  frame.body.bodyHeader.measure_medium_field.parts[0],
                    'records': recs
                }

                if args.output == 'json':
                    print(json.dumps(ydata, indent=4, sort_keys=True))

                elif args.output == 'yaml':
                    def float_representer(dumper, value):
                        if int(value) == value:
                            text = '{0:.4f}'.format(value).rstrip('0').rstrip('.')
                            return dumper.represent_scalar(u'tag:yaml.org,2002:int', text)
                        else:
                            text = '{0:.4f}'.format(value).rstrip('0').rstrip('.')
                        return dumper.represent_scalar(u'tag:yaml.org,2002:float', text)

                    # Handle float and Decimal representation
                    yaml.add_representer(float, float_representer)
                    yaml.add_representer(Decimal, float_representer)

                    print(yaml.dump(ydata, default_flow_style=False, allow_unicode=True, encoding=None))

            elif frame is not None:
                print(frame.to_JSON())

    except serial.serialutil.SerialException as e:
        print(e)


if __name__ == '__main__':
    # meterbus.ADDRESS_NETWORK_LAYER
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
                        type=int, default=3,
                        help='Number of ping retries for each address')
    parser.add_argument('-o', '--output', default="dump",
                        help='Output format [dump,json,yaml]')
    parser.add_argument('--echofix', action='store_true',
                        help='Read and ignore echoed data from target')
    parser.add_argument('device', type=str, help='Serial device, URI or binary file')

    args = parser.parse_args()

    meterbus.debug(args.d)

    try:
        mode = os.stat(args.device).st_mode
        if stat.S_ISREG(mode):
            do_reg_file(args)
        else:
            do_char_dev(args)
    except OSError:
        do_char_dev(args)

