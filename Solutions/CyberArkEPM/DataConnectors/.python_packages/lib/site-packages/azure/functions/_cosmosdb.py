# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import collections

from . import _abc
from ._jsonutils import json


class Document(_abc.Document, collections.UserDict):
    """An Azure Document.

    Document objects are ``UserDict`` subclasses and behave like dicts.
    """

    @classmethod
    def from_json(cls, json_data: str) -> 'Document':
        """Create a Document from a JSON string."""
        return cls.from_dict(json.loads(json_data))

    @classmethod
    def from_dict(cls, dct: dict) -> 'Document':
        """Create a Document from a dict object."""
        return cls({k: v for k, v in dct.items()})

    def to_json(self) -> str:
        """Return the JSON representation of the document."""
        return json.dumps(dict(self))

    def to_dict(self) -> dict:
        """Return the document as a dict - directly using self would also work
        as Document is ``UserDict`` subclass and behave like dict"""
        return dict(self)

    def __getitem__(self, key):
        return collections.UserDict.__getitem__(self, key)

    def __setitem__(self, key, value):
        return collections.UserDict.__setitem__(self, key, value)

    def __repr__(self) -> str:
        return (
            f'<azure.Document at 0x{id(self):0x}>'
        )


class DocumentList(_abc.DocumentList, collections.UserList):
    "A ``UserList`` subclass containing a list of :class:`~Document` objects"
    pass
