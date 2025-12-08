# Slack

| | |
|----------|-------|
| **Connector ID** | `SlackAudit` |
| **Publisher** | Slack |
| **Tables Ingested** | [`SlackAuditNativePoller_CL`](../tables-index.md#slackauditnativepoller_cl) |
| **Used in Solutions** | [SlackAudit](../solutions/slackaudit.md) |
| **Connector Definition Files** | [azuredeploy_Slack_native_poller_connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Data%20Connectors/SlackNativePollerConnector/azuredeploy_Slack_native_poller_connector.json) |

The [Slack](https://slack.com) data connector provides the capability to ingest [Slack Audit Records](https://api.slack.com/admins/audit-logs) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://api.slack.com/admins/audit-logs#the_audit_event) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more. This data connector uses Microsoft Sentinel native polling capability.

[← Back to Connectors Index](../connectors-index.md)
