# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=no-self-use
from typing import (  # pylint: disable=unused-import
    Tuple, Dict, List,
    TYPE_CHECKING
)

from ._models import ShareProperties, DirectoryProperties, FileProperties
from ._shared.response_handlers import deserialize_metadata
from ._generated.models import ShareFileRangeList


def deserialize_share_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    share_properties = ShareProperties(
        metadata=metadata,
        **headers
    )
    return share_properties


def deserialize_directory_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    directory_properties = DirectoryProperties(
        metadata=metadata,
        **headers
    )
    return directory_properties


def deserialize_file_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    file_properties = FileProperties(
        metadata=metadata,
        **headers
    )
    if 'Content-Range' in headers:
        if 'x-ms-content-md5' in headers:
            file_properties.content_settings.content_md5 = headers['x-ms-content-md5']
        else:
            file_properties.content_settings.content_md5 = None
    return file_properties


def deserialize_file_stream(response, obj, headers):
    file_properties = deserialize_file_properties(response, obj, headers)
    obj.properties = file_properties
    return response.location_mode, obj


def deserialize_permission(response, obj, headers):  # pylint: disable=unused-argument
    '''
    Extracts out file permission
    '''

    return obj.permission


def deserialize_permission_key(response, obj, headers):  # pylint: disable=unused-argument
    '''
    Extracts out file permission key
    '''

    if response is None or headers is None:
        return None
    return headers.get('x-ms-file-permission-key', None)


def get_file_ranges_result(ranges):
    # type: (ShareFileRangeList) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]
    file_ranges = []  # type: ignore
    clear_ranges = []  # type: List
    if ranges.ranges:
        file_ranges = [
            {'start': file_range.start, 'end': file_range.end} for file_range in ranges.ranges]  # type: ignore
    if ranges.clear_ranges:
        clear_ranges = [
            {'start': clear_range.start, 'end': clear_range.end} for clear_range in ranges.clear_ranges]
    return file_ranges, clear_ranges
