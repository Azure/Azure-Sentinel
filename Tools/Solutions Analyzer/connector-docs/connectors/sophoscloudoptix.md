# Sophos Cloud Optix

| | |
|----------|-------|
| **Connector ID** | `SophosCloudOptix` |
| **Publisher** | Sophos |
| **Tables Ingested** | [`SophosCloudOptix_CL`](../tables-index.md#sophoscloudoptix_cl) |
| **Used in Solutions** | [Sophos Cloud Optix](../solutions/sophos-cloud-optix.md) |
| **Connector Definition Files** | [Connector_REST_API_SophosCloudOptix.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20Cloud%20Optix/Data%20Connectors/Connector_REST_API_SophosCloudOptix.json) |

The [Sophos Cloud Optix](https://www.sophos.com/products/cloud-optix.aspx) connector allows you to easily connect your Sophos Cloud Optix logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's cloud security and compliance posture and improves your cloud security operation capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Get the Workspace ID and the Primary Key**

Copy the Workspace ID and Primary Key for your workspace.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**2. Configure the Sophos Cloud Optix Integration**

In Sophos Cloud Optix go to [Settings->Integrations->Microsoft Sentinel](https://optix.sophos.com/#/integrations/sentinel) and enter the Workspace ID and Primary Key copied in Step 1.

**3. Select Alert Levels**

In Alert Levels, select which Sophos Cloud Optix alerts you want to send to Microsoft Sentinel.

**4. Turn on the integration**

To turn on the integration, select Enable, and then click Save.

[← Back to Connectors Index](../connectors-index.md)
