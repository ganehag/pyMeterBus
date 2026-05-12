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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Request data from WiFi ACM-ESP.')
    parser.add_argument('device', type=str, default='wifiacmesp', nargs='?', help='IP address')
    parser.add_argument('-d', action='store_true', help='Enable verbose debug')
    args = parser.parse_args()

    meterbus.debug(args.d)

    with serial.serial_for_url(F"socket://{args.device}:4455", 2400, 8, 'E', 1, timeout=2) as sock:
            frame = None
            meterbus.send_request_frame(sock, 254)
            frame = meterbus.load(meterbus.recv_frame(sock, meterbus.FRAME_DATA_LENGTH))
            
            if frame is not None:
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
                print(ydata)