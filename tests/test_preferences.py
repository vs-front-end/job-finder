from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from app.main import create_app


def build_client(tmp_path: Path) -> tuple[TestClient, Path]:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "filtros": {"titulos_aceitos": ["front.?end"], "tecnologias": ["React"]},
                "fontes": {
                    "himalayas": False,
                    "jobicy": False,
                    "remote_ok": False,
                    "remotive": False,
                    "we_work_remotely": False,
                    "arbeitnow": False,
                    "hacker_news": False,
                    "arc": False,
                    "y_combinator": False,
                    "the_muse": False,
                    "get_on_board": False,
                    "startup_jobs": False,
                    "working_nomads": False,
                    "remotejobs_org": False,
                    "landing_jobs": False,
                    "jobspresso": False,
                    "remote_first_jobs": False,
                    "ats": False,
                },
            }
        ),
        encoding="utf-8",
    )
    app = create_app(config_path, tmp_path / "test.db", start_scheduler=False)
    return TestClient(app), config_path


def test_preferences_roundtrip_persists_and_reloads(tmp_path: Path) -> None:
    client, config_path = build_client(tmp_path)

    initial = client.get("/api/preferences").json()
    assert initial["accepted_titles"] == ["front.?end"]

    payload = {
        **initial,
        "residence_country": "pt",
        "accepted_titles": ["full.?stack"],
        "technologies": ["Vue", "TypeScript"],
        "max_age_days": 14,
        "search_terms": ["Vue"],
    }
    response = client.put("/api/preferences", json=payload)

    assert response.status_code == 200
    assert response.json()["residence_country"] == "PT"
    saved = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert saved["objetivo"]["pais_residencia"] == "PT"
    assert saved["filtros"]["titulos_aceitos"] == ["full.?stack"]
    assert saved["filtros"]["idade_maxima_dias"] == 14
    assert client.get("/api/preferences").json()["technologies"] == ["Vue", "TypeScript"]


def test_preferences_rejects_invalid_regex(tmp_path: Path) -> None:
    client, _ = build_client(tmp_path)
    initial = client.get("/api/preferences").json()

    response = client.put(
        "/api/preferences", json={**initial, "accepted_titles": ["([invalid"]}
    )

    assert response.status_code == 422
