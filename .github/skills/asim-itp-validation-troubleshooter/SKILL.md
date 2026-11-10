---
name: asim-itp-validation-troubleshooter
description: Diagnoses GitHub Actions runs for the ASIM ingestion-time parser validation workflow. Use when a user provides a run URL or ID, asks why an ITP target was missed or failed, or needs exact evidence-based remediation without automatic code changes.
---

# ASIM ingestion-time validation troubleshooter

Diagnose the `Run ASIM ingest-time parser validation` workflow from its run
metadata, job timing, artifacts, logs, and the exact pull-request revision that
was tested. Explain the root cause and recommend precise fixes. Do not edit,
commit, push, rerun, deploy, or modify Azure resources unless the user
explicitly asks in a later request.

## Inputs

Required:

- A GitHub Actions run URL or numeric run ID.

Optional:

- A target ID when the run contains multiple parsers.
- A pull-request URL or number when it is not recoverable from the run.
- A previous run to compare.

Use `Azure/Azure-Sentinel` as the repository unless the user explicitly names
another repository.

## Prerequisites

- Run from an Azure-Sentinel checkout.
- Use the GitHub CLI and verify that `gh auth status` succeeds.
- Keep downloaded artifacts outside the repository. Never commit run artifacts,
  resource IDs, workspace details, or customer data.

## Evidence priority

Use evidence in this order:

1. Run event metadata, head SHA, base SHA, attempt, and per-step timestamps.
2. Target `report.json`, which provides the canonical ordered stage result.
3. `validation-result.json` and nested Azure/provider diagnostics.
4. `static-validation.json`, `prepared-fixture.json`, `target.json`,
   `discovery.json`, and `matrix.json`.
5. Exact job logs for checkout, discovery, template validation, ingestion, and
   reporting.
6. Parser, fixture, and workflow content at the run's recorded head/base SHAs.

Do not diagnose from the PR's current **Files changed** view until comparing its
current head SHA with the run head SHA. If they differ, state the timing
difference and inspect the run SHA. A later fix must never be described as
content that the earlier run tested.

## Collect diagnostics

Run:

```powershell
.\.github\skills\asim-itp-validation-troubleshooter\scripts\Get-AsimItpValidationDiagnostics.ps1 `
  -Run "<run URL or ID>"
```

Optional parameters:

```powershell
-Repository "Azure/Azure-Sentinel"
-Attempt <attempt number>
-OutputDirectory "<directory outside the repository>"
-IncludeSuccessfulTargetLogs
```

An `/attempts/<N>` run URL is recognized automatically. For an older attempt,
the collector uses attempt-specific metadata and logs and skips automatic
artifact download rather than mixing in artifacts from the latest attempt.

The script creates:

- `run.json` — run, PR, job, step, and timing metadata.
- `artifacts\` — downloaded `asim-ingestion-*` artifacts when available.
- `logs\` — discovery/report logs plus failed or cancelled target logs.
- `diagnostics.json` — normalized diagnostic evidence.
- `diagnostics.md` — concise stage and failure summary.

If artifact download fails because artifacts expired or were never produced,
continue with job logs and explicitly state the evidence limitation.

## Investigation workflow

1. **Verify run identity**
   - Confirm workflow name, run attempt, event, conclusion, PR number, base SHA,
     and head SHA.
   - If the PR moved after the run, inspect files at the run SHA.

2. **Inspect job and step timing**
   - Distinguish job queue time from execution time.
   - Identify the step consuming the runtime.
   - A ten-minute discovery job may have spent all ten minutes in checkout and
     never executed discovery.

3. **Inspect discovery**
   - Compare `changedPaths`, `changedParserPaths`, `indexErrors`, and `targets`.
   - Validate exact, case-sensitive paths:

     ```text
     Parsers/ASim<Schema>/IngestTimeParsers/<Parser>.yaml
     ```

   - Zero targets with changed sample data commonly means a misspelled or
     mis-cased parser directory.

4. **Inspect each target in report order**

   ```text
   discovery
   counterpart
   template
   fixture
   filtering
   parserDcr
   parserIngestion
   schema
   data
   *rawDcr
   *rawIngestion
   *qtpExecution
   *parity
   cleanup
   ```

   The `*` stages are optional replay/parity stages. Use the artifact status,
   not the asterisk alone, to determine whether a failure is required,
   warning-only, blocked, skipped, or not run.

5. **Find the earliest causal failure**
   - Later skipped/not-run stages are consequences, not independent causes.
   - Preserve nested Azure errors such as `InvalidTransformQuery`,
     `InvalidStream`, and exact KQL line/column diagnostics.

6. **Map the failure to source**
   - Decode `ParserQuery` from the exact run artifact.
   - Map Azure DCR line numbers to the literal query block.
   - Trace KQL column lifetimes through `project`, `project-rename`, `extend`,
     parsing operators, and final projection.
   - Confirm fixture column names and types against `prepared-fixture.json`.

7. **Recommend an exact fix**
   - Name the file, operator, field, or missing artifact.
   - Show a minimal before/after KQL or exact expected path.
   - Separate parser defects from validator limitations and infrastructure
     failures.
   - State which stages should run after the fix.

Read [failure-catalog.md](references/failure-catalog.md) for stage semantics,
common signatures, and remediation patterns.

## Required diagnostic rules

### Static `EventVendor` and `EventProduct`

Fixture discovery requires one non-empty, filename-safe literal assignment for
each field. The resolver examines **every** assignment. An earlier dynamic
assignment still fails even when a later literal overwrites it:

```kusto
| project-rename EventProduct = DeviceProduct
| extend EventProduct = "FortiGate"
```

Recommend removing the dead dynamic assignment or otherwise making every
assignment the same literal. Explain that this is conservative regex-based
validation, not KQL last-write-wins analysis.

### Missing source-specific fixture

Report the exact required path from `discoveryErrors` or
`fixtureResolution.path`. Do not invent a differently cased vendor/product
name. The required format is:

```text
Sample Data/ASIM/<EventVendor>_<EventProduct>_<Schema>_<SourceRawTable>_IngestedLogs.csv
```

### Undefined symbols during DCR creation

Check whether an earlier `project-rename` or `project` removed the original
column:

```kusto
| project-rename EventOriginalUid = CrowdStrikeId
| extend EventUid = CrowdStrikeId
```

After the rename, recommend using `EventOriginalUid` or creating `EventUid`
before the rename.

### Checkout timeout

Use step timestamps and the exact `git fetch` command. If checkout uses
`fetch-depth: 0` and fetches `refs/heads/*` plus `refs/tags/*`, identify the
full-repository fetch as the bottleneck. Do not attribute that time to Python
target discovery.

### Current PR differs from run

Always report both SHAs and the later commit time. Explain which findings are
already fixed and which remain at the current head.

## Output format

Lead with the causal outcome, then provide:

````markdown
**Run:** <ID>, attempt <N>, head <SHA>
**Target:** <target ID or "discovery">
**Failure point:** <stage and step>

| Stage | Status | Evidence |
|---|---|---|
| ... | ... | ... |

**Root cause:** ...

**Exact fix:**
```kusto
<minimal correction when applicable>
```

**Consequences:** <stages skipped or blocked because of the root failure>
````

For multi-target runs, use one compact row per target followed by details only
for failed targets. Do not repeat large artifact payloads or fixture rows.
