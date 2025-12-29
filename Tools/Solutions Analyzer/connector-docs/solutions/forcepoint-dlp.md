# Forcepoint DLP

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2022-05-09 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20DLP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20DLP) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Forcepoint DLP](../connectors/forcepoint-dlp.md)

**Publisher:** Forcepoint

The Forcepoint DLP (Data Loss Prevention) connector allows you to automatically export DLP incident data from Forcepoint DLP into Microsoft Sentinel in real-time. This enriches visibility into user activities and data loss incidents, enables further correlation with data from Azure workloads and other feeds, and improves monitoring capability with Workbooks inside Microsoft Sentinel.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Follow step by step instructions in the [Forcepoint DLP documentation for Microsoft Sentinel](https://frcpnt.com/dlp-sentinel) to configure this connector.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `ForcepointDLPEvents_CL` |
| **Connector Definition Files** | [Forcepoint%20DLP.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20DLP/Data%20Connectors/Forcepoint%20DLP.json) |

[→ View full connector details](../connectors/forcepoint-dlp.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ForcepointDLPEvents_CL` | [Forcepoint DLP](../connectors/forcepoint-dlp.md) |

[← Back to Solutions Index](../solutions-index.md)
