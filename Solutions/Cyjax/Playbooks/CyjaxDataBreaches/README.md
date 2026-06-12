# Cyjax Data Breaches

## Summary

This playbook is triggered manually from the Data Breaches tab in the Cyjax Workbook within Microsoft Sentinel. It fetches email credential breach data from the Cyjax API based on user-provided inputs (Query, Since, and Until) and displays the results in the workbook panel. This playbook helps you investigate potential email credential compromises using the Cyjax Data Breaches API.

### Prerequisites

1. Obtain a Cyjax API key and store it in Azure Key Vault as a secret named 'Cyjax-API-Key'.
2. Create or identify an Azure Key Vault and note its name and Tenant ID.
3. Ensure you have a Log Analytics Workspace configured for Microsoft Sentinel.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here (default: CyjaxDataBreaches).
   * CyjaxBaseUrl: Base URL for the Cyjax API (default: https://api.cymon.co).
   * KeyVaultName: Name of the Azure Key Vault where the Cyjax API key is stored.
   * TenantId: Microsoft Entra ID Tenant ID where the Key Vault is located.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCyjax%2FPlaybooks%2FCyjaxDataBreaches%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCyjax%2FPlaybooks%2FCyjaxDataBreaches%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select Keyvault connection resource.
2. Go to General → edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps for Log Analytics Data Collector connection.

#### b. Add Access policy in Keyvault

Add access policy for the playbook's managed identity to read secrets from Key Vault.
1. Go to logic app → *your logic app* → identity → System assigned Managed identity and copy Object (principal) ID.
2. Go to keyvaults → *your keyvault* → Access policies → create.
3. Select Get and List permissions for Secrets. Click next.
4. In the principal section, search by copied object ID. Click next.
5. Click review + create.

#### c. Configure Workbook Integration

Configure the Cyjax workbook to call this playbook with the HTTP POST URL.
1. Go to Logic App → *your Logic App* → Logic app designer.
2. Copy the HTTP POST URL from the trigger.
3. Configure the Cyjax workbook Data Breaches tab to use this URL for querying email credential breaches.
