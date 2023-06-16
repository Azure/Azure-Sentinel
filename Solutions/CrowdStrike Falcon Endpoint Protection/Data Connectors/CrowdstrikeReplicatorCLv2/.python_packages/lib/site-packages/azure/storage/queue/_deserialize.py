# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=unused-argument

from azure.core.exceptions import ResourceExistsError

from ._shared.models import StorageErrorCode
from ._models import QueueProperties
from ._shared.response_handlers import deserialize_metadata


def deserialize_queue_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    queue_properties = QueueProperties(
        metadata=metadata,
        **headers
    )
    return queue_properties


def deserialize_queue_creation(response, obj, headers):
    response = response.http_response
    if response.status_code == 204:
        error_code = StorageErrorCode.queue_already_exists
        error = ResourceExistsError(
            message=(
                "Queue already exists\n"
                f"RequestId:{headers['x-ms-request-id']}\n"
                f"Time:{headers['Date']}\n"
                f"ErrorCode:{error_code}"),
            response=response)
        error.error_code = error_code
        error.additional_info = {}
        raise error
    return headers
