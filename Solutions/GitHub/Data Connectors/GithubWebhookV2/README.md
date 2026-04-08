# GitHub Webhook V2 Data Connector

> ⚠️ **IMPORTANT: Migrate to V2**
>
> The original GitHub Webhook connector (`GithubWebhook`) uses the **Azure Monitor HTTP Data Collector API (CLv1 / ODS endpoint)**. Microsoft is replacing this API with the **Logs Ingestion API (CLv2)**. V2 of this connector is the strategic replacement and should be used for all new deployments. Existing V1 deployments should be migrated to V2.
>
> See the [Migrating from V1](#migrating-from-v1) section below for step-by-step instructions.

## Overview

This connector is the designated successor to the original [GitHub Webhook connector](../GithubWebhook/) and ingests [GitHub webhook events](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads) into Microsoft Sentinel using the **Logs Ingestion API (CLv2)** with **Managed Identity** authentication. It replaces the CLv1 HTTP Data Collector API (ODS endpoint) used by the original connector.

| | V1 (original) | V2 (this connector) |
|---|---|---|
| **API** | HTTP Data Collector API (ODS) — being replaced by CLv2 | Logs Ingestion API (CLv2/GIG) |
| **Auth** | SharedKey (`WorkspaceID` + `WorkspaceKey`) | Managed Identity (`DefaultAzureCredential`) |
| **Table** | `githubscanaudit_CL` | `GitHubWebhookEvents_CL` |
| **Column names** | Auto-generated `_s` / `_d` / `_b` suffixes | Explicit schema, identical `_s` / `_d` / `_b` names |
| **Unified view** | `githubscanaudit_CL` only | `githubscanaudit()` parser (unions both tables) |
| **Recommendation** | Migrate to V2 | ✅ Recommended for all deployments |

## Architecture

```
GitHub Org Webhook
        │  POST (HMAC-SHA256 signed)
        ▼
Azure Function App (HTTP trigger)
  ├── GithubWebhookConnectorV2/__init__.py
  │     ├── Verify x-hub-signature-256 (HMAC-SHA256)
  │     ├── customizeJson() — flatten nested JSON to _s strings
  │     └── LogsIngestionClient.upload() → DCE → DCR
  │
  ├── System-assigned Managed Identity
  │     └── Monitoring Metrics Publisher role on DCR
  │
  └── App Settings
        ├── DCE_ENDPOINT
        ├── DCR_RULE_ID
        ├── DCR_STREAM_NAME  (Custom-GitHubWebhookEvents_CL)
        └── GithubWebhookSecret  (optional, for HMAC validation)

DCR → Log Analytics Workspace → GitHubWebhookEvents_CL table
```

## Prerequisites

- Microsoft Sentinel workspace
- Permissions to create Azure Function Apps, role assignments, and DCE/DCR resources
- A GitHub Organization with Webhook configuration access

## Deployment

### Option 1 — ARM Template (Recommended)

[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGitHub%2FData%2520Connectors%2FGithubWebhookV2%2Fazuredeploy_GithubWebhookV2_API_FunctionApp.json)

**Required parameters:**

| Parameter | Description |
|---|---|
| `FunctionName` | Name for the new Function App (default: `fngithubwebhookv2`) |
| `WorkspaceName` | The **name** of your Log Analytics workspace (e.g. `my-sentinel-workspace`). Deploy to the **same resource group** as the workspace. |
| `GithubWebhookSecret` | *(Optional)* Secret string used to validate the `x-hub-signature-256` header sent by GitHub |

The template automatically provisions:
- Storage Account, App Service Plan, Function App (with SystemAssigned identity)
- Application Insights
- Custom Log table `GitHubWebhookEvents_CL`
- Data Collection Endpoint (DCE)
- Data Collection Rule (DCR) with `transformKql: "source"` passthrough
- Role assignment granting the Function App's Managed Identity the **Monitoring Metrics Publisher** role on the DCR

### Option 2 — Manual Deployment

1. Deploy the Function App manually following the [Azure Functions manual deployment instructions](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/AzureFunctionsManualDeployment.md).
2. Create the `GitHubWebhookEvents_CL` table with the schema defined in the ARM template.
3. Create a DCE and DCR pointing to `GitHubWebhookEvents_CL`.
4. Enable **System Assigned Managed Identity** on the Function App.
5. Grant the Managed Identity the **Monitoring Metrics Publisher** role on the DCR.
6. Set the following Application Settings:

| Setting | Value |
|---|---|
| `DCE_ENDPOINT` | Logs ingestion endpoint URL from your DCE |
| `DCR_RULE_ID` | `immutableId` of your DCR |
| `DCR_STREAM_NAME` | `Custom-GitHubWebhookEvents_CL` |
| `GithubWebhookSecret` | *(Optional)* Your GitHub webhook secret |

## GitHub Webhook Configuration

1. In the Azure Portal, navigate to your Function App → **Functions** → `GithubWebhookConnectorV2` → **Get Function URL** and copy the URL.
2. In GitHub, go to your Organization → **Settings** → **Webhooks** → **Add webhook**.
3. Paste the Function URL into **Payload URL**.
4. Set **Content type** to `application/json`.
5. If you set a `GithubWebhookSecret`, enter the same value in the **Secret** field.
6. Choose which events to subscribe to and click **Add webhook**.

## Querying Data

| Query | Description |
|---|---|
| `GitHubWebhookEvents_CL \| sort by TimeGenerated desc` | All V2 events |
| `githubscanaudit() \| sort by TimeGenerated desc` | Unified view (V1 + V2, all historical data) |
| `GitHubCodeScanningData()` | Code scanning alerts (uses `githubscanaudit()` — works with both tables) |
| `GitHubDependabotData()` | Dependabot vulnerability alerts |
| `GitHubSecretScanningData()` | Secret scanning alerts |

## Migrating from V1

> ⚠️ **Microsoft is replacing the CLv1 HTTP Data Collector API (used by the original GitHub Webhook connector) with the Logs Ingestion API (CLv2). V2 is the recommended replacement. Migrate existing V1 deployments to V2 to remain on a supported ingestion path.**

Because both tables share identical column names (`_s` / `_d` / `_b` suffixes), all existing workbooks, analytic rules, hunting queries, and parsers (`GitHubCodeScanningData`, `GitHubDependabotData`, `GitHubSecretScanningData`) continue to work without modification via the `githubscanaudit()` union parser.

**Migration Steps:**

1. **Deploy V2.** Complete all deployment steps above.

2. **Update the GitHub webhook URL.** In your GitHub Organization (**Settings → Webhooks**), update the payload URL to point to the new V2 Function App URL. This immediately redirects new events to V2.

3. **Verify V2 is receiving events.** Trigger some GitHub events and confirm data appears in `GitHubWebhookEvents_CL` within 5–10 minutes.

4. **Validate the unified parser.** Run the following in Log Analytics to confirm events appear:
   ```kql
   githubscanaudit()
   | sort by TimeGenerated desc
   | take 50
   ```

5. **Stop the V1 Function App.** Once V2 is confirmed working:
   - In the Azure Portal, navigate to your original V1 Function App.
   - Under **Overview**, click **Stop**.
   - This prevents any residual processing while freeing up Function App compute costs.

6. **Retain V1 historical data.** The `githubscanaudit_CL` table data is subject to your workspace retention policy. No action is required — historical V1 data remains queryable via `githubscanaudit()` until it ages out.

> **Note:** Do not delete V1 Function App resources until you are satisfied V2 is fully operational and you do not need to roll back.

## File Structure

```
GithubWebhookV2/
├── GithubWebhookConnectorV2/
│   ├── __init__.py          # Azure Function — CLv2 ingestion logic
│   └── function.json        # HTTP trigger binding
├── azuredeploy_GithubWebhookV2_API_FunctionApp.json  # ARM template
├── GithubWebhookV2_API_FunctionApp.json              # Connector definition
├── host.json                # Function host settings (retry, timeout)
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Related Resources

- [Original V1 connector](../GithubWebhook/)
- [`githubscanaudit` union parser](../../Parsers/GitHubScanAudit.yaml)
- [Azure Monitor HTTP Data Collector API deprecation](https://aka.ms/Sentinel-Logs_migration)
- [Logs Ingestion API overview](https://docs.microsoft.com/azure/azure-monitor/logs/logs-ingestion-api-overview)
- [Azure Monitor Ingestion client library for Python](https://docs.microsoft.com/python/api/overview/azure/monitor-ingestion-readme)
