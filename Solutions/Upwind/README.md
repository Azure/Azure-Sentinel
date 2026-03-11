# Upwind Sentinel Connector

Microsoft Sentinel data connector that ingests **compute platform assets** from the [Upwind](https://upwind.io) cloud security platform into a custom Log Analytics table (`UpwindLogs_CL`) using an Azure Function and the [Azure Monitor Ingestion API](https://learn.microsoft.com/azure/azure-monitor/logs/logs-ingestion-api-overview) (DCE/DCR).

## What it does

- Timer-triggered Azure Function (Python 3.11) that runs on a configurable CRON schedule (default: top of every hour)
- Authenticates to Upwind via OAuth2 `client_credentials` flow
- Pages through all compute platform assets from `/v2/organizations/{orgId}/inventory/catalog/assets/search`
- Maps each asset to the `UpwindLogsAssets_CL` schema and ships records via the Azure Monitor Ingestion API

## Folder structure

```
UpwindLogsLoader/
├── SolutionMetadata.json
├── ReleaseNotes.md
├── Data/
│   └── Solution_UpwindLogsLoader.json
├── Package/
│   ├── 3.0.0.zip                    <- Sentinel content hub package
│   ├── createUiDefinition.json
│   ├── mainTemplate.json
│   └── testParameters.json
└── Data Connectors/
    ├── azuredeploy_UpwindLogsLoader_API_FunctionApp.json  <- ARM deploy template
    ├── UpwindLogsLoader_API_FunctionApp.json              <- Connector definition
    ├── createUiDef.json                                   <- Deployment wizard UI
    ├── UpwindLogsLoader.zip      <- Self-contained Function App package
    ├── host.json
    ├── requirements.txt
    ├── Logos/
    │   └── upwind.svg
    └── UpwindLogsLoader/
        ├── __init__.py
        ├── config.py
        ├── function.json
        ├── upwind_catalog_client.py
        └── upwind_client.py
```

## Deployment

Click the button below to deploy all required Azure resources (DCE, custom table, DCR, role assignment, storage, App Insights, Function App) in one step:

[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#view/Microsoft_Azure_CreateUIDef/CustomDeploymentBlade/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FUpwind%2FData%20Connectors%2Fazuredeploy_UpwindLogsLoader_API_FunctionApp.json/uiFormDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FUpwind%2FData%20Connectors%2FcreateUiDef.json)

### Parameters

| Parameter                        | Description                                                     |
|----------------------------------|-----------------------------------------------------------------|
| `WorkspaceName`                  | Name of your Log Analytics / Sentinel workspace                 |
| `UpwindOrgId`                    | Upwind Organization ID (Settings → Organization)                |
| `UpwindClientId`                 | Upwind API Client ID (Settings → API Keys)                      |
| `UpwindClientSecret`             | Upwind API Client Secret                                        |
| `AppInsightsWorkspaceResourceID` | Full Resource ID of the Log Analytics workspace                 |
| `UpwindLogsSchedule`             | CRON schedule for the function trigger (default: `0 0 * * * *`) |

## Table schema

| Column                      | Type     | API field                   |
|-----------------------------|----------|-----------------------------|
| `TimeGenerated`             | datetime | Ingestion time              |
| `id`                        | string   | `id`                        |
| `category`                  | string   | `category`                  |
| `sub_category`              | string   | `sub_category`              |
| `cloud_provider`            | string   | `cloud_provider`            |
| `cloud_account_id`          | string   | `cloud_account_id`          |
| `resource_type`             | string   | `resource_type`             |
| `cloud_resource_id`         | string   | `cloud_resource_id`         |
| `region`                    | string   | `region`                    |
| `name`                      | string   | `name`                      |
| `protected_by`              | string   | `protected_by`              |
| `status`                    | string   | `status`                    |
| `tags`                      | dynamic  | `tags`                      |
| `network_risk`              | dynamic  | `network_risk`              |
| `detection_risk`            | dynamic  | `detection_risk`            |
| `vulnerability_risk`        | dynamic  | `vulnerability_risk`        |
| `high_privilege_risk`       | dynamic  | `high_privilege_risk`       |
| `technologies`              | dynamic  | `technologies`              |
| `public_ip_addresses`       | dynamic  | `public_ip_addresses`       |
| `private_ip_addresses`      | dynamic  | `private_ip_addresses`      |
| `sensitive_data_at_rest`    | dynamic  | `sensitive_data_at_rest`    |
| `sensitive_data_in_transit` | dynamic  | `sensitive_data_in_transit` |

## Sample KQL queries

```kql
// All assets, most recent first
UpwindLogsAssets_CL
| sort by TimeGenerated desc

// Assets with critical vulnerabilities
UpwindLogsAssets_CL
| extend vulnCritical = toint(vulnerability_risk.critical_count)
| where vulnCritical > 0
| project name, resource_type, cloud_provider, region, vulnCritical
| sort by vulnCritical desc

// Assets with elevated privileges
UpwindLogsAssets_CL
| where tobool(high_privilege_risk.has_elevated_privilege) == true
| project name, resource_type, cloud_provider, region, cloud_account_id

// Asset count by cloud provider
UpwindLogsAssets_CL
| where TimeGenerated > ago(24h)
| summarize count() by cloud_provider
```