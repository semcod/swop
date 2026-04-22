"""
Tests for the swop runtime and reconciliation engine.
"""

import pytest

from swop import (
    BackendIntrospector,
    DriftError,
    FrontendIntrospector,
    SwopRuntime,
)


def _runtime(mode="SOFT"):
    backend = BackendIntrospector(
        models={"Pressure": ["temp", "pressure_low", "pressure_high"]},
        routes=["/pressure", "/status"],
    )
    return SwopRuntime(mode=mode, backend=backend, frontend=FrontendIntrospector())


def test_add_model_commits_version():
    runtime = _runtime()
    runtime.add_model("Pressure", ["temp", "pressure_low", "pressure_high"])
    assert "Pressure" in runtime.graph.models
    assert runtime.graph.version >= 2
    assert runtime.graph.history[-1].changes == ["add_model:Pressure"]


def test_run_sync_detects_invalid_bindings():
    runtime = _runtime(mode="SOFT")
    runtime.add_model("Pressure", ["temp"])
    runtime.add_ui_binding("#sensor-temp", "temp")
    runtime.add_ui_binding("#broken", "non_existing_field")

    drift = runtime.run_sync()

    assert "#broken" in drift.invalid_bindings
    assert "#sensor-temp" not in drift.invalid_bindings


def test_auto_heal_removes_invalid_bindings():
    runtime = _runtime(mode="AUTO_HEAL")
    runtime.add_model("Pressure", ["temp"])
    runtime.add_ui_binding("#sensor-temp", "temp")
    runtime.add_ui_binding("#broken", "missing")

    runtime.run_sync()

    selectors = {b.selector for b in runtime.graph.ui_bindings}
    assert "#broken" not in selectors
    assert "#sensor-temp" in selectors


def test_strict_mode_raises_on_invalid_binding():
    runtime = _runtime(mode="STRICT")
    runtime.add_model("Pressure", ["temp"])
    runtime.add_ui_binding("#broken", "missing")

    with pytest.raises(DriftError):
        runtime.run_sync()


def test_state_yaml_is_serializable():
    runtime = _runtime()
    runtime.add_model("Pressure", ["temp"])
    runtime.add_ui_binding("#sensor-temp", "temp")
    runtime.run_sync()

    yaml_text = runtime.state_yaml()
    assert "graph_version" in yaml_text
    assert "Pressure" in yaml_text


def test_docker_export_contains_services():
    runtime = _runtime()
    runtime.add_service("api", ["/pressure", "/status"])
    compose = runtime.docker_compose()
    assert "api" in compose
    assert "image" in compose
