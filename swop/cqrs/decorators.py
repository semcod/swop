"""
No-op CQRS decorators.

Each decorator registers the wrapped class into the module-global
:class:`CqrsRegistry` and returns it unchanged. Legacy projects can
sprinkle these decorators without altering any runtime behaviour.

Usage::

    from swop import command, event, query, handler

    @command("customer")
    @dataclass
    class CreateCustomer:
        name: str
        email: str

    @handler(CreateCustomer)
    class CreateCustomerHandler:
        def handle(self, cmd: CreateCustomer) -> int: ...

    @event("customer")
    @dataclass
    class CustomerCreated:
        customer_id: int

    @query("customer")
    @dataclass
    class GetCustomer:
        customer_id: int
"""

import inspect
from typing import Callable, Iterable, Optional, Type, TypeVar, Union

from swop.cqrs.registry import CqrsRecord, get_registry

T = TypeVar("T", bound=type)


def _collect_source(cls: type) -> tuple[Optional[str], Optional[int]]:
    try:
        source_file = inspect.getsourcefile(cls)
    except (TypeError, OSError):
        source_file = None
    try:
        _, line = inspect.getsourcelines(cls)
    except (TypeError, OSError):
        line = None
    return source_file, line


def _normalize_emits(emits: Optional[Iterable[Union[str, type]]]) -> tuple[str, ...]:
    if not emits:
        return ()
    out: list[str] = []
    for item in emits:
        if isinstance(item, type):
            out.append(item.__name__)
        else:
            out.append(str(item))
    return tuple(out)


def _make_decorator(kind: str):
    def decorator(
        context: str,
        *,
        emits: Optional[Iterable[Union[str, type]]] = None,
    ) -> Callable[[T], T]:
        if not isinstance(context, str) or not context.strip():
            raise ValueError(f"@{kind} requires a non-empty context name")

        emit_tuple = _normalize_emits(emits)

        def wrap(cls: T) -> T:
            if not isinstance(cls, type):
                raise TypeError(
                    f"@{kind}('{context}') must decorate a class, got {cls!r}"
                )
            source_file, source_line = _collect_source(cls)
            qualname = f"{cls.__module__}.{cls.__qualname__}"
            record = CqrsRecord(
                kind=kind,
                context=context,
                qualname=qualname,
                module=cls.__module__,
                cls=cls,
                source_file=source_file,
                source_line=source_line,
                emits=emit_tuple,
            )
            get_registry().register(record)
            # Expose the record on the class for downstream tools.
            setattr(cls, "__swop_cqrs__", record)
            return cls

        return wrap

    decorator.__name__ = kind
    decorator.__doc__ = f"Register the decorated class as a CQRS {kind}."
    return decorator


command = _make_decorator("command")
query = _make_decorator("query")
event = _make_decorator("event")


def handler(
    target: Union[type, str],
    *,
    context: Optional[str] = None,
) -> Callable[[T], T]:
    """
    Register the decorated class as the handler for ``target``.

    ``target`` may be the command/query class itself or its qualified
    name as a string. If ``context`` is omitted it falls back to the
    target's registered context when available.
    """

    target_name: str
    target_context: Optional[str] = context
    if isinstance(target, type):
        target_name = target.__name__
        target_record = getattr(target, "__swop_cqrs__", None)
        if target_record is not None and target_context is None:
            target_context = target_record.context
    elif isinstance(target, str) and target.strip():
        target_name = target
    else:
        raise TypeError("@handler requires a class or non-empty string target")

    resolved_context = target_context or "default"

    def wrap(cls: T) -> T:
        if not isinstance(cls, type):
            raise TypeError(
                f"@handler({target_name!r}) must decorate a class, got {cls!r}"
            )
        source_file, source_line = _collect_source(cls)
        qualname = f"{cls.__module__}.{cls.__qualname__}"
        record = CqrsRecord(
            kind="handler",
            context=resolved_context,
            qualname=qualname,
            module=cls.__module__,
            cls=cls,
            source_file=source_file,
            source_line=source_line,
            handles=target_name,
        )
        get_registry().register(record)
        setattr(cls, "__swop_cqrs__", record)
        return cls

    return wrap
