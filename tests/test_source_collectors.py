from __future__ import annotations

from app.collectors.feeds import (
    LandingJobsCollector,
    RemoteFirstJobsRssCollector,
    RemoteJobsOrgCollector,
    StartupJobsCollector,
    TheMuseCollector,
    WorkingNomadsCollector,
)
from app.collectors.public_pages import GetOnBoardCollector, _countries_from_location


class FixtureTheMuseCollector(TheMuseCollector):
    async def _get(self, params: dict[str, object] | None = None) -> object:
        return {
            "results": [
                {
                    "id": 42,
                    "name": "Senior Software Engineer",
                    "contents": "<p>Remote worldwide. React and TypeScript.</p>",
                    "publication_date": "2026-07-15T10:00:00Z",
                    "refs": {"landing_page": "https://www.themuse.com/jobs/example/42"},
                    "locations": [{"name": "Flexible / Remote"}],
                    "company": {"name": "Example"},
                }
            ]
        }


class FixtureStartupJobsCollector(StartupJobsCollector):
    async def _get(self, params: dict[str, object] | None = None) -> object:
        return {
            "data": [
                {
                    "id": "startup-1",
                    "title": "Full Stack Developer",
                    "description": "Remote for Latin America",
                    "url": "https://startup.jobs/example/startup-1",
                    "apply_url": "https://example.com/apply",
                    "company": {"name": "Startup"},
                    "location": "LATAM",
                    "salary_min": 80_000,
                    "salary_max": 120_000,
                    "salary_currency": "USD",
                    "published_at": "2026-07-15T10:00:00Z",
                }
            ]
        }


class FixtureWorkingNomadsCollector(WorkingNomadsCollector):
    async def _get(self, params: dict[str, object] | None = None) -> object:
        return [
            {
                "url": "https://www.workingnomads.com/job/react/1",
                "title": "React Developer",
                "description": "<p>React and TypeScript.</p>",
                "company_name": "Nomad Co",
                "category_name": "Development",
                "location": "Anywhere",
                "pub_date": "2026-07-15T10:00:00Z",
                "tags": "react",
            },
            {
                "url": "https://www.workingnomads.com/job/sales/2",
                "title": "Sales Executive",
                "description": "<p>Sales.</p>",
                "company_name": "Nomad Co",
                "category_name": "Sales",
                "location": "Anywhere",
                "pub_date": "2026-07-15T10:00:00Z",
                "tags": "sales",
            },
        ]


class FixtureRemoteJobsOrgCollector(RemoteJobsOrgCollector):
    async def _get(self, params: dict[str, object] | None = None) -> object:
        return {
            "data": [
                {
                    "id": "abc-123",
                    "title": "Frontend Engineer",
                    "url": "https://remotejobs.org/remote-jobs/frontend-engineer-acme",
                    "apply_url": "https://example.com/apply",
                    "company": {"name": "Acme"},
                    "category": {"name": "Programming", "slug": "programming"},
                    "location": "Remote",
                    "salary_min": 90_000,
                    "salary_max": 120_000,
                    "type": "Full-time",
                    "description": "React and TypeScript.",
                    "posted_at": "2026-07-16T07:00:00+00:00",
                }
            ]
        }


class FixtureLandingJobsCollector(LandingJobsCollector):
    async def _get(self, params: dict[str, object] | None = None) -> object:
        return [
            {
                "id": 10,
                "remote": True,
                "title": "Full Stack Engineer",
                "url": "https://landing.jobs/at/wellhub/full-stack-engineer",
                "role_description": "<p>React front end.</p>",
                "main_requirements": "<ul><li>TypeScript</li></ul>",
                "locations": [{"country_code": "BR"}, {"country_code": "PT"}],
                "type": "Full-time",
                "gross_salary_low": 40_000,
                "gross_salary_high": 60_000,
                "currency_code": "EUR",
                "published_at": "2026-07-10T10:00:00Z",
                "expires_at": "2026-10-10",
            },
            {
                "id": 11,
                "remote": False,
                "title": "Onsite Engineer",
                "url": "https://landing.jobs/at/acme/onsite-engineer",
                "role_description": "<p>Onsite.</p>",
                "published_at": "2026-07-12T10:00:00Z",
            },
        ]


async def test_working_nomads_collector_keeps_only_development() -> None:
    jobs, _ = await FixtureWorkingNomadsCollector(20, 20).collect()

    assert len(jobs) == 1
    assert jobs[0].title == "React Developer"
    assert jobs[0].company == "Nomad Co"


async def test_remotejobs_org_collector_normalizes_api() -> None:
    jobs, _ = await FixtureRemoteJobsOrgCollector(20, 20).collect()

    assert len(jobs) == 1
    assert jobs[0].company == "Acme"
    assert jobs[0].apply_url == "https://example.com/apply"
    assert jobs[0].salary_min == 90_000


async def test_landing_jobs_collector_keeps_remote_and_reads_countries() -> None:
    jobs, _ = await FixtureLandingJobsCollector(20, 20).collect()

    assert len(jobs) == 1
    assert jobs[0].company == "Wellhub"
    assert jobs[0].allowed_countries == ["BR", "PT"]
    assert jobs[0].salary_currency == "EUR"
    assert "TypeScript" in jobs[0].description


def test_remote_first_jobs_rss_splits_company_from_title() -> None:
    company, title = RemoteFirstJobsRssCollector._split_title("Senior Software Engineer at Twilio")

    assert company == "Twilio"
    assert title == "Senior Software Engineer"


async def test_the_muse_collector_normalizes_public_api() -> None:
    jobs, _ = await FixtureTheMuseCollector(20, 20, "test-key").collect()

    assert len(jobs) == 1
    assert jobs[0].company == "Example"
    assert jobs[0].location_text == "Flexible / Remote"


async def test_startup_jobs_collector_normalizes_api() -> None:
    jobs, _ = await FixtureStartupJobsCollector(20, 20, "test-key").collect()

    assert len(jobs) == 1
    assert jobs[0].salary_currency == "USD"
    assert jobs[0].apply_url == "https://example.com/apply"


def test_get_on_board_reads_structured_job() -> None:
    page = """
    <div itemscope itemtype="http://schema.org/JobPosting">
      <span itemprop="title">Frontend Engineer</span>
      <div itemprop="hiringOrganization"><strong itemprop="name">Acme</strong></div>
      <time itemprop="datePosted" datetime="2026-07-15T10:00:00Z"></time>
      <span itemprop="employmentType">FULL_TIME</span>
      <span class="location"><span title="Candidates can reside in Brazil.">Remote</span></span>
      <span itemprop="baseSalary">
        <span itemprop="value">
          <span itemprop="minValue" content="5000"></span>
          <span itemprop="maxValue" content="7000"></span>
          <span itemprop="unitText" content="MONTH"></span>
        </span>
        <span itemprop="currency" content="USD"></span>
      </span>
      <div itemprop="description"><p>React and <strong>TypeScript</strong>.</p></div>
    </div>
    """

    job = GetOnBoardCollector(20, 20, 7)._detail(
        page, "https://www.getonbrd.com/jobs/programming/frontend-engineer-acme-remote"
    )

    assert job.allowed_countries == ["BR"]
    assert job.salary_min == 5000
    assert job.salary_currency == "USD"
    assert job.description == "React and TypeScript."


def test_get_on_board_does_not_narrow_a_region_to_listed_countries() -> None:
    countries = _countries_from_location("Candidates can reside in South America or Mexico.")

    assert countries == []
