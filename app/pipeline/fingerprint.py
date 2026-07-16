from __future__ import annotations

import hashlib
import json

from app.config import AppConfig
from app.models import RawJob
from app.pipeline.canonical import canonicalize_url

FINGERPRINT_VERSION = 4


def processing_fingerprint(job: RawJob, config: AppConfig) -> str:
    job_payload = job.model_dump(mode="json", exclude={"raw_payload"})
    job_payload["source_url"] = canonicalize_url(job.source_url)
    job_payload["apply_url"] = canonicalize_url(job.apply_url or job.source_url)
    job_payload["canonical_url"] = canonicalize_url(
        job.canonical_url or job.apply_url or job.source_url
    )
    payload = {
        "version": FINGERPRINT_VERSION,
        "job": job_payload,
        "profile": config.perfil.model_dump(mode="json"),
        "objective": config.objetivo.model_dump(mode="json"),
        "filters": config.filtros.model_dump(mode="json"),
        "ai_enabled": config.ia.enabled,
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()
