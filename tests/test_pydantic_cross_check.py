"""Tests for swop.registry.pydantic_cross_check.

Regression for the c2004 ADR-012 Wave 2 bug: ``GetServiceIdHealth.query.json``
declared ``database.enum = ["ok", "error"]`` while the backing Pydantic model
was ``Literal["ok", "error"]`` but the route handler wrote ``"degraded"``.
After the runtime crash the contract was widened to
``["ok", "degraded", "error"]``. This test fixes that expectation and checks
that the cross-check reports drift the *next* time either side moves.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from swop.registry import (
    cross_check_contract,
    cross_check_contracts,
    load_contracts,
)
from swop.registry.loader import Contract


@pytest.fixture()
def project_root(tmp_path: Path) -> Path:
    (tmp_path / "contracts").mkdir()
    (tmp_path / "backend").mkdir()
    return tmp_path


def _write_contract(project_root: Path, filename: str, data: dict) -> Contract:
    path = project_root / "contracts" / filename
    path.write_text(json.dumps(data), encoding="utf-8")
    return next(c for c in load_contracts(project_root / "contracts") if c.path == path)


def _write_pydantic_module(project_root: Path, body: str) -> Path:
    path = project_root / "backend" / "service_id.py"
    path.write_text(textwrap.dedent(body), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_aligned_enum_and_literal_are_ok(project_root: Path) -> None:
    _write_pydantic_module(
        project_root,
        """
        from typing import Literal
        from pydantic import BaseModel

        class _Checks(BaseModel):
            database: Literal["ok", "degraded", "error"]
            cqrs_bus: Literal["ok", "error"]
        """,
    )
    contract = _write_contract(
        project_root,
        "GetServiceIdHealth.query.json",
        {
            "query": "GetServiceIdHealth",
            "kind": "CQRS_QUERY",
            "version": "1.0.0",
            "module": "connect-id",
            "input": {},
            "output": {
                "checks": {
                    "type": "object",
                    "properties": {
                        "database": {
                            "type": "string",
                            "enum": ["ok", "degraded", "error"],
                        },
                        "cqrs_bus": {
                            "type": "string",
                            "enum": ["ok", "error"],
                        },
                    },
                }
            },
            "layers": {"python": "backend/service_id.py"},
        },
    )

    result = cross_check_contract(contract, root=project_root)

    assert result.ok is True
    assert not result.errors


# ---------------------------------------------------------------------------
# Regression: the actual c2004 bug
# ---------------------------------------------------------------------------


def test_contract_enum_narrower_than_literal_is_flagged(project_root: Path) -> None:
    """Contract missing the ``degraded`` value — exactly the state we had
    before the fix in commit 7ee866dc."""
    _write_pydantic_module(
        project_root,
        """
        from typing import Literal
        from pydantic import BaseModel

        class _Checks(BaseModel):
            database: Literal["ok", "degraded", "error"]
        """,
    )
    contract = _write_contract(
        project_root,
        "GetServiceIdHealth.query.json",
        {
            "query": "GetServiceIdHealth",
            "kind": "CQRS_QUERY",
            "version": "1.0.0",
            "module": "connect-id",
            "input": {},
            "output": {
                "checks": {
                    "type": "object",
                    "properties": {
                        "database": {
                            "type": "string",
                            "enum": ["ok", "error"],
                        },
                    },
                }
            },
            "layers": {"python": "backend/service_id.py"},
        },
    )

    result = cross_check_contract(contract, root=project_root)

    assert result.ok is False
    assert any("database" in err and "degraded" in err for err in result.errors)


def test_output_contract_wider_than_literal_is_warning_not_error(
    project_root: Path,
) -> None:
    """Inverse output drift: contract advertises values Pydantic never returns.

    Under directional rules this is a **warning**, not an error, because no
    client can crash on a value that the server will never emit. The contract
    is dishonest about dead code paths but the runtime is safe.
    """
    _write_pydantic_module(
        project_root,
        """
        from typing import Literal
        from pydantic import BaseModel

        class _Checks(BaseModel):
            database: Literal["ok", "error"]
        """,
    )
    contract = _write_contract(
        project_root,
        "GetServiceIdHealth.query.json",
        {
            "query": "GetServiceIdHealth",
            "kind": "CQRS_QUERY",
            "version": "1.0.0",
            "module": "connect-id",
            "input": {},
            "output": {
                "checks": {
                    "type": "object",
                    "properties": {
                        "database": {
                            "type": "string",
                            "enum": ["ok", "degraded", "error"],
                        },
                    },
                }
            },
            "layers": {"python": "backend/service_id.py"},
        },
    )

    result = cross_check_contract(contract, root=project_root)

    assert result.ok is True, f"should be warning-only, got errors: {result.errors}"
    assert any(
        "database" in w and "degraded" in w and "dead code" in w.lower()
        for w in result.warnings
    ), f"expected warning about dead code paths, got: {result.warnings}"


def test_input_contract_wider_than_literal_is_error(project_root: Path) -> None:
    """Input drift: contract advertises a value Pydantic will reject with 422.

    A client obeying the contract will send a value the server cannot accept.
    Under directional rules this is an **error** regardless of which side is
    wider (here contract ⊋ pydantic on ``input``).
    """
    _write_pydantic_module(
        project_root,
        """
        from typing import Literal
        from pydantic import BaseModel

        class IdentifyCommandInput(BaseModel):
            method: Literal["rfid", "manual"]
        """,
    )
    contract = _write_contract(
        project_root,
        "Identify.command.json",
        {
            "command": "Identify",
            "kind": "CQRS_COMMAND",
            "version": "1.0.0",
            "module": "connect-id",
            "input": {
                "method": {
                    "type": "string",
                    "enum": ["rfid", "qr", "manual"],
                }
            },
            "output": {},
            "layers": {"python": "backend/service_id.py"},
        },
    )

    result = cross_check_contract(contract, root=project_root)

    assert result.ok is False, (
        "contract advertising values Pydantic will reject must fail"
    )
    assert any(
        "input" in err and "method" in err and "qr" in err for err in result.errors
    ), f"expected error citing qr on input, got: {result.errors}"


def test_input_pydantic_wider_than_contract_is_ok(project_root: Path) -> None:
    """Input drift: Pydantic tolerates more values than the contract advertises.

    This is an **intentional API restriction**, not a drift. The server will
    accept anything a client sends that matches the contract; the extra
    Pydantic values are simply inaccessible via this public surface.
    """
    _write_pydantic_module(
        project_root,
        """
        from typing import Literal
        from pydantic import BaseModel

        class IdentifyCommandInput(BaseModel):
            method: Literal["rfid", "qr", "barcode", "manual"]
        """,
    )
    contract = _write_contract(
        project_root,
        "Identify.command.json",
        {
            "command": "Identify",
            "kind": "CQRS_COMMAND",
            "version": "1.0.0",
            "module": "connect-id",
            "input": {
                "method": {
                    "type": "string",
                    "enum": ["rfid", "manual"],
                }
            },
            "output": {},
            "layers": {"python": "backend/service_id.py"},
        },
    )

    result = cross_check_contract(contract, root=project_root)

    assert result.ok is True, f"intentional narrowing must be ok, got: {result.errors}"
    assert not result.warnings, (
        f"input narrowing should not even warn, got: {result.warnings}"
    )


# ---------------------------------------------------------------------------
# Silent skips (non-errors)
# ---------------------------------------------------------------------------


def test_missing_pydantic_field_is_silently_skipped(project_root: Path) -> None:
    """Contract field with enum, but no matching Pydantic field -> silent skip."""
    _write_pydantic_module(
        project_root,
        """
        from pydantic import BaseModel

        class User(BaseModel):
            name: str
        """,
    )
    contract = _write_contract(
        project_root,
        "GetUser.query.json",
        {
            "query": "GetUser",
            "kind": "CQRS_QUERY",
            "version": "1.0.0",
            "module": "connect-id",
            "input": {},
            "output": {
                "role": {"type": "string", "enum": ["admin", "operator"]},
            },
            "layers": {"python": "backend/service_id.py"},
        },
    )

    result = cross_check_contract(contract, root=project_root)

    assert result.ok is True


def test_contract_without_layers_python_is_skipped(tmp_path: Path) -> None:
    (tmp_path / "contracts").mkdir()
    contract = _write_contract(
        tmp_path,
        "GetFoo.query.json",
        {
            "query": "GetFoo",
            "kind": "CQRS_QUERY",
            "version": "1.0.0",
            "module": "foo",
            "input": {},
            "output": {"kind": {"type": "string", "enum": ["a", "b"]}},
            "layers": {"python": None},
        },
    )

    result = cross_check_contract(contract, root=tmp_path)

    assert result.ok is True


def test_optional_literal_union_is_handled(project_root: Path) -> None:
    """``Literal[...] | None`` unwrapping — common Pydantic pattern."""
    _write_pydantic_module(
        project_root,
        """
        from typing import Literal, Optional
        from pydantic import BaseModel

        class _Checks(BaseModel):
            database: Optional[Literal["ok", "error"]]
            cqrs_bus: Literal["ok", "error"] | None
        """,
    )
    contract = _write_contract(
        project_root,
        "GetServiceIdHealth.query.json",
        {
            "query": "GetServiceIdHealth",
            "kind": "CQRS_QUERY",
            "version": "1.0.0",
            "module": "connect-id",
            "input": {},
            "output": {
                "checks": {
                    "type": "object",
                    "properties": {
                        "database": {"type": "string", "enum": ["ok", "error"]},
                        "cqrs_bus": {"type": "string", "enum": ["ok", "error"]},
                    },
                }
            },
            "layers": {"python": "backend/service_id.py"},
        },
    )

    result = cross_check_contract(contract, root=project_root)

    assert result.ok is True, result.format()


# ---------------------------------------------------------------------------
# Batch API
# ---------------------------------------------------------------------------


def test_cross_check_contracts_returns_pairs(project_root: Path) -> None:
    _write_pydantic_module(
        project_root,
        """
        from typing import Literal
        from pydantic import BaseModel

        class _Checks(BaseModel):
            database: Literal["ok", "error"]
        """,
    )
    good = _write_contract(
        project_root,
        "GetA.query.json",
        {
            "query": "GetA",
            "kind": "CQRS_QUERY",
            "version": "1.0.0",
            "module": "m",
            "input": {},
            "output": {"database": {"type": "string", "enum": ["ok", "error"]}},
            "layers": {"python": "backend/service_id.py"},
        },
    )
    bad = _write_contract(
        project_root,
        "GetB.query.json",
        {
            "query": "GetB",
            "kind": "CQRS_QUERY",
            "version": "1.0.0",
            "module": "m",
            "input": {},
            "output": {"database": {"type": "string", "enum": ["ok", "error", "extra"]}},
            "layers": {"python": "backend/service_id.py"},
        },
    )

    pairs = cross_check_contracts([good, bad], root=project_root)
    by_name = {c.name: r for c, r in pairs}
    # GetA: equal sets -> clean
    assert by_name["GetA"].ok is True
    assert not by_name["GetA"].warnings
    # GetB: output contract ⊋ pydantic -> warning-only under directional rules
    # (server never emits 'extra', so the client cannot crash on it).
    assert by_name["GetB"].ok is True
    assert any("extra" in w for w in by_name["GetB"].warnings)
