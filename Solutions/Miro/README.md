# Miro solution for Microsoft Sentinel

<img src="../../Logos/Miro.svg" alt="Miro" width="20%"/><br>

## Overview

The [Miro](https://miro.com/) connector ingests audit logs, content activity logs and AI interaction logs from [Miro REST APIs](https://developers.miro.com/reference) into Microsoft Sentinel using the Codeless Connector Framework (CCF). This centralizes Miro workspace activity monitoring in Microsoft Sentinel for security threat detection, incident investigation, and compliance reporting.

## Data connectors

This solution includes three data connectors:

1. **Miro Audit Logs (Enterprise Plan)**: Organization-wide audit events including user authentication, content access, team changes, and administrative actions. [API documentation](https://developers.miro.com/reference/enterprise-get-audit-logs) | [Audit logs overview](https://developers.miro.com/reference/audit-logs).
2. **Miro Content Logs (Enterprise Plan + Enterprise Guard)**: Content activity tracking including item creation, updates, and deletions for compliance and eDiscovery. [API documentation](https://developers.miro.com/reference/enterprise-board-content-item-logs-fetch) | [Content logs overview](https://developers.miro.com/reference/board-content-logs).
3. **Miro AI Interaction Logs (Beta) (Enterprise Plan + Enterprise Guard)**: User interactions with AI features in Miro: the prompt received from the user, the response returned to them, and the model and tool calls made in between. [API documentation](https://developers.miro.com/reference/enterprise-get-ai-interaction-logs) | [AI interaction logs overview](https://help.miro.com/hc/en-us/articles/34049604547858). This connector is in Beta: the AI interaction logs API may change before general availability.

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

**For AI interaction logs connector:**

- Miro Enterprise Plan + Enterprise Guard add-on.
- A Miro admin turns on **Collect AI interaction logs** in Admin console > Security > Audit logs > Settings. Only interactions after that are recorded. If the setting is not visible, contact your Miro account manager.
- OAuth scope: `aiinteractionlogs:read`.
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

**One token for all Miro connectors:** the **SIEM** toggle creates one access token with every log scope your organization is entitled to:

- `auditlogs:read` (Enterprise Plan).
- `contentlogs:export` (Enterprise Guard add-on).
- `aiinteractionlogs:read` (Enterprise Guard add-on with AI interaction logs).

If the SIEM toggle was enabled before it offered these scopes, turn it off and on again to get a token that includes them, then update the token in every connector that uses it. Turning the toggle off invalidates its current token, so every connector that uses it fails to poll until it has the new token. The eDiscovery toggle remains an alternative for the content logs connector.

**Token rotation:** rotate a SIEM token by turning the toggle off and on, or a custom app token (Option 2) by reinstalling the app, then update every connector that uses it. Revoke a token whose scopes you no longer need the same way, by turning the toggle off or uninstalling the app.

#### Get the access token and organization ID

1. Open [Miro company settings](https://miro.com/app/settings/).
2. Expand the **Apps and integrations** section.
3. Click **Enterprise integrations**.
4. Enable the **SIEM** toggle.
5. Copy the **Access Token** value that appears.
6. For the content logs and AI interaction logs connectors, get your **Organization ID** from the browser URL:
   - Look at the browser URL to find your organization ID.
   - The URL format is: `https://miro.com/app/settings/company/{ORGANIZATION_ID}/`.
   - Copy your organization ID from the URL (the numeric value).
7. Store the token and organization ID securely.

#### Alternative for the content logs connector

Instead of the SIEM toggle, you can enable the **eDiscovery** toggle in step 4. Its token is for the content logs connector only.

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
   - `aiinteractionlogs:read` for the AI interaction logs connector (requires Enterprise Guard).
6. Click **Install app and get OAuth token**.
7. Copy the **Access Token** and store it securely.

For detailed OAuth setup instructions, see [Getting started with OAuth](https://developers.miro.com/docs/getting-started-with-oauth).

#### Step 2: Get organization ID (for content logs and AI interaction logs)

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

#### Miro AI interaction logs connector

1. In Microsoft Sentinel, go to **Data connectors**.
2. Find **Miro AI Interaction Logs (Beta) (Enterprise Plan + Enterprise Guard)** and click **Open connector page**.
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
- `ai_assisted`: Whether the action was performed with AI assistance.
- `actor`: User who performed the action, as returned by the API (JSON).
- `ai`: AI-related information about the action, as returned by the API (JSON).
- `state`: Item state information (JSON).

### MiroAIInteractionLogs_CL

AI interaction logs, one row per step of an interaction:

- User input and the output returned to the user.
- Model invocation requests and responses.
- Tool invocation requests and responses.

Key columns:

- `TimeGenerated`: Time when the AI interaction occurred.
- `eventType`: Step of the interaction this entry records (`input`, `output`, `model_invocation_request`, `model_invocation_response`, `tool_invocation_request`, `tool_invocation_response`).
- `turnId`: Identifier that groups the events of one exchange.
- `surface`: Where in Miro the interaction started.
- `actor_email`: User who produced the interaction.
- `object_id`: Miro object involved in the interaction.
- `session_id`: Session that groups the events of one conversation.
- `model`, `tool`: Model and tool information for invocation events (JSON).
- `details`: Additional details about the interaction (JSON); the structure varies by event type.

**Note:** The `details` column may contain unstructured data that could reveal information used in interactions with the LLM. Azure Monitor truncates any field value longer than 64 KB at ingestion ([Logs Ingestion API limits](https://learn.microsoft.com/azure/azure-monitor/fundamentals/service-limits)), so a long `details` value can arrive cut off.

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

### AI-assisted content changes

```kusto
MiroContentLogs_CL
| where TimeGenerated > ago(7d)
| summarize Changes = count() by ai_assisted, actionType
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

### AI interactions by surface and event type

```kusto
MiroAIInteractionLogs_CL
| where TimeGenerated > ago(7d)
| summarize Interactions = count() by surface, eventType
| order by Interactions desc
```

### AI activity by user

```kusto
MiroAIInteractionLogs_CL
| where TimeGenerated > ago(30d) and eventType == "input"
| summarize Prompts = count() by actor_email
| top 10 by Prompts desc
```

## Troubleshooting

### No data appearing

- Verify the access token is valid and has the correct scopes.
- For content logs and AI interaction logs, confirm your organization has the Enterprise Guard add-on.
- For AI interaction logs, confirm that AI interaction logs are enabled for your organization; only interactions after enabling are recorded.
- Confirm the organization ID is correct (for content logs and AI interaction logs).
- Wait 5–10 minutes for initial data ingestion.
- Check the connector status in the **Data connectors** page.

### Authentication errors

**If using Option 1 (enterprise integrations toggle):**

- Go to [Miro company settings](https://miro.com/app/settings/), expand **Apps and integrations**, and click **Enterprise integrations**.
- Verify the toggle (SIEM for all connectors, or eDiscovery for content logs) is still enabled.
- If a connector is denied with a token from the SIEM toggle, turn the toggle off and on again to get a token with the scopes your organization is entitled to.
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

### AI interaction logs not working

- Verify your Miro plan includes the **Enterprise Guard** add-on.
- Confirm **Collect AI interaction logs** is on in Admin console > Security > Audit logs > Settings. Interactions before it was turned on are not recorded.
- Confirm the token has the `aiinteractionlogs:read` scope.
- Double-check that the organization ID is correct.
- Contact your Miro account manager if the setting is not visible.

## Support

### Miro resources

- **Miro Help Center**: [https://help.miro.com](https://help.miro.com).
- **Miro Audit Logs**: [https://help.miro.com/hc/en-us/articles/360017571434-Audit-logs](https://help.miro.com/hc/en-us/articles/360017571434-Audit-logs).
- **Miro Content Logs**: [https://help.miro.com/hc/en-us/articles/17774729839378-Content-Logs-overview](https://help.miro.com/hc/en-us/articles/17774729839378-Content-Logs-overview).
- **Miro AI interaction logs**: [https://help.miro.com/hc/en-us/articles/34049604547858](https://help.miro.com/hc/en-us/articles/34049604547858).
- **Miro Sentinel integration guide**: [https://help.miro.com/hc/en-us/articles/31325908249362](https://help.miro.com/hc/en-us/articles/31325908249362).

### Miro developer documentation

- **Getting started with Enterprise API**: [https://developers.miro.com/docs/getting-started-with-enterprise-api](https://developers.miro.com/docs/getting-started-with-enterprise-api).
- **Getting started with OAuth**: [https://developers.miro.com/docs/getting-started-with-oauth](https://developers.miro.com/docs/getting-started-with-oauth).
- **OAuth token authorization**: [https://developers.miro.com/reference/authorization-flow-for-non-expiring-access-tokens](https://developers.miro.com/reference/authorization-flow-for-non-expiring-access-tokens).
- **Audit Logs API**: [https://developers.miro.com/reference/enterprise-get-audit-logs](https://developers.miro.com/reference/enterprise-get-audit-logs).
- **Content Logs API**: [https://developers.miro.com/reference/enterprise-board-content-item-logs-fetch](https://developers.miro.com/reference/enterprise-board-content-item-logs-fetch).
- **AI Interaction Logs API**: [https://developers.miro.com/reference/enterprise-get-ai-interaction-logs](https://developers.miro.com/reference/enterprise-get-ai-interaction-logs).
- **API reference**: [https://developers.miro.com/reference](https://developers.miro.com/reference).

### Microsoft Sentinel

- **Microsoft Sentinel documentation**: [https://docs.microsoft.com/azure/sentinel/](https://docs.microsoft.com/azure/sentinel/).
