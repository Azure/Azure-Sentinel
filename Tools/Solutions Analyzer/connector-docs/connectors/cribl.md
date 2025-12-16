# Cribl

| | |
|----------|-------|
| **Connector ID** | `Cribl` |
| **Publisher** | Cribl |
| **Tables Ingested** | [`CriblAccess_CL`](../tables-index.md#criblaccess_cl), [`CriblAudit_CL`](../tables-index.md#criblaudit_cl), [`CriblInternal_CL`](../tables-index.md#criblinternal_cl), [`CriblUIAccess_CL`](../tables-index.md#cribluiaccess_cl) |
| **Used in Solutions** | [Cribl](../solutions/cribl.md) |
| **Connector Definition Files** | [Connector_Cribl.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cribl/Data%20Connectors/Connector_Cribl.json) |

The [Cribl](https://cribl.io/accelerate-cloud-migration/) connector allows you to easily connect your Cribl (Cribl Enterprise Edition - Standalone) logs with Microsoft Sentinel. This gives you more security insight into your organization's data pipelines.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Installation and setup instructions for Cribl Stream for Microsoft Sentinel**

Use the documentation from this Github repository and configure Cribl Stream using 

https://docs.cribl.io/stream/usecase-azure-workspace/

[← Back to Connectors Index](../connectors-index.md)
