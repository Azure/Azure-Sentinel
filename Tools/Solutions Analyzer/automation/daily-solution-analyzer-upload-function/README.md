# Daily Solution Analyzer Upload (Azure Function)

This Function App uploads Solution Analyzer CSVs to Azure Data Explorer (Kusto) on a daily schedule.

If deployment was blocked and you need to resume later, use:

- [CONTINUATION-RUNBOOK.md](CONTINUATION-RUNBOOK.md)

It reuses the existing uploader in [../../upload_to_kusto.py](../../upload_to_kusto.py) and runs it with:

- `--solution-analyzer`
- `--raw-base-url` pointing to the output branch CSV location
- `--auth-mode managed-identity` (recommended)

## Trigger

Timer trigger schedule in [function_app.py](function_app.py):

- `0 15 2 * * *` (daily at 02:15 UTC)

## Required App Settings

- `KUSTO_CLUSTER_URL`: e.g. `https://dataacquisition.eastus.kusto.windows.net`
- `KUSTO_DATABASE`: target database name
- `SA_OUTPUT_RAW_BASE_URL`: raw GitHub URL for output branch CSV root
  - Current output branch URL: `https://raw.githubusercontent.com/Azure/Azure-Sentinel/solution_analyzer_output/Tools/Solutions%20Analyzer`
- `KUSTO_AUTH_MODE`: `managed-identity` or `azure-cli`
  - Use `managed-identity` in Azure
- `MANAGED_IDENTITY_CLIENT_ID` (optional): user-assigned MI client ID

## Permissions

Grant the Function App managed identity permissions on the Kusto database:

- Admin path: `.add database <db> ingestors ('aadapp=<objectId>')`
- And if needed for DDL (drop/create): admin-level permissions for table management

The uploader drops and recreates target tables before ingestion, so table admin permissions are required.

## Local test

1. Copy [local.settings.sample.json](local.settings.sample.json) to `local.settings.json`
2. Fill values
3. Start Function host:

```bash
func start
```

4. Trigger manually from Azure Portal or wait for the schedule.

## Deployment notes

You can deploy end-to-end with the script in this folder:

```powershell
cd "Tools/Solutions Analyzer/automation/daily-solution-analyzer-upload-function"

./deploy_connectorsacceleration_staging.ps1 `
  -FunctionAppName "<function-app-name>" `
  -StorageAccountName "<storage-account-name>" `
  -AppServicePlanName "<plan-name>"
```

This wrapper preloads your known environment defaults:

- Subscription: `2f0fdbc8-ab60-4386-af30-dd0fac77130e` (`ConnectorsAcceleration.Staging`)
- Resource group: `dataacquisition-rg`
- Location: `eastus`
- Output branch CSV source: `solution_analyzer_output`

If you need full control, use:

```powershell
./deploy_function.ps1 `
  -SubscriptionId "<subscription-guid>" `
  -ResourceGroup "<rg-name>" `
  -Location "eastus" `
  -FunctionAppName "<function-app-name>" `
  -StorageAccountName "<storage-account-name>" `
  -AppServicePlanName "<plan-name>" `
  -KustoClusterUrl "https://dataacquisition.eastus.kusto.windows.net" `
  -KustoDatabase "dataacquisition" `
  -SaOutputRawBaseUrl "https://raw.githubusercontent.com/<org>/<repo>/<output-branch>/Tools/Solutions%20Analyzer" `
  -KustoAuthMode "managed-identity"
```

Then grant Kusto permissions using [grant_kusto_permissions.kql](grant_kusto_permissions.kql):

1. Get the Function principal ID from deploy output (or `az functionapp identity show ...`).
2. Replace placeholders in the KQL file.
3. Execute commands on the target Kusto database.

Finally run a smoke validation:

```powershell
./smoke_test_upload.ps1 -SubscriptionId "<subscription-guid>" -ResourceGroup "<rg-name>" -FunctionAppName "<function-app-name>"
```

## Why Azure Function over Logic App

This workflow needs:

- Python/Kusto SDK control (table drop/create/mapping + queued ingestion)
- Strong retry/error logging
- Easy reuse of existing upload logic

An Azure Function is a better fit than Logic App for this code-heavy ingestion path.
