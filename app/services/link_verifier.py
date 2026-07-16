from __future__ import annotations

import re

import httpx

CLOSED_PATTERNS = re.compile(
    r"job (?:is )?no longer available|no longer accepting applications|"
    r"position has been filled|job not found|vaga encerrada",
    re.IGNORECASE,
)


class LinkVerifier:
    def __init__(self, timeout: int):
        self.timeout = timeout

    async def is_open(self, url: str) -> bool:
        headers = {"User-Agent": "JobFinder/0.1 (+local personal job research)"}
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout, follow_redirects=True, headers=headers
            ) as client:
                response = await client.get(url)
            if response.status_code in {404, 410} or response.status_code >= 500:
                return False
            if response.status_code in {401, 403, 429}:
                return True
            return not CLOSED_PATTERNS.search(response.text[:200_000])
        except httpx.HTTPError:
            return True
