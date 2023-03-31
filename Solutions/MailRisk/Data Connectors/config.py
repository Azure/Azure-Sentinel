import os

from dotenv import load_dotenv
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

load_dotenv()

keyVaultName = os.environ["KEY_VAULT_NAME"]

if keyVaultName:
    keyVaultUri = f"https://{keyVaultName}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=keyVaultUri, credential=credential)
    
    API_KEY = client.get_secret(f"{keyVaultName}-APIKey").value
    API_SECRET = client.get_secret(f"{keyVaultName}-APISecret").value
    # Primary or secondary Connected Sources client authentication key   
    WORKSPACE_KEY = client.get_secret(f"{keyVaultName}-WorkspaceKey").value
else:
    API_KEY= os.getenv('API_KEY')
    API_SECRET= os.getenv('API_SECRET')
    # Primary or secondary Connected Sources client authentication key   
    WORKSPACE_KEY=os.getenv('WORKSPACE_KEY')
    
BASE_URL = os.getenv('BASE_URL', 'https://api.mailrisk.com/v1/')

# Log Analytics workspace ID
WORKSPACE_ID=os.getenv('WORKSPACE_ID')

# The log type is the name of the event that is being submitted
LOG_TYPE=os.getenv('LOG_TYPE', 'MailRiskEmails')

VERIFY_CERTIFICATE = (os.getenv('VERIFY_CERTIFICATE', 'True') == 'True')
