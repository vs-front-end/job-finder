from datetime import UTC, datetime, timedelta

from app.config import AppConfig, ObjectiveConfig
from app.models import Eligibility, RawJob
from app.pipeline.gates import geographic_gate, remote_gate, technical_gate


def raw(**changes: object) -> RawJob:
    values: dict[str, object] = {
        "source": "test",
        "source_job_id": "1",
        "source_url": "https://example.com/job/1",
        "title": "Senior Software Engineer",
        "company": "Example",
        "description": "React and TypeScript. Remote worldwide.",
        "location_text": "Remote",
    }
    values.update(changes)
    return RawJob.model_validate(values)


def test_negative_geo_rule_wins_over_worldwide() -> None:
    job = raw(description="Remote worldwide, but candidates must reside in the United States")

    result = geographic_gate(job)

    assert result.decision == Eligibility.INCOMPATIBLE
    assert result.geo_match == "no"


def test_brazil_country_is_compatible() -> None:
    result = geographic_gate(raw(allowed_countries=["BR"]))

    assert result.decision == Eligibility.COMPATIBLE
    assert result.geo_evidence == "BR"


def test_remote_without_region_is_uncertain() -> None:
    result = geographic_gate(raw(description="Build APIs with Python from a remote office."))

    assert result.decision == Eligibility.UNCERTAIN
    assert result.geo_match == "unknown"


def test_remote_gate_accepts_remote_job() -> None:
    result = remote_gate(raw(remote_scope="remote"))

    assert result.accepted is True


def test_remote_gate_rejects_hybrid_job() -> None:
    result = remote_gate(
        raw(title="Software Engineer - Remote or Hybrid", remote_scope="remote")
    )

    assert result.accepted is False


def test_remote_gate_rejects_ats_without_remote_scope() -> None:
    result = remote_gate(raw(ats="greenhouse", location_text="New York"))

    assert result.accepted is False


def test_remote_gate_does_not_confuse_hybrid_technology_with_workplace() -> None:
    result = remote_gate(
        raw(description="Build a hybrid AI and human platform.", remote_scope="remote")
    )

    assert result.accepted is True


def test_technical_gate_finds_technologies(config: AppConfig) -> None:
    result = technical_gate(raw(), config)

    assert result.accepted is True
    assert result.technologies == ["React", "TypeScript"]


def test_technical_gate_can_require_a_profile_technology(config: AppConfig) -> None:
    filters = config.filtros.model_copy(update={"exigir_tecnologia_compativel": True})
    strict_config = config.model_copy(update={"filtros": filters})

    result = technical_gate(
        raw(description="Build distributed systems. Remote worldwide."), strict_config
    )

    assert result.accepted is False
    assert "technology" in result.reason


def test_technical_gate_rejects_old_job(config: AppConfig) -> None:
    result = technical_gate(raw(date_posted=datetime.now(UTC) - timedelta(days=31)), config)

    assert result.accepted is False
    assert "older" in result.reason


def test_technical_gate_rejects_explicit_brl(config: AppConfig) -> None:
    result = technical_gate(raw(salary_currency="BRL"), config)

    assert result.accepted is False
    assert "Currency" in result.reason


def test_technical_gate_rejects_spanish_only_job(config: AppConfig) -> None:
    result = technical_gate(
        raw(
            title="Desarrollador Frontend",
            description=(
                "Buscamos un desarrollador con experiencia. Requisitos y responsabilidades: "
                "conocimientos de React. Puedes postular desde Latinoamérica."
            ),
        ),
        config,
    )

    assert result.accepted is False
    assert "language" in result.reason


def test_technical_gate_accepts_portuguese_job(config: AppConfig) -> None:
    result = technical_gate(
        raw(
            title="Desenvolvedor Frontend",
            description=(
                "Sobre a vaga: buscamos uma pessoa desenvolvedora. Você terá responsabilidades "
                "com React. Requisitos: experiência e conhecimentos de TypeScript."
            ),
        ),
        config,
    )

    assert result.accepted is True


def test_us_resident_treats_us_restriction_as_compatible() -> None:
    job = raw(description="Remote position, US only.")

    result = geographic_gate(job, ObjectiveConfig(pais_residencia="US"))

    assert result.decision == Eligibility.COMPATIBLE


def test_timezone_check_uses_configured_offsets() -> None:
    job = raw(description="Build APIs.", timezone_requirements=["UTC-8 to UTC-5"])

    result = geographic_gate(job, ObjectiveConfig(fusos_aceitos=["UTC-5"]))

    assert result.decision == Eligibility.COMPATIBLE
