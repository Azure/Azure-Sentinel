# Forcepoint DLP

| | |
|----------|-------|
| **Connector ID** | `Forcepoint_DLP` |
| **Publisher** | Forcepoint |
| **Tables Ingested** | [`ForcepointDLPEvents_CL`](../tables-index.md#forcepointdlpevents_cl) |
| **Used in Solutions** | [Forcepoint DLP](../solutions/forcepoint-dlp.md) |
| **Connector Definition Files** | [Forcepoint%20DLP.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20DLP/Data%20Connectors/Forcepoint%20DLP.json) |

The Forcepoint DLP (Data Loss Prevention) connector allows you to automatically export DLP incident data from Forcepoint DLP into Microsoft Sentinel in real-time. This enriches visibility into user activities and data loss incidents, enables further correlation with data from Azure workloads and other feeds, and improves monitoring capability with Workbooks inside Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Follow step by step instructions in the [Forcepoint DLP documentation for Microsoft Sentinel](https://frcpnt.com/dlp-sentinel) to configure this connector.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
