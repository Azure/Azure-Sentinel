# Red Canary Threat Detection

| | |
|----------|-------|
| **Connector ID** | `RedCanaryDataConnector` |
| **Publisher** | Red Canary |
| **Tables Ingested** | [`RedCanaryDetections_CL`](../tables-index.md#redcanarydetections_cl) |
| **Used in Solutions** | [Red Canary](../solutions/red-canary.md) |
| **Connector Definition Files** | [RedCanaryDataConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Red%20Canary/Data%20Connectors/RedCanaryDataConnector.json) |

The Red Canary data connector provides the capability to ingest published Detections into Microsoft Sentinel using the Data Collector REST API.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Create an Automate Playbook and Trigger as detailed in [this article](https://help.redcanary.com/hc/en-us/articles/4410957523479-Azure-Sentinel). You can skip the **Add analysis rule to Microsoft Sentinel** section; this data connector allows you to import the analysis rule directly into your workspace.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
