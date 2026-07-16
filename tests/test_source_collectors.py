from __future__ import annotations

from app.collectors.feeds import StartupJobsCollector, TheMuseCollector
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
