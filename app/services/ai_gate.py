from __future__ import annotations

import asyncio
import json

from app.config import AiConfig
from app.models import GateResult, RawJob


class AiGate:
    def __init__(self, config: AiConfig, profile: str):
        self.config = config
        self.profile = profile

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
        return f"""Analise a vaga para um candidato residente no Brasil. Não invente dados.
Ausência de restrição geográfica significa unknown, nunca yes.
Retorne SOMENTE JSON com decision, role_match, geo_match, reason, geo_evidence,
employment_type e payment_currency.

PERFIL:
{self.profile}

VAGA:
Título: {job.title}
Empresa: {job.company}
Localização: {job.location_text}
Descrição completa:
{job.description}
"""

    @staticmethod
    def _parse(value: str) -> GateResult:
        start = value.find("{")
        end = value.rfind("}")
        if start < 0 or end < start:
            raise ValueError("JSON ausente")
        return GateResult.model_validate_json(value[start : end + 1])
