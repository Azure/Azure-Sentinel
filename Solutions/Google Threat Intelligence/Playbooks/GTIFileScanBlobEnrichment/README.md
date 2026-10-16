# Google Threat Intelligence - FileScan Blob Enrichment

## Summary

This playbook is triggered when a file is added or modified in a monitored Azure Blob Storage container (`When_a_blob_is_added_or_modified`). Files up to 32MB are read directly and submitted to Google Threat Intelligence (GTI/VirusTotal) for file scanning; files larger than 32MB are handed off to the shared GTIFileUpload Azure Function, which uploads them to GTI on the playbook's behalf. The playbook then polls the analysis until it completes, retrieves the file report, and ingests the results into the custom Log Analytics table `GTI_FileScan_CL` via a Data Collection Endpoint/Data Collection Rule (DCE/DCR) for further investigation in Microsoft Sentinel.

### Prerequisites

1. Deploy the GTIFileUpload Function App playbook (`Solutions/Google Threat Intelligence/Playbooks/CustomConnector/GTIFileUpload_FunctionAppConnector/azuredeploy.json`) to this resource group before deploying this playbook, since files larger than 32MB are uploaded to GTI by that Function rather than by this Logic App.
2. Obtain a Google Threat Intelligence API key and store it in Azure Key Vault as a secret (default secret name: `GTIApiKey`).
3. Create or identify an Azure Key Vault and note its name.
4. Ensure you have a Log Analytics Workspace configured for Microsoft Sentinel; the `GTI_FileScan_CL` custom table and its DCE/DCR are created automatically by this template.
5. Identify the Azure Storage Account and container to monitor for new or modified blobs.
6. The Logic App's managed identity requires the 'Storage Blob Data Reader' role on the Storage Account (the `azureblob` connection uses Managed Identity authentication) and the 'Key Vault Secrets User' role on the Key Vault. The GTIFileUpload Function's managed identity also requires 'Storage Blob Data Reader' on the Storage Account.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here (default: GTIFileScanBlobEnrichment).
   * KeyVaultName: Name of the Azure Key Vault containing the GTI API key.
   * KeyVaultSecretName: Name of the Key Vault secret that holds the GTI API key (default: GTIApiKey).
   * StorageAccountName: Name of the Azure Storage Account to monitor for new blobs.
   * ContainerName: Name of the blob container to monitor.
   * TriggerFrequencyMinutes: How often (in minutes) the playbook polls the container for new or modified blobs (default: 5).
   * WorkspaceName: Name of the Log Analytics workspace where GTI_FileScan_CL data will be ingested.
   * FunctionAppName: Name of the shared GTIFileUpload Azure Function App used to upload files larger than 32MB to GTI (default: gtifileupload).
   * DisableSandbox: If true, files will not be detonated in sandbox environments (default: false; allowed: false, true).
   * StorageRegion: GTI storage region for uploaded files; keep 'default' to use the group's private_scanning.storage_region preference (default: default; allowed: default, US, CA, EU, GB).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTIFileScanBlobEnrichment%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTIFileScanBlobEnrichment%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select Keyvault connection resource.
2. Go to General → edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps for the azureblob connection.

#### b. Add Access policy in Keyvault

Add access policy for the playbook's managed identity to read secrets from Key Vault.
1. Go to logic app → *your logic app* → identity → System assigned Managed identity and copy Object (principal) ID.
2. Go to keyvaults → *your keyvault* → Access policies → create.
3. Select Get and List permissions for Secrets. Click next.
4. In the principal section, search by copied object ID. Click next.
5. Click review + create.

#### c. RBAC propagation

The ARM template grants the Logic App's managed identity the Monitoring Metrics Publisher role on the Data Collection Rule automatically. This can take 1-3 minutes to propagate — if the first run returns a 403 on ingestion, wait a few minutes and retry.

#### d. Enable the Blob Trigger

1. Confirm the Storage Account and container specified in the deployment parameters exist and are reachable by the Logic App's managed identity (Storage Blob Data Reader role, required since the azureblob connection uses Managed Identity auth).
2. Upload a test file to the monitored container and confirm a run appears in the Logic App's run history.
