# Garrison ULTRA

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Garrison |
| **Support Tier** | Partner |
| **Support Link** | [https://support.ultra.garrison.com](https://support.ultra.garrison.com) |
| **Categories** | domains |
| **First Published** | 2024-10-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Garrison%20ULTRA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Garrison%20ULTRA) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Garrison ULTRA Remote Logs](../connectors/garrisonultraremotelogs.md)

**Publisher:** Garrison

The [Garrison ULTRA](https://www.garrison.com/en/garrison-ultra-cloud-platform) Remote Logs connector allows you to ingest Garrison ULTRA Remote Logs into Microsoft Sentinel.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Garrison ULTRA**: To use this data connector you must have an active [Garrison ULTRA](https://www.garrison.com/en/garrison-ultra-cloud-platform) license.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Deployment - Azure Resource Manager (ARM) Template**

These steps outline the automated deployment of the Garrison ULTRA Remote Logs data connector using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FSolutions%2FGarrison%2520ULTRA%2FData%2520Connectors%2FGarrisonULTRARemoteLogs%2Fazuredeploy_DataCollectionResources.json) 			
2. Provide the required details such as Resource Group, Microsoft Sentinel Workspace and ingestion configurations 
> **NOTE:** It is recommended to create a new Resource Group for deployment of these resources.
3. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
4. Click **Purchase** to deploy.

| | |
|--------------------------|---|
| **Tables Ingested** | `Garrison_ULTRARemoteLogs_CL` |
| **Connector Definition Files** | [GarrisonULTRARemoteLogs_ConnectorUI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Garrison%20ULTRA/Data%20Connectors/GarrisonULTRARemoteLogs/GarrisonULTRARemoteLogs_ConnectorUI.json) |

[→ View full connector details](../connectors/garrisonultraremotelogs.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Garrison_ULTRARemoteLogs_CL` | [Garrison ULTRA Remote Logs](../connectors/garrisonultraremotelogs.md) |

[← Back to Solutions Index](../solutions-index.md)
