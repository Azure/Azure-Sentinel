# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ._queue_client_async import QueueClient
from ._queue_service_client_async import QueueServiceClient


__all__ = [
    'QueueClient',
    'QueueServiceClient',
]
