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

from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceModifiedError,
    ResourceExistsError,
    ClientAuthenticationError,
    DecodeError)

from .parser import _to_utc_datetime
from .models import StorageErrorCode, UserDelegationKey, get_enum_value


if TYPE_CHECKING:
    from datetime import datetime
    from azure.core.exceptions import AzureError


_LOGGER = logging.getLogger(__name__)


class PartialBatchErrorException(HttpResponseError):
    """There is a partial failure in batch operations.

    :param str message: The message of the exception.
    :param response: Server response to be deserialized.
    :param list parts: A list of the parts in multipart response.
    """

    def __init__(self, message, response, parts):
        self.parts = parts
        super(PartialBatchErrorException, self).__init__(message=message, response=response)


def parse_length_from_content_range(content_range):
    '''
    Parses the blob length from the content range header: bytes 1-3/65537
    '''
    if content_range is None:
        return None

    # First, split in space and take the second half: '1-3/65537'
    # Next, split on slash and take the second half: '65537'
    # Finally, convert to an int: 65537
    return int(content_range.split(' ', 1)[1].split('/', 1)[1])


def normalize_headers(headers):
    normalized = {}
    for key, value in headers.items():
        if key.startswith('x-ms-'):
            key = key[5:]
        normalized[key.lower().replace('-', '_')] = get_enum_value(value)
    return normalized


def deserialize_metadata(response, obj, headers):  # pylint: disable=unused-argument
    raw_metadata = {k: v for k, v in response.headers.items() if k.startswith("x-ms-meta-")}
    return {k[10:]: v for k, v in raw_metadata.items()}


def return_response_headers(response, deserialized, response_headers):  # pylint: disable=unused-argument
    return normalize_headers(response_headers)


def return_headers_and_deserialized(response, deserialized, response_headers):  # pylint: disable=unused-argument
    return normalize_headers(response_headers), deserialized


def return_context_and_deserialized(response, deserialized, response_headers):  # pylint: disable=unused-argument
    return response.location_mode, deserialized


def process_storage_error(storage_error):
    raise_error = HttpResponseError
    error_code = storage_error.response.headers.get('x-ms-error-code')
    error_message = storage_error.message
    additional_data = {}
    try:
        error_body = ContentDecodePolicy.deserialize_from_http_generics(storage_error.response)
        if error_body:
            for info in error_body.iter():
                if info.tag.lower() == 'code':
                    error_code = info.text
                elif info.tag.lower() == 'message':
                    error_message = info.text
                else:
                    additional_data[info.tag] = info.text
    except DecodeError:
        pass

    try:
        if error_code:
            error_code = StorageErrorCode(error_code)
            if error_code in [StorageErrorCode.condition_not_met,
                              StorageErrorCode.blob_overwritten]:
                raise_error = ResourceModifiedError
            if error_code in [StorageErrorCode.invalid_authentication_info,
                              StorageErrorCode.authentication_failed]:
                raise_error = ClientAuthenticationError
            if error_code in [StorageErrorCode.resource_not_found,
                              StorageErrorCode.cannot_verify_copy_source,
                              StorageErrorCode.blob_not_found,
                              StorageErrorCode.queue_not_found,
                              StorageErrorCode.container_not_found,
                              StorageErrorCode.parent_not_found,
                              StorageErrorCode.share_not_found]:
                raise_error = ResourceNotFoundError
            if error_code in [StorageErrorCode.account_already_exists,
                              StorageErrorCode.account_being_created,
                              StorageErrorCode.resource_already_exists,
                              StorageErrorCode.resource_type_mismatch,
                              StorageErrorCode.blob_already_exists,
                              StorageErrorCode.queue_already_exists,
                              StorageErrorCode.container_already_exists,
                              StorageErrorCode.container_being_deleted,
                              StorageErrorCode.queue_being_deleted,
                              StorageErrorCode.share_already_exists,
                              StorageErrorCode.share_being_deleted]:
                raise_error = ResourceExistsError
    except ValueError:
        # Got an unknown error code
        pass

    try:
        error_message += "\nErrorCode:{}".format(error_code.value)
    except AttributeError:
        error_message += "\nErrorCode:{}".format(error_code)
    for name, info in additional_data.items():
        error_message += "\n{}:{}".format(name, info)

    error = raise_error(message=error_message, response=storage_error.response)
    error.error_code = error_code
    error.additional_info = additional_data
    raise error


def parse_to_internal_user_delegation_key(service_user_delegation_key):
    internal_user_delegation_key = UserDelegationKey()
    internal_user_delegation_key.signed_oid = service_user_delegation_key.signed_oid
    internal_user_delegation_key.signed_tid = service_user_delegation_key.signed_tid
    internal_user_delegation_key.signed_start = _to_utc_datetime(service_user_delegation_key.signed_start)
    internal_user_delegation_key.signed_expiry = _to_utc_datetime(service_user_delegation_key.signed_expiry)
    internal_user_delegation_key.signed_service = service_user_delegation_key.signed_service
    internal_user_delegation_key.signed_version = service_user_delegation_key.signed_version
    internal_user_delegation_key.value = service_user_delegation_key.value
    return internal_user_delegation_key
