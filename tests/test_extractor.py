import json

from bs4 import BeautifulSoup

from app.services.extractor import JobPageExtractor


def test_finds_job_posting_inside_graph() -> None:
    payload = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Organization", "name": "Acme"},
            {"@type": "JobPosting", "title": "Senior Developer"},
        ],
    }
    soup = BeautifulSoup(
        f'<script type="application/ld+json">{json.dumps(payload)}</script>', "html.parser"
    )

    posting = JobPageExtractor._find_posting(soup)

    assert posting is not None
    assert posting["title"] == "Senior Developer"


def test_extracts_applicant_countries() -> None:
    posting = {
        "applicantLocationRequirements": [
            {"@type": "Country", "name": "Brazil"},
            {"@type": "AdministrativeArea", "name": "Latin America"},
        ]
    }

    location, countries, regions = JobPageExtractor._locations(posting)

    assert location == "Brazil, Latin America"
    assert countries == ["Brazil"]
    assert regions == ["Latin America"]
