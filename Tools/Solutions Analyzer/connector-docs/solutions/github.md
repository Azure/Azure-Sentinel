# GitHub

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub) |

## Data Connectors

This solution provides **3 data connector(s)**.

### [GitHub Enterprise Audit Log (via Codeless Connector Framework) (Preview)](../connectors/githubauditdefinitionv2.md)

**Publisher:** Microsoft

### [[Deprecated] GitHub Enterprise Audit Log](../connectors/githubecauditlogpolling.md)

**Publisher:** GitHub

### [GitHub (using Webhooks)](../connectors/githubwebhook.md)

**Publisher:** Microsoft

The [GitHub](https://www.github.com) webhook data connector provides the capability to ingest GitHub subscribed events into Microsoft Sentinel using [GitHub webhook events](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads). The connector provides ability to get events into Microsoft Sentinel which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more. 



 **Note:** If you are intended to ingest Github Audit logs, Please refer to GitHub Enterprise Audit Log Connector from "**Data Connectors**" gallery.

| | |
|--------------------------|---|
| **Tables Ingested** | `githubscanaudit_CL` |
| **Connector Definition Files** | [GithubWebhook_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Data%20Connectors/GithubWebhook/GithubWebhook_API_FunctionApp.json) |

[→ View full connector details](../connectors/githubwebhook.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GitHubAuditLogPolling_CL` | [[Deprecated] GitHub Enterprise Audit Log](../connectors/githubecauditlogpolling.md) |
| `GitHubAuditLogsV2_CL` | [GitHub Enterprise Audit Log (via Codeless Connector Framework) (Preview)](../connectors/githubauditdefinitionv2.md) |
| `githubscanaudit_CL` | [GitHub (using Webhooks)](../connectors/githubwebhook.md) |

[← Back to Solutions Index](../solutions-index.md)
