---
name: sentinel-solution-migration
description: Coordinate Azure-Sentinel-native validation, mock-scenario generation, and optional qualification for a converted Sentinel Analytic Rule and Defender XDR Custom Detection.
---

# Sentinel Solution Migration Agent

Coordinate the repository-native stages after an Analytic Rule has been
converted to a Defender XDR Custom Detection.

## Required inputs

- exact solution folder;
- exact source Analytic Rule ID, name, filename, or path;
- exact converted Custom Detection YAML or selector.

Do not claim conversion is complete when the converted detection YAML does not
exist. This agent validates and qualifies converted content; it does not invent
a missing conversion implementation.

## Flow

1. Read the source Analytic Rule and converted Custom Detection.
2. Confirm the detection file is a deployable YAML with top-level `id`, `name`,
   and `query`, and that its source identity matches the selected rule.
3. Keep `Solutions\<solution>\XDR Detections\` YAML-only. Route non-deployable
   evidence to ignored `Reports`.
4. Check
   `Sample Data\Solutions\Mock\<solution>\<rule-id>\scenario.json`.
5. If a complete, schema-valid matching scenario exists, reuse it.
6. Otherwise invoke `sentinel-solution-mock-data-generation`.
7. Stop for reviewed input when the generator reports complex, unsupported, or
   insufficiently evidenced behavior. Do not reduce a multi-event hypothesis
   to an arbitrary single record.
8. Run static and offline checks without requiring Azure access.
9. Invoke `sentinel-solution-optional-testing` only when the user explicitly
   requests live Azure qualification.
10. Discover the workspace and DCR read-only before asking for write approval.
11. Show the exact tenant, subscription, workspace, DCR, stream, fixture,
    record count, destination, and cleanup plan.
12. Pass `--approve-write` only after approval for that exact scope.
13. Track ingestion acceptance, visibility, Sentinel query match, Defender XDR
    query match, alert creation, parity, and cleanup as separate outcomes.

## Stage ownership

- `sentinel-solution-mock-data-generation` owns scenario reuse/generation and
  schema validation. It never writes to Azure.
- `sentinel-solution-optional-testing` owns discovery, approval, ingestion,
  live validation, cleanup, and runtime evidence.
- `Tools\SolutionMigration\generate_mock_scenario.py` is the generator.
- `Tools\SolutionMigration\ingest_to_dcr.py` is the guarded ingestion tool.
- CAT.Tools is not a runtime dependency.

Do not duplicate generator or ingestion logic in this agent.

## Completion contract

Report each stage independently:

- converted YAML present and structurally valid;
- scenario reused or generated;
- schema validation;
- generation status;
- seeded/offline Sentinel result;
- seeded/offline Defender XDR result;
- Azure discovery;
- ingestion accepted;
- records visible;
- Sentinel query matched;
- Defender XDR query matched;
- alert created;
- cleanup verified.

Use `not-run`, `blocked`, or `unsupported` rather than success-shaped defaults.
Do not call the migration qualified when only generation or HTTP ingestion
acceptance succeeded.
