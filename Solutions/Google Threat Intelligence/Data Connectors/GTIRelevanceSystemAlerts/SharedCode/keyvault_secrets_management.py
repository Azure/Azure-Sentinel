"""KeyVault secrets management for the GTI Relevance System Alerts connector."""

from azure.keyvault.secrets import SecretClient
from azure.identity import ManagedIdentityCredential
from azure.core.exceptions import ResourceNotFoundError

from SharedCode import consts
from SharedCode.logger import applogger


class KeyVaultSecretManage:
    """Manage secrets in Azure Key Vault using the Function App Managed Identity."""

    def __init__(self) -> None:
        """Initialize the Key Vault client using the configured vault name."""
        self.keyvault_name = consts.KEYVAULT_NAME
        if ".us" in consts.SCOPE:
            self.keyvault_uri = "https://{}.vault.usgovcloudapi.net/".format(self.keyvault_name)
        else:
            self.keyvault_uri = "https://{}.vault.azure.net/".format(self.keyvault_name)
        self.client = self._get_client()

    def _get_client(self):
        """Obtain the Azure Key Vault SecretClient using Managed Identity.

        Returns:
            SecretClient: Authenticated Key Vault client.
        """
        credential = ManagedIdentityCredential()
        return SecretClient(vault_url=self.keyvault_uri, credential=credential)

    def get_keyvault_secret(self, secret_name):
        """Retrieve a secret value from Azure Key Vault.

        Args:
            secret_name (str): Name of the secret to retrieve.

        Returns:
            str: The secret value, or empty string if the secret does not exist.
        """
        try:
            applogger.debug("Retrieving secret '{}' from KeyVault '{}'.".format(secret_name, self.keyvault_name))
            retrieved_secret = self.client.get_secret(secret_name)
            applogger.debug("Retrieved secret '{}'.".format(retrieved_secret.name))
            return retrieved_secret.value
        except ResourceNotFoundError:
            applogger.warning("Secret '{}' not found in KeyVault '{}'.".format(secret_name, self.keyvault_name))
            return ""

    def set_keyvault_secret(self, secret_name, secret_value):
        """Create or update a secret in Azure Key Vault.

        Args:
            secret_name (str): Name of the secret to set.
            secret_value (str): Value to store.
        """
        applogger.debug("Creating or updating secret '{}' in KeyVault '{}'.".format(secret_name, self.keyvault_name))
        self.client.set_secret(secret_name, secret_value)
        applogger.debug("Secret '{}' stored successfully.".format(secret_name))
