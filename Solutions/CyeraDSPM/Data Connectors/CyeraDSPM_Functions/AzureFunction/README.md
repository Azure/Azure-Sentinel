# Cyera → Sentinel Connector (Azure Function)

## Overview
This HTTP-triggered Python Function fetches data from the Cyera API and ingests it into Microsoft Sentinel via **Logs Ingestion (DCE/DCR)**.  
It maintains watermarks in Blob Storage to avoid duplicate ingestion.

---

## 1. Prerequisites
- Azure Subscription and Resource Group for the Function
- Existing **DCR / DCE** (same region as Log Analytics workspace)
- Cyera API credentials (`CYERA_CLIENT_ID`, `CYERA_SECRET`)
- Required Azure roles:
  - Contributor or Monitoring Contributor on DCR/DCE
  - Storage Blob Data Contributor (for Blob cursor storage)

---

## 2. Deploy Function App

### Create resources
```bash
SUB="<subscription-id>"
RG="<resource-group>"
LOC="<region>"
SA="stcyeraconn$RANDOM"
PLAN="plan-cyera"
FUNC="func-cyera-connector"

az group create -n "$RG" -l "$LOC"
az storage account create -n "$SA" -g "$RG" -l "$LOC" --sku Standard_LRS --kind StorageV2
az functionapp plan create -g "$RG" -n "$PLAN" -l "$LOC" --sku Y1 --is-linux
az functionapp create -g "$RG" -n "$FUNC" --storage-account "$SA" --plan "$PLAN"   --runtime python --functions-version 4 --os-type Linux --runtime-version 3.11
```

### Assign Managed Identity
```bash
az functionapp identity assign -g "$RG" -n "$FUNC"
MI=$(az functionapp identity show -g "$RG" -n "$FUNC" --query principalId -o tsv)

# Grant Monitoring Contributor on DCR
az role assignment create --assignee-object-id "$MI"   --role "Monitoring Contributor" --scope "<DCR_ARM_ID>"

# Grant Blob Data Contributor if using STATE_ACCOUNT_URL
az role assignment create --assignee-object-id "$MI"   --role "Storage Blob Data Contributor" --scope "<STORAGE_ACCOUNT_ARM_ID>"
```

---

## 3. Configure Application Settings

```bash
# Cyera API
az functionapp config appsettings set -g "$RG" -n "$FUNC" --settings   CYERA_BASE_URL="https://api.cyera.io"   CYERA_CLIENT_ID="<entra-app-client-id>"   CYERA_SECRET="<entra-app-client-secret>"

# DCR / DCE
az functionapp config appsettings set -g "$RG" -n "$FUNC" --settings   DCE_INGEST="https://<dce-name>.<region>-1.ingest.monitor.azure.com"   DCR_IMMUTABLE_ID="<dcr-immutable-id>"

# Canonical Streams (input to DCR)
az functionapp config appsettings set -g "$RG" -n "$FUNC" --settings   STREAM_ASSETS="Custom-CyeraAssets"   STREAM_IDENTITIES="Custom-CyeraIdentities"   STREAM_CLASSIFICATIONS="Custom-CyeraClassifications"   STREAM_ISSUES="Custom-CyeraIssues"

# Optional Blob-based state storage
az functionapp config appsettings set -g "$RG" -n "$FUNC" --settings   STATE_ACCOUNT_URL="https://$SA.blob.core.windows.net"   STATE_CONTAINER="cyera-cursors"   STATE_PREFIX="cursors"
```

---

## 4. Deploy the Connector Code
```bash
az functionapp deployment source config-zip -g "$RG" -n "$FUNC" --src cyera-connector.zip
```

---

## 5. Test Connectivity

Invoke directly:
```bash
FUNC_URL="https://$FUNC.azurewebsites.net/api/CyeraConnector"
curl "$FUNC_URL?entity=assets"
```
Expected output:
```json
{"entity":"assets","fetched":123,"ingested":123,"posts":1}
```

---

## 6. Scheduling
You can trigger runs using:
- Azure Logic App (HTTP Recurrence)
- Azure Automation
- A Timer Trigger (add CRON schedule to `function.json`)

---

## 7. Troubleshooting
| Issue | Likely Cause | Resolution |
|--------|---------------|------------|
| 401 Unauthorized | Wrong DCE URL or DCR ID | Verify `DCE_INGEST` and `DCR_IMMUTABLE_ID` |
| 403 Forbidden | MI lacks rights | Ensure Monitoring Contributor role on DCR |
| Blob errors | Missing Storage role | Add Storage Blob Data Contributor on account |
| No data in Sentinel | Mismatched streams | Verify input stream names match DCR source streams |

---

## 8. Security
The default `authLevel` is `"anonymous"`.  
Before production deployment, edit `CyeraConnector/function.json` to use:
```json
"authLevel": "function"
```
Then call with the Function key (`x-functions-key` header).

---

## 9. Validation Queries
```kusto
CyeraAssets_MS_CL | take 10
CyeraAssets_CL | order by ingestion_time() desc | take 10
CyeraIdentities_CL | take 10
CyeraClassifications_CL | take 10
CyeraIssues_CL | take 10
```

---

## 10. Version
CyeraConnector v1.6.2 — 2025‑10-23  
Tested on: Python 3.11 / Azure Functions v4 / azure-functions==1.20.0
