from __future__ import annotations

from enum import StrEnum


class ExportView(StrEnum):
    """Named export shapes for dict and JSON output."""

    FULL = "full"
    SUMMARY = "summary"
    RECORDS = "records"
