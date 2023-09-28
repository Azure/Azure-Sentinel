"""Base classes for STIX 2.1 type definitions."""

from ..base import (
    _DomainObject, _Extension, _Observable, _RelationshipObject, _STIXBase,
)


class _STIXBase21(_STIXBase):
    pass


class _Observable(_Observable, _STIXBase21):

    def __init__(self, **kwargs):
        super(_Observable, self).__init__(**kwargs)
        if 'id' not in kwargs:
            # Specific to 2.1+ observables: generate a deterministic ID
            id_ = self._generate_id()

            # Spec says fall back to UUIDv4 if no contributing properties were
            # given.  That's what already happened (the following is actually
            # overwriting the default uuidv4), so nothing to do here.
            if id_ is not None:
                # Can't assign to self (we're immutable), so slip the ID in
                # more sneakily.
                self._inner["id"] = id_


class _Extension(_Extension, _STIXBase21):
    extension_type = None


class _DomainObject(_DomainObject, _STIXBase21):
    pass


class _RelationshipObject(_RelationshipObject, _STIXBase21):
    pass
