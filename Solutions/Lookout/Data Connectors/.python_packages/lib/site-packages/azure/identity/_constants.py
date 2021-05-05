# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


DEVELOPER_SIGN_ON_CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"
AZURE_VSCODE_CLIENT_ID = "aebc6443-996d-45c2-90f0-388ff96faa56"
VSCODE_CREDENTIALS_SECTION = "VS Code Azure"
DEFAULT_REFRESH_OFFSET = 300
DEFAULT_TOKEN_REFRESH_RETRY_DELAY = 30


class AzureAuthorityHosts:
    AZURE_CHINA = "login.chinacloudapi.cn"
    AZURE_GERMANY = "login.microsoftonline.de"
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
    CERT_VARS = (AZURE_CLIENT_ID, AZURE_CLIENT_CERTIFICATE_PATH, AZURE_TENANT_ID)

    AZURE_USERNAME = "AZURE_USERNAME"
    AZURE_PASSWORD = "AZURE_PASSWORD"
    USERNAME_PASSWORD_VARS = (AZURE_CLIENT_ID, AZURE_USERNAME, AZURE_PASSWORD)

    IDENTITY_ENDPOINT = "IDENTITY_ENDPOINT"
    IDENTITY_HEADER = "IDENTITY_HEADER"
    IDENTITY_SERVER_THUMBPRINT = "IDENTITY_SERVER_THUMBPRINT"
    IMDS_ENDPOINT = "IMDS_ENDPOINT"
    MSI_ENDPOINT = "MSI_ENDPOINT"
    MSI_SECRET = "MSI_SECRET"

    AZURE_AUTHORITY_HOST = "AZURE_AUTHORITY_HOST"


class Endpoints:
    # https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/how-to-use-vm-token#get-a-token-using-http
    IMDS = "http://169.254.169.254/metadata/identity/oauth2/token"

    AAD_OAUTH2_V2_FORMAT = "https://" + KnownAuthorities.AZURE_PUBLIC_CLOUD + "/{}/oauth2/v2.0/token"
