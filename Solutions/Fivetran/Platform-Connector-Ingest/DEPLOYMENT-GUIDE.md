# Deployment guide: Fivetran Platform Connector ingest into Sentinel

End-to-end runbook for the third connection path (Platform Connector -> ADLS -> Azure
Function -> Logs Ingestion API -> Sentinel). Every value in angle brackets is yours to
set; nothing here is environment-specific.

## Prerequisites

- A Log Analytics workspace with Microsoft Sentinel enabled (`<workspace-name>` in
  resource group `<sentinel-rg>`).
- The Fivetran Platform Connector already landing parquet in an ADLS Gen2 account
  (`<adls-account>`, container `<container>`, lake root `<lake-root>/<schema>/`), in
  resource group `<storage-rg>`.
- Azure CLI (`az`) 2.60+ with the `eventgrid` extension, and Azure Functions Core Tools
  v4 (`func`).
- Contributor on `<sentinel-rg>` and `<function-rg>`, plus rights to create role
  assignments on the storage account and DCR.

Set shell variables once:

```bash
SUB=<subscription-id>
SENTINEL_RG=<sentinel-rg>
STORAGE_RG=<storage-rg>
FUNC_RG=<function-rg>
LOCATION=<region>
WORKSPACE=<workspace-name>
ADLS=<adls-account>
CONTAINER=<container>
LAKE_PREFIX=<lake-root>/<schema>          # path under the container, no table segment
FUNC_APP=func-fivetran-platform
FUNC_SA=<function-app-storage-account>    # small storage account for the function host
UAMI=id-fivetran-platform-ingest
```

## 1. Tables + DCR (Sentinel side, bicep)

```bash
az bicep build -f bicep/sentinel-tables-dcr.bicep    # optional local compile

az deployment group create \
  -g "$SENTINEL_RG" \
  -f bicep/sentinel-tables-dcr.bicep \
  -p workspaceName="$WORKSPACE"
```

Record the outputs `logsIngestionEndpoint` and `dcrImmutableId`; you set them as function
app settings in step 4. (You will re-run this in step 3 with `functionPrincipalId` once
the identity exists, to grant it Monitoring Metrics Publisher on the DCR.)

## 2. User-assigned managed identity (created first)

```bash
az identity create -g "$FUNC_RG" -n "$UAMI"
UAMI_ID=$(az identity show -g "$FUNC_RG" -n "$UAMI" --query id -o tsv)
UAMI_PRINCIPAL=$(az identity show -g "$FUNC_RG" -n "$UAMI" --query principalId -o tsv)
UAMI_CLIENT=$(az identity show -g "$FUNC_RG" -n "$UAMI" --query clientId -o tsv)
```

## 3. Pre-grant RBAC (managed identity, no keys)

Grant the identity read on the lake, and Monitoring Metrics Publisher on the DCR. Because
the identity already exists, both grants are in place before the function first runs.

```bash
# Read the lake parquet
az role assignment create \
  --assignee-object-id "$UAMI_PRINCIPAL" --assignee-principal-type ServicePrincipal \
  --role "Storage Blob Data Reader" \
  --scope "/subscriptions/$SUB/resourceGroups/$STORAGE_RG/providers/Microsoft.Storage/storageAccounts/$ADLS"

# Post to the DCR: re-run the bicep with the principal id (idempotent role assignment)
az deployment group create \
  -g "$SENTINEL_RG" \
  -f bicep/sentinel-tables-dcr.bicep \
  -p workspaceName="$WORKSPACE" functionPrincipalId="$UAMI_PRINCIPAL"
```

## 4. Flex Consumption function app

```bash
az functionapp create \
  --resource-group "$FUNC_RG" \
  --name "$FUNC_APP" \
  --flexconsumption-location "$LOCATION" \
  --runtime python \
  --runtime-version 3.11 \
  --storage-account "$FUNC_SA" \
  --assign-identity "$UAMI_ID"

# App settings: DCR endpoint + rule id from step 1 outputs, and the UAMI client id so
# DefaultAzureCredential selects the user-assigned identity.
az functionapp config appsettings set -g "$FUNC_RG" -n "$FUNC_APP" --settings \
  DCR_ENDPOINT="<logsIngestionEndpoint-from-step-1>" \
  DCR_RULE_ID="<dcrImmutableId-from-step-1>" \
  AUDIT_STREAM="Custom-Fivetran_AuditTrail_CL" \
  PLATFORM_STREAM="Custom-Fivetran_Platform_CL" \
  AZURE_CLIENT_ID="$UAMI_CLIENT"

# Security hardening
az functionapp update -g "$FUNC_RG" -n "$FUNC_APP" --set httpsOnly=true
az functionapp config set -g "$FUNC_RG" -n "$FUNC_APP" --min-tls-version 1.2
az resource update --resource-group "$FUNC_RG" --name scm \
  --namespace Microsoft.Web --resource-type basicPublishingCredentialsPolicies \
  --parent "sites/$FUNC_APP" --set properties.allow=false
az resource update --resource-group "$FUNC_RG" --name ftp \
  --namespace Microsoft.Web --resource-type basicPublishingCredentialsPolicies \
  --parent "sites/$FUNC_APP" --set properties.allow=false
```

Publish the code from this folder:

```bash
cd function
func azure functionapp publish "$FUNC_APP" --python
cd ..
```

## 5. Event Grid subscription (filtered, dead-lettered)

Create a dead-letter container, then subscribe the function to Blob Created events for
the lake data files only.

```bash
# Dead-letter container (can be on the function storage account)
az storage container create --account-name "$FUNC_SA" --name eventgrid-deadletter --auth-mode login

FUNC_ID=$(az functionapp show -g "$FUNC_RG" -n "$FUNC_APP" --query id -o tsv)
DEADLETTER_ID=$(az storage account show -g "$FUNC_RG" -n "$FUNC_SA" --query id -o tsv)

az eventgrid event-subscription create \
  --name fivetran-platform-ingest \
  --source-resource-id "/subscriptions/$SUB/resourceGroups/$STORAGE_RG/providers/Microsoft.Storage/storageAccounts/$ADLS" \
  --endpoint-type azurefunction \
  --endpoint "$FUNC_ID/functions/FivetranPlatformIngest" \
  --included-event-types Microsoft.Storage.BlobCreated \
  --subject-begins-with "/blobServices/default/containers/$CONTAINER/blobs/$LAKE_PREFIX/" \
  --subject-ends-with ".parquet" \
  --deadletter-endpoint "$DEADLETTER_ID/blobServices/default/containers/eventgrid-deadletter" \
  --max-delivery-attempts 30 \
  --event-ttl 1440
```

The subject filter drops everything except `.parquet` under the lake root; the function
further restricts to `/<table>/data/*.parquet`, so `_delta_log` checkpoints and Iceberg
metadata never ingest. If you only want the audit table, narrow `--subject-begins-with`
to `.../$LAKE_PREFIX/audit_trail/`.

### Fallback: webhook endpoint

If the `azurefunction` endpoint type is unavailable in your environment, use a webhook to
the Event Grid extension endpoint instead (rotate the system key periodically):

```bash
KEY=$(az functionapp keys list -g "$FUNC_RG" -n "$FUNC_APP" --query systemKeys.eventgrid_extension -o tsv)
ENDPOINT="https://$FUNC_APP.azurewebsites.net/runtime/webhooks/eventgrid?functionName=FivetranPlatformIngest&code=$KEY"
# ...same az eventgrid event-subscription create but with:
#   --endpoint-type webhook --endpoint "$ENDPOINT"
```

## 6. Content (parsers + hunting query)

Import the three files in `content/` into the workspace (as saved functions / a hunting
query), or package them via your content pipeline:

- `vimAuditEventFivetranAuditTrail.yaml`
- `ASimAuditEventFivetranAuditTrail.yaml`
- `FivetranAuditTrailSensitiveChanges_ASIM_Hunting.yaml`

## 7. Verify

```kql
Fivetran_AuditTrail_CL | take 10
Fivetran_Platform_CL | summarize count() by FivetranTable
ASimAuditEventFivetranAuditTrail | take 10
```

Allow 10-15 minutes after the first blob event for rows to appear (table/DCR schema
warm-up). Check function health in Application Insights:

```kql
traces | where operation_Name == "FivetranPlatformIngest" | order by timestamp desc | take 50
```

## 8. ASIM validation (before proposing upstream)

Run `ASimSchemaTester` and `ASimDataTester` against `vimAuditEventFivetranAuditTrail` in
a workspace with real rows. Register Fivetran Platform with the `imAuditEvent` unifying
parser for the cross-source blend.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Function shows "0 functions" | Dependency build (old Consumption plan) | Confirm the app is on **Flex Consumption**; Flex builds Python deps remotely. |
| 403 reading the blob | Identity missing Storage Blob Data Reader, or `AZURE_CLIENT_ID` not set | Re-check step 3 grant and the `AZURE_CLIENT_ID` app setting. |
| 403 posting to Logs Ingestion | Identity missing Monitoring Metrics Publisher on the DCR | Re-run step 3 bicep with `functionPrincipalId`. |
| No rows, no invocations | Subject filter too narrow, or Event Grid not firing | Check the Event Grid subscription metrics and the dead-letter container. |
| Duplicate audit rows | Delta/Iceberg compaction re-emit (expected) | The ASIM parser dedupes by `id`; query through the parser, not the raw table. |
