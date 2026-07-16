from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class Eligibility(StrEnum):
    COMPATIBLE = "compatible"
    UNCERTAIN = "uncertain"
    INCOMPATIBLE = "incompatible"
    PENDING = "pending"
    ERROR = "error"


class WorkflowStatus(StrEnum):
    NEW = "new"
    SAVED = "saved"
    DISMISSED = "dismissed"
    APPLIED = "applied"
    INTERVIEW_HR = "interview_hr"
    CODE_TEST = "code_test"
    INTERVIEW_TECHNICAL = "interview_technical"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    CLOSED = "closed"


class ApplicationEventType(StrEnum):
    SAVED = "saved"
    DISMISSED = "dismissed"
    APPLIED_MANUAL = "applied_manual"
    INTERVIEW_HR = "interview_hr"
    CODE_TEST = "code_test"
    INTERVIEW_TECHNICAL = "interview_technical"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    CLOSED_WITHOUT_APPLICATION = "closed_without_application"


class PlatformAvailability(StrEnum):
    ACTIVE = "active"
    NEEDS_KEY = "needs_key"
    MANUAL = "manual"
    PLANNED = "planned"


class PlatformTrackingStatus(StrEnum):
    PENDING = "pending"
    DONE = "done"
    REVIEW_DUE = "review_due"
    SKIPPED = "skipped"


class RawJob(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    source_job_id: str | None = None
    source_url: str
    apply_url: str | None = None
    canonical_url: str | None = None
    ats: str | None = None
    ats_board: str | None = None
    ats_job_id: str | None = None
    title: str
    company: str
    description: str = ""
    location_text: str = ""
    remote_scope: str | None = None
    allowed_countries: list[str] = Field(default_factory=list)
    allowed_regions: list[str] = Field(default_factory=list)
    timezone_requirements: list[str] = Field(default_factory=list)
    employment_type: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = None
    salary_period: str | None = None
    date_posted: datetime | None = None
    valid_through: datetime | None = None
    raw_payload: dict[str, object] | None = None


class GateResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: Eligibility
    role_match: bool
    geo_match: Literal["yes", "unknown", "no"]
    reason: str
    geo_evidence: str | None = None
    employment_type: Literal["employee", "contractor", "eor", "unknown"] = "unknown"
    payment_currency: str = "unknown"


class NormalizedJob(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    source_job_id: str | None
    source_url: str
    apply_url: str
    canonical_url: str
    ats: str | None
    ats_board: str | None
    ats_job_id: str | None
    title: str
    normalized_title: str
    company: str
    normalized_company: str
    description: str
    location_text: str
    remote_scope: str | None
    geo_json: dict[str, object]
    employment_type: str | None
    salary_min: float | None
    salary_max: float | None
    salary_currency: str | None
    salary_period: str | None
    date_posted: datetime | None
    valid_through: datetime | None
    eligibility: Eligibility
    eligibility_reason: str
    geo_evidence: str | None
    relevant_technologies: list[str] = Field(default_factory=list)
    raw_payload: dict[str, object] | None = None


class JobSourceRead(BaseModel):
    source: str
    source_job_id: str | None
    source_url: str
    first_seen_at: datetime
    last_seen_at: datetime


class JobRead(BaseModel):
    id: int
    canonical_url: str
    apply_url: str
    ats: str | None
    ats_board: str | None
    ats_job_id: str | None
    title: str
    company: str
    description: str
    description_html: str | None
    location_text: str
    remote_scope: str | None
    geo_json: dict[str, object]
    employment_type: str | None
    salary_min: float | None
    salary_max: float | None
    salary_currency: str | None
    salary_period: str | None
    date_posted: datetime | None
    valid_through: datetime | None
    eligibility: Eligibility
    eligibility_reason: str
    geo_evidence: str | None
    workflow_status: WorkflowStatus
    relevant_technologies: list[str]
    first_seen_at: datetime
    last_seen_at: datetime
    last_verified_at: datetime | None
    closed_at: datetime | None
    sources: list[JobSourceRead] = Field(default_factory=list)


class JobListResponse(BaseModel):
    items: list[JobRead]
    total: int
    counts: dict[str, int]


class EventCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event: ApplicationEventType
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    notes: str = Field(default="", max_length=4000)


class ApplicationEventRead(EventCreate):
    id: int
    job_id: int


class EligibilityFeedback(BaseModel):
    model_config = ConfigDict(extra="forbid")

    eligibility: Eligibility
    reason: str = Field(min_length=2, max_length=500)


class UrlImport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: HttpUrl


class RunSummary(BaseModel):
    source: str
    status: Literal["success", "partial", "error", "running"]
    fetched: int = 0
    inserted: int = 0
    updated: int = 0
    duplicates: int = 0
    errors: int = 0
    error_message: str | None = None


class SourceHealth(BaseModel):
    source: str
    started_at: datetime
    finished_at: datetime | None
    status: str
    fetched: int
    inserted: int
    updated: int
    duplicates: int
    errors: int
    error_message: str | None


class PlatformRead(BaseModel):
    id: str
    name: str
    url: str
    category: str
    availability: PlatformAvailability
    description: str
    tracking_status: PlatformTrackingStatus
    last_reviewed_at: datetime | None = None
    notes: str = ""


class PlatformUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tracking_status: PlatformTrackingStatus
    notes: str = Field(default="", max_length=2000)
