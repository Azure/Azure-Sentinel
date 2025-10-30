import os

from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()

def checkIfSecretUri(possibleSecretUri):
    if '@Microsoft.KeyVault' in possibleSecretUri:
        secret_uri = possibleSecretUri.split("=", maxsplit=1)[1].rstrip(")")
        vault_url, secret_name = secret_uri.split("/secrets/")

        client = SecretClient(vault_url=vault_url.replace('keyvault', 'KeyVault'), credential=credential)
        if "/" in secret_name:
            secret_name = secret_name.split("/", maxsplit=1)[0]
        return client.get_secret(secret_name).value
    return possibleSecretUri

API_KEY = os.environ.get('API_KEY')
API_KEY = checkIfSecretUri(API_KEY)

API_SECRET = os.environ.get('API_SECRET')
API_SECRET = checkIfSecretUri(API_SECRET)

# Log Analytics workspace ID
WORKSPACE_ID=os.environ.get('WORKSPACE_ID')

# Primary or secondary Connected Sources client authentication key   
WORKSPACE_KEY = os.environ.get('WORKSPACE_KEY')
WORKSPACE_KEY = checkIfSecretUri(WORKSPACE_KEY)

BASE_URL = os.environ.get('BASE_URL', 'https://api.mailrisk.com/v1/')

# The log type is the name of the event that is being submitted
LOG_TYPE=os.environ.get('LOG_TYPE', 'MailRiskEmails')

VERIFY_CERTIFICATE = (os.environ.get('VERIFY_CERTIFICATE', 'True') == 'True')


