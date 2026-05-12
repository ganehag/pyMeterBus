from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from meterbus.model import (
    AckFrame,
    ApplicationKind,
    ControlField,
    ControlFrame,
    DataEncoding,
    DataInformation,
    DataRecord,
    DecodeResult,
    DecodedValue,
    Diagnostic,
    Direction,
    FrameKind,
    FunctionType,
    LongFrame,
    PrimaryAddress,
    Severity,
    ShortFrame,
    Telegram,
    Unit,
    UnknownRecord,
    ValueInformation,
    ValueType,
    VariableDataHeader,
    VariableDataTelegram,
)


def test_string_enums_are_json_friendly():
    assert FrameKind.LONG.value == "long"
    assert str(ApplicationKind.VARIABLE_DATA) == "variable_data"
    assert Severity.ERROR == "error"


def test_diagnostic_is_immutable_and_exportable():
    diagnostic = Diagnostic(
        severity=Severity.WARNING,
        code="checksum_mismatch",
        message="Checksum mismatch",
        offset=7,
        context={"expected": 1, "actual": 2},
    )

    assert diagnostic.to_dict() == {
        "severity": "warning",
        "code": "checksum_mismatch",
        "message": "Checksum mismatch",
        "offset": 7,
        "context": {"expected": 1, "actual": 2},
    }
    with pytest.raises(TypeError):
        diagnostic.context["expected"] = 3
    with pytest.raises(FrozenInstanceError):
        diagnostic.code = "changed"


def test_primary_address_validates_single_byte_range():
    assert PrimaryAddress(0).value == 0
    assert PrimaryAddress(255).value == 255

    with pytest.raises(ValueError):
        PrimaryAddress(-1)
    with pytest.raises(ValueError):
        PrimaryAddress(256)


def test_frame_models_preserve_raw_bytes_and_kind():
    diagnostic = Diagnostic(Severity.INFO, "example", "example")
    ack = AckFrame(diagnostics=(diagnostic,))
    short = ShortFrame(
        raw=b"\x10\x08\x0B\x13\x16",
        checksum=0x13,
        checksum_valid=True,
        diagnostics=(),
        control=ControlField(raw=0x08, direction=Direction.MASTER_TO_SLAVE),
        address=PrimaryAddress(0x0B),
    )
    control = ControlFrame(
        raw=b"\x68\x03\x03\x68\x08\x0B\x72\x85\x16",
        checksum=0x85,
        checksum_valid=True,
        diagnostics=(),
        length=3,
        control=ControlField(raw=0x08),
        address=PrimaryAddress(0x0B),
        ci=0x72,
    )
    long = LongFrame(
        raw=b"\x68\x03\x03\x68\x08\x0B\x72\x85\x16",
        checksum=0x85,
        checksum_valid=True,
        diagnostics=(),
        length=3,
        control=ControlField(raw=0x08),
        address=PrimaryAddress(0x0B),
        ci=0x72,
        payload=b"payload",
    )

    assert ack.kind is FrameKind.ACK
    assert ack.raw == b"\xE5"
    assert ack.diagnostics == (diagnostic,)
    assert short.kind is FrameKind.SHORT
    assert short.address.value == 0x0B
    assert control.kind is FrameKind.CONTROL
    assert control.ci == 0x72
    assert long.kind is FrameKind.LONG
    assert long.payload == b"payload"


def test_control_field_validates_single_byte_range():
    assert ControlField(0).raw == 0
    assert ControlField(255).raw == 255

    with pytest.raises(ValueError):
        ControlField(-1)
    with pytest.raises(ValueError):
        ControlField(256)


def test_record_models_allow_decimal_values_without_float_artifacts():
    unit = Unit(name="relative_humidity", symbol="%RH")
    dif = DataInformation(
        raw=b"\x02",
        data_encoding=DataEncoding.INTEGER,
        function=FunctionType.MINIMUM_VALUE,
        storage_number=0,
    )
    vif = ValueInformation(
        raw=b"\xFC\x03",
        unit=unit,
        kind="variable_vif",
        multiplier=Decimal("0.01"),
    )
    value = DecodedValue(
        raw=b"\xC8\x11",
        value=Decimal("45.52"),
        type=ValueType.DECIMAL,
        unit=unit,
        scaled=True,
    )
    record = DataRecord(
        raw=b"\x02\xFC\x03\xC8\x11",
        dif=dif,
        vif=vif,
        value=value,
        function=dif.function,
        storage_number=dif.storage_number,
    )

    assert record.value.value == Decimal("45.52")
    assert record.unit if False else record.vif.unit.symbol == "%RH"
    assert record.more_records_follow is False


def test_unknown_record_preserves_raw_bytes():
    record = UnknownRecord(raw=b"\x0F\xAA", reason="manufacturer_specific")

    assert record.raw == b"\x0F\xAA"
    assert record.reason == "manufacturer_specific"


def test_telegram_and_decode_result_models_connect_frame_to_application_data():
    frame = LongFrame(
        raw=b"\x68\x03\x03\x68\x08\x0B\x72\x85\x16",
        checksum=0x85,
        checksum_valid=True,
        diagnostics=(),
        length=3,
        control=ControlField(raw=0x08),
        address=PrimaryAddress(0x0B),
        ci=0x72,
        payload=b"",
    )
    header = VariableDataHeader(
        identification_number="00000021",
        manufacturer="ABC",
        manufacturer_raw=b"\xB0\x5C",
        version=2,
        medium=27,
        access_number=18,
        status=0,
        signature=b"\x00\x00",
        raw=b"header",
    )
    telegram = VariableDataTelegram(
        frame=frame,
        diagnostics=(),
        header=header,
        records=(),
        more_records_follow=False,
        raw_application_data=b"application",
    )
    result = DecodeResult(
        ok=True,
        telegram=telegram,
        frame=frame,
        diagnostics=(),
        raw=frame.raw,
    )

    assert isinstance(telegram, Telegram)
    assert telegram.application_kind is ApplicationKind.VARIABLE_DATA
    assert result.ok is True
    assert result.telegram is telegram
    assert result.frame is frame
