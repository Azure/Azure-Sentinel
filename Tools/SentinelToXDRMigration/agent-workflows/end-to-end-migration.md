# Sentinel to Defender XDR migration workflow

This is the canonical, agent-neutral workflow for authoring and migrating
Microsoft Sentinel solution content to Defender XDR Custom Detections. Agent
adapters must reference this document rather than redefine the process.

Deterministic behavior belongs to:

- `Tools\SentinelToXDRMigration`;
- `Tools\Create-Azure-Sentinel-Solution`; and
- the repository validation tools.

Agents coordinate these tools but must not reproduce conversion, validation,
packaging, deployment, or comparison logic in prompts.

## Profiles

### Authoring

`Discovery -> Conversion -> Validation -> Packaging -> Report`

This is the ISV publishing workflow. It does not require a tenant, workspace,
deployment, mock ingestion, or alert-parity test.

### Qualification — explicit opt-in

`Discovery -> Conversion -> Validation -> Packaging -> Deployment -> Mock ingestion -> Alert parity -> Report`

This is optional internal or ISV lab testing. Before initialization, require
the user to explicitly choose **Authoring**, **Qualification**, or **Cancel**.
There is no default and no workflow state may be created while the choice is
missing or declined. A configured tenant or workspace does not imply consent.

Qualification requires an approved non-production tenant and workspace plus
separate approval immediately before deployment or ingestion writes.

## Initialize or resume

Install the CLI when necessary:

```powershell
python -m pip install -e Tools\SentinelToXDRMigration
```

Run `workflow-status` first. If state does not exist, or
`context.profileSelectionConfirmed` is not `true`, obtain the explicit profile
selection before initializing:

```powershell
sentinel-xdr-migration workflow-init `
  --solution "<solution-path>" `
  --workflow-profile authoring `
  --version-bump none
```

For an approved qualification run, use `qualification` and include
`--workspace-resource-id`.

Always resume from persisted state:

```powershell
sentinel-xdr-migration workflow-status --solution "<solution-path>"
sentinel-xdr-migration workflow-next --solution "<solution-path>"
```

When workflow context contains a full `workspaceResourceId`, it is authoritative
for the rest of that run. Pass it explicitly to every Azure command and never
list, rediscover, rank, or scan other workspaces. A Log Analytics customer-ID
GUID may be resolved to an ARM resource ID once, then the ARM ID must be
persisted. A tenant mismatch is an authentication blocker for the selected
workspace, not a reason to choose another workspace.

The ignored local file
`Reports\<solution>\sentinel-xdr-migration\workflow-state.json` records stage status, attempts,
timestamps, artifacts, evidence, profile, workspace, and version action. Never
store credentials or tokens in it and never mark a stage passed without
evidence.

Start and complete each stage:

```powershell
sentinel-xdr-migration workflow-start-stage `
  --solution "<solution-path>" `
  --stage discovery

sentinel-xdr-migration workflow-complete-stage `
  --solution "<solution-path>" `
  --stage discovery `
  --status passed `
  --message "Reviewed source inventory" `
  --artifact inspection="Reports\<solution>\sentinel-xdr-migration\inspection.json" `
  --evidence "Analytic Rules\Example.yaml"
```

Allowed terminal statuses are `passed`, `failed`, and `blocked`. Explain
failed and blocked results. Correct and retry only that stage.

## Stage gates

### Discovery

Run `sentinel-xdr-migration inspect`. Account for every source rule, ID, table,
query, and existing XDR artifact. Reject duplicate IDs, ambiguous provenance,
and content without defensible attacker behavior or observable telemetry.

### Conversion

Run `sentinel-xdr-migration convert`. Preserve source Analytic Rules. Generated
files belong under `XDR Detections`, remain disabled, and contain source
provenance. Pass only with no conflicts and no unresolved `needsReview` item.
Only deployable detection YAML belongs under `XDR Detections`; conversion
manifests, reports, configuration, validation evidence, and state belong under
`Reports\<solution>\sentinel-xdr-migration`.

### Validation

Run structural validation, then validate original Sentinel and converted
Advanced Hunting queries. Prefer capabilities advertised by the official
Sentinel Triage MCP. Fall back to Log Analytics for Sentinel queries and
Microsoft Graph for Advanced Hunting only for provider-level failures.

Unavailable workload tables are blocked environment results. Zero rows prove
query execution, not behavioral parity. Entity mappings require review.

Defender Advanced Hunting and Log Analytics workspace queries are distinct
surfaces. A table visible in one does not prove availability in the other.
Always name the failing surface and use only the persisted workspace for
Sentinel validation.

For Authoring, structural success with an environment-only runtime gap may
complete this stage as passed with `runtimeStatus=environment-blocked`; preserve
the exact error and do not claim runtime qualification. This allows V4 package
creation. Qualification keeps the same gap blocking because deployment, mock
ingestion, and parity require the selected lab environment.

### Packaging

Use V4 for solutions containing XDR Detections:

```powershell
sentinel-xdr-migration package-v4 `
  --solution ".\Solutions\<solution>" `
  --version-bump none
```

V3 is the legacy Sentinel-only packager and intentionally skips XDR
Detections. Use `none` for repeat checks. Use an approved `patch`, `minor`, or
`major` action once when preparing the submission package; it synchronizes the
solution data and metadata versions.

Require the generated template, UI definition, parameter file, versioned ZIP,
AR/CD count matching, correct `E5Flavor` conditions, disabled CDs, unique IDs,
and explained validation results. Complete the packaging stage only with
`packager=V4`, the generated `packaging.v4.json`, and its template, UI,
parameters, and ZIP paths. Existing package files are not current-run evidence.

### Deployment — qualification only

Deploy every reviewed AR and CD disabled. Verify Azure RBAC and Microsoft Graph
scopes separately. A successful write without live read verification is
blocked, not passed. Never infer Azure resource permissions from Entra Global
Administrator.

### Mock ingestion — qualification only

Use `sentinel-solution-optional-testing` for this stage:

1. Run read-only workspace, DCR, Sentinel query, and effective ingestion
   permission preflight before fixture preparation.
2. Present Continue, Retry permission check, or Cancel. Continue is not write
   approval.
3. Check the default rule-specific fixture path first.
4. Reuse a complete reviewed scenario or invoke
   `sentinel-solution-mock-data-generation`.
5. Require reviewed input for joins, thresholds, aggregation, sequences,
   historical baselines, watchlists, anomalies, and absence-of-data behavior.
6. Require separate exact-scope approval immediately before ingestion.
7. Track ingestion acceptance and query visibility independently.

Every fixture needs a unique scenario marker and expected malicious match-key
set. Pass only after ingestion is accepted and the exact target query can
observe the records. The existing runtime-validation and alert-parity stages
remain unchanged.

### Alert parity — qualification only

Use `start-alert-parity-batch` with a plan covering every converted detection:

1. Verify all ARs and CDs are disabled.
2. Enable all reviewed pairs.
3. Ingest every dedicated fixture.
4. Capture alerts for every pair.
5. Compare counts, match keys, severity, tactics, entities, decisive evidence,
   and benign controls.
6. Complete or abort so every rule is disabled after success or failure.

### Report

Run `sentinel-xdr-migration solution-report`. The JSON and HTML reports must
distinguish passes, review requirements, environment blocks, skipped checks,
and genuine failures.

## Safety and completion

- Never use production telemetry or a production workspace for qualification.
- Ask before interactive authentication.
- Do not bypass failed or blocked gates.
- Do not rerun a passed release packaging stage and increment twice.
- Keep detections disabled except during controlled parity.
- Authoring completes after packaging and reporting pass.
- Qualification completes only after all optional lab stages and reporting
  pass.
