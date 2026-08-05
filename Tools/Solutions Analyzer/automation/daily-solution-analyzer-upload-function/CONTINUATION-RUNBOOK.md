# Daily Solution Analyzer Upload - Continuation Runbook

Use this after platform blockers are resolved.

## 1. Current state snapshot

Completed already:
- PIM Contributor activation for scope `/subscriptions/2f0fdbc8-ab60-4386-af30-dd0fac77130e/resourceGroups/dataacquisition-rg`.
- Function app created: `sa-csv-upload-func`.
- Storage account exists: `sacsvupldsa20260616`.
- Deployment scripts prepared and updated for:
  - Output branch source URL
  - Managed identity auth mode
  - Flex/Consumption/Premium hosting options

Blocking symptom that must be resolved externally:
- Function code publish currently fails (HTTP 415 / SKU-specific deployment behavior on current host path).

## 2. Decision tree (pick one path)

### Path A (preferred): Keep existing function app and fix publish path

Use this if your platform team resolves Flex deployment behavior for `sa-csv-upload-func`.

Run:

```powershell
cd "C:\Users\ofshezaf\GitHub\Azure-Sentinel\Tools\Solutions Analyzer\automation\daily-solution-analyzer-upload-function"

.\deploy_connectorsacceleration_staging.ps1 \
  -FunctionAppName "sa-csv-upload-func" \
  -StorageAccountName "sacsvupldsa20260616" \
  -HostingModel "flex"
```

### Path B: Premium hosting (if EP1 quota is approved)

Use this if East US EP1 quota is increased.

```powershell
cd "C:\Users\ofshezaf\GitHub\Azure-Sentinel\Tools\Solutions Analyzer\automation\daily-solution-analyzer-upload-function"

.\deploy_connectorsacceleration_staging.ps1 \
  -FunctionAppName "sa-csv-upload-func-prem" \
  -StorageAccountName "sacsvupldsa20260616" \
  -HostingModel "premium" \
  -AppServicePlanName "sa-csv-upload-plan"
```

### Path C: Existing known-good Function host (fastest operational fallback)

Use this if you have an existing Function App that can accept zip deployment.

```powershell
cd "C:\Users\ofshezaf\GitHub\Azure-Sentinel\Tools\Solutions Analyzer\automation\daily-solution-analyzer-upload-function"

.\deploy_function.ps1 \
  -SubscriptionId "2f0fdbc8-ab60-4386-af30-dd0fac77130e" \
  -ResourceGroup "dataacquisition-rg" \
  -Location "eastus" \
  -FunctionAppName "<existing-function-app-name>" \
  -StorageAccountName "sacsvupldsa20260616" \
  -KustoClusterUrl "https://dataacquisition.eastus.kusto.windows.net" \
  -KustoDatabase "dataacquisition" \
  -SaOutputRawBaseUrl "https://raw.githubusercontent.com/Azure/Azure-Sentinel/solution_analyzer_output/Tools/Solutions%20Analyzer" \
  -KustoAuthMode "managed-identity" \
  -HostingModel "premium" \
  -AppServicePlanName "<existing-plan-name>"
```

## 3. Post-deployment steps (required)

### 3.1 Get function managed identity principal id

```powershell
az functionapp identity show \
  --name "<function-app-name>" \
  --resource-group "dataacquisition-rg" \
  --subscription "2f0fdbc8-ab60-4386-af30-dd0fac77130e" \
  --query "principalId" -o tsv
```

### 3.2 Grant Kusto permissions

Open and apply:
- `grant_kusto_permissions.kql`

Replace placeholders:
- `<KUSTO_DATABASE>` -> `dataacquisition`
- `<FUNCTION_PRINCIPAL_ID>` -> principal id from previous step

### 3.3 Smoke check function metadata

```powershell
.\smoke_test_upload.ps1 \
  -SubscriptionId "2f0fdbc8-ab60-4386-af30-dd0fac77130e" \
  -ResourceGroup "dataacquisition-rg" \
  -FunctionAppName "<function-app-name>"
```

## 4. Validate first successful run

### 4.1 Trigger function manually

Portal path:
- Function App -> Functions -> `daily_solution_analyzer_upload` -> Run

### 4.2 Validate in logs

Check Application Insights / Monitor for:
- "Starting daily Solution Analyzer upload"
- "Daily Solution Analyzer upload completed successfully"

### 4.3 Validate in Kusto

Run in target database:

```kusto
.show tables
| where TableName startswith "solution_analyzer_"
| project TableName
| order by TableName asc
```

Quick row-count spot check:

```kusto
solution_analyzer_mapping
| count
```

## 5. What "done" looks like

All must be true:
- Function deploy succeeds without publish errors.
- Managed identity is enabled and granted Kusto permissions.
- Manual run succeeds.
- Expected `solution_analyzer_*` tables exist and are refreshed.
- Timer trigger is visible and enabled.

## 6. If it fails again

Collect these for quick triage:
- Deployment error output from the deployment script.
- `az functionapp log deployment list --name <function> --resource-group dataacquisition-rg -o json`.
- Function run logs (stdout/stderr) from Monitor.
- Current app settings names:

```powershell
az functionapp config appsettings list \
  --name "<function-app-name>" \
  --resource-group "dataacquisition-rg" \
  --query "[].name" -o tsv
```
