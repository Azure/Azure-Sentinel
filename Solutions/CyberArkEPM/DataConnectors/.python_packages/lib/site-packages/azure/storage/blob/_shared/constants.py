# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .._serialize import _SUPPORTED_API_VERSIONS


X_MS_VERSION = _SUPPORTED_API_VERSIONS[-1]

# Connection defaults
CONNECTION_TIMEOUT = 20
READ_TIMEOUT = 60
DATA_BLOCK_SIZE = 256 * 1024

DEFAULT_OAUTH_SCOPE = "/.default"
STORAGE_OAUTH_SCOPE = "https://storage.azure.com/.default"

SERVICE_HOST_BASE = "core.windows.net"
