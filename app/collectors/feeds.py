from __future__ import annotations

import feedparser
import httpx

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


class JsonCollector:
    def __init__(self, name: str, url: str, timeout: int, limit: int):
        self.name = name
        self.url = url
        self.timeout = timeout
        self.limit = limit

    async def _get(self, params: dict[str, object] | None = None) -> object:
        headers = {"User-Agent": "JobFinder/0.1 (+local personal job research)"}
        async with httpx.AsyncClient(
            timeout=self.timeout, follow_redirects=True, headers=headers
        ) as client:
            response = await client.get(self.url, params=params)
            response.raise_for_status()
            return response.json()


class HimalayasCollector(JsonCollector):
    def __init__(self, timeout: int, limit: int, terms: list[str]):
        super().__init__("himalayas", "https://himalayas.app/jobs/api/search", timeout, limit)
        self.terms = terms or ["software engineer"]

    async def collect(self, checkpoint: str | None = None) -> tuple[list[RawJob], str | None]:
        items: list[object] = []
        latest_checkpoint = ""
        for term in self.terms:
            payload = mapping(await self._get({"q": term, "sort": "recent", "page": 1}))
            items.extend(list_of_mappings(payload.get("jobs")))
            latest_checkpoint = identifier(payload.get("updatedAt")) or latest_checkpoint
        jobs: list[RawJob] = []
        seen: set[str] = set()
        for item in list_of_mappings(items):
            countries = [
                text(country.get("alpha2"))
                for country in list_of_mappings(item.get("locationRestrictions"))
            ]
            guid = text(item.get("guid"))
            url = text(item.get("applicationLink"))
            if not guid or guid in seen or not url or not text(item.get("title")):
                continue
            seen.add(guid)
            timezones = item.get("timezoneRestrictions")
            jobs.append(
                RawJob(
                    source=self.name,
                    source_job_id=guid,
                    source_url=url,
                    apply_url=url,
                    title=text(item.get("title")),
                    company=text(item.get("companyName"), "Unknown"),
                    description=html_to_text(item.get("description")),
                    location_text=", ".join(countries) if countries else "Worldwide",
                    remote_scope="worldwide" if not countries else "countries",
                    allowed_countries=[country for country in countries if country],
                    timezone_requirements=(
                        [str(value) for value in timezones if isinstance(value, int | float | str)]
                        if isinstance(timezones, list)
                        else []
                    ),
                    employment_type=text(item.get("employmentType")) or None,
                    salary_min=number(item.get("minSalary")),
                    salary_max=number(item.get("maxSalary")),
                    salary_currency=text(item.get("currency")) or None,
                    salary_period=text(item.get("salaryPeriod")) or None,
                    date_posted=parse_datetime(item.get("pubDate")),
                    valid_through=parse_datetime(item.get("expiryDate")),
                    raw_payload=dict(item),
                )
            )
            if len(jobs) >= self.limit:
                break
        return jobs, latest_checkpoint or None


class JobicyCollector(JsonCollector):
    def __init__(self, timeout: int, limit: int):
        super().__init__("jobicy", "https://jobicy.com/api/v2/remote-jobs", timeout, limit)

    async def collect(self, checkpoint: str | None = None) -> tuple[list[RawJob], str | None]:
        payload = mapping(
            await self._get({"count": min(self.limit, 50), "industry": "engineering"})
        )
        jobs = []
        for item in list_of_mappings(payload.get("jobs")):
            job_id = identifier(item.get("id"))
            url = text(item.get("url"))
            if not job_id or not url or not text(item.get("jobTitle")):
                continue
            jobs.append(
                RawJob(
                    source=self.name,
                    source_job_id=job_id,
                    source_url=url,
                    apply_url=url,
                    title=text(item.get("jobTitle")),
                    company=text(item.get("companyName"), "Unknown"),
                    description=html_to_text(item.get("jobDescription")),
                    location_text=text(item.get("jobGeo"), "Remote"),
                    remote_scope=text(item.get("jobGeo")) or None,
                    employment_type=(
                        ", ".join(list_of_text(item.get("jobType")))
                        or text(item.get("jobType"))
                        or None
                    ),
                    salary_min=(
                        number(item.get("salaryMin")) or number(item.get("annualSalaryMin"))
                    ),
                    salary_max=(
                        number(item.get("salaryMax")) or number(item.get("annualSalaryMax"))
                    ),
                    salary_currency=text(item.get("salaryCurrency")) or None,
                    salary_period=text(item.get("salaryPeriod"), "annual"),
                    date_posted=parse_datetime(item.get("pubDate")),
                    raw_payload=dict(item),
                )
            )
        return jobs, None


class RemoteOkCollector(JsonCollector):
    def __init__(self, timeout: int, limit: int):
        super().__init__("remote_ok", "https://remoteok.com/api", timeout, limit)

    async def collect(self, checkpoint: str | None = None) -> tuple[list[RawJob], str | None]:
        payload = await self._get()
        items = list_of_mappings(payload)
        jobs = []
        for item in items:
            job_id = identifier(item.get("id"))
            url = text(item.get("apply_url")) or text(item.get("url"))
            if not job_id or not url or not text(item.get("position")):
                continue
            jobs.append(
                RawJob(
                    source=self.name,
                    source_job_id=job_id,
                    source_url=text(item.get("url"), url),
                    apply_url=url,
                    title=text(item.get("position")),
                    company=text(item.get("company"), "Unknown"),
                    description=html_to_text(item.get("description")),
                    location_text=text(item.get("location"), "Remote"),
                    remote_scope="remote",
                    employment_type="full-time",
                    salary_min=number(item.get("salary_min")),
                    salary_max=number(item.get("salary_max")),
                    salary_currency="USD" if number(item.get("salary_min")) else None,
                    salary_period="annual",
                    date_posted=parse_datetime(item.get("date")),
                    raw_payload=dict(item),
                )
            )
        return jobs[: self.limit], None


class RemotiveCollector(JsonCollector):
    def __init__(self, timeout: int, limit: int):
        super().__init__("remotive", "https://remotive.com/api/remote-jobs", timeout, limit)

    async def collect(self, checkpoint: str | None = None) -> tuple[list[RawJob], str | None]:
        payload = mapping(await self._get({"category": "software-dev", "limit": self.limit}))
        jobs = []
        for item in list_of_mappings(payload.get("jobs")):
            job_id = identifier(item.get("id"))
            url = text(item.get("url"))
            if not job_id or not url or not text(item.get("title")):
                continue
            jobs.append(
                RawJob(
                    source=self.name,
                    source_job_id=job_id,
                    source_url=url,
                    apply_url=url,
                    title=text(item.get("title")),
                    company=text(item.get("company_name"), "Unknown"),
                    description=html_to_text(item.get("description")),
                    location_text=text(item.get("candidate_required_location"), "Remote"),
                    remote_scope=text(item.get("candidate_required_location")) or None,
                    employment_type=text(item.get("job_type")) or None,
                    date_posted=parse_datetime(item.get("publication_date")),
                    raw_payload=dict(item),
                )
            )
        return jobs[: self.limit], None


class ArbeitnowCollector(JsonCollector):
    def __init__(self, timeout: int, limit: int):
        super().__init__("arbeitnow", "https://www.arbeitnow.com/api/job-board-api", timeout, limit)

    async def collect(self, checkpoint: str | None = None) -> tuple[list[RawJob], str | None]:
        payload = mapping(await self._get())
        jobs = []
        for item in list_of_mappings(payload.get("data")):
            if item.get("remote") is not True:
                continue
            slug = text(item.get("slug"))
            url = text(item.get("url"))
            if not slug or not url or not text(item.get("title")):
                continue
            jobs.append(
                RawJob(
                    source=self.name,
                    source_job_id=slug,
                    source_url=url,
                    apply_url=url,
                    title=text(item.get("title")),
                    company=text(item.get("company_name"), "Unknown"),
                    description=html_to_text(item.get("description")),
                    location_text=text(item.get("location"), "Remote"),
                    remote_scope="remote",
                    employment_type="full-time",
                    date_posted=parse_datetime(item.get("created_at")),
                    raw_payload=dict(item),
                )
            )
        return jobs[: self.limit], None


class TheMuseCollector(JsonCollector):
    def __init__(self, timeout: int, limit: int, api_key: str):
        super().__init__("the_muse", "https://www.themuse.com/api/public/jobs", timeout, limit)
        self.api_key = api_key

    async def collect(self, checkpoint: str | None = None) -> tuple[list[RawJob], str | None]:
        payload = mapping(
            await self._get(
                {
                    "page": 0,
                    "category": "Software Engineering",
                    "location": "Flexible / Remote",
                    "descending": "true",
                    "api_key": self.api_key,
                }
            )
        )
        jobs: list[RawJob] = []
        for item in list_of_mappings(payload.get("results")):
            job_id = identifier(item.get("id"))
            refs = mapping(item.get("refs"))
            url = text(refs.get("landing_page"))
            if not job_id or not url or not text(item.get("name")):
                continue
            locations = [
                text(location.get("name")) for location in list_of_mappings(item.get("locations"))
            ]
            company = mapping(item.get("company"))
            jobs.append(
                RawJob(
                    source=self.name,
                    source_job_id=job_id,
                    source_url=url,
                    apply_url=url,
                    title=text(item.get("name")),
                    company=text(company.get("name"), "Unknown"),
                    description=html_to_text(item.get("contents")),
                    location_text=", ".join(locations) or "Remote",
                    remote_scope="remote",
                    date_posted=parse_datetime(item.get("publication_date")),
                    raw_payload=dict(item),
                )
            )
        return jobs[: self.limit], None


class StartupJobsCollector(JsonCollector):
    def __init__(self, timeout: int, limit: int, api_key: str):
        super().__init__("startup_jobs", "https://api.startup.jobs/v1/jobs", timeout, limit)
        self.api_key = api_key

    async def _get(self, params: dict[str, object] | None = None) -> object:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "JobFinder/0.1 (+local personal job research)",
        }
        async with httpx.AsyncClient(
            timeout=self.timeout, follow_redirects=True, headers=headers
        ) as client:
            response = await client.get(self.url, params=params)
            response.raise_for_status()
            return response.json()

    async def collect(self, checkpoint: str | None = None) -> tuple[list[RawJob], str | None]:
        payload = mapping(await self._get({"workplace_type": "remote", "role": "engineering"}))
        items = (
            list_of_mappings(payload.get("data"))
            or list_of_mappings(payload.get("jobs"))
            or list_of_mappings(payload.get("results"))
        )
        jobs: list[RawJob] = []
        for item in items:
            job_id = identifier(item.get("id"))
            url = text(item.get("url")) or text(item.get("job_url"))
            apply_url = text(item.get("apply_url")) or url
            company_value = item.get("company")
            company = mapping(company_value)
            company_name = text(company.get("name")) or text(item.get("company_name"))
            if not job_id or not url or not text(item.get("title")):
                continue
            countries = list_of_text(item.get("countries"))
            jobs.append(
                RawJob(
                    source=self.name,
                    source_job_id=job_id,
                    source_url=url,
                    apply_url=apply_url,
                    title=text(item.get("title")),
                    company=company_name or "Unknown",
                    description=html_to_text(item.get("description")),
                    location_text=(
                        text(item.get("location"))
                        or text(item.get("candidate_location"))
                        or "Remote"
                    ),
                    remote_scope="remote",
                    allowed_countries=countries,
                    employment_type=text(item.get("employment_type")) or None,
                    salary_min=number(item.get("salary_min")),
                    salary_max=number(item.get("salary_max")),
                    salary_currency=text(item.get("salary_currency")) or None,
                    salary_period=text(item.get("salary_period")) or None,
                    date_posted=(
                        parse_datetime(item.get("published_at"))
                        or parse_datetime(item.get("created_at"))
                    ),
                    raw_payload=dict(item),
                )
            )
        return jobs[: self.limit], None


class RssCollector:
    def __init__(self, name: str, url: str, timeout: int, limit: int):
        self.name = name
        self.url = url
        self.timeout = timeout
        self.limit = limit

    async def collect(self, checkpoint: str | None = None) -> tuple[list[RawJob], str | None]:
        headers = {"User-Agent": "JobFinder/0.1 (+local personal job research)"}
        async with httpx.AsyncClient(
            timeout=self.timeout, follow_redirects=True, headers=headers
        ) as client:
            response = await client.get(self.url)
            response.raise_for_status()
        parsed = feedparser.parse(response.content)
        jobs = []
        for entry in parsed.entries[: self.limit]:
            item = mapping(entry)
            title_value = text(item.get("title"))
            url = text(item.get("link"))
            if not title_value or not url:
                continue
            company, title = self._split_title(title_value)
            jobs.append(
                RawJob(
                    source=self.name,
                    source_job_id=text(item.get("id")) or url,
                    source_url=url,
                    apply_url=url,
                    title=title,
                    company=company,
                    description=html_to_text(item.get("summary")),
                    location_text=self._location(item),
                    remote_scope="remote",
                    date_posted=parse_datetime(item.get("published")),
                    raw_payload=dict(item),
                )
            )
        return jobs, text(mapping(parsed.get("feed")).get("updated")) or None

    @staticmethod
    def _split_title(value: str) -> tuple[str, str]:
        if ":" in value:
            company, title = value.split(":", 1)
            return company.strip(), title.strip()
        return "Unknown", value

    @staticmethod
    def _location(item: object) -> str:
        data = mapping(item)
        tags = list_of_mappings(data.get("tags"))
        labels = [text(tag.get("term")) for tag in tags]
        location = next(
            (label for label in labels if "only" in label.lower() or "world" in label.lower()), ""
        )
        return location or "Remote"


def default_rss(timeout: int, limit: int) -> RssCollector:
    return RssCollector(
        "we_work_remotely", "https://weworkremotely.com/remote-jobs.rss", timeout, limit
    )


class WeWorkRemotelyCollector:
    name = "we_work_remotely"
    urls = (
        "https://weworkremotely.com/categories/remote-full-stack-programming-jobs.rss",
        "https://weworkremotely.com/categories/remote-back-end-programming-jobs.rss",
        "https://weworkremotely.com/categories/remote-front-end-programming-jobs.rss",
        "https://weworkremotely.com/categories/remote-programming-jobs.rss",
        "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
    )

    def __init__(self, timeout: int, limit: int):
        self.timeout = timeout
        self.limit = limit

    async def collect(self, checkpoint: str | None = None) -> tuple[list[RawJob], str | None]:
        jobs: list[RawJob] = []
        seen: set[str] = set()
        latest_checkpoint = ""
        for url in self.urls:
            collected, current_checkpoint = await RssCollector(
                self.name, url, self.timeout, self.limit
            ).collect(checkpoint)
            latest_checkpoint = current_checkpoint or latest_checkpoint
            for job in collected:
                identity = job.source_job_id or job.source_url
                if identity in seen:
                    continue
                seen.add(identity)
                jobs.append(job)
                if len(jobs) >= self.limit:
                    return jobs, latest_checkpoint or None
        return jobs, latest_checkpoint or None
