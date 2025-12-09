# GitHub (using Webhooks)

| | |
|----------|-------|
| **Connector ID** | `GitHubWebhook` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`githubscanaudit_CL`](../tables-index.md#githubscanaudit_cl) |
| **Used in Solutions** | [GitHub](../solutions/github.md) |
| **Connector Definition Files** | [GithubWebhook_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitHub/Data%20Connectors/GithubWebhook/GithubWebhook_API_FunctionApp.json) |

The [GitHub](https://www.github.com) webhook data connector provides the capability to ingest GitHub subscribed events into Microsoft Sentinel using [GitHub webhook events](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads). The connector provides ability to get events into Microsoft Sentinel which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more. 



 **Note:** If you are intended to ingest Github Audit logs, Please refer to GitHub Enterprise Audit Log Connector from "**Data Connectors**" gallery.

[← Back to Connectors Index](../connectors-index.md)
