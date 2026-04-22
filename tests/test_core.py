"""
Tests for core module
"""

import inspect as pkg_inspect
from inspector.core import inspect_object, get_signature


def test_inspect_object():
    """Test inspect_object function"""
    obj = "test string"
    info = inspect_object(obj)
    assert info['type'] == 'str'
    assert info['module'] == 'builtins'


def test_get_signature():
    """Test get_signature function"""
    def example_func(a, b, c=None):
        pass

    sig = get_signature(example_func)
    assert 'a' in sig
    assert 'b' in sig
    assert 'c' in sig
