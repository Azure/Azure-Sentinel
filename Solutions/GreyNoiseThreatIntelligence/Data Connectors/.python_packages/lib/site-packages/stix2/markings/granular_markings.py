"""Functions for working with STIX2 granular markings."""

from stix2 import exceptions
from stix2.markings import utils
from stix2.utils import is_marking
from stix2.versioning import new_version


def get_markings(obj, selectors, inherited=False, descendants=False, marking_ref=True, lang=True):
    """
    Get all granular markings associated to with the properties.

    Args:
        obj: An SDO or SRO object.
        selectors: string or list of selector strings relative to the SDO or
            SRO in which the properties appear.
        inherited (bool): If True, include markings inherited relative to the
            properties.
        descendants (bool): If True, include granular markings applied to any
            children relative to the properties.
        marking_ref (bool): If False, excludes markings that use
            ``marking_ref`` property.
        lang (bool): If False, excludes markings that use ``lang`` property.

    Raises:
        InvalidSelectorError: If `selectors` fail validation.

    Returns:
        list: Marking identifiers that matched the selectors expression.

    """
    selectors = utils.convert_to_list(selectors)
    utils.validate(obj, selectors)

    granular_markings = obj.get('granular_markings', [])

    if not granular_markings:
        return []

    results = set()

    for marking in granular_markings:
        for user_selector in selectors:
            for marking_selector in marking.get('selectors', []):
                if any([
                    (user_selector == marking_selector),  # Catch explicit selectors.
                    (user_selector.startswith(marking_selector) and inherited),  # Catch inherited selectors.
                    (marking_selector.startswith(user_selector) and descendants),
                ]):  # Catch descendants selectors
                    ref = marking.get('marking_ref')
                    lng = marking.get('lang')

                    if ref and marking_ref:
                        results.add(ref)
                    if lng and lang:
                        results.add(lng)

    return list(results)


def set_markings(obj, marking, selectors, marking_ref=True, lang=True):
    """
    Remove all granular markings associated with selectors and append a new
    granular marking. Refer to `clear_markings` and `add_markings` for details.

    Args:
        obj: An SDO or SRO object.
        selectors: string or list of selector strings relative to the SDO or
            SRO in which the properties appear.
        marking: identifier or list of marking identifiers that apply to the
            properties selected by `selectors`.
        marking_ref (bool): If False, markings that use the ``marking_ref``
            property will not be removed.
        lang (bool): If False, markings that use the ``lang`` property
            will not be removed.

    Returns:
        A new version of the given SDO or SRO with specified markings removed
        and new ones added.

    """
    obj = clear_markings(obj, selectors, marking_ref, lang)
    return add_markings(obj, marking, selectors)


def remove_markings(obj, marking, selectors):
    """
    Remove a granular marking from the granular_markings collection. The method
    makes a best-effort attempt to distinguish between a marking-definition
    or language granular marking.

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

    """
    selectors = utils.convert_to_list(selectors)
    marking = utils.convert_to_marking_list(marking)
    utils.validate(obj, selectors)

    granular_markings = obj.get('granular_markings')

    if not granular_markings:
        return obj

    granular_markings = utils.expand_markings(granular_markings)

    to_remove = []
    for m in marking:
        if is_marking(m):
            to_remove.append({'marking_ref': m, 'selectors': selectors})
        else:
            to_remove.append({'lang': m, 'selectors': selectors})

    remove = utils.build_granular_marking(to_remove).get('granular_markings')

    if not any(marking in granular_markings for marking in remove):
        raise exceptions.MarkingNotFoundError(obj, remove)

    granular_markings = [
        m for m in granular_markings if m not in remove
    ]

    granular_markings = utils.compress_markings(granular_markings)

    if granular_markings:
        return new_version(obj, granular_markings=granular_markings, allow_custom=True)
    else:
        return new_version(obj, granular_markings=None, allow_custom=True)


def add_markings(obj, marking, selectors):
    """
    Append a granular marking to the granular_markings collection. The method
    makes a best-effort attempt to distinguish between a marking-definition
    or language granular marking.

    Args:
        obj: An SDO or SRO object.
        marking: identifier or list of marking identifiers that apply to the
            properties selected by `selectors`.
        selectors: list of type string, selectors must be relative to the TLO
            in which the properties appear.

    Raises:
        InvalidSelectorError: If `selectors` fail validation.

    Returns:
        A new version of the given SDO or SRO with specified markings added.

    """
    selectors = utils.convert_to_list(selectors)
    marking = utils.convert_to_marking_list(marking)
    utils.validate(obj, selectors)

    granular_marking = []
    for m in marking:
        if is_marking(m):
            granular_marking.append({'marking_ref': m, 'selectors': sorted(selectors)})
        else:
            granular_marking.append({'lang': m, 'selectors': sorted(selectors)})

    if obj.get('granular_markings'):
        granular_marking.extend(obj.get('granular_markings'))

    granular_marking = utils.expand_markings(granular_marking)
    granular_marking = utils.compress_markings(granular_marking)
    return new_version(obj, granular_markings=granular_marking, allow_custom=True)


def clear_markings(obj, selectors, marking_ref=True, lang=True):
    """
    Remove all granular markings associated with the selectors.

    Args:
        obj: An SDO or SRO object.
        selectors: string or list of selectors strings relative to the SDO or
            SRO in which the properties appear.
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

    """
    selectors = utils.convert_to_list(selectors)
    utils.validate(obj, selectors)

    granular_markings = obj.get('granular_markings')

    if not granular_markings:
        return obj

    granular_markings = utils.expand_markings(granular_markings)

    granular_dict = utils.build_granular_marking([
        {'selectors': selectors, 'marking_ref': 'N/A'},
        {'selectors': selectors, 'lang': 'N/A'},
    ])

    clear = granular_dict.get('granular_markings', [])

    if not any(
        clear_selector in sdo_selectors.get('selectors', [])
        for sdo_selectors in granular_markings
        for clear_marking in clear
        for clear_selector in clear_marking.get('selectors', [])
    ):
        raise exceptions.MarkingNotFoundError(obj, clear)

    for granular_marking in granular_markings:
        for s in selectors:
            if s in granular_marking.get('selectors', []):
                ref = granular_marking.get('marking_ref')
                lng = granular_marking.get('lang')

                if ref and marking_ref:
                    granular_marking['marking_ref'] = ''
                if lng and lang:
                    granular_marking['lang'] = ''

    granular_markings = utils.compress_markings(granular_markings)

    if granular_markings:
        return new_version(obj, granular_markings=granular_markings, allow_custom=True)
    else:
        return new_version(obj, granular_markings=None, allow_custom=True)


def is_marked(obj, marking=None, selectors=None, inherited=False, descendants=False):
    """
    Check if field is marked by any marking or by specific marking(s).

    Args:
        obj: An SDO or SRO object.
        marking: identifier or list of marking identifiers that apply to the
            properties selected by `selectors`.
        selectors (bool): string or list of selectors strings relative to the
            SDO or SRO in which the properties appear.
        inherited (bool): If True, return markings inherited from the given
            selector.
        descendants (bool): If True, return granular markings applied to any
            children of the given selector.

    Raises:
        InvalidSelectorError: If `selectors` fail validation.

    Returns:
        bool: True if ``selectors`` is found on internal SDO or SRO collection.
            False otherwise.

    Note:
        When a list of marking identifiers is provided, if ANY of the provided
        marking identifiers match, True is returned.

    """
    if selectors is None:
        raise TypeError("Required argument 'selectors' must be provided")

    selectors = utils.convert_to_list(selectors)
    marking = utils.convert_to_marking_list(marking)
    utils.validate(obj, selectors)

    granular_markings = obj.get('granular_markings', [])

    marked = False
    markings = set()

    for granular_marking in granular_markings:
        for user_selector in selectors:
            for marking_selector in granular_marking.get('selectors', []):

                if any([
                    (user_selector == marking_selector),  # Catch explicit selectors.
                    (user_selector.startswith(marking_selector) and inherited),  # Catch inherited selectors.
                    (marking_selector.startswith(user_selector) and descendants),
                ]):  # Catch descendants selectors
                    marking_ref = granular_marking.get('marking_ref', '')
                    lang = granular_marking.get('lang', '')

                    if marking and any(x == marking_ref for x in marking):
                        markings.update([marking_ref])
                    if marking and any(x == lang for x in marking):
                        markings.update([lang])

                    marked = True

    if marking:
        # All user-provided markings must be found.
        return markings.issuperset(set(marking))

    return marked
