from __future__ import annotations

import asyncio
import json

from app.config import AiConfig
from app.models import GateResult, RawJob


class AiGate:
    def __init__(self, config: AiConfig, profile: str, country: str = "BR"):
        self.config = config
        self.profile = profile
        self.country = country

    async def classify(self, job: RawJob, fallback: GateResult) -> GateResult:
        if not self.config.enabled:
            return fallback
        prompt = self._prompt(job)
        try:
            process = await asyncio.create_subprocess_exec(
                self.config.command,
                "-p",
                prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(process.communicate(), self.config.timeout_seconds)
            if process.returncode != 0:
                return fallback
            return self._parse(stdout.decode())
        except (FileNotFoundError, TimeoutError, ValueError, json.JSONDecodeError):
            return fallback

    def _prompt(self, job: RawJob) -> str:
        return f"""Analyze the job for a candidate residing in {self.country}. Do not invent data.
Absence of a geographic restriction means unknown, never yes.
Return ONLY JSON with decision, role_match, geo_match, reason, geo_evidence,
employment_type and payment_currency.

PROFILE:
{self.profile}

JOB:
Title: {job.title}
Company: {job.company}
Location: {job.location_text}
Full description:
{job.description}
"""

    @staticmethod
    def _parse(value: str) -> GateResult:
        start = value.find("{")
        end = value.rfind("}")
        if start < 0 or end < start:
            raise ValueError("missing JSON")
        return GateResult.model_validate_json(value[start : end + 1])
