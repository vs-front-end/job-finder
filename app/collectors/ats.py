from __future__ import annotations

import httpx

from app.collectors.values import (
    html_to_text,
    identifier,
    list_of_mappings,
    mapping,
    number,
    parse_datetime,
    text,
)
from app.config import CompanyConfig
from app.models import RawJob


class AtsCollector:
    def __init__(self, company: CompanyConfig, timeout: int, limit: int):
        self.company = company
        self.timeout = timeout
        self.limit = limit
        self.name = f"{company.ats}:{company.board}"

    async def collect(self, checkpoint: str | None = None) -> tuple[list[RawJob], str | None]:
        methods = {
            "greenhouse": self._greenhouse,
            "lever": self._lever,
            "ashby": self._ashby,
        }
        method = methods.get(self.company.ats)
        if not method:
            raise ValueError(f"ATS não suportado na fase 1: {self.company.ats}")
        return await method(), None

    async def _request(self, url: str, params: dict[str, object] | None = None) -> object:
        headers = {"User-Agent": "JobFinder/0.1 (+local personal job research)"}
        async with httpx.AsyncClient(
            timeout=self.timeout, follow_redirects=True, headers=headers
        ) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    async def _greenhouse(self) -> list[RawJob]:
        payload = mapping(
            await self._request(
                f"https://boards-api.greenhouse.io/v1/boards/{self.company.board}/jobs",
                {"content": "true"},
            )
        )
        jobs = []
        for item in list_of_mappings(payload.get("jobs"))[: self.limit]:
            job_id = identifier(item.get("id"))
            url = text(item.get("absolute_url"))
            if not job_id or not url:
                continue
            location = text(mapping(item.get("location")).get("name"))
            metadata = list_of_mappings(item.get("metadata"))
            employment = next(
                (
                    text(meta.get("value"))
                    for meta in metadata
                    if text(meta.get("name")).lower() == "employment type"
                ),
                None,
            )
            jobs.append(
                RawJob(
                    source=self.name,
                    source_job_id=job_id,
                    source_url=url,
                    apply_url=url,
                    ats="greenhouse",
                    ats_board=self.company.board,
                    ats_job_id=job_id,
                    title=text(item.get("title")),
                    company=self.company.nome,
                    description=html_to_text(item.get("content")),
                    location_text=location,
                    remote_scope="remote" if "remote" in location.lower() else None,
                    employment_type=employment,
                    date_posted=parse_datetime(item.get("updated_at")),
                    raw_payload=dict(item),
                )
            )
        return jobs

    async def _lever(self) -> list[RawJob]:
        payload = await self._request(
            f"https://api.lever.co/v0/postings/{self.company.board}",
            {"mode": "json", "limit": self.limit},
        )
        jobs = []
        for item in list_of_mappings(payload):
            job_id = text(item.get("id"))
            url = text(item.get("hostedUrl"))
            apply_url = text(item.get("applyUrl")) or url
            if not job_id or not url:
                continue
            categories = mapping(item.get("categories"))
            location = text(categories.get("location"))
            lists = list_of_mappings(item.get("lists"))
            body = "\n\n".join(
                part
                for part in [
                    text(item.get("descriptionPlain")),
                    text(item.get("additionalPlain")),
                    *[
                        f"{text(section.get('text'))}\n{html_to_text(section.get('content'))}"
                        for section in lists
                    ],
                ]
                if part
            )
            salary = mapping(item.get("salaryRange"))
            jobs.append(
                RawJob(
                    source=self.name,
                    source_job_id=job_id,
                    source_url=url,
                    apply_url=apply_url,
                    ats="lever",
                    ats_board=self.company.board,
                    ats_job_id=job_id,
                    title=text(item.get("text")),
                    company=self.company.nome,
                    description=body,
                    location_text=location,
                    remote_scope="remote" if "remote" in location.lower() else None,
                    employment_type=text(categories.get("commitment")) or None,
                    salary_min=number(salary.get("min")),
                    salary_max=number(salary.get("max")),
                    salary_currency=text(salary.get("currency")) or None,
                    salary_period=text(salary.get("interval")) or None,
                    date_posted=parse_datetime(item.get("createdAt")),
                    raw_payload=dict(item),
                )
            )
        return jobs

    async def _ashby(self) -> list[RawJob]:
        payload = mapping(
            await self._request(
                f"https://api.ashbyhq.com/posting-api/job-board/{self.company.board}"
            )
        )
        jobs = []
        for item in list_of_mappings(payload.get("jobs"))[: self.limit]:
            job_id = text(item.get("id")) or text(item.get("jobUrl"))
            url = text(item.get("jobUrl"))
            apply_url = text(item.get("applyUrl")) or url
            if not job_id or not url:
                continue
            location = text(item.get("location"))
            jobs.append(
                RawJob(
                    source=self.name,
                    source_job_id=job_id,
                    source_url=url,
                    apply_url=apply_url,
                    ats="ashby",
                    ats_board=self.company.board,
                    ats_job_id=job_id,
                    title=text(item.get("title")),
                    company=self.company.nome,
                    description=html_to_text(item.get("descriptionHtml"))
                    or text(item.get("descriptionPlain")),
                    location_text=location,
                    remote_scope="remote" if item.get("isRemote") is True else None,
                    employment_type=text(item.get("employmentType")) or None,
                    date_posted=parse_datetime(item.get("publishedAt")),
                    raw_payload=dict(item),
                )
            )
        return jobs
