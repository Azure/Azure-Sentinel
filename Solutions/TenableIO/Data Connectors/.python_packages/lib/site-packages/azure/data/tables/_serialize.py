# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from binascii import hexlify
from typing import Dict
from uuid import UUID
from datetime import datetime
from math import isnan
from enum import Enum
import sys

import six
from azure.core import MatchConditions
from azure.core.exceptions import raise_with_traceback

from ._entity import EdmType
from ._common_conversion import _encode_base64, _to_utc_datetime
from ._error import _ERROR_VALUE_TOO_LARGE, _ERROR_TYPE_NOT_SUPPORTED


def _get_match_headers(etag, match_condition):
    if match_condition == MatchConditions.IfNotModified:
        if not etag:
            raise ValueError("IfNotModified must be specified with etag.")
        return etag
    if match_condition == MatchConditions.Unconditionally:
        if etag:
            raise ValueError("Etag is not supported for an Unconditional operation.")
        return "*"
    raise ValueError("Unsupported match condition: {}".format(match_condition))


def _parameter_filter_substitution(parameters, query_filter):
    # type: (Dict[str, str], str) -> str
    """Replace user defined parameter in filter
    :param parameters: User defined parameters
    :param str query_filter: Filter for querying
    """
    if parameters:
        filter_strings = query_filter.split(' ')
        for index, word in enumerate(filter_strings):
            if word[0] == u'@':
                val = parameters[word[1:]]
                if val in [True, False]:
                    filter_strings[index] = str(val).lower()
                elif isinstance(val, (float)):
                    filter_strings[index] = str(val)
                elif isinstance(val, six.integer_types):
                    if val.bit_length() <= 32:
                        filter_strings[index] = str(val)
                    else:
                        filter_strings[index] = "{}L".format(str(val))
                elif isinstance(val, datetime):
                    filter_strings[index] = "datetime'{}'".format(_to_utc_datetime(val))
                elif isinstance(val, UUID):
                    filter_strings[index] = "guid'{}'".format(str(val))
                elif isinstance(val, six.binary_type):
                    v = str(hexlify(val))
                    if v[0] == 'b': # Python 3 adds a 'b' and quotations, python 2.7 does neither
                        v = v[2:-1]
                    filter_strings[index] = "X'{}'".format(v)
                else:
                    filter_strings[index] = "'{}'".format(val.replace("'", "''"))
        return ' '.join(filter_strings)
    return query_filter


def _to_entity_binary(value):
    return EdmType.BINARY, _encode_base64(value)


def _to_entity_bool(value):
    return None, value


def _to_entity_datetime(value):
    if isinstance(value, str):
        # Pass a serialized datetime straight through
        return EdmType.DATETIME, value
    try:
        # Check is this is a 'round-trip' datetime, and if so
        # pass through the original value.
        if value.tables_service_value:
            return EdmType.DATETIME, value.tables_service_value
    except AttributeError:
        pass
    return EdmType.DATETIME, _to_utc_datetime(value)


def _to_entity_float(value):
    if isnan(value):
        return EdmType.DOUBLE, "NaN"
    if value == float("inf"):
        return EdmType.DOUBLE, "Infinity"
    if value == float("-inf"):
        return EdmType.DOUBLE, "-Infinity"
    return EdmType.DOUBLE, value


def _to_entity_guid(value):
    return EdmType.GUID, str(value)


def _to_entity_int32(value):
    value = int(value)
    if value >= 2 ** 31 or value < -(2 ** 31):
        raise TypeError(_ERROR_VALUE_TOO_LARGE.format(str(value), EdmType.INT32))
    return None, value


def _to_entity_int64(value):
    if sys.version_info < (3,):
        ivalue = int(value)
    else:
        ivalue = int(value)
    if ivalue >= 2 ** 63 or ivalue < -(2 ** 63):
        raise TypeError(_ERROR_VALUE_TOO_LARGE.format(str(value), EdmType.INT64))
    return EdmType.INT64, str(value)


def _to_entity_str(value):
    return EdmType.STRING, value


def _to_entity_none(value):  # pylint: disable=unused-argument
    return None, None


# Conversion from Python type to a function which returns a tuple of the
# type string and content string.
_PYTHON_TO_ENTITY_CONVERSIONS = {
    int: _to_entity_int32,
    bool: _to_entity_bool,
    datetime: _to_entity_datetime,
    float: _to_entity_float,
    UUID: _to_entity_guid,
    Enum: _to_entity_str,
}
try:
    _PYTHON_TO_ENTITY_CONVERSIONS.update(
        {
            unicode: _to_entity_str,  # type: ignore
            str: _to_entity_binary,
            long: _to_entity_int32,  # type: ignore
        }
    )
except NameError:
    _PYTHON_TO_ENTITY_CONVERSIONS.update(
        {
            str: _to_entity_str,
            bytes: _to_entity_binary,
        }
    )

# Conversion from Edm type to a function which returns a tuple of the
# type string and content string.
_EDM_TO_ENTITY_CONVERSIONS = {
    EdmType.BINARY: _to_entity_binary,
    EdmType.BOOLEAN: _to_entity_bool,
    EdmType.DATETIME: _to_entity_datetime,
    EdmType.DOUBLE: _to_entity_float,
    EdmType.GUID: _to_entity_guid,
    EdmType.INT32: _to_entity_int32,
    EdmType.INT64: _to_entity_int64,
    EdmType.STRING: _to_entity_str,
}


def _add_entity_properties(source):
    """Converts an entity object to json to send.
    The entity format is:
    {
       "Address":"Mountain View",
       "Age":23,
       "AmountDue":200.23,
       "CustomerCode@odata.type":"Edm.Guid",
       "CustomerCode":"c9da6455-213d-42c9-9a79-3e9149a57833",
       "CustomerSince@odata.type":"Edm.DateTime",
       "CustomerSince":"2008-07-10T00:00:00",
       "IsActive":true,
       "NumberOfOrders@odata.type":"Edm.Int64",
       "NumberOfOrders":"255",
       "PartitionKey":"mypartitionkey",
       "RowKey":"myrowkey"
    }
    """

    properties = {}

    to_send = dict(source)  # shallow copy

    # set properties type for types we know if value has no type info.
    # if value has type info, then set the type to value.type
    for name, value in to_send.items():
        mtype = ""

        if isinstance(value, Enum):
            try:
                conv = _PYTHON_TO_ENTITY_CONVERSIONS.get(unicode)  # type: ignore
            except NameError:
                conv = _PYTHON_TO_ENTITY_CONVERSIONS.get(str)
            mtype, value = conv(value)
        elif isinstance(value, datetime):
            mtype, value = _to_entity_datetime(value)
        elif isinstance(value, tuple):
            conv = _EDM_TO_ENTITY_CONVERSIONS.get(value[1])
            mtype, value = conv(value[0])
        else:
            conv = _PYTHON_TO_ENTITY_CONVERSIONS.get(type(value))
            if conv is None and value is not None:
                raise TypeError(_ERROR_TYPE_NOT_SUPPORTED.format(type(value)))
            if value is None:
                conv = _to_entity_none

            mtype, value = conv(value)

        # form the property node
        if value is not None:
            properties[name] = value
            if mtype:
                properties[name + "@odata.type"] = mtype.value

    # generate the entity_body
    return properties


def serialize_iso(attr):
    """Serialize Datetime object into ISO-8601 formatted string.

    :param Datetime attr: Object to be serialized.
    :rtype: str
    :raises ValueError: If format is invalid.
    """
    if not attr:
        return None
    if isinstance(attr, str):
        # Pass a string through unaltered
        return attr
    try:
        utc = attr.utctimetuple()
        if utc.tm_year > 9999 or utc.tm_year < 1:
            raise OverflowError("Hit max or min date")

        date = "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}".format(
            utc.tm_year, utc.tm_mon, utc.tm_mday, utc.tm_hour, utc.tm_min, utc.tm_sec
        )
        return date + "Z"
    except (ValueError, OverflowError) as err:
        msg = "Unable to serialize datetime object."
        raise_with_traceback(ValueError, msg, err)
    except AttributeError as err:
        msg = "ISO-8601 object must be valid Datetime object."
        raise_with_traceback(TypeError, msg, err)
