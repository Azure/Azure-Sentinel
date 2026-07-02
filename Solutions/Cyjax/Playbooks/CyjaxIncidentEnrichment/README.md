# Cyjax Incident Enrichment

## Summary

This playbook is triggered manually or automatically from an incident in Microsoft Sentinel. It iterates through each entity in the incident (IP addresses, DNS/Domain names, file hashes, URLs, and Emails) and enriches them with threat intelligence data from the Cyjax API. The enrichment data is formatted and added as an incident comment via the CyjaxAddCommentToIncident sub-playbook, providing security analysts with comprehensive threat context directly within the incident.

### Prerequisites

1. Deploy the CyjaxAddCommentToIncident playbook before deploying this playbook.
2. Obtain a Cyjax API key and store it in Azure Key Vault as a secret named 'Cyjax-API-Key'.
3. Create or identify an Azure Key Vault and note its name and Tenant ID.
4. Ensure you have a Log Analytics Workspace configured for Microsoft Sentinel.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here (default: CyjaxIncidentEnrichment).
   * CyjaxBaseUrl: Base URL for the Cyjax API (default: https://api.cymon.co).
   * AddIncidentCommentPlaybookName: Name of the deployed CyjaxAddCommentToIncident playbook (default: CyjaxAddCommentToIncident).
   * KeyVaultName: Name of the Azure Key Vault where the Cyjax API key is stored.
   * TenantId: Microsoft Entra ID Tenant ID where the Key Vault is located.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCyjax%2FPlaybooks%2FCyjaxIncidentEnrichment%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCyjax%2FPlaybooks%2FCyjaxIncidentEnrichment%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select Microsoft Sentinel connection resource.
2. Go to General → edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps for Key Vault connection.

#### b. Add Access policy in Keyvault

Add access policy for the playbook's managed identity to read secrets from Key Vault.
1. Go to logic app → *your logic app* → identity → System assigned Managed identity and copy Object (principal) ID.
2. Go to keyvaults → *your keyvault* → Access policies → create.
3. Select Get and List permissions for Secrets. Click next.
4. In the principal section, search by copied object ID. Click next.
5. Click review + create.

#### c. Attach to Automation Rule or Manual Trigger

Configure how this playbook will be triggered:
1. **For Automatic Enrichment**: Create an automation rule in Microsoft Sentinel that triggers this playbook when incidents are created or updated.
2. **For Manual Enrichment**: Run the playbook manually from the incident page by selecting "Run playbook" and choosing CyjaxIncidentEnrichment.
3. Verify that the CyjaxAddCommentToIncident sub-playbook is accessible and properly configured.
