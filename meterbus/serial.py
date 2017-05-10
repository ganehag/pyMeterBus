#!/usr/bin/python
# -*- coding: utf-8 -*-

from .telegram_short import TelegramShort
from .telegram_long import TelegramLong
from .aux import is_primary_address, is_secondary_address
from .defines import *

def send_ping_frame(ser, address):
  if is_primary_address(address) == False:
    return False

  frame = TelegramShort()
  frame.header.cField.parts = [
    CONTROL_MASK_SND_NKE | CONTROL_MASK_DIR_M2S
  ]
  frame.header.aField.parts = [address]

  ser.write(frame)

def send_request_frame(ser, address):
  if is_primary_address(address) == False:
    return False

  frame = TelegramShort()
  frame.header.cField.parts = [
    CONTROL_MASK_REQ_UD2 | CONTROL_MASK_DIR_M2S
  ]
  frame.header.aField.parts = [address]

  ser.write(frame)

def send_select_frame(ser, secondary_address):
  frame = TelegramLong()

  frame.header.cField.parts = [
    CONTROL_MASK_SND_UD | CONTROL_MASK_DIR_M2S | CONTROL_MASK_FCB
  ]
  frame.header.aField.parts = [ADDRESS_NETWORK_LAYER]

  frame.body.bodyHeaderLength = 9
  frame_data = [
    CONTROL_INFO_SELECT_SLAVE,
    0, 0, 0, 0,
    0, 0, 0, 0
  ]
  val = int(secondary_address[14:], 16)
  frame_data[8] = val & 0xFF

  val = int(secondary_address[12:14], 16)
  frame_data[7] = val & 0xFF

  val = int(secondary_address[8:12], 16)
  frame_data[5] = (val>>8) & 0xFF
  frame_data[6] = val & 0xFF

  frame_data[4] = int(secondary_address[0:2], 16)
  frame_data[3] = int(secondary_address[2:4], 16)
  frame_data[2] = int(secondary_address[4:6], 16)
  frame_data[1] = int(secondary_address[6:8], 16)

  frame.body.bodyHeader = frame_data

  ser.write(frame)


def recv_frame(ser, length=1):
  return ser.read(length)
