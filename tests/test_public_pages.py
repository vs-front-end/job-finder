from __future__ import annotations

import json
from datetime import UTC, datetime
from html import escape

from app.collectors.public_pages import (
    ArcCollector,
    YCombinatorCollector,
    _relative_datetime,
    _salary_range,
)


def test_arc_reads_next_data_jobs() -> None:
    payload = {"props": {"pageProps": {"arcJobs": [{"randomKey": "abc"}]}}}
    page = f'<script id="__NEXT_DATA__" type="application/json">{json.dumps(payload)}</script>'

    jobs = ArcCollector._search_jobs(page)

    assert len(jobs) == 1
    assert jobs[0]["randomKey"] == "abc"


def test_y_combinator_reads_data_page() -> None:
    payload = {"props": {"jobPostings": [{"id": 42}]}}
    page = f'<div data-page="{escape(json.dumps(payload), quote=True)}"></div>'

    props = YCombinatorCollector._page_props(page)

    assert props["jobPostings"][0]["id"] == 42


def test_relative_job_age() -> None:
    parsed = _relative_datetime("6 days")

    assert parsed is not None
    assert 5 <= (datetime.now(UTC) - parsed).days <= 6


def test_salary_range_with_strong_currency() -> None:
    minimum, maximum, currency = _salary_range("€70K - €95K")

    assert minimum == 70_000
    assert maximum == 95_000
    assert currency == "EUR"
