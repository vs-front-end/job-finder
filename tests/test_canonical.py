from app.pipeline.canonical import canonicalize_url, normalize_identity


def test_canonical_url_keeps_path_case_and_removes_tracking() -> None:
    value = "HTTPS://Example.COM/Jobs/ABC?utm_source=x&Role=Dev#apply"

    assert canonicalize_url(value) == "https://example.com/Jobs/ABC?Role=Dev"


def test_canonical_url_only_removes_source_on_known_ats() -> None:
    ats = canonicalize_url("https://jobs.lever.co/acme/ABC?source=site&team=core")
    regular = canonicalize_url("https://example.com/job?source=board")

    assert ats == "https://jobs.lever.co/acme/ABC?team=core"
    assert regular == "https://example.com/job?source=board"


def test_normalize_identity_removes_accents_and_punctuation() -> None:
    assert normalize_identity("Engenheiro de Sóftware — Sênior") == "engenheiro de software senior"
