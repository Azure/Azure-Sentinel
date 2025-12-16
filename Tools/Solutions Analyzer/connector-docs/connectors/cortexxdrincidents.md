# Cortex XDR - Incidents

| | |
|----------|-------|
| **Connector ID** | `CortexXDRIncidents` |
| **Publisher** | DEFEND Ltd. |
| **Tables Ingested** | [`PaloAltoCortexXDR_Incidents_CL`](../tables-index.md#paloaltocortexxdr_incidents_cl) |
| **Used in Solutions** | [Cortex XDR](../solutions/cortex-xdr.md) |
| **Connector Definition Files** | [CortexXDR_DataConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cortex%20XDR/Data%20Connectors/CortexXDR_DataConnector.json) |

Custom Data connector from DEFEND to utilise the Cortex API to ingest incidents from Cortex XDR platform into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

**Custom Permissions:**
- **Cortex API credentials**: **Cortex API Token** is required for REST API. [See the documentation to learn more about API](https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api.html). Check all requirements and follow the instructions for obtaining credentials.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Enable Cortex XDR API**

Connect Cortex XDR to Microsoft Sentinel via Cortex API to process Cortex Incidents.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `APIKey`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
