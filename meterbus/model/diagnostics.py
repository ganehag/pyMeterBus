"""Diagnostics returned by pyMeterBus 2.0 decoders."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from .enums import Severity


@dataclass(frozen=True)
class Diagnostic:
    """A structured warning or error produced while decoding."""

    severity: Severity
    code: str
    message: str
    offset: int | None = None
    context: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "context", MappingProxyType(dict(self.context)))

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-friendly representation."""

        payload: dict[str, object] = {
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
        }
        if self.offset is not None:
            payload["offset"] = self.offset
        if self.context:
            payload["context"] = dict(self.context)
        return payload
