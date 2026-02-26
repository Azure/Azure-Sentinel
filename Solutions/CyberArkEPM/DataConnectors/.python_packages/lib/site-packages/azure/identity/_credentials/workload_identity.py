# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import time
from typing import Any
from typing import Optional

from .client_assertion import ClientAssertionCredential
from .._constants import EnvironmentVariables


WORKLOAD_CONFIG_ERROR = (
    "WorkloadIdentityCredential authentication unavailable. The workload options are not fully "
    "configured. See the troubleshooting guide for more information: "
    "https://aka.ms/azsdk/python/identity/workloadidentitycredential/troubleshoot"
)


class TokenFileMixin:

    _token_file_path: str

    def __init__(self, **_: Any) -> None:
        super(TokenFileMixin, self).__init__()
        self._jwt = ""
        self._last_read_time = 0

    def _get_service_account_token(self) -> str:
        now = int(time.time())
        if now - self._last_read_time > 600:
            with open(self._token_file_path, encoding="utf-8") as f:
                self._jwt = f.read()
            self._last_read_time = now
        return self._jwt


class WorkloadIdentityCredential(ClientAssertionCredential, TokenFileMixin):
    """Authenticates using Microsoft Entra Workload ID.

    Workload identity authentication is a feature in Azure that allows applications running on virtual machines (VMs)
    to access other Azure resources without the need for a service principal or managed identity. With workload
    identity authentication, applications authenticate themselves using their own identity, rather than using a shared
    service principal or managed identity. Under the hood, workload identity authentication uses the concept of Service
    Account Credentials (SACs), which are automatically created by Azure and stored securely in the VM. By using
    workload identity authentication, you can avoid the need to manage and rotate service principals or managed
    identities for each application on each VM. Additionally, because SACs are created automatically and managed by
    Azure, you don't need to worry about storing and securing sensitive credentials themselves.

    The WorkloadIdentityCredential supports Azure workload identity authentication on Azure Kubernetes and acquires
    a token using the service account credentials available in the Azure Kubernetes environment. Refer
    to `this workload identity overview <https://learn.microsoft.com/azure/aks/workload-identity-overview>`__
    for more information.

    :keyword str tenant_id: ID of the application's Microsoft Entra tenant. Also called its "directory" ID.
    :keyword str client_id: The client ID of a Microsoft Entra app registration.
    :keyword str token_file_path: The path to a file containing a Kubernetes service account token that authenticates
        the identity.

    .. admonition:: Example:

        .. literalinclude:: ../samples/credential_creation_code_snippets.py
            :start-after: [START workload_identity_credential]
            :end-before: [END workload_identity_credential]
            :language: python
            :dedent: 4
            :caption: Create a WorkloadIdentityCredential.
    """

    def __init__(
        self,
        *,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        token_file_path: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        tenant_id = tenant_id or os.environ.get(EnvironmentVariables.AZURE_TENANT_ID)
        client_id = client_id or os.environ.get(EnvironmentVariables.AZURE_CLIENT_ID)
        token_file_path = token_file_path or os.environ.get(EnvironmentVariables.AZURE_FEDERATED_TOKEN_FILE)

        missing_args = []
        if not tenant_id:
            missing_args.append("'tenant_id'")
        if not client_id:
            missing_args.append("'client_id'")
        if not token_file_path:
            missing_args.append("'token_file_path'")

        if missing_args:
            missing_args_str = ", ".join(missing_args)
            error_message = f"{WORKLOAD_CONFIG_ERROR}. Missing required arguments: {missing_args_str}."
            raise ValueError(error_message)

        # Type assertions since we've validated these are not None
        assert tenant_id is not None
        assert client_id is not None
        assert token_file_path is not None

        self._token_file_path = token_file_path

        super(WorkloadIdentityCredential, self).__init__(
            tenant_id=tenant_id,
            client_id=client_id,
            func=self._get_service_account_token,
            token_file_path=token_file_path,
            **kwargs,
        )
