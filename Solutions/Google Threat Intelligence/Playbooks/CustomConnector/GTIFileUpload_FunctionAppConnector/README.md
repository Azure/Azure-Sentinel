# Google Threat Intelligence - Large File Upload Function

## Summary

The GTI Custom Connector's file-upload action is limited to files up to 32MB, so files larger than that cannot be submitted through a standard Logic App action. This Azure Function closes that gap: given a blob location and a GTI API key, it downloads the file itself (using its own system-assigned managed identity, so the content never has to pass through the calling Logic App) and submits it to Google Threat Intelligence via the large-file upload URL flow. It is shared by the GTIFileScanEnrichment and GTIFileScanBlobEnrichment playbooks, which call it as a single HTTP action, passing a reference to the blob to upload.

### Prerequisites

1. A Google Threat Intelligence (VirusTotal) API key.
2. The file to be scanned must already be staged in an Azure Storage Account blob container (e.g. uploaded there by the calling playbook) before invoking this function.
3. A Log Analytics Workspace to use for the Function App's Application Insights instance.
4. After deployment, the Function App's managed identity must be granted the **Storage Blob Data Reader** role on every Storage Account whose blobs will be uploaded via this function.

### Deployment Instructions

1. To deploy the Function App, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * **FunctionAppName**: Name for the Function App (default: `gtifileupload`). A short unique suffix is appended automatically.
   * **GTIBaseUrl**: Base URL for the Google Threat Intelligence API (default: `https://www.virustotal.com`).
   * **AppInsightsWorkspaceResourceID**: Fully qualified resource ID of the Log Analytics workspace to use for Application Insights (format: `/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{workspaceName}`).
   * **LogLevel**: Log verbosity for the Function App (default: `Info`; allowed values: `Debug`, `Info`, `Warning`, `Error`).

The template also provisions a Storage Account (for the Function App's own runtime storage) and an Application Insights component, and deploys the function code from the published release package automatically.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FCustomConnector%2FGTIFileUpload_FunctionAppConnector%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FCustomConnector%2FGTIFileUpload_FunctionAppConnector%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Grant Storage access to the Function App's managed identity

1. Go to each Storage Account that holds files this function will upload.
2. Access Control (IAM) → Add role assignment → select **Storage Blob Data Reader**.
3. Assign it to the Function App's system-assigned managed identity (found under the Function App → Identity).

No API key or connection string needs to be configured on the Function App itself — the GTI API key and the target storage account/container/blob are supplied per-request by the calling playbook, not stored as app settings.

#### b. Retrieve the Function URL and Key

1. Go to the Function App → Functions → **GTIUploadLargeFile** → Get Function Url.
2. Copy the URL including the function key (`code=` query parameter). The function uses function-key authorization (`authLevel: function`), so this key must be included on every call.

#### c. Wire Into a Playbook

Call this Function App from a Logic App/playbook using an HTTP action (`POST`) pointed at the Function URL (including the `code=` key), with a JSON body containing:

* `storageAccountName` (required): name of the Storage Account holding the file.
* `containerName` (required): blob container name.
* `blobPath` (required): path of the blob within the container.
* `apiKey` (required): the GTI API key to use for the upload.
* `disable_sandbox` (optional): boolean to disable sandbox analysis.
* `password` (optional): password for password-protected archives.
* `storage_region` (optional): one of `US`, `CA`, `EU`, `GB`.

The function downloads the blob itself and returns a JSON response `{"analysisId": <string|null>, "statusCode": <int>, "error": <string|null>}`, which the calling playbook can use to track or retrieve the GTI analysis.
