from __future__ import annotations

from pathlib import Path

import yaml

from app.config import AppConfig
from app.models import Preferences


def read_preferences(config: AppConfig) -> Preferences:
    return Preferences(
        profile_summary=config.perfil.resumo,
        residence_country=config.objetivo.pais_residencia,
        accepted_timezones=config.objetivo.fusos_aceitos,
        accepted_titles=config.filtros.titulos_aceitos,
        rejected_titles=config.filtros.titulos_rejeitados,
        technologies=config.filtros.tecnologias,
        require_technology_match=config.filtros.exigir_tecnologia_compativel,
        rejected_keywords=config.filtros.palavras_rejeitadas,
        accepted_languages=config.filtros.idiomas_aceitos,
        rejected_currencies=config.filtros.moedas_rejeitadas,
        max_age_days=config.filtros.idade_maxima_dias,
        search_terms=config.buscas.termos,
    )


def apply_preferences(config: AppConfig, preferences: Preferences) -> AppConfig:
    payload = config.model_dump()
    payload["perfil"]["resumo"] = preferences.profile_summary
    payload["objetivo"]["pais_residencia"] = preferences.residence_country.upper()
    payload["objetivo"]["fusos_aceitos"] = preferences.accepted_timezones
    payload["filtros"]["titulos_aceitos"] = preferences.accepted_titles
    payload["filtros"]["titulos_rejeitados"] = preferences.rejected_titles
    payload["filtros"]["tecnologias"] = preferences.technologies
    payload["filtros"]["exigir_tecnologia_compativel"] = preferences.require_technology_match
    payload["filtros"]["palavras_rejeitadas"] = preferences.rejected_keywords
    payload["filtros"]["idiomas_aceitos"] = preferences.accepted_languages
    payload["filtros"]["moedas_rejeitadas"] = preferences.rejected_currencies
    payload["filtros"]["idade_maxima_dias"] = preferences.max_age_days
    payload["buscas"]["termos"] = preferences.search_terms
    return AppConfig.model_validate(payload)


def write_config(config: AppConfig, path: Path) -> None:
    payload = config.model_dump()
    path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
