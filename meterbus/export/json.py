"""JSON export helper for pyMeterBus 2.0 models."""

from __future__ import annotations

import json
from typing import Any

from .dict import to_dict


def to_json(value: Any, *, indent: int | None = None) -> str:
    """Convert a pyMeterBus v2 model object into a deterministic JSON string."""

    separators = None if indent is not None else (",", ":")
    return json.dumps(
        to_dict(value),
        ensure_ascii=False,
        indent=indent,
        separators=separators,
        sort_keys=True,
    )
