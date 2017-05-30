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

    def reset(self):
        self.master.reset_input_buffer()
        self.master.reset_output_buffer()

    def test_valid_request(self):
        self.reset()
        meterbus.send_request_frame(self.master, 0)
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

if __name__ == '__main__':
    unittest.main()
