# Microsoft Sentinel to Defender XDR migration toolkit

This toolkit converts the analytic rules in a Microsoft Sentinel solution into
versioned Defender XDR Custom Detection YAML files.

The first milestone intentionally stops before ARM generation. It creates and
validates:

```text
Solutions/<solution>/
  Analytic Rules/
    <rule>.yaml
  XDR Detections/
    <rule>.yaml
    manifest.json
```

Each XDR Detection YAML contains:

- the properties required to generate a
  `Microsoft.Security/detectionRules` resource;
- a disabled-by-default lifecycle state;
- converted KQL;
- translated entity mappings;
- one supported MITRE tactic;
- a `contentProvenance` block linking the detection to its source analytic
  rule and recording conversion warnings.

The YAML contract is defined in
[`schema/xdr-detection.schema.json`](schema/xdr-detection.schema.json).

## Safety model

Conversion is conservative. A file is still generated when manual work is
needed, but `contentProvenance.conversion.status` is set to `needsReview` and
validation fails until blocking issues are resolved. The tool never changes
files under `Analytic Rules` and does not modify `Package/mainTemplate.json`.

Generated detections start with:

```yaml
properties:
  status: disabled
```

## Install

```powershell
cd Tools\SentinelToXDRMigration
python -m pip install -e .
```

## First-run setup

Run the guided setup once:

```powershell
sentinel-xdr-migration setup
```

If tenant security policy blocks device-code authentication, use interactive
browser authentication:

```powershell
sentinel-xdr-migration setup --hunting-auth-method browser
```

Setup checks the local environment and launches authentication only when it is
needed:

- `az login` for original Sentinel query execution through Log Analytics;
- a one-time Microsoft Graph device-code sign-in for Advanced Hunting.

Authentication tokens are managed by Azure CLI and the operating system's
credential cache. The toolkit stores only an authentication record and
non-secret configuration under `~/.sentinel-xdr-migration`.

Inspect readiness at any time:

```powershell
sentinel-xdr-migration doctor
```

Conversion and structural validation always remain available in offline mode.
Missing runtime access is reported explicitly and never blocks YAML generation.
For unattended inspection without opening sign-in prompts:

```powershell
sentinel-xdr-migration setup --non-interactive
```

The CLI setup covers Azure CLI and direct Microsoft Graph authentication. The
official Triage MCP is configured and authenticated in the agent host, not by
this Python package. For first use, configure:

```text
https://sentinel.microsoft.com/mcp/triage
```

Sign in with a supported tenant member identity and complete the tenant's
required Defender/Sentinel onboarding, consent, and security-reader access.
Guest identities may not work. The agent should verify that
`RunAdvancedHuntingQuery` is available before selecting Triage as its runtime
provider.

## Command line

### Resumable end-to-end workflow

The repository agent uses a gated workflow manifest. The default `authoring`
profile coordinates discovery, conversion, validation, packaging, and final
reporting:

```powershell
sentinel-xdr-migration workflow-init `
  --solution "Solutions\<solution>" `
  --workflow-profile authoring `
  --version-bump patch

sentinel-xdr-migration workflow-status --solution "Solutions\<solution>"
sentinel-xdr-migration workflow-next --solution "Solutions\<solution>"
```

The workflow state is written to:

```text
Reports\<solution>\sentinel-xdr-migration\workflow-state.json
```

Each stage is explicitly started and completed so interrupted runs can resume
without relying on conversation history:

```powershell
sentinel-xdr-migration workflow-start-stage `
  --solution "Solutions\<solution>" `
  --stage discovery

sentinel-xdr-migration workflow-complete-stage `
  --solution "Solutions\<solution>" `
  --stage discovery `
  --status passed `
  --artifact inspection="Reports\<solution>\sentinel-xdr-migration\inspection.json" `
  --evidence "Analytic Rules\Example.yaml"
```

Stages accept `passed`, `failed`, or `blocked`. Failed and blocked stages
require an explanation and can be retried after their cause is corrected.
Downstream stages remain locked until every dependency passes. The contract is
defined by [`schema/workflow-state.schema.json`](schema/workflow-state.schema.json).

Deployment, mock ingestion, and strict AR/CD alert parity are optional internal
qualification stages. They are not required for ISV authoring, PR submission,
Partner Center publishing, or customer deployment. To include them in an
approved non-production lab workflow, initialize with:

```powershell
sentinel-xdr-migration workflow-init `
  --solution "Solutions\<solution>" `
  --workflow-profile qualification `
  --workspace-resource-id "<workspace-arm-id>" `
  --version-bump patch
```

Inspect a solution:

```powershell
python -m sentinel_xdr_migration.cli inspect `
  --solution "Solutions\Azure Activity"
```

Convert every analytic rule:

```powershell
python -m sentinel_xdr_migration.cli convert `
  --solution "Solutions\Azure Activity"
```

Every conversion run automatically creates:

```text
Reports\<solution>\sentinel-xdr-migration\transformation-report.html
```

The self-contained report shows attempted, converted, needs-review, and
conflict counts, followed by each rule's output status, warnings, and errors.
It can be opened locally without a server or external assets.

Validate the generated YAML:

```powershell
python -m sentinel_xdr_migration.cli validate `
  --solution "Solutions\Azure Activity"
```

Validate converted queries through Microsoft Graph Advanced Hunting:

```powershell
python -m sentinel_xdr_migration.cli validate-advanced-hunting `
  --solution "Solutions\Azure Activity"
```

The runtime validator probes required tables first. A query is reported as
`blocked` rather than `failed` when its Sentinel workload table is unavailable
in the current tenant. It creates:

```text
Reports\<solution>\sentinel-xdr-migration\runtime-validation.graph.json
Reports\<solution>\sentinel-xdr-migration\runtime-validation.graph.html
```

Agents using the official Triage MCP should inspect its advertised capabilities
and use suitable MCP tools first for all supported runtime query operations.
For Advanced Hunting, execute the queries from `validation-plan`, normalize the
results, and record them through the same reporting contract:

```powershell
sentinel-xdr-migration record-runtime-validation `
  --solution "Solutions\Azure Activity" `
  --provider triage-mcp `
  --results "<normalized-results.json>"
```

This creates `runtime-validation.triage-mcp.json` and
`runtime-validation.triage-mcp.html`. The public CLI does not implement or host
an MCP server; the repository skill invokes the configured official MCP.

For original Sentinel queries, the orchestrator falls back to Log Analytics
CLI/API when the connected MCP does not advertise a suitable workspace-query
tool or has a provider-level failure. Record those normalized results with
`--provider log-analytics-cli`; rules intentionally excluded from a targeted
live scenario can use the `not-run` status. For Advanced Hunting, the
orchestrator falls back to the Graph CLI. A genuine KQL error returned by
Triage is preserved as a failed detection and is not retried through another
provider.

## Strict live alert parity

Query execution alone does not prove migration parity. In a non-production lab,
the optional alert-parity workflow temporarily enables an already deployed
Sentinel Analytic Rule and its migrated Custom Detection, ingests a reviewed
payload containing a unique marker, and compares normalized alerts strictly.

For full internal qualification, create a JSON plan containing one contract,
payload, unique marker, and expected malicious key set per converted detection,
then enable all pairs and ingest all fixtures:

```powershell
sentinel-xdr-migration start-alert-parity-batch `
  --solution "Solutions\<solution>" `
  --workspace-resource-id "<workspace-arm-id>" `
  --plan "<qualification-plan.json>"
```

The plan must cover every converted detection. All rules must begin disabled
and are disabled again if any enablement or ingestion fails.

For targeted troubleshooting, start one or more explicitly selected rule
pairs with a shared fixture:

```powershell
sentinel-xdr-migration start-alert-parity `
  --solution "Solutions\<solution>" `
  --workspace-resource-id "<workspace-arm-id>" `
  --contract "<ingestion-contract>" `
  --payload "<mock-json>" `
  --scenario-marker "<unique-marker>" `
  --expected-match-key "<expected-malicious-key>" `
  --detection "<Detection.yaml>"
```

The command requires both rules to be disabled, enables them, invokes the
separate `azure-monitor-logs-ingestion` CLI, and emits provider-neutral capture
queries. It does not use fixed sleeps. Prefer official Sentinel Triage MCP
query tools and use the documented CLI/API fallbacks only for provider-level
failures.

After normalizing both alert sets, complete the comparison:

```powershell
sentinel-xdr-migration complete-alert-parity `
  --solution "Solutions\<solution>" `
  --results "<normalized-alert-results.json>"
```

Strict parity requires equal alert counts, stable match keys, severity, tactics,
entities, and decisive evidence. The observed keys must also equal the declared
malicious match-key set, so a benign false positive on both platforms still
fails. Completion disables every selected rule in a cleanup path even when
comparison fails. If capture cannot be completed, run:

```powershell
sentinel-xdr-migration abort-alert-parity --solution "Solutions\<solution>"
```

State and reports are written under
`Reports\<solution>\sentinel-xdr-migration` as `alert-parity-state.json` and
`alert-parity-report.json`.

## Consolidated solution report

Build one solution-level JSON and HTML report after any stage:

```powershell
sentinel-xdr-migration solution-report `
  --solution "Solutions\<solution>" `
  --ingestion-report "<stream-one-ingestion-report.json>" `
  --ingestion-report "<stream-two-ingestion-report.json>"
```

The report includes every source rule, AR and CD identifiers and statuses,
conversion and structural results, runtime providers, deployment, strict alert
parity, entity recommendations, ingestion artifacts, and complete structured
errors. The HTML renders detailed errors in expandable sections; the JSON
retains the complete sanitized provider response rather than only a summary.

Outputs:

```text
Reports\<solution>\sentinel-xdr-migration\migration-report.json
Reports\<solution>\sentinel-xdr-migration\migration-report.html
```

## Deploy Custom Detections

Deployment uses the documented Microsoft Graph beta Custom Detection API. The
API is preview and requires delegated `CustomDetection.ReadWrite.All` consent
plus an appropriate Defender XDR or Entra security role.

Authenticate once:

```powershell
sentinel-xdr-migration setup-deployment --tenant-id "<tenant-id>"
```

This uses Azure CLI browser authentication by default. Device-code and direct
browser credential flows are also available:

```powershell
sentinel-xdr-migration setup-deployment `
  --tenant-id "<tenant-id>" `
  --auth-method browser
```

Deploy every structurally valid, fully converted detection:

```powershell
sentinel-xdr-migration deploy --solution "Solutions\<solution>"
```

Rules are always submitted as disabled. The command creates missing rules,
updates matching client-provided IDs, and writes
`Reports\<solution>\sentinel-xdr-migration\deployment.graph.json`.

Use `--overwrite` to replace previously generated files. Without it, the
converter refuses to overwrite a file whose content differs.

## Optional migration configuration

Create `Reports/<solution>/sentinel-xdr-migration/migration-config.yaml` when a solution needs explicit
table, function, or column rewrites:

```yaml
schemaVersion: 1.0.0
tableMappings:
  LegacyTable_CL: CurrentTable_CL
functionMappings:
  LegacyParser: CurrentParser
columnMappings:
  LegacyTable_CL:
    UserName: AccountUpn
```

Mappings are applied token-by-token. Time-column handling is table-aware:
native Defender tables use `Timestamp`, while verified Sentinel workload
tables such as `AzureActivity` retain `TimeGenerated`. Rewrites skip quoted
strings and line comments. Runtime validation is authoritative for tables and
KQL constructs exposed through the unified Advanced Hunting surface.

Entity mappings are checked against columns plausibly produced by `project`,
`extend`, `summarize`, `distinct`, `parse`, and `mv-expand`. The analyzer
deliberately over-approximates output rather than blocking queries it cannot
prove invalid. High-confidence Account, Host, IP, URL, and Azure resource
columns can be repaired or inferred when source mappings are incomplete.

The generated file declares `resourceType:
Microsoft.Security/detectionRules`. A later packaging milestone can consume
this field and the `apiVersion`/`properties` block without reinterpreting the
source analytic rule.

## Agent skills

Repository-native skills under `.github/skills/` teach compatible agents how
to invoke this utility:

- `sentinel-xdr-end-to-end-orchestrator`
- `sentinel-xdr-rule-converter`
- `sentinel-xdr-detection-validator`
- `sentinel-xdr-migration-orchestrator`
- `sentinel-xdr-solution-packager`
- `sentinel-xdr-solution-deployer`
- `sentinel-xdr-alert-parity-validator`

The repository also provides one user-facing custom agent:

```text
.github/agents/sentinel-xdr-migration.agent.md
```

Select **Sentinel XDR Migration** from the host's agent picker. The agent uses
the top-level orchestrator skill, which delegates to the specialist skills
while the CLI remains the source of deterministic behavior and persisted
workflow state.

The skills call the CLI through the agent's normal terminal tools. They contain
no credentials and do not host a custom MCP server.

The canonical agent-neutral contract is:

```text
Tools\SentinelToXDRMigration\agent-workflows\end-to-end-migration.md
```

Thin adapters are provided for:

- generic agents through `AGENTS.md`;
- GitHub Copilot through `.github\agents` and `.github\skills`;
- Claude Code through `CLAUDE.md` and
  `.claude\skills\sentinel-xdr-migration\SKILL.md`;
- Cursor through `.cursor\rules\sentinel-xdr-migration.mdc`; and
- Windsurf through `.windsurf\rules\sentinel-xdr-migration.md`.

All adapters point to the same workflow and deterministic CLI. They must not
fork the stage definitions or make optional qualification mandatory.

Microsoft's official Sentinel Triage MCP can optionally provide Advanced
Hunting schema and execution tools:

`https://sentinel.microsoft.com/mcp/triage`

It is not required. The utility remains usable without MCP, and missing runtime
access never blocks offline conversion or structural validation.

## Logging

Runtime logs and reports are written below `Data/`:

- `Data/logs/sentinel-xdr-migration.log`
- `Data/reports/last-conversion.json`
- `Data/reports/last-advanced-hunting-validation.json`

These files are local execution artifacts and are ignored by Git.

## Tests

```powershell
python -m unittest discover -s Tools\SentinelToXDRMigration\tests -p "test_*.py"
```

## Planned milestones

- workbook conversion;
- solution migration dashboard;
- optional retrieval-assisted guidance for schemas, prior art, and historical
  findings.
