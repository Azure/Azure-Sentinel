---
name: sentinel-solution-optional-testing
description: Optionally qualify Microsoft Sentinel solution content by discovering an Azure workspace, ingesting reviewed mock data through an installed DCR, validating telemetry and rule behavior, and preserving evidence. Use only when the user requests live testing or qualification.
version: 1.0.0
allowed-tools: Bash, Read, Grep, Glob
---

# Sentinel Solution Optional Testing

Use this skill only for optional live qualification. Authoring, packaging, and
static validation must remain available when Azure access or write permissions
are unavailable.

Before entering this skill, the migration Agent must run the existing toolkit
startup readiness flow:

```powershell
sentinel-xdr-migration doctor
```

On first use or when authentication is incomplete, it must run
`sentinel-xdr-migration setup` and then retry `doctor`. This keeps `az login`,
Sentinel authentication, and Advanced Hunting authentication at the beginning
of the migration without changing the original runtime-validation flow.

After the Qualification target is locked and before Discovery, make one
complete advance-consent request for the anticipated bounded qualification
plan. If it has not happened yet, do so before fixture review or this skill's
live preflight. Reuse persisted consent when target and plan identity remain
unchanged; do not repeat the same broad question later.

The target-specific DCR permission preflight in this skill runs at the
beginning of the optional testing extension, before fixture generation or
ingestion. This preflight is required for the ingestion permission/resource
checks, not as a separate gate to determine whether an AR or CD already
exists. Its exact-ID Graph reads are currently bundled into the same CLI
preflight and cannot be skipped independently; a denied/unknown result remains
a backend limitation until that check is separated. Do not ignore a blocked
preflight to proceed; making that bundled check optional requires a maintainer
change to the backend.

## Workspace identity contract

Read `workflow-status` and the generated `qualification-target.json` before
preflight. The locked context contains tenant ID, subscription ID, workspace
ARM resource ID, and workspace customer ID:

- treat all four identifiers as authoritative for the entire run;
- pass the target artifact through `--target-context` to every
  optional-testing command;
- never run `az monitor log-analytics workspace list`, Resource Graph workspace
  discovery, table scans across workspaces, or primary-workspace inference;
- fail closed if the authenticated tenant or subscription differs;
- verify the resolved customer ID still matches; and
- return no workspace alternatives.

This skill must never resolve or rediscover a workspace. When the exact ARM
path fails, return control to the orchestrator. Only the centralized
`qualification-diagnose` command may perform one exact customer-ID lookup
restricted to the locked subscription.

If an Azure or MCP request reports a tenant mismatch, treat it as an
authentication-context failure for the selected workspace. Ask to
reauthenticate to the correct tenant and retry the same workspace. Do not look
for another workspace. If the stored workspace is inaccessible or deleted,
present **Retry authentication**, **Select another workspace**, **Continue
offline**, and **Cancel**; discover alternatives only after the user explicitly
selects **Select another workspace**.

## Advance scope planning and consent

Use the single advance request made after target lock and before Discovery.
Before fixture review or any environment-write step, expose and refresh the
Qualification scope plan for the explicitly selected run; ask for renewed
advance consent only if the target, plan identity, action/resource families,
payload, caps, package flags, or cleanup ownership changed:

```powershell
sentinel-xdr-migration plan-deployment `
  --solution "Solutions\<solution>" `
  --run-id "<run-id>"
```

This deterministic local command does not authenticate or call Azure. Review
the `deploymentPlanning` metadata from `preflight-deployment` or the persisted
`deployment-scope-plan.json`: exact locked tenant/subscription/resource group/
workspace/solution/version, recursive source inventory and eligible
additional-CD upper bound, exclusions, package and content hashes, resource
types, caps, ingestion details, and conditional component choices. The
solution `.env` is only read through the target configuration resolver; it is
not credentials or consent, cannot retarget a locked run, and is excluded
from source/package fingerprints. Supply `--run-id` whenever multiple runs
exist; never choose the latest run implicitly.

When a component has sufficient exact evidence, persist explicit planning
consent using `review-deployment-plan`, the current `--expected-plan-sha256`,
an explicit `--actor`, and the complete selected component set. Planning
consent is bound to the exact plan and target. It is not permission, technical
readiness, deployment evidence, or write approval. Missing, declined,
unknown, or stale consent remains unapproved; changed target/content/package
hashes, payload, resource family, flags, or count caps require renewed consent.
Do not hand-edit workflow state to simulate acceptance. Consent denial or
absence does not block independent read-only checks or offline work.

The early request must show all seven potential action groups, even when some
are conditional or currently unsupported:

1. disabled Sentinel AR and Graph CD creation/approved updates, with exact
   source IDs, current drafts, pair counts, and caps;
2. conditional fallback DCR/DCE creation, bound to the destination contract
   and proven absence of a compatible solution DCR;
3. conditional exact custom-log table creation only when its table is proven
   absent;
4. mock telemetry ingestion with payload, records/batches, stream, marker,
   schema hashes, estimated bytes/cost, and retention impact;
5. controlled parity with exact pairs, a bounded time window, enable/restore
   counts, and completion/abort recovery;
6. current full-package installation and selected XDR registration flags; and
7. explicitly owned cleanup/deletion with exact ownership evidence, resource
   list, cap, and exclusions.

Present **Approve the broadest currently bounded and available scope** as the
preselected suggested action, with **Select components**, **Revise the plan**,
and **Decline advance consent** also available. The preselection is not
approval. Before submission, show every selected component, cap, target,
resource family, and package flag/value. Require affirmative submission or
confirmation of that exact display; a preselected choice without submission,
cancel/close, decline, or absent response must record no consent. Users may
narrow, revise, or decline.

Suggest only currently supported components whose complete scope is bound to
the plan. If available, this may select the disabled Sentinel-AR/Graph-CD pair
and the distinct later `fullPackageAcceptance` component. Show all package
selection flags individually with their exact values; when a plan exposes five
valid flags and the broad proposal sets them all true, display each named flag
as `true`. Never infer or invent package flags. Unknown/provisional ingestion,
DCR/DCE, table creation, parity, or cleanup remains excluded unless that
component is itself fully bounded, supported, and explicitly displayed.
Where the broadest set cannot be fully bound, suggest only the largest valid
bounded subset and identify every unavailable/excluded action group and why.

Only the exact affirmative submission may be persisted, after checking all
components and flag values against the current plan. Prior DCR/DCE consent
does not approve ingestion, parity enablement, package installation, or
cleanup.

Disabled Sentinel alert rules and Graph Custom Detections are an explicit
pair-first component with an approved upper-bound cap. Full-package
installation and any selected XDR installation/Content Hub registration are
separate later component(s), requiring a current verified package and explicit
values for all available package flags. Stored playbook, workbook, connector,
API, or connection definitions do not approve their live instantiation or
enablement.

Mock-ingestion planning is a separate component. Do not approve it while the
reviewed run-bound payload/route is incomplete or unknown. The complete scope
identifies destination/table and stream, payload hash and record count,
batching limits, cost and retention impact, contract/schema/transform hashes,
marker and timestamp fields, and one shared payload ingested once per AR/CD
pair; benign controls remain separate. DCR/DCE support ingestion of locally
generated mock data, not mock generation. A DCR fallback is conditional on no
compatible existing solution DCR being proven; the current resolver checks
registered exact resource names only and does not discover arbitrary
solution-owned DCRs. DCE consent is separate and requires explicit selection
or evidence it is required by the route. Custom-table creation is conditional
only when the exact contract proves a custom-log table absent and supplies its
schema/path/column count. An incompatible existing table must not be altered.
A compatible native destination such as `CommonSecurityLog` makes table
creation not needed; never create a custom lookalike.

The current planner can persist advance consent for disabled AR/CD pairs,
package acceptance, mock-ingestion, fallback DCR/DCE, and custom-table
creation only when exact evidence and conditions are satisfied.
`controlledAlertParity` is provisional until a finite test window and complete
batch fixture plan are bound; the current CLI cannot persist parity consent.
`ownedResourceCleanup` is unsupported because there is no exact run-owned
deletion inventory or deletion executor. Do not invent consent component
names or claim those scopes are approved.

Provisioning DCR/DCE resources, creating a table, ingesting data, deploying
rules/packages, enablement, cleanup/deletion, retention changes, and role or
identity changes remain distinct operation scopes. Obtain explicit final
approval immediately before each bounded write operation or batch. Show all
exact resources/actions and counts in that batch; one approval may cover its
enumerated API requests and need not be repeated per HTTP call. Ask again if
the batch expands. Unknown permission is not granted. Authentication, Entra
admin consent, roles, and permissions are not resource-write approval.

## Safety contract

- Never treat workspace discovery as write approval.
- Never generate or deploy a Custom Detection as part of mock-data ingestion.
- Use exactly one rule-specific `mock.json` for both the source Analytic Rule
  and converted Custom Detection.
- Ingest that shared payload once. Separate AR and CD payloads are prohibited.
- Group compatible `mock.json` payloads by source table and supported ingestion
  path for one-time batch execution; never create a recurring ingestion job.
- Never ingest a heuristic payload merely because it matches the stream schema.
- Require a documented detection hypothesis and reviewed malicious and benign
  fixtures for the exact rule.
- A successful ingestion response proves only that Azure accepted the records.
  It does not prove table visibility, query matching, alert creation, or parity.
- Block only this optional qualification stage when access is unavailable.

## Tool

Run from the Azure-Sentinel repository root:

```powershell
python Tools\SolutionMigration\ingest_to_dcr.py `
  --target-context "Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\qualification-target.json" `
  --stream "<Custom-StreamName_CL>" `
  --solution "<solution-name-or-folder>" `
  --discover-only `
  --login
```

This first read-only discovery also runs the target-specific permission
preflight. It verifies:

- a read-only Log Analytics query against the selected workspace;
- effective DCR access for `Microsoft.Insights/Telemetry/Write`;
- existence and packaged-schema compatibility of the DCR destination custom
  table; and
- when that table is absent, effective workspace permission for
  `Microsoft.OperationalInsights/workspaces/tables/write`.

The preflight writes no telemetry and does not grant write approval. If Azure
does not allow effective DCR permissions to be inspected, report ingestion
permission as `unknown` rather than treating it as granted.

During Qualification, `--target-context` is mandatory. It disables workspace
selection and verifies the active Azure tenant, subscription, workspace ARM
ID, and customer ID before DCR inspection.

## Prerequisites

Report missing requirements with the exact blocked capability:

- Azure CLI authentication: run `az login`.
- Workspace and DCR discovery: Azure Resource Graph read access.
- Logs ingestion: `Microsoft.Insights/Telemetry/Write`, commonly granted by
  `Monitoring Metrics Publisher` on the DCR.
- Runtime query validation: workspace query permission, commonly granted by
  `Log Analytics Reader`.

Common roles are examples, not requirements; equivalent custom roles are valid.
After displaying the preflight results, present these user actions:

1. **Continue** — when all required checks are ready, proceed to fixture review
   and the separate exact-scope write-approval step. When a check is blocked or
   unknown, continue only in offline mode and skip live ingestion.
2. **Retry permission check** — rerun the same `--discover-only` command after
   the user changes authentication, role assignments, workspace, or DCR.
3. **Cancel** — stop optional testing without affecting conversion or static
   validation.

When the only recoverable blocker is a missing custom table, and the solution
package defines the exact table schema, add a fourth action:

4. **Deploy missing table and retry** — show the exact tenant, subscription,
   workspace resource ID, table name, packaged schema path, column count, table
   plan, and required permission. Explain that table creation changes the
   workspace and may cause ingestion and retention charges. Obtain explicit
   approval for this exact workspace and table, then run:

   ```powershell
   python Tools\SolutionMigration\ingest_to_dcr.py `
     --target-context "Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\qualification-target.json" `
     --stream "<Custom-StreamName_CL>" `
     --solution "<solution-name-or-folder>" `
     --deploy-missing-table `
     --approve-table-write
   ```

The command may create only a table confirmed absent by the immediately
preceding preflight. It must use the schema from the packaged solution, wait
for provisioning, verify the resulting schema, and rerun the complete
preflight. It must not update an existing table, repair schema differences,
deploy a DCR or DCE, or ingest data. Table approval is separate from
`--approve-write`. The table is a persistent workspace prerequisite and is not
automatically deleted during mock-data cleanup.

Use structured user elicitation so the actions render as selectable buttons
when the host supports it. Otherwise present the same three choices as a
numbered list and wait for the user's selection.

Never interpret **Continue** as `--approve-write`. Write approval is requested
later, after the exact payload and cleanup plan are shown.

## Fixture review

The optional-testing skill does not invent fixtures during ingestion. It first
checks for a reviewed fixture, then invokes
`sentinel-solution-mock-data-generation` when the fixture is absent. The
generation skill uses public neutral table structures under:

```text
Sample Data\Tables\<TableName>\
    base-event.json
    metadata.json
```

The base event is not malicious and must never be edited for one rule. Copy it
into a rule-specific working scenario, then use both the source Analytic Rule
and converted Custom Detection to determine the decisive predicates,
correlation keys, joins, thresholds, time relationships, projected entities,
and platform-specific field mappings.

The checked-in base catalog is produced by a one-time maintenance utility.
This runtime flow does not invoke CAT.Tools and does not regenerate the
complete Standard-table catalog.

When generating a rule-specific scenario:

1. Identify every source table used by the Analytic Rule and every destination
   table used by the Custom Detection.
2. Load each source table's `base-event.json` and `metadata.json`.
3. Copy the base record; never alter the checked-in table file.
4. Set malicious values that satisfy the documented behavior and both query
   forms.
5. Set a benign negative control that differs on a decisive predicate.
6. Preserve correlation keys across related records and generate the required
   event count for joins, thresholds, sequences, and aggregation.
7. Refresh timestamps to the intended test window.
8. Validate all values against `metadata.json`.
9. If a required table, column, mapping, or defensible negative control is
   missing, stop and mark the scenario `manual-review-required`.

Use these sources, in order:

1. the selected rule under `Solutions\<solution>\Analytic Rules\` or
   `Solutions\<solution>\Analytics Rules\`;
2. the installed connector's DCR `streamDeclarations`, `dataFlows`, and
   `transformKql`;
3. the solution parser and custom-table schema;
4. representative sample data already supplied by the solution, when present;
5. vendor-documented event examples, only after verifying them against the
   repository's current stream contract.

The default ingestion fixture location is:

```text
Sample Data\Solutions\Mock\<solution>\<rule-id>\
    mock.json
    scenario.json
```

`scenario.json` must record the source rule, converted Custom Detection,
source and destination tables, stream when applicable, hypothesis, shared mock
record count, benign validation-control count, decisive fields, locked correlation paths,
limitations, and separate validation status. Reject the fixture if schema
validation is not `passed`, the mock record count is zero, or the scenario lacks
a defensible negative control.

First try the default folder. If the requested fixture is absent:

1. Tell the user the exact path that was checked.
2. Invoke `sentinel-solution-mock-data-generation` with the exact solution,
   Analytic Rule, and converted Custom Detection.
3. If safe automatic generation succeeds, review the generated
   `scenario.json` and continue.
4. If generation reports `manual-review-required` or `unsupported-payload`,
   request a reviewed multi-event scenario or stop the live stage.
5. Only when the fixture is maintained outside the default repository path,
   ask the user for the folder containing `mock.json` and
   `scenario.json`, then retry with `--mock-data-folder "<folder>"`.

Do not silently search unrelated directories or select another rule's fixture.

## Automatic agent mode

When invoked by XDR Solution Manager, this skill owns the complete testing
extension. A user request such as “test this AR and CD” is sufficient. Do not
ask the user to run commands or provide paths already present in the solution,
scenario manifest, qualification target, or generated contract.

Before fixture preparation, retain the complete recursive source-rule
inventory for accounting and build a no-write plan for the current approved
Qualification scope. For a partial package, the currently applied
evidence-based package-selection plan is authoritative: plan fixtures and
ingestion only for its selected, validated AR/CD pairs. Do not let excluded
rule failures block selected-subset progress, but preserve their identities
and reasons as excluded evidence and never claim full-inventory qualification.
Use the exact plan hash reported by `workflow-status`:

```powershell
python Tools\SolutionMigration\resolve_ingestion_contracts.py `
  --solution "Solutions\<solution>" `
  --target-context "Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\qualification-target.json" `
  --selection-plan "Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\package-selection-plan.json" `
  --expected-selection-plan-sha256 "<current-applied-plan-sha256>" `
  --output "Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\<version>\ingestion-contract-plan.json"
```

The selected plan must be freshly applied, run-bound, and meet the canonical
strictly-over-50% validated migrated-detection threshold. The planner still
accounts for the full original inventory, marks unselected rules as
not-selected, and records the exact selection-plan hash and scope. It groups
only identical registered table schema/transform contracts and preserves each
selected AR/CD source file and query hash. Unknown or multi-table lineage and
complex scenarios remain blocked for review; the plan neither generates
fixtures nor calls Azure. Before requesting any ingestion approval, rerun it
with the reviewed inventory, target, and selection-plan hashes and a new
`--output` filename so the reviewed plan is preserved. Stop if it returns
`stale-plan`. Then use the
no-write `azure-monitor-logs-ingestion resolve --check-existing` for each
registered table group required by the selected fixtures in the same locked
workspace, recording one report per table. Do not treat either plan as write
approval. A complete package follows the existing full valid inventory path.

### DCR preference and permission preflight

The intended selection policy is solution-first: prefer a DCR explicitly
listed or referenced by the solution only when its deployed identity in the
locked workspace and its public input stream, fixture fields, transform,
destination table/schema, endpoint, and permissions are proven compatible
with the exact shared payload. A packaged ARM reference alone does not prove
that the DCR is deployed. Do not confuse its internal identifier with the
public `Custom-*` input stream or enumerate other workspaces.

If no solution-listed DCR is suitable, a supported registered contract may
produce a separate, isolated DCR configuration authored locally and
provisioned only in the approved non-production target. For Logs Ingestion
API fallback, structured input must use a customer-authored `Custom-*` stream
and `transformKql` to map to a supported `Microsoft-*` output stream. Public
table schema, including the anonymous
[`/v1/metadata` endpoint](https://api.loganalytics.io/v1/metadata), does not
reveal a connector's internal parser/enrichment or by itself prove ingestion
capability; check the documented table feature/capability route and never
assume reserved/service-managed columns are writable. A DCE is required for
private-link ingestion or when the DCR has no ingestion endpoint. The current
contract tool may use an isolated DCE/DCR pair by design, but that does not
make DCE a universal API requirement. “Locally” means locally authored
configuration, not a local ingestion service. Never modify an existing
connector DCR or add a stream to force compatibility. A native table without
a supported ingestion contract must use a documented native telemetry
generator or remain blocked; never redirect its rule to a custom lookalike
table.

**Implementation status:** The current no-write resolver is contract-specific:
it checks registered table contracts against resource candidates in the locked
workspace, but does not discover or prefer DCRs referenced by the solution.
Its `compatible-existing` result proves only the reported contract
compatibility, not that a solution-listed DCR was selected. Treat the
solution-first preference as planned until that integration is present, and
report only resource identities and checks actually established.

Before requesting fixture or ingestion approval, show separate results for
telemetry-write, DCR creation, conditional DCE creation, and conditional
destination-table creation permissions. Check DCE creation only when the
selected route includes a DCE. This no-write diagnostic does not provision
resources or authorize a write. An `unknown` or pending-review permission is
not granted. A missing write permission blocks that write only; continue
independent read-only workspace, DCR, schema, and query checks.

The preflight requires no fixture. Pass `--run-id` when the solution has
multiple runs; omit it only when the run is unique.

```powershell
sentinel-xdr-migration preflight-deployment `
  --solution "Solutions\<solution>" `
  --auth-method azure-cli `
  --run-id "<run-id>"
```

It adds `dcrPermissionPreflight` to the top-level Graph report and writes
`qualification-dcr-preflight.json` under the selected run's
`Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\` directory. The
subreport includes `status`, `workspaceQueryPermission`, and per-contract
`resourceReadAccess`, `tableSchemaCompatibility`, `ingestionAuthorization`,
`resourceProvisioningAuthorization`, `tableCreationAuthorization`,
`reportPath`, `targetFingerprint`, `schemaFingerprint`, and
`transformFingerprint`, `contractFingerprint`, `resourceFingerprint`,
`candidateProvenance`, and `candidateSelection`. `contractFingerprint` is the
SHA-256 of the registered serialized contract. `resourceFingerprint` hashes
the exact target workspace, candidate DCE/DCR/table IDs, returned resource
configuration/schema, and current resource states. Provenance is
`registered-contract-resolver`, and candidate selection is
`exact-contract-resource-names-only`.
`resourceProvisioningAuthorization` distinguishes
`dcrWrite` and `dceWrite` at the exact resource-group scope; DCE write is
checked only when the missing-pair plan includes DCE provisioning.

Per-capability authorization statuses are `ready`, `denied`, `unknown`,
`not-yet-verifiable`, or `not-needed`; table schema status is `compatible`,
`blocked`, or `unknown`; workspace query permission is `ready`, `denied`,
`unknown`, or `not-checked`; aggregate report status is `ready`,
`action-required`, `blocked`, `unknown`, or `not-applicable`.
`resourceReadAccess` is `ready`, `denied`, `unknown`, or `unavailable`
(including HTTP 401); `targetVerification` is `blocked`, `unavailable`,
`confirmed`, or `not-checked`. A `ready` permission only means the effective
permission pattern was inspected, not upload acceptance, table visibility, or
query matching. Keep each status distinct and do not convert unknown or
pending review into permission.

For each selected pair:

1. Resolve the exact source AR and converted CD.
2. Reuse or generate the one shared rule-specific mock.
3. Read `scenario.ingestion.contract` when present.
4. Apply the locked workspace ARM ID with the ingestion tool's `--workspace`
   override. Never write the workspace into the checked-in contract.
5. Resolve the registered table using the no-write command above. Verify
   whether the compatible resource is the solution-listed DCR; do not infer
   that association from the contract resolver alone. If provisioning is
   needed, after separate exact-scope approval provision or reuse the isolated
   contract-specific DCE/DCR used by the current tool route, ingest once, and
   verify visibility. Do not interpret this implementation choice as a
   universal DCE requirement.
6. Execute both exact queries and require non-zero semantic row parity scoped
   to the current fixture timestamps and unique values.
7. Start alert parity only after row parity passes.
8. Persist evidence and perform cleanup without requiring the user to assemble
   intermediate files.

Reviewed Standard-table contracts currently registered under
`Tools\AzureMonitorLogsIngestion\registry.yaml` are eligible for a
no-write resolution plan. Tables without a registered contract remain offline
or native-telemetry blocked. The registry requires a reviewed transform and
documented Logs Ingestion API route; table presence in the public metadata
catalog alone does not prove writable support.

Before any standard-table provisioning or ingestion, resolve the exact
registered table against the locked workspace and inspect only its
contract-specific resource candidates:

```powershell
azure-monitor-logs-ingestion resolve `
  --table "<scenario.sourceTable>" `
  --workspace "<locked-workspace-arm-id>" `
  --check-existing `
  --report "Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\<version>\ingestion-resolution.json"
```

This command is read-only. Continue only when its output is either
`compatible-existing` or `provisioning-plan`, and review its schema and
transform fingerprints, target workspace, and references alongside
`scenario.ingestion.contractResolution`. Keep the report with the run
artifacts. A mismatch, partial DCE/DCR pair, or missing/incompatible
destination table blocks the live stage pending review. A provisioning plan is
not write approval. Obtain the existing exact-scope approval before invoking
`run`; the resolver never creates resources.

Before requesting approval:

1. Read `scenario.json`, the source analytic rule, and connector DCR transform.
2. Confirm the solution, rule ID, rule name, stream, and output stream agree.
3. Verify every raw fixture field and value conforms to the selected input stream.
4. Verify transform-derived fields, parser mappings, timestamps, and correlation
   keys.
5. Verify the shared mock payload is expected to match both the AR and CD, and
   verify the non-ingested benign validation control is expected not to match.
6. Treat seeded Sentinel/AH harness results only as logical query evidence; they
   do not prove live visibility or alert parity.
7. Do not auto-ingest single-row heuristic fixtures for joins, thresholds,
   aggregates, historical baselines, watchlists, anomaly logic, or
   absence-of-data rules. Build a purpose-specific scenario or mark the runtime
   test unsupported.
8. Require `generationStatus=qualification-ready`,
   `validation.schemaValidation=passed`, and
   `ingestion.directLogsIngestionSupported=true`.
9. Before enabling either rule, prove that the exact AR and CD queries return
   the same uniquely marked rows from the single shared ingestion.
10. When a native table does not support synthetic Logs Ingestion, use only a
    documented native telemetry generator. Never copy the records to a custom
    lookalike table because the deployed AR/CD queries would not read it.

## Approval and ingestion

Show the exact tenant, subscription, workspace, workspace resource ID, DCR,
stream, payload path, record count, affected table, rule, and cleanup plan.
Obtain explicit user approval for that exact scope.

Only after approval, run:

```powershell
python Tools\SolutionMigration\ingest_to_dcr.py `
  --target-context "Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\qualification-target.json" `
  --stream "<Custom-StreamName_CL>" `
  --solution "<solution-folder>" `
  --rule-id "<rule-id>" `
  --approve-write
```

For a generated registered Standard-table contract, provision and ingest with:

```powershell
azure-monitor-logs-ingestion run `
  --contract "<scenario-folder>\ingestion-contract.yaml" `
  --workspace "<locked-workspace-arm-id>" `
  --payload "<scenario-folder>\mock.json" `
  --report "<versioned-report-path>"
```

The `--workspace` value must come from `qualification-target.json`.

Do not pass `--approve-write` before the user approves.
Do not infer or request hidden service-side KQL transformations from the Log
Analytics query SDK: it executes queries, while the DCR's customer-visible
`transformKql` is validated as exact ARM resource configuration.

When the default fixture is not present, use the folder supplied by the user:

```powershell
python Tools\SolutionMigration\ingest_to_dcr.py `
  --target-context "Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\qualification-target.json" `
  --stream "<Custom-StreamName_CL>" `
  --solution "<solution-folder>" `
  --rule-id "<rule-id>" `
  --mock-data-folder "<folder-containing-the-fixtures>" `
  --approve-write
```

## Validation

After Azure accepts the payload:

1. Wait for ingestion visibility and query the destination table for unique
   fixture identifiers.
2. Run the exact analytic-rule KQL over the intended time window.
3. Run the benign validation control separately without treating it as another
   live ingestion payload.
4. Record expected and observed row counts, timestamps, entities, and errors.
5. If alert validation was approved, verify alert creation separately.
6. Perform and verify the stated cleanup.

Store evidence under the solution's ignored migration `Logs` directory. Mark
results as `accepted`, `visible`, `query-matched`, and `alert-created`
independently; never collapse them into a single success status.

`Solutions\<solution>\XDR Detections\` contains detection-shaped YAML files
only. Write scenario manifests, migration state, DCR discovery, ingestion
receipts, query results, parity captures, cleanup evidence, JSON, and HTML
artifacts under:

```text
Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\<version>\
```
