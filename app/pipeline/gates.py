from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.config import AppConfig, ObjectiveConfig
from app.models import Eligibility, GateResult, RawJob

GLOBAL_PATTERNS = (
    r"\bworldwide\b",
    r"\banywhere\b",
    r"\bglobal\b",
    r"\bremote(?:ly)? (?:from )?anywhere\b",
)
COUNTRY_NAMES: dict[str, tuple[str, ...]] = {
    "AR": ("argentina",),
    "AU": ("australia",),
    "BR": ("brazil", "brasil"),
    "CA": ("canada",),
    "CL": ("chile",),
    "CO": ("colombia",),
    "CZ": ("czech republic", "czechia"),
    "DE": ("germany",),
    "DK": ("denmark",),
    "ES": ("spain",),
    "FI": ("finland",),
    "FR": ("france",),
    "GB": ("united kingdom", "uk", "britain"),
    "GR": ("greece",),
    "IE": ("ireland",),
    "IN": ("india",),
    "IT": ("italy",),
    "MX": ("mexico", "méxico"),
    "NG": ("nigeria",),
    "NL": ("netherlands", "holland"),
    "NO": ("norway",),
    "NZ": ("new zealand",),
    "PE": ("peru",),
    "PH": ("philippines",),
    "PL": ("poland",),
    "PT": ("portugal",),
    "RO": ("romania",),
    "SE": ("sweden",),
    "TR": ("turkey", "türkiye"),
    "UA": ("ukraine",),
    "US": ("united states", "usa"),
    "UY": ("uruguay",),
    "ZA": ("south africa",),
}
REGION_TERMS: dict[str, tuple[str, ...]] = {
    "latam": ("latam", "latin america", "south america"),
    "americas": ("americas",),
    "north-america": ("north america",),
    "europe": ("europe", "emea"),
    "asia": ("apac", "asia"),
    "africa": ("africa", "emea"),
    "oceania": ("oceania", "apac"),
}
COUNTRY_REGIONS: dict[str, tuple[str, ...]] = {
    "AR": ("latam", "americas"),
    "AU": ("oceania",),
    "BR": ("latam", "americas"),
    "CA": ("north-america", "americas"),
    "CL": ("latam", "americas"),
    "CO": ("latam", "americas"),
    "CZ": ("europe",),
    "DE": ("europe",),
    "DK": ("europe",),
    "ES": ("europe",),
    "FI": ("europe",),
    "FR": ("europe",),
    "GB": ("europe",),
    "GR": ("europe",),
    "IE": ("europe",),
    "IN": ("asia",),
    "IT": ("europe",),
    "MX": ("latam", "north-america", "americas"),
    "NG": ("africa",),
    "NL": ("europe",),
    "NO": ("europe",),
    "NZ": ("oceania",),
    "PE": ("latam", "americas"),
    "PH": ("asia",),
    "PL": ("europe",),
    "PT": ("europe",),
    "RO": ("europe",),
    "SE": ("europe",),
    "TR": ("europe", "asia"),
    "UA": ("europe",),
    "US": ("north-america", "americas"),
    "UY": ("latam", "americas"),
    "ZA": ("africa",),
}
EU_MEMBERS = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE",
    "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE",
}
RESTRICTED_SCOPE_PATTERNS: tuple[tuple[str, str], ...] = (
    ("US", r"\bus only\b"),
    ("US", r"\bu\.?s\.?[- ]based\b"),
    ("US", r"\bmust (?:be|reside|live) in (?:the )?(?:u\.?s\.?|united states)\b"),
    ("US", r"\bremote within (?:the )?u\.?s\.?\b"),
    ("US", r"\bauthori[sz]ed to work in (?:the )?u\.?s\.?(?: without sponsorship)?\b"),
    ("CA", r"\bcanada only\b"),
    ("GB", r"\buk only\b"),
    ("EU", r"\beu only\b"),
    ("EU", r"\beea only\b"),
)
NON_REMOTE_WORKPLACE_PATTERNS = (
    r"\bhybrid\b",
    r"\bon[- ]?site\b",
    r"\bin[- ]office\b",
    r"\boffice[- ]based\b",
)
NON_REMOTE_DESCRIPTION_PATTERNS = (
    r"\bremote\s*(?:or|/)\s*hybrid\b",
    r"\bhybrid\s+(?:role|position|work|working|schedule|arrangement|model|workplace)\b",
    r"\b(?:role|position|work|working|schedule|arrangement|model|workplace)\s+(?:is\s+)?hybrid\b",
    r"\b\d+\s+days?\s+(?:per\s+week\s+)?(?:in|at)\s+(?:the\s+)?office\b",
)
REMOTE_EVIDENCE_PATTERNS = (
    r"\bremote\b",
    r"\bworldwide\b",
    r"\banywhere\b",
)
LANGUAGE_PATTERNS = {
    "en": (
        r"\bwe are\b",
        r"\byou will\b",
        r"\bexperience\b",
        r"\brequirements\b",
        r"\bresponsibilities\b",
        r"\bskills\b",
        r"\babout the role\b",
    ),
    "pt": (
        r"\bvocê\b",
        r"\bexperiência\b",
        r"\brequisitos\b",
        r"\bresponsabilidades\b",
        r"\bconhecimentos\b",
        r"\bdesenvolvedor(?:a)?\b",
        r"\bsobre a vaga\b",
    ),
    "es": (
        r"\bbuscamos\b",
        r"\bexperiencia\b",
        r"\brequisitos\b",
        r"\bresponsabilidades\b",
        r"\bconocimientos\b",
        r"\bdesarrollador(?:a)?\b",
        r"\bsobre el puesto\b",
        r"\bpostular\b",
    ),
    "de": (
        r"\bwir suchen\b",
        r"\berfahrung\b",
        r"\bkenntnisse\b",
        r"\baufgaben\b",
        r"\banforderungen\b",
        r"\bdeutsch\b",
    ),
    "fr": (
        r"\bnous recherchons\b",
        r"\bexpérience\b",
        r"\bcompétences\b",
        r"\bmissions\b",
        r"\bprofil recherché\b",
        r"\bfrançais\b",
    ),
}


@dataclass(frozen=True)
class TechnicalResult:
    accepted: bool
    reason: str
    technologies: list[str]


@dataclass(frozen=True)
class RemoteResult:
    accepted: bool
    reason: str


def remote_gate(job: RawJob) -> RemoteResult:
    workplace = f"{job.title}\n{job.location_text}\n{job.remote_scope or ''}"
    if _first_match(NON_REMOTE_WORKPLACE_PATTERNS, workplace):
        return RemoteResult(False, "Hybrid or on-site workplace")
    if _first_match(NON_REMOTE_DESCRIPTION_PATTERNS, job.description):
        return RemoteResult(False, "Description requires hybrid or on-site work")
    if job.ats:
        is_remote = bool(re.search(r"\bremote\b", job.remote_scope or "", re.I))
        return RemoteResult(
            is_remote, "ATS confirmed remote" if is_remote else "ATS without remote scope"
        )
    if job.remote_scope or _first_match(REMOTE_EVIDENCE_PATTERNS, workplace):
        return RemoteResult(True, "Remote workplace confirmed")
    return RemoteResult(False, "No evidence of remote workplace")


def technical_gate(job: RawJob, config: AppConfig) -> TechnicalResult:
    filters = config.filtros
    searchable = f"{job.title}\n{job.description}"
    if filters.titulos_rejeitados and any(
        re.search(pattern, job.title, re.I) for pattern in filters.titulos_rejeitados
    ):
        return TechnicalResult(False, "Title is on the exclusion list", [])
    if filters.titulos_aceitos and not any(
        re.search(pattern, job.title, re.I) for pattern in filters.titulos_aceitos
    ):
        return TechnicalResult(False, "Title does not match the configured profile", [])
    if filters.palavras_rejeitadas and any(
        re.search(pattern, searchable, re.I) for pattern in filters.palavras_rejeitadas
    ):
        return TechnicalResult(False, "Description contains an excluded keyword", [])
    unsupported_language = _unsupported_language(searchable, filters.idiomas_aceitos)
    if unsupported_language:
        return TechnicalResult(
            False,
            f"Detected language outside the profile: {unsupported_language}",
            [],
        )
    if job.salary_currency and job.salary_currency.upper() in {
        currency.upper() for currency in filters.moedas_rejeitadas
    }:
        return TechnicalResult(False, "Currency explicitly rejected by the profile", [])
    if job.date_posted and job.date_posted < datetime.now(UTC) - timedelta(
        days=filters.idade_maxima_dias
    ):
        return TechnicalResult(False, "Job is older than the configured limit", [])
    technologies = [
        technology
        for technology in filters.tecnologias
        if re.search(rf"\b{re.escape(technology)}\b", searchable, re.I)
    ]
    if filters.exigir_tecnologia_compativel and not technologies:
        return TechnicalResult(False, "No profile technology found in the description", [])
    return TechnicalResult(True, "Technical profile matches", technologies)


def geographic_gate(job: RawJob, objective: ObjectiveConfig | None = None) -> GateResult:
    objective = objective or ObjectiveConfig()
    country = objective.pais_residencia.upper()
    evidence_source = f"{job.location_text}\n{job.description}"
    for scope, pattern in RESTRICTED_SCOPE_PATTERNS:
        evidence = _match_excerpt(pattern, evidence_source)
        if not evidence:
            continue
        if _scope_includes(scope, country):
            return _compatible(job, f"Restriction matches your region: {evidence}", evidence)
        return GateResult(
            decision=Eligibility.INCOMPATIBLE,
            role_match=True,
            geo_match="no",
            reason=f"Incompatible geographic restriction: {evidence}",
            geo_evidence=evidence,
            employment_type=_employment(job.employment_type),
            payment_currency=job.salary_currency or "unknown",
        )
    normalized_countries = {item.upper() for item in job.allowed_countries}
    if normalized_countries:
        country_aliases = {country} | {
            name.upper() for name in COUNTRY_NAMES.get(country, ())
        }
        if normalized_countries & country_aliases:
            evidence = ", ".join(job.allowed_countries)
            return _compatible(job, f"Country explicitly accepted: {evidence}", evidence)
        return GateResult(
            decision=Eligibility.INCOMPATIBLE,
            role_match=True,
            geo_match="no",
            reason=f"Allowed country list does not include {country}",
            geo_evidence=", ".join(job.allowed_countries),
            employment_type=_employment(job.employment_type),
            payment_currency=job.salary_currency or "unknown",
        )
    positive = _first_match(_positive_patterns(country), evidence_source)
    if positive:
        return _compatible(job, f"Compatible region found: {positive}", positive)
    timezone = _compatible_timezone(job.timezone_requirements, objective.fusos_aceitos)
    if timezone:
        return _compatible(job, f"Accepted timezone range: {timezone}", timezone)
    return GateResult(
        decision=Eligibility.UNCERTAIN,
        role_match=True,
        geo_match="unknown",
        reason=f"Remote job without confirmation that it accepts candidates in {country}",
        geo_evidence=None,
        employment_type=_employment(job.employment_type),
        payment_currency=job.salary_currency or "unknown",
    )


def _positive_patterns(country: str) -> tuple[str, ...]:
    patterns = list(GLOBAL_PATTERNS)
    for name in COUNTRY_NAMES.get(country, ()):
        patterns.append(rf"\b{re.escape(name)}\b")
    for region in COUNTRY_REGIONS.get(country, ()):
        for term in REGION_TERMS.get(region, ()):
            patterns.append(rf"\b{re.escape(term)}\b")
    return tuple(patterns)


def _scope_includes(scope: str, country: str) -> bool:
    if scope == country:
        return True
    return scope == "EU" and country in EU_MEMBERS


def _match_excerpt(pattern: str, value: str) -> str | None:
    match = re.search(pattern, value, re.I)
    if not match:
        return None
    start = max(0, match.start() - 50)
    end = min(len(value), match.end() + 70)
    return " ".join(value[start:end].split())


def _first_match(patterns: tuple[str, ...], value: str) -> str | None:
    for pattern in patterns:
        excerpt = _match_excerpt(pattern, value)
        if excerpt:
            return excerpt
    return None


def _compatible(job: RawJob, reason: str, evidence: str) -> GateResult:
    return GateResult(
        decision=Eligibility.COMPATIBLE,
        role_match=True,
        geo_match="yes",
        reason=reason,
        geo_evidence=evidence,
        employment_type=_employment(job.employment_type),
        payment_currency=job.salary_currency or "unknown",
    )


def _accepted_offsets(accepted_timezones: list[str]) -> set[int]:
    offsets: set[int] = set()
    for value in accepted_timezones:
        match = re.search(r"([+-]?\d{1,2})", value)
        if match:
            offsets.add(int(match.group(1)))
    return offsets


def _compatible_timezone(values: list[str], accepted_timezones: list[str]) -> str | None:
    offsets = _accepted_offsets(accepted_timezones)
    if not offsets:
        return None
    for value in values:
        matches = [int(item) for item in re.findall(r"(?<!\d)([+-]?\d{1,2})(?!\d)", value)]
        if any(offset in offsets for offset in matches):
            return value
        if len(matches) >= 2 and any(
            min(matches) <= offset <= max(matches) for offset in offsets
        ):
            return value
    return None


def _employment(value: str | None) -> str:
    if not value:
        return "unknown"
    lowered = value.lower()
    if "contract" in lowered:
        return "contractor"
    if "eor" in lowered or "employer of record" in lowered:
        return "eor"
    if "full" in lowered or "employee" in lowered or "permanent" in lowered:
        return "employee"
    return "unknown"


def _unsupported_language(value: str, accepted: list[str]) -> str | None:
    accepted_codes = {language.lower() for language in accepted}
    scores = {
        language: sum(bool(re.search(pattern, value, re.I)) for pattern in patterns)
        for language, patterns in LANGUAGE_PATTERNS.items()
    }
    accepted_score = max((scores.get(language, 0) for language in accepted_codes), default=0)
    unsupported = [
        (language, score) for language, score in scores.items() if language not in accepted_codes
    ]
    language, score = max(unsupported, key=lambda item: item[1], default=("", 0))
    if score >= 4 and score >= accepted_score + 2:
        return language
    return None
