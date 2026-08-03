# PRODAFTUstaATP-Backfill

On-demand backfill playbook for the **PRODAFT USTA - Account Takeover Prevention** solution.

The codeless (CCF) data connector only polls **forward** from the moment it is connected.
This playbook loads history: it pages through the USTA compromised-credentials API and
pushes the records into the workspace via the **Logs Ingestion API**, applying the same
transform — password redaction and field mapping — as live polling. Plaintext passwords are
never written to the workspace.

The deployment is **self-contained**: it creates the `PRODAFTUstaCompromisedCredentials_CL`
table if it does not exist yet, provisions its own Data Collection Endpoint (DCE) and Data
Collection Rule (DCR) — the DCR uses the same schema and transform as the connector — and
grants its own managed identity the required role. You do **not** need to look up any
endpoint URI or DCR immutable ID by hand.

## Prerequisites

1. The **PRODAFT USTA - Account Takeover Prevention** solution is **installed**.
   The codeless connector only creates `PRODAFTUstaCompromisedCredentials_CL` once it
   ingests its first record, so you may run this backfill *before* any live data has
   arrived — the deployment creates the table itself when it is missing, and leaves it
   untouched when the connector already created it.
   (Connecting the data connector is recommended so forward polling is also active.)
2. A PRODAFT USTA long-lived API key.
3. Permission to deploy into the workspace resource group, to write tables on the workspace
   (`Microsoft.OperationalInsights/workspaces/tables/write`, included in Log Analytics
   Contributor), **and to create role assignments**
   (`Microsoft.Authorization/roleAssignments/write` — i.e. Owner or User Access
   Administrator on that scope), since the template assigns *Monitoring Metrics Publisher*
   to the playbook's identity automatically.

## Scripted deployment (run from this folder)

```bash
# ---- configuration ----
SUB="<subscription-id>"
RG="<usta-sentinel-resource-group>"        # resource group of the Sentinel workspace
WORKSPACE="<sentinel-workspace-name>"
LOCATION="<workspace-region>"              # e.g. westeurope
USTA_API_KEY="<usta-api-key>"
BACKFILL_DAYS=90
PLAYBOOK="PRODAFTUstaATP-Backfill"

az account set --subscription "$SUB"

# Deploy the playbook. It creates the target table if missing, its own DCE + DCR,
# derives the ingestion endpoint and DCR immutable ID automatically, and assigns
# its identity the 'Monitoring Metrics Publisher' role on that DCR.
az deployment group create \
  --resource-group "$RG" \
  --template-file azuredeploy.json \
  --parameters PlaybookName="$PLAYBOOK" \
               WorkspaceName="$WORKSPACE" \
               WorkspaceLocation="$LOCATION" \
               UstaApiKey="$USTA_API_KEY" \
               BackfillDays=$BACKFILL_DAYS

# Run the backfill once (or use 'Run Trigger' on the Logic App in the portal)
az rest --method POST \
  --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Logic/workflows/$PLAYBOOK/triggers/manual/run?api-version=2016-10-01"
```

> If the workspace is in a **different resource group** than this deployment, add
> `WorkspaceResourceGroup="<workspace-rg>"` to the parameters.

> **RBAC propagation:** the role assignment created by the deployment can take a minute to
> become effective. If the first run shows 403 responses from the ingestion API in the run
> history, simply run the trigger again.

Monitor progress under **Logic App → Runs history**, then verify data:

```kql
PRODAFTUstaCompromisedCredentials
| sort by Created desc
| take 10
```

## Behavior and notes

* The backfill writes through its own DCR into the same `PRODAFTUstaCompromisedCredentials_CL`
  table as the connector, using an identical transform, so backfilled and live rows are
  indistinguishable to the solution's content.
* The table is deployed with the same schema the connector declares. Deploying a table is a
  PUT, so it creates the table when absent and is a no-op when it already exists. Retention
  comes from `TableRetentionDays` (default 90, matching the connector). If you have changed
  the table's retention after it was created, pass your current value so a redeploy does not
  reset it.
* Pages of 100 records are posted per request — well under the Logs Ingestion API's 1 MB
  request limit. The loop follows the API's `next` URL until exhausted (up to 1000 pages / 4 hours).
* The API key and the fetched credential data are hidden from the Logic App run history:
  secure inputs are enabled on both HTTP actions, and secure outputs on the fetch action
  (a successful ingestion returns an empty 204 body, so its output carries no data).
* `TimeGenerated` is set at ingestion time by the DCR; the true event time is preserved in
  `Created`, which the solution's rules, hunting query, and workbook filter on — so a
  backfill does not trigger an alert storm.
* Log Analytics is append-only: re-running the playbook stores duplicate rows for tickets
  that are already ingested. The `PRODAFTUstaCompromisedCredentials` parser function
  deduplicates at query time (one row per `TicketId`), so duplicates are invisible to all
  solution content.
