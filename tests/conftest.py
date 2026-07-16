from __future__ import annotations

from pathlib import Path

import pytest

from app.config import AppConfig
from app.database import Repository


@pytest.fixture
def config() -> AppConfig:
    return AppConfig.model_validate(
        {
            "filtros": {
                "titulos_aceitos": ["software.*engineer", "developer", "front.?end"],
                "titulos_rejeitados": ["manager"],
                "tecnologias": ["React", "TypeScript", "Python"],
            },
            "fontes": {
                "himalayas": False,
                "jobicy": False,
                "remote_ok": False,
                "remotive": False,
                "we_work_remotely": False,
                "arbeitnow": False,
                "hacker_news": False,
                "ats": False,
            },
            "limites": {"verificar_links": False},
        }
    )


@pytest.fixture
def repository(tmp_path: Path) -> Repository:
    instance = Repository(tmp_path / "test.db")
    instance.initialize()
    return instance
