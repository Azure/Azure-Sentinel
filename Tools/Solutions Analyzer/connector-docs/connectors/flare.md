# Flare

| | |
|----------|-------|
| **Connector ID** | `Flare` |
| **Publisher** | Flare |
| **Tables Ingested** | [`Firework_CL`](../tables-index.md#firework_cl) |
| **Used in Solutions** | [Flare](../solutions/flare.md) |
| **Connector Definition Files** | [Connector_REST_API_FlareSystemsFirework.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Flare/Data%20Connectors/Connector_REST_API_FlareSystemsFirework.json) |

[Flare](https://flare.systems/platform/) connector allows you to receive data and intelligence from Flare on Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Required Flare permissions**: only Flare organization administrators may configure the Microsoft Sentinel integration.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Creating an Alert Channel for Microsoft Sentinel**
As an organization administrator, authenticate on [Flare](https://app.flare.systems) and access the [team page](https://app.flare.systems#/team) to create a new alert channel.

  Click on 'Create a new alert channel' and select 'Microsoft Sentinel'. Enter your Shared Key And WorkspaceID. Save the Alert Channel. 
 For more help and details, see our [Azure configuration documentation](https://docs.microsoft.com/azure/sentinel/connect-data-sources).
  - **Workspace ID**: `{0}`
  - **Primary key**: `{0} `
**2. Associating your alert channel to an alert feed**
At this point, you may configure alerts to be sent to Microsoft Sentinel the same way that you would configure regular email alerts.

  For a more detailed guide, refer to the Flare documentation.

[← Back to Connectors Index](../connectors-index.md)
