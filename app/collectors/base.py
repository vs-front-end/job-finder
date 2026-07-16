from __future__ import annotations

from typing import Protocol

from app.models import RawJob


class Collector(Protocol):
    name: str

    async def collect(self, checkpoint: str | None = None) -> tuple[list[RawJob], str | None]: ...
