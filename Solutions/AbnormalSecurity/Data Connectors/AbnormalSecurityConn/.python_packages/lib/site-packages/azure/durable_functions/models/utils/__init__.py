"""Utility functions used by the Durable Function python library.

_Internal Only_
"""
from pkgutil import extend_path
import typing
__path__: typing.Iterable[str] = extend_path(__path__, __name__)  # type: ignore
