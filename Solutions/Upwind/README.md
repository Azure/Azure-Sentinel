# Upwind Sentinel Connector

Microsoft Sentinel data connector that ingests **compute platform assets** from the [Upwind](https://upwind.io) cloud security platform into a custom Log Analytics table (`UpwindLogs_CL`) using an Azure Function and the [Azure Monitor Ingestion API](https://learn.microsoft.com/azure/azure-monitor/logs/logs-ingestion-api-overview) (DCE/DCR).

## What it does

- Timer-triggered Azure Function (Python 3.11) that runs on a configurable CRON schedule (default: top of every hour)
- Authenticates to Upwind via OAuth2 `client_credentials` flow
- Pages through all compute platform assets from `/v2/organizations/{orgId}/inventory/catalog/assets/search`
- Maps each asset to the `UpwindLogs_CL` schema and ships records via the Azure Monitor Ingestion API

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

| Parameter | Description |
|---|---|
| `WorkspaceName` | Name of your Log Analytics / Sentinel workspace |
| `UpwindOrgId` | Upwind Organization ID (Settings → Organization) |
| `UpwindClientId` | Upwind API Client ID (Settings → API Keys) |
| `UpwindClientSecret` | Upwind API Client Secret |
| `AppInsightsWorkspaceResourceID` | Full Resource ID of the Log Analytics workspace |
| `UpwindLogsSchedule` | CRON schedule for the function trigger (default: `0 0 * * * *`) |

## Table schema — `UpwindLogs_CL`

| Column | Type | API field |
|---|---|---|
| `TimeGenerated` | datetime | Ingestion time |
| `AssetId` | string | `id` |
| `Category` | string | `category` |
| `SubCategory` | string | `sub_category` |
| `CloudProvider` | string | `cloud_provider` |
| `CloudAccountId` | string | `cloud_account_id` |
| `ResourceType` | string | `resource_type` |
| `CloudResourceId` | string | `cloud_resource_id` |
| `Region` | string | `region` |
| `AssetName` | string | `name` |
| `ProtectedBy` | string | `protected_by` |
| `Status` | string | `status` |
| `Tags` | dynamic | `tags` |
| `NetworkRisk` | dynamic | `network_risk` |
| `DetectionRisk` | dynamic | `detection_risk` |
| `VulnerabilityRisk` | dynamic | `vulnerability_risk` |
| `HighPrivilegeRisk` | dynamic | `high_privilege_risk` |
| `Technologies` | dynamic | `technologies` |
| `PublicIpAddresses` | dynamic | `public_ip_addresses` |
| `PrivateIpAddresses` | dynamic | `private_ip_addresses` |
| `SensitiveDataAtRest` | dynamic | `sensitive_data_at_rest` |
| `SensitiveDataInTransit` | dynamic | `sensitive_data_in_transit` |

## Sample KQL queries

```kql
// All assets, most recent first
UpwindLogs_CL
| sort by TimeGenerated desc

// Assets with critical vulnerabilities
UpwindLogs_CL
| extend vulnCritical = toint(VulnerabilityRisk.critical_count)
| where vulnCritical > 0
| project AssetName, ResourceType, CloudProvider, Region, vulnCritical
| sort by vulnCritical desc

// Assets with elevated privileges
UpwindLogs_CL
| where tobool(HighPrivilegeRisk.has_elevated_privilege) == true
| project AssetName, ResourceType, CloudProvider, Region, CloudAccountId

// Asset count by cloud provider
UpwindLogs_CL
| where TimeGenerated > ago(24h)
| summarize count() by CloudProvider
```
