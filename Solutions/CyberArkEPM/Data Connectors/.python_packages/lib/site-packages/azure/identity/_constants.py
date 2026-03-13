# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import warnings

DEVELOPER_SIGN_ON_CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"
AZURE_VSCODE_CLIENT_ID = "aebc6443-996d-45c2-90f0-388ff96faa56"
VSCODE_CREDENTIALS_SECTION = "VS Code Azure"
DEFAULT_REFRESH_OFFSET = 300
DEFAULT_TOKEN_REFRESH_RETRY_DELAY = 30

CACHE_NON_CAE_SUFFIX = ".nocae"  # cspell:disable-line
CACHE_CAE_SUFFIX = ".cae"


class AzureAuthorityHostsMeta(type):
    def __getattr__(cls, name):
        if name == "AZURE_GERMANY":
            warnings.warn(
                "AZURE_GERMANY is deprecated. Microsoft Cloud Germany was closed on October 29th, 2021.",
                DeprecationWarning,
                stacklevel=2,
            )
            return "login.microsoftonline.de"
        raise AttributeError(f"{name} not found in {cls.__name__}")


class AzureAuthorityHosts(metaclass=AzureAuthorityHostsMeta):
    """Constants for Microsoft Entra ID authority hosts.
    These are used to construct authority URLs for various Azure environments.
    """

    AZURE_CHINA = "login.chinacloudapi.cn"
    AZURE_GOVERNMENT = "login.microsoftonline.us"
    AZURE_PUBLIC_CLOUD = "login.microsoftonline.com"


class KnownAuthorities(AzureAuthorityHosts):
    """Alias of :class:`AzureAuthorityHosts`"""


class EnvironmentVariables:
    AZURE_CLIENT_ID = "AZURE_CLIENT_ID"
    AZURE_CLIENT_SECRET = "AZURE_CLIENT_SECRET"
    AZURE_TENANT_ID = "AZURE_TENANT_ID"
    CLIENT_SECRET_VARS = (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)

    AZURE_CLIENT_CERTIFICATE_PATH = "AZURE_CLIENT_CERTIFICATE_PATH"
    AZURE_CLIENT_CERTIFICATE_PASSWORD = "AZURE_CLIENT_CERTIFICATE_PASSWORD"
    AZURE_CLIENT_SEND_CERTIFICATE_CHAIN = "AZURE_CLIENT_SEND_CERTIFICATE_CHAIN"
    CERT_VARS = (AZURE_CLIENT_ID, AZURE_CLIENT_CERTIFICATE_PATH, AZURE_TENANT_ID)

    AZURE_USERNAME = "AZURE_USERNAME"
    AZURE_PASSWORD = "AZURE_PASSWORD"
    USERNAME_PASSWORD_VARS = (AZURE_CLIENT_ID, AZURE_USERNAME, AZURE_PASSWORD)

    AZURE_POD_IDENTITY_AUTHORITY_HOST = "AZURE_POD_IDENTITY_AUTHORITY_HOST"
    IDENTITY_ENDPOINT = "IDENTITY_ENDPOINT"
    IDENTITY_HEADER = "IDENTITY_HEADER"
    IDENTITY_SERVER_THUMBPRINT = "IDENTITY_SERVER_THUMBPRINT"
    IMDS_ENDPOINT = "IMDS_ENDPOINT"
    MSI_ENDPOINT = "MSI_ENDPOINT"
    MSI_SECRET = "MSI_SECRET"

    AZURE_AUTHORITY_HOST = "AZURE_AUTHORITY_HOST"
    AZURE_IDENTITY_DISABLE_MULTITENANTAUTH = "AZURE_IDENTITY_DISABLE_MULTITENANTAUTH"
    AZURE_REGIONAL_AUTHORITY_NAME = "AZURE_REGIONAL_AUTHORITY_NAME"

    AZURE_FEDERATED_TOKEN_FILE = "AZURE_FEDERATED_TOKEN_FILE"

    AZURE_TOKEN_CREDENTIALS = "AZURE_TOKEN_CREDENTIALS"
    WORKLOAD_IDENTITY_VARS = (AZURE_AUTHORITY_HOST, AZURE_TENANT_ID, AZURE_FEDERATED_TOKEN_FILE)
