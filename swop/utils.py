"""
Utility functions
"""


def is_callable(obj):
    """
    Check if an object is callable.

    Args:
        obj: Any Python object

    Returns:
        bool: True if object is callable, False otherwise
    """
    return callable(obj)


def get_docstring(obj):
    """
    Get the docstring of an object.

    Args:
        obj: Any Python object

    Returns:
        str or None: Docstring if available, None otherwise
    """
    return obj.__doc__
