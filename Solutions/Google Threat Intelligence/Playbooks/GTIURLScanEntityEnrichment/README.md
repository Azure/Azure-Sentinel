# Google Threat Intelligence URLScan Entity Enrichment

## Summary

This playbook is triggered from a URL entity on a Microsoft Sentinel incident. It submits the URL to the Google Threat Intelligence (GTI) private API for scanning, polls the analysis until it completes, and retrieves the full URL report. The report is ingested into the GTI_URLScan_CL custom table via a DCE/DCR, and an enrichment comment is posted on the associated incident through the GTIAddCommentToIncident sub-playbook.

### Prerequisites

1. Deploy the GTIAddCommentToIncident playbook before deploying this playbook.
2. Obtain a GTI (VirusTotal) API key and store it in Azure Key Vault as a secret named 'GTIApiKey' (or update the KeyVaultSecretName parameter to match).
3. Create or identify an Azure Key Vault and note its name.
4. Ensure you have a Log Analytics Workspace configured for Microsoft Sentinel.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here (default: GTIURLScanEntityEnrichment).
   * KeyVaultName: Name of the Azure Key Vault that stores the GTI API key.
   * KeyVaultSecretName: Name of the Key Vault secret that holds the GTI (VirusTotal) API key (default: GTIApiKey).
   * WorkspaceName: Name of the Log Analytics workspace for GTI_URLScan_CL ingestion.
   * GTIAddCommentPlaybookName: Name of the deployed GTIAddCommentToIncident playbook (default: GTIAddCommentToIncident).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTIURLScanEntityEnrichment%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTIURLScanEntityEnrichment%2Fazuredeploy.json)

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

#### c. Attach to URL Entity

This playbook runs against a URL entity on an incident.
1. On an incident's Entities tab, right-click a URL entity.
2. Select Run playbook, and choose GTIURLScanEntityEnrichment.
3. Confirm the enrichment comment appears on the incident after the run completes.
