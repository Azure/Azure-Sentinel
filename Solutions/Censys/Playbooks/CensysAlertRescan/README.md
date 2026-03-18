# Censys Alert Rescan

## Summary

This playbook is triggered manually via HTTP request from a workbook or automation. It accepts input parameters including IOC Type (Host or Web Property), IP, Port, Protocol, Transport Protocol, Hostname, and Alert ID. The playbook initiates a rescan request to the Censys API, monitors scan status until completion, retrieves the updated asset data, and ingests the rescan results into Log Analytics. If the alert is associated with an incident, the playbook invokes the CensysIncidentEnrichment sub-playbook to add the rescan data as an incident comment.

### Prerequisites

1. Deploy the CensysAddIncidentComment playbook before deploying this playbook.
2. Obtain a Censys API token and store it in Azure Key Vault as a secret named 'Censys-Access-Token'.
3. Obtain the Censys Organization ID from your Censys platform account.
4. Create or identify an Azure Key Vault and note its name and Tenant ID.
5. Ensure you have a Log Analytics Workspace configured for Microsoft Sentinel.
6. Configure the Censys workbook to trigger this playbook with required parameters.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here (default: CensysAlertRescan).
   * OrganizationID: Your Censys Organization ID from the Censys platform account settings.
   * KeyVaultName: Name of the Azure Key Vault where the Censys API token is stored.
   * TenantId: Azure AD Tenant ID where the Key Vault is located.
   * WorkspaceName: Name of the Log Analytics Workspace where Microsoft Sentinel is deployed.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCensys%2FPlaybooks%2FCensysAlertRescan%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCensys%2FPlaybooks%2FCensysAlertRescan%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select keyvault connection resource.
2. Go to General → edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps for Azure Monitor Logs and Log Analytics Data Collector connections.

#### b. Add Access policy in Keyvault

Add access policy for the playbook's managed identity to read secrets from Key Vault.
1. Go to logic app → *your logic app* → identity → System assigned Managed identity and copy Object (principal) ID.
2. Go to keyvaults → *your keyvault* → Access policies → create.
3. Select Get and List permissions for Secrets. Click next.
4. In the principal section, search by copied object ID. Click next.
5. Click review + create.

#### c. Configure Workbook Integration

Configure the Censys workbook to call this playbook with the HTTP POST URL and required parameters.
1. Go to Logic App → *your Logic App* → Logic app designer.
2. Copy the HTTP POST URL from the trigger.
3. Configure the Censys workbook to use this URL for triggering rescans.
