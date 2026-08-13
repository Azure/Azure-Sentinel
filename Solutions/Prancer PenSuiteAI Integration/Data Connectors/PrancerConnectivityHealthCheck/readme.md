# Prancer Connectivity Health Check

**Trust class: fully autonomous (read-only against the customer's own
`PrancerFindings_CL` table; writes only to a purpose-built health-status
table and an outbound webhook — no write access to `PrancerFindings_CL`
itself, no customer infrastructure changes).**

A Timer-triggered Azure Function that independently verifies Prancer's
push-based ingestion pipeline is still working. Prancer's backend
(`pac-result-receiver`) pushes findings directly into a customer's
`PrancerFindings_CL` table via the Azure Monitor Logs Ingestion API and a
Data Collection Rule (DCR) auto-provisioned by Prancer's in-product
connectivity wizard — there is no polling connector, so nothing on the
customer side ever independently confirms that ingestion is still healthy.
If a DCR role assignment is revoked, a workspace is reconfigured, or
Prancer's backend has an outage, a customer currently has no signal other
than noticing `PrancerFindings_CL` has gone quiet. This Function closes that
gap.

## Flow

1. Runs on a timer schedule (default: every 6 hours — `0 0 */6 * * *`,
   configurable by editing `function.json`'s `schedule`).
2. Acquires an Azure AD token via the OAuth2 client-credentials grant
   (`https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token`,
   scope `https://api.loganalytics.io/.default`) and queries the customer's
   own `PrancerFindings_CL` table via the Log Analytics Query API:
   `PrancerFindings_CL | summarize LastReceived = max(TimeGenerated)`.
3. Computes staleness: `now - LastReceived`, in hours, compared against
   `STALENESS_THRESHOLD_HOURS` (default 48h — scan cadence varies by
   customer, so this deliberately does not assume near-real-time freshness).
4. Reports the result through two independent channels:
   - **Webhook** (`HEALTH_CHECK_WEBHOOK_URL`) — a JSON POST with workspace
     name, last-received timestamp, staleness in hours, and a healthy/
     unhealthy boolean. Works with Teams incoming webhooks, Slack incoming
     webhooks, or any generic HTTPS endpoint. This channel does **not**
     depend on `PrancerFindings_CL`, its DCR, or any Sentinel table being
     healthy — it only needs outbound HTTPS from the Function App, which is
     independent of every failure mode this check exists to detect. This is
     why it's the primary signal.
   - **`PrancerConnectivityHealth_CL`** — if the Log Analytics query itself
     succeeded (meaning workspace/API access is fine, whether the data
     turned out stale or fresh), the Function also writes one status row
     into this separate table via the Logs Ingestion API, using a
     **separate, minimal DCR/DCE** from the one that serves
     `PrancerFindings_CL` (see "Why not just write into
     `PrancerFindings_CL`" below). This lets customers build their own
     native Sentinel analytic rule on "no healthy check-in in N hours" if
     they want in-product alerting in addition to the webhook.
5. Authenticates both the query and the ingestion call using the same
   service-principal client-credentials pattern already established
   elsewhere in this solution: `CLIENT_ID` + `CLIENT_SECRET` + `TENANT_ID`.
   The Logs Ingestion API call uses scope `https://monitor.azure.com/.default`
   (per Microsoft's [Logs Ingestion API documentation](https://learn.microsoft.com/azure/azure-monitor/logs/logs-ingestion-api-overview)).

## Why not just write into `PrancerFindings_CL`?

Because the one thing this check exists to catch is "the pipeline that
writes to `PrancerFindings_CL` is broken." If the health-check status were
written through that same DCR, the exact failure modes it's meant to detect
— a revoked DCR role assignment, a broken ingestion identity, a
misconfigured workspace — would also silently swallow the health signal
itself. A customer would see no data in `PrancerFindings_CL` *and* no
health-check row explaining why, which is strictly worse than today's
silence. Using a separate DCR/DCE, and (independently) a webhook that
doesn't touch Log Analytics at all, means at least one of the two channels
keeps working in almost any failure scenario, including the specific one
this Function is built to catch.

## Quick Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/PLACEHOLDER-RAW-GITHUB-URL-TO-azuredeploy.json)

*(Deploy-to-Azure button target is a placeholder — point it at this
template's raw GitHub URL once merged into `Azure/Azure-Sentinel`.)*

## Prerequisites

1. The Prancer Sentinel solution's Data Connector, DCR, and
   `PrancerFindings_CL` table must already be deployed and receiving data.
2. An App Registration (service principal) with `CLIENT_ID` / `CLIENT_SECRET`
   / `TENANT_ID` that has **Log Analytics Reader** (or equivalent read
   access) on the workspace hosting `PrancerFindings_CL`, so it can call the
   Log Analytics Query API. This can be the same App Registration Prancer's
   backend uses for ingestion, or a separate read-only one — a separate one
   is recommended so this Function's credential does not also carry
   ingestion-write privileges it doesn't need for the query step.
3. **A separate, minimal DCE and DCR provisioned for
   `PrancerConnectivityHealth_CL`**, distinct from the DCR/DCE that serves
   `PrancerFindings_CL`. See
   `../../Data/dcr-connectivity-health-transform.md` for the exact table
   schema and the minimal DCR shape needed. Grant the same (or a separate)
   App Registration the **Monitoring Metrics Publisher** role scoped to this
   new DCR. This step is optional in the sense that the Function still runs
   and still sends the webhook without it (`HEALTH_DCE_ENDPOINT` /
   `HEALTH_DCR_IMMUTABLE_ID` left blank), but it is required for the
   in-Sentinel alerting path described above.
4. A Teams incoming webhook, Slack incoming webhook, or generic HTTPS
   endpoint URL, if you want the (strongly recommended) webhook
   notification channel. Optional but should not be skipped — it's the one
   channel that survives even if the health DCR/DCE above is itself
   misconfigured.
5. A Log Analytics workspace resource ID to back the Function's
   Application Insights instance (workspace-based Application Insights is
   required by current Azure defaults — this can be the same workspace that
   hosts `PrancerFindings_CL`, or any other operational workspace).

## Post-Deployment steps

1. Confirm the Function App's application settings were populated
   correctly: `WORKSPACE_ID`, `TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`,
   `STALENESS_THRESHOLD_HOURS`, `HEALTH_CHECK_WEBHOOK_URL`,
   `HEALTH_DCE_ENDPOINT`, `HEALTH_DCR_IMMUTABLE_ID`, `HEALTH_STREAM_NAME`,
   and optionally `WORKSPACE_NAME` / `CUSTOMER_ID`.
2. Deploy the function code itself — the ARM template provisions the
   infrastructure (Storage Account, Application Insights, Consumption plan,
   Function App) but does not push code. Deploy this folder's contents with
   `func azure functionapp publish <FunctionAppName>` (Azure Functions Core
   Tools) or a zip-deploy of this directory.
3. Trigger a manual run (Azure Portal → Function App → Functions → the timer
   function → **Test/Run**, or wait for the next 6-hour tick) and confirm:
   - The webhook receives a payload with a sane `stalenessHours` value.
   - If the health DCR/DCE were configured, a new row appears in
     `PrancerConnectivityHealth_CL` within a few minutes.
4. If the webhook payload reports `isHealthy: false` unexpectedly, check
   first whether `PrancerFindings_CL` is genuinely stale (e.g. no recent
   scans) before assuming a pipeline break — the default 48h threshold is
   deliberately conservative but customers with infrequent scan schedules
   should raise `STALENESS_THRESHOLD_HOURS` accordingly.
5. Adjust the timer `schedule` in `function.json` if 6 hours doesn't match
   your desired check frequency (this requires redeploying the function
   code, not just the app settings).

## Judgment calls / fallbacks used

- **Function App shape**: `Microsoft.Web/sites` (`kind: functionapp,linux`)
  on a `Microsoft.Web/serverfarms` Consumption plan (`Y1`/`Dynamic`), with a
  companion `Microsoft.Storage/storageAccounts` and workspace-based
  `Microsoft.Insights/components`. This mirrors the resource shape and
  `apiVersion`s used by another connector Function already merged into
  `Azure/Azure-Sentinel` (XBOW's `AzureFunctionXbow`), rather than being
  freshly guessed, so confidence is high on the nested properties
  (`linuxFxVersion: "python|3.11"`, `FUNCTIONS_EXTENSION_VERSION: "~4"`,
  `FUNCTIONS_WORKER_RUNTIME: "python"`, the `AzureWebJobsStorage`
  connection-string construction via `listKeys`).
- **Authentication**: uses `CLIENT_ID`/`CLIENT_SECRET`/`TENANT_ID` app
  settings and a manual OAuth2 client-credentials POST via `requests`
  rather than the `azure-identity`/`azure-monitor-ingestion` SDKs, to keep
  the dependency footprint to `azure-functions` + `requests` only. If a
  future maintainer prefers the SDK approach (as XBOW's connector does),
  swapping `_get_aad_token`/`_push_health_row` for
  `ClientSecretCredential`/`LogsIngestionClient` is a contained change.
- **Logs Ingestion API scope**: confirmed against Microsoft's own
  documentation (`https://monitor.azure.com/.default`) rather than assumed
  by analogy to the Query API's scope — these are genuinely different
  resource audiences and it would have been easy to get this wrong.
- **No managed identity**: this Function does not use a system-assigned
  managed identity for the Log Analytics Query API or Logs Ingestion API
  calls, since the task requires the same service-principal
  client-credentials pattern already established elsewhere in this
  solution. A managed-identity variant (with role assignments on both the
  query workspace and the health DCR) is a reasonable future enhancement
  but was not built here to stay consistent with the rest of the solution's
  auth pattern.
- **`WORKSPACE_NAME` / `CUSTOMER_ID` app settings**: not explicitly listed
  in the original task's app-settings enumeration, added as small optional
  conveniences — `WORKSPACE_NAME` for a human-readable webhook message, and
  `CUSTOMER_ID` to populate the `CustomerId` column on
  `PrancerConnectivityHealth_CL` (mirroring the `CustomerId` column already
  present on `PrancerFindings_CL`). Both default safely (empty / falls back
  to `WORKSPACE_ID`) if left unset.
- **`host.json`**: not explicitly requested in the original file list, but
  added because a Python Azure Function is not actually deployable without
  one; content mirrors the same merged XBOW connector's `host.json`
  (`functionTimeout: 00:10:00`, standard Application Insights sampling,
  the standard `Microsoft.Azure.Functions.ExtensionBundle` v4 range).
