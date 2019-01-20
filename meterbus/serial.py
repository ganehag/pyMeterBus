#!/usr/bin/python
# -*- coding: utf-8 -*-

from .globals import g
from .telegram_short import TelegramShort
from .telegram_long import TelegramLong
from .auxiliary import is_primary_address, is_secondary_address

from .telegram_ack import TelegramACK
from .telegram_short import TelegramShort
from .telegram_control import TelegramControl
from .telegram_long import TelegramLong
from .wtelegram_snd_nr import WTelegramSndNr

from .exceptions import (MBusFrameDecodeError, MBusFrameCRCError, FrameMismatch,
                         MbusFrameLengthError)

from .defines import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def serial_send(ser, data):
  if g.debug:
    frame_data = bytearray(data)
    logger.info('SEND ({0:03d}) {1}'.format(
       len(data),
       " ".join(["{:02x}".format(x).upper() for x in frame_data])
    ))

  ser.write(bytearray(data))

def send_ping_frame(ser, address):
  if is_primary_address(address) == False:
    return False

  frame = TelegramShort()
  frame.header.cField.parts = [
    CONTROL_MASK_SND_NKE | CONTROL_MASK_DIR_M2S
  ]
  frame.header.aField.parts = [address]

  serial_send(ser, frame)

def send_request_frame(ser, address=None, req=None):
  if address is not None and is_primary_address(address) == False:
    return False

  if req is None and address is not None:
    frame = TelegramShort()
    frame.header.cField.parts = [
      CONTROL_MASK_REQ_UD2 | CONTROL_MASK_DIR_M2S
    ]
    frame.header.aField.parts = [address]
  else:
    frame = req

  if frame is not None:
    serial_send(ser, frame)

  return frame

def send_request_frame_multi(ser, address=None, req=None):
  if address is not None and is_primary_address(address) == False:
    return False

  if req is None:
    frame = TelegramShort()
    frame.header.cField.parts = [
      CONTROL_MASK_REQ_UD2 | CONTROL_MASK_DIR_M2S | CONTROL_MASK_FCV | CONTROL_MASK_FCB
    ]
    frame.header.aField.parts = [address]
  else:
    frame = req

  if frame is not None:
    serial_send(ser, frame)

  return frame

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

  serial_send(ser, frame)


def recv_frame(ser, length=1):
  data = b""
  frame = None

  while frame is None:
    characters = ser.read(length)

    if isinstance(characters, str):
      characters = bytearray(characters)

    if len(characters) == 0:
      break

    data += characters

    if g.debug and characters:
      logger.info('RECV ({0:03d}) {1}'.format(
         len(characters),
         " ".join(["{:02x}".format(x).upper() for x in characters])
      ))

    for Frame in [WTelegramSndNr, TelegramACK, TelegramShort, TelegramControl,
                  TelegramLong]:
        try:
            frame = Frame.parse(list(data))
            return data

        except MBusFrameCRCError as e:
            pass

        except FrameMismatch as e:
            pass

        except MBusFrameDecodeError as e:
            pass

        except MbusFrameLengthError as e:
            length = (e.length) - len(data)

  if len(data):
    return False

  return None
