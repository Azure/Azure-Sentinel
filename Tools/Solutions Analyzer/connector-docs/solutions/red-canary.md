# Red Canary

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Red Canary |
| **Support Tier** | Partner |
| **Support Link** | [https://www.redcanary.com](https://www.redcanary.com) |
| **Categories** | domains |
| **First Published** | 2022-03-04 |
| **Last Updated** | 2022-03-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Red%20Canary](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Red%20Canary) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Red Canary Threat Detection](../connectors/redcanarydataconnector.md)

**Publisher:** Red Canary

The Red Canary data connector provides the capability to ingest published Detections into Microsoft Sentinel using the Data Collector REST API.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Create an Automate Playbook and Trigger as detailed in [this article](https://help.redcanary.com/hc/en-us/articles/4410957523479-Azure-Sentinel). You can skip the **Add analysis rule to Microsoft Sentinel** section; this data connector allows you to import the analysis rule directly into your workspace.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `RedCanaryDetections_CL` |
| **Connector Definition Files** | [RedCanaryDataConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Red%20Canary/Data%20Connectors/RedCanaryDataConnector.json) |

[→ View full connector details](../connectors/redcanarydataconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `RedCanaryDetections_CL` | [Red Canary Threat Detection](../connectors/redcanarydataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
