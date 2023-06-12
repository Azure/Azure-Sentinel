# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Iterable, Dict, List, Type, Tuple,
    TYPE_CHECKING
)

import logging
from os import fstat
from io import (SEEK_END, SEEK_SET, UnsupportedOperation)

import isodate

from azure.core.exceptions import raise_with_traceback


_LOGGER = logging.getLogger(__name__)


def serialize_iso(attr):
    """Serialize Datetime object into ISO-8601 formatted string.

    :param Datetime attr: Object to be serialized.
    :rtype: str
    :raises: ValueError if format invalid.
    """
    if not attr:
        return None
    if isinstance(attr, str):
        attr = isodate.parse_datetime(attr)
    try:
        utc = attr.utctimetuple()
        if utc.tm_year > 9999 or utc.tm_year < 1:
            raise OverflowError("Hit max or min date")

        date = "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}".format(
            utc.tm_year, utc.tm_mon, utc.tm_mday,
            utc.tm_hour, utc.tm_min, utc.tm_sec)
        return date + 'Z'
    except (ValueError, OverflowError) as err:
        msg = "Unable to serialize datetime object."
        raise_with_traceback(ValueError, msg, err)
    except AttributeError as err:
        msg = "ISO-8601 object must be valid Datetime object."
        raise_with_traceback(TypeError, msg, err)


def get_length(data):
    length = None
    # Check if object implements the __len__ method, covers most input cases such as bytearray.
    try:
        length = len(data)
    except:  # pylint: disable=bare-except
        pass

    if not length:
        # Check if the stream is a file-like stream object.
        # If so, calculate the size using the file descriptor.
        try:
            fileno = data.fileno()
        except (AttributeError, UnsupportedOperation):
            pass
        else:
            try:
                return fstat(fileno).st_size
            except OSError:
                # Not a valid fileno, may be possible requests returned
                # a socket number?
                pass

        # If the stream is seekable and tell() is implemented, calculate the stream size.
        try:
            current_position = data.tell()
            data.seek(0, SEEK_END)
            length = data.tell() - current_position
            data.seek(current_position, SEEK_SET)
        except (AttributeError, UnsupportedOperation):
            pass

    return length


def read_length(data):
    try:
        if hasattr(data, 'read'):
            read_data = b''
            for chunk in iter(lambda: data.read(4096), b""):
                read_data += chunk
            return len(read_data), read_data
        if hasattr(data, '__iter__'):
            read_data = b''
            for chunk in data:
                read_data += chunk
            return len(read_data), read_data
    except:  # pylint: disable=bare-except
        pass
    raise ValueError("Unable to calculate content length, please specify.")


def validate_and_format_range_headers(
        start_range, end_range, start_range_required=True,
        end_range_required=True, check_content_md5=False, align_to_page=False):
    # If end range is provided, start range must be provided
    if (start_range_required or end_range is not None) and start_range is None:
        raise ValueError("start_range value cannot be None.")
    if end_range_required and end_range is None:
        raise ValueError("end_range value cannot be None.")

    # Page ranges must be 512 aligned
    if align_to_page:
        if start_range is not None and start_range % 512 != 0:
            raise ValueError("Invalid page blob start_range: {0}. "
                             "The size must be aligned to a 512-byte boundary.".format(start_range))
        if end_range is not None and end_range % 512 != 511:
            raise ValueError("Invalid page blob end_range: {0}. "
                             "The size must be aligned to a 512-byte boundary.".format(end_range))

    # Format based on whether end_range is present
    range_header = None
    if end_range is not None:
        range_header = 'bytes={0}-{1}'.format(start_range, end_range)
    elif start_range is not None:
        range_header = "bytes={0}-".format(start_range)

    # Content MD5 can only be provided for a complete range less than 4MB in size
    range_validation = None
    if check_content_md5:
        if start_range is None or end_range is None:
            raise ValueError("Both start and end range requied for MD5 content validation.")
        if end_range - start_range > 4 * 1024 * 1024:
            raise ValueError("Getting content MD5 for a range greater than 4MB is not supported.")
        range_validation = 'true'

    return range_header, range_validation


def add_metadata_headers(metadata=None):
    # type: (Optional[Dict[str, str]]) -> Dict[str, str]
    headers = {}
    if metadata:
        for key, value in metadata.items():
            headers['x-ms-meta-{}'.format(key.strip())] = value.strip() if value else value
    return headers
