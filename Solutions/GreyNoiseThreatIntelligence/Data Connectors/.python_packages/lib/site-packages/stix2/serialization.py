"""STIX2 core serialization methods."""

import datetime as dt
import io

import simplejson as json

import stix2.base

from .utils import format_datetime


class STIXJSONEncoder(json.JSONEncoder):
    """Custom JSONEncoder subclass for serializing Python ``stix2`` objects.

    If an optional property with a default value specified in the STIX 2 spec
    is set to that default value, it will be left out of the serialized output.

    An example of this type of property include the ``revoked`` common property.
    """

    def default(self, obj):
        if isinstance(obj, (dt.date, dt.datetime)):
            return format_datetime(obj)
        elif isinstance(obj, stix2.base._STIXBase):
            tmp_obj = dict(obj)
            for prop_name in obj._defaulted_optional_properties:
                del tmp_obj[prop_name]
            return tmp_obj
        else:
            return super(STIXJSONEncoder, self).default(obj)


class STIXJSONIncludeOptionalDefaultsEncoder(json.JSONEncoder):
    """Custom JSONEncoder subclass for serializing Python ``stix2`` objects.

    Differs from ``STIXJSONEncoder`` in that if an optional property with a default
    value specified in the STIX 2 spec is set to that default value, it will be
    included in the serialized output.
    """

    def default(self, obj):
        if isinstance(obj, (dt.date, dt.datetime)):
            return format_datetime(obj)
        elif isinstance(obj, stix2.base._STIXBase):
            return dict(obj)
        else:
            return super(STIXJSONIncludeOptionalDefaultsEncoder, self).default(obj)


def serialize(obj, pretty=False, include_optional_defaults=False, **kwargs):
    """
    Serialize a STIX object.

    Args:
        obj: The STIX object to be serialized.
        pretty (bool): If True, output properties following the STIX specs
            formatting. This includes indentation. Refer to notes for more
            details. (Default: ``False``)
        include_optional_defaults (bool): Determines whether to include
            optional properties set to the default value defined in the spec.
        **kwargs: The arguments for a json.dumps() call.

    Returns:
        str: The serialized JSON object.

    Note:
        The argument ``pretty=True`` will output the STIX object following
        spec order. Using this argument greatly impacts object serialization
        performance. If your use case is centered across machine-to-machine
        operation it is recommended to set ``pretty=False``.

        When ``pretty=True`` the following key-value pairs will be added or
        overridden: indent=4, separators=(",", ": "), item_sort_key=sort_by.
    """
    with io.StringIO() as fp:
        fp_serialize(obj, fp, pretty, include_optional_defaults, **kwargs)
        return fp.getvalue()


def fp_serialize(obj, fp, pretty=False, include_optional_defaults=False, **kwargs):
    """
    Serialize a STIX object to ``fp`` (a text stream file-like supporting object).

    Args:
        obj: The STIX object to be serialized.
        fp: A text stream file-like object supporting ``.write()``.
        pretty (bool): If True, output properties following the STIX specs
            formatting. This includes indentation. Refer to notes for more
            details. (Default: ``False``)
        include_optional_defaults (bool): Determines whether to include
            optional properties set to the default value defined in the spec.
        **kwargs: The arguments for a json.dumps() call.

    Returns:
        None

    Note:
        The argument ``pretty=True`` will output the STIX object following
        spec order. Using this argument greatly impacts object serialization
        performance. If your use case is centered across machine-to-machine
        operation it is recommended to set ``pretty=False``.

        When ``pretty=True`` the following key-value pairs will be added or
        overridden: indent=4, separators=(",", ": "), item_sort_key=sort_by.
    """
    if pretty:
        def sort_by(element):
            return find_property_index(obj, *element)

        kwargs.update({'indent': 4, 'separators': (',', ': '), 'item_sort_key': sort_by})

    if include_optional_defaults:
        json.dump(obj, fp, cls=STIXJSONIncludeOptionalDefaultsEncoder, **kwargs)
    else:
        json.dump(obj, fp, cls=STIXJSONEncoder, **kwargs)


def _find(seq, val):
    """
    Search sequence 'seq' for val.  This behaves like str.find(): if not found,
    -1 is returned instead of throwing an exception.

    Args:
        seq: The sequence to search
        val: The value to search for

    Returns:
        int: The index of the value if found, or -1 if not found
    """
    try:
        return seq.index(val)
    except ValueError:
        return -1


def _find_property_in_seq(seq, search_key, search_value):
    """
    Helper for find_property_index(): search for the property in all elements
    of the given sequence.

    Args:
        seq: The sequence
        search_key: Property name to find
        search_value: Property value to find

    Returns:
        int: A property index, or -1 if the property was not found
    """
    idx = -1
    for elem in seq:
        idx = find_property_index(elem, search_key, search_value)
        if idx >= 0:
            break

    return idx


def find_property_index(obj, search_key, search_value):
    """
    Search (recursively) for the given key and value in the given object.
    Return an index for the key, relative to whatever object it's found in.

    Args:
        obj: The object to search (list, dict, or stix object)
        search_key: A search key
        search_value: A search value

    Returns:
        int: An index; -1 if the key and value aren't found
    """
    # Special-case keys which are numbers-as-strings, e.g. for cyber-observable
    # mappings.  Use the int value of the key as the index.
    if search_key.isdigit():
        return int(search_key)

    if isinstance(obj, stix2.base._STIXBase):
        if search_key in obj and obj[search_key] == search_value:
            idx = _find(list(obj), search_key)
        else:
            idx = _find_property_in_seq(obj.values(), search_key, search_value)
    elif isinstance(obj, dict):
        if search_key in obj and obj[search_key] == search_value:
            idx = _find(sorted(obj), search_key)
        else:
            idx = _find_property_in_seq(obj.values(), search_key, search_value)
    elif isinstance(obj, list):
        idx = _find_property_in_seq(obj, search_key, search_value)
    else:
        # Don't know how to search this type
        idx = -1

    return idx
