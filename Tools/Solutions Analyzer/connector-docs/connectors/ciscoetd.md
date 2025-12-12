# Cisco ETD

| | |
|----------|-------|
| **Connector ID** | `CiscoETD` |
| **Publisher** | Cisco |
| **Tables Ingested** | [`CiscoETD_CL`](../tables-index.md#ciscoetd_cl) |
| **Used in Solutions** | [Cisco ETD](../solutions/cisco-etd.md) |
| **Connector Definition Files** | [CiscoETD_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ETD/Data%20Connectors/CiscoETD_API_FunctionApp.json) |

The connector fetches data from ETD api for threat analysis

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Email Threat Defense API, API key, Client ID and Secret**: Ensure you have the API key, Client ID and Secret key.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the ETD API to pull its logs into Microsoft Sentinel.

**Follow the deployment steps to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the ETD data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following).
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**2. Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the Cisco ETD data connector using an ARM Template.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-CiscoETD-azuredeploy)
2. Select the preferred **Subscription**, **Resource Group** and **Region**. 
3. Enter the **WorkspaceID**, **SharedKey**, **ClientID**, **ClientSecret**, **ApiKey**, **Verdicts**, **ETD Region**
4. Click **Create** to deploy.

[← Back to Connectors Index](../connectors-index.md)
