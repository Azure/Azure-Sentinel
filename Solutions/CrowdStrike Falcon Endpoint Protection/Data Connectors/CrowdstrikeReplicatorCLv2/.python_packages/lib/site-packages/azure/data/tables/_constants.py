# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._generated._version import VERSION

# default values for common package, in case it is used directly
DEFAULT_X_MS_VERSION = "2018-03-28"
X_MS_VERSION = VERSION

# Live ServiceClient URLs
SERVICE_HOST_BASE = "core.windows.net"

STORAGE_OAUTH_SCOPE = "https://storage.azure.com/.default"

NEXT_TABLE_NAME = "x-ms-continuation-NextTableName"
NEXT_PARTITION_KEY = "x-ms-continuation-NextPartitionKey"
NEXT_ROW_KEY = "x-ms-continuation-NextRowKey"
