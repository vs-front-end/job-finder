from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.config import AppConfig
from app.models import Eligibility, GateResult, RawJob

POSITIVE_PATTERNS = (
    r"\bbrazil\b",
    r"\bbrasil\b",
    r"\blatam\b",
    r"\blatin america\b",
    r"\bsouth america\b",
    r"\bworldwide\b",
    r"\banywhere\b",
    r"\bglobal\b",
    r"\bremote(?:ly)? (?:from )?anywhere\b",
    r"\bamericas\b",
)
NEGATIVE_PATTERNS = (
    r"\bus only\b",
    r"\bu\.?s\.?[- ]based\b",
    r"\bmust (?:be|reside|live) in (?:the )?(?:u\.?s\.?|united states)\b",
    r"\bcanada only\b",
    r"\buk only\b",
    r"\beu only\b",
    r"\beea only\b",
    r"\bremote within (?:the )?u\.?s\.?\b",
    r"\bauthori[sz]ed to work in (?:the )?u\.?s\.?(?: without sponsorship)?\b",
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
        return RemoteResult(False, "Modalidade híbrida ou presencial")
    if _first_match(NON_REMOTE_DESCRIPTION_PATTERNS, job.description):
        return RemoteResult(False, "Descrição exige trabalho híbrido ou presencial")
    if job.ats:
        is_remote = bool(re.search(r"\bremote\b", job.remote_scope or "", re.I))
        return RemoteResult(is_remote, "ATS confirmou remoto" if is_remote else "ATS sem remoto")
    if job.remote_scope or _first_match(REMOTE_EVIDENCE_PATTERNS, workplace):
        return RemoteResult(True, "Modalidade remota confirmada")
    return RemoteResult(False, "Sem evidência de modalidade remota")


def technical_gate(job: RawJob, config: AppConfig) -> TechnicalResult:
    filters = config.filtros
    searchable = f"{job.title}\n{job.description}"
    if filters.titulos_rejeitados and any(
        re.search(pattern, job.title, re.I) for pattern in filters.titulos_rejeitados
    ):
        return TechnicalResult(False, "Título está na lista de exclusão", [])
    if filters.titulos_aceitos and not any(
        re.search(pattern, job.title, re.I) for pattern in filters.titulos_aceitos
    ):
        return TechnicalResult(False, "Título fora do perfil configurado", [])
    if filters.palavras_rejeitadas and any(
        re.search(pattern, searchable, re.I) for pattern in filters.palavras_rejeitadas
    ):
        return TechnicalResult(False, "Descrição contém termo de exclusão", [])
    unsupported_language = _unsupported_language(searchable, filters.idiomas_aceitos)
    if unsupported_language:
        return TechnicalResult(
            False,
            f"Idioma detectado fora do objetivo: {unsupported_language}",
            [],
        )
    if job.salary_currency and job.salary_currency.upper() in {
        currency.upper() for currency in filters.moedas_rejeitadas
    }:
        return TechnicalResult(False, "Moeda explicitamente fora do objetivo", [])
    if job.date_posted and job.date_posted < datetime.now(UTC) - timedelta(
        days=filters.idade_maxima_dias
    ):
        return TechnicalResult(False, "Vaga mais antiga que o limite configurado", [])
    technologies = [
        technology
        for technology in filters.tecnologias
        if re.search(rf"\b{re.escape(technology)}\b", searchable, re.I)
    ]
    if filters.exigir_tecnologia_compativel and not technologies:
        return TechnicalResult(False, "Nenhuma tecnologia do perfil encontrada", [])
    return TechnicalResult(True, "Perfil técnico compatível", technologies)


def geographic_gate(job: RawJob, country: str = "BR") -> GateResult:
    evidence_source = f"{job.location_text}\n{job.description}"
    negative = _first_match(NEGATIVE_PATTERNS, evidence_source)
    if negative:
        return GateResult(
            decision=Eligibility.INCOMPATIBLE,
            role_match=True,
            geo_match="no",
            reason=f"Restrição geográfica incompatível: {negative}",
            geo_evidence=negative,
            employment_type=_employment(job.employment_type),
            payment_currency=job.salary_currency or "unknown",
        )
    normalized_countries = {item.upper() for item in job.allowed_countries}
    if normalized_countries:
        if (
            country.upper() in normalized_countries
            or "BRASIL" in normalized_countries
            or "BRAZIL" in normalized_countries
        ):
            evidence = ", ".join(job.allowed_countries)
            return _compatible(job, f"País aceito explicitamente: {evidence}", evidence)
        return GateResult(
            decision=Eligibility.INCOMPATIBLE,
            role_match=True,
            geo_match="no",
            reason="Lista de países permitidos não inclui o Brasil",
            geo_evidence=", ".join(job.allowed_countries),
            employment_type=_employment(job.employment_type),
            payment_currency=job.salary_currency or "unknown",
        )
    positive = _first_match(POSITIVE_PATTERNS, evidence_source)
    if positive:
        return _compatible(job, f"Região compatível encontrada: {positive}", positive)
    timezone = _compatible_timezone(job.timezone_requirements)
    if timezone:
        return _compatible(job, f"Fuso aceito inclui UTC-3: {timezone}", timezone)
    return GateResult(
        decision=Eligibility.UNCERTAIN,
        role_match=True,
        geo_match="unknown",
        reason="Vaga remota sem confirmação de que aceita candidatos no Brasil",
        geo_evidence=None,
        employment_type=_employment(job.employment_type),
        payment_currency=job.salary_currency or "unknown",
    )


def _first_match(patterns: tuple[str, ...], value: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, value, re.I)
        if match:
            start = max(0, match.start() - 50)
            end = min(len(value), match.end() + 70)
            return " ".join(value[start:end].split())
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


def _compatible_timezone(values: list[str]) -> str | None:
    for value in values:
        matches = [int(item) for item in re.findall(r"(?<!\d)([+-]?\d{1,2})(?!\d)", value)]
        if -3 in matches or len(matches) >= 2 and min(matches) <= -3 <= max(matches):
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
