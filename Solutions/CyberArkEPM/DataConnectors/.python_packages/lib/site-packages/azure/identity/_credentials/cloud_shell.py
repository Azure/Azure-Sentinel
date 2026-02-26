# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
from typing import Any, Optional, Dict, Mapping

from azure.core.rest import HttpRequest

from .._constants import EnvironmentVariables
from .._internal import within_dac
from .._internal.managed_identity_client import ManagedIdentityClient
from .._internal.managed_identity_base import ManagedIdentityBase


def validate_client_id_and_config(client_id: Optional[str], identity_config: Optional[Mapping[str, str]]) -> None:
    if within_dac.get():
        return
    if client_id:
        raise ValueError("client_id should not be set for cloud shell managed identity.")
    if identity_config:
        valid_keys = {"object_id", "resource_id", "client_id"}
        if len(identity_config.keys() & valid_keys) > 0:
            raise ValueError(f"identity_config must not contain the following keys: {', '.join(valid_keys)}")


class CloudShellCredential(ManagedIdentityBase):
    def get_client(self, **kwargs: Any) -> Optional[ManagedIdentityClient]:
        client_id = kwargs.get("client_id")
        identity_config = kwargs.get("identity_config")
        validate_client_id_and_config(client_id, identity_config)

        url = os.environ.get(EnvironmentVariables.MSI_ENDPOINT)
        if url:
            return ManagedIdentityClient(
                request_factory=functools.partial(_get_request, url), base_headers={"Metadata": "true"}, **kwargs
            )
        return None

    def get_unavailable_message(self, desc: str = "") -> str:
        return f"Cloud Shell managed identity configuration not found in environment. {desc}"


def _get_request(url: str, scope: str, identity_config: Dict) -> HttpRequest:
    return HttpRequest("POST", url, data=dict({"resource": scope}, **identity_config))
