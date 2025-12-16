# ContrastADR

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Contrast Security |
| **Support Tier** | Partner |
| **Support Link** | [https://support.contrastsecurity.com/hc/en-us](https://support.contrastsecurity.com/hc/en-us) |
| **Categories** | domains |
| **First Published** | 2025-01-18 |
| **Last Updated** | 2025-01-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [ContrastADR](../connectors/contrastadr.md)

**Publisher:** Contrast Security

The ContrastADR data connector provides the capability to ingest Contrast ADR attack events into Microsoft Sentinel using the ContrastADR Webhook. ContrastADR data connector can enrich the incoming webhook data with ContrastADR API enrichment calls.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).

**Setup Instructions:**

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

| | |
|--------------------------|---|
| **Tables Ingested** | `ContrastADRIncident_CL` |
| | `ContrastADR_CL` |
| **Connector Definition Files** | [ContrastADR_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Data%20Connectors/ContrastADR_API_FunctionApp.json) |

[→ View full connector details](../connectors/contrastadr.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ContrastADRIncident_CL` | [ContrastADR](../connectors/contrastadr.md) |
| `ContrastADR_CL` | [ContrastADR](../connectors/contrastadr.md) |

[← Back to Solutions Index](../solutions-index.md)
