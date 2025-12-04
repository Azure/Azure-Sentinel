# SlackAudit

## Solution Information

| | |
|------------------------|-------|
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

### [[DEPRECATED] Slack Audit](../connectors/slackauditapi.md)

**Publisher:** Slack

### [SlackAudit (via Codeless Connector Framework)](../connectors/slackauditlogsccpdefinition.md)

**Publisher:** Microsoft

The SlackAudit data connector provides the capability to ingest [Slack Audit logs](https://api.slack.com/admins/audit-logs) into Microsoft Sentinel through the REST API. Refer to [API documentation](https://api.slack.com/admins/audit-logs-call) for more information.

| | |
|--------------------------|---|
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

[← Back to Solutions Index](../solutions-index.md)
