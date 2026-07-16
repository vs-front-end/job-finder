from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import ValidationError

from app.collectors import build_collectors
from app.models import (
    ApplicationEventRead,
    EligibilityFeedback,
    EventCreate,
    JobListResponse,
    JobRead,
    PlatformRead,
    PlatformUpdate,
    Preferences,
    RunSummary,
    SourceHealth,
    UrlImport,
)
from app.pipeline import Pipeline
from app.services.extractor import JobPageExtractor
from app.services.preferences import apply_preferences, read_preferences, write_config

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/jobs", response_model=JobListResponse)
def list_jobs(
    request: Request,
    tab: str = "new",
    q: str = "",
    limit: Annotated[int, Query(ge=1, le=100)] = 30,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> JobListResponse:
    return request.app.state.repository.list_jobs(tab, q.strip(), limit, offset)


@router.get("/jobs/{job_id}", response_model=JobRead)
def get_job(job_id: int, request: Request) -> JobRead:
    job = request.app.state.repository.get_job(job_id)
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    return job


@router.get("/jobs/{job_id}/events", response_model=list[ApplicationEventRead])
def list_events(job_id: int, request: Request) -> list[ApplicationEventRead]:
    return request.app.state.repository.list_events(job_id)


@router.post("/jobs/{job_id}/events", response_model=ApplicationEventRead)
def add_event(job_id: int, event: EventCreate, request: Request) -> ApplicationEventRead:
    if not request.app.state.repository.get_job(job_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    return request.app.state.repository.add_event(job_id, event)


@router.patch("/jobs/{job_id}/eligibility", status_code=status.HTTP_204_NO_CONTENT)
def correct_eligibility(job_id: int, feedback: EligibilityFeedback, request: Request) -> None:
    try:
        request.app.state.repository.correct_eligibility(job_id, feedback)
    except KeyError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found") from error


@router.post("/jobs/{job_id}/verify")
async def verify_job(job_id: int, request: Request) -> dict[str, bool]:
    job = request.app.state.repository.get_job(job_id)
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    is_open = await request.app.state.pipeline.link_verifier.is_open(job.apply_url)
    request.app.state.repository.mark_verified(job_id, is_open)
    return {"open": is_open}


@router.post("/jobs/import", response_model=RunSummary)
async def import_job(payload: UrlImport, request: Request) -> RunSummary:
    extractor = JobPageExtractor(request.app.state.config.limites.timeout_segundos)
    try:
        raw_job = await extractor.extract(str(payload.url))
    except Exception as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error

    class ManualCollector:
        name = raw_job.source

        async def collect(self, checkpoint: str | None = None):
            return [raw_job], None

    summaries = await request.app.state.pipeline.run([ManualCollector()])
    return summaries[0]


@router.post("/runs", status_code=status.HTTP_202_ACCEPTED)
async def run_now(request: Request) -> dict[str, str]:
    pipeline = request.app.state.pipeline
    if pipeline.lock.locked():
        raise HTTPException(status.HTTP_409_CONFLICT, "A collection run is already in progress")
    task = asyncio.create_task(pipeline.run(request.app.state.collectors))
    request.app.state.run_task = task
    return {"status": "started"}


@router.get("/runs/status")
def run_status(request: Request) -> dict[str, bool]:
    return {"running": request.app.state.pipeline.lock.locked()}


@router.get("/sources", response_model=list[SourceHealth])
def sources(request: Request) -> list[SourceHealth]:
    return request.app.state.repository.source_health()


@router.get("/platforms", response_model=list[PlatformRead])
def platforms(request: Request) -> list[PlatformRead]:
    return request.app.state.repository.list_platforms()


@router.patch("/platforms/{platform_id}", response_model=PlatformRead)
def update_platform(platform_id: str, payload: PlatformUpdate, request: Request) -> PlatformRead:
    try:
        return request.app.state.repository.update_platform(platform_id, payload)
    except KeyError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Platform not found") from error


@router.get("/preferences", response_model=Preferences)
def get_preferences(request: Request) -> Preferences:
    return read_preferences(request.app.state.config)


@router.put("/preferences", response_model=Preferences)
def update_preferences(payload: Preferences, request: Request) -> Preferences:
    state = request.app.state
    if state.pipeline.lock.locked():
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Wait for the current collection run to finish"
        )
    try:
        config = apply_preferences(state.config, payload)
    except ValidationError as error:
        first = error.errors()[0]
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, f"{first['loc']}: {first['msg']}"
        ) from error
    write_config(config, state.config_path)
    state.config = config
    state.collectors = build_collectors(config)
    state.pipeline = Pipeline(state.repository, config)
    scheduler = state.scheduler
    scheduler.pipeline = state.pipeline
    scheduler.collectors = state.collectors
    scheduler.interval = timedelta(hours=config.limites.intervalo_padrao_horas)
    return read_preferences(config)
