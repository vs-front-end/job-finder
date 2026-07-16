PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  canonical_url TEXT NOT NULL UNIQUE,
  apply_url TEXT NOT NULL,
  ats TEXT,
  ats_board TEXT,
  ats_job_id TEXT,
  title TEXT NOT NULL,
  normalized_title TEXT NOT NULL,
  company TEXT NOT NULL,
  normalized_company TEXT NOT NULL,
  description TEXT NOT NULL,
  location_text TEXT NOT NULL,
  remote_scope TEXT,
  geo_json TEXT NOT NULL DEFAULT '{}',
  employment_type TEXT,
  salary_min REAL,
  salary_max REAL,
  salary_currency TEXT,
  salary_period TEXT,
  date_posted TEXT,
  valid_through TEXT,
  eligibility TEXT NOT NULL,
  eligibility_reason TEXT NOT NULL,
  geo_evidence TEXT,
  workflow_status TEXT NOT NULL DEFAULT 'new',
  relevant_technologies TEXT NOT NULL DEFAULT '[]',
  first_seen_at TEXT NOT NULL,
  last_seen_at TEXT NOT NULL,
  last_verified_at TEXT,
  closed_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE (ats, ats_board, ats_job_id)
);

CREATE INDEX IF NOT EXISTS idx_jobs_eligibility ON jobs(eligibility);
CREATE INDEX IF NOT EXISTS idx_jobs_workflow ON jobs(workflow_status);
CREATE INDEX IF NOT EXISTS idx_jobs_date ON jobs(date_posted DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_normalized ON jobs(normalized_company, normalized_title);

CREATE TABLE IF NOT EXISTS job_sources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  source TEXT NOT NULL,
  source_job_id TEXT,
  source_url TEXT NOT NULL,
  first_seen_at TEXT NOT NULL,
  last_seen_at TEXT NOT NULL,
  raw_payload TEXT,
  payload_hash TEXT,
  UNIQUE (source, source_job_id)
);

CREATE INDEX IF NOT EXISTS idx_job_sources_job ON job_sources(job_id);

CREATE TABLE IF NOT EXISTS source_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  status TEXT NOT NULL,
  fetched INTEGER NOT NULL DEFAULT 0,
  inserted INTEGER NOT NULL DEFAULT 0,
  updated INTEGER NOT NULL DEFAULT 0,
  duplicates INTEGER NOT NULL DEFAULT 0,
  errors INTEGER NOT NULL DEFAULT 0,
  error_message TEXT,
  checkpoint TEXT
);

CREATE INDEX IF NOT EXISTS idx_source_runs_source ON source_runs(source, started_at DESC);

CREATE TABLE IF NOT EXISTS application_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  event TEXT NOT NULL,
  occurred_at TEXT NOT NULL,
  notes TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_events_job ON application_events(job_id, occurred_at DESC);

CREATE TABLE IF NOT EXISTS eligibility_feedback (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  previous_eligibility TEXT NOT NULL,
  corrected_eligibility TEXT NOT NULL,
  reason TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS platform_tracking (
  platform_id TEXT PRIMARY KEY,
  tracking_status TEXT NOT NULL,
  last_reviewed_at TEXT,
  notes TEXT NOT NULL DEFAULT '',
  updated_at TEXT NOT NULL
);
