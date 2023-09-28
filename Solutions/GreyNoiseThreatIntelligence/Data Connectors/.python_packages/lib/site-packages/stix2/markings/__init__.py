"""
Functions for working with STIX 2 Data Markings.

These high level functions will operate on both object-level markings and
granular markings unless otherwise noted in each of the functions.

Note:
    These functions are also available as methods on SDOs, SROs, and Marking
    Definitions. The corresponding methods on those classes are identical to
    these functions except that the `obj` parameter is omitted.

.. autosummary::
   :toctree: markings

   granular_markings
   object_markings
   utils

|
"""

from stix2.markings import granular_markings, object_markings


def get_markings(obj, selectors=None, inherited=False, descendants=False, marking_ref=True, lang=True):
    """
    Get all markings associated to the field(s) specified by selectors.

    Args:
        obj: An SDO or SRO object.
        selectors: string or list of selectors strings relative to the SDO or
            SRO in which the properties appear.
        inherited (bool): If True, include object level markings and granular
            markings inherited relative to the properties.
        descendants (bool): If True, include granular markings applied to any
            children relative to the properties.
        marking_ref (bool): If False, excludes markings that use
            ``marking_ref`` property.
        lang (bool): If False, excludes markings that use ``lang`` property.

    Returns:
        list: Marking identifiers that matched the selectors expression.

    Note:
        If ``selectors`` is None, operation will be performed only on object
        level markings.

    """
    if selectors is None:
        return object_markings.get_markings(obj)

    results = granular_markings.get_markings(
        obj,
        selectors,
        inherited,
        descendants,
        marking_ref,
        lang,
    )

    if inherited:
        results.extend(object_markings.get_markings(obj))

    return list(set(results))


def set_markings(obj, marking, selectors=None, marking_ref=True, lang=True):
    """
    Remove all markings associated with selectors and appends a new granular
    marking. Refer to `clear_markings` and `add_markings` for details.

    Args:
        obj: An SDO or SRO object.
        marking: identifier or list of marking identifiers that apply to the
            properties selected by `selectors`.
        selectors: string or list of selectors strings relative to the SDO or
            SRO in which the properties appear.
        marking_ref (bool): If False, markings that use the ``marking_ref``
            property will not be removed.
        lang (bool): If False, markings that use the ``lang`` property
            will not be removed.

    Returns:
        A new version of the given SDO or SRO with specified markings removed
        and new ones added.

    Note:
        If ``selectors`` is None, operations will be performed on object level
        markings. Otherwise on granular markings.

    """
    if selectors is None:
        return object_markings.set_markings(obj, marking)
    else:
        return granular_markings.set_markings(obj, marking, selectors, marking_ref, lang)


def remove_markings(obj, marking, selectors=None):
    """
    Remove a marking from this object.

    Args:
        obj: An SDO or SRO object.
        marking: identifier or list of marking identifiers that apply to the
            properties selected by `selectors`.
        selectors: string or list of selectors strings relative to the SDO or
            SRO in which the properties appear.

    Raises:
        InvalidSelectorError: If `selectors` fail validation.
        MarkingNotFoundError: If markings to remove are not found on
            the provided SDO or SRO.

    Returns:
        A new version of the given SDO or SRO with specified markings removed.

    Note:
        If ``selectors`` is None, operations will be performed on object level
        markings. Otherwise on granular markings.

   """
    if selectors is None:
        return object_markings.remove_markings(obj, marking)
    else:
        return granular_markings.remove_markings(obj, marking, selectors)


def add_markings(obj, marking, selectors=None):
    """
    Append a marking to this object.

    Args:
        obj: An SDO or SRO object.
        marking: identifier or list of marking identifiers that apply to the
            properties selected by `selectors`.
        selectors: string or list of selectors strings relative to the SDO or
            SRO in which the properties appear.

    Raises:
        InvalidSelectorError: If `selectors` fail validation.

    Returns:
        A new version of the given SDO or SRO with specified markings added.

    Note:
        If ``selectors`` is None, operations will be performed on object level
        markings. Otherwise on granular markings.

    """
    if selectors is None:
        return object_markings.add_markings(obj, marking)
    else:
        return granular_markings.add_markings(obj, marking, selectors)


def clear_markings(obj, selectors=None, marking_ref=True, lang=True):
    """
    Remove all markings associated with the selectors.

    Args:
        obj: An SDO or SRO object.
        selectors: string or list of selectors strings relative to the SDO or
            SRO in which the field(s) appear(s).
        marking_ref (bool): If False, markings that use the ``marking_ref``
            property will not be removed.
        lang (bool): If False, markings that use the ``lang`` property
            will not be removed.

    Raises:
        InvalidSelectorError: If `selectors` fail validation.
        MarkingNotFoundError: If markings to remove are not found on
            the provided SDO or SRO.

    Returns:
        A new version of the given SDO or SRO with specified markings cleared.

    Note:
        If ``selectors`` is None, operations will be performed on object level
        markings. Otherwise on granular markings.

    """
    if selectors is None:
        return object_markings.clear_markings(obj)
    else:
        return granular_markings.clear_markings(obj, selectors, marking_ref, lang)


def is_marked(obj, marking=None, selectors=None, inherited=False, descendants=False):
    """
    Check if field(s) is marked by any marking or by specific marking(s).

    Args:
        obj: An SDO or SRO object.
        marking: identifier or list of marking identifiers that apply to the
            properties selected by `selectors`.
        selectors: string or list of selectors strings relative to the SDO or
            SRO in which the field(s) appear(s).
        inherited (bool): If True, include object level markings and granular
            markings inherited to determine if the properties is/are marked.
        descendants (bool): If True, include granular markings applied to any
            children of the given selector to determine if the properties
            is/are marked.

    Returns:
        bool: True if ``selectors`` is found on internal SDO or SRO collection.
            False otherwise.

    Note:
        When a list of marking identifiers is provided, if ANY of the provided
        marking identifiers match, True is returned.

        If ``selectors`` is None, operation will be performed only on object
        level markings.

    """
    if selectors is None:
        return object_markings.is_marked(obj, marking)

    result = granular_markings.is_marked(
        obj,
        marking,
        selectors,
        inherited,
        descendants,
    )

    if inherited:
        granular_marks = granular_markings.get_markings(obj, selectors)
        object_marks = object_markings.get_markings(obj)

        if granular_marks:
            result = granular_markings.is_marked(
                obj,
                granular_marks,
                selectors,
                inherited,
                descendants,
            )

        result = result or object_markings.is_marked(obj, object_marks)

    return result


class _MarkingsMixin(object):
    pass


# Note that all of these methods will return a new object because of immutability
_MarkingsMixin.get_markings = get_markings
_MarkingsMixin.set_markings = set_markings
_MarkingsMixin.remove_markings = remove_markings
_MarkingsMixin.add_markings = add_markings
_MarkingsMixin.clear_markings = clear_markings
_MarkingsMixin.is_marked = is_marked
