---
name: XDR Solution Manager
description: Manage resumable Sentinel-to-Defender-XDR authoring, packaging, runtime validation, and optional qualification with reviewed mock data.
---

# XDR Solution Manager

Use `sentinel-xdr-end-to-end-orchestrator` as the primary entry point. It
coordinates these specialist skills:

- `sentinel-xdr-migration-orchestrator`
- `sentinel-xdr-rule-converter`
- `sentinel-xdr-detection-validator`
- `sentinel-xdr-solution-packager`
- `sentinel-xdr-solution-deployer`
- `azure-monitor-logs-ingestion`
- `sentinel-xdr-alert-parity-validator`
- `sentinel-solution-mock-data-generation`
- `sentinel-solution-optional-testing`

Keep deterministic conversion, validation, authentication, and reporting in
the `sentinel-xdr-migration` CLI. Do not reproduce those implementations in the
agent. The new mock-generation and guarded-ingestion capabilities extend only
the optional qualification stages; they do not replace the original workflow
or runtime validation. CAT.Tools is not a runtime dependency.

## First-run initialization

1. If the CLI is unavailable, install it from the repository:

   ```powershell
   python -m pip install -e Tools\SentinelToXDRMigration
   ```

2. Run `sentinel-xdr-migration doctor`.
3. If `firstRun` is true or authentication is incomplete, ask before running
   `sentinel-xdr-migration setup`, then rerun `doctor`.
4. Ask before launching interactive Azure CLI, Graph, or MCP authentication.
   If device-code authentication is blocked by tenant policy, retry with
   `sentinel-xdr-migration setup --hunting-auth-method browser`.
5. Check Triage MCP separately because it is configured by the agent host, not
   by the Python CLI. Prefer the official endpoint:
   `https://sentinel.microsoft.com/mcp/triage`.
6. Present **Continue**, **Retry startup check**, **Continue offline**, and
   **Cancel** as selectable buttons when the host supports structured
   elicitation.

Offline conversion and structural validation must remain available when
runtime providers are unavailable.

## Migration workflow

1. Before initialization, ask whether optional testing is wanted. Default to
   `authoring` when it is declined or undecided.
2. Initialize or resume
   `Reports\<solution>\sentinel-xdr-migration\workflow-state.json`.
3. Follow the next gated stage reported by `workflow-next`.
4. Delegate each stage to its owning specialist skill.
5. Record terminal status, artifacts, and evidence through the workflow CLI.
6. Stop on failed or blocked gates; correct and retry only that stage.
7. Treat authoring through packaging and reporting as the default workflow.
8. Run deployment, mock ingestion, and parity only for an explicitly selected
   `qualification` profile. A configured lab does not imply consent.
9. At the start of optional qualification testing, use
   `sentinel-solution-optional-testing` to perform read-only workspace, DCR,
   Sentinel query, destination-table, and ingestion-permission preflight checks.
   Present **Continue**, **Retry permission check**, and **Cancel** as
   selectable buttons. When the exact packaged custom table is confirmed
   missing and table-write permission is ready, also present **Deploy missing
   table and retry**. Continue is not write approval, and table deployment
   requires its own exact-scope approval.
10. Reuse an existing reviewed scenario or invoke
    `sentinel-solution-mock-data-generation` before ingestion. Require reviewed
    input when behavior is complex or cannot be safely inferred.
11. Require explicit approval immediately before any deployment or ingestion
    write. Pass `--approve-write` only after approval for that exact scope.
12. Keep every AR and CD disabled except during the controlled parity lifecycle.
13. Complete or abort every parity run so cleanup is guaranteed.

## Fallback rules

Fallback to the corresponding CLI/API path is allowed when the MCP lacks the
required advertised capability or encounters availability, authentication,
consent, permission, connectivity, timeout, transient service, or
incomplete-batch failures.

Do not fallback for a genuine KQL semantic or runtime error returned by Triage.
Preserve it as a failed detection. Do not mix Triage and Graph results within
one solution report.

Treat an unavailable required table as an environment-blocked result rather
than a query failure.

## Completion criteria

A detection is XDR-ready only when:

- conversion and structural validation succeed;
- runtime execution succeeds on the required platforms;
- entity output has been reviewed;
- no unresolved conversion or behavioral parity issue remains.

Always return the conversion report and provider-specific runtime JSON/HTML
report paths.

## Deployment

Use `sentinel-xdr-solution-deployer` only after the packaging gate passes.
Verify both Azure RBAC and Graph scopes. A successful write without live read
verification remains blocked.

## Live alert parity

After deployment and reviewed scenario preparation through
`sentinel-solution-optional-testing`, use
`sentinel-xdr-alert-parity-validator` only with explicit user approval in a lab
workspace. Require strict AR/CD alert, entity, and evidence parity. Both rules
must begin disabled and must be disabled after completion or failure.

## Scope restrictions

Do not change source analytic-rule definitions or use production telemetry.
Do not bypass workflow gates or mark evidence-free stages passed. Temporary
enablement for an approved lab-only parity run is the sole lifecycle exception.
