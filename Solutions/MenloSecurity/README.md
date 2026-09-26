# Menlo Security Solution for Microsoft Sentinel

The **Menlo Security** solution ingests security logs from the [Menlo Security](https://www.menlosecurity.com) cloud platform into Microsoft Sentinel. [Menlo Security](https://www.menlosecurity.com) protects organizations from browser-based threats using an isolation-first approach; this solution brings that telemetry into Microsoft Sentinel for threat detection, investigation, and response.

> **Note:** This solution is currently in public preview.

## What it does

The solution installs a single **data connector** that runs as three independent, timer-triggered Azure Functions — one per log type. Each function polls the Menlo Security Log Fetch API every 3 minutes and ships events to a custom Log Analytics table via the Azure Monitor Logs Ingestion API. No inbound network access to your environment is required.

| Log type | Log Analytics table | Description |
|----------|---------------------|-------------|
| Audit | `MenloAudit_CL` | Admin and policy change events |
| Bandwidth | `MenloBandwidth_CL` | Proxy bandwidth usage per user and domain |
| Web | `MenloWeb_CL` | Web request events including URLs, categories, and threat verdicts |

## Architecture

All connector resources are deployed into a dedicated resource group named **`MenloSecurityLogs`**, created in the same Azure region as your Log Analytics workspace. The custom tables are created in your existing workspace's resource group.

| Resource | Purpose |
|----------|---------|
| **Azure Function App** (Flex Consumption, Linux, Python) | Hosts the three timer-triggered ingestion functions |
| **Azure Storage Account** | Function host state, deployment package, and per-log-type last-sync timestamps |
| **Azure Key Vault** | Stores the Menlo API token as a secret (resolved via Key Vault reference) |
| **Application Insights** | Function execution, error, and performance monitoring (workspace-based) |
| **Data Collection Endpoint (DCE)** | HTTPS ingestion endpoint that receives logs from the Function App |
| **Data Collection Rule (DCR)** | Applies KQL type transforms and routes logs to the correct tables |
| **Log Analytics tables** (3) | `MenloAudit_CL`, `MenloBandwidth_CL`, `MenloWeb_CL` |

The Function App authenticates to Azure using a **System-Assigned Managed Identity** — no passwords, connection strings, or client secrets are used for any Azure resource access. Inbound HTTP traffic to the Function App is denied; timer triggers require no inbound access.

## Deployment

1. Install this solution from the Microsoft Sentinel **Content Hub**.
2. During deployment you are prompted for:
   - The name and resource group of your existing Log Analytics workspace.
   - Your Menlo Security API token (a valid token with permission to access the `/api/rep/v2/fetch/client_select` endpoint, obtained from the Menlo Security admin console).
3. The deploying identity requires **Owner** (or **Contributor** + **User Access Administrator**) on the target subscription/resource group, since the deployment creates RBAC role assignments connecting the Function App's managed identity to Key Vault, Storage, and the DCR.

### Enabling log collection

All three log-collection functions are deployed in a **disabled** state. After deployment, enable the log types you want to collect:

1. Open the **Function App** created by this solution.
2. Go to **Configuration → Application settings**.
3. For each log type you want to enable, set the corresponding app setting to `0`:

   | Log type | App setting | Enable value |
   |----------|-------------|--------------|
   | Audit logs | `AzureWebJobs.TimerTriggerAuditLogs.Disabled` | `0` |
   | Bandwidth logs | `AzureWebJobs.TimerTriggerBandwidthLogs.Disabled` | `0` |
   | Web logs | `AzureWebJobs.TimerTriggerWebLogs.Disabled` | `0` |

4. Click **Save**. Each enabled function begins polling on a 3-minute interval.

### Verifying ingestion

After enabling at least one log type, wait 5–10 minutes for the first data to appear, then run in Microsoft Sentinel **Logs**:

```kusto
MenloAudit_CL | take 10
MenloBandwidth_CL | take 10
MenloWeb_CL | take 10
```

If no data appears after 15 minutes, check the Function App's **Monitor** tab for invocation errors.

## Configuration

All tuning parameters are Function App settings and can be adjusted after deployment without redeploying infrastructure. The `*` prefix is replaced with `AUDIT`, `BANDWIDTH`, or `WEB` to configure each log type independently.

| Setting | Default | Description |
|---------|---------|-------------|
| `TIMER_SCHEDULE` | `0 */3 * * * *` | Cron expression controlling how often each trigger fires |
| `*_INITIAL_LOOKBACK_MINUTES` | `2880` (2 days) | How far back to fetch on first run |
| `*_CHUNK_SIZE_MINUTES` | `3` | Size of each time-window chunk |
| `*_LAG_TIME_MINUTES` | `3` | Buffer subtracted from current time to allow for API lag |
| `*_MAX_THREADS` | `3` | Concurrent API requests per invocation |

## Support

This solution is supported by Menlo Security. For assistance, visit [https://www.menlosecurity.com/support](https://www.menlosecurity.com/support).
