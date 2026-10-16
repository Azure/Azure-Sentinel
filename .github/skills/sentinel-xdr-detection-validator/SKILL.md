---
name: sentinel-xdr-detection-validator
description: Validate generated XDR Detection YAML structurally and validate source and converted KQL through official Microsoft Sentinel Triage MCP tools first, with direct API fallback.
---

# Validate XDR Detection YAML

Offline validation requires `contentProvenance.requiredWorkloads` records
(`workload`, `dataTypes`) and `contentProvenance.requiredDataConnectors` records
(`connectorId`, `dataTypes`). Missing fields, malformed/unknown workloads and
`dependencyReviewRequired: true` block validation. Use
`sentinel-xdr-dependency-helper` to review unresolved prerequisites against an
explicitly approved lab. Conversion never calls or requires Log Analytics.
Reviewed empty connector arrays are valid for native XDR-only content.

Live source validation requests `Prefer: include-dataSources=true`, retains
input metadata, and compares it with authored workload/connector declarations.
It uses API metadata for 1-10 distinct tables; successful missing metadata or
more than 10 tables falls back to the conservative scanner. Failed or partial
queries never become empty successful dependencies. Source connector
declarations are compared without inventing connectors from shared tables.
Authoring can use the helper's explicitly approved lab reads and offline
metadata import without enabling the Qualification-only SDK execution route.

Use the `sentinel-xdr-migration` CLI for deterministic planning, structural
validation, fallback execution, and reporting. Runtime query execution prefers:

- Microsoft Sentinel Triage MCP for every query operation supported by the
  connected server:
  `https://sentinel.microsoft.com/mcp/triage`.
- Native Azure Monitor Query SDK for complete original Sentinel-query
  execution after a Triage provider failure, or when the CLI path is explicitly
  selected.
- Log Analytics CLI/API results remain importable as a legacy original
  Sentinel-query fallback.
- Microsoft Graph Advanced Hunting through the CLI as the Advanced Hunting
  fallback.

## Provider fallback policy

Inspect the connected Triage MCP tools and use a suitable advertised tool
first. Do not invent a tool name or assume a capability. Fall back to the
corresponding direct provider only when Triage cannot act as a provider,
including:

- the MCP server or the required query tool is unavailable;
- authentication, consent, or permission fails;
- the request times out or the MCP service returns a transient/provider error;
- a provider failure prevents completion of the full solution batch.

Original Sentinel queries fall back to the Azure Monitor Query SDK (or imported
legacy Log Analytics CLI/API results). Advanced Hunting queries fall back to
Graph. Do not fall back when Triage successfully executes the
request and returns a real KQL semantic/runtime error. That is a detection
failure, not an MCP failure. Do not combine providers within one query-family
report; if Triage fails mid-batch, rerun that complete batch through its direct
provider.

Before any live query, confirm the exact persisted Log Analytics workspace
and/or Defender tenant, and verify the required read permissions for that
provider. Never choose another workspace to recover from a failure. Do not
launch authentication without first asking. Structural validation, runtime
execution, schema binding, and qualification are separate outcomes; a provider
fallback or successful query never marks a rule validated or proves parity.

For partial publication, do not weaken this rule-level evidence contract.
`package-selection-plan` counts only unique, current source IDs represented by
eligible deployable Custom Detections against the complete original Sentinel
rule inventory; the partial threshold is strictly over 50%. Qualification may
use only the fresh applied selected subset and must keep excluded item failures
visible. Never relabel a partial selected-query result as full-inventory
Validation or Qualification.

## Workflow

1. Run `sentinel-xdr-migration doctor`.
2. On first run, run `sentinel-xdr-migration setup --non-interactive`.
3. Ask before launching interactive authentication. Never block offline conversion.
4. Run:

   ```powershell
   sentinel-xdr-migration validate --solution "<solution-path>"
   ```

5. Stop if structural errors remain. Each detection requires its own top-level
   `version` (`major.minor.patch`) in `[3.1.0, 4.0.0)`, separate from
   `schemaVersion: 1.0.0`. Source Sentinel `1.x` versions remain valid provenance
   and must not be promoted to satisfy this check. For older files without the
   XDR version, report the reconversion guidance rather than changing provenance
   or accepting Data/solution version fallbacks.
6. Generate the complete runtime plan:

   ```powershell
   sentinel-xdr-migration validation-plan --solution "<solution-path>"
   ```

   Use advertised official Triage MCP tools first for every supported
   `sentinelQuery` and `advancedHuntingQuery`. For Advanced Hunting, invoke
   `RunAdvancedHuntingQuery`.    If the connected MCP does not advertise a suitable original Sentinel
   workspace-query tool, either run the toolkit's native SDK provider for the
   full family or use the legacy Log Analytics CLI/API import path without
   treating that capability gap as a KQL failure.

   The native source-query runner requires an existing Qualification run and
   its locked target. It verifies the active Azure CLI tenant and subscription
   without signing in, sends each exact persisted source KQL string directly to
   `LogsQueryClient.query_workspace(timespan=None)`, and records full returned
   schemas and rows in the ignored run-local SDK report:

   ```powershell
   sentinel-xdr-migration validate-sentinel-sdk `
     --solution "<solution-path>" `
     --run-id "<qualification-run-id>"
   ```

   Defaults bound each request to 90 seconds and the complete source family to
   30 minutes, with at most two transient retries per query. The complete
   recursive source inventory must map one-to-one to current generated
   detections. Authentication, authorization, query, transport and partial
   result failures are retained distinctly. Zero returned rows indicate query
   execution only, not parity.

   Normalize Advanced Hunting results into a JSON file containing exactly one
   entry per detection and the returned target-query output `schema` array when
   custom details are present. Copy `querySha256` from the matching
   `advancedHuntingQuerySha256` in the runtime plan; it must hash the exact KQL
   sent to the provider:

   ```json
   {
     "results": [
       {
         "detection": "Example.yaml",
         "status": "passed",
         "statusCode": 200,
         "rowCount": 0,
         "querySha256": "<exact advancedHuntingQuery SHA-256 from validation-plan>",
         "schema": [{"Name": "DeviceId"}, {"Name": "Timestamp"}],
         "error": null
       }
     ]
   }
   ```

   Allowed statuses are `passed`, `failed`, and `blocked`. Then record the
   provider results:

   ```powershell
   sentinel-xdr-migration record-runtime-validation `
     --solution "<solution-path>" `
     --provider triage-mcp `
     --results "<normalized-results.json>"
   ```

7. If Triage cannot complete an entire query family for a provider-level
   reason, create a run-local `provider-gap-<family>.json` recording the
   advertised tool name (or `unavailable`), exact target reference, one
   approved reason code (`tool-unavailable`, `authentication`, `authorization`,
   `timeout`, `transient-provider-error`, or `batch-provider-failure`), a
   concise reason, `batchComplete: true`, `scopeVerified: true`,
   `permissionsVerified: true`, and `kqlError: false`. Do not use a gap record
   for a real KQL error. The CLI rejects incomplete, cross-family, wrong-provider,
   or unscoped fallback evidence.

   For original Sentinel queries, rerun that **complete family** against the
   exact locked workspace. Prefer the native SDK command above; pass the
   run-local provider-gap evidence if Triage failed:

   ```powershell
   sentinel-xdr-migration validate-sentinel-sdk `
     --solution "<solution-path>" `
     --run-id "<qualification-run-id>" `
     --provider-gap-evidence "<run-local-provider-gap-sentinel.json>"
   ```

   For externally imported provider results, normalize one result per
   detection and include `querySha256` from that rule's
   `sentinelQuerySha256` plan entry, then record it with the gap evidence:

   ```powershell
   sentinel-xdr-migration record-runtime-validation `
     --solution "<solution-path>" `
     --provider log-analytics-cli `
     --results "<complete-sentinel-results.json>" `
     --provider-gap-evidence "<run-local-provider-gap-sentinel.json>"
   ```

   If and only if Triage has an Advanced Hunting provider-level failure, run
   the complete Advanced Hunting batch through Graph with the same kind of
   run-local evidence:

   ```powershell
   sentinel-xdr-migration validate-advanced-hunting `
     --solution "<solution-path>" `
     --provider-gap-evidence "<run-local-provider-gap-advanced-hunting.json>"
   ```

8. Runtime providers create JSON and self-contained HTML reports under
   `Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>`. Treat `blocked` as an
   environment gap, not a conversion failure.
9. For every rule:
   - execute the original `sentinelQuery`;
   - execute the `advancedHuntingQuery`;
   - record whether each query binds and executes;
   - compare returned entity columns when representative rows exist.
   Imported `passed` Sentinel results without a matching `querySha256` are
   blocked. Graph results bind automatically to the exact Advanced Hunting
   query executed by the validator. A query rewrite invalidates old evidence;
   rerun the complete Sentinel and Advanced Hunting families for the current
   artifact before the workflow can pass runtime validation.
10. Zero rows are not proof of behavioral parity. Record them as execution
   success with data validation still pending. A table probe that executes and
   returns zero rows proves the table binds on that query surface.
11. Do not change `contentProvenance.conversion.status` to `validated` unless
   both queries execute and the entity output has been reviewed.

## Query-surface isolation

Defender Advanced Hunting and Sentinel Log Analytics are separate query
surfaces even when the Defender portal shows a selected Sentinel workspace.
A table name resolving in Advanced Hunting does not prove that the same name
resolves through the Log Analytics workspace API, and vice versa.

- Probe the original `sentinelQuery` only against the exact persisted
  Log Analytics workspace.
- Probe the converted `advancedHuntingQuery` only through Defender Advanced
  Hunting.
- Never use workspace table-management inventory as query-availability proof.
- Never scan other workspaces after the workflow workspace is selected.
- Report the surface explicitly, for example:
  `IdentityInfo unavailable through log-analytics-workspace; available through
  defender-advanced-hunting`.
- Do not say a table is unavailable "in every accessible workspace" unless the
  user explicitly requested a multi-workspace audit.

For an **Authoring** profile, an environment-only runtime block does not prevent
V3.1 packaging when structural validation passed. Complete validation as passed
with `runtimeStatus=environment-blocked` only when no current exact-query
KQL/runtime failure exists, preserve the provider error and query surface, and
do not claim the detection is runtime-qualified. For a
**Qualification** profile, the same runtime block remains blocking until the
selected lab environment satisfies the required query surfaces.

Return a per-rule result and an overall pass/needs-review summary.

Best-effort entity-mapping assumptions recorded by conversion do not prevent
read-only Sentinel/Advanced Hunting execution or output-schema binding tests.
Run and report those tests against the exact hash-bound queries, retaining the
assumption as pending human review. A successful query or custom-detail schema
binding is not approval, entity correlation, or alert parity. Keep technical
failures and other unresolved review findings blocking as applicable; do not
package or deploy while an entity-mapping review remains pending.

For unresolved table/schema or conversion assumptions, use provider-owned
evidence: standard-table and schema documentation, live query schema from the
selected provider, or the custom connector's DCR/table metadata. Do not
substitute customer research or invent a schema. Present each proposed
assumption with its exact scope, source/query hash, evidence, and `accept` or
`reject` choice; no decision is automatic. Accepted assumptions still require
reconversion and the normal structural/runtime checks. If content hashes change,
re-review rather than reusing an earlier decision.
