# Upwind Sentinel Connector

Microsoft Sentinel data connector that ingests data from **six Upwind API endpoints** — inventory/catalog assets (all categories), vulnerability findings, threat detections, threat events, threat stories, and configuration (posture) findings — from the [Upwind](https://upwind.io) cloud security platform into six custom Log Analytics tables, using an Azure Function and the [Azure Monitor Ingestion API](https://learn.microsoft.com/azure/azure-monitor/logs/logs-ingestion-api-overview) (DCE/DCR).

## What it does

- Timer-triggered Azure Function (Python 3.11) that runs on a configurable CRON schedule (default: top of every hour)
- Authenticates to Upwind via OAuth2 `client_credentials` flow
- Fetches all six datasets on every run, **independently** — if one Upwind endpoint fails or isn't entitled for your org, the others still complete
- Ships each dataset to its own DCR stream / custom table via the Azure Monitor Ingestion API

| Dataset | Upwind endpoint | Sync style | Destination table |
|---|---|---|---|
| Inventory / catalog assets (all categories) | `POST /v2/organizations/{orgId}/inventory/catalog/assets/search` | Full current-state snapshot | `UpwindCatalogAssets_CL` |
| Vulnerability findings | `GET /v1/organizations/{orgId}/vulnerability-findings` | Full current-state snapshot | `UpwindVulnerabilityFindings_CL` |
| Threat detections | `GET /v1/organizations/{orgId}/threat-detections` | Time-windowed (`UpwindThreatLookbackMinutes`) | `UpwindThreatDetections_CL` |
| Threat events | `GET /v1/organizations/{orgId}/threat-events` | Time-windowed (`UpwindThreatLookbackMinutes`) | `UpwindThreatEvents_CL` |
| Threat stories | `POST /v2/organizations/{orgId}/threats/stories/search` | Time-windowed (`UpwindThreatLookbackMinutes`) | `UpwindThreatStories_CL` |
| Configuration (posture) findings | `POST /v2/organizations/{orgId}/configurations/findings/search` | Time-windowed (`UpwindThreatLookbackMinutes`) | `UpwindConfigurationFindings_CL` |

The two full-snapshot datasets (inventory assets, vulnerability findings) represent Upwind's *current* state and are re-pulled in full on every run. The four time-windowed datasets pull everything seen/updated in the last `UpwindThreatLookbackMinutes` (default 90) — set that comfortably larger than `UpwindCatalogSchedule`'s interval so nothing is missed between runs; overlap just produces harmless duplicate rows.

> **Note:** `title` and `type` are reserved/invalid column names for Log Analytics custom tables, so the four affected datasets (threat detections, threat events, threat stories, configuration findings) rename them to `title_text` and `event_type` before upload.

## Folder structure

```
UpwindCatalogLoader/
├── SolutionMetadata.json
├── ReleaseNotes.md
├── Data/
│   └── Solution_UpwindCatalogLoader.json
├── Package/
│   ├── 1.0.0.zip                    <- Sentinel content hub package
│   ├── createUiDefinition.json
│   ├── mainTemplate.json
│   └── testParameters.json
└── Data Connectors/
    ├── azuredeploy_UpwindCatalogLoader_API_FunctionApp.json  <- ARM deploy template
    ├── UpwindCatalogLoader_API_FunctionApp.json              <- Connector definition
    ├── UpwindCatalogLoader.zip      <- Self-contained Function App package
    ├── host.json
    ├── proxies.json
    ├── requirements.txt
    └── UpwindLogsLoader/
        ├── __init__.py                              <- fetches + uploads all 6 datasets
        ├── config.py
        ├── function.json
        ├── upwind_client.py                          <- shared auth/retry/pagination
        ├── upwind_catalog_client.py                  <- inventory/catalog assets
        ├── upwind_vulnerability_client.py             <- vulnerability findings
        ├── upwind_threat_detections_client.py
        ├── upwind_threat_events_client.py
        ├── upwind_threat_stories_client.py
        └── upwind_configuration_findings_client.py
```

## Deployment

Click the button below to deploy all required Azure resources (DCE, 6 custom tables, DCR with 6 streams, role assignment, storage, App Insights, Function App) in one step:

[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FMitchellGulledge3%2Fupwind%2Fmain%2FData%2520Connectors%2Fazuredeploy_UpwindCatalogLoader_API_FunctionApp.json)

### Parameters

| Parameter | Description |
|---|---|
| `WorkspaceName` | Name of your Log Analytics / Sentinel workspace |
| `WorkspaceResourceGroup` | *(optional)* Resource group containing that workspace. Defaults to the resource group you're deploying into. Set this if your workspace lives in a **different** resource group than the one you want these new resources (Function App, storage, DCE/DCR) created in — this template supports that split. Requires write permission on both resource groups. |
| `UpwindOrgId` | Upwind Organization ID (Settings → Organization) |
| `UpwindClientId` | Upwind API Client ID (Settings → API Keys) |
| `UpwindClientSecret` | Upwind API Client Secret |
| `AzureClientObjectId` | Object ID of the App Registration used by the Function App |
| `AppInsightsWorkspaceResourceID` | Full Resource ID of the Log Analytics workspace |
| `UpwindCatalogSchedule` | CRON schedule for the function trigger (default: `0 0 * * * *`) |
| `UpwindThreatLookbackMinutes` | *(optional, default 90)* Lookback window in minutes for threat detections, threat events, threat stories, and configuration findings. Should exceed `UpwindCatalogSchedule`'s interval. |

## Table schemas

### `UpwindCatalogAssets_CL` — inventory / catalog assets (all categories)

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

### `UpwindVulnerabilityFindings_CL`

| Column | Type | API field |
|---|---|---|
| `TimeGenerated` | datetime | Ingestion time |
| `id` | string | `id` |
| `cve_id` | string | `cve_id` |
| `severity` | string | `severity` |
| `status` | string | `status` |
| `first_seen_time` | datetime | `first_seen_time` |
| `last_scan_time` | datetime | `last_scan_time` |
| `resource` | dynamic | `resource` |
| `package` | dynamic | `package` |
| `fix` | dynamic | `fix` |
| `fix_available` | string | `fix_available` |
| `exploitable` | string | `exploitable` |
| `internet_exposure` | string | `internet_exposure` |
| `source` | string | `source` |
| `image_name` | string | `image_name` |
| `remediation` | dynamic | `remediation` |

### `UpwindThreatDetections_CL`

| Column | Type | API field |
|---|---|---|
| `TimeGenerated` | datetime | Ingestion time |
| `id` | string | `id` |
| `title_text` | string | `title` (renamed — reserved column name) |
| `description` | string | `description` |
| `category` | string | `category` |
| `event_type` | string | `type` (renamed — reserved column name) |
| `severity` | string | `severity` |
| `status` | string | `status` |
| `first_seen_time` | datetime | `first_seen_time` |
| `last_seen_time` | datetime | `last_seen_time` |
| `occurrence_count` | long | `occurrence_count` |
| `resource` | dynamic | `resource` |
| `mitre_attacks` | dynamic | `mitre_attacks` |
| `triggers` | dynamic | `triggers` |

### `UpwindThreatEvents_CL`

| Column | Type | API field |
|---|---|---|
| `TimeGenerated` | datetime | Ingestion time |
| `id` | string | `id` |
| `title_text` | string | `title` (renamed — reserved column name) |
| `category` | string | `category` |
| `event_type` | string | `type` (renamed — reserved column name) |
| `severity` | string | `severity` |
| `status` | string | `status` |
| `first_seen_time` | datetime | `first_seen_time` |
| `last_seen_time` | datetime | `last_seen_time` |
| `resource` | dynamic | `resource` |
| `raw` | dynamic | `raw` |

### `UpwindThreatStories_CL`

| Column | Type | API field |
|---|---|---|
| `TimeGenerated` | datetime | Ingestion time |
| `id` | string | `id` |
| `title_text` | string | `title` (renamed — reserved column name) |
| `status` | string | `status` |
| `severity` | string | `severity` |
| `create_time` | datetime | `create_time` |
| `update_time` | datetime | `update_time` |
| `primary_resource` | dynamic | `primary_resource` |
| `summary` | string | `summary` |
| `detection_ids` | dynamic | `detection_ids` |
| `event_ids` | dynamic | `event_ids` |
| `risk_factors` | dynamic | `risk_factors` |

### `UpwindConfigurationFindings_CL`

| Column | Type | API field |
|---|---|---|
| `TimeGenerated` | datetime | Ingestion time |
| `id` | string | `id` |
| `title_text` | string | `title` (renamed — reserved column name) |
| `status` | string | `status` |
| `severity` | string | `severity` |
| `first_seen_time` | datetime | `first_seen_time` |
| `evaluation_time` | datetime | `evaluation_time` |
| `framework` | dynamic | `framework` |
| `rule` | dynamic | `rule` |
| `resource` | dynamic | `resource` |
| `risk_categories` | dynamic | `risk_categories` |

## Sample KQL queries

```kql
// All assets, most recent first
UpwindCatalogAssets_CL
| sort by TimeGenerated desc

// Assets with critical vulnerabilities
UpwindCatalogAssets_CL
| extend vulnCritical = toint(VulnerabilityRisk.critical_count)
| where vulnCritical > 0
| project AssetName, ResourceType, CloudProvider, Region, vulnCritical
| sort by vulnCritical desc

// Assets with elevated privileges
UpwindCatalogAssets_CL
| where tobool(HighPrivilegeRisk.has_elevated_privilege) == true
| project AssetName, ResourceType, CloudProvider, Region, CloudAccountId

// Asset count by cloud provider
UpwindCatalogAssets_CL
| where TimeGenerated > ago(24h)
| summarize count() by CloudProvider

// Open critical/high vulnerabilities with an available fix
UpwindVulnerabilityFindings_CL
| where status == "open" and severity in ("critical", "high") and fix_available == "true"
| project cve_id, severity, image_name, resource, fix
| sort by severity asc

// Threat detections in the last 24h by severity
UpwindThreatDetections_CL
| where TimeGenerated > ago(24h)
| summarize count() by severity

// Threat stories still open, most recently updated first
UpwindThreatStories_CL
| where status != "closed"
| sort by update_time desc
| project id, title_text, severity, status, update_time

// Failing configuration findings by framework
UpwindConfigurationFindings_CL
| where status == "fail"
| mv-expand framework
| summarize count() by tostring(framework.name)
```
