# Atlassian Confluence

| | |
|----------|-------|
| **Connector ID** | `AtlassianConfluence` |
| **Publisher** | Atlassian |
| **Tables Ingested** | [`AtlassianConfluenceNativePoller_CL`](../tables-index.md#atlassianconfluencenativepoller_cl) |
| **Used in Solutions** | [AtlassianConfluenceAudit](../solutions/atlassianconfluenceaudit.md) |
| **Connector Definition Files** | [azuredeploy_Confluence_native_poller_connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianConfluenceAudit/Data%20Connectors/ConfluenceNativePollerConnector/azuredeploy_Confluence_native_poller_connector.json) |

The Atlassian Confluence data connector provides the capability to ingest [Atlassian Confluence audit logs](https://developer.atlassian.com/cloud/confluence/rest/api-group-audit/) into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

**Custom Permissions:**
- **Atlassian Confluence API credentials**: Confluence Username and Confluence Access Token are required. [See the documentation to learn more about Atlassian Confluence API](https://developer.atlassian.com/cloud/confluence/rest/intro/). Confluence domain must be provided as well.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Atlassian Confluence**

Please insert your credentials
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `BasicAuth`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
