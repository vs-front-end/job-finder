from __future__ import annotations

import json
from urllib.parse import urljoin, urlsplit

import httpx
from bs4 import BeautifulSoup

from app.collectors.values import (
    html_to_text,
    list_of_mappings,
    mapping,
    number,
    parse_datetime,
    text,
)
from app.models import RawJob


class JobPageExtractor:
    def __init__(self, timeout: int):
        self.timeout = timeout

    async def extract(self, url: str) -> RawJob:
        headers = {"User-Agent": "JobFinder/0.1 (+local personal job research)"}
        async with httpx.AsyncClient(
            timeout=self.timeout, follow_redirects=True, headers=headers
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
        final_url = str(response.url)
        soup = BeautifulSoup(response.text, "html.parser")
        posting = self._find_posting(soup)
        if not posting:
            raise ValueError("The page has no recognizable JSON-LD JobPosting")
        organization = mapping(posting.get("hiringOrganization"))
        salary = mapping(posting.get("baseSalary"))
        salary_value = mapping(salary.get("value"))
        location_text, countries, regions = self._locations(posting)
        canonical_tag = soup.find("link", rel="canonical")
        canonical = text(canonical_tag.get("href")) if canonical_tag else final_url
        apply_url = self._apply_url(posting, final_url)
        identifier = posting.get("identifier")
        identifier_value = text(mapping(identifier).get("value")) or text(identifier)
        return RawJob(
            source=f"manual:{urlsplit(final_url).hostname or 'web'}",
            source_job_id=identifier_value or canonical,
            source_url=final_url,
            apply_url=apply_url,
            canonical_url=urljoin(final_url, canonical),
            title=text(posting.get("title")),
            company=text(organization.get("name"), "Unknown"),
            description=html_to_text(posting.get("description")),
            location_text=location_text,
            remote_scope="remote"
            if text(posting.get("jobLocationType")).upper() == "TELECOMMUTE"
            else None,
            allowed_countries=countries,
            allowed_regions=regions,
            employment_type=self._employment(posting.get("employmentType")),
            salary_min=number(salary_value.get("minValue")) or number(salary_value.get("value")),
            salary_max=number(salary_value.get("maxValue")) or number(salary_value.get("value")),
            salary_currency=text(posting.get("salaryCurrency")) or None,
            salary_period=text(salary_value.get("unitText")) or None,
            date_posted=parse_datetime(posting.get("datePosted")),
            valid_through=parse_datetime(posting.get("validThrough")),
            raw_payload=posting,
        )

    @classmethod
    def _find_posting(cls, soup: BeautifulSoup) -> dict[str, object] | None:
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                payload = json.loads(script.get_text())
            except (json.JSONDecodeError, TypeError):
                continue
            for item in cls._walk(payload):
                type_value = item.get("@type")
                types = type_value if isinstance(type_value, list) else [type_value]
                if "JobPosting" in types:
                    return item
        return None

    @classmethod
    def _walk(cls, value: object) -> list[dict[str, object]]:
        if isinstance(value, list):
            return [item for nested in value for item in cls._walk(nested)]
        if not isinstance(value, dict):
            return []
        items = [value]
        graph = value.get("@graph")
        if graph is not None:
            items.extend(cls._walk(graph))
        return items

    @staticmethod
    def _locations(posting: dict[str, object]) -> tuple[str, list[str], list[str]]:
        requirements = posting.get("applicantLocationRequirements")
        requirement_items = requirements if isinstance(requirements, list) else [requirements]
        countries: list[str] = []
        regions: list[str] = []
        for item in requirement_items:
            data = mapping(item)
            name = text(data.get("name"))
            kind = text(data.get("@type"))
            if not name:
                continue
            if kind == "Country":
                countries.append(name)
            else:
                regions.append(name)
        locations = list_of_mappings(posting.get("jobLocation"))
        labels = []
        for location in locations:
            address = mapping(location.get("address"))
            labels.append(
                ", ".join(
                    filter(
                        None,
                        [
                            text(address.get("addressLocality")),
                            text(address.get("addressRegion")),
                            text(address.get("addressCountry")),
                        ],
                    )
                )
            )
        location_text = ", ".join([*countries, *regions, *[label for label in labels if label]])
        return location_text or "Remote", countries, regions

    @staticmethod
    def _apply_url(posting: dict[str, object], fallback: str) -> str:
        for key in ("directApplyUrl", "url"):
            value = text(posting.get(key))
            if value:
                return urljoin(fallback, value)
        return fallback

    @staticmethod
    def _employment(value: object) -> str | None:
        if isinstance(value, list):
            labels = [item for item in value if isinstance(item, str)]
            return ", ".join(labels) or None
        return text(value) or None
