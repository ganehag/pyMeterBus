"""Helpers for loading pyMeterBus golden fixtures in tests.

The fixture corpus is intentionally plain: raw frame and telegram bytes live in
`.hex` files so they can also be reused by non-Python implementations later.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures"


@dataclass(frozen=True)
class HexFixture:
    """A loaded `.hex` fixture."""

    name: str
    path: Path
    data: bytes

    @property
    def hex(self) -> str:
        """Return normalized uppercase hex separated by spaces."""

        return self.data.hex(" ").upper()


def fixture_root() -> Path:
    """Return the root directory for test fixtures."""

    return _FIXTURE_ROOT


def parse_hex_fixture_text(text: str) -> bytes:
    """Parse fixture text containing hexadecimal bytes.

    The parser accepts whitespace between bytes and ignores comments beginning
    with `#`. It fails loudly if a token is not exactly one byte of hex.
    """

    tokens: list[str] = []
    for line in text.splitlines():
        line_without_comment = line.split("#", 1)[0]
        for token in line_without_comment.split():
            if len(token) != 2:
                raise ValueError(f"invalid hex byte token: {token!r}")
            try:
                int(token, 16)
            except ValueError as exc:
                raise ValueError(f"invalid hex byte token: {token!r}") from exc
            tokens.append(token)

    return bytes.fromhex("".join(tokens))


def load_hex_fixture(relative_path: str | Path) -> HexFixture:
    """Load a `.hex` fixture by path relative to `tests/fixtures`."""

    path = fixture_root() / relative_path
    data = parse_hex_fixture_text(path.read_text(encoding="utf-8"))
    return HexFixture(name=path.stem, path=path, data=data)


def iter_hex_fixtures(subdir: str) -> tuple[HexFixture, ...]:
    """Load all `.hex` fixtures below a fixture subdirectory."""

    root = fixture_root() / subdir
    return tuple(
        load_hex_fixture(path.relative_to(fixture_root()))
        for path in sorted(root.glob("*.hex"))
    )
