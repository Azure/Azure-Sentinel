# PRODAFTUstaIoC-BackfillMaliciousUrls

On-demand historical backfill for the PRODAFT USTA **Malicious URLs** IoC feed, part of the
**PRODAFT USTA - IoC Threat Intelligence** solution.

The hourly [`PRODAFTUstaIoC-ImportMaliciousUrls`](../PRODAFTUstaIoC-ImportMaliciousUrls/readme.md) playbook only moves **forward** from its watermark, so it
cannot reach history that predates its first run. This playbook loads that history: it pages the
`malicious-urls` feed from `BackfillDays` ago (default **90**) up to the present, maps each record to a
STIX 2.1 indicator with the **same mapping** as the import playbook, and uploads it under the same
`SourceSystem` — `PRODAFT USTA - Malicious URLs` — so backfilled and incremental data are indistinguishable.

## Safe to run alongside the import playbook

* STIX ids are **deterministic**, so re-uploading a record **updates** it rather than duplicating it.
* The import playbook's watermark is `max(Created)`. Loading *older* records never moves it backwards,
  and if the backfill catches up to the present it lands on the value the import playbook would have
  reached anyway. Neither playbook can make the other skip records.
* The trigger allows **one run at a time** (`concurrency: 1`), so pressing Run Trigger again while a
  backfill is still going queues the run instead of doubling the API load.

## Resolved IP addresses

When a record carries `ip_addresses`, every address is appended to the **same** indicator's
pattern as its own observation expression — `ipv4-addr:value` or `ipv6-addr:value`, chosen per
address — so the indicator covers the URL/hash and its resolved IPs under one validity window.
Only the **first 10** addresses of a record are included; any beyond that are dropped.

Microsoft Sentinel expands a multi-observation pattern into one `ObservableKey`/`ObservableValue` row per
observable, so those IPs are independently matchable. Note that CDN-fronted hosts resolve to
shared edge addresses, which can produce false positives if you match on IP alone.

## Parameters

| Parameter | Required | Default | Notes |
|---|---|---|---|
| `PlaybookName` | no | `PRODAFTUstaIoC-BackfillMaliciousUrls` | Logic App name. |
| `UstaBaseUrl` | no | `https://usta.prodaft.com` | USTA API base URL. |
| `UstaApiKey` | **yes** | — | USTA long-lived API key (secured). |
| `WorkspaceName` | **yes** | — | Name of the Microsoft Sentinel (Log Analytics) workspace that indicators are uploaded to. |
| `WorkspaceResourceGroup` | no | resource group of the deployment | Resource group of the workspace, if it differs from where the playbook is deployed. |
| `BackfillDays` | no | `90` | Days of history to load, counted back from now. Ignored when `startTime` is supplied in the trigger body. |

## Deploy — from the portal

1. **Microsoft Sentinel → Content hub → PRODAFT USTA - IoC Threat Intelligence → Manage → Playbook
   templates**, select **PRODAFT USTA - Backfill Malicious URLs**, choose **Create playbook**, and supply
   `UstaApiKey` and `WorkspaceName`.
2. The playbook is created with a **system-assigned managed identity** automatically.
3. **Grant the role**: **Log Analytics workspace → Access control (IAM) → Add → Add role assignment**
   → Role **Microsoft Sentinel Contributor** → **Members: Managed identity** → pick this Logic App →
   **Review + assign**. **Open IAM on the workspace itself, not on the Logic App** — granting the role while the playbook's own blade is open scopes it to the Logic App (`.../Microsoft.Logic/workflows/...`), which looks correct in the portal but gives the identity no access to the workspace. The API connection deployed with the playbook uses that
   same managed identity, so there is no connection to authorize interactively.
4. Run it: **Logic App → Overview → Run Trigger → manual**. It does **not** run on a schedule.

## Deploy — via Azure CLI (run from this folder)

```bash
# ---- configuration ----
SUB="<subscription-id>"
RG="<resource-group>"                  # resource group of the Microsoft Sentinel workspace
WS="<workspace-name>"                  # Log Analytics workspace name
USTA_API_KEY="<usta-api-key>"
BACKFILL_DAYS=90
PLAYBOOK="PRODAFTUstaIoC-BackfillMaliciousUrls"

az account set --subscription "$SUB"

# 1. Deploy the playbook and capture its managed-identity principalId
PRINCIPAL_ID=$(az deployment group create \
  --resource-group "$RG" \
  --template-file azuredeploy.json \
  --parameters PlaybookName="$PLAYBOOK" \
               UstaApiKey="$USTA_API_KEY" \
               WorkspaceName="$WS" \
               BackfillDays=$BACKFILL_DAYS \
  --query properties.outputs.playbookPrincipalId.value -o tsv)

# 2. Grant that identity 'Microsoft Sentinel Contributor' on the workspace
az role assignment create \
  --assignee-object-id "$PRINCIPAL_ID" \
  --assignee-principal-type ServicePrincipal \
  --role "Microsoft Sentinel Contributor" \
  --scope "$(az monitor log-analytics workspace show -g "$RG" -n "$WS" --query id -o tsv)"

# 3. Run the backfill once
az rest --method POST \
  --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Logic/workflows/$PLAYBOOK/triggers/manual/run?api-version=2016-10-01"
```

> **RBAC propagation:** the role assignment can take a minute to become effective. If the first run
> shows 401/403 on **Upload STIX Objects**, simply run the trigger again.

## If the run does not finish

Paging is capped at **5000 pages / 4 hours** per run. If the feed holds more than that, the run ends
as **Failed** with error code `UstaBackfillIncomplete`. Everything fetched up to that point has
already been uploaded, and the message carries the timestamp to resume from:

```
Re-run this playbook with a trigger body of {"startTime":"2026-05-14T09:31:07Z"} to continue
from where it stopped.
```

`startTime` overrides `BackfillDays`, so the same mechanism loads any specific window you want:

```bash
az rest --method POST \
  --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Logic/workflows/$PLAYBOOK/triggers/manual/run?api-version=2016-10-01" \
  --body '{"startTime":"2026-05-14T09:31:07Z"}'
```

Because uploads are idempotent, resuming a little earlier than where it stopped is harmless.

## Behavior and notes

* Pages of 100 records are requested, following the API's `next` link until the feed is exhausted.
* The API key and the fetched records are hidden from the run history (`secureData` on the fetch action).
* A page returning a non-200 — for example HTTP 403 when the API key lacks Security Intelligence IoC
  permissions — stops paging and fails the run with `UstaFetchFailed` rather than reporting success.
* `valid_from` and `valid_until` are taken straight from the feed, exactly as the import playbook does.

## Verify

```kql
ThreatIntelIndicators
| where SourceSystem == "PRODAFT USTA - Malicious URLs"
| summarize Indicators = count(), Oldest = min(Created), Newest = max(Created)
```
