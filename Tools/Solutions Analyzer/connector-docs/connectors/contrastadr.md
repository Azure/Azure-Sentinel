# ContrastADR

| | |
|----------|-------|
| **Connector ID** | `ContrastADR` |
| **Publisher** | Contrast Security |
| **Tables Ingested** | [`ContrastADRIncident_CL`](../tables-index.md#contrastadrincident_cl), [`ContrastADR_CL`](../tables-index.md#contrastadr_cl) |
| **Used in Solutions** | [ContrastADR](../solutions/contrastadr.md) |
| **Connector Definition Files** | [ContrastADR_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Data%20Connectors/ContrastADR_API_FunctionApp.json) |

The ContrastADR data connector provides the capability to ingest Contrast ADR attack events into Microsoft Sentinel using the ContrastADR Webhook. ContrastADR data connector can enrich the incoming webhook data with ContrastADR API enrichment calls.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Use these Workspace id and primakey key as shared key in azure function app
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**2. Azure Resource Manager (ARM) Template**

Use this method to automate deployment of the ContrastADR Data Connector using ARM Template.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-ContrastADR-azuredeploy)
2. Provide the following parameters: Region, Function Name, LOG_ANALYTICS_SHARED_KEY, LOG_ANALYTICS_WORKSPACE_ID

[← Back to Connectors Index](../connectors-index.md)
