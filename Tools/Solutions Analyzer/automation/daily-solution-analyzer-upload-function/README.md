# Daily Solution Analyzer Upload (Azure Function)

This Function App uploads Solution Analyzer CSVs to Azure Data Explorer (Kusto) on a daily schedule.

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
  - Example: `https://raw.githubusercontent.com/<org>/<repo>/<branch>/Tools/Solutions%20Analyzer`
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

Deploy this folder as a Python Function App package.

Recommended:

1. `func azure functionapp publish <app-name>`
2. Configure app settings listed above
3. Enable system-assigned or user-assigned managed identity
4. Grant Kusto permissions

## Why Azure Function over Logic App

This workflow needs:

- Python/Kusto SDK control (table drop/create/mapping + queued ingestion)
- Strong retry/error logging
- Easy reuse of existing upload logic

An Azure Function is a better fit than Logic App for this code-heavy ingestion path.
