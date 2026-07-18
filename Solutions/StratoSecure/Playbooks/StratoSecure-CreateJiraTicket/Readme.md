# StratoSecure — Create Jira Ticket

Creates a Jira bug ticket for each StratoSecure security finding incident triggered in Microsoft Sentinel. The ticket includes incident title, description, severity labels, and is tagged `sentinel`, `stratosecure`, and `appsec`.

## Prerequisites

- Microsoft Sentinel workspace
- Jira Cloud or Server instance accessible from Azure Logic Apps
- Jira API token with create-issue permission on the target project
- StratoSecure Platform API key (generated at client.stratocode.io)

## Post-Deployment Steps

1. Grant the Logic App system-assigned managed identity the **Microsoft Sentinel Responder** role on the Sentinel workspace.
2. Store the `JiraApiToken` in Azure Key Vault and reference it in the parameter.
3. Verify the `JiraProject` key matches an existing project in your Jira instance.

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| PlaybookName | string | Logic App resource name |
| JiraBaseUrl | string | Jira instance base URL (e.g. https://your-org.atlassian.net) |
| JiraProject | string | Jira project key where tickets will be created (default: SEC) |
| JiraApiToken | securestring | Jira API token for authentication |
| JiraUserEmail | string | Email address associated with the Jira API token |
| LogAnalyticsWorkspaceId | string | Workspace ID for audit logging |
| LogAnalyticsWorkspaceKey | securestring | Workspace primary key for audit logging |
| RequireApproval | bool | When true, actions execute only after approval condition evaluates (default: true) |
