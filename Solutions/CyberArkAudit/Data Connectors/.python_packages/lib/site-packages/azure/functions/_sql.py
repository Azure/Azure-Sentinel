# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import abc
import collections
import json


class BaseSqlRow(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def from_json(cls, json_data: str) -> 'BaseSqlRow':
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, dct: dict) -> 'BaseSqlRow':
        raise NotImplementedError

    @abc.abstractmethod
    def __getitem__(self, key):
        raise NotImplementedError

    @abc.abstractmethod
    def __setitem__(self, key, value):
        raise NotImplementedError

    @abc.abstractmethod
    def to_json(self) -> str:
        raise NotImplementedError


class BaseSqlRowList(abc.ABC):
    pass


class SqlRow(BaseSqlRow, collections.UserDict):
    """A SQL Row.

    SqlRow objects are ''UserDict'' subclasses and behave like dicts.
    """

    @classmethod
    def from_json(cls, json_data: str) -> 'BaseSqlRow':
        """Create a SqlRow from a JSON string."""
        return cls.from_dict(json.loads(json_data))

    @classmethod
    def from_dict(cls, dct: dict) -> 'BaseSqlRow':
        """Create a SqlRow from a dict object"""
        return cls({k: v for k, v in dct.items()})

    def to_json(self) -> str:
        """Return the JSON representation of the SqlRow"""
        return json.dumps(dict(self))

    def __getitem__(self, key):
        return collections.UserDict.__getitem__(self, key)

    def __setitem__(self, key, value):
        return collections.UserDict.__setitem__(self, key, value)

    def __repr__(self) -> str:
        return (
            f'<SqlRow at 0x{id(self):0x}>'
        )


class SqlRowList(BaseSqlRowList, collections.UserList):
    "A ''UserList'' subclass containing a list of :class:'~SqlRow' objects"
    pass
