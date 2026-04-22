"""
Inspect package
"""

__version__ = "0.1.1"

from inspector.core import inspect_object, get_signature
from inspector.utils import is_callable, get_docstring

__all__ = [
    "inspect_object",
    "get_signature",
    "is_callable",
    "get_docstring",
]
