# Miro Solution for Microsoft Sentinel

<img src="./Logo/Miro.svg" alt="Miro" width="20%"/><br>

## Overview

The [Miro](https://miro.com/) solution for Microsoft Sentinel provides the capability to ingest audit logs and content activity logs from [Miro REST APIs](https://developers.miro.com/reference) into Microsoft Sentinel using the Codeless Connector Framework (CCF). This connector enables organizations to monitor and analyze activities within their Miro workspaces. For detailed instructions, refer to the [documentation](https://help.miro.com/hc/en-us/articles/31325908249362).

**Underlying Microsoft technology used:**

This solution is dependent on the following technology and this dependency may be in [Preview](https://azure.microsoft.com/support/legal/preview-supplemental-terms/) state or might result in additional ingestion or operational costs:

• [Codeless Connector Framework (CCF)](https://learn.microsoft.com/azure/sentinel/create-codeless-connector)

## Data Connectors

This solution includes two data connectors:

1. **Miro Audit Logs (Enterprise Plan)**: Organization-wide audit events including user authentication, content access, team changes, and administrative actions. [API Documentation](https://developers.miro.com/reference/enterprise-get-audit-logs) | [Audit Logs Overview](https://developers.miro.com/reference/audit-logs)
2. **Miro Content Logs (Enterprise Plan + Enterprise Guard)**: Content activity tracking including item creation, updates, and deletions for compliance and eDiscovery. [API Documentation](https://developers.miro.com/reference/enterprise-board-content-item-logs-fetch) | [Content Logs Overview](https://developers.miro.com/reference/board-content-logs)

## Prerequisites

### General Requirements
- Active Microsoft Sentinel workspace
- Company Admin role in Miro organization
- Miro OAuth Access Token (non-expiring)

### Connector-Specific Requirements

**For Audit Logs Connector:**
- Miro Enterprise Plan
- OAuth scope: `auditlogs:read`
- Access Token

**For Content Logs Connector:**
- Miro Enterprise Plan + Enterprise Guard add-on
- OAuth scope: `contentlogs:export`
- Access Token
- Miro Organization ID

## Installation

There are two ways to set up the Miro connectors:

- **Method 1 (Recommended):** Use Enterprise Integrations - Simplest setup with automatic token generation
- **Method 2 (Alternative):** Create Custom OAuth Application - More control over OAuth app configuration

**Note:** When using Method 1, the integration is automatically tied to the team with the largest number of users in your organization. When using Method 2, you can choose which team to install the app to. However, **the team selection does not affect which logs are collected** - both methods provide organization-wide log access. All integration-relevant events from all teams are included in your logs.

---

### Method 1: Using Enterprise Integrations (Recommended)

This is the simplest method for most users. It automatically creates an OAuth application and generates an access token for you through Miro's Enterprise Integrations settings.

#### For Audit Logs Connector:

1. Open [Miro Company Settings](https://miro.com/app/settings/)
2. Expand the **Apps and integrations** section
3. Click **Enterprise integrations**
4. Enable the **SIEM** toggle
5. Copy the **Access Token** value that appears
6. Store the token securely

#### For Content Logs Connector:

1. Open [Miro Company Settings](https://miro.com/app/settings/)
2. Expand the **Apps and integrations** section
3. Click **Enterprise integrations**
4. Enable the **eDiscovery** toggle
5. Copy the **Access Token** value that appears
6. Get your **Organization ID** from the browser URL:
   - Look at the browser URL to find your Organization ID
   - The URL format is: `https://miro.com/app/settings/company/{ORGANIZATION_ID}/`
   - Copy your Organization ID from the URL (the numeric value)
7. Store both the token and Organization ID securely

---

### Method 2: Using Custom OAuth Application (Alternative)

This method gives you more control over the OAuth application configuration. Use this if you need to customize scopes, manage multiple integrations, or prefer manual OAuth app management.

#### Step 1: Create Miro OAuth Application

1. Log in to your Miro account
2. Go to [Miro App Settings](https://miro.com/app/settings/user-profile/apps)
3. Click **Create new app**
4. Select **Non-expiring access token** option during app creation ([Learn more about OAuth tokens](https://developers.miro.com/reference/authorization-flow-for-expiring-access-tokens))
5. Enable required OAuth scopes:
   - `auditlogs:read` for Audit Logs connector
   - `contentlogs:export` for Content Logs connector (requires Enterprise Guard)
6. Click **Install app and get OAuth token**
7. Copy the **Access Token** and store it securely

For detailed OAuth setup instructions, see [Getting Started with OAuth](https://developers.miro.com/docs/getting-started-with-oauth).

#### Step 2: Get Organization ID (for Content Logs only)

1. Go to [Miro Company Settings](https://miro.com/app/settings/)
2. Look at the browser URL to find your Organization ID
   - The URL format is: `https://miro.com/app/settings/company/{ORGANIZATION_ID}/`
   - Copy your Organization ID from the URL (the numeric value)

---

### Deploy Solution in Microsoft Sentinel

1. In Microsoft Sentinel, navigate to **Content Hub**
2. Search for **"Miro"** and click the solution
3. Click **Install** and follow the deployment wizard
4. Select your Log Analytics workspace
5. Complete the installation

### Configure Data Connectors

#### Miro Audit Logs Connector

1. In Microsoft Sentinel, go to **Data connectors**
2. Find **Miro Audit Logs (Enterprise Plan)** and click **Open connector page**
3. Click **Connect**
4. Enter your **Access Token**
5. Click **Connect** to activate the connector

#### Miro Content Logs Connector

1. In Microsoft Sentinel, go to **Data connectors**
2. Find **Miro Content Logs (Enterprise Plan + Enterprise Guard)** and click **Open connector page**
3. Click **Connect**
4. Enter your **Organization ID**
5. Enter your **Access Token**
6. Click **Connect** to activate the connector

Data ingestion begins within 5-10 minutes after connector activation.

## Data Tables

### MiroAuditLogs_CL

Organization-level audit events including:
- User authentication and access
- Content operations
- Team and organization changes
- User profile modifications
- Administrative actions

Key columns:
- `TimeGenerated`: Event timestamp
- `event`: Event name identifying the specific action or activity
- `logType`: Type of log entry
- `category`: Event category grouping related events
- `createdBy_email`: User who triggered the event
- `context_ip`: IP address of the event
- `details`: Additional event-specific information (JSON)

### MiroContentLogs_CL

Content-level activity logs including:
- Item-level operations with user attribution and timestamps
- State transitions and modifications
- Activity tracking for compliance and eDiscovery

Key columns:
- `TimeGenerated`: Event timestamp
- `actionType`: Type of action performed on the content
- `actor_email`: User who performed the action
- `itemType`: Type of content item affected
- `contentId`: Unique identifier of the content
- `state`: Item state information (JSON)

## Sample Queries

### View Recent Audit Events

```kusto
MiroAuditLogs_CL
| sort by TimeGenerated desc
| project TimeGenerated, event, category, createdBy_email, context_ip
| take 20
```

### Activity by User and Event Type

```kusto
MiroAuditLogs_CL
| summarize EventCount = count() by createdBy_email, event, category
| order by EventCount desc
```

### Content Changes by User

```kusto
MiroContentLogs_CL
| where TimeGenerated > ago(7d)
| summarize Changes = count() by actor_email, actionType
| order by Changes desc
```

### Event Trends Over Time

```kusto
MiroAuditLogs_CL
| summarize count() by event, bin(TimeGenerated, 1h)
| render timechart
```

### Most Active Users (Content Changes)

```kusto
MiroContentLogs_CL
| where TimeGenerated > ago(30d)
| summarize TotalActions = count() by actor_email
| top 10 by TotalActions desc
```

## Troubleshooting

### No Data Appearing

- Verify the access token is valid and has correct scopes
- For Content Logs, confirm your organization has Enterprise Guard add-on
- Confirm Organization ID is correct (for Content Logs)
- Wait 5-10 minutes for initial data ingestion
- Check connector status in the Data connectors page

### Authentication Errors

**If using Method 1 (Enterprise Integrations toggle):**
- Go to [Company Settings](https://miro.com/app/settings/) > expand **Apps and integrations** > click **Enterprise integrations**
- Verify the toggle (SIEM for Audit Logs, eDiscovery for Content Logs) is still enabled
- If another admin disabled the toggle, the token will be invalidated
- Re-enable the toggle to generate a new token and update the connector configuration
- Verify you have Company Admin role in Miro

**If using Method 2 (Custom OAuth app):**
- Verify the token hasn't been revoked in [Miro App Settings](https://miro.com/app/settings/user-profile/apps)
- Ensure the OAuth application has the required scopes enabled
- Regenerate the token if needed and update in the connector configuration
- Verify you have Company Admin role in Miro

### Content Logs Not Working

- Verify your Miro plan includes **Enterprise Guard** add-on (not available on base Enterprise Plan)
- Confirm the OAuth scope `contentlogs:export` is enabled
- Double-check the Organization ID is correct
- Contact your Miro account manager if you need to upgrade to Enterprise Guard

## Support

### Miro Resources
- **Miro Help Center**: [https://help.miro.com](https://help.miro.com)
- **Miro Audit Logs**: [https://help.miro.com/hc/en-us/articles/360017571434-Audit-logs](https://help.miro.com/hc/en-us/articles/360017571434-Audit-logs)
- **Miro Content Logs**: [https://help.miro.com/hc/en-us/articles/17774729839378-Content-Logs-overview](https://help.miro.com/hc/en-us/articles/17774729839378-Content-Logs-overview)
- **Miro Sentinel Integration Guide**: [https://help.miro.com/hc/en-us/articles/31325908249362](https://help.miro.com/hc/en-us/articles/31325908249362)

### Miro Developer Documentation
- **Getting Started with Enterprise API**: [https://developers.miro.com/docs/getting-started-with-enterprise-api](https://developers.miro.com/docs/getting-started-with-enterprise-api)
- **Getting Started with OAuth**: [https://developers.miro.com/docs/getting-started-with-oauth](https://developers.miro.com/docs/getting-started-with-oauth)
- **OAuth Token Authorization**: [https://developers.miro.com/reference/authorization-flow-for-expiring-access-tokens](https://developers.miro.com/reference/authorization-flow-for-expiring-access-tokens)
- **Audit Logs API**: [https://developers.miro.com/reference/enterprise-get-audit-logs](https://developers.miro.com/reference/enterprise-get-audit-logs)
- **Content Logs API**: [https://developers.miro.com/reference/enterprise-board-content-item-logs-fetch](https://developers.miro.com/reference/enterprise-board-content-item-logs-fetch)
- **API Reference**: [https://developers.miro.com/reference](https://developers.miro.com/reference)

### Microsoft Sentinel
- **Microsoft Sentinel Documentation**: [https://docs.microsoft.com/azure/sentinel/](https://docs.microsoft.com/azure/sentinel/)
