"""
Inspect package
"""

__version__ = "0.1.3"

from swop.core import inspect_object, get_signature
from swop.utils import is_callable, get_docstring

__all__ = [
    "inspect_object",
    "get_signature",
    "is_callable",
    "get_docstring",
]
