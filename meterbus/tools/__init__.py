import argparse
import serial
import os
import simplejson as json
import stat
import time
import yaml

from decimal import Decimal

try:
    import meterbus
except ImportError:
    import sys
    sys.path.append('../../')
    import meterbus


def ping_address(ser, address, retries=5, read_echo=False):
    for i in range(0, retries + 1):
        meterbus.send_ping_frame(ser, address, read_echo)
        try:
            frame = meterbus.load(meterbus.recv_frame(ser, 1))
            if isinstance(frame, meterbus.TelegramACK):
                return True
        except meterbus.MBusFrameDecodeError:
            pass

        time.sleep(0.5)

    return False


def init_slaves(ser, read_echo=False):
    if False is ping_address(ser, meterbus.ADDRESS_NETWORK_LAYER, 0, read_echo):
        return ping_address(ser, meterbus.ADDRESS_BROADCAST_NOREPLY, 0, read_echo)
    else:
        return True

    return False


def mbus_scan_secondary_address_range(ser, pos, mask, read_echo=False):
    # F character is a wildcard
    if mask[pos].upper() == 'F':
        l_start, l_end = 0, 9
    else:
        if pos < 15:
            mbus_scan_secondary_address_range(ser, pos+1, mask, read_echo)
        else:
            l_start = l_end = ord(mask[pos]) - ord('0')

    if mask[pos].upper() == 'F' or pos == 15:
        for i in range(l_start, l_end+1):  # l_end+1 is to include l_end val
            new_mask = (mask[:pos] + "{0:1X}".format(i) + mask[pos+1:]).upper()
            val, match, manufacturer = mbus_probe_secondary_address(
                ser, new_mask, read_echo)

            if val is True:
                print("Device found with id {0} ({1}), using mask {2}".format(
                      match, manufacturer, new_mask))
            elif val is False:  # Collision
                mbus_scan_secondary_address_range(ser, pos+1, new_mask, read_echo)


def mbus_probe_secondary_address(ser, mask, read_echo=False):
    # False -> Collison
    # None -> No reply
    # True -> Single reply
    meterbus.send_select_frame(ser, mask, read_echo)
    try:
        frame = meterbus.load(meterbus.recv_frame(ser, 1))
    except meterbus.MBusFrameDecodeError as e:
        frame = e.value

    if isinstance(frame, meterbus.TelegramACK):
        meterbus.send_request_frame(ser, meterbus.ADDRESS_NETWORK_LAYER, read_echo=read_echo)
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

            if frame is not None:
                return frame

    except serial.serialutil.SerialException as e:
        print(e)

    return None

def serialize_frame(frame, encoding):
    # Simple serialization
    if str(encoding) == 'dump':
        return frame.to_JSON()

    # Pretty serialization
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

    if str(encoding) == 'json':
        return json.dumps(ydata, indent=4, sort_keys=True)

    elif str(encoding) == 'yaml':
        def float_representer(dumper, value):
            if int(value) == value:
                text = '{0:.4f}'.format(value).rstrip('0').rstrip('.')
                return dumper.represent_scalar(u'tag:yaml.org,2002:int', text)

            else:
                text = '{0:.4f}'.format(value).rstrip('0').rstrip('.')
                return dumper.represent_scalar(u'tag:yaml.org,2002:float', text)

        # Handle encoding formats
        yaml.add_representer(float, float_representer)
        yaml.add_representer(Decimal, float_representer)

        return yaml.dump(ydata, default_flow_style=False, allow_unicode=True, encoding=None)

    raise Exception("invalid serialization encoding {0}".format(encoding))


#
# Serial scan primary address tool
#
def serial_scan_primary():
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
    parser.add_argument('--echofix', action='store_true',
                        help='Read and ignore echoed data from target')
    parser.add_argument('device', type=str, help='Serial device or URI')

    args = parser.parse_args()

    meterbus.debug(args.d)

    try:
        with serial.serial_for_url(args.device,
                                   args.baudrate, 8, 'E', 1, timeout=1) as ser:
            for address in range(0, meterbus.MAX_PRIMARY_SLAVES + 1):
                if ping_address(ser, address, args.retries, args.echofix):
                    print(
                        "Found a M-Bus device at address {0}".format(address)
                    )
    except serial.serialutil.SerialException as e:
        print(e)


#
# Serial Scan secondary address tool
#
def serial_scan_secondary():
    def sec_addr_valid(string):
        if False is meterbus.is_secondary_address(string):
            raise argparse.ArgumentTypeError(
                "Not a valid secondary address mask")
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
    parser.add_argument('--echofix', action='store_true',
                        help='Read and ignore echoed data from target')
    parser.add_argument('device', type=str, help='Serial device or URI')

    args = parser.parse_args()

    meterbus.debug(args.d)

    try:
        with serial.serial_for_url(args.device,
                                   args.baudrate, 8, 'E', 1, timeout=1) as ser:

            # Ensure we are at the beginning of the records
            init_slaves(ser, args.echofix)

            mbus_scan_secondary_address_range(ser, 0, args.address, args.echofix)

    except serial.serialutil.SerialException as e:
        print(e)


#
# Serial request data tool (single frame reply)
#
def serial_request_single():
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
    parser.add_argument('-o', '--output', default="dump",
                        help='Output format')
    parser.add_argument('--echofix', action='store_true',
                        help='Read and ignore echoed data from target')
    parser.add_argument('device', type=str,
                        help='Serial device, URI or binary file')

    args = parser.parse_args()

    meterbus.debug(args.d)

    frame = None

    try:
        mode = os.stat(args.device).st_mode
        if stat.S_ISREG(mode):
            with open(args.device, 'rb') as f:
                frame = meterbus.load(f.read())
        else:
            frame = do_char_dev(args)

    except OSError:
            frame = do_char_dev(args)

    if frame is not None:
        print(serialize_frame(frame, args.output))


#
# Serial request data tool (multi frame reply)
#
def serial_request_multi():
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
    parser.add_argument('-o', '--output', default="json",
                        help='Output format')
    parser.add_argument('--echofix', action='store_true',
                        help='Read and ignore echoed data from target')
    parser.add_argument('device', type=str, help='Serial device or URI')
    args = parser.parse_args()

    meterbus.debug(args.d)

    address = args.address
    try:
        if 0 <= int(args.address) <= 254:
            address = int(args.address)
    except ValueError:
        pass

    try:
        ibt = meterbus.inter_byte_timeout(args.baudrate)
        with serial.serial_for_url(args.device,
                                   args.baudrate, 8, 'E', 1,
                                   inter_byte_timeout=ibt,
                                   timeout=1) as ser:
            frame = None

            if meterbus.is_primary_address(address):
                if False is ping_address(ser, address, args.retries):
                    sys.exit(1)

                meterbus.send_request_frame_multi(ser, address, read_echo=args.echofix)
                frame = meterbus.load(
                    meterbus.recv_frame(ser))

            elif meterbus.is_secondary_address(address):
                if False is ping_address(ser,
                                         meterbus.ADDRESS_NETWORK_LAYER, args.retries, args.echofix):
                    ping_address(ser, meterbus.ADDRESS_BROADCAST_NOREPLY, args.retries, args.echofix)

                meterbus.send_select_frame(ser, address, read_echo=args.echofix)
                frame = meterbus.load(meterbus.recv_frame(ser, 1))

                # Ensure that the select frame request was handled by the slave
                assert isinstance(frame, meterbus.TelegramACK)

                req = meterbus.send_request_frame_multi(
                          ser, meterbus.ADDRESS_NETWORK_LAYER, read_echo=args.echofix)

                try:
                    frame = meterbus.load(meterbus.recv_frame(ser))
                except meterbus.MBusFrameDecodeError:
                    frame = None

                while frame and frame.more_records_follow:
                    # toogle FCB on and off
                    req.header.cField.parts[0] ^= meterbus.CONTROL_MASK_FCB

                    req = meterbus.send_request_frame_multi(
                              ser, meterbus.ADDRESS_NETWORK_LAYER, req, read_echo=args.echofix)

                    next_frame = meterbus.load(meterbus.recv_frame(ser))
                    frame += next_frame

            if frame is not None:
                print(serialize_frame(frame, args.output))

    except serial.serialutil.SerialException as e:
        print(e)
