"""
Tests for swop.config.
"""

from pathlib import Path

import pytest

from swop.config import SwopConfigError, load_config


def _write(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")


def test_load_minimal_config(tmp_path):
    cfg_path = tmp_path / "swop.yaml"
    _write(cfg_path, "version: 1\nproject: demo\n")

    cfg = load_config(cfg_path)
    assert cfg.project == "demo"
    assert cfg.version == 1
    assert cfg.language == "python"
    assert cfg.source_roots == []
    assert cfg.bounded_contexts == []
    assert cfg.bus is None
    assert cfg.read_models is None
    assert cfg.project_root == tmp_path
    assert cfg.state_path == tmp_path / ".swop"


def test_load_full_config(tmp_path, monkeypatch):
    monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@mq:5672/")
    monkeypatch.setenv("DB_URL", "postgresql://user:pw@db:5432/app")

    cfg_path = tmp_path / "swop.yaml"
    _write(
        cfg_path,
        """\
version: 1
project: c2004
language: python
source_roots:
  - backend/app
  - services
exclude:
  - "**/tests/**"
bounded_contexts:
  - name: customer
    source: backend/app/domain/customer
  - name: firmware
    source: backend/firmware
    external: true
bus:
  type: rabbitmq
  url: "${RABBITMQ_URL}"
read_models:
  engine: postgresql
  url: "${DB_URL}"
""",
    )

    cfg = load_config(cfg_path)
    assert cfg.project == "c2004"
    assert cfg.source_roots == ["backend/app", "services"]
    assert len(cfg.bounded_contexts) == 2
    assert cfg.bounded_contexts[0].name == "customer"
    assert cfg.bounded_contexts[1].external is True
    assert cfg.bus is not None
    assert cfg.bus.type == "rabbitmq"
    assert cfg.bus.url == "amqp://guest:guest@mq:5672/"
    assert cfg.read_models is not None
    assert cfg.read_models.url == "postgresql://user:pw@db:5432/app"
    assert cfg.context("customer") is not None
    assert cfg.context("missing") is None


def test_env_vars_keep_literal_when_missing(tmp_path):
    cfg_path = tmp_path / "swop.yaml"
    _write(
        cfg_path,
        """\
version: 1
project: demo
bus:
  type: rabbitmq
  url: "${UNSET_VAR_XYZ}"
""",
    )
    cfg = load_config(cfg_path)
    assert cfg.bus is not None
    assert cfg.bus.url == "${UNSET_VAR_XYZ}"


def test_missing_config_raises(tmp_path):
    with pytest.raises(SwopConfigError):
        load_config(tmp_path / "nope.yaml")


def test_bounded_context_without_required_fields(tmp_path):
    cfg_path = tmp_path / "swop.yaml"
    _write(
        cfg_path,
        """\
version: 1
project: demo
bounded_contexts:
  - name: orphan
""",
    )
    with pytest.raises(SwopConfigError):
        load_config(cfg_path)


def test_unknown_keys_stored_in_extra(tmp_path):
    cfg_path = tmp_path / "swop.yaml"
    _write(
        cfg_path,
        """\
version: 1
project: demo
future_feature:
  flag: true
""",
    )
    cfg = load_config(cfg_path)
    assert cfg.extra["future_feature"] == {"flag": True}
