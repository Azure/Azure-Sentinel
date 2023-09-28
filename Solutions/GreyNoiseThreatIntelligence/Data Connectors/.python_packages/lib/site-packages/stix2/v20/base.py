"""Base classes for STIX 2.0 type definitions."""

from ..base import (
    _DomainObject, _Extension, _Observable, _RelationshipObject, _STIXBase,
)


class _STIXBase20(_STIXBase):
    pass


class _Observable(_Observable, _STIXBase20):
    pass


class _Extension(_Extension, _STIXBase20):
    pass


class _DomainObject(_DomainObject, _STIXBase20):
    pass


class _RelationshipObject(_RelationshipObject, _STIXBase20):
    pass
