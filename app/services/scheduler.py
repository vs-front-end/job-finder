from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from app.collectors.base import Collector
from app.config import AppConfig
from app.database import Repository
from app.pipeline import Pipeline


class Scheduler:
    def __init__(
        self,
        repository: Repository,
        pipeline: Pipeline,
        collectors: list[Collector],
        config: AppConfig,
    ):
        self.repository = repository
        self.pipeline = pipeline
        self.collectors = collectors
        self.interval = timedelta(hours=config.limites.intervalo_padrao_horas)
        self.stop_event = asyncio.Event()

    async def serve(self) -> None:
        while not self.stop_event.is_set():
            due = [collector for collector in self.collectors if self._is_due(collector.name)]
            if due and not self.pipeline.lock.locked():
                await self.pipeline.run(due)
            try:
                await asyncio.wait_for(self.stop_event.wait(), timeout=60)
            except TimeoutError:
                continue

    def stop(self) -> None:
        self.stop_event.set()

    def _is_due(self, source: str) -> bool:
        last_success = self.repository.last_success(source)
        return last_success is None or datetime.now(UTC) - last_success >= self.interval
