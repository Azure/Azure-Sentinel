# Google Threat Intelligence - URL Scan Enrichment

## Summary

This playbook is triggered by an HTTP POST request, typically invoked manually, from a workbook, or from another playbook, with a URL to analyze. It submits the URL to the GTI (VirusTotal) private scanning API, then polls the analysis status with a progressive back-off (30s → 60s → 120s, up to 30 minutes) until the scan completes. Once complete, it retrieves the full URL report using the URL ID returned in the analysis metadata and ingests the complete report data into the custom `GTI_URLScan_CL` table via a Data Collection Endpoint/Rule. This gives analysts a persisted, queryable GTI verdict, threat score, and full scan detail for any URL submitted for investigation, without leaving Sentinel.

### Prerequisites

1. A Key Vault must exist containing the GTI (VirusTotal) API key as a secret (default secret name: `GTIApiKey`).
2. The Key Vault must have `enabledForTemplateDeployment` set to `true`.
3. A Log Analytics Workspace must be configured for Microsoft Sentinel; the playbook creates and ingests into the `GTI_URLScan_CL` custom table in this workspace.
4. Note the Key Vault name — it is required as a deployment parameter.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here (default: GTIURLScanEnrichment).
   * KeyVaultName: Name of the Azure Key Vault that stores the GTI API key (no default — must be provided).
   * KeyVaultSecretName: Name of the Key Vault secret that holds the GTI (VirusTotal) API key (default: GTIApiKey).
   * WorkspaceName: Name of the Log Analytics workspace for `GTI_URLScan_CL` ingestion (no default — must be provided).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTIURLScanEnrichment%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTIURLScanEnrichment%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize the connection.
1. Go to your logic app → API connections → Select the Key Vault connection resource.
2. Go to General → edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.

#### b. Grant Key Vault access to the Logic App managed identity

The playbook's managed identity must be able to read the GTI API key secret.
1. Go to logic app → *your logic app* → identity → System assigned Managed identity and copy Object (principal) ID.
2. Go to your Key Vault → Access control (IAM) → Add role assignment.
3. Select the 'Key Vault Secrets User' role. Click next.
4. In the members section, search by the copied object ID. Click next.
5. Click review + assign.

Note: the 'Monitoring Metrics Publisher' role required on the Data Collection Rule (for ingestion into `GTI_URLScan_CL`) is assigned automatically by this template — no manual action is needed for that role.

#### c. Wire Up the Trigger

This playbook is triggered by an HTTP Request, so it must be called explicitly.
1. Go to logic app → *your logic app* → the "manual" trigger, and copy the HTTP POST URL.
2. Call it with a JSON body containing at minimum `url` (required), and optionally `user_agent` and `storage_region` (one of "", "US", "CA", "EU", "GB").
3. Use this callback URL from a workbook button, another playbook, or a manual test call (e.g. via Postman or curl) to submit a URL for GTI scanning and enrichment.
