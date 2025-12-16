# Theom

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Theom |
| **Support Tier** | Partner |
| **Support Link** | [https://www.theom.ai](https://www.theom.ai) |
| **Categories** | domains |
| **First Published** | 2022-11-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Theom](../connectors/theom.md)

**Publisher:** Theom

Theom Data Connector enables organizations to connect their Theom environment to Microsoft Sentinel. This solution enables users to receive alerts on data security risks, create and enrich incidents, check statistics and trigger SOAR playbooks in Microsoft Sentinel

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

1. In **Theom UI Console** click on **Manage -> Alerts** on the side bar.
2. Select  **Sentinel** tab.
3. Click on **Active** button to enable the configuration.
4. Enter `Primary` key as `Authorization Token`
5. Enter `Endpoint URL` as `https://<Workspace ID>.ods.opinsights.azure.com/api/logs?api-version=2016-04-01`
6. Click on `SAVE SETTINGS`
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `TheomAlerts_CL` |
| **Connector Definition Files** | [Theom.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Theom/Data%20Connectors/Theom.json) |

[→ View full connector details](../connectors/theom.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `TheomAlerts_CL` | [Theom](../connectors/theom.md) |

[← Back to Solutions Index](../solutions-index.md)
