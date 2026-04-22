"""
Tests for the swop CLI entry point.
"""

from swop.cli import main


def test_cli_state_command(capsys):
    exit_code = main(["--mode", "SOFT", "state"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "graph_version" in captured.out


def test_cli_export_docker(capsys):
    exit_code = main(["--mode", "SOFT", "export", "docker"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "services" in captured.out


def test_cli_inspect_backend(capsys):
    exit_code = main(["--mode", "SOFT", "inspect", "backend"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "routes" in captured.out or "models" in captured.out
