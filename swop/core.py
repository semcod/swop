"""
Core inspection utilities
"""


def inspect_object(obj):
    """
    Inspect an object and return its basic information.

    Args:
        obj: Any Python object

    Returns:
        dict: Dictionary containing object information
    """
    info = {
        'type': type(obj).__name__,
        'module': type(obj).__module__,
        'class': obj.__class__.__name__,
    }
    return info


def get_signature(func):
    """
    Get the signature of a function.

    Args:
        func: A callable function

    Returns:
        str: String representation of the function signature
    """
    import inspect as insp
    sig = insp.signature(func)
    return str(sig)
