# Cognni

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `CognniSentinelDataConnector` |
| **Publisher** | Cognni |
| **Used in Solutions** | [Cognni](../solutions/cognni.md) |
| **Collection Method** | Unknown (Custom Log) |
| **Connector Definition Files** | [CognniSentinelConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cognni/Data%20Connectors/CognniSentinelConnector.json) |

The Cognni connector offers a quick and simple integration with Microsoft Sentinel. You can use Cognni to autonomously map your previously unclassified important information and detect related incidents. This allows you to recognize risks to your important information, understand the severity of the incidents, and investigate the details you need to remediate, fast enough to make a difference.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`CognniIncidents_CL`](../tables/cognniincidents-cl.md) | — | — |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect to Cognni**

1. Go to [Cognni integrations page](https://intelligence.cognni.ai/integrations)
2. Click **'Connect'** on the 'Microsoft Sentinel' box
3. Copy and paste **'workspaceId'** and **'sharedKey'** (from below) to the related fields on Cognni's integrations screen
4. Click the **'Connect'** botton to complete the configuration.  
  Soon, all your Cognni-detected incidents will be forwarded here (into Microsoft Sentinel)

Not a Cognni user? [Join us](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/shieldox.appsource_freetrial)
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Shared Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
