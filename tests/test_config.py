from __future__ import annotations

from pathlib import Path

import pytest

from app.config import load_config


def test_rejects_unknown_config_field(tmp_path: Path) -> None:
    path = tmp_path / "config.yaml"
    path.write_text("campo_inventado: true\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="Extra inputs are not permitted"):
        load_config(path)


def test_rejects_invalid_regex(tmp_path: Path) -> None:
    path = tmp_path / "config.yaml"
    path.write_text("filtros:\n  titulos_aceitos: ['[']\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="regex inválida"):
        load_config(path)
