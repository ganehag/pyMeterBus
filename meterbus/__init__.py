#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    python meterbus
    ~~~~~~~~~~~~~~~

    A library to decode M-Bus frames.

    :copyright: (c) 2017 by Mikael Ganehag Brorsson.
    :license: BSD, see LICENSE for more details.
"""

from .defines import *

from .core_objects import DataEncoding, FunctionType, MeasureUnit, VIFUnit, \
    VIFUnitExt, VIFUnitSecExt, VIFTable

from .telegram_ack import TelegramACK
from .telegram_short import TelegramShort
from .telegram_control import TelegramControl
from .telegram_long import TelegramLong

from .telegram_body import TelegramBody, TelegramBodyHeader, \
    TelegramBodyPayload

from .wtelegram_snd_nr import WTelegramSndNr
from .wtelegram_header import WTelegramHeader

from .exceptions import MBusFrameDecodeError, FrameMismatch

from .serial import *
from .aux import *


def load(data):
    if not data:
        raise MBusFrameDecodeError("empty frame")

    if isinstance(data, str):
        data = list(map(ord, data))

    for Frame in [WTelegramSndNr, TelegramACK, TelegramShort, TelegramControl,
                  TelegramLong]:
        try:
            return Frame.parse(data)

        except FrameMismatch as e:
            pass

    if not data:
        raise MBusFrameDecodeError("unable to decode frame")

def debug(state):
  pass
