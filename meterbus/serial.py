#!/usr/bin/python
# -*- coding: utf-8 -*-

from .telegram_short import TelegramShort
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

def recv_frame(ser, length=1):
  return ser.read(length)
