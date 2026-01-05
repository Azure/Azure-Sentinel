# Miro Content Logs (Enterprise Plan + Enterprise Guard)

| | |
|----------|-------|
| **Connector ID** | `MiroContentLogsDataConnector` |
| **Publisher** | Miro |
| **Tables Ingested** | [`MiroContentLogs_CL`](../tables-index.md#mirocontentlogs_cl) |
| **Used in Solutions** | [Miro](../solutions/miro.md) |
| **Connector Definition Files** | [MiroContentLogs_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Miro/Data%20Connectors/MiroContentLogs_CCF/MiroContentLogs_DataConnectorDefinition.json) |

The [Miro Content Logs](https://help.miro.com/hc/en-us/articles/17774729839378-Content-Logs-overview) data connector enables you to ingest content activity logs from Miro into Microsoft Sentinel. Part of Miro's Enterprise Guard eDiscovery capabilities, this connector provides content-level visibility for compliance, legal hold, and advanced threat detection.



**Key features:**

- Track all content item changes.

- Monitor content modifications by user and timestamp.

- Support compliance and eDiscovery requirements.

- Detect data exfiltration and insider threats.

- Meet regulatory and legal hold obligations.



**Requirements:**

- **Miro Plan**: [Enterprise Plan](https://miro.com/pricing/) + **Enterprise Guard** add-on.

- **OAuth scope**: `contentlogs:export`.

- **Role**: Company Admin in your Miro organization.

- **Organization ID**: Your Miro organization identifier.



💡 **Not on Enterprise Plan yet?** Upgrade to [Miro Enterprise](https://miro.com/enterprise/) to unlock advanced security and compliance features for your team's collaboration activities in Microsoft Sentinel.



💡 **Need Content Logs?** Content activity logging is part of [Miro Enterprise Guard](https://miro.com/enterprise-guard/), which provides advanced security, compliance, and eDiscovery features. Contact your Miro account manager to add Enterprise Guard to your Enterprise Plan and unlock content-level monitoring in Microsoft Sentinel.



**Note:** If you only have the base Enterprise Plan (without Enterprise Guard), please use the **Miro Audit Logs** connector instead for organization-level event monitoring.



For detailed instructions, refer to the [documentation](https://help.miro.com/hc/en-us/articles/31325908249362).

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **Miro Enterprise Plan with Enterprise Guard**: Miro Enterprise Plan with Enterprise Guard add-on is required. Content logs are part of Miro's eDiscovery features and are not available on base Enterprise Plan or lower tiers.
- **Miro OAuth Application**: Miro OAuth application with contentlogs:export scope and Company Admin role is required.
- **Miro Organization ID**: Your Miro organization ID is required to access content logs.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**Step 1: Verify your Miro plan and Enterprise Guard**

1. Ensure your organization has [Miro Enterprise Plan](https://miro.com/pricing/) with **Enterprise Guard** add-on.
2. Content logs are part of Miro's eDiscovery (Enterprise Guard) features.
3. If you don't have Enterprise Guard yet, contact your [Miro account manager](https://miro.com/contact/sales/) to upgrade.
4. Without Enterprise Guard, use the **Miro Audit Logs** connector for organization-level monitoring.
5. You must be a **Company Admin** to set up this integration.

**Step 2: Choose your setup option**

There are two ways to set up the Miro Content Logs connector.

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
4. Enable the **eDiscovery** toggle.
5. Copy the **Access Token** value that appears.
6. Get your **Organization ID** from the browser URL:
   - Look at the browser URL to find your Organization ID.
   - The URL format is: `https://miro.com/app/settings/company/{ORGANIZATION_ID}/`.
   - Copy your Organization ID from the URL (the numeric value).
7. **Important:** Store both the token and Organization ID securely—they provide full access to content logs.
8. The token will work until you disable the toggle.
9. Proceed to Step 3.

**Option 2: Custom OAuth application (alternative)**

1. Go to [Miro App Settings](https://miro.com/app/settings/user-profile/apps).
2. Click **Create new app**.
3. Select **Non-expiring access token** option during app creation.
4. Enable the OAuth scope: **`contentlogs:export`**.
5. Click **Install app and get OAuth token**.
6. Authorize the app to access your organization.
7. Copy the **Access Token** that is displayed.
8. Get your **Organization ID**:
   - Go to [Miro Company Settings](https://miro.com/app/settings/).
   - Look at the browser URL to find your Organization ID.
   - The URL format is: `https://miro.com/app/settings/company/{ORGANIZATION_ID}/`.
   - Copy your Organization ID from the URL (the numeric value).
9. **Important:** Store both the token and Organization ID securely—they provide full access to content logs.
10. The token will work until you uninstall the app.

**Step 3: Learn more**

For detailed information about Miro content logs and eDiscovery:
- [Miro Content Logs overview](https://help.miro.com/hc/en-us/articles/17774729839378-Content-Logs-overview)
- [Miro Enterprise Guard](https://miro.com/enterprise-guard/)
- [Miro API reference](https://developers.miro.com/reference/enterprise-board-content-item-logs-fetch)
- [OAuth non-expiring tokens](https://developers.miro.com/reference/authorization-flow-for-expiring-access-tokens)
- [Enterprise integrations settings](https://miro.com/app/settings/)

**6. Connect to Miro to start collecting content logs in Microsoft Sentinel.**

**Step 4: Connect to Miro**

Provide the required values below to complete the connection.
- **Organization ID**: Enter your Miro Organization ID
- **Access token**: (password field)
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
