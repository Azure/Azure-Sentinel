# SlackAudit

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-03-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit) |

## Data Connectors

This solution provides **3 data connector(s)**.

### [Slack](../connectors/slackaudit.md)

**Publisher:** Slack

The [Slack](https://slack.com) data connector provides the capability to ingest [Slack Audit Records](https://api.slack.com/admins/audit-logs) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://api.slack.com/admins/audit-logs#the_audit_event) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more. This data connector uses Microsoft Sentinel native polling capability.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SlackAuditNativePoller_CL` |
| **Connector Definition Files** | [azuredeploy_Slack_native_poller_connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Data%20Connectors/SlackNativePollerConnector/azuredeploy_Slack_native_poller_connector.json) |

[→ View full connector details](../connectors/slackaudit.md)

### [[DEPRECATED] Slack Audit](../connectors/slackauditapi.md)

**Publisher:** Slack

The [Slack](https://slack.com) Audit data connector provides the capability to ingest [Slack Audit Records](https://api.slack.com/admins/audit-logs) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://api.slack.com/admins/audit-logs#the_audit_event) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SlackAudit_CL` |
| **Connector Definition Files** | [SlackAudit_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Data%20Connectors/SlackAudit_API_FunctionApp.json) |

[→ View full connector details](../connectors/slackauditapi.md)

### [SlackAudit (via Codeless Connector Framework)](../connectors/slackauditlogsccpdefinition.md)

**Publisher:** Microsoft

The SlackAudit data connector provides the capability to ingest [Slack Audit logs](https://api.slack.com/admins/audit-logs) into Microsoft Sentinel through the REST API. Refer to [API documentation](https://api.slack.com/admins/audit-logs-call) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SlackAuditV2_CL` |
| **Connector Definition Files** | [SlackAuditLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlackAudit/Data%20Connectors/SlackAuditLog_CCP/SlackAuditLog_ConnectorDefinition.json) |

[→ View full connector details](../connectors/slackauditlogsccpdefinition.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SlackAuditNativePoller_CL` | [Slack](../connectors/slackaudit.md) |
| `SlackAuditV2_CL` | [SlackAudit (via Codeless Connector Framework)](../connectors/slackauditlogsccpdefinition.md) |
| `SlackAudit_CL` | [[DEPRECATED] Slack Audit](../connectors/slackauditapi.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.5       | 12-12-2025                     | Updated the **Parser** yaml file. |
| 3.0.4       | 28-07-2025                     | Removed Deprecated **Data Connector**. |
| 3.0.3       | 30-06-2025                     | Moving **CCF Data Connector** to GA. |
| 3.0.2       | 30-05-2025                     | Preview tag added to **CCF Data Connector**. |
| 3.0.1       | 24-04-2025                     | Migrated the **Function app Connector** to **CCP Data Connector** and Updated the **Parser**. |
| 3.0.0       | 23-08-2023                     | Manual deployment instructions updated for **Data Connector** & Convert **Parser** from text to yaml. |

[← Back to Solutions Index](../solutions-index.md)
