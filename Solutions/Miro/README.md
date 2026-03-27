# Miro solution for Microsoft Sentinel

<img src="./Logo/Miro.svg" alt="Miro" width="20%"/><br>

## Overview

The [Miro](https://miro.com/) connector ingests audit logs and content activity logs from [Miro REST APIs](https://developers.miro.com/reference) into Microsoft Sentinel using the Codeless Connector Framework (CCF). This centralizes Miro workspace activity monitoring in Microsoft Sentinel for security threat detection, incident investigation, and compliance reporting.

## Data connectors

This solution includes two data connectors:

1. **Miro Audit Logs (Enterprise Plan)**: Organization-wide audit events including user authentication, content access, team changes, and administrative actions. [API documentation](https://developers.miro.com/reference/enterprise-get-audit-logs) | [Audit logs overview](https://developers.miro.com/reference/audit-logs).
2. **Miro Content Logs (Enterprise Plan + Enterprise Guard)**: Content activity tracking including item creation, updates, and deletions for compliance and eDiscovery. [API documentation](https://developers.miro.com/reference/enterprise-board-content-item-logs-fetch) | [Content logs overview](https://developers.miro.com/reference/board-content-logs).

## Prerequisites

### General requirements

- Active Microsoft Sentinel workspace.
- Company Admin role in your Miro organization.
- Miro OAuth access token (non-expiring).

### Connector-specific requirements

**For audit logs connector:**

- Miro Enterprise Plan.
- OAuth scope: `auditlogs:read`.
- Access token.

**For content logs connector:**

- Miro Enterprise Plan + Enterprise Guard add-on.
- OAuth scope: `contentlogs:export`.
- Access token.
- Miro organization ID.

## Installation

There are two ways to set up the Miro connectors.

- **Option 1 (recommended):** Use enterprise integrations. Simplest setup with automatic token generation.
- **Option 2 (alternative):** Create custom OAuth application. More control over OAuth app configuration.

**Note:** When using Option 1, the integration is automatically tied to the team with the largest number of users in your organization. When using Option 2, you can choose which team to install the app to. However, **the team selection does not affect which logs are collected**—both options provide organization-wide log access. All integration-relevant events from all teams are included in your logs.

---

### Option 1: Use enterprise integrations (recommended)

This is the simplest option for most users. It automatically creates an OAuth application and generates an access token for you through Miro's enterprise integrations settings.

#### For audit logs connector

1. Open [Miro company settings](https://miro.com/app/settings/).
2. Expand the **Apps and integrations** section.
3. Click **Enterprise integrations**.
4. Enable the **SIEM** toggle.
5. Copy the **Access Token** value that appears.
6. Store the token securely.

#### For content logs connector

1. Open [Miro company settings](https://miro.com/app/settings/).
2. Expand the **Apps and integrations** section.
3. Click **Enterprise integrations**.
4. Enable the **eDiscovery** toggle.
5. Copy the **Access Token** value that appears.
6. Get your **Organization ID** from the browser URL:
   - Look at the browser URL to find your organization ID.
   - The URL format is: `https://miro.com/app/settings/company/{ORGANIZATION_ID}/`.
   - Copy your organization ID from the URL (the numeric value).
7. Store both the token and organization ID securely.

---

### Option 2: Use custom OAuth application (alternative)

This option gives you more control over the OAuth application configuration. Use this if you need to customize scopes, manage multiple integrations, or prefer manual OAuth app management.

#### Step 1: Create Miro OAuth application

1. Log in to your Miro account.
2. Go to [Miro app settings](https://miro.com/app/settings/user-profile/apps).
3. Click **Create new app**.
4. Select the **Non-expiring access token** option during app creation ([learn more about OAuth tokens](https://developers.miro.com/reference/authorization-flow-for-non-expiring-access-tokens)).
5. Enable the required OAuth scopes:
   - `auditlogs:read` for the audit logs connector.
   - `contentlogs:export` for the content logs connector (requires Enterprise Guard).
6. Click **Install app and get OAuth token**.
7. Copy the **Access Token** and store it securely.

For detailed OAuth setup instructions, see [Getting started with OAuth](https://developers.miro.com/docs/getting-started-with-oauth).

#### Step 2: Get organization ID (for content logs only)

1. Go to [Miro company settings](https://miro.com/app/settings/).
2. Look at the browser URL to find your organization ID.
   - The URL format is: `https://miro.com/app/settings/company/{ORGANIZATION_ID}/`.
   - Copy your organization ID from the URL (the numeric value).

---

### Deploy solution in Microsoft Sentinel

1. In Microsoft Sentinel, navigate to **Content Hub**.
2. Search for **"Miro"** and click the solution.
3. Click **Install** and follow the deployment wizard.
4. Select your Log Analytics workspace.
5. Complete the installation.

### Configure data connectors

#### Miro audit logs connector

1. In Microsoft Sentinel, go to **Data connectors**.
2. Find **Miro Audit Logs (Enterprise Plan)** and click **Open connector page**.
3. Click **Connect**.
4. Enter your **Access Token**.
5. Click **Connect** to activate the connector.

#### Miro content logs connector

1. In Microsoft Sentinel, go to **Data connectors**.
2. Find **Miro Content Logs (Enterprise Plan + Enterprise Guard)** and click **Open connector page**.
3. Click **Connect**.
4. Enter your **Organization ID**.
5. Enter your **Access Token**.
6. Click **Connect** to activate the connector.

Data ingestion begins within 5–10 minutes after connector activation.

## Data tables

### MiroAuditLogs_CL

Organization-level audit events including:

- User authentication and access.
- Content operations.
- Team and organization changes.
- User profile modifications.
- Administrative actions.

Key columns:

- `TimeGenerated`: Event timestamp.
- `event`: Event name identifying the specific action or activity.
- `logType`: Type of log entry.
- `category`: Event category grouping related events.
- `createdBy_email`: User who triggered the event.
- `context_ip`: IP address of the event.
- `details`: Additional event-specific information (JSON).

### MiroContentLogs_CL

Content-level activity logs including:

- Item-level operations with user attribution and timestamps.
- State transitions and modifications.
- Activity tracking for compliance and eDiscovery.

Key columns:

- `TimeGenerated`: Event timestamp.
- `actionType`: Type of action performed on the content.
- `actor_email`: User who performed the action.
- `itemType`: Type of content item affected.
- `contentId`: Unique identifier of the content.
- `state`: Item state information (JSON).

## Sample queries

### View recent audit events

```kusto
MiroAuditLogs_CL
| sort by TimeGenerated desc
| project TimeGenerated, event, category, createdBy_email, context_ip
| take 20
```

### Activity by user and event type

```kusto
MiroAuditLogs_CL
| summarize EventCount = count() by createdBy_email, event, category
| order by EventCount desc
```

### Content changes by user

```kusto
MiroContentLogs_CL
| where TimeGenerated > ago(7d)
| summarize Changes = count() by actor_email, actionType
| order by Changes desc
```

### Event trends over time

```kusto
MiroAuditLogs_CL
| summarize count() by event, bin(TimeGenerated, 1h)
| render timechart
```

### Most active users (content changes)

```kusto
MiroContentLogs_CL
| where TimeGenerated > ago(30d)
| summarize TotalActions = count() by actor_email
| top 10 by TotalActions desc
```

## Troubleshooting

### No data appearing

- Verify the access token is valid and has the correct scopes.
- For content logs, confirm your organization has the Enterprise Guard add-on.
- Confirm the organization ID is correct (for content logs).
- Wait 5–10 minutes for initial data ingestion.
- Check the connector status in the **Data connectors** page.

### Authentication errors

**If using Option 1 (enterprise integrations toggle):**

- Go to [Miro company settings](https://miro.com/app/settings/), expand **Apps and integrations**, and click **Enterprise integrations**.
- Verify the toggle (SIEM for audit logs, eDiscovery for content logs) is still enabled.
- If another admin disabled the toggle, the token will be invalidated.
- Re-enable the toggle to generate a new token and update the connector configuration.
- Verify you have the Company Admin role in Miro.

**If using Option 2 (custom OAuth app):**

- Verify the token has not been revoked in [Miro app settings](https://miro.com/app/settings/user-profile/apps).
- Ensure the OAuth application has the required scopes enabled.
- Regenerate the token if needed and update it in the connector configuration.
- Verify you have the Company Admin role in Miro.

### Content logs not working

- Verify your Miro plan includes the **Enterprise Guard** add-on (not available on the base Enterprise Plan).
- Confirm the OAuth scope `contentlogs:export` is enabled.
- Double-check that the organization ID is correct.
- Contact your Miro account manager if you need to upgrade to Enterprise Guard.

## Support

### Miro resources

- **Miro Help Center**: [https://help.miro.com](https://help.miro.com).
- **Miro Audit Logs**: [https://help.miro.com/hc/en-us/articles/360017571434-Audit-logs](https://help.miro.com/hc/en-us/articles/360017571434-Audit-logs).
- **Miro Content Logs**: [https://help.miro.com/hc/en-us/articles/17774729839378-Content-Logs-overview](https://help.miro.com/hc/en-us/articles/17774729839378-Content-Logs-overview).
- **Miro Sentinel integration guide**: [https://help.miro.com/hc/en-us/articles/31325908249362](https://help.miro.com/hc/en-us/articles/31325908249362).

### Miro developer documentation

- **Getting started with Enterprise API**: [https://developers.miro.com/docs/getting-started-with-enterprise-api](https://developers.miro.com/docs/getting-started-with-enterprise-api).
- **Getting started with OAuth**: [https://developers.miro.com/docs/getting-started-with-oauth](https://developers.miro.com/docs/getting-started-with-oauth).
- **OAuth token authorization**: [https://developers.miro.com/reference/authorization-flow-for-non-expiring-access-tokens](https://developers.miro.com/reference/authorization-flow-for-non-expiring-access-tokens).
- **Audit Logs API**: [https://developers.miro.com/reference/enterprise-get-audit-logs](https://developers.miro.com/reference/enterprise-get-audit-logs).
- **Content Logs API**: [https://developers.miro.com/reference/enterprise-board-content-item-logs-fetch](https://developers.miro.com/reference/enterprise-board-content-item-logs-fetch).
- **API reference**: [https://developers.miro.com/reference](https://developers.miro.com/reference).

### Microsoft Sentinel

- **Microsoft Sentinel documentation**: [https://docs.microsoft.com/azure/sentinel/](https://docs.microsoft.com/azure/sentinel/).
