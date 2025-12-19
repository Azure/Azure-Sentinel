# Wiz

| | |
|----------|-------|
| **Connector ID** | `Wiz` |
| **Publisher** | Wiz |
| **Tables Ingested** | [`WizAuditLogsV2_CL`](../tables-index.md#wizauditlogsv2_cl), [`WizAuditLogs_CL`](../tables-index.md#wizauditlogs_cl), [`WizIssuesV2_CL`](../tables-index.md#wizissuesv2_cl), [`WizIssues_CL`](../tables-index.md#wizissues_cl), [`WizVulnerabilitiesV2_CL`](../tables-index.md#wizvulnerabilitiesv2_cl), [`WizVulnerabilities_CL`](../tables-index.md#wizvulnerabilities_cl) |
| **Used in Solutions** | [Wiz](../solutions/wiz.md) |
| **Connector Definition Files** | [template_WIZ.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Wiz/Data%20Connectors/template_WIZ.json) |

The Wiz connector allows you to easily send Wiz Issues, Vulnerability Findings, and Audit logs to Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Wiz Service Account credentials**: Ensure you have your Wiz service account client ID and client secret, API endpoint URL, and auth URL. Instructions can be found on [Wiz documentation](https://docs.wiz.io/wiz-docs/docs/azure-sentinel-native-integration#collect-authentication-info-from-wiz).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector: Uses Azure Functions to connect to Wiz API to pull Wiz Issues, Vulnerability Findings, and Audit Logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.
Creates an Azure Key Vault with all the required parameters stored as secrets.

**1. STEP 1 - Get your Wiz credentials**

Follow the instructions on [Wiz documentation](https://docs.wiz.io/wiz-docs/docs/azure-sentinel-native-integration#collect-authentication-info-from-wiz) to get the erquired credentials.

**2. STEP 2 - Deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Wiz Connector, have the Workspace ID and Workspace Primary Key (can be copied from the following), as well as the Wiz credentials from the previous step.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Option 1: Deploy using the Azure Resource Manager (ARM) Template**

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-wiz-azuredeploy) 
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the following parameters: 
> - Choose **KeyVaultName** and **FunctionName** for the new resources 
 >- Enter the following Wiz credentials from step 1: **WizAuthUrl**, **WizEndpointUrl**, **WizClientId**, and **WizClientSecret** 
>- Enter the Workspace credentials **AzureLogsAnalyticsWorkspaceId** and **AzureLogAnalyticsWorkspaceSharedKey**
>- Choose the Wiz data types you want to send to Microsoft Sentinel, choose at least one from **Wiz Issues**, **Vulnerability Findings**, and **Audit Logs**.
 
>- (optional) follow [Wiz documentation](https://docs.wiz.io/wiz-docs/docs/azure-sentinel-native-integration#optional-create-a-filter-for-wiz-queries) to add **IssuesQueryFilter**, **VulnerbailitiesQueryFilter**, and **AuditLogsQueryFilter**.
 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**4. Option 2: Manual Deployment of the Azure Function**

>Follow [Wiz documentation](https://docs.wiz.io/wiz-docs/docs/azure-sentinel-native-integration#manual-deployment) to deploy the connector manually.

[← Back to Connectors Index](../connectors-index.md)
