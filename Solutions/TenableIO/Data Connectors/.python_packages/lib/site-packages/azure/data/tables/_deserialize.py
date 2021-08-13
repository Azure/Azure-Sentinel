# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Union, Dict, Any, Optional

from uuid import UUID
import logging
import datetime

import six

from ._entity import EntityProperty, EdmType, TableEntity
from ._common_conversion import _decode_base64_to_bytes, TZ_UTC


_LOGGER = logging.getLogger(__name__)

try:
    from urllib.parse import quote
except ImportError:
    from urllib2 import quote  # type: ignore


class TablesEntityDatetime(datetime.datetime):

    @property
    def tables_service_value(self):
        try:
            return self._service_value
        except AttributeError:
            return ""


def url_quote(url):
    return quote(url)


def get_enum_value(value):
    if value is None or value in ["None", ""]:
        return None
    try:
        return value.value
    except AttributeError:
        return value


def _from_entity_binary(value):
    # type: (str) -> EntityProperty
    return _decode_base64_to_bytes(value)


def _from_entity_int32(value):
    # type: (str) -> int
    return int(value)


def _from_entity_int64(value):
    # type: (str) -> EntityProperty
    return EntityProperty(int(value), EdmType.INT64)


def _from_entity_datetime(value):
    # Cosmos returns this with a decimal point that throws an error on deserialization
    cleaned_value = clean_up_dotnet_timestamps(value)
    try:
        dt_obj = TablesEntityDatetime.strptime(cleaned_value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=TZ_UTC
        )
    except ValueError:
        dt_obj = TablesEntityDatetime.strptime(cleaned_value, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=TZ_UTC
        )
    dt_obj._service_value = value  # pylint:disable=protected-access
    return dt_obj


def clean_up_dotnet_timestamps(value):
    # .NET has more decimal places than Python supports in datetime objects, this truncates
    # values after 6 decimal places.
    value = value.split(".")
    ms = ""
    if len(value) == 2:
        ms = value[-1].replace("Z", "")
        if len(ms) > 6:
            ms = ms[:6]
        ms = ms + "Z"
        return ".".join([value[0], ms])

    return value[0]


def deserialize_iso(value):
    if not value:
        return value
    return _from_entity_datetime(value)


def _from_entity_guid(value):
    return UUID(value)


def _from_entity_str(value):
    # type: (Union[str, bytes]) -> str
    if isinstance(value, six.binary_type):
        return value.decode('utf-8')
    return value


_EDM_TYPES = [
    EdmType.BINARY,
    EdmType.INT64,
    EdmType.GUID,
    EdmType.DATETIME,
    EdmType.STRING,
    EdmType.INT32,
    EdmType.DOUBLE,
    EdmType.BOOLEAN,
]

_ENTITY_TO_PYTHON_CONVERSIONS = {
    EdmType.BINARY: _from_entity_binary,
    EdmType.INT32: _from_entity_int32,
    EdmType.INT64: _from_entity_int64,
    EdmType.DOUBLE: float,
    EdmType.DATETIME: _from_entity_datetime,
    EdmType.GUID: _from_entity_guid,
    EdmType.STRING: _from_entity_str,
}


def _convert_to_entity(entry_element):
    """Convert json response to entity.
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
    entity = TableEntity()

    properties = {}
    edmtypes = {}
    odata = {}

    for name, value in entry_element.items():
        if name.startswith("odata."):
            odata[name[6:]] = value
        elif name.endswith("@odata.type"):
            edmtypes[name[:-11]] = value
        else:
            properties[name] = value

    # Partition key is a known property
    partition_key = properties.pop("PartitionKey", None)
    if partition_key:
        entity["PartitionKey"] = partition_key

    # Row key is a known property
    row_key = properties.pop("RowKey", None)
    if row_key:
        entity["RowKey"] = row_key

    # Timestamp is a known property
    timestamp = properties.pop("Timestamp", None)

    for name, value in properties.items():
        mtype = edmtypes.get(name)

        # Add type for Int32/64
        if isinstance(value, int) and mtype is None:
            mtype = EdmType.INT32

            if value >= 2 ** 31 or value < (-(2 ** 31)):
                mtype = EdmType.INT64

        # Add type for String
        try:
            if isinstance(value, unicode) and mtype is None:  # type: ignore
                mtype = EdmType.STRING
        except NameError:
            if isinstance(value, str) and mtype is None:
                mtype = EdmType.STRING

        # no type info, property should parse automatically
        if not mtype:
            entity[name] = value
        elif mtype in [EdmType.STRING, EdmType.INT32]:
            entity[name] = value
        else:  # need an object to hold the property
            conv = _ENTITY_TO_PYTHON_CONVERSIONS.get(mtype)
            if conv is not None:
                new_property = conv(value)
            else:
                new_property = EntityProperty(mtype, value)
            entity[name] = new_property

    # extract etag from entry
    etag = odata.pop("etag", None)
    odata.pop("metadata", None)
    if timestamp:
        if not etag:
            etag = "W/\"datetime'" + url_quote(timestamp) + "'\""
        timestamp = _from_entity_datetime(timestamp)
    odata.update({'etag': etag, 'timestamp': timestamp})
    entity._metadata = odata  # pylint: disable=protected-access
    return entity


def _extract_etag(response):
    """ Extracts the etag from the response headers. """
    if response and response.headers:
        return response.headers.get("etag")

    return None


def _extract_continuation_token(continuation_token):
    """Extract list entity continuation headers from token.

    :param dict(str,str) continuation_token: The listing continuation token.
    :returns: The next partition key and next row key in a tuple
    :rtype: (str,str)
    """
    if not continuation_token:
        return None, None
    try:
        return continuation_token.get("PartitionKey"), continuation_token.get("RowKey")
    except AttributeError:
        raise ValueError("Invalid continuation token format.")


def _normalize_headers(headers):
    normalized = {}
    for key, value in headers.items():
        if key.startswith("x-ms-"):
            key = key[5:]
        normalized[key.lower().replace("-", "_")] = get_enum_value(value)
    return normalized


def _return_headers_and_deserialized(
    response, deserialized, response_headers
):  # pylint: disable=unused-argument
    return _normalize_headers(response_headers), deserialized


def _return_context_and_deserialized(
    response, deserialized, response_headers
):  # pylint: disable=unused-argument
    return response.context['location_mode'], deserialized, response_headers


def _trim_service_metadata(metadata, content=None):
    # type: (Dict[str, str], Optional[Dict[str, Any]]) -> Dict[str, Any]
    result = {
        "date": metadata.pop("date", None),
        "etag": metadata.pop("etag", None),
        "version": metadata.pop("version", None),
    }
    preference = metadata.pop('preference_applied', None)
    if preference:
        result["preference_applied"] = preference
        result["content"] = content  # type: ignore
    return result
