from dict2xml.logic import Converter, Node

from .version import VERSION


def dict2xml(data, *args, **kwargs):
    """Return an XML string of a Python dict object."""
    return Converter(*args, **kwargs).build(data)


__all__ = ["dict2xml", "Converter", "Node", "VERSION"]
