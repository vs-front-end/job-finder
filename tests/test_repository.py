from __future__ import annotations

from app.database import Repository
from app.models import (
    ApplicationEventType,
    Eligibility,
    EventCreate,
    GateResult,
    PlatformTrackingStatus,
    PlatformUpdate,
    RawJob,
)
from app.pipeline.normalize import normalize_job


def normalized(source: str = "feed", source_id: str = "job-1"):
    raw = RawJob(
        source=source,
        source_job_id=source_id,
        source_url=f"https://{source}.example/jobs/{source_id}",
        apply_url="https://company.example/Jobs/ABC?utm_source=feed",
        title="Software Engineer",
        company="Acme",
        description="Remote worldwide. React.",
        location_text="Worldwide",
    )
    gate = GateResult(
        decision=Eligibility.COMPATIBLE,
        role_match=True,
        geo_match="yes",
        reason="Worldwide",
        geo_evidence="worldwide",
    )
    return normalize_job(raw, gate, ["React"])


def test_upsert_deduplicates_same_canonical_url(repository: Repository) -> None:
    first_id, first_outcome = repository.upsert_job(normalized())
    second_id, second_outcome = repository.upsert_job(normalized("other", "other-1"))

    assert first_outcome == "inserted"
    assert second_outcome == "updated"
    assert first_id == second_id
    fetched = repository.get_job(first_id)
    assert fetched is not None
    assert len(fetched.sources) == 2


def test_event_updates_status_without_removing_history(repository: Repository) -> None:
    job_id, _ = repository.upsert_job(normalized())
    repository.add_event(job_id, EventCreate(event=ApplicationEventType.APPLIED_MANUAL))
    repository.add_event(job_id, EventCreate(event=ApplicationEventType.INTERVIEW_HR))

    job = repository.get_job(job_id)
    events = repository.list_events(job_id)

    assert job is not None
    assert job.workflow_status == "interview_hr"
    assert [event.event for event in events] == [
        ApplicationEventType.INTERVIEW_HR,
        ApplicationEventType.APPLIED_MANUAL,
    ]


def test_lists_uncertain_separately(repository: Repository) -> None:
    job = normalized()
    job.eligibility = Eligibility.UNCERTAIN
    repository.upsert_job(job)

    assert repository.list_jobs("new", "", 20, 0).total == 0
    assert repository.list_jobs("uncertain", "", 20, 0).total == 1


def test_platform_checklist_is_persistent(repository: Repository) -> None:
    updated = repository.update_platform(
        "revelo",
        PlatformUpdate(tracking_status=PlatformTrackingStatus.DONE, notes="Perfil completo"),
    )

    reloaded = next(platform for platform in repository.list_platforms() if platform.id == "revelo")

    assert updated.tracking_status == PlatformTrackingStatus.DONE
    assert reloaded.notes == "Perfil completo"
    assert reloaded.last_reviewed_at is not None
