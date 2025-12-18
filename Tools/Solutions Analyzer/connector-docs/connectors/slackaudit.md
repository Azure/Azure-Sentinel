# Slack

| | |
|----------|-------|
| **Connector ID** | `SlackAudit` |
| **Publisher** | Slack |
| **Tables Ingested** | [`SlackAuditNativePoller_CL`](../tables-index.md#slackauditnativepoller_cl) |
| **Used in Solutions** | [SlackAudit](../solutions/slackaudit.md) |
| **Connector Definition Files** | [azuredeploy_Slack_native_poller_connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Data%20Connectors/SlackNativePollerConnector/azuredeploy_Slack_native_poller_connector.json) |

The [Slack](https://slack.com) data connector provides the capability to ingest [Slack Audit Records](https://api.slack.com/admins/audit-logs) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://api.slack.com/admins/audit-logs#the_audit_event) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more. This data connector uses Microsoft Sentinel native polling capability.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

**Custom Permissions:**
- **Slack API credentials**: **SlackAPIBearerToken** is required for REST API. [See the documentation to learn more about API](https://api.slack.com/web#authentication). Check all [requirements and follow the instructions](https://api.slack.com/web#authentication) for obtaining credentials.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Slack to Microsoft Sentinel**

Enable Slack audit Logs.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `APIKey`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
