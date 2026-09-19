---
name: sentinel-solution-mock-data-generation
description: Generate or reuse reviewed malicious and benign mock fixtures for a Microsoft Sentinel Analytic Rule and its converted Defender XDR Custom Detection. Uses only Azure-Sentinel repository content and never writes to Azure.
version: 1.0.0
allowed-tools: Bash, Read, Grep, Glob
---

# Sentinel Solution Mock Data Generation

Use this skill when a migration or optional-testing workflow needs mock data
for a specific Analytic Rule and converted Custom Detection.

## Safety contract

- Work entirely inside the Azure-Sentinel repository.
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

## Existing-scenario-first flow

Check:

```text
Sample Data\Solutions\Mock\<solution>\<rule-id>\
    malicious.json
    benign.json
    scenario.json
```

Run:

```powershell
python Tools\SolutionMigration\generate_mock_scenario.py `
  --solution "<solution-folder>" `
  --rule "<rule-id-or-exact-name>" `
  --custom-detection "Solutions\<solution>\XDR Detections\<detection>.yaml"
```

Without `--force`, a complete scenario that passed schema validation is
returned with `status=existing-scenario`. Reuse it after reviewing that its AR,
CD, stream, and hypothesis still match the current content.

## Automatic generation

For a simple rule, the tool:

1. reads the AR and CD;
2. extracts decisive source predicates;
3. inspects the solution package and parser;
4. reverse-maps fields through parser and DCR transforms when a declared
   `Custom-*` input stream exists;
5. otherwise starts from the checked-in Standard-table base event;
6. creates a malicious record that satisfies the decisive predicate;
7. creates a type-safe benign negative control;
8. validates every field against the DCR or table metadata;
9. writes the rule-specific fixture bundle.

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

## Reviewed complex scenarios

For complex behavior, supply a reviewed JSON file:

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
  --reviewed-scenario "<scenario.json>"
```

The supplied records must already match the raw DCR input contract or the
Standard-table metadata contract.

## Output contract

```text
Sample Data\Solutions\Mock\<solution>\<rule-id>\
    malicious.json
    benign.json
    scenario.json
```

`scenario.json` records:

- AR and CD identity;
- attack hypothesis;
- query-complexity assessment;
- source and destination tables;
- DCR, stream, output stream, and ingestion mode;
- decisive field mappings and locked paths;
- malicious and benign record counts;
- schema validation;
- separate seeded, live, alert, and cleanup statuses.

Only `generationStatus=qualification-ready` scenarios with
`directLogsIngestionSupported=true` may proceed to direct DCR ingestion.
`generated-offline-only` scenarios remain valid for query harnesses but not
for direct Logs Ingestion API qualification.

## Handoff

After generation or reuse:

1. present the scenario path and status;
2. review the AR/CD identity, DCR mapping, record counts, and limitations;
3. hand off to `sentinel-solution-optional-testing` only when the user requests
   live qualification;
4. never treat generation as proof of ingestion, query match, alert creation,
   or migration parity.
