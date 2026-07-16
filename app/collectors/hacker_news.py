from __future__ import annotations

import re

import httpx

from app.collectors.values import (
    html_to_text,
    identifier,
    list_of_mappings,
    mapping,
    parse_datetime,
    text,
)
from app.models import RawJob


class HackerNewsCollector:
    name = "hacker_news"

    def __init__(self, timeout: int, limit: int):
        self.timeout = timeout
        self.limit = limit

    async def collect(self, checkpoint: str | None = None) -> tuple[list[RawJob], str | None]:
        headers = {"User-Agent": "JobFinder/0.1 (+local personal job research)"}
        async with httpx.AsyncClient(
            timeout=self.timeout, follow_redirects=True, headers=headers
        ) as client:
            story_response = await client.get(
                "https://hn.algolia.com/api/v1/search_by_date",
                params={"tags": "story,author_whoishiring", "hitsPerPage": 10},
            )
            story_response.raise_for_status()
            story = self._latest_story(mapping(story_response.json()).get("hits"))
            story_id = identifier(story.get("objectID"))
            if not story_id:
                return [], checkpoint
            comments_response = await client.get(
                "https://hn.algolia.com/api/v1/search",
                params={"tags": f"comment,story_{story_id}", "hitsPerPage": min(self.limit, 1000)},
            )
            comments_response.raise_for_status()
        jobs = []
        for item in list_of_mappings(mapping(comments_response.json()).get("hits")):
            body = html_to_text(item.get("comment_text"))
            if not self._is_remote(body):
                continue
            job_id = identifier(item.get("objectID"))
            title, company = self._identity(body)
            if not job_id or not title:
                continue
            url = f"https://news.ycombinator.com/item?id={job_id}"
            jobs.append(
                RawJob(
                    source=self.name,
                    source_job_id=job_id,
                    source_url=url,
                    apply_url=self._first_url(body) or url,
                    title=title,
                    company=company,
                    description=body,
                    location_text=self._location(body),
                    remote_scope="remote",
                    date_posted=parse_datetime(item.get("created_at")),
                    raw_payload=dict(item),
                )
            )
        return jobs, story_id

    @staticmethod
    def _latest_story(value: object) -> dict[str, object]:
        for story in list_of_mappings(value):
            title = text(story.get("title")).lower()
            if "who is hiring" in title:
                return dict(story)
        return {}

    @staticmethod
    def _is_remote(body: str) -> bool:
        lowered = body.lower()
        return "remote" in lowered and not re.search(r"\bno remote\b|\bon-?site only\b", lowered)

    @staticmethod
    def _identity(body: str) -> tuple[str, str]:
        first_line = next((line.strip() for line in body.splitlines() if line.strip()), "")
        parts = [part.strip() for part in first_line.split("|") if part.strip()]
        company = parts[0][:120] if parts else "Unknown"
        role = next(
            (
                part
                for part in parts[1:]
                if re.search(r"engineer|developer|devops|frontend|backend|full.?stack", part, re.I)
            ),
            "Software role",
        )
        return role[:200], company

    @staticmethod
    def _location(body: str) -> str:
        match = re.search(
            r"(?:remote[^|\n]{0,80}|(?:brazil|latam|latin america|worldwide|americas)[^|\n]{0,60})",
            body,
            re.I,
        )
        return match.group(0).strip() if match else "Remote"

    @staticmethod
    def _first_url(body: str) -> str | None:
        match = re.search(r"https?://[^\s<>)\]]+", body)
        return match.group(0).rstrip(".,") if match else None
