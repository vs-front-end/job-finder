from __future__ import annotations

from app.config import AppConfig
from app.database import Repository
from app.models import GateResult, RawJob
from app.pipeline import Pipeline


class GoodCollector:
    name = "good"

    async def collect(self, checkpoint: str | None = None):
        return [
            RawJob(
                source="good",
                source_job_id="1",
                source_url="https://example.com/1",
                title="Software Engineer",
                company="Acme",
                description="Remote worldwide. React and Python.",
                location_text="Worldwide",
                remote_scope="remote",
            )
        ], None


class BrokenCollector:
    name = "broken"

    async def collect(self, checkpoint: str | None = None):
        raise RuntimeError("source unavailable")


class ChangedCollector:
    name = "good"

    async def collect(self, checkpoint: str | None = None):
        return [
            RawJob(
                source="good",
                source_job_id="1",
                source_url="https://example.com/1",
                title="Software Engineer",
                company="Acme",
                description="Remote worldwide. React, Python and TypeScript.",
                location_text="Worldwide",
                remote_scope="remote",
            )
        ], None


class RejectedCollector:
    name = "good"

    async def collect(self, checkpoint: str | None = None):
        return [
            RawJob(
                source="good",
                source_job_id="1",
                source_url="https://example.com/1",
                title="Engineering Manager",
                company="Acme",
                description="Remote worldwide. React and Python.",
                location_text="Worldwide",
                remote_scope="remote",
            )
        ], None


class CountingAiGate:
    def __init__(self) -> None:
        self.calls = 0

    async def classify(self, job: RawJob, fallback: GateResult) -> GateResult:
        self.calls += 1
        return fallback


class CountingLinkVerifier:
    def __init__(self) -> None:
        self.calls = 0

    async def is_open(self, url: str) -> bool:
        self.calls += 1
        return True


async def test_source_failure_does_not_cancel_following_source(
    repository: Repository, config: AppConfig
) -> None:
    pipeline = Pipeline(repository, config)

    summaries = await pipeline.run([BrokenCollector(), GoodCollector()])

    assert [summary.status for summary in summaries] == ["error", "success"]
    assert repository.list_jobs("new", "", 20, 0).total == 1


async def test_unchanged_job_skips_gates_on_later_runs(
    repository: Repository, config: AppConfig
) -> None:
    pipeline = Pipeline(repository, config)
    ai_gate = CountingAiGate()
    pipeline.ai_gate = ai_gate

    await pipeline.run([GoodCollector()])
    summaries = await pipeline.run([GoodCollector()])

    assert ai_gate.calls == 1
    assert summaries[0].updated == 1
    assert summaries[0].duplicates == 1
    assert repository.list_jobs("all", "", 20, 0).total == 1


async def test_unchanged_job_only_revalidates_link_after_interval(
    repository: Repository, config: AppConfig
) -> None:
    enabled_limits = config.limites.model_copy(update={"verificar_links": True})
    enabled_config = config.model_copy(update={"limites": enabled_limits})
    pipeline = Pipeline(repository, enabled_config)
    verifier = CountingLinkVerifier()
    pipeline.link_verifier = verifier

    await pipeline.run([GoodCollector()])
    await pipeline.run([GoodCollector()])

    assert verifier.calls == 1


async def test_changed_job_runs_gates_and_updates_existing_record(
    repository: Repository, config: AppConfig
) -> None:
    pipeline = Pipeline(repository, config)
    ai_gate = CountingAiGate()
    pipeline.ai_gate = ai_gate

    await pipeline.run([GoodCollector()])
    await pipeline.run([ChangedCollector()])

    result = repository.list_jobs("all", "", 20, 0)
    assert ai_gate.calls == 2
    assert result.total == 1
    assert "TypeScript" in result.items[0].description


async def test_job_is_removed_when_updated_title_fails_filter(
    repository: Repository, config: AppConfig
) -> None:
    pipeline = Pipeline(repository, config)

    await pipeline.run([GoodCollector()])
    await pipeline.run([RejectedCollector()])

    assert repository.list_jobs("all", "", 20, 0).total == 0
