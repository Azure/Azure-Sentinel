# SAP Integration Suite - Microsoft Sentinel Connector Tool

This directory contains PowerShell scripts to connect Microsoft Sentinel to SAP Integration Suite runtime instances. The tool creates multiple Sentinel connections based on destinations defined in a CSV file.

## Overview

This onboarding script is primarily intended for the **agentless data connector for SAP ERP** but works equally well for community extensions that follow the same integration pattern.

The SAP Integration Suite connector uses the `SAPCC` connector definition to ingest SAP data into standard Microsoft SAP tables:

| Table | Description |
|-------|-------------|
| `ABAPAuditLog` | SAP Security Audit Log events |
| `ABAPChangeDocsLog` | SAP Change Documents |
| `ABAPUserDetails` | User master data |
| `ABAPAuthorizationDetails` | Role and authorization details |
| `SentinelHealth` | Connector health and heartbeat |

These standard tables integrate natively with the Microsoft Sentinel Solution for SAP analytics rules, workbooks, and hunting queries.

## Key Features

- **Dual-mode credential support**:
  - **Cloud Foundry Mode**: Credentials retrieved at runtime via CF CLI (no stored secrets)
  - **Direct Mode**: Supply credentials directly via params
- **CSV-based destination management**: Process multiple SAP destinations from a CSV file
- **Automatic connection naming**: Connections are named `{ConnectionPrefix}-{DestinationName}`
- **Shared infrastructure**: Single DCE/DCR shared across all connections
- **Enforced DCE/DCR naming**: Names are derived from the Log Analytics workspace ID and validated, so they always match Azure portal deployed resources:
  - DCR: `Microsoft-Sentinel-SAPCC-DCR-<first 12 chars of workspace GUID>`
  - DCE: `ASI-<full workspace GUID>`

  The scripts abort with a clear error if a name (or a supplied DCE reference) violates this convention, because downstream processes depend on it.

## Files

| File | Description |
|------|-------------|
| `discover-destinations.ps1` | Discover BTP destinations using BTP CLI and export to CSV |
| `provision-sap-cpi-runtime.ps1` | Provision service instance and retrieve service key credentials |
| `connect-sentinel-to-integration-suite.ps1` | Main script - creates Sentinel connections from destinations.csv |
| `IntegrationSuiteHelpers.ps1` | Shared helper functions for Azure, DCR/DCE, CSV processing, and CF operations |
| `SAPCC_DCR.json` | Data Collection Rule template with SAP data streams |
| `destinations-sample.csv` | Sample CSV file showing expected destination format |
| [`AUDIT-LOG-SMOKE-TEST.md`](AUDIT-LOG-SMOKE-TEST.md) | Manual smoke test to validate the Security Audit Log RFC on the SAP backend before raising a support ticket |

## Architecture

### Script Execution Flow

**Cloud Foundry Mode:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    connect-sentinel-to-integration-suite.ps1                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Validate Azure CLI login                                                 │
│  2. Validate CF CLI login                                                    │
│  3. Call provision-sap-cpi-runtime.ps1 ──────────────────────────────────┐  │
│  4. Import destinations.csv                                               │  │
│  5. Create/Get DCE and DCR (shared)                                       │  │
│  6. Loop: Create connection for each destination                          │  │
└──────────────────────────────────────────────────────────────────────────┼──┘
                                                                           │
                                         ┌─────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     provision-sap-cpi-runtime.ps1                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Create service instance (if not exists)                                   │
│  • Create service key (if not exists)                                        │
│  • Retrieve and return credentials                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Direct Mode:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    connect-sentinel-to-integration-suite.ps1                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Validate Azure CLI login                                                 │
│  2. Use direct credentials (parameters or service key file)                  │
│  3. Import destinations.csv                                                  │
│  4. Create/Get DCE and DCR (shared)                                          │
│  5. Loop: Create connection for each destination                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Microsoft Sentinel                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │ Data Connectors │───▶│ DCE             │───▶│ Log Analytics Tables    │  │
│  │ (per destination)│    │ (Shared)        │    │ - ABAPAuditLog          │  │
│  │ SAP-Dest1       │    └────────┬────────┘    │ - ABAPChangeDocsLog     │  │
│  │ SAP-Dest2       │             │             │ - ABAPUserDetails       │  │
│  │ SAP-DestN       │             ▼             │ - ABAPAuthorizationDet. │  │
│  └────────┬────────┘     ┌───────────────┐     │ - SentinelHealth        │  │
│           │              │ SAPCC-DCR     │────▶└─────────────────────────┘  │
│           │              │ (Shared)      │                                   │
│           │              └───────────────┘                                   │
└───────────┼──────────────────────────────────────────────────────────────────┘
            │
            │ HTTPS (OAuth2) + rfcDestinationName header
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SAP Integration Suite                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ /http/microsoft/sentinel/sap-log-trigger                            │    │
│  │ (Integration Flow)                                                   │    │
│  └────────────────────────────────┬────────────────────────────────────┘    │
│                                   │ RFC (routed by destination header)       │
│                    ┌──────────────┼──────────────┐                           │
│                    ▼              ▼              ▼                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                             │
│  │ SAP ERP 1  │  │ SAP ERP 2  │  │ SAP S/4    │  (Multiple backends)        │
│  └────────────┘  └────────────┘  └────────────┘                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

### Azure Requirements (Required for all modes)

1. **Azure CLI** installed and authenticated
   - Install: https://learn.microsoft.com/cli/azure/install-azure-cli
   - Login: `az login`

2. **Azure Permissions**
   - Contributor role on the resource group (for DCE/DCR creation)
   - Microsoft Sentinel Contributor role (for data connector creation)

3. **Microsoft Sentinel Workspace**
   - Log Analytics workspace with Microsoft Sentinel enabled
   - Microsoft Sentinel Solution for SAP installed from Content Hub

### Cloud Foundry CLI Requirements (CF Mode only)

Required only when using **Cloud Foundry Mode** (runtime credential retrieval):

1. **Cloud Foundry CLI (cf)** installed
   - Download: https://docs.cloudfoundry.org/cf-cli/install-go-cli.html
   - Login: `cf login -a <cf-api-endpoint>`
   - Target org/space: `cf target -o <org> -s <space>`

2. **CF Permissions**
   - Service instance creation/read permissions
   - Service key creation/read permissions

### Direct Mode Prerequisites

For **Direct Mode** (credentials supplied via parameters), you need:
- OAuth Client ID and Secret from your SAP Integration Suite service
- Integration Server URL
- Token Endpoint URL (varies by environment - see examples below)

### SAP BTP CLI Requirements (optional - for destination discovery)

1. **SAP BTP CLI** installed
   - Download: https://tools.hana.ondemand.com/#cloud
   - Login: `btp login`

2. **BTP Permissions**
   - Read access to connectivity destinations in your subaccount

### SAP Integration Suite Requirements

1. **SAP Process Integration Runtime** service instance
   - Service plan: `integration-flow`
   - For CF Mode: Will be created automatically if not exists

2. **Integration Flow** deployed at:
   - Path: `/http/microsoft/sentinel/sap-log-trigger`
   - Or custom path specified via `-ApiPathSuffix` parameter

3. **RFC Destinations** configured
   - One destination per SAP backend system
   - Listed in destinations.csv

## Service Key / Credential Structures

### Cloud Foundry Environment (BTP Multi-Cloud)

The service key from SAP BTP "SAP Process Integration Runtime" service looks like this:

```json
{
  "oauth": {
    "clientid": "sb-xxx!b3750|it-rt-tenant!b18631",
    "clientsecret": "xxxxxx",
    "url": "https://tenant.it-cpi023-rt.cfapps.eu20-001.hana.ondemand.com",
    "tokenurl": "https://tenant.authentication.eu20.hana.ondemand.com/oauth/token"
  }
}
```

## Usage

### Cloud Foundry Mode (Recommended for BTP Multi-Cloud)

Use this mode when your Integration Suite is on SAP BTP Cloud Foundry environment:

```powershell
# Step 1: Login to Cloud Foundry (credentials retrieved at runtime)
cf login -a <cf-api-endpoint>
cf target -o <org> -s <space>

# Step 2: Login to Azure
az login --tenant "<microsoft-entra-tenant-id>"
az account set --subscription "<subscription-id>"

# Step 3: Create/edit destinations.csv (or use discover-destinations.ps1)
# Format: DestinationName;Type;LocationID;Authorization Type;ProxyType;Description;PollingFrequencyInMinutes

# Step 4: Run the connection script (CF Mode - no credential parameters)
.\connect-sentinel-to-integration-suite.ps1 `
    -SubscriptionId "<subscription-id>" `
    -ResourceGroupName "<resource-group>" `
    -WorkspaceName "<sentinel-workspace-name>" `
    -DestinationsCsvPath ".\destinations.csv"
```

This will:
1. Retrieve Integration Suite credentials from CF at runtime (no secrets stored)
2. Create/verify DCE and DCR in Azure
3. Create a Sentinel connection for each destination in the CSV

---

### Direct Mode (Manual Credentials)

Use this mode when you want to supply credentials directly:

```powershell
# Step 1: Login to Azure
az login --tenant "<microsoft-entra-tenant-id>"
az account set --subscription "<subscription-id>"

# Step 2: Prepare credentials (secure input)
$secret = Read-Host "Enter Secret" -AsSecureString

# Step 3: Run the connection script with direct credentials - Basic Auth
.\connect-sentinel-to-integration-suite.ps1 `
    -SubscriptionId "<subscription-id>" `
    -ResourceGroupName "<resource-group>" `
    -WorkspaceName "<sentinel-workspace-name>" `
    -DestinationsCsvPath ".\destinations.csv" `
    -IntegrationServerUrl "https://tenant.it-cpi023-rt.hana.ondemand.com" `
    -ClientId "your-username" `
    -ClientSecret $secret `
    -AuthType "Basic"
```

---

### Verifying the Connection

After running the script:
1. **Verify data ingestion** in Sentinel tables `SentinelHealth` and `ABAPAuditLog` after the polling interval.
2. (Optionally) verify Data Connector definition using the Azure REST APIs. [API Playground](https://portal.azure.com/?feature.customportal=false#view/Microsoft_Azure_Resources/ArmPlayground.ReactView) is a simple way using your portal login. [List your data connectors](https://learn.microsoft.com/rest/api/securityinsights/data-connectors/list?view=rest-securityinsights-2025-09-01&tabs=HTTP) using this request on the playground:

   ```http
   subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{workspaceName}/providers/Microsoft.SecurityInsights/dataConnectors?api-version=2025-09-01
   ```

---

### Changing an existing connection's tenant or endpoint

Plan an overlap when moving a connection to another SAP Integration Suite (CPI) tenant
or endpoint. Saving a registration is not proof that the collector has started using the
new settings.

In the service-telemetry investigation of four connection changes on 10 November 2026,
updates under the same destination name preserved the polling position: the requested
windows remained consecutive rather than restarting at the save time. However, cached
connection settings took about 40 minutes to change. Calls to the previous tenant initially
succeeded, then returned HTTP 401 after access there was withdrawn. Those failed windows
were discarded, leaving gaps even though the polling windows themselves were continuous.
This observed cache delay is not a guaranteed refresh interval.

The seven-day automatic retry mechanism still applies to eligible transient failures;
it does not recover windows discarded after HTTP 401. Do not rely on it to protect a tenant
change after old credentials or endpoints are disabled.

#### Preferred: A/B migration (make before break)

**A** is the existing working collection path; **B** is the replacement. Run both against
the intended SAP sources during validation, then retire A. Do not disconnect A first or
overwrite its registration and assume B inherits its polling position. A newly created
connection starts collecting at its own start time; it does not automatically load history
or inherit another connection's retry windows.

1. **Prepare and rehearse.** Coordinate with the SAP Basis, integration and SOC teams.
   Record A's connection identity, CPI tenant, destination and expected SAP
   `SystemId`/`ClientId` pairs, and the corresponding settings for B. Record UTC change
   times and agree on validation, rollback and duplicate-handling criteria. Rehearse in a
   non-production landscape and check that SAP and CPI can support the temporary extra
   polling load. Keep A's tenant, endpoint, destination and credentials working.
2. **Create B alongside A.** Create the destination in the new tenant under a **new
   destination name**, for example with a migration suffix, pointing to the intended SAP
   backend and client. Register B as an **additional Sentinel connection** with a distinct
   identity; do not overwrite A. With this tool, use a CSV containing only B's destination
   and supply B's tenant settings. Connections are named
   `{ConnectionPrefix}-{DestinationName}`; verify the resulting name differs from A's
   before running the script. Do not alter A's shared DCE/DCR or other working connections.
3. **Prove B is collecting correctly while A remains active.** Confirm sustained regular
   polling over multiple completed polling intervals, not just a successful save or
   connection test. Check `SentinelHealth` using B's actual `SentinelResourceName`, confirm
   requests and successful processing in B's CPI message monitor, and reconcile new
   `ABAPAuditLog` events for **every expected `SystemId`/`ClientId`** and `SystemUniqueId`
   where applicable against SAP source records. Validate the other configured data sources
   as well. A heartbeat, HTTP 200 or workspace-wide activity does not prove that the correct
   client's data arrived. Allow for ingestion latency; do not use 25-37 minutes, 40 minutes
   or any other fixed delay as a readiness test.
4. **Validate and move downstream analytics to B.** Identify the tables, parsers, analytics
   rules, workbooks and automation that consume A. Validate their expected results with B
   before switching their active source selection. Where both paths feed a parser or the
   same table, explicitly review overlap and source selection as described below; changing
   a connection registration alone does not move these consumers. Record the UTC analytics
   cutover and keep A available for rollback. If B fails validation, retain A as the active
   path and resolve B's configuration before proceeding.
5. **Retire A only after acceptance.** Once B's per-client coverage and downstream
   analytics have been accepted, remove only A's Sentinel connection, or stop A's collector
   if migrating from the container-based connector. Keep its old tenant and credentials
   available for at least one further hour, and longer if requests still reach it. An
   elapsed hour alone is not proof that the transition has completed. Do not remove shared
   infrastructure that B or another connection still uses.
6. **Reconcile and recover.** Compare coverage around B's start, the analytics cutover and
   A's final polling windows with SAP source records for each expected system/client.
   Investigate empty periods rather than assuming they are missing records. For confirmed
   gaps, obtain approval and use the [time-slice backfill tool](../TimeSliceBackfill/README.md)
   through the validated endpoint and destination, while the records are still retained
   in SAP. Follow its dry-run, safety-lag and load-protection guidance, then verify the
   recovered records. Continue monitoring B before decommissioning A's remaining resources.

This procedure aims to avoid a collection gap by maintaining overlap, but is not an atomic
handover or a guarantee of zero loss or exactly-once ingestion. Independent collection paths
do not share a handover cursor. If parallel operation is not possible, treat the change as
a planned interruption with source retention and approved backfill, not as a gap-free switch.

##### Handling overlap and duplicates in analytics

Temporary duplicate ingestion is expected when A and B read the same source interval.
The iFlow does not deduplicate these records. SAP parsers can include both legacy and
agentless sources, so disabling A does not immediately remove its already-ingested records
from query results.

Before the cutover, compare both paths over a bounded UTC interval and inspect duplicate
groups using a source-event identity validated against SAP. Do not treat all records with
the same timestamp, system and client as duplicates: distinct legitimate events can share
those values. There is no single guaranteed unique event ID for `ABAPAuditLog`; validate
any composite key against representative source events before using it for query-time
deduplication.

Use the source discriminator actually exposed by the relevant table or parser to validate
B separately. `SentinelResourceName` identifies the connection in `SentinelHealth`; do not
assume that it is also present on every SAP event table. For a container-to-agentless
migration, review the parser's source selection so historical A records do not continue to
double-count events. For two agentless connections whose events cannot be distinguished
in the destination table, use CPI processing evidence and SAP source records to establish
coverage; do not invent a per-connection event filter.

Agree on one active source or a validated deduplication strategy for each affected consumer,
including scheduled-rule lookback windows that cross the cutover. Check duplicate-sensitive
counts and alerts before retiring A. Query-time filtering or deduplication does not prevent
duplicate ingestion, delete stored rows or reverse ingestion charges.

#### If the destination name must stay the same

If possible, stage B under a temporary destination name and follow the A/B procedure above.
If the same registration must be updated in place, this is **not** an A/B migration. Keep
the old tenant and credentials valid while cached settings refresh. Record the save time
in UTC, then verify regular requests at the new endpoint and the expected per-client data
before retiring the old environment. Do not assume the seven-day retry mechanism will
recover a period during which no connection requested data, a successful response with
the wrong client's data, or discarded HTTP 401 windows.

If uninterrupted access to the old endpoint cannot be maintained, plan an approved backfill
using [`Invoke-SapAgentlessBackfill.ps1`](../TimeSliceBackfill/README.md) with the **new**
tenant's endpoint, credentials and destination. Use the interval from **five minutes before
to at least 60 minutes after the save** as an initial reconciliation range; extend it if
telemetry shows a later switchover or additional failed windows. This is a planning buffer,
not a guaranteed upper bound on the gap.

Wait until the selected end time is in the past by the script's safety lag (five minutes by
default) before requesting the full range. An immediate run clamps the end time and cannot
recover future windows; explicitly run any remaining interval later. Follow the backfill
README's dry-run, load-protection and source-retention guidance, inspect its results, and
verify recovered records against SAP. A successful response alone does not prove complete
recovery. Replaying already collected windows can create duplicates; query-time
deduplication does not delete stored rows or reverse ingestion charges.

> [!NOTE]
> In the investigated save flow, the built-in connection test also requested and ingested
> the preceding minute. Repeated saves can therefore create short duplicate intervals;
> they are not a substitute for validating sustained regular polling.

---

### Destination Discovery (discover-destinations.ps1)

Discover SAP BTP destinations configured for Microsoft Sentinel and export them to a CSV file.

```powershell
# Step 1: Login to SAP BTP
btp login

# Step 2: Discover destinations matching "Sentinel" pattern
.\discover-destinations.ps1 -SubaccountId "your-subaccount-guid"

# Custom filter pattern
.\discover-destinations.ps1 -SubaccountId "your-subaccount-guid" -NameFilter "MySAP"

# Custom output path
.\discover-destinations.ps1 -SubaccountId "your-subaccount-guid" -CsvPath ".\my-destinations.csv"

# Append to existing CSV instead of overwriting
.\discover-destinations.ps1 -SubaccountId "your-subaccount-guid" -AppendCsv
```

**discover-destinations.ps1 Parameters:**

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `SubaccountId` | Yes | - | SAP BTP Subaccount ID (GUID) |
| `NameFilter` | No | `Sentinel` | Filter pattern for destination names |
| `CsvPath` | No | `.\destinations.csv` | Path to export CSV file |
| `DefaultPollingFrequency` | No | `1` | Default polling frequency in minutes for discovered destinations |
| `AppendCsv` | No | `$false` | Append to existing CSV instead of overwriting |

---

### Destinations CSV Format

The destinations.csv file uses semicolon (`;`) as delimiter:

```csv
DestinationName;Type;LocationID;Authorization Type;ProxyType;Description;PollingFrequencyInMinutes
Sentinel_SAP_ERP_PROD;RFC;;CONFIGURED_USER;OnPremise;Production SAP ERP system;5
Sentinel_SAP_ERP_DEV;RFC;;CONFIGURED_USER;OnPremise;Development SAP ERP system;10
```

**Required columns:**
- `DestinationName` - Name of the RFC destination (used as `rfcDestinationName` header)

**Optional columns:**
- `PollingFrequencyInMinutes` - Polling interval (default: 5 minutes)
- `Type`, `LocationID`, `Authorization Type`, `ProxyType`, `Description` - For documentation only

---

### Service Instance Provisioning (provision-sap-cpi-runtime.ps1)

If you need to create the CPI service instance separately:

```powershell
# Login to Cloud Foundry
cf login -a <cf-api-endpoint>
cf target -o <org> -s <space>

# Provision service instance and key
.\provision-sap-cpi-runtime.ps1 `
    -InstanceName "cpi-sentinel-integration-rt" `
    -KeyName "cpi-sentinel-integration-key"
```

**provision-sap-cpi-runtime.ps1 Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `InstanceName` | `cpi-sentinel-integration-rt` | Name for the Process Integration Runtime service instance |
| `ServicePlan` | `integration-flow` | Service plan for Process Integration Runtime |
| `KeyName` | `cpi-sentinel-integration-key` | Name for the service key |

---

## Parameters

### connect-sentinel-to-integration-suite.ps1 Parameters

**Azure Configuration (Required):**
| Parameter | Description |
|-----------|-------------|
| `SubscriptionId` | Azure Subscription ID where Microsoft Sentinel is deployed |
| `ResourceGroupName` | Resource Group name containing the Sentinel workspace |
| `WorkspaceName` | Log Analytics workspace name with Sentinel enabled |

**Direct Mode (Credential Parameters - bypasses CF CLI):**
| Parameter | Description |
|-----------|-------------|
| `IntegrationServerUrl` | Integration Server URL (e.g., `https://tenant.it-cpi023-rt.hana.ondemand.com`) |
| `TokenEndpoint` | OAuth Token Endpoint URL (e.g., `https://oauthasservices-xxx.hana.ondemand.com/oauth2/api/v1/token`) |
| `ClientId` | OAuth Client ID |
| `ClientSecret` | OAuth Client Secret (SecureString) |
| `ServiceKeyPath` | Path to service key JSON file (alternative to individual credential parameters) |

> **Note**: If any Direct Mode credential parameter is provided, CF Mode is bypassed. You can use either individual parameters (`-IntegrationServerUrl`, `-TokenEndpoint`, `-ClientId`, `-ClientSecret`) or a service key file (`-ServiceKeyPath`).

**Destinations Configuration:**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `DestinationsCsvPath` | `.\destinations.csv` | Path to destinations CSV file |
| `ConnectionPrefix` | `SAP` | Prefix for connection names (connections named `{prefix}{DestinationName}`) |

**Integration Suite Service Instance:**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `InstanceName` | `cpi-sentinel-integration-rt` | CPI service instance name in Cloud Foundry |
| `KeyName` | `cpi-sentinel-integration-key` | Service key name for the CPI instance |

**Optional Parameters:**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `ApiPathSuffix` | `/microsoft/sentinel/sap-log-trigger` | API path suffix after `/http` |
| `ApiVersion` | `2025-07-01-preview` | Azure Management API version |

## Troubleshooting

### Common Issues

1. **CF CLI Not Logged In**
   - Run `cf login -a <cf-api-endpoint>`
   - Target your org/space: `cf target -o <org> -s <space>`
   - Verify with: `cf target`

2. **Azure CLI Authentication Failed**
   - Verify Azure CLI is logged in: `az account show`
   - Check subscription is set correctly: `az account set --subscription "<id>"`

3. **Connection Creation Failed**
   - Verify Microsoft Sentinel Solution for SAP is installed
   - Check Azure RBAC permissions
   - Ensure the workspace exists in the specified resource group

4. **DCE/DCR Creation Failed**
   - Verify Contributor permissions on the resource group
   - Check if DCE/DCR with same name already exists

5. **CSV File Issues**
   - Ensure CSV uses semicolon (`;`) as delimiter
   - Verify `DestinationName` column exists and has values
   - Check file encoding is UTF-8

6. **No Data in Tables**
   - Verify Integration Suite integration flow is deployed and active
   - Check RFC destination is correctly configured in BTP
   - Review SentinelHealth table for connector heartbeat

### Logs and Diagnostics

1. **Check connector health:**
   ```kusto
   SentinelHealth
   | where SentinelResourceName startswith "ApiPolling-SAP"
   | order by TimeGenerated desc
   | take 10;
   ```

2. **Check SAP audit logs:**
   ```kusto
   ABAPAuditLog
   | order by TimeGenerated desc
   | take 10
   ```

## Contributing

This project welcomes contributions and suggestions. See the [Contributing section](https://github.com/Azure/Azure-Sentinel?tab=readme-ov-file#contribution-guidelines) of this repository for reference.

## Related Documentation

- [Microsoft Sentinel Solution for SAP](https://learn.microsoft.com/azure/sentinel/sap/solution-overview)
- [SAP Integration Suite Documentation](https://help.sap.com/docs/integration-suite)
- [Data Collection Rules in Azure Monitor](https://learn.microsoft.com/azure/azure-monitor/essentials/data-collection-rule-overview)
- [Cloud Foundry CLI Documentation](https://docs.cloudfoundry.org/cf-cli/)
