# Vectra Generate Access Token

## Summary

This playbook will generate access token and refresh token for another playbooks.

### Prerequisites

1. Users must have a valid pair of Vectra API Client ID and Client secret credentials.
2. Store Vectra API Client credentials in Key Vault and obtain key vault name and Tenant ID.
   * Create a Key Vault with a unique name.
   * Go to KeyVault → secrets, click on Generate/import, and create 'Vectra-Client-ID' & 'Vectra-Client-Secret' for storing client_id and client_secret respectively.
   * NOTE: Ensure the Permission model in the Access Configuration of Key Vault is set to **'Vault access policy'**.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here.
   * KeyVaultName: Name of the Key Vault where secrets are stored.
   * TenantId: Tenant ID where the Key Vault is located.
   * BaseURL: Enter the base URL of your Vectra account.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraGenerateAccessToken%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraGenerateAccessToken%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize Connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select keyvault connection resource.
2. Go to General → Edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps for other connections.

#### b. Add Access Policy in Key Vault

Add access policy for the playbook's managed identity and authorized user to read and write secrets of the Key Vault.
1. Go to Logic App → *your Logic App* → Identity → System assigned Managed identity and copy Object (principal) ID.
2. Go to Key Vaults → *your Key Vault* → Access policies → Create.
3. Select all keys & secrets permissions. Click next.
4. In the principal section, search by copied Object ID. Click next.
5. Click review + create.
6. Repeat the above steps 2 to 5 to add access policy for the user account using which connection is authorized.
