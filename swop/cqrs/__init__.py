"""
CQRS annotations and registry for swop.

Provides no-op decorators (``@command``, ``@query``, ``@event``,
``@handler``) that register classes in a module-level
:class:`CqrsRegistry`. The decorators intentionally return the wrapped
class unchanged so they can be applied to legacy code without altering
runtime behaviour.
"""

from swop.cqrs.decorators import command, event, handler, query
from swop.cqrs.registry import (
    CqrsRecord,
    CqrsRegistry,
    get_registry,
    reset_registry,
)

__all__ = [
    "command",
    "event",
    "handler",
    "query",
    "CqrsRecord",
    "CqrsRegistry",
    "get_registry",
    "reset_registry",
]
