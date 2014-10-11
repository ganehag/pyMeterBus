import json

from .telegram_header import TelegramHeader
from .telegram_body import TelegramBody


class Telegram(object):
    def __init__(self, header=None, body=None):
        if header:
            self._header = header
        else:
            self._header = TelegramHeader()
        if body:
            self._body = body
        else:
            self._body = TelegramBody()

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, value):
        self._header = TelegramHeader()
        self._header.load(value)

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        self._body = TelegramBody()
        self._body.load(value)

    @property
    def records(self):
        """Alias property for easy access to records"""
        return self.body.bodyPayload.records

    def load(self, tgr):
        telegram = tgr

        if isinstance(tgr, basestring):
            telegram = map(ord, tgr)

        headerLength = self.header.headerLength
        firstHeader = telegram[0:headerLength]

        # Copy CRC and stopByte into header
        resultHeader = firstHeader + telegram[-2:]

        self.header.load(resultHeader)
        self.body.load(telegram[headerLength:-2])

    def parse(self):
        self.body.parse()

    def debug(self):
        self.header.debug()
        self.body.debug()

    def to_JSON(self):
        return json.dumps({
            'head': json.loads(self.header.to_JSON()),
            'body': json.loads(self.body.to_JSON())
        }, sort_keys=False, indent=4)
