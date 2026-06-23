# Data Ingestion Guide

## ⚠️ PREREQUISITE: Data Lake Must Be Active

**Before starting ANY data ingestion work, validate that the data lake is onboarded and active.**

Run the data lake validation script (tenant-wide; classifies Onboarded / Stale / NotOnboarded):
```powershell
./scripts/Validate-DataLake.ps1
```

> **Do NOT** rely on a single-RG `az resource list ... Microsoft.SentinelPlatformServices/sentinelplatformservices` check. That resource persists after offboarding and its linked workspace can be deleted/stale while `provisioningState=Succeeded`. The validator above combines a tenant-wide platform scan with per-workspace `Microsoft.SecurityInsights/onboardingStates/default` verification.

**If data lake is NOT active** → Do not proceed. Guide user through data lake onboarding first (see `data-lake-onboarding-guide.md`).

---

## Overview

This guide covers data ingestion approaches for the Sentinel data lake. ISVs need to understand both production and lab approaches:

| Approach | When to Use | Mechanism |
|----------|-------------|-----------|
| **Data Connector (Production)** | ISV product streaming data to customer's Sentinel | CCF Pull/Push connectors via Connector Builder Agent |
| **DCE/DCR + Logs Ingestion API (Lab / Phase 3)** | Populate correlated sample data for an agent use case | Per-table DCE + DCR; orchestrator POSTs JSON records (see Phase 3 section) |
| **KQL Jobs (Deprecated)** | _Historical reference only — moved to `legacy/`_ | See `legacy/README.md` |
| **Summary Rules** | Aggregate high-volume verbose logs | Scheduled aggregation into Analytics tier |

> **Connector type drives Phase 3 routing.** Before applying any guidance below, read `connectorType` from `config/progress.json` (set in Phase 0):
> - **`custom-table`** → ISV ships its own `*_CL` table → use the DCE/DCR/`_CL` flow in this guide.
> - **`native-cef-syslog`** → ISV ingests into a shared native table (`CommonSecurityLog`, `Syslog`, `SecurityEvent`, etc.) → see "Native-table ingestion" section below — **do NOT create DCE/DCR or a custom table**.
> - **`native-builtin`** → first-party platform data (SigninLogs, SecurityAlert, etc.) → no ingestion infrastructure needed.

---

## Production Approach: Data Connectors

ISVs follow this path for production data ingestion:

1. **Develop a Data Connector** using one of:
   - [Sentinel Connector Builder Agent](https://learn.microsoft.com/en-us/azure/sentinel/create-custom-connector-builder-agent) — AI-assisted in VS Code with GitHub Copilot (reduces weeks → hours)
   - [Codeless Connector Framework (CCF)](https://learn.microsoft.com/en-us/azure/sentinel/create-codeless-connector) — For pull-based data sources
   - [CCF Push](https://learn.microsoft.com/en-us/azure/sentinel/create-push-codeless-connector) — For push-based data sources

2. **Ingest Data to Data Lake** — Stream telemetry through the connector

3. **Leverage Sentinel Platform** — Data exploration, Graph, MCP server, Security Copilot Agents

**Alternative:** If a connector already exists, refer to the [Sentinel Data Connectors Reference](https://learn.microsoft.com/en-us/azure/sentinel/data-connectors-reference) to enable it.

### Validating DCR / Logs Ingestion API Pipeline

After running `Ingest-SampleData.ps1` (or any production POST to the DCE), **always validate that data actually landed in the destination `_CL` table**. The agent must run this check before declaring Phase 3 complete or moving the user to Phase 4.

> **Latency:** DCR-ingested data takes 5-10 minutes to appear. Wait at least 10 minutes after the last POST before validating.

Run the validation script:

```powershell
./scripts/Validate-Ingestion.ps1 `
    -SubscriptionId "<sub-id>" `
    -ResourceGroupName "<rg>" `
    -WorkspaceName "<workspace>" `
    -Tables @("<YourTable>_CL") `
    -LookbackHours 24
```

Or run the equivalent KQL directly in Log Analytics:

```kql
<YourTable>_CL
| where TimeGenerated > ago(24h)
| summarize Rows=count(), Latest=max(TimeGenerated)
```

**If 0 rows after 10+ minutes:** the agent must investigate — common causes are DCR transform dropping rows, schema mismatch between `streamDeclaration` and target table, missing `Monitoring Metrics Publisher` role on the DCR for the sending identity, or wrong stream name (must be `Custom-<name>` matching DCR).

---

## Native-table ingestion (CEF / Syslog / Built-in)

**Use this path when `connectorType` is `native-cef-syslog` or `native-builtin`.**

CEF/Syslog connectors (Silverfort, Cisco, Palo Alto, Fortinet, Check Point, etc.) and many built-in vendor connectors do **not** ship their own table. Their rows land in a Sentinel-native shared table — `CommonSecurityLog`, `Syslog`, `SecurityEvent`, `WindowsEvent`, etc. — and are filtered to a specific vendor by columns such as `DeviceVendor` / `DeviceProduct` (CEF) or `ProcessName` / `Computer` (Syslog).

### What to skip
- ❌ **Do not** create a `*_CL` custom table (`az monitor log-analytics workspace table create`)
- ❌ **Do not** create a DCE
- ❌ **Do not** create a custom DCR or assign `Monitoring Metrics Publisher`
- ❌ **Do not** invent column names — the schema is fixed by the platform

### What to do
1. **Fetch the destination native table's official schema** from `https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/<TableName>` (e.g., `tables/commonsecuritylog`, `tables/syslog`, `tables/securityevent`). Save to `config/ingestion-schemas.json`.
2. **Author one DCR + Logs Ingestion API stream per source table** (Phase 3 pipeline) that POSTs rows into the native table. Use the same `streamDeclarations` + `dataFlows` shape documented in the Phase 3 section. Per row, set:
   - **Vendor identity columns** — copy from `config/isv-schema.json.vendorFilters` (e.g., `DeviceVendor="<ISV Vendor Name>"`, `DeviceProduct="<ISV Product Name>"`). Every row must satisfy the same `where` clause the ISV's analytic rules use, otherwise the agent's KQL will not return your sample rows.
   - **Detection-signal columns** — copy from `config/isv-schema.json.detectionSignals` and ensure each scenario in the use-case brief has at least one matching row (e.g., `DeviceEventClassID="NewIncident"` AND `Message` contains each enum value the analytic rules look for). If the rules `parse_json` the `Message`, build a real JSON string in `Message`.
   - **Standard columns** — populate `TimeGenerated` (within `ago(7d)`), `SourceIP`, `DestinationIP`, `DeviceAction`, etc., respecting the official schema's types and enums.
3. **Correlate across native correlation tables** — reuse the same UPN / hostname / IP across `CommonSecurityLog` (or your destination), `SigninLogs`, `IdentityInfo`, `SecurityAlert`, `DeviceEvents`, etc., so the agent's cross-table joins succeed.

### Validation (Branch B/C)

```kql
<NativeTable>
| where TimeGenerated > ago(24h)
| where DeviceVendor == "<vendor>" and DeviceProduct == "<product>"
| summarize Rows=count(), Latest=max(TimeGenerated)
```

Then run **one of the agent's per-scenario detection KQL queries** to confirm at least one row matches each scenario:

```kql
<NativeTable>
| where TimeGenerated > ago(7d)
| where DeviceVendor == "<vendor>" and DeviceProduct == "<product>"
| where DeviceEventClassID == "NewIncident" and Message has "<ScenarioEnum>"
| count
```

**If 0 rows but the table has data:** check vendor-filter columns — most common cause is `DeviceVendor`/`DeviceProduct` set to a different casing or string than the analytic rules expect. **If 0 rows total:** the Logs Ingestion POST failed (re-run `Invoke-AttackScenarioIngestion.ps1` with `-Verbose` and inspect HTTP responses) or the destination table is in a tier that rejects writes from the ingest identity.

`scripts/Validate-Ingestion.ps1` accepts native table names — pass `-Tables @("CommonSecurityLog")` (no `_CL` suffix) and the script will run a row count + sample preview against the workspace.

---

## Phase 3 Sample Data: DCE/DCR + Logs Ingestion API

> **Heads-up:** the previous KQL-Jobs-based lab approach has been **deprecated** and
> moved to `legacy/kql-jobs/` + `legacy/scripts/`. Phase 3 sample-data work now uses
> the per-table **Data Collection Endpoint (DCE) + Data Collection Rule (DCR) + Logs
> Ingestion API** pipeline documented in this section.

### Why we switched

| KQL Jobs (deprecated) | DCE/DCR + Logs Ingestion API (current) |
|---|---|
| Portal-only `POST /jobs` API; no ARM/Bicep/Terraform | First-class ARM + REST surface |
| `datatable()` literals with strict canonical shape | JSON record arrays; native types |
| `_KQL_CL` / `_KQL` suffix forced on destination | Native + custom `_CL` tables, full control |
| 15-min results latency, async job runs | ~5-10 min ingestion latency, synchronous POST |
| Sample-data only; no analytics-rule parity | Identical pipeline to production ISV connectors |

### Architecture

```
scenarios/<scenario>.json     ┐
config/entities.json          │  Invoke-AttackScenarioIngestion.ps1
schemas/<Table>.json          │  └─ generate correlated records
config/use-case-brief.md      │     and call ↓
config/isv-schema.json        ┘
                              Invoke-SampleDataIngestion.ps1
                              ├─ deploy DCE (1x)
                              ├─ deploy DCR per table (Nx)
                              ├─ create *_CL tables (Nx)
                              ├─ AAD token (resource https://monitor.azure.com)
                              └─ POST {DCE}/dataCollectionRules/{id}/streams/Custom-<Table>
                                                ↓
                                Log Analytics workspace
                                (Analytics tier `_CL` tables)
                                                ↓
                                Validate-Ingestion.ps1 -ScenarioPath ...
                                ├─ per-table row count
                                └─ per-scenario kqlAssertion (count >= expectedMinHits)
```

### Phase 3 entrypoints

| Script | Role |
|---|---|
| `scripts/Invoke-AttackScenarioIngestion.ps1` | Orchestrator. Reads scenario JSON, synthesises correlated records, calls the engine per table. |
| `scripts/Invoke-SampleDataIngestion.ps1` | Engine. Deploys DCE/DCR/tables (idempotent), acquires AAD token, POSTs records. |
| `scripts/Validate-Ingestion.ps1 -ScenarioPath <path>` | Validator. Runs per-table row counts + every `scenarioCoverage[]` KQL assertion; exits non-zero on any miss. |
| `scripts/Package-Agent.ps1` | Packager. Applies the conditional `_CL` rename (see below) when building the agent bundle. |

### Conditional `_CL` rename rule (MANDATORY at package time)

Phase 3 deliberately writes sample data into `_CL` table names — including for
**native-mirror tables** whose schemas are 1:1 with canonical 1P tables documented on
`learn.microsoft.com`. These exist in `_CL` form only during lab/dev; their canonical
production name has no `_CL`. The packager rewrites them at publish time so the
shipped manifest references the production names.

`scripts/Package-Agent.ps1` consumes a **native-mirror rename list** (a constant in
the script). For this Phase 3 baseline the list contains `SigninLogs_CL`,
`SecurityAlert_CL`, `DeviceLogonEvents_CL`, but it is extensible — any table
classified as a 1P native via the rule below may be added to it.

**All other `_CL` tables are genuine custom tables** (delivered by a Sentinel Solution
/ data connector, or defined locally in `config/isv-schema.json`). `_CL` is part of
their permanent production name and is **preserved verbatim** through packaging.

**Table classification rule** (apply per table before adding to or removing from the
native-mirror rename list):

1. **Check `https://github.com/Azure/Azure-Sentinel/tree/master/Solutions` first.** If
   the table is referenced from any Solution's `Data Connectors/`, `Parsers/`,
   `Workbooks/`, or `Analytic Rules/`, the table is **custom `_CL`** — do **not**
   add it to the native-mirror rename list. `_CL` stays.
2. **Else, check `https://learn.microsoft.com/azure/azure-monitor/reference/tables/<name>`.**
   If the page describes a Microsoft 1P service writing to the table via diagnostic
   settings or a built-in pipeline (Entra ID, Defender for Identity, Defender for
   Endpoint, Defender for Cloud, Activity Logs, etc.) and the table is not also
   defined under `Azure/Azure-Sentinel/Solutions`, the table is **1P native** — add
   it to the native-mirror rename list so `_CL` is stripped at package time.
3. **If still ambiguous, default to custom `_CL`** and leave it off the rename list.

Cite the exact Solution path or Learn URL when justifying any addition to the
native-mirror rename list.

`scripts/Package-Agent.ps1` performs both the rename and a validator:
1. **Rename:** whole-word regex `\b<RenameListName>_CL\b` → `<RenameListName>` across the bundled instructions/KQL, for every name on the native-mirror rename list.
2. **Validator (a):** assert zero residual occurrences of any name on the rename list.
3. **Validator (b):** assert every `_CL` name in the source that is **not** on the rename list still exists, unchanged, in the packaged output.

The packager exits non-zero on either validator failure — this is the safety net that
prevents accidental table-name corruption when promoting to production.

### Native-table source-of-truth schemas

| Table | Schema URL | Ingestion-time DCR? |
|---|---|---|
| SigninLogs | <https://learn.microsoft.com/azure/azure-monitor/reference/tables/signinlogs> | Yes |
| SecurityAlert | <https://learn.microsoft.com/azure/azure-monitor/reference/tables/securityalert> | Yes |
| DeviceLogonEvents | <https://learn.microsoft.com/azure/azure-monitor/reference/tables/devicelogonevents> | Yes |

Mirror columns 1:1 (name + Azure Monitor type) so the Phase 6 promotion is a pure
table-name rename, not a schema port.

### Scenario JSON contract

`scenarios/<scenario>.json` is the orchestrator's input. Required top-level keys:

| Key | Purpose |
|---|---|
| `tables[]` | Table list with per-table record counts and timing windows |
| `correlationRules` | UPN / PathId / CorrelationId / DeviceName fan-out rules |
| `scenarioCoverage[]` | One entry per detection scenario: `id`, `name`, `tables[]`, `kqlAssertion`, `expectedMinHits` |
| `extensions[]` | Developer-prompt-driven deltas (`extend_scenario` verb) |

The validator's pass/fail decision is driven entirely by `scenarioCoverage[]`.

### PowerShell `ConvertTo-Json` array-unwrap quirk (document, do not "fix")

`ConvertTo-Json -Depth 5` collapses single-element arrays into scalars:

```powershell
@('T1003.006') | ConvertTo-Json   # → "T1003.006"   (scalar)
@('T1003.006','T1078') | ConvertTo-Json   # → ["T1003.006","T1078"]   (array)
```

Sentinel `dynamic` columns accept **both** scalar and array forms — KQL queries that
use `has`, `has_any`, or `mv-expand` work in either case. **Do not** add `-AsArray`
hacks or post-process the JSON. Authors of scenario JSON should be aware that any
single-tactic entry will arrive as a string; multi-tactic entries as an array.

### Latency, idempotency, and re-runs

- **DCR immutableId propagation:** 30-60s after deploy; the engine retries POST until 204.
- **Ingestion latency to `_CL` table:** 5-10 minutes typical.
- **Idempotency:** all three deploys (DCE, DCR, table) are idempotent — re-running the
  orchestrator only adds new records; it never destroys or duplicates infrastructure.
- **Re-running with the same scenario file:** appends another N records each time.
  To get a clean baseline, drop the `_CL` tables (`az monitor log-analytics workspace
  table delete --name <Table>_CL`) and re-run.

### Validation workflow (Phase 3 sign-off)

```bash
# 1. Verify all 10 tables landed rows
pwsh ./scripts/Validate-Ingestion.ps1 \
    -SubscriptionId <subscription-id-guid> \
    -ResourceGroupName <resource-group> \
    -WorkspaceName <workspace-name>

# 2. Verify all 7 detection scenarios meet expectedMinHits
pwsh ./scripts/Validate-Ingestion.ps1 \
    -SubscriptionId <subscription-id-guid> \
    -ResourceGroupName <resource-group> \
    -WorkspaceName <workspace-name> \
    -ScenarioPath scenarios/tier0-attacker-investigation.json
```

Phase 3 only flips to `ingestion_complete` after step 2 exits 0.

---

## Summary Rules: High-Frequency Aggregation

### When to Use

- Aggregate **high-volume verbose logs** (network, firewall, identity)
- Create **precompiled data** for dashboards
- **Cost savings** by summarizing expensive analytics-tier data
- Results stored in **Analytics tier** custom tables

### Creating Summary Rules

**Via Portal:**
1. Navigate to **Microsoft Sentinel** → **Configuration** → **Summary rules**
2. Define KQL aggregation query
3. Set scheduling (frequency, delay)
4. Results auto-write to custom analytics table

**Via ARM Template:**
```json
{
  "type": "Microsoft.OperationalInsights/workspaces/providers/alertRules",
  "properties": {
    "query": "CommonSecurityLog | summarize count() by DeviceVendor, bin(TimeGenerated, 1h)",
    "destinationTable": "NetworkSummary_CL",
    "queryFrequency": "PT1H",
    "queryPeriod": "PT1H"
  }
}
```

---

## Decision Guide

```
┌───────────────────────────────────────────────────────────────────┐
│ Is this PRODUCTION data from ISV product?                         │
│   YES → Build Data Connector (CCF Pull/Push or Connector Builder)│
│   NO ↓                                                            │
├───────────────────────────────────────────────────────────────────┤
│ Need to populate sample/test data for an agent use case (lab)?    │
│   YES → Use the Phase 3 DCE/DCR + Logs Ingestion API pipeline    │
│         (Invoke-AttackScenarioIngestion.ps1)                     │
│   NO ↓                                                            │
├───────────────────────────────────────────────────────────────────┤
│ Need high-frequency aggregation of verbose logs?                  │
│   YES → Use Summary Rules                                        │
│   NO  → Stop — re-evaluate whether ingestion is required.         │
└───────────────────────────────────────────────────────────────────┘
```

---

## References

- [Logs Ingestion API in Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview)
- [Data Collection Endpoints (DCE)](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/data-collection-endpoint-overview)
- [Data Collection Rules (DCR) structure](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/data-collection-rule-structure)
- [Send data with the Logs Ingestion API (tutorial)](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tutorial-logs-ingestion-api)
- [SigninLogs table reference](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs)
- [SecurityAlert table reference](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/securityalert)
- [DeviceLogonEvents table reference](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/devicelogonevents)
- [Sentinel Connector Builder Agent](https://learn.microsoft.com/en-us/azure/sentinel/create-custom-connector-builder-agent)
- [Codeless Connector Framework](https://learn.microsoft.com/en-us/azure/sentinel/create-codeless-connector)
- [Summary Rules](https://learn.microsoft.com/en-us/azure/sentinel/summary-rules)
- [Data Lake Service Limits](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-lake-service-limits)
- _Deprecated:_ [KQL Jobs in Data Lake](https://learn.microsoft.com/en-us/azure/sentinel/datalake/kql-jobs) — see `legacy/README.md`
