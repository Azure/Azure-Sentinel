# Release Notes — Upwind Logs Loader

## v1.0.0 (Initial Release)

### Features
- Azure Function (Python 3.11, timer trigger) that ingests compute platform assets from the Upwind cloud security platform
- OAuth2 client_credentials authentication against `https://auth.upwind.io/oauth/token`
- Paginated POST to Upwind `/v2/organizations/{orgId}/inventory/catalog/assets/search` with `compute_platform` category filter
- Cursor-based pagination with exponential backoff on 429 / transient errors
- Sends asset records to a custom Log Analytics table (`UpwindLogs_CL`) via the Azure Monitor Ingestion API (DCE + DCR)
- Single ARM template deploys all required Azure resources: DCE, custom table, DCR, role assignment, App Service Plan, storage, Application Insights, and Function App
- Configurable timer schedule (default: top of every hour)
