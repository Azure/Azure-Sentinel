# PrancerConnectivityHealth_CL — table schema

Companion table for the `PrancerConnectivityHealthCheck` Azure Function
(`Data Connectors/PrancerConnectivityHealthCheck/`). Documents the minimal
schema a future implementer needs to provision the **separate** DCE/DCR this
table requires. This is deliberately a short schema note, not a Bicep/ARM
template — see "Why a separate DCR/DCE" below for the reasoning, and the
Function's `readme.md` for the customer-facing provisioning steps.

## Why this table is separate from `PrancerFindings_CL`

`PrancerFindings_CL` is fed by a DCR that depends on a specific role
assignment (`Monitoring Metrics Publisher` scoped to that DCR) and a specific
ingestion identity managed by Prancer's backend. The entire point of the
connectivity health check is to detect when *that* pipe breaks — a revoked
role assignment, a reconfigured workspace, a backend outage. Writing the
health-check's own status row through the same DCR/table would mean the
health signal disappears in exactly the scenario it exists to catch. A
second, minimal, independently-provisioned DCR/DCE — used only for this one
lightweight row per run — keeps the signal alive even when the findings
pipeline is fully down.

## Table: `PrancerConnectivityHealth_CL`

```json
[
  { "name": "TimeGenerated", "type": "datetime" },
  { "name": "CustomerId", "type": "string" },
  { "name": "WorkspaceId", "type": "string" },
  { "name": "LastFindingReceived", "type": "datetime" },
  { "name": "StalenessHours", "type": "real" },
  { "name": "IsHealthy", "type": "bool" }
]
```

| Column | Type | Description |
| --- | --- | --- |
| `TimeGenerated` | `datetime` | Timestamp of the health-check run itself (when the Function executed), in UTC. Standard Log Analytics ingestion-time column; the DCR should map it from the payload rather than relying on ingestion-time defaulting, so the row's own age is queryable independent of `LastFindingReceived`. |
| `CustomerId` | `string` | Optional Prancer-side customer identifier, mirrors the `CustomerId` column already present on `PrancerFindings_CL` (see `docs/sentinel/prancer-findings-native-table-schema.json`). May be empty if the deploying customer did not set the Function's `CUSTOMER_ID` app setting. |
| `WorkspaceId` | `string` | GUID of the Log Analytics workspace that was queried. Included so a single Function deployment's rows are unambiguous if a customer ever repoints it, and so a multi-tenant Sentinel deployment can filter per workspace. |
| `LastFindingReceived` | `datetime` | The `max(TimeGenerated)` value read from `PrancerFindings_CL` at check time. `null`/absent if the table had zero rows at check time (never ingested, or wiped) — the Function still writes a row in this case, with `IsHealthy = false`. |
| `StalenessHours` | `real` | `TimeGenerated - LastFindingReceived`, in hours, rounded to 2 decimal places. `null`/absent when `LastFindingReceived` is null. |
| `IsHealthy` | `bool` | `true` if `StalenessHours <= STALENESS_THRESHOLD_HOURS` (default 48h, configurable on the Function). `false` if stale, or if `PrancerFindings_CL` had no rows at all. |

## Minimal DCR/DCE to provision

This table needs its own Data Collection Endpoint (DCE) and Data Collection
Rule (DCR), separate from whatever DCR/DCE serves `PrancerFindings_CL`. At a
minimum the DCR needs:

- A `streamDeclarations` entry (suggested name: `Custom-PrancerConnectivityHealth_CL`)
  whose columns match the table above.
- A `dataFlows` entry with `transformKql: "source"` (no transformation
  needed — the Function's payload already matches the table shape) and
  `outputStream: "Custom-PrancerConnectivityHealth_CL_CL"` pointed at the
  target Log Analytics workspace.
- A **Monitoring Metrics Publisher** role assignment, scoped to this DCR,
  granted to the same App Registration (service principal) already used for
  `CLIENT_ID`/`CLIENT_SECRET` on the Function — the same identity can hold
  that role on both the findings DCR and this health DCR without issue;
  what matters is that the two DCRs themselves are separate resources, so a
  problem specific to the findings DCR (e.g. its role assignment being
  revoked) doesn't also revoke access to this one.

Once provisioned, the DCE's logs-ingestion endpoint and the DCR's
`immutableId` become the Function App's `HEALTH_DCE_ENDPOINT` and
`HEALTH_DCR_IMMUTABLE_ID` app settings (see
`Data Connectors/PrancerConnectivityHealthCheck/readme.md`).

## Suggested Sentinel analytic rule (not shipped in this pass)

With this table in place, a customer (or a future rule in this solution)
could alert on "no healthy check-in in N hours" independent of both the
webhook and `PrancerFindings_CL`, e.g.:

```kql
PrancerConnectivityHealth_CL
| summarize LastHealthyCheckIn = maxif(TimeGenerated, IsHealthy == true)
| extend HoursSinceLastHealthyCheckIn = datetime_diff('hour', now(), LastHealthyCheckIn)
| where isnull(LastHealthyCheckIn) or HoursSinceLastHealthyCheckIn > 12
```

Not added as a formal Analytic Rule YAML in this pass — left for a follow-up
once this table has live data to validate against, consistent with how other
content in this solution is only added after it's been confirmed against
real ingested rows.
