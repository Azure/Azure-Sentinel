# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from abc import ABC, abstractmethod
from typing import Any, Union
from types import SimpleNamespace


"""
Azure Functions JSON utilities.
This module provides a JSON interface that can be used to serialize and
deserialize objects to and from JSON format. It supports both the `orjson`
and the standard `json` libraries, falling back to the standard library
if `orjson` is not available (installed).
"""


try:
    import orjson as _orjson
except ImportError:
    _orjson = None

# Standard library is always present
import json as _std_json


class JsonInterface(ABC):
    @abstractmethod
    def dumps(self, obj: Any) -> str:
        pass

    @abstractmethod
    def loads(self, s: Union[str, bytes, bytearray]) -> Any:
        pass


class OrJsonAdapter(JsonInterface):
    def __init__(self):
        assert _orjson is not None
        self.orjson = _orjson

    def dumps(self, obj: Any) -> str:
        # orjson.dumps returns bytes, decode to str
        return self.orjson.dumps(obj).decode("utf-8")

    def loads(self, s: Union[str, bytes, bytearray]) -> Any:
        return self.orjson.loads(s)


class StdJsonAdapter(JsonInterface):
    def __init__(self):
        self.json = _std_json

    def dumps(self, obj: Any) -> str:
        return self.json.dumps(obj)

    def loads(self, s: Union[str, bytes, bytearray]) -> Any:
        return self.json.loads(s)


if _orjson is not None:
    json_impl = OrJsonAdapter()
else:
    json_impl = StdJsonAdapter()


def dumps(obj: Any) -> str:
    return json_impl.dumps(obj)


def loads(s: Union[str, bytes, bytearray]) -> Any:
    return json_impl.loads(s)


json = SimpleNamespace(
    dumps=dumps,
    loads=loads
)
