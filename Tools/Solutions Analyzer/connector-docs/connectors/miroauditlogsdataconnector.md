# Miro Audit Logs (Enterprise Plan)

| | |
|----------|-------|
| **Connector ID** | `MiroAuditLogsDataConnector` |
| **Publisher** | Miro |
| **Tables Ingested** | [`MiroAuditLogs_CL`](../tables-index.md#miroauditlogs_cl) |
| **Used in Solutions** | [Miro](../solutions/miro.md) |
| **Connector Definition Files** | [MiroAuditLogs_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Miro/Data%20Connectors/MiroAuditLogs_CCF/MiroAuditLogs_DataConnectorDefinition.json) |

The [Miro Audit Logs](https://help.miro.com/hc/en-us/articles/360017571434-Audit-logs) data connector enables you to ingest organization-wide audit events from Miro into Microsoft Sentinel. Monitor user activities, security events, content access, team changes, and administrative actions to enhance your security operations and compliance capabilities.



**Key features:**

- Track user authentication and access patterns.

- Monitor content creation, sharing, and deletion.

- Audit team and organization configuration changes.

- Detect suspicious activities and policy violations.

- Meet compliance and regulatory requirements.



**Requirements:**

- **Miro Plan**: [Enterprise Plan](https://miro.com/pricing/).

- **OAuth scope**: `auditlogs:read`.

- **Role**: Company Admin in your Miro organization.



💡 **Not on Enterprise Plan yet?** Upgrade to [Miro Enterprise](https://miro.com/enterprise/) to unlock audit logs and gain comprehensive visibility into your team's activities in Microsoft Sentinel.



For detailed instructions, refer to the [documentation](https://help.miro.com/hc/en-us/articles/31325908249362).

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **Miro Enterprise Plan**: Miro Enterprise Plan subscription is required.
- **Miro OAuth Application**: Miro OAuth application with auditlogs:read scope and Company Admin role is required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**Step 1: Verify your Miro plan**

1. Ensure your organization has an active [Miro Enterprise Plan](https://miro.com/pricing/).
2. If you need to upgrade, contact [Miro Sales](https://miro.com/contact/sales/) or your account manager.
3. You must be a **Company Admin** to set up this integration.

**Step 2: Choose your setup option**

There are two ways to set up the Miro Audit Logs connector.

**Option 1 (recommended):** Use Enterprise integrations
- Simplest setup with automatic token generation.
- Recommended for most users.
- See Option 1 below.

**Option 2 (alternative):** Create custom OAuth application
- More control over OAuth app configuration.
- For advanced users or custom integration needs.
- See Option 2 below.

**Note:** When using Option 1, the integration is automatically tied to the team with the largest number of users in your organization. When using Option 2, you can choose which team to install the app to. However, **the team selection does not affect which logs are collected**—both options provide organization-wide log access. All integration-relevant events from all teams are included in your logs.

**Option 1: Enterprise integrations (recommended)**

1. Open [Miro Company Settings](https://miro.com/app/settings/).
2. Expand the **Apps and integrations** section.
3. Click **Enterprise integrations**.
4. Enable the **SIEM** toggle.
5. Copy the **Access Token** value that appears.
6. **Important:** Store the token securely—it provides full access to audit logs.
7. The token will work until you disable the toggle.
8. Proceed to Step 3.

**Option 2: Custom OAuth application (alternative)**

1. Go to [Miro App Settings](https://miro.com/app/settings/user-profile/apps).
2. Click **Create new app**.
3. Select **Non-expiring access token** option during app creation.
4. Enable the OAuth scope: **`auditlogs:read`**.
5. Click **Install app and get OAuth token**.
6. Authorize the app to access your organization.
7. Copy the **Access Token** that is displayed.
8. **Important:** Store the token securely—it provides full access to audit logs.
9. The token will work until you uninstall the app.

**Step 3: Learn more**

For detailed information about Miro audit logs:
- [Miro Audit Logs documentation](https://help.miro.com/hc/en-us/articles/360017571434-Audit-logs)
- [Miro API reference](https://developers.miro.com/reference/enterprise-get-audit-logs)
- [OAuth non-expiring tokens](https://developers.miro.com/reference/authorization-flow-for-expiring-access-tokens)
- [Enterprise integrations settings](https://miro.com/app/settings/)

**6. Connect to Miro to start collecting audit logs in Microsoft Sentinel.**

**Step 4: Connect to Miro**

Provide your Miro access token below to complete the connection.
- **Access token**: (password field)
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
