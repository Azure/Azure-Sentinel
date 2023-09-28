"""STIX2 core versioning methods."""

from collections.abc import Mapping
import copy
import datetime as dt
import itertools
import uuid

import stix2.base
import stix2.registry
from stix2.utils import (
    detect_spec_version, get_timestamp, is_sco, parse_into_datetime,
)
import stix2.v20

from .exceptions import (
    InvalidValueError, ObjectNotVersionableError, RevokeError,
    TypeNotVersionableError, UnmodifiablePropertyError,
)

# STIX object properties that cannot be modified
STIX_UNMOD_PROPERTIES = ['created', 'created_by_ref', 'id', 'type']
_VERSIONING_PROPERTIES = {"created", "modified", "revoked"}


def _fudge_modified(old_modified, new_modified, use_stix21):
    """
    Ensures a new modified timestamp is newer than the old.  When they are
    too close together, new_modified must be pushed further ahead to ensure
    it is distinct and later, after JSON serialization (which may mean it's
    actually being pushed a little ways into the future).  JSON serialization
    can remove precision, which can cause distinct timestamps to accidentally
    become equal, if we're not careful.

    :param old_modified: A previous "modified" timestamp, as a datetime object
    :param new_modified: A candidate new "modified" timestamp, as a datetime
        object
    :param use_stix21: Whether to use STIX 2.1+ versioning timestamp precision
        rules (boolean).  This is important so that we are aware of how
        timestamp precision will be truncated, so we know how close together
        the timestamps can be, and how far ahead to potentially push the new
        one.
    :return: A suitable new "modified" timestamp.  This may be different from
        what was passed in, if it had to be pushed ahead.
    """
    if use_stix21:
        # 2.1+: we can use full precision
        if new_modified <= old_modified:
            new_modified = old_modified + dt.timedelta(microseconds=1)
    else:
        # 2.0: we must use millisecond precision
        one_ms = dt.timedelta(milliseconds=1)
        if new_modified - old_modified < one_ms:
            new_modified = old_modified + one_ms

    return new_modified


def _get_stix_version(data):
    """
    Bit of factored out functionality for getting/detecting the STIX version
    of the given value.

    :param data: An object, e.g. _STIXBase instance or dict
    :return: The STIX version as a string in "X.Y" notation, or None if the
        version could not be determined.
    """
    stix_version = None
    if isinstance(data, Mapping):

        # First, determine spec version.  It's easy for our stix2 objects; more
        # work for dicts.
        if isinstance(data, stix2.v20._STIXBase20):
            stix_version = "2.0"
        elif isinstance(data, stix2.v21._STIXBase21):
            stix_version = "2.1"
        elif isinstance(data, dict):
            stix_version = detect_spec_version(data)

    return stix_version


def _is_versionable_type(data):
    """
    Determine whether type of the given object is versionable.  This check is
    done on the basis of support for three properties for the object type:
    "created", "modified", and "revoked".  If all three are supported, the
    object type is versionable; otherwise it is not.  Dicts must have a "type"
    property.  This is used in STIX version detection and to determine a
    complete set of supported properties for the type.

    If a dict is passed whose "type" is unregistered, then this library has no
    knowledge of the type.  It can't determine what properties are "supported".
    This function will be lax and treat the type as versionable.

    Note that this support check is not sufficient for creating a new object
    version.  Support for the versioning properties does not mean that
    sufficient properties are actually present on the object.

    Also, detect whether it represents a STIX 2.1 or greater spec version.

    :param data: The object to check.  Must be either a stix object, or a dict
        with a "type" property.
    :return: A 2-tuple: the first element is True if the object is versionable
        and False if not; the second is the STIX version as a string in "X.Y"
        notation.
    """

    is_versionable = False
    stix_version = None

    if isinstance(data, Mapping):
        # First, determine spec version
        stix_version = _get_stix_version(data)

        # Then, determine versionability.
        if isinstance(data, stix2.base._STIXBase):
            is_versionable = _VERSIONING_PROPERTIES.issubset(
                data._properties,
            )

        elif isinstance(data, dict):
            # Tougher to handle dicts.  We need to consider STIX version,
            # map to a registered class, and from that get a more complete
            # picture of its properties.

            cls = stix2.registry.class_for_type(data.get("type"), stix_version)
            if cls:
                is_versionable = _VERSIONING_PROPERTIES.issubset(
                    cls._properties,
                )

            else:
                # The type is not registered, so we have no knowledge of
                # what properties are supported.  Let's be lax and let them
                # version it.
                is_versionable = True

    return is_versionable, stix_version


def _check_versionable_object(data):
    """
    Determine whether there are or may be sufficient properties present on
    an object to allow versioning.  Raises an exception if the object can't be
    versioned.

    Also detect STIX spec version.

    :param data: The object to check, e.g. dict with a "type" property, or
        _STIXBase instance
    :return: True if the object is STIX 2.1+, or False if not
    :raises TypeNotVersionableError: If the object didn't have the versioning
        properties and the type was found to not support them
    :raises ObjectNotVersionableError: If the type was found to support
        versioning but there were insufficient properties on the object
    """
    if isinstance(data, Mapping):
        if data.keys() >= _VERSIONING_PROPERTIES:
            # If the properties all already exist in the object, assume they
            # are either supported by the type, or are custom properties, and
            # allow versioning.
            stix_version = _get_stix_version(data)

        else:
            is_versionable_type, stix_version = _is_versionable_type(data)
            if is_versionable_type:
                # The type supports the versioning properties (or we don't
                # recognize it and just assume it does).  The question shifts
                # to whether the object has sufficient properties to create a
                # new version.  Just require "created" for now.  We need at
                # least that as a starting point for new version timestamps.
                is_versionable = "created" in data

                if not is_versionable:
                    raise ObjectNotVersionableError(data)
            else:
                raise TypeNotVersionableError(data)

    else:
        raise TypeNotVersionableError(data)

    return stix_version


def new_version(data, allow_custom=None, **kwargs):
    """
    Create a new version of a STIX object, by modifying properties and
    updating the ``modified`` property.

    :param data: The object to create a new version of.  Maybe a stix2 object
        or dict.
    :param allow_custom: Whether to allow custom properties on the new object.
        If True, allow them (regardless of whether the original had custom
        properties); if False disallow them; if None, auto-detect from the
        object: if it has custom properties, allow them in the new version,
        otherwise don't allow them.
    :param kwargs: The properties to change.  Setting to None requests property
        removal.
    :return: The new object.
    """

    stix_version = _check_versionable_object(data)

    if data.get('revoked'):
        raise RevokeError("new_version")
    try:
        new_obj_inner = copy.deepcopy(data._inner)
    except AttributeError:
        new_obj_inner = copy.deepcopy(data)

    # Make sure certain properties aren't trying to change
    # ID contributing properties of 2.1+ SCOs may also not change if a UUIDv5
    # is in use (depending on whether they were used to create it... but they
    # probably were).  That would imply an ID change, which is not allowed
    # across versions.
    sco_locked_props = []
    if is_sco(data, "2.1"):
        uuid_ = uuid.UUID(data["id"][-36:])
        if uuid_.variant == uuid.RFC_4122 and uuid_.version == 5:
            if isinstance(data, stix2.base._Observable):
                cls = data.__class__
            else:
                cls = stix2.registry.class_for_type(
                    data["type"], stix_version, "observables",
                )

            sco_locked_props = cls._id_contributing_properties

    unchangable_properties = set()
    for prop in itertools.chain(STIX_UNMOD_PROPERTIES, sco_locked_props):
        if prop in kwargs:
            unchangable_properties.add(prop)
    if unchangable_properties:
        raise UnmodifiablePropertyError(unchangable_properties)

    # Different versioning precision rules in STIX 2.0 vs 2.1, so we need
    # to know which rules to apply.
    precision_constraint = "min" if stix_version == "2.1" else "exact"

    old_modified = data.get("modified") or data.get("created")
    old_modified = parse_into_datetime(
        old_modified, precision="millisecond",
        precision_constraint=precision_constraint,
    )

    cls = type(data)
    if 'modified' in kwargs:
        new_modified = parse_into_datetime(
            kwargs['modified'], precision='millisecond',
            precision_constraint=precision_constraint,
        )
        if new_modified <= old_modified:
            raise InvalidValueError(
                cls, 'modified',
                "The new modified datetime cannot be before than or equal to the current modified datetime."
                "It cannot be equal, as according to STIX 2 specification, objects that are different "
                "but have the same id and modified timestamp do not have defined consumer behavior.",
            )

    else:
        new_modified = get_timestamp()
        new_modified = _fudge_modified(
            old_modified, new_modified, stix_version != "2.0",
        )

        kwargs['modified'] = new_modified

    new_obj_inner.update(kwargs)

    # Set allow_custom appropriately if versioning an object.  We will ignore
    # it for dicts.
    if isinstance(data, stix2.base._STIXBase):
        if allow_custom is None:
            new_obj_inner["allow_custom"] = data.has_custom
        else:
            new_obj_inner["allow_custom"] = allow_custom

    # Exclude properties with a value of 'None' in case data is not an instance of a _STIXBase subclass
    return cls(**{k: v for k, v in new_obj_inner.items() if v is not None})


def revoke(data):
    """Revoke a STIX object.

    Returns:
        A new version of the object with ``revoked`` set to ``True``.
    """
    if not isinstance(data, Mapping):
        raise ValueError(
            "cannot revoke object of this type! Try a dictionary "
            "or instance of an SDO or SRO class.",
        )

    if data.get('revoked'):
        raise RevokeError("revoke")
    return new_version(data, revoked=True)


def remove_custom_stix(stix_obj):
    """Remove any custom STIX objects or properties.

    Warnings:
        This function is a best effort utility, in that it will remove custom
        objects and properties based on the type names; i.e. if "x-" prefixes
        object types, and "x\\_" prefixes property types. According to the
        STIX2 spec, those naming conventions are a SHOULDs not MUSTs, meaning
        that valid custom STIX content may ignore those conventions and in
        effect render this utility function invalid when used on that STIX
        content.

    Args:
        stix_obj (dict OR python-stix obj): a single python-stix object
                                             or dict of a STIX object

    Returns:
        A new version of the object with any custom content removed
    """

    if stix_obj['type'].startswith('x-'):
        # if entire object is custom, discard
        return None

    custom_props = {
        k: None
        for k in stix_obj if k.startswith("x_")
    }

    if custom_props:
        new_obj = new_version(stix_obj, allow_custom=False, **custom_props)

        return new_obj

    else:
        return stix_obj
