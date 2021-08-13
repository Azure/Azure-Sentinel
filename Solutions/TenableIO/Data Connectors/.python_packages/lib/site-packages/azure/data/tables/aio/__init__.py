# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.data.tables.aio._table_client_async import TableClient
from azure.data.tables.aio._table_service_client_async import TableServiceClient

__all__ = [
    "TableClient",
    "TableServiceClient",
]
