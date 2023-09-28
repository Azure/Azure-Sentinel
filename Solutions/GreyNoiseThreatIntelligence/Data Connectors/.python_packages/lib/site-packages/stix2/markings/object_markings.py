"""Functions for working with STIX2 object markings."""

from stix2 import exceptions
from stix2.markings import utils
from stix2.versioning import new_version


def get_markings(obj):
    """
    Get all object level markings from the given SDO or SRO object.

    Args:
        obj: A SDO or SRO object.

    Returns:
        list: Marking identifiers contained in the SDO or SRO. Empty list if no
            markings are present in `object_marking_refs`.

    """
    return obj.get('object_marking_refs', [])


def add_markings(obj, marking):
    """
    Append an object level marking to the object_marking_refs collection.

    Args:
        obj: A SDO or SRO object.
        marking: identifier or list of identifiers to apply SDO or SRO object.

    Returns:
        A new version of the given SDO or SRO with specified markings added.

    """
    marking = utils.convert_to_marking_list(marking)

    object_markings = set(obj.get('object_marking_refs', []) + marking)

    return new_version(obj, object_marking_refs=list(object_markings), allow_custom=True)


def remove_markings(obj, marking):
    """
    Remove an object level marking from the object_marking_refs collection.

    Args:
        obj: A SDO or SRO object.
        marking: identifier or list of identifiers that apply to the
            SDO or SRO object.

    Raises:
        MarkingNotFoundError: If markings to remove are not found on
            the provided SDO or SRO.

    Returns:
        A new version of the given SDO or SRO with specified markings removed.

    """
    marking = utils.convert_to_marking_list(marking)

    object_markings = obj.get('object_marking_refs', [])

    if not object_markings:
        return obj

    if any(x not in obj['object_marking_refs'] for x in marking):
        raise exceptions.MarkingNotFoundError(obj, marking)

    new_markings = [x for x in object_markings if x not in marking]
    if new_markings:
        return new_version(obj, object_marking_refs=new_markings, allow_custom=True)
    else:
        return new_version(obj, object_marking_refs=None, allow_custom=True)


def set_markings(obj, marking):
    """
    Remove all object level markings and append new object level markings to
    the collection. Refer to `clear_markings` and `add_markings` for details.

    Args:
        obj: A SDO or SRO object.
        marking: identifier or list of identifiers to apply in the
            SDO or SRO object.

    Returns:
        A new version of the given SDO or SRO with specified markings removed
        and new ones added.

    """
    return add_markings(clear_markings(obj), marking)


def clear_markings(obj):
    """
    Remove all object level markings from the object_marking_refs collection.

    Args:
        obj: A SDO or SRO object.

    Returns:
        A new version of the given SDO or SRO with object_marking_refs cleared.

    """
    return new_version(obj, object_marking_refs=None, allow_custom=True)


def is_marked(obj, marking=None):
    """
    Check if SDO or SRO is marked by any marking or by specific marking(s).

    Args:
        obj: A SDO or SRO object.
        marking: identifier or list of marking identifiers that apply to the
            SDO or SRO object.

    Returns:
        bool: True if SDO or SRO has object level markings. False otherwise.

    Note:
        When an identifier or list of identifiers is provided, if ANY of the
        provided marking refs match, True is returned.

    """
    marking = utils.convert_to_marking_list(marking)
    object_markings = obj.get('object_marking_refs', [])

    if marking:
        return any(x in object_markings for x in marking)
    else:
        return bool(object_markings)
