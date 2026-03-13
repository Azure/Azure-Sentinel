# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
from typing import Optional, Any

from .._internal.managed_identity_base import AsyncManagedIdentityBase
from .._internal.managed_identity_client import AsyncManagedIdentityClient
from ..._constants import EnvironmentVariables
from ..._credentials.cloud_shell import _get_request, validate_client_id_and_config


class CloudShellCredential(AsyncManagedIdentityBase):
    def get_client(self, **kwargs: Any) -> Optional[AsyncManagedIdentityClient]:
        client_id = kwargs.get("client_id")
        identity_config = kwargs.get("identity_config")
        validate_client_id_and_config(client_id, identity_config)

        url = os.environ.get(EnvironmentVariables.MSI_ENDPOINT)
        if url:
            return AsyncManagedIdentityClient(
                request_factory=functools.partial(_get_request, url), base_headers={"Metadata": "true"}, **kwargs
            )
        return None

    def get_unavailable_message(self, desc: str = "") -> str:
        return f"Cloud Shell managed identity configuration not found in environment. {desc}"
