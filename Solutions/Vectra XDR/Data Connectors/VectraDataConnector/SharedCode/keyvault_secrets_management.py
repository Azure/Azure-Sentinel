"""This file is used for accessing keyvault to get or set secrets."""
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError
from ..SharedCode import consts


class KeyVaultSecretManage:
    """This class contains methods to authenticate with Azure KeyVault and get or set secrets in keyvault."""

    def __init__(self, applogger) -> None:
        """Intialize instance variables for class."""
        self.keyvault_name = consts.KEYVAULT_NAME
        self.keyvault_uri = "https://{}.vault.azure.net/".format(self.keyvault_name)
        self.client = self.get_client()
        self.applogger = applogger

    def get_client(self):
        """To obtain AzureKeyVault client.

        Returns:
            SecretClient: returns client object for accessing AzureKeyVault.
        """
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=self.keyvault_uri, credential=credential)
        return client

    def get_keyvault_secret(self, secret_name):
        """To get value of provided secretname from AzureKeyVault.

        Args:
            secret_name (str): secret name to get its value.
        """
        try:
            self.applogger.debug("Retrieving secret {} from {}.".format(secret_name, self.keyvault_name))
            retrieved_secret = self.client.get_secret(secret_name)
            self.applogger.debug("Retrieved secret value for {}.".format(retrieved_secret.name))
            return retrieved_secret.value

        except ResourceNotFoundError as err:
            self.applogger.error("Resource not found : '{}' ".format(err))
            self.set_keyvault_secret(secret_name, "")
            return ""

    def set_keyvault_secret(self, secret_name, secret_value):
        """To update secret value of given secret name or create new secret.

        Args:
            secret_name (str): secret name to update its value or create it.
            secret_value (str): secret value to be set as value of given secret name.
        """
        self.applogger.debug("Creating or updating a secret '{}'.".format(secret_name))
        self.client.set_secret(secret_name, secret_value)
        self.applogger.debug("Secret created successfully : '{}' .".format(secret_name))

    def get_properties_list_of_secrets(self):
        """To get list of secrets stored in keyvault with its properties.

        Returns:
            list: _description_
        """
        secret_properties = self.client.list_properties_of_secrets()
        properties_list = [secret_property.name for secret_property in secret_properties]
        return properties_list
