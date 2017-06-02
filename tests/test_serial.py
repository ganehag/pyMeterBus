import os
import sys
import serial

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import unittest
import meterbus
from meterbus.exceptions import *


class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.master = serial.serial_for_url(
            'loop://', baudrate=2400, timeout=0.1)
        self.slave = self.master
        self.partial_frame = b"\x68\x53\x53\x68\x08\x05\x72\x34\x08"
        self.crcerror_frame = b"\x68\x03\x03\x68\x08\x0b\x72\x00\x16"

    def reset(self):
        self.master.reset_input_buffer()
        self.master.reset_output_buffer()

    def test_valid_request(self):
        self.reset()
        meterbus.send_request_frame(self.master, 0)
        self.assertEqual(self.slave.read(5),
                         b"\x10\x5B\x00\x5B\x16")

    def test_existing_valid_request(self):
        self.reset()

        frame = meterbus.TelegramShort()
        frame.header.cField.parts = [
            meterbus.CONTROL_MASK_REQ_UD2 | meterbus.CONTROL_MASK_DIR_M2S
        ]
        frame.header.aField.parts = [0]

        meterbus.send_request_frame(self.master, req=frame)
        self.assertEqual(self.slave.read(5),
                         b"\x10\x5B\x00\x5B\x16")

    def test_ping_frame(self):
        self.reset()
        meterbus.send_ping_frame(self.master, 0)
        self.assertEqual(self.slave.read(5),
                         b"\x10\x40\x00\x40\x16")

        # Slave sends ACK reply
        self.slave.write(b'\xE5')

        frame_data = meterbus.recv_frame(self.master, 1)
        frame = meterbus.load(frame_data)

        self.assertIsInstance(frame, meterbus.TelegramACK)

    def test_invalid_ping_frame_address(self):
        self.reset()
        retval = meterbus.send_ping_frame(self.master, 600)
        self.assertEqual(retval, False)

    def test_invalid_request_frame_address(self):
        self.reset()
        retval = meterbus.send_request_frame(self.master, 600, None)
        self.assertEqual(retval, False)

    def test_request_frame(self):
        self.reset()
        frame = meterbus.TelegramShort()
        frame.header.cField.parts = [
            meterbus.CONTROL_MASK_REQ_UD2 | meterbus.CONTROL_MASK_DIR_M2S
        ]
        frame.header.aField.parts = [0]

        meterbus.send_request_frame(self.master, req=frame)

        self.assertEqual(self.slave.read(5),
                         b"\x10\x5B\x00\x5B\x16")

    def test_empty_reply(self):
        self.reset()
        meterbus.send_ping_frame(self.master,
                                 0)

        self.assertEqual(self.slave.read(5),
                         b"\x10\x40\x00\x40\x16")

        # Slave does not send anything

        frame_data = meterbus.recv_frame(self.master, 1)
        try:
            frame = meterbus.load(frame_data)
        except MBusFrameDecodeError as e:
            frame = e.value

        self.assertEqual(frame, None)

    def test_send_select_frame(self):
        self.reset()
        meterbus.send_select_frame(self.master,
                                   "00000001DADAFA1B")

        reply = (b"\x68\x0b\x0b\x68\x73\xfd\x52\x01\x00"
                 b"\x00\x00\xda\xda\xfa\x1b\x8c\x16")

        self.assertEqual(self.slave.read(len(reply)), reply)

        # Slave sends ACK reply
        self.slave.write(b'\xE5')

        frame_data = meterbus.recv_frame(self.master, 1)
        frame = meterbus.load(frame_data)

        self.assertIsInstance(frame, meterbus.TelegramACK)

    def test_invalid_multi_req_frame_address(self):
        self.reset()
        retval = meterbus.send_request_frame_multi(self.master,
                                                   600)
        self.assertEqual(retval, False)

    def test_multi_req_frame(self):
        self.reset()
        frame = meterbus.send_request_frame_multi(self.master,
                                                  0)

        self.assertEqual(self.slave.read(5),
                         b"\x10\x7B\x00\x7B\x16")

        # Next frame
        frame.header.cField.parts[0] ^= meterbus.CONTROL_MASK_FCB
        frame = meterbus.send_request_frame_multi(self.master,
                                                  req=frame)

        self.assertEqual(self.slave.read(5),
                         b"\x10\x5B\x00\x5B\x16")

    def test_read_partial_frame(self):
        self.reset()
        self.slave.write(self.partial_frame)
        frame = meterbus.recv_frame(self.master)
        self.assertEqual(frame, False)

    def test_crc_error_frame(self):
        self.reset()
        self.slave.write(self.crcerror_frame)
        frame = meterbus.recv_frame(self.master)
        self.assertEqual(frame, False)

if __name__ == '__main__':
    unittest.main()
