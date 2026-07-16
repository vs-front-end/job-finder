from __future__ import annotations

import json
import re
from contextlib import suppress
from datetime import UTC, datetime, timedelta
from html import unescape
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.collectors.values import (
    html_to_text,
    identifier,
    list_of_mappings,
    list_of_text,
    mapping,
    number,
    parse_datetime,
    text,
)
from app.models import RawJob

HEADERS = {"User-Agent": "JobFinder/0.1 (+local personal job research)"}


class PublicPageCollector:
    def __init__(self, timeout: int, limit: int, max_age_days: int):
        self.timeout = timeout
        self.limit = limit
        self.max_age_days = max_age_days

    async def _get(self, client: httpx.AsyncClient, url: str) -> str:
        response = await client.get(url)
        response.raise_for_status()
        return response.text

    def _is_recent(self, posted_at: datetime | None) -> bool:
        return posted_at is not None and posted_at >= datetime.now(UTC) - timedelta(
            days=self.max_age_days
        )


class ArcCollector(PublicPageCollector):
    name = "arc"
    base_url = "https://arc.dev"

    def __init__(self, timeout: int, limit: int, max_age_days: int, tags: list[str]):
        super().__init__(timeout, limit, max_age_days)
        self.tags = tags

    async def collect(self, checkpoint: str | None = None) -> tuple[list[RawJob], str | None]:
        jobs: list[RawJob] = []
        seen: set[str] = set()
        async with httpx.AsyncClient(
            timeout=self.timeout, follow_redirects=True, headers=HEADERS
        ) as client:
            for tag in self.tags:
                page = await self._get(client, f"{self.base_url}/remote-jobs/{tag}")
                for item in self._search_jobs(page):
                    job_id = identifier(item.get("randomKey"))
                    posted_at = parse_datetime(item.get("postedAt"))
                    if not job_id or job_id in seen or not self._is_recent(posted_at):
                        continue
                    seen.add(job_id)
                    slug = text(item.get("urlString"))
                    if not slug:
                        continue
                    url = f"{self.base_url}/remote-jobs/details/{slug}-{job_id}"
                    detail = item
                    with suppress(httpx.HTTPError):
                        detail = self._detail_job(await self._get(client, url)) or item
                    jobs.append(self._to_raw(detail, url, posted_at))
                    if len(jobs) >= self.limit:
                        return jobs, None
        return jobs, None

    @staticmethod
    def _page_props(page: str) -> object:
        script = BeautifulSoup(page, "html.parser").find("script", id="__NEXT_DATA__")
        if script is None or not script.string:
            return {}
        return mapping(mapping(mapping(json.loads(script.string)).get("props")).get("pageProps"))

    @classmethod
    def _search_jobs(cls, page: str) -> list[object]:
        return (
            list(cls._page_props(page).get("arcJobs", []))
            if isinstance(cls._page_props(page).get("arcJobs"), list)
            else []
        )

    @classmethod
    def _detail_job(cls, page: str) -> object:
        return cls._page_props(page).get("job")

    def _to_raw(self, value: object, url: str, posted_at: datetime | None) -> RawJob:
        item = mapping(value)
        countries = list_of_text(item.get("requiredCountries"))
        categories = [
            text(category.get("name")) for category in list_of_mappings(item.get("categories"))
        ]
        hourly_min = number(item.get("minHourlyRate"))
        hourly_max = number(item.get("maxHourlyRate"))
        company = mapping(item.get("company"))
        return RawJob(
            source=self.name,
            source_job_id=identifier(item.get("randomKey")),
            source_url=url,
            apply_url=url,
            title=text(item.get("title")),
            company=text(company.get("name"), "Confidential client via Arc"),
            description=text(item.get("description")) or ", ".join(categories),
            location_text=", ".join(countries) or "Remote",
            remote_scope="countries" if countries else "remote",
            allowed_countries=countries,
            timezone_requirements=list_of_text(item.get("timezone")),
            employment_type=text(item.get("jobType")) or None,
            salary_min=hourly_min or number(item.get("minAnnualSalary")),
            salary_max=hourly_max or number(item.get("maxAnnualSalary")),
            salary_period="hourly" if hourly_min or hourly_max else "annual",
            date_posted=posted_at or parse_datetime(item.get("createdAt")),
            raw_payload=dict(item),
        )


class YCombinatorCollector(PublicPageCollector):
    name = "y_combinator"
    base_url = "https://www.ycombinator.com"
    search_url = f"{base_url}/jobs/role/software-engineer/remote"

    async def collect(self, checkpoint: str | None = None) -> tuple[list[RawJob], str | None]:
        async with httpx.AsyncClient(
            timeout=self.timeout, follow_redirects=True, headers=HEADERS
        ) as client:
            listing = self._page_props(await self._get(client, self.search_url))
            candidates = list_of_mappings(listing.get("jobPostings"))
            jobs: list[RawJob] = []
            for item in candidates:
                posted_at = _relative_datetime(item.get("createdAt"))
                if not self._is_recent(posted_at):
                    continue
                relative_url = text(item.get("url"))
                if not relative_url:
                    continue
                url = urljoin(self.base_url, relative_url)
                detail = item
                with suppress(httpx.HTTPError):
                    detail_props = self._page_props(await self._get(client, url))
                    detail = mapping(detail_props.get("job")) or item
                jobs.append(self._to_raw(detail, url, posted_at))
                if len(jobs) >= self.limit:
                    break
            return jobs, None

    @staticmethod
    def _page_props(page: str) -> object:
        node = BeautifulSoup(page, "html.parser").select_one("[data-page]")
        if node is None:
            return {}
        value = node.attrs.get("data-page")
        if not isinstance(value, str):
            return {}
        return mapping(mapping(json.loads(unescape(value))).get("props"))

    def _to_raw(self, value: object, url: str, posted_at: datetime | None) -> RawJob:
        item = mapping(value)
        salary_min, salary_max, currency = _salary_range(item.get("salaryRange"))
        description = text(item.get("description"))
        if not description:
            description = "\n".join(
                filter(
                    None,
                    [
                        text(item.get("companyOneLiner")),
                        ", ".join(list_of_text(item.get("skills"))),
                        text(item.get("visa")),
                    ],
                )
            )
        return RawJob(
            source=self.name,
            source_job_id=identifier(item.get("id")),
            source_url=url,
            apply_url=text(item.get("applyUrl"), url),
            title=text(item.get("title")),
            company=text(item.get("companyName"), "Unknown"),
            description=description,
            location_text=text(item.get("location"), "Remote"),
            remote_scope="remote",
            employment_type=text(item.get("type")) or None,
            salary_min=salary_min,
            salary_max=salary_max,
            salary_currency=currency,
            salary_period="annual" if salary_min or salary_max else None,
            date_posted=posted_at,
            raw_payload=dict(item),
        )


class GetOnBoardCollector(PublicPageCollector):
    name = "get_on_board"
    search_url = "https://www.getonbrd.com/jobs/programming"

    async def collect(self, checkpoint: str | None = None) -> tuple[list[RawJob], str | None]:
        jobs: list[RawJob] = []
        seen: set[str] = set()
        async with httpx.AsyncClient(
            timeout=self.timeout, follow_redirects=True, headers=HEADERS
        ) as client:
            listing = BeautifulSoup(await self._get(client, self.search_url), "html.parser")
            for card in listing.select("a.results-item[href]"):
                href = card.attrs.get("href")
                if not isinstance(href, str) or not _programming_url(href):
                    continue
                url = href.split("?", 1)[0]
                if url in seen or not _remote_card(card):
                    continue
                seen.add(url)
                posted_at = _short_date(card)
                if not self._is_recent(posted_at):
                    continue
                try:
                    job = self._detail(await self._get(client, url), url)
                except (httpx.HTTPError, ValueError):
                    continue
                if self._is_recent(job.date_posted):
                    jobs.append(job)
                if len(jobs) >= self.limit:
                    break
        return jobs, None

    def _detail(self, page: str, url: str) -> RawJob:
        soup = BeautifulSoup(page, "html.parser")
        root = soup.select_one('[itemtype="http://schema.org/JobPosting"]')
        if root is None:
            raise ValueError("Get on Board não publicou dados estruturados")
        title = _item_text(root, "title")
        company_root = root.select_one('[itemprop="hiringOrganization"]')
        company = _item_text(company_root, "name") if company_root else "Unknown"
        location = root.select_one(".location")
        location_detail = location.select_one("[title]") if location else None
        location_title = location_detail.attrs.get("title") if location_detail else None
        location_text = (
            location_title
            if isinstance(location_title, str)
            else location.get_text(" ", strip=True)
            if location
            else "Remote"
        )
        countries = _countries_from_location(location_text)
        salary = root.select_one('[itemprop="baseSalary"]')
        description = root.select_one('[itemprop="description"]')
        source_id = url.rstrip("/").rsplit("/", 1)[-1]
        return RawJob(
            source=self.name,
            source_job_id=source_id,
            source_url=url,
            apply_url=url,
            title=title,
            company=company,
            description=html_to_text(str(description)) if description else "",
            location_text=location_text,
            remote_scope="worldwide" if "anywhere" in location_text.lower() else "remote",
            allowed_countries=countries,
            employment_type=_item_text(root, "employmentType") or None,
            salary_min=_item_number(salary, "minValue"),
            salary_max=_item_number(salary, "maxValue"),
            salary_currency=_item_content(salary, "currency"),
            salary_period=_item_content(salary, "unitText"),
            date_posted=_item_datetime(root, "datePosted"),
            raw_payload={"description": str(description)} if description else None,
        )


def _relative_datetime(value: object) -> datetime | None:
    label = text(value).lower()
    now = datetime.now(UTC)
    if label in {"today", "just now"}:
        return now
    match = re.search(r"(\d+)\s+(hour|day|week|month|year)s?", label)
    if not match:
        return None
    amount = int(match.group(1))
    unit = match.group(2)
    days = {"hour": 0, "day": 1, "week": 7, "month": 30, "year": 365}[unit] * amount
    return now - timedelta(days=days)


def _salary_range(value: object) -> tuple[float | None, float | None, str | None]:
    label = text(value)
    currency = None
    for marker, code in (("CA$", "CAD"), ("US$", "USD"), ("$", "USD"), ("€", "EUR"), ("£", "GBP")):
        if marker in label:
            currency = code
            break
    values = re.findall(r"(?:CA\$|US\$|[$€£])?\s*([\d,.]+)\s*([KkMm]?)", label)
    parsed: list[float] = []
    for raw, suffix in values:
        amount = number(raw)
        if amount is None:
            continue
        multiplier = 1_000_000 if suffix.lower() == "m" else 1_000 if suffix.lower() == "k" else 1
        parsed.append(amount * multiplier)
    return (
        parsed[0] if parsed else None,
        parsed[1] if len(parsed) > 1 else None,
        currency,
    )


def _programming_url(url: str) -> bool:
    return "/jobs/programming/" in url or "/empleos/programacion/" in url


def _remote_card(card: object) -> bool:
    if not hasattr(card, "select_one"):
        return False
    location = card.select_one(".location")
    return location is not None and "remote" in location.get_text(" ", strip=True).lower()


def _short_date(card: object) -> datetime | None:
    if not hasattr(card, "select"):
        return None
    months = {
        "jan": 1,
        "ene": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "abr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "ago": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
        "dic": 12,
    }
    for node in reversed(card.select(".opacity-half.size0")):
        match = re.fullmatch(r"([A-Za-z]{3})\s+(\d{1,2})", node.get_text(" ", strip=True))
        if match and match.group(1).lower() in months:
            now = datetime.now(UTC)
            parsed = datetime(
                now.year, months[match.group(1).lower()], int(match.group(2)), tzinfo=UTC
            )
            return (
                parsed if parsed <= now + timedelta(days=1) else parsed.replace(year=now.year - 1)
            )
    return None


def _item_text(root: object, prop: str) -> str:
    if not hasattr(root, "select_one"):
        return ""
    node = root.select_one(f'[itemprop="{prop}"]')
    return node.get_text(" ", strip=True) if node else ""


def _item_content(root: object, prop: str) -> str | None:
    if not hasattr(root, "select_one"):
        return None
    node = root.select_one(f'[itemprop="{prop}"]')
    value = node.attrs.get("content") if node else None
    return value.strip() if isinstance(value, str) and value.strip() else None


def _item_number(root: object, prop: str) -> float | None:
    return number(_item_content(root, prop))


def _item_datetime(root: object, prop: str) -> datetime | None:
    if not hasattr(root, "select_one"):
        return None
    node = root.select_one(f'[itemprop="{prop}"]')
    value = node.attrs.get("datetime") if node else None
    return parse_datetime(value)


def _countries_from_location(value: str) -> list[str]:
    country_codes = {
        "argentina": "AR",
        "brazil": "BR",
        "brasil": "BR",
        "chile": "CL",
        "colombia": "CO",
        "costa rica": "CR",
        "dominican republic": "DO",
        "ecuador": "EC",
        "guatemala": "GT",
        "mexico": "MX",
        "panama": "PA",
        "paraguay": "PY",
        "peru": "PE",
        "uruguay": "UY",
        "bolivia": "BO",
        "united states": "US",
        "canada": "CA",
    }
    lowered = value.lower()
    if any(
        region in lowered
        for region in ("anywhere", "worldwide", "south america", "latin america", "latam")
    ):
        return []
    return [code for name, code in country_codes.items() if name in lowered]
