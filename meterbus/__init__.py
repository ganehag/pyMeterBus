#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    python meterbus
    ~~~~~~~~~~~~~~~

    A library to decode M-Bus frames.

    :copyright: (c) 2017-2019 by Mikael Ganehag Brorsson.
    :license: BSD, see LICENSE for more details.
"""

from .globals import g
from .defines import *

from .core_objects import DataEncoding, FunctionType, MeasureUnit, VIFUnit, \
    VIFUnitExt, VIFUnitSecExt, VIFTable, DateCalculator

from .telegram_ack import TelegramACK
from .telegram_short import TelegramShort
from .telegram_control import TelegramControl
from .telegram_long import TelegramLong

from .data_information_block import DataInformationBlock
from .value_information_block import ValueInformationBlock
from .telegram_header import TelegramHeader
from .telegram_body import TelegramBody, TelegramBodyHeader, \
    TelegramBodyPayload
from .telegram_field import TelegramField
from .telegram_variable_data_record import TelegramVariableDataRecord

try:
    from .wtelegram_snd_nr import WTelegramSndNr
    from .wtelegram_body import WTelegramFrame, WTelegramBaseDataHeader
    from .wtelegram_header import WTelegramHeader
except ImportError:
    WTelegramSndNr = None
    WTelegramFrame = None
    WTelegramBaseDataHeader = None
    WTelegramHeader = None

from .exceptions import MBusFrameDecodeError, FrameMismatch

try:
    from .serial import *
except ImportError:
    pass

from .auxiliary import *
from .api import decode, decode_one, decode_one_frame

__author__ = "Mikael Ganehag Brorsson"
__license__ = "BSD-3-Clause"
__version__ = "0.8.4"


def load(data):
    if not data:
        raise MBusFrameDecodeError("empty frame", data)

    if isinstance(data, str):
        data = list(map(ord, data))

    elif isinstance(data, bytes):
        data = list(data)

    elif isinstance(data, bytearray):
        data = list(data)

    elif isinstance(data, list):
        pass

    frame_types = [TelegramACK, TelegramShort, TelegramControl, TelegramLong]
    if WTelegramSndNr is not None:
        frame_types.insert(0, WTelegramSndNr)

    for Frame in frame_types:
        try:
            return Frame.parse(data)

        except FrameMismatch as e:
            pass

    raise MBusFrameDecodeError("unable to decode frame")

def debug(state):
  g.debug = state

def add_wmbus_encryption_key(id_nr, key):
    if WTelegramBaseDataHeader is None:
        raise ImportError("wireless M-Bus support requires pycryptodome")
    WTelegramBaseDataHeader.add_decryption_key(id_nr, key)
