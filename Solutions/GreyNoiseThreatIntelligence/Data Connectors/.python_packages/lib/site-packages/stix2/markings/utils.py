"""Utility functions for STIX2 data markings."""

import collections

from stix2 import exceptions, utils


def _evaluate_expression(obj, selector):
    """Walk an SDO or SRO generating selectors to match against ``selector``.

    If a match is found and the the value of this property is present in the
    objects. Matching value of the property will be returned.

    Args:
        obj: An SDO or SRO object.
        selector (str): A string following the selector syntax.

    Returns:
        list: Values contained in matching property. Otherwise empty list.

    """
    for items, value in iterpath(obj):
        path = '.'.join(items)

        if path == selector and value:
            return [value]

    return []


def _validate_selector(obj, selector):
    """Evaluate each selector against an object."""
    results = list(_evaluate_expression(obj, selector))

    if len(results) >= 1:
        return True


def _get_marking_id(marking):
    if type(marking).__name__ == 'MarkingDefinition':  # avoid circular import
        return marking.id
    return marking


def validate(obj, selectors):
    """Given an SDO or SRO, check that each selector is valid."""
    if selectors:
        for s in selectors:
            if not _validate_selector(obj, s):
                raise exceptions.InvalidSelectorError(obj, s)
        return

    raise exceptions.InvalidSelectorError(obj, selectors)


def convert_to_list(data):
    """Convert input into a list for further processing."""
    if data is not None:
        if isinstance(data, list):
            return data
        else:
            return [data]


def convert_to_marking_list(data):
    """Convert input into a list of marking identifiers."""
    if data is not None:
        if isinstance(data, list):
            return [_get_marking_id(x) for x in data]
        else:
            return [_get_marking_id(data)]


def compress_markings(granular_markings):
    """Compress granular markings list.

    If there is more than one marking identifier matches. It will collapse into
    a single granular marking.

    Example:
        >>> compress_markings([
        ...     {
        ...         "selectors": [
        ...             "description"
        ...         ],
        ...         "marking_ref": "marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9"
        ...     },
        ...     {
        ...         "selectors": [
        ...             "name"
        ...         ],
        ...         "marking_ref": "marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9"
        ...     }
        ... ])
        [
            {
                "selectors": [
                    "description",
                    "name"
                ],
                "marking_ref": "marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9"
            }
        ]

    Args:
        granular_markings: The granular markings list property present in a
            SDO or SRO.

    Returns:
        list: A list with all markings collapsed.

    """
    if not granular_markings:
        return

    map_ = collections.defaultdict(set)

    for granular_marking in granular_markings:
        if granular_marking.get('marking_ref'):
            map_[granular_marking.get('marking_ref')].update(granular_marking.get('selectors'))

        if granular_marking.get('lang'):
            map_[granular_marking.get('lang')].update(granular_marking.get('selectors'))

    compressed = \
        [
            {'marking_ref': item, 'selectors': sorted(selectors)}
            if utils.is_marking(item) else
            {'lang': item, 'selectors': sorted(selectors)}
            for item, selectors in map_.items()
        ]

    return compressed


def expand_markings(granular_markings):
    """Expand granular markings list.

    If there is more than one selector per granular marking. It will be
    expanded using the same marking_ref.

    Example:
        >>> expand_markings([
        ...     {
        ...         "selectors": [
        ...             "description",
        ...             "name"
        ...         ],
        ...         "marking_ref": "marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9"
        ...     }
        ... ])
        [
            {
                "selectors": [
                    "description"
                ],
                "marking_ref": "marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9"
            },
            {
                "selectors": [
                    "name"
                ],
                "marking_ref": "marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9"
            }
        ]

    Args:
        granular_markings: The granular markings list property present in a
            SDO or SRO.

    Returns:
        list: A list with all markings expanded.

    """
    expanded = []

    for marking in granular_markings:
        selectors = marking.get('selectors')
        marking_ref = marking.get('marking_ref')
        lang = marking.get('lang')

        if marking_ref:
            expanded.extend(
                [
                    {'marking_ref': marking_ref, 'selectors': [selector]}
                    for selector in selectors
                ],
            )
        if lang:
            expanded.extend(
                [
                    {'lang': lang, 'selectors': [selector]}
                    for selector in selectors
                ],
            )

    return expanded


def build_granular_marking(granular_marking):
    """Return a dictionary with the required structure for a granular marking.
    """
    return {'granular_markings': expand_markings(granular_marking)}


def iterpath(obj, path=None):
    """Generator which walks the input ``obj`` model.

    Each iteration yields a tuple containing a list of ancestors and the
    property value.

    Args:
        obj: An SDO or SRO object.
        path: None, used recursively to store ancestors.

    Example:
        >>> for item in iterpath(obj):
        >>>     print(item)
        (['type'], 'campaign')
        ...
        (['cybox', 'objects', '[0]', 'hashes', 'sha1'], 'cac35ec206d868b7d7cb0b55f31d9425b075082b')

    Returns:
        tuple: Containing two items: a list of ancestors and the
            property value.

    """
    if path is None:
        path = []

    for varname, varobj in iter(sorted(obj.items())):
        path.append(varname)
        yield (path, varobj)

        if isinstance(varobj, dict):

            for item in iterpath(varobj, path):
                yield item

        elif isinstance(varobj, list):

            for item in varobj:
                index = '[{0}]'.format(varobj.index(item))
                path.append(index)

                yield (path, item)

                if isinstance(item, dict):
                    for descendant in iterpath(item, path):
                        yield descendant

                path.pop()

        path.pop()


def check_tlp_marking(marking_obj, spec_version):
    # Specific TLP Marking validation case.

    if marking_obj.get("definition_type", "") == "tlp":
        color = marking_obj["definition"]["tlp"]

        if color == "white":
            if spec_version == '2.0':
                w = (
                    '{"created": "2017-01-20T00:00:00.000Z", "definition": {"tlp": "white"}, "definition_type": "tlp",'
                    ' "id": "marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9", "type": "marking-definition"}'
                )
            else:
                w = (
                    '{"created": "2017-01-20T00:00:00.000Z", "definition": {"tlp": "white"}, "definition_type": "tlp",'
                    ' "id": "marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9", "name": "TLP:WHITE",'
                    ' "type": "marking-definition", "spec_version": "2.1"}'
                )
            if marking_obj["id"] != "marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9":
                raise exceptions.TLPMarkingDefinitionError(marking_obj["id"], w)
            elif utils.format_datetime(marking_obj["created"]) != "2017-01-20T00:00:00.000Z":
                raise exceptions.TLPMarkingDefinitionError(utils.format_datetime(marking_obj["created"]), w)

        elif color == "green":
            if spec_version == '2.0':
                g = (
                    '{"created": "2017-01-20T00:00:00.000Z", "definition": {"tlp": "green"}, "definition_type": "tlp",'
                    ' "id": "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da", "type": "marking-definition"}'
                )
            else:
                g = (
                    '{"created": "2017-01-20T00:00:00.000Z", "definition": {"tlp": "green"}, "definition_type": "tlp",'
                    ' "id": "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da", "name": "TLP:GREEN",'
                    ' "type": "marking-definition", "spec_version": "2.1"}'
                )
            if marking_obj["id"] != "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da":
                raise exceptions.TLPMarkingDefinitionError(marking_obj["id"], g)
            elif utils.format_datetime(marking_obj["created"]) != "2017-01-20T00:00:00.000Z":
                raise exceptions.TLPMarkingDefinitionError(utils.format_datetime(marking_obj["created"]), g)

        elif color == "amber":
            if spec_version == '2.0':
                a = (
                    '{"created": "2017-01-20T00:00:00.000Z", "definition": {"tlp": "amber"}, "definition_type": "tlp",'
                    ' "id": "marking-definition--f88d31f6-486f-44da-b317-01333bde0b82", "type": "marking-definition"}'
                )
            else:
                a = (
                    '{"created": "2017-01-20T00:00:00.000Z", "definition": {"tlp": "amber"}, "definition_type": "tlp",'
                    ' "id": "marking-definition--f88d31f6-486f-44da-b317-01333bde0b82", "name": "TLP:AMBER",'
                    ' "type": "marking-definition", "spec_version": "2.1"}'
                )
            if marking_obj["id"] != "marking-definition--f88d31f6-486f-44da-b317-01333bde0b82":
                raise exceptions.TLPMarkingDefinitionError(marking_obj["id"], a)
            elif utils.format_datetime(marking_obj["created"]) != "2017-01-20T00:00:00.000Z":
                raise exceptions.TLPMarkingDefinitionError(utils.format_datetime(marking_obj["created"]), a)

        elif color == "red":
            if spec_version == '2.0':
                r = (
                    '{"created": "2017-01-20T00:00:00.000Z", "definition": {"tlp": "red"}, "definition_type": "tlp",'
                    ' "id": "marking-definition--5e57c739-391a-4eb3-b6be-7d15ca92d5ed", "type": "marking-definition"}'
                )
            else:
                r = (
                    '{"created": "2017-01-20T00:00:00.000Z", "definition": {"tlp": "red"}, "definition_type": "tlp",'
                    ' "id": "marking-definition--5e57c739-391a-4eb3-b6be-7d15ca92d5ed", "name": "TLP:RED",'
                    ' "type": "marking-definition", "spec_version": "2.1"}'
                )
            if marking_obj["id"] != "marking-definition--5e57c739-391a-4eb3-b6be-7d15ca92d5ed":
                raise exceptions.TLPMarkingDefinitionError(marking_obj["id"], r)
            elif utils.format_datetime(marking_obj["created"]) != "2017-01-20T00:00:00.000Z":
                raise exceptions.TLPMarkingDefinitionError(utils.format_datetime(marking_obj["created"]), r)

        else:
            raise exceptions.TLPMarkingDefinitionError(marking_obj["id"], "Does not match any TLP Marking definition")
