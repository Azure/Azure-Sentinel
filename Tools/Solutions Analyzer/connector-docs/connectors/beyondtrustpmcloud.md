# BeyondTrust PM Cloud

| | |
|----------|-------|
| **Connector ID** | `BeyondTrustPMCloud` |
| **Publisher** | BeyondTrust |
| **Tables Ingested** | [`BeyondTrustPM_ActivityAudits_CL`](../tables-index.md#beyondtrustpm_activityaudits_cl), [`BeyondTrustPM_ClientEvents_CL`](../tables-index.md#beyondtrustpm_clientevents_cl) |
| **Used in Solutions** | [BeyondTrustPMCloud](../solutions/beyondtrustpmcloud.md) |
| **Connector Definition Files** | [BeyondTrustPMCloud_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BeyondTrustPMCloud/Data%20Connectors/BeyondTrustPMCloud_API_FunctionApp.json) |

The BeyondTrust Privilege Management Cloud data connector provides the capability to ingest activity audit logs and client event logs from BeyondTrust PM Cloud into Microsoft Sentinel.



This connector uses Azure Functions to pull data from the BeyondTrust PM Cloud API and ingest it into custom Log Analytics tables.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **BeyondTrust PM Cloud API credentials**: BeyondTrust PM Cloud OAuth Client ID and Client Secret are required. Contact BeyondTrust support for API access.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the BeyondTrust PM Cloud API to pull logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**NOTE:** This connector uses the OAuth 2.0 client credentials flow to authenticate with the BeyondTrust PM Cloud API.

**1. STEP 1 - Obtain BeyondTrust PM Cloud API credentials**

Contact BeyondTrust support to obtain OAuth API credentials (Client ID and Client Secret) for accessing the BeyondTrust PM Cloud API.

**2. STEP 2 - Deploy the connector and the associated Azure Function**

Use this method for automated deployment of the BeyondTrust PM Cloud data connector using an ARM Template.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FBeyondTrustPMCloud%2FData%2520Connectors%2Fazuredeploy_BeyondTrustPMCloud_API_FunctionApp.json)
2. Select the preferred **Subscription**, **Resource Group** (must contain your Log Analytics workspace), and **Location**. 
3. Enter the required parameters:
   - **Workspace Name**: Name of your Log Analytics workspace (e.g., `beyondtrust-pmcloud`)
   - **BeyondTrust PM Cloud Base URL**: Your tenant URL (e.g., `https://yourcompany.beyondtrustcloud.com`)
   - **BeyondTrust Client ID**: OAuth Client ID from Step 1
   - **BeyondTrust Client Secret**: OAuth Client Secret from Step 1
   - **Activity Audits Polling Interval**: How often to collect Activity Audits (default: 15 minutes)
   - **Client Events Polling Interval**: How often to collect Client Events (default: 5 minutes)
   - **Log Level**: Logging level for troubleshooting (default: Information)
   - **Historical Data Timeframe**: How far back to collect data on first run (default: 1 day)
4. Review advanced settings (Hosting Plan SKU, Storage Account Type) and adjust if needed.
5. Mark the checkbox labeled **I agree to the terms and conditions stated above**.
6. Click **Purchase** to deploy.
7. The deployment creates all required resources: Function App, Storage Account, Data Collection Endpoint, Data Collection Rules, and custom Log Analytics tables.
8. Data should begin flowing within 15-30 minutes of deployment.

[← Back to Connectors Index](../connectors-index.md)
