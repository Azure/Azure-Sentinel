# PRODAFTUstaATP-Backfill

On-demand backfill playbook for the **PRODAFT USTA - Account Takeover Prevention** solution.

The codeless (CCF) data connector only polls **forward** from the moment it is connected.
This playbook loads history: it pages through the USTA compromised-credentials API and
pushes the records to the connector's **Data Collection Endpoint** (Logs Ingestion API),
so the same DCR transform — password redaction and field mapping — is applied exactly as
for live polling. Plaintext passwords are never written to the workspace.

## Prerequisites

1. The solution is **installed** (this deploys the `PRODAFTUstaATPDCR` data collection
   rule, its data collection endpoint, and the `PRODAFTUstaCompromisedCredentials_CL`
   table) and the **PRODAFT USTA - Account Takeover Prevention** data connector is
   **connected** (this creates the poller and starts polling forward).
2. A PRODAFT USTA long-lived API key.
3. Azure CLI signed in with permission to deploy into the workspace resource group and to
   create role assignments on the DCR (`Microsoft.Authorization/roleAssignments/write`,
   i.e. Owner or User Access Administrator on that scope).

## Scripted deployment (run from this folder)

```bash
# ---- configuration ----
SUB="<subscription-id>"
RG="<usta-sentinel-resource-group>"        # resource group of the Sentinel workspace
USTA_API_KEY="<usta-api-key>"
BACKFILL_DAYS=90
PLAYBOOK="PRODAFTUstaATP-Backfill"

az account set --subscription "$SUB"

# 1. Locate the connector's DCR (deployed by the solution as 'PRODAFTUstaATPDCR')
DCR_ID=$(az monitor data-collection rule list --resource-group "$RG" \
  --query "[?contains(name, 'PRODAFTUstaATP')].id | [0]" -o tsv)
DCR_IMMUTABLE_ID=$(az monitor data-collection rule show --ids "$DCR_ID" \
  --query immutableId -o tsv)
DCE_ID=$(az monitor data-collection rule show --ids "$DCR_ID" \
  --query dataCollectionEndpointId -o tsv)
# If DCE_ID comes back empty, list endpoints directly:
#   az monitor data-collection endpoint list -g "$RG" -o table

# 2. Resolve the DCE logs-ingestion URI
DCE_URI=$(az monitor data-collection endpoint show --ids "$DCE_ID" \
  --query logsIngestion.endpoint -o tsv)
echo "DCR immutable ID: $DCR_IMMUTABLE_ID"
echo "DCE ingestion URI: $DCE_URI"

# 3. Deploy the playbook (captures its managed identity from the deployment output)
PRINCIPAL_ID=$(az deployment group create \
  --resource-group "$RG" \
  --template-file azuredeploy.json \
  --parameters PlaybookName="$PLAYBOOK" \
               DataCollectionEndpointUri="$DCE_URI" \
               DataCollectionRuleImmutableId="$DCR_IMMUTABLE_ID" \
               UstaApiKey="$USTA_API_KEY" \
               BackfillDays=$BACKFILL_DAYS \
  --query properties.outputs.playbookPrincipalId.value -o tsv)

# 4. Grant the playbook's identity 'Monitoring Metrics Publisher' on the DCR
az role assignment create \
  --assignee-object-id "$PRINCIPAL_ID" \
  --assignee-principal-type ServicePrincipal \
  --role "Monitoring Metrics Publisher" \
  --scope "$DCR_ID"

# 5. Run the backfill once (or use 'Run Trigger' on the Logic App in the portal)
az rest --method POST \
  --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Logic/workflows/$PLAYBOOK/triggers/manual/run?api-version=2016-10-01"
```

> **RBAC propagation:** the role assignment in step 4 can take a minute to become
> effective. If the first run shows 403 responses from the ingestion API in the run
> history, simply run the trigger again (step 5).

Monitor progress under **Logic App → Runs history**, then verify data:

```kql
PRODAFTUstaCompromisedCredentials
| sort by Created desc
| take 10
```

## Behavior and notes

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
