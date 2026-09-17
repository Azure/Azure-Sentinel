---
name: sentinel-solution-migration
description: Coordinate the existing Sentinel-to-XDR migration flow and optionally extend its testing stage with reviewed mock generation and guarded ingestion.
---

# Sentinel Solution Migration Agent

Coordinate the existing `Tools\SentinelToXDRMigration` flow without replacing
or reimplementing its conversion, validation, deployment, or runtime
validation behavior. Add mock generation and DCR ingestion only as optional
testing capabilities.

## Required inputs

- exact solution folder;
- exact source Analytic Rule ID, name, filename, or path;
- exact converted Custom Detection YAML or selector when conversion has
  already run.

## Startup prerequisites

Run authentication and general runtime readiness before migration work:

```powershell
sentinel-xdr-migration doctor
```

If this is the first run or authentication is incomplete, run:

```powershell
sentinel-xdr-migration setup
sentinel-xdr-migration doctor
```

This is the existing toolkit setup. It owns Azure CLI `az login`, Sentinel
authentication, Advanced Hunting authentication, and offline fallback.
Do not duplicate its token or authentication storage.

Show the readiness results and present:

1. **Continue** - proceed when runtime prerequisites are ready.
2. **Retry startup check** - rerun `doctor` after authentication or permission
   changes.
3. **Continue offline** - retain conversion and static validation while marking
   unavailable runtime stages `not-run` or `blocked`.
4. **Cancel** - stop without modifying solution content.

Use structured user elicitation so these actions render as selectable buttons
when available.

## Flow

1. Complete the startup prerequisite stage above.
2. Run the existing toolkit's inspect, conversion, and structural-validation
   stages unchanged.
3. Read the source Analytic Rule and converted Custom Detection.
4. Confirm the detection file is a deployable YAML with top-level `id`, `name`,
   and `query`, and that its source identity matches the selected rule.
5. Keep `Solutions\<solution>\XDR Detections\` YAML-only. Route non-deployable
   evidence to ignored `Reports`.
6. If optional live testing was requested, determine the exact stream from the
   solution DCR and run the read-only workspace, DCR, Sentinel query, and
   effective ingestion-permission preflight before preparing mock data.
7. Present **Continue**, **Retry permission check**, and **Cancel**:
    - Continue to fixture review when checks pass.
    - Continue without live ingestion when a required check is blocked or
      unknown.
    - Retry the same read-only preflight after access changes.
    - Cancel only the optional testing extension.
    - The Continue action is not write approval.
8. Check
   `Sample Data\Solutions\Mock\<solution>\<rule-id>\scenario.json`.
9. If a complete, schema-valid matching scenario exists, reuse it.
10. Otherwise invoke `sentinel-solution-mock-data-generation`.
11. Stop for reviewed input when the generator reports complex, unsupported, or
   insufficiently evidenced behavior. Do not reduce a multi-event hypothesis
   to an arbitrary single record.
12. Run static and offline checks without requiring Azure access.
13. Invoke `sentinel-solution-optional-testing` only when the user explicitly
   requests live Azure qualification.
14. Show the exact tenant, subscription, workspace, DCR, stream, fixture,
    record count, destination, and cleanup plan.
15. Pass `--approve-write` only after approval for that exact scope. The
    preflight Continue action is not write approval.
16. Return to the existing toolkit's runtime-validation stages. Do not replace
    its Sentinel, Advanced Hunting, Triage MCP, result-recording, deployment,
    parity, or packaging behavior.
17. Track ingestion acceptance, visibility, Sentinel query match, Defender XDR
    query match, alert creation, parity, and cleanup as separate outcomes.

## Stage ownership

- `sentinel-solution-mock-data-generation` owns scenario reuse/generation and
  schema validation. It never writes to Azure.
- `sentinel-solution-optional-testing` owns discovery, approval, ingestion,
  live validation, cleanup, and runtime evidence.
- `Tools\SentinelToXDRMigration` retains ownership of the original setup,
  conversion, structural validation, runtime validation, deployment, parity,
  and packaging flow.
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
