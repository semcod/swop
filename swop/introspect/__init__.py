"""
Introspection layer.

Provides backend and frontend introspectors used to extract the *actual*
runtime state of a system, which is then compared against the declared
project graph by the reconciliation engine.
"""

from swop.introspect.backend import BackendIntrospector
from swop.introspect.frontend import FrontendIntrospector

__all__ = ["BackendIntrospector", "FrontendIntrospector"]
