"""
Tests for swop.cqrs decorators + registry.
"""

from dataclasses import dataclass

import pytest

from swop.cqrs import (
    CqrsRegistry,
    command,
    event,
    get_registry,
    handler,
    query,
    reset_registry,
)


@pytest.fixture(autouse=True)
def _reset():
    reset_registry()
    yield
    reset_registry()


def test_command_decorator_registers_class():
    @command("customer")
    @dataclass
    class CreateCustomer:
        name: str
        email: str

    reg = get_registry()
    records = reg.of_kind("command")
    assert len(records) == 1
    record = records[0]
    assert record.context == "customer"
    assert record.cls is CreateCustomer
    assert record.qualname.endswith("CreateCustomer")
    assert record.source_file is not None
    assert getattr(CreateCustomer, "__swop_cqrs__") is record


def test_query_and_event_decorators_kept_separate():
    @query("customer")
    @dataclass
    class GetCustomer:
        customer_id: int

    @event("customer", emits=())
    @dataclass
    class CustomerCreated:
        customer_id: int

    reg = get_registry()
    assert {r.kind for r in reg.all()} == {"query", "event"}
    assert reg.by_context("customer")


def test_handler_decorator_links_to_target_class():
    @command("device")
    @dataclass
    class PowerOn:
        device_id: str

    @handler(PowerOn)
    class PowerOnHandler:
        def handle(self, cmd: PowerOn) -> bool:
            return True

    reg = get_registry()
    handlers = reg.of_kind("handler")
    assert len(handlers) == 1
    record = handlers[0]
    assert record.handles == "PowerOn"
    # context inherited from the decorated target
    assert record.context == "device"


def test_handler_decorator_accepts_string_target():
    @handler("LegacyCommand", context="legacy")
    class LegacyHandler:
        pass

    reg = get_registry()
    records = reg.of_kind("handler")
    assert records[0].handles == "LegacyCommand"
    assert records[0].context == "legacy"


def test_decorators_reject_non_class_targets():
    with pytest.raises(TypeError):
        command("customer")(lambda: None)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        command("")  # blank context


def test_registry_summary_groups_by_kind():
    @command("a")
    class Cmd: ...

    @query("a")
    class Qry: ...

    @event("a")
    class Evt: ...

    @handler(Cmd)
    class H: ...

    summary = get_registry().summary()
    assert summary == {"command": 1, "query": 1, "event": 1, "handler": 1}


def test_emits_accepts_classes_and_strings():
    @event("customer")
    class CustomerSuspended: ...

    @command("customer", emits=[CustomerSuspended, "CustomerArchived"])
    class SuspendCustomer:
        pass

    record = getattr(SuspendCustomer, "__swop_cqrs__")
    assert record.emits == ("CustomerSuspended", "CustomerArchived")


def test_reset_registry_clears_state():
    @command("x")
    class C: ...

    assert len(get_registry()) == 1
    reset_registry()
    assert len(get_registry()) == 0


def test_local_registry_is_independent():
    reg = CqrsRegistry()
    from swop.cqrs.registry import CqrsRecord

    reg.register(CqrsRecord(kind="command", context="z", qualname="a.B", module="a", cls=type))
    assert len(reg) == 1
    assert len(get_registry()) == 0
