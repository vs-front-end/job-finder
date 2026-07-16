from __future__ import annotations

import re
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProfileConfig(StrictModel):
    resumo: str = ""


class ObjectiveConfig(StrictModel):
    pais_residencia: str = "BR"
    fusos_aceitos: list[str] = Field(default_factory=lambda: ["UTC-5", "UTC-4", "UTC-3", "UTC-2"])
    moedas_preferidas: list[str] = Field(default_factory=lambda: ["USD"])
    modalidades: list[str] = Field(default_factory=lambda: ["full-time", "contractor", "eor"])
    aceita_vaga_brasileira: bool = True


class FiltersConfig(StrictModel):
    titulos_aceitos: list[str] = Field(default_factory=list)
    titulos_rejeitados: list[str] = Field(default_factory=list)
    senioridades: list[str] = Field(default_factory=list)
    tecnologias: list[str] = Field(default_factory=list)
    exigir_tecnologia_compativel: bool = False
    palavras_rejeitadas: list[str] = Field(default_factory=list)
    idiomas_aceitos: list[str] = Field(default_factory=lambda: ["en", "pt"])
    moedas_rejeitadas: list[str] = Field(default_factory=lambda: ["BRL"])
    idade_maxima_dias: int = Field(default=7, ge=1, le=365)

    @field_validator("titulos_aceitos", "titulos_rejeitados", "palavras_rejeitadas")
    @classmethod
    def validate_regexes(cls, values: list[str]) -> list[str]:
        for value in values:
            try:
                re.compile(value, re.IGNORECASE)
            except re.error as error:
                raise ValueError(f"regex inválida '{value}': {error}") from error
        return values


class SearchConfig(StrictModel):
    termos: list[str] = Field(default_factory=list)
    arc_tags: list[str] = Field(
        default_factory=lambda: [
            "reactjs",
            "typescript",
            "javascript",
            "nodejs",
            "python",
            "full-stack-development",
        ]
    )
    consultas_xray: list[str] = Field(default_factory=list)


class CompanyConfig(StrictModel):
    nome: str
    ats: str
    board: str
    prioridade: str = "normal"
    ativo: bool = True


class FeedsConfig(StrictModel):
    google_alerts: list[str] = Field(default_factory=list)
    extras: list[str] = Field(default_factory=list)


class SourcesConfig(StrictModel):
    himalayas: bool = True
    jobicy: bool = True
    remote_ok: bool = True
    remotive: bool = True
    we_work_remotely: bool = True
    arbeitnow: bool = True
    hacker_news: bool = True
    arc: bool = True
    y_combinator: bool = True
    the_muse: bool = True
    get_on_board: bool = True
    startup_jobs: bool = True
    working_nomads: bool = True
    remotejobs_org: bool = True
    landing_jobs: bool = True
    jobspresso: bool = True
    remote_first_jobs: bool = True
    ats: bool = True
    linkedin_jobspy: bool = False
    glassdoor_jobspy: bool = False
    brave_search: bool = False


class LimitsConfig(StrictModel):
    intervalo_padrao_horas: int = Field(default=6, ge=1, le=168)
    timeout_segundos: int = Field(default=20, ge=2, le=120)
    concorrencia_por_dominio: int = Field(default=1, ge=1, le=10)
    itens_por_fonte: int = Field(default=100, ge=1, le=1000)
    verificar_links: bool = True
    revalidar_links_horas: int = Field(default=24, ge=1, le=720)


class AiConfig(StrictModel):
    enabled: bool = False
    command: str = "claude"
    timeout_seconds: int = Field(default=90, ge=10, le=600)


class AppConfig(StrictModel):
    perfil: ProfileConfig = Field(default_factory=ProfileConfig)
    objetivo: ObjectiveConfig = Field(default_factory=ObjectiveConfig)
    filtros: FiltersConfig = Field(default_factory=FiltersConfig)
    buscas: SearchConfig = Field(default_factory=SearchConfig)
    empresas: list[CompanyConfig] = Field(default_factory=list)
    feeds: FeedsConfig = Field(default_factory=FeedsConfig)
    fontes: SourcesConfig = Field(default_factory=SourcesConfig)
    limites: LimitsConfig = Field(default_factory=LimitsConfig)
    ia: AiConfig = Field(default_factory=AiConfig)


def load_config(path: Path) -> AppConfig:
    if not path.exists():
        raise RuntimeError(f"Configuração não encontrada: {path}")
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return AppConfig.model_validate(payload)
    except (yaml.YAMLError, ValidationError) as error:
        raise RuntimeError(f"Configuração inválida em {path}:\n{error}") from error
