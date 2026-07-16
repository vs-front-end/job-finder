from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from app.collectors.base import Collector
from app.config import AppConfig
from app.database import Repository
from app.models import Eligibility, RunSummary
from app.pipeline.canonical import canonicalize_url
from app.pipeline.fingerprint import processing_fingerprint
from app.pipeline.gates import geographic_gate, remote_gate, technical_gate
from app.pipeline.normalize import normalize_job
from app.services.ai_gate import AiGate
from app.services.link_verifier import LinkVerifier


class Pipeline:
    def __init__(self, repository: Repository, config: AppConfig):
        self.repository = repository
        self.config = config
        self.lock = asyncio.Lock()
        self.ai_gate = AiGate(config.ia, config.perfil.resumo)
        self.link_verifier = LinkVerifier(config.limites.timeout_segundos)

    async def run(self, collectors: list[Collector]) -> list[RunSummary]:
        if self.lock.locked():
            raise RuntimeError("Já existe uma coleta em andamento")
        async with self.lock:
            summaries = []
            for collector in collectors:
                summaries.append(await self._run_collector(collector))
            return summaries

    async def _run_collector(self, collector: Collector) -> RunSummary:
        run_id = self.repository.start_run(collector.name)
        summary = RunSummary(source=collector.name, status="running")
        try:
            jobs, _ = await collector.collect()
            summary.fetched = len(jobs)
            for raw_job in jobs:
                try:
                    apply_url = canonicalize_url(raw_job.apply_url or raw_job.source_url)
                    canonical_url = canonicalize_url(raw_job.canonical_url or apply_url)
                    source_url = canonicalize_url(raw_job.source_url)
                    fingerprint = processing_fingerprint(raw_job, self.config)
                    existing = self.repository.find_existing_job(
                        ats=raw_job.ats,
                        ats_board=raw_job.ats_board,
                        ats_job_id=raw_job.ats_job_id,
                        source=raw_job.source,
                        source_job_id=raw_job.source_job_id,
                        source_url=source_url,
                        canonical_url=canonical_url,
                        apply_url=apply_url,
                    )
                    remote = remote_gate(raw_job)
                    if not remote.accepted:
                        if existing:
                            self.repository.delete_job(existing.job_id)
                        continue
                    if raw_job.valid_through and raw_job.valid_through < datetime.now(UTC):
                        if existing:
                            self.repository.mark_verified(existing.job_id, False)
                        continue
                    if (
                        existing
                        and existing.source_id is not None
                        and existing.payload_hash == fingerprint
                    ):
                        self.repository.touch_existing_job(
                            existing, raw_job.raw_payload, fingerprint
                        )
                        if self._link_revalidation_due(existing.last_verified_at):
                            is_open = await self.link_verifier.is_open(apply_url)
                            self.repository.mark_verified(existing.job_id, is_open)
                        summary.updated += 1
                        summary.duplicates += 1
                        continue
                    technical = technical_gate(raw_job, self.config)
                    if not technical.accepted:
                        if existing:
                            self.repository.delete_job(existing.job_id)
                        continue
                    gate = geographic_gate(raw_job, self.config.objetivo.pais_residencia)
                    if gate.decision != Eligibility.INCOMPATIBLE:
                        gate = await self.ai_gate.classify(raw_job, gate)
                    normalized = normalize_job(raw_job, gate, technical.technologies)
                    job_id, outcome = self.repository.upsert_job(normalized, fingerprint)
                    if self.config.limites.verificar_links:
                        is_open = await self.link_verifier.is_open(normalized.apply_url)
                        self.repository.mark_verified(job_id, is_open)
                        if not is_open:
                            continue
                    if outcome == "inserted":
                        summary.inserted += 1
                    else:
                        summary.updated += 1
                        summary.duplicates += 1
                except Exception:
                    summary.errors += 1
            summary.status = "partial" if summary.errors else "success"
        except Exception as error:
            summary.status = "error"
            summary.errors += 1
            summary.error_message = str(error)[:1000]
        self.repository.finish_run(run_id, summary)
        return summary

    def _link_revalidation_due(self, last_verified_at: datetime | None) -> bool:
        if not self.config.limites.verificar_links:
            return False
        if last_verified_at is None:
            return True
        maximum_age = timedelta(hours=self.config.limites.revalidar_links_horas)
        return datetime.now(UTC) - last_verified_at.astimezone(UTC) >= maximum_age
