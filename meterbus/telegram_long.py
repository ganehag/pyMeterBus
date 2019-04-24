import simplejson as json

from .telegram_body import TelegramBody
from .telegram_header import TelegramHeader
from .exceptions import (MBusFrameCRCError, MBusFrameDecodeError, FrameMismatch,
                         MbusFrameLengthError)

class TelegramLong(object):
    @staticmethod
    def parse(data):
        if data is None:
            raise MBusFrameDecodeError("Data is None")

        if data is not None and len(data) < 9:
            raise MBusFrameDecodeError("Invalid M-Bus length")

        if data[0] != 0x68:
            raise FrameMismatch()

        return TelegramLong(data)

    def __init__(self, dbuf=None):
        self._header = TelegramHeader()
        self._body = TelegramBody()

        if dbuf != None:
            tgr = dbuf
            if isinstance(dbuf, str):
                tgr = list(map(ord, dbuf))
            elif isinstance(dbuf, bytes):
                tgr = list(dbuf)

            headerLength = self.header.headerLength
            firstHeader = tgr[0:headerLength]

            # Copy CRC and stopByte into header
            resultHeader = firstHeader + tgr[-2:]

            self.header.load(resultHeader)

            # start + length + length + start = 4 bytes
            # crc + stop = 2 bytes
            if len(dbuf) - 6 < self.header.lField.parts[0]:
                raise MbusFrameLengthError(self.header.lField.parts[0] + 6)

            if self.header.lField.parts[0] < 3:
                raise MBusFrameDecodeError("Invalid M-Bus length value")

            self.body.load(tgr[headerLength:-2])

            if self.body.isVariableData == False:
                raise MBusFrameDecodeError("Not a variable data long frame")

            if not self.check_crc():
                raise MBusFrameCRCError(self.compute_crc(),
                                        self.header.crcField.parts[0])

    @property
    def secondary_address(self):
        layout = ("{0:02X}{1:02X}{2:02X}{3:02X}"
                  "{ma1:02X}{ma2:02X}{ver:02X}{med:02X}")
        sec = layout.format(
            *self.body.bodyHeader.id_nr,
            ma1=self.body.bodyHeader.manufacturer_field.parts[0],
            ma2=self.body.bodyHeader.manufacturer_field.parts[1],
            ver=self.body.bodyHeader.version_field.parts[0],
            med=self.body.bodyHeader.measure_medium_field.parts[0]
        )
        return sec

    @property
    def manufacturer(self):
       return self.body.bodyHeader.manufacturer_field.decodeManufacturer

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

    @property
    def more_records_follow(self):
        for rec in self.body.bodyPayload.records:
            if rec.more_records_follow:
                return True

        return False

    @property
    def interpreted(self):
        return {
            'head': self.header.interpreted,
            'body': self.body.interpreted
        }

    def load(self, tgr):
        telegram = tgr

        if isinstance(tgr, str):
            telegram = list(map(ord, tgr))

        headerLength = self.header.headerLength
        firstHeader = telegram[0:headerLength]

        # Copy CRC and stopByte into header
        resultHeader = firstHeader + telegram[-2:]

        self.header.load(resultHeader)
        self.body.load(telegram[headerLength:-2])

    # def parse(self):
    #     self.body.parse()

    def compute_crc(self):
        return (self.header.cField.parts[0] +
                self.header.aField.parts[0] +
                sum(self.body.bodyHeader.ci_field.parts) +
                sum(self.body.bodyHeader.id_nr_field.parts) +
                sum(self.body.bodyHeader.manufacturer_field.parts) +
                sum(self.body.bodyHeader.version_field.parts) +
                sum(self.body.bodyHeader.measure_medium_field.parts) +
                sum(self.body.bodyHeader.acc_nr_field.parts) +
                sum(self.body.bodyHeader.status_field.parts) +
                sum(self.body.bodyHeader.sig_field.parts) +
                sum(self.body.bodyPayload.body.parts)) % 256

    def check_crc(self):
        return self.compute_crc() == self.header.crcField.parts[0]

    def to_JSON(self):
        return json.dumps(self.interpreted, sort_keys=True, indent=4, use_decimal=True)

    def __len__(self):
       return (
         len(self.header.startField.parts) * 2 +
         len(self.header.lField.parts) * 2 +
         len(self.header.cField.parts) +
         len(self.header.aField.parts) +
         len(self.body.bodyHeader.ci_field.parts) +
         len(self.body.bodyHeader.id_nr_field.parts) +
         len(self.body.bodyHeader.manufacturer_field.parts) +
         len(self.body.bodyHeader.version_field.parts) +
         len(self.body.bodyHeader.measure_medium_field.parts) +
         len(self.body.bodyHeader.acc_nr_field.parts) +
         len(self.body.bodyHeader.status_field.parts) +
         len(self.body.bodyHeader.sig_field.parts) +
         len(self.body.bodyPayload.body.parts) +
         1 +
         len(self.header.stopField.parts)
       )

    def __iter__(self):
        self.header.lField = [
          len(self.header.cField.parts) +
          len(self.header.aField.parts) +
          len(self.body.bodyHeader.ci_field.parts) +
          len(self.body.bodyHeader.id_nr_field) +
          len(self.body.bodyHeader.manufacturer_field.parts) +
          len(self.body.bodyHeader.version_field.parts) +
          len(self.body.bodyHeader.measure_medium_field.parts) +
          len(self.body.bodyHeader.acc_nr_field.parts) +
          len(self.body.bodyHeader.status_field.parts) +
          len(self.body.bodyHeader.sig_field.parts) +
          len(self.body.bodyPayload.body.parts)
        ]

        yield self.header.startField.parts[0]
        yield self.header.lField.parts[0]
        yield self.header.lField.parts[0]
        yield self.header.startField.parts[0]

        yield self.header.cField.parts[0]
        yield self.header.aField.parts[0]
        yield self.body.bodyHeader.ci_field.parts[0]

        for part in self.body.bodyHeader.id_nr_field.parts:
            yield part

        for part in self.body.bodyHeader.manufacturer_field.parts:
            yield part

        for part in self.body.bodyHeader.version_field.parts:
            yield part

        for part in self.body.bodyHeader.measure_medium_field.parts:
            yield part

        for part in self.body.bodyHeader.acc_nr_field.parts:
            yield part

        for part in self.body.bodyHeader.status_field.parts:
            yield part

        for part in self.body.bodyHeader.sig_field.parts:
            yield part

        for part in self.body.bodyPayload.body.parts:
            yield part

        yield self.compute_crc()
        yield self.header.stopField.parts[0]

    def __add__(self, frame):
        import copy
        dup = copy.deepcopy(self)
        dup.body.bodyPayload._records = [
            x for x in dup.body.bodyPayload._records if not x.more_records_follow
        ]
        dup.body.bodyPayload._records += frame.body.bodyPayload._records
        return dup
