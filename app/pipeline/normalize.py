from __future__ import annotations

from app.collectors.values import html_to_text
from app.models import GateResult, NormalizedJob, RawJob
from app.pipeline.canonical import canonicalize_url, normalize_identity


def normalize_job(job: RawJob, gate: GateResult, technologies: list[str]) -> NormalizedJob:
    apply_url = canonicalize_url(job.apply_url or job.source_url)
    canonical_url = canonicalize_url(job.canonical_url or apply_url)
    description = html_to_text(job.description)
    return NormalizedJob(
        source=job.source,
        source_job_id=job.source_job_id,
        source_url=canonicalize_url(job.source_url),
        apply_url=apply_url,
        canonical_url=canonical_url,
        ats=job.ats,
        ats_board=job.ats_board,
        ats_job_id=job.ats_job_id,
        title=" ".join(job.title.split()),
        normalized_title=normalize_identity(job.title),
        company=" ".join(job.company.split()),
        normalized_company=normalize_identity(job.company),
        description=description,
        location_text=" ".join(job.location_text.split()),
        remote_scope=job.remote_scope,
        geo_json={
            "allowed_countries": job.allowed_countries,
            "allowed_regions": job.allowed_regions,
            "timezone_requirements": job.timezone_requirements,
        },
        employment_type=job.employment_type,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency,
        salary_period=job.salary_period,
        date_posted=job.date_posted,
        valid_through=job.valid_through,
        eligibility=gate.decision,
        eligibility_reason=gate.reason,
        geo_evidence=gate.geo_evidence,
        relevant_technologies=technologies,
        raw_payload=job.raw_payload,
    )
