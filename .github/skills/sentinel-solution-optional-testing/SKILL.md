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

## Safety contract

- Never treat workspace discovery as write approval.
- Never generate or deploy a Custom Detection as part of mock-data ingestion.
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
  --stream "<Custom-StreamName_CL>" `
  --discover-only `
  --login
```

This first read-only discovery also runs the target-specific permission
preflight. It verifies:

- a read-only Log Analytics query against the selected workspace;
- effective DCR access for `Microsoft.Insights/Telemetry/Write`.

The preflight writes no telemetry and does not grant write approval. If Azure
does not allow effective DCR permissions to be inspected, report ingestion
permission as `unknown` rather than treating it as granted.

The tool uses Azure CLI authentication. It selects workspaces in this order:

1. explicit `--workspace`;
2. `AZURE_SENTINEL_WORKSPACE_ID`;
3. `LA_WORKSPACE_ID`;
4. the first accessible workspace, sorted by name, in the active Azure
   subscription.

Tell the user which workspace was selected and list any alternatives returned
by the tool. Ask whether they want a different workspace before any write.
Accept a workspace name, customer ID, or full ARM resource ID. Require a full
ARM resource ID when a name or customer ID is ambiguous.

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
    malicious.json
    benign.json
    scenario.json
```

`scenario.json` must record the source rule, converted Custom Detection,
source and destination tables, stream when applicable, hypothesis, malicious
and benign record counts, decisive fields, locked correlation paths,
limitations, and separate validation status. Reject the fixture if schema
validation is not `passed`, either record count is zero, or the scenario lacks
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
   ask the user for the folder containing `malicious.json`, `benign.json`, and
   `scenario.json`, then retry with `--mock-data-folder "<folder>"`.

Do not silently search unrelated directories or select another rule's fixture.

Before requesting approval:

1. Read `scenario.json`, the source analytic rule, and connector DCR transform.
2. Confirm the solution, rule ID, rule name, stream, and output stream agree.
3. Verify every raw fixture field and value conforms to the selected input stream.
4. Verify transform-derived fields, parser mappings, timestamps, and correlation
   keys.
5. Verify the malicious fixture is expected to match and the benign fixture is
   expected not to match.
6. Treat seeded Sentinel/AH harness results only as logical query evidence; they
   do not prove live visibility or alert parity.
7. Do not auto-ingest single-row heuristic fixtures for joins, thresholds,
   aggregates, historical baselines, watchlists, anomaly logic, or
   absence-of-data rules. Build a purpose-specific scenario or mark the runtime
   test unsupported.
8. Require `generationStatus=qualification-ready`,
   `validation.schemaValidation=passed`, and
   `ingestion.directLogsIngestionSupported=true`.

## Approval and ingestion

Show the exact tenant, subscription, workspace, workspace resource ID, DCR,
stream, payload path, record count, affected table, rule, and cleanup plan.
Obtain explicit user approval for that exact scope.

Only after approval, run:

```powershell
python Tools\SolutionMigration\ingest_to_dcr.py `
  --workspace "<workspace-name-customer-id-or-arm-id>" `
  --stream "<Custom-StreamName_CL>" `
  --solution "<solution-folder>" `
  --rule-id "<rule-id>" `
  --fixture malicious `
  --approve-write
```

Do not pass `--approve-write` before the user approves.

When the default fixture is not present, use the folder supplied by the user:

```powershell
python Tools\SolutionMigration\ingest_to_dcr.py `
  --workspace "<workspace-name-customer-id-or-arm-id>" `
  --stream "<Custom-StreamName_CL>" `
  --solution "<solution-folder>" `
  --rule-id "<rule-id>" `
  --fixture malicious `
  --mock-data-folder "<folder-containing-the-fixtures>" `
  --approve-write
```

## Validation

After Azure accepts the payload:

1. Wait for ingestion visibility and query the destination table for unique
   fixture identifiers.
2. Run the exact analytic-rule KQL over the intended time window.
3. Run the benign case separately.
4. Record expected and observed row counts, timestamps, entities, and errors.
5. If alert validation was approved, verify alert creation separately.
6. Perform and verify the stated cleanup.

Store evidence under the migration run's versioned `Reports` directory. Mark
results as `accepted`, `visible`, `query-matched`, and `alert-created`
independently; never collapse them into a single success status.

`Solutions\<solution>\XDR Detections\` contains detection-shaped YAML files
only. Write scenario manifests, migration state, DCR discovery, ingestion
receipts, query results, parity captures, cleanup evidence, JSON, and HTML
artifacts under:

```text
Reports\<solution>\<version>\<run-id>\
```
