# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import collections
import json

from . import _abc


# Internal properties of CosmosDB documents.
_SYSTEM_KEYS = {'_etag', '_lsn', '_rid', '_self', '_ts'}


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
        filtered = {k: v for k, v in dct.items() if k not in _SYSTEM_KEYS}
        return cls(filtered)

    def to_json(self) -> str:
        """Return the JSON representation of the document."""
        return json.dumps(dict(self))

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
