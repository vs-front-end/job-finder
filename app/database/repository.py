from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.models import (
    ApplicationEventRead,
    ApplicationEventType,
    EligibilityFeedback,
    EventCreate,
    JobListResponse,
    JobRead,
    JobSourceRead,
    NormalizedJob,
    PlatformAvailability,
    PlatformRead,
    PlatformTrackingStatus,
    PlatformUpdate,
    RunSummary,
    SourceHealth,
    WorkflowStatus,
)
from app.services.description import rich_description

EVENT_STATUS = {
    ApplicationEventType.SAVED: WorkflowStatus.SAVED,
    ApplicationEventType.DISMISSED: WorkflowStatus.DISMISSED,
    ApplicationEventType.APPLIED_MANUAL: WorkflowStatus.APPLIED,
    ApplicationEventType.INTERVIEW_HR: WorkflowStatus.INTERVIEW_HR,
    ApplicationEventType.CODE_TEST: WorkflowStatus.CODE_TEST,
    ApplicationEventType.INTERVIEW_TECHNICAL: WorkflowStatus.INTERVIEW_TECHNICAL,
    ApplicationEventType.OFFER: WorkflowStatus.OFFER,
    ApplicationEventType.REJECTED: WorkflowStatus.REJECTED,
    ApplicationEventType.WITHDRAWN: WorkflowStatus.WITHDRAWN,
    ApplicationEventType.CLOSED_WITHOUT_APPLICATION: WorkflowStatus.CLOSED,
}


@dataclass(frozen=True)
class ExistingJob:
    job_id: int
    source_id: int | None
    payload_hash: str | None
    last_verified_at: datetime | None


class Repository:
    def __init__(self, path: Path):
        self.path = path

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
        with self.connect() as connection:
            connection.executescript(schema)

    def upsert_job(
        self, job: NormalizedJob, payload_hash: str | None = None
    ) -> tuple[int, str]:
        now = datetime.now(UTC).isoformat()
        with self.connect() as connection:
            existing = self._find_existing(connection, job)
            if existing:
                job_id = int(existing["id"])
                connection.execute(
                    """
                    UPDATE jobs SET apply_url = ?, canonical_url = ?, title = ?,
                      normalized_title = ?,
                      company = ?, normalized_company = ?, description = ?, location_text = ?,
                      remote_scope = ?, geo_json = ?, employment_type = ?, salary_min = ?,
                      salary_max = ?, salary_currency = ?, salary_period = ?, date_posted = ?,
                      valid_through = ?, eligibility = ?, eligibility_reason = ?, geo_evidence = ?,
                      relevant_technologies = ?, last_seen_at = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    self._job_update_values(job, now, job_id),
                )
                outcome = "updated"
            else:
                cursor = connection.execute(
                    """
                    INSERT INTO jobs (
                      canonical_url, apply_url, ats, ats_board, ats_job_id, title, normalized_title,
                      company, normalized_company, description, location_text, remote_scope,
                      geo_json,
                      employment_type, salary_min, salary_max, salary_currency, salary_period,
                      date_posted, valid_through, eligibility, eligibility_reason, geo_evidence,
                      relevant_technologies, first_seen_at, last_seen_at, created_at, updated_at
                    ) VALUES (
                      ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                      ?, ?, ?, ?
                    )
                    """,
                    self._job_insert_values(job, now),
                )
                job_id = int(cursor.lastrowid)
                outcome = "inserted"
            self._upsert_source(connection, job_id, job, now, payload_hash)
            return job_id, outcome

    def find_existing_job(
        self,
        *,
        ats: str | None,
        ats_board: str | None,
        ats_job_id: str | None,
        source: str,
        source_job_id: str | None,
        source_url: str,
        canonical_url: str,
        apply_url: str,
    ) -> ExistingJob | None:
        with self.connect() as connection:
            row = None
            if ats and ats_board and ats_job_id:
                row = connection.execute(
                    "SELECT * FROM jobs WHERE ats = ? AND ats_board = ? AND ats_job_id = ?",
                    (ats, ats_board, ats_job_id),
                ).fetchone()
            if row is None and source_job_id:
                row = connection.execute(
                    """
                    SELECT jobs.* FROM jobs
                    JOIN job_sources ON jobs.id = job_sources.job_id
                    WHERE job_sources.source = ? AND job_sources.source_job_id = ?
                    """,
                    (source, source_job_id),
                ).fetchone()
            if row is None:
                row = connection.execute(
                    "SELECT * FROM jobs WHERE canonical_url = ? OR apply_url = ? LIMIT 1",
                    (canonical_url, apply_url),
                ).fetchone()
            if row is None:
                return None

            if source_job_id:
                source_row = connection.execute(
                    """
                    SELECT id, payload_hash FROM job_sources
                    WHERE job_id = ? AND source = ? AND source_job_id = ?
                    """,
                    (row["id"], source, source_job_id),
                ).fetchone()
            else:
                source_row = connection.execute(
                    """
                    SELECT id, payload_hash FROM job_sources
                    WHERE job_id = ? AND source = ? AND source_url = ?
                    """,
                    (row["id"], source, source_url),
                ).fetchone()

            return ExistingJob(
                job_id=int(row["id"]),
                source_id=int(source_row["id"]) if source_row else None,
                payload_hash=source_row["payload_hash"] if source_row else None,
                last_verified_at=(
                    datetime.fromisoformat(row["last_verified_at"])
                    if row["last_verified_at"]
                    else None
                ),
            )

    def touch_existing_job(
        self,
        existing: ExistingJob,
        raw_payload: dict[str, object] | None,
        payload_hash: str,
    ) -> None:
        if existing.source_id is None:
            return
        now = datetime.now(UTC).isoformat()
        raw = (
            json.dumps(raw_payload, ensure_ascii=False, sort_keys=True)
            if raw_payload
            else None
        )
        with self.connect() as connection:
            connection.execute(
                "UPDATE jobs SET last_seen_at = ? WHERE id = ?",
                (now, existing.job_id),
            )
            connection.execute(
                """
                UPDATE job_sources SET last_seen_at = ?, raw_payload = ?, payload_hash = ?
                WHERE id = ?
                """,
                (now, raw, payload_hash, existing.source_id),
            )

    def delete_job(self, job_id: int) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM jobs WHERE id = ?", (job_id,))

    def _find_existing(
        self, connection: sqlite3.Connection, job: NormalizedJob
    ) -> sqlite3.Row | None:
        if job.ats and job.ats_board and job.ats_job_id:
            row = connection.execute(
                "SELECT id FROM jobs WHERE ats = ? AND ats_board = ? AND ats_job_id = ?",
                (job.ats, job.ats_board, job.ats_job_id),
            ).fetchone()
            if row:
                return row
        if job.source_job_id:
            row = connection.execute(
                """
                SELECT jobs.id FROM jobs JOIN job_sources ON jobs.id = job_sources.job_id
                WHERE job_sources.source = ? AND job_sources.source_job_id = ?
                """,
                (job.source, job.source_job_id),
            ).fetchone()
            if row:
                return row
        return connection.execute(
            "SELECT id FROM jobs WHERE canonical_url = ? OR apply_url = ? LIMIT 1",
            (job.canonical_url, job.apply_url),
        ).fetchone()

    @staticmethod
    def _job_insert_values(job: NormalizedJob, now: str) -> tuple[object, ...]:
        return (
            job.canonical_url,
            job.apply_url,
            job.ats,
            job.ats_board,
            job.ats_job_id,
            job.title,
            job.normalized_title,
            job.company,
            job.normalized_company,
            job.description,
            job.location_text,
            job.remote_scope,
            json.dumps(job.geo_json, ensure_ascii=False),
            job.employment_type,
            job.salary_min,
            job.salary_max,
            job.salary_currency,
            job.salary_period,
            job.date_posted.isoformat() if job.date_posted else None,
            job.valid_through.isoformat() if job.valid_through else None,
            job.eligibility.value,
            job.eligibility_reason,
            job.geo_evidence,
            json.dumps(job.relevant_technologies, ensure_ascii=False),
            now,
            now,
            now,
            now,
        )

    @staticmethod
    def _job_update_values(job: NormalizedJob, now: str, job_id: int) -> tuple[object, ...]:
        return (
            job.apply_url,
            job.canonical_url,
            job.title,
            job.normalized_title,
            job.company,
            job.normalized_company,
            job.description,
            job.location_text,
            job.remote_scope,
            json.dumps(job.geo_json, ensure_ascii=False),
            job.employment_type,
            job.salary_min,
            job.salary_max,
            job.salary_currency,
            job.salary_period,
            job.date_posted.isoformat() if job.date_posted else None,
            job.valid_through.isoformat() if job.valid_through else None,
            job.eligibility.value,
            job.eligibility_reason,
            job.geo_evidence,
            json.dumps(job.relevant_technologies, ensure_ascii=False),
            now,
            now,
            job_id,
        )

    @staticmethod
    def _upsert_source(
        connection: sqlite3.Connection,
        job_id: int,
        job: NormalizedJob,
        now: str,
        content_hash: str | None,
    ) -> None:
        raw = (
            json.dumps(job.raw_payload, ensure_ascii=False, sort_keys=True)
            if job.raw_payload
            else None
        )
        payload_hash = content_hash or (hashlib.sha256(raw.encode()).hexdigest() if raw else None)
        if job.source_job_id:
            connection.execute(
                """
                INSERT INTO job_sources (
                  job_id, source, source_job_id, source_url, first_seen_at, last_seen_at,
                  raw_payload, payload_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source, source_job_id) DO UPDATE SET
                  job_id = excluded.job_id, source_url = excluded.source_url,
                  last_seen_at = excluded.last_seen_at, raw_payload = excluded.raw_payload,
                  payload_hash = excluded.payload_hash
                """,
                (
                    job_id,
                    job.source,
                    job.source_job_id,
                    job.source_url,
                    now,
                    now,
                    raw,
                    payload_hash,
                ),
            )
            return
        existing = connection.execute(
            "SELECT id FROM job_sources WHERE job_id = ? AND source = ? AND source_url = ?",
            (job_id, job.source, job.source_url),
        ).fetchone()
        if existing:
            connection.execute(
                """
                UPDATE job_sources SET last_seen_at = ?, raw_payload = ?, payload_hash = ?
                WHERE id = ?
                """,
                (now, raw, payload_hash, existing["id"]),
            )
        else:
            connection.execute(
                """
                INSERT INTO job_sources (
                  job_id, source, source_job_id, source_url, first_seen_at, last_seen_at,
                  raw_payload, payload_hash
                ) VALUES (?, ?, NULL, ?, ?, ?, ?, ?)
                """,
                (job_id, job.source, job.source_url, now, now, raw, payload_hash),
            )

    def list_jobs(self, tab: str, query: str, limit: int, offset: int) -> JobListResponse:
        where, parameters = self._tab_filter(tab)
        if query:
            where += " AND (title LIKE ? OR company LIKE ? OR description LIKE ?)"
            term = f"%{query}%"
            parameters.extend([term, term, term])
        order = """
          ORDER BY CASE eligibility WHEN 'compatible' THEN 0 WHEN 'uncertain' THEN 1 ELSE 2 END,
          CASE salary_currency
            WHEN 'USD' THEN 0 WHEN 'EUR' THEN 1 WHEN 'GBP' THEN 2 WHEN 'CAD' THEN 3
            WHEN 'CHF' THEN 4 WHEN 'AUD' THEN 5 WHEN 'NZD' THEN 6 ELSE 7
          END,
          COALESCE(date_posted, first_seen_at) DESC
        """
        with self.connect() as connection:
            total = int(
                connection.execute(
                    f"SELECT COUNT(*) FROM jobs WHERE {where}", parameters
                ).fetchone()[0]
            )
            rows = connection.execute(
                f"SELECT * FROM jobs WHERE {where} {order} LIMIT ? OFFSET ?",
                [*parameters, limit, offset],
            ).fetchall()
            counts = {
                row["workflow_status"]: int(row["amount"])
                for row in connection.execute(
                    "SELECT workflow_status, COUNT(*) amount FROM jobs GROUP BY workflow_status"
                ).fetchall()
            }
            for row in connection.execute(
                "SELECT eligibility, COUNT(*) amount FROM jobs GROUP BY eligibility"
            ).fetchall():
                counts[row["eligibility"]] = int(row["amount"])
            aggregate = connection.execute(
                """
                SELECT
                  SUM(CASE WHEN eligibility = 'compatible' AND workflow_status = 'new'
                    THEN 1 ELSE 0 END) new_compatible,
                  SUM(CASE WHEN eligibility = 'uncertain' AND workflow_status = 'new'
                    THEN 1 ELSE 0 END) new_uncertain,
                  SUM(CASE WHEN workflow_status IN (
                    'interview_hr', 'code_test', 'interview_technical', 'offer'
                  ) THEN 1 ELSE 0 END) in_process,
                  SUM(CASE WHEN workflow_status IN ('closed', 'rejected', 'withdrawn')
                    THEN 1 ELSE 0 END) closed_total,
                  COUNT(*) all_jobs
                FROM jobs
                """
            ).fetchone()
            aggregate_fields = (
                "new_compatible",
                "new_uncertain",
                "in_process",
                "closed_total",
                "all_jobs",
            )
            counts.update({key: int(aggregate[key] or 0) for key in aggregate_fields})
            return JobListResponse(
                items=[self._to_job(connection, row) for row in rows], total=total, counts=counts
            )

    @staticmethod
    def _tab_filter(tab: str) -> tuple[str, list[object]]:
        filters = {
            "new": ("eligibility = 'compatible' AND workflow_status = 'new'", []),
            "uncertain": ("eligibility = 'uncertain' AND workflow_status = 'new'", []),
            "saved": ("workflow_status = 'saved'", []),
            "applied": ("workflow_status = 'applied'", []),
            "in_process": (
                "workflow_status IN ('interview_hr','code_test','interview_technical','offer')",
                [],
            ),
            "closed": ("workflow_status IN ('closed','rejected','withdrawn')", []),
            "dismissed": ("workflow_status = 'dismissed'", []),
            "all": ("1 = 1", []),
        }
        return filters.get(tab, filters["new"])

    def get_job(self, job_id: int) -> JobRead | None:
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            return self._to_job(connection, row) if row else None

    def _to_job(self, connection: sqlite3.Connection, row: sqlite3.Row) -> JobRead:
        sources = connection.execute(
            "SELECT * FROM job_sources WHERE job_id = ? ORDER BY first_seen_at", (row["id"],)
        ).fetchall()
        description_html = rich_description(
            [(source["source"], source["raw_payload"]) for source in sources]
        )
        return JobRead(
            id=row["id"],
            canonical_url=row["canonical_url"],
            apply_url=row["apply_url"],
            ats=row["ats"],
            ats_board=row["ats_board"],
            ats_job_id=row["ats_job_id"],
            title=row["title"],
            company=row["company"],
            description=row["description"],
            description_html=description_html,
            location_text=row["location_text"],
            remote_scope=row["remote_scope"],
            geo_json=json.loads(row["geo_json"]),
            employment_type=row["employment_type"],
            salary_min=row["salary_min"],
            salary_max=row["salary_max"],
            salary_currency=row["salary_currency"],
            salary_period=row["salary_period"],
            date_posted=row["date_posted"],
            valid_through=row["valid_through"],
            eligibility=row["eligibility"],
            eligibility_reason=row["eligibility_reason"],
            geo_evidence=row["geo_evidence"],
            workflow_status=row["workflow_status"],
            relevant_technologies=json.loads(row["relevant_technologies"]),
            first_seen_at=row["first_seen_at"],
            last_seen_at=row["last_seen_at"],
            last_verified_at=row["last_verified_at"],
            closed_at=row["closed_at"],
            sources=[JobSourceRead.model_validate(dict(source)) for source in sources],
        )

    def add_event(self, job_id: int, event: EventCreate) -> ApplicationEventRead:
        status = EVENT_STATUS[event.event]
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO application_events (job_id, event, occurred_at, notes)
                VALUES (?, ?, ?, ?)
                """,
                (job_id, event.event.value, event.occurred_at.isoformat(), event.notes),
            )
            connection.execute(
                "UPDATE jobs SET workflow_status = ?, updated_at = ? WHERE id = ?",
                (status.value, datetime.now(UTC).isoformat(), job_id),
            )
            return ApplicationEventRead(id=cursor.lastrowid, job_id=job_id, **event.model_dump())

    def list_events(self, job_id: int) -> list[ApplicationEventRead]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM application_events WHERE job_id = ? ORDER BY occurred_at DESC",
                (job_id,),
            ).fetchall()
            return [ApplicationEventRead.model_validate(dict(row)) for row in rows]

    def correct_eligibility(self, job_id: int, feedback: EligibilityFeedback) -> None:
        now = datetime.now(UTC).isoformat()
        with self.connect() as connection:
            current = connection.execute(
                "SELECT eligibility FROM jobs WHERE id = ?", (job_id,)
            ).fetchone()
            if not current:
                raise KeyError(job_id)
            connection.execute(
                """
                INSERT INTO eligibility_feedback (
                  job_id, previous_eligibility, corrected_eligibility, reason, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (job_id, current["eligibility"], feedback.eligibility.value, feedback.reason, now),
            )
            connection.execute(
                """
                UPDATE jobs SET eligibility = ?, eligibility_reason = ?, updated_at = ?
                WHERE id = ?
                """,
                (feedback.eligibility.value, feedback.reason, now, job_id),
            )

    def start_run(self, source: str) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO source_runs (source, started_at, status) VALUES (?, ?, 'running')",
                (source, datetime.now(UTC).isoformat()),
            )
            return int(cursor.lastrowid)

    def finish_run(self, run_id: int, summary: RunSummary) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                UPDATE source_runs SET finished_at = ?, status = ?, fetched = ?, inserted = ?,
                  updated = ?, duplicates = ?, errors = ?, error_message = ? WHERE id = ?
                """,
                (
                    datetime.now(UTC).isoformat(),
                    summary.status,
                    summary.fetched,
                    summary.inserted,
                    summary.updated,
                    summary.duplicates,
                    summary.errors,
                    summary.error_message,
                    run_id,
                ),
            )

    def source_health(self) -> list[SourceHealth]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT sr.* FROM source_runs sr
                JOIN (SELECT source, MAX(id) id FROM source_runs GROUP BY source) latest
                  ON sr.id = latest.id ORDER BY sr.source
                """
            ).fetchall()
            return [SourceHealth.model_validate(dict(row)) for row in rows]

    def last_success(self, source: str) -> datetime | None:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT finished_at FROM source_runs
                WHERE source = ? AND status IN ('success','partial')
                ORDER BY id DESC LIMIT 1
                """,
                (source,),
            ).fetchone()
            return (
                datetime.fromisoformat(row["finished_at"]) if row and row["finished_at"] else None
            )

    def mark_verified(self, job_id: int, is_open: bool) -> None:
        now = datetime.now(UTC).isoformat()
        with self.connect() as connection:
            connection.execute(
                """
                UPDATE jobs SET last_verified_at = ?, closed_at = ?,
                  workflow_status = CASE WHEN ? THEN workflow_status ELSE 'closed' END
                WHERE id = ?
                """,
                (now, None if is_open else now, is_open, job_id),
            )

    def list_platforms(self) -> list[PlatformRead]:
        from app.platforms import platform_catalog

        with self.connect() as connection:
            rows = connection.execute("SELECT * FROM platform_tracking").fetchall()
        tracking = {row["platform_id"]: row for row in rows}
        platforms = []
        for definition in platform_catalog():
            saved = tracking.get(definition.id)
            default_status = (
                PlatformTrackingStatus.DONE
                if definition.availability == PlatformAvailability.ACTIVE
                else PlatformTrackingStatus.PENDING
            )
            platforms.append(
                PlatformRead(
                    id=definition.id,
                    name=definition.name,
                    url=definition.url,
                    category=definition.category,
                    availability=definition.availability,
                    description=definition.description,
                    tracking_status=(
                        PlatformTrackingStatus(saved["tracking_status"])
                        if saved
                        else default_status
                    ),
                    last_reviewed_at=(
                        datetime.fromisoformat(saved["last_reviewed_at"])
                        if saved and saved["last_reviewed_at"]
                        else None
                    ),
                    notes=saved["notes"] if saved else "",
                )
            )
        return platforms

    def update_platform(self, platform_id: str, update: PlatformUpdate) -> PlatformRead:
        from app.platforms import platform_catalog

        definitions = {platform.id: platform for platform in platform_catalog()}
        if platform_id not in definitions:
            raise KeyError(platform_id)
        now = datetime.now(UTC).isoformat()
        with self.connect() as connection:
            existing = connection.execute(
                "SELECT last_reviewed_at FROM platform_tracking WHERE platform_id = ?",
                (platform_id,),
            ).fetchone()
            last_reviewed_at = (
                now
                if update.tracking_status == PlatformTrackingStatus.DONE
                else existing["last_reviewed_at"]
                if existing
                else None
            )
            connection.execute(
                """
                INSERT INTO platform_tracking (
                  platform_id, tracking_status, last_reviewed_at, notes, updated_at
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(platform_id) DO UPDATE SET
                  tracking_status = excluded.tracking_status,
                  last_reviewed_at = excluded.last_reviewed_at,
                  notes = excluded.notes,
                  updated_at = excluded.updated_at
                """,
                (
                    platform_id,
                    update.tracking_status.value,
                    last_reviewed_at,
                    update.notes,
                    now,
                ),
            )
        return next(platform for platform in self.list_platforms() if platform.id == platform_id)
