---
name: sentinel-solution-mock-data-generation
description: Generate or reuse one shared mock.json payload for a Microsoft Sentinel Analytic Rule and its converted Defender XDR Custom Detection. Uses only Azure-Sentinel repository content and never writes to Azure.
version: 1.0.0
allowed-tools: Bash, Read, Grep, Glob
---

# Sentinel Solution Mock Data Generation

Use this skill when a migration or optional-testing workflow needs mock data
for a specific Analytic Rule and converted Custom Detection.

## Safety contract

- Read source rules and toolkit contracts without modifying them.
- Write only under the explicit `--output-root`, or under this toolkit
  repository's default mock root when no output root is supplied. Cross-worktree
  generation must always use `--output-root`.
- Never write fixture files into a source checkout implicitly.
- Never invoke CAT.Tools at runtime.
- Check for an existing reviewed scenario before generating a new one.
- Never overwrite an existing scenario unless the user explicitly requests
  regeneration and the prior fixture has been reviewed.
- Never infer a multi-event attack only because a schema permits it.
- Automatically generate only simple, decisive predicates.
- Require a reviewed scenario for joins, sequences, aggregation, thresholds,
  watchlists, external data, historical baselines, anomaly logic, and
  absence-of-data rules.
- Generate synthetic data only. Never copy customer or tenant telemetry.
- Never ingest, deploy, enable, or delete Azure resources.

## Inputs

Require:

1. solution folder name;
2. exact Analytic Rule name, ID, filename, or path;
3. the converted Custom Detection in
   `Solutions\<solution>\XDR Detections\`, or its exact path.

The generator uses:

- source Analytic Rule YAML;
- converted Custom Detection YAML;
- `Sample Data\Tables\<Table>\base-event.json`;
- `Sample Data\Tables\<Table>\metadata.json`;
- solution `Package\mainTemplate.json`;
- solution parsers;
- DCR `streamDeclarations`, `dataFlows`, `transformKql`, and output stream.
- the reviewed standard-table capability registry at
  `Tools\AzureMonitorLogsIngestion\registry.yaml` for writable standard-table
  routes, schemas, and transforms.

For separate checkouts, pass `--source-root` for the repository containing the
solution and `--toolkit-root` for the repository containing this generator and
its registry. The toolkit's `Sample Data` is used by default; pass
`--sample-data-root` only when the neutral table samples live elsewhere.
Absolute AR/CD paths are resolved and checked to remain inside `--source-root`.
Output and table paths reject symlink escapes; the resolved source, toolkit,
sample-data, and output roots are printed in the result and recorded in the
scenario manifest.

## Existing-scenario-first flow

Check:

```text
<output-root>\<solution>\<rule-id>\  (defaults to toolkit Sample Data\Solutions\Mock)
    mock.json
    scenario.json
```

Run:

```powershell
python Tools\SolutionMigration\generate_mock_scenario.py `
  --solution "<solution-folder>" `
  --rule "<rule-id-or-exact-name>" `
  --custom-detection "Solutions\<solution>\XDR Detections\<detection>.yaml" `
  --source-root "<Azure-Sentinel-repository>" `
  --toolkit-root "<repository-containing-this-generator>" `
  --output-root "<Azure-Sentinel-repository>\Sample Data\Solutions\Mock"
```

Without `--force`, a complete scenario that passed schema validation is
returned with `status=existing-scenario`. Reuse it after reviewing that its AR,
CD, stream, and hypothesis still match the current content.
The final output location is `<output-root>\<solution>\<rule-id>\`; the tool
does not silently fall back to a source-root-relative destination.

## Automatic generation

For a simple rule, the tool:

1. reads the AR and CD;
2. extracts decisive source predicates;
3. inspects the solution package and parser;
4. reverse-maps fields through parser and DCR transforms when a declared
   `Custom-*` input stream exists;
5. otherwise resolves the exact source table through the capability registry,
   checks source fields against the registered input/output schema, and starts
   from the checked-in Standard-table base event;
6. creates records that satisfy the decisive predicate;
7. creates a type-safe benign negative control for validation only;
8. validates every field against the DCR or table metadata;
9. writes the qualifying records to one shared `mock.json` payload.

The registry only supports explicit reviewed capabilities. Field extraction
matches exact identifiers already present in a known table schema; it is not a
general KQL parser. Unknown/ambiguous tables, unregistered fields, or unresolved
mapping produce a blocked/offline scenario instead of a guessed contract.
Registry schema and transform fingerprints identify the exact template used.
`liveValidated=false` means the contract still needs exact-workspace validation;
generation never claims that the live table/DCR accepts it.

Optional deterministic controls:

```powershell
python Tools\SolutionMigration\generate_mock_scenario.py `
  --solution "<solution>" `
  --rule "<rule>" `
  --custom-detection "<path>" `
  --randomize --copies 3 --seed 42 `
  --lock "requestId=campaign-1" `
  --benign-set "action=read"
```

## Provisional candidate inputs

An unreviewed candidate is not a reviewed scenario. Pass it with
`--candidate-scenario`; this transports and type-checks the rows but does not
assert human acceptance or semantic query validation. Candidate input always
yields `generationStatus=generated-offline-only`, including simple rules, so it
cannot pass the direct-ingestion gate. The API result uses
`status=generated-candidate` (or `existing-candidate` on reuse). The
`scenarioReview` manifest object reports `status=review-pending`,
`inputKind=candidate`, the resolved input path and SHA-256, and
`semanticValidation=not-run`; `validation.semanticReview=pending` and
`validation.semanticMatch=not-run`. Reuse checks the candidate hash, and
`--force` cannot overwrite an unreviewed fixture.

```powershell
python Tools\SolutionMigration\generate_mock_scenario.py `
  --solution "<solution>" `
  --rule "<rule>" `
  --custom-detection "<path>" `
  --candidate-scenario "<candidate.json>" `
  --source-root "<Azure-Sentinel-repository>" `
  --toolkit-root "<repository-containing-this-generator>" `
  --output-root "<Azure-Sentinel-repository>\Sample Data\Solutions\Mock"
```

## Reviewed complex scenarios

For complex behavior, supply a candidate or reviewed JSON file:

```json
{
  "name": "reviewed-sequence",
  "hypothesis": "Documented behavior observable in the selected telemetry.",
  "lockedPaths": ["requestId"],
  "maliciousRecords": [
    {}
  ],
  "benignRecords": [
    {}
  ]
}
```

Run with:

```powershell
python Tools\SolutionMigration\generate_mock_scenario.py `
  --solution "<solution>" `
  --rule "<rule>" `
  --custom-detection "<path>" `
  --reviewed-scenario "<scenario.json>" `
  --source-root "<Azure-Sentinel-repository>" `
  --toolkit-root "<repository-containing-this-generator>" `
  --output-root "<Azure-Sentinel-repository>\Sample Data\Solutions\Mock"
```

Use `--candidate-scenario` while human review is pending and
`--reviewed-scenario` only after a human reviewer accepts the hypothesis and
records. The JSON contract is exactly `name` (non-empty string), `hypothesis`
(non-empty string), optional `lockedPaths` (string array),
`maliciousRecords` (non-empty array of objects), and `benignRecords` (non-empty
array of objects). Each record must already match the selected raw DCR input
contract or Standard-table metadata contract; malformed or unknown fields and
type mismatches block generation. This transports reviewed multi-field and
multi-record fixtures; it does not solve KQL joins, aggregates, thresholds, or
prove that records satisfy either query. Keep those cases `manual-review-required`
and `generated-offline-only` until independently validated. Do not treat
schema validation as semantic matching or approval for environment writes.
`expectedMatchKeys` is not a supported machine-checked field; record expected
join/grouping keys and unique marker values in the hypothesis/review notes and
verify them against the exact AR and CD queries separately.

For the Cisco ASA average-rate rule, candidate records must preserve the exact
one-hour current window and prior `ago(6h)..ago(1h)` five-hour interval,
including the source's `prev6hCumTotal / 6` comparison and OR of all three
doubling thresholds. Keep the five join/group keys aligned across the two
windows and construct `Message` values that the source's parsing expressions
actually accept. For the exfiltration rule, preserve the >=1-GiB sent-byte
threshold, rounded >=95% upload ratio, time window, ASA/FTD product, allowed
action, private source IP, and public destination IP predicates. The generator
only transports and type-checks these reviewed rows; it does not synthesize
Cisco message grammar, calculate query aggregates, or prove a match. Include
separate benign controls and keep both rules blocked from automatic semantic
qualification.

Example Cisco ASA routing (candidate JSON paths are supplied by the author;
this generator does not invent them):

```powershell
python Tools\SolutionMigration\generate_mock_scenario.py `
  --source-root "<Azure-Sentinel-1 checkout>" `
  --toolkit-root "<toolkit checkout>" `
  --solution CiscoASA `
  --rule 795edf2d-cf3e-45b5-8452-fe6c9e6a582e `
  --custom-detection "Solutions\CiscoASA\XDR Detections\CiscoASA-ThreatDetectionMessage.yaml" `
  --candidate-scenario "<candidate-threat-detection-message.json>" `
  --output-root "<Azure-Sentinel-1 checkout>\Sample Data\Solutions\Mock"

python Tools\SolutionMigration\generate_mock_scenario.py `
  --source-root "<Azure-Sentinel-1 checkout>" `
  --toolkit-root "<toolkit checkout>" `
  --solution CiscoASA `
  --rule 79f29feb-6a9d-4cdf-baaa-2daf480a5da1 `
  --custom-detection "Solutions\CiscoASA\XDR Detections\CiscoASA-AvgAttackDetectRateIncrease.yaml" `
  --candidate-scenario "<candidate-average-detection-rate.json>" `
  --output-root "<Azure-Sentinel-1 checkout>\Sample Data\Solutions\Mock"

python Tools\SolutionMigration\generate_mock_scenario.py `
  --source-root "<Azure-Sentinel-1 checkout>" `
  --toolkit-root "<toolkit checkout>" `
  --solution CiscoASA `
  --rule f3a8c2d0-7b41-4e9a-9f6a-2d8a1c4e5b72 `
  --custom-detection "Solutions\CiscoASA\XDR Detections\CiscoASA-PossibleDataExfiltration.yaml" `
  --candidate-scenario "<candidate-data-exfiltration.json>" `
  --output-root "<Azure-Sentinel-1 checkout>\Sample Data\Solutions\Mock"
```

## Output contract

```text
<output-root>\<solution>\<rule-id>\ (defaults to toolkit Sample Data\Solutions\Mock)
    mock.json
    scenario.json
```

`scenario.json` records:

- AR and CD identity;
- attack hypothesis;
- query-complexity assessment;
- source and destination tables;
- DCR, stream, output stream, and ingestion mode;
- decisive field mappings and locked paths;
- shared mock record count and benign validation-control count;
- schema validation;
- explicit candidate/reviewed/not-required semantic-review status and input hash;
- separate seeded, live, alert, and cleanup statuses.

Only `generationStatus=qualification-ready` scenarios with
`directLogsIngestionSupported=true` may proceed to direct DCR ingestion.
`generated-offline-only` scenarios remain valid for query harnesses but not
for direct Logs Ingestion API qualification.

## Handoff

After generation or reuse:

1. present the scenario path and status;
2. review the AR/CD identity, DCR mapping, shared mock record count, and limitations;
3. hand off to `sentinel-solution-optional-testing` only when the user requests
   live qualification;
4. never treat generation as proof of ingestion, query match, alert creation,
   or migration parity.
