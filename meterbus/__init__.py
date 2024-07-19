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

from .wtelegram_snd_nr import WTelegramSndNr
from .wtelegram_body import WTelegramFrame
from .wtelegram_header import WTelegramHeader

from .exceptions import MBusFrameDecodeError, FrameMismatch

from .serial import *
from .auxiliary import *

__author__ = "Mikael Ganehag Brorsson"
__license__ = "BSD-3-Clause"
__version__ = "0.8.4"


def load(data):
    if not data:
        raise MBusFrameDecodeError("empty frame", data)

    data = convert_data(data)

    for Frame in (TelegramACK, TelegramShort, TelegramControl,
                  TelegramLong, WTelegramSndNr):
        try:
            return Frame.parse(data)

        except FrameMismatch as e:
            pass

    raise MBusFrameDecodeError("unable to decode frame")


def load_all(data):
    if not data:
        raise MBusFrameDecodeError("empty frame", data)

    dats = split_frames(convert_data(data))

    return [load(d) for d in dats]


def convert_data(data):

    if isinstance(data, list):
        # assume that the data is already processed and quickly return it
        return data

    elif isinstance(data, str):
        data = list(map(ord, data))

    elif isinstance(data, bytes):
        data = list(data)

    elif isinstance(data, bytearray):
        data = list(data)

    return data


def split_frames(data):
    """
    try to extract more then one frame from data and return a list
    of frames

    there are user cases in tcp connection when more then one frame
    is received from the slave in one batch. These are long frames
    in all the user cases, but the split function is designed to
    be more generic and able to split all kinds of mbus frames
    """

    data = convert_data(data)
    # or assume the data is already converted and skip this step

    if data is None or len(data) == 0:
        raise MBusFrameDecodeError("Data is None")

    while len(data) > 0:
        # ack
        if data[0] == 0xE5:
            yield data[:1]
            data = data[1:]
            continue

        # short frame
        elif len(data) >= 5 and data[0] == 0x10 and data[4] == 0x16:
            yield data[:5]
            data = data[5:]
            continue

        # long/control frame (+6 is for the header)
        elif data[0] == 0x68 and data[3] == 0x68 and data[1] == data[2] \
                and len(data) >= data[1]+6 and data[data[1]+6-1] == 0x16:
            yield data[:data[1] + 6]
            data = data[data[1] + 6:]
            continue

        else:
            raise MBusFrameDecodeError("invalid data")
            # or could consume data by bytes
            # data = data[1:]



def debug(state):
  g.debug = state
