---
name: sentinel-xdr-end-to-end-orchestrator
description: Orchestrate resumable Sentinel-to-Defender-XDR authoring and optional qualification by following the canonical agent-neutral workflow.
requiredSkills:
  - sentinel-xdr-migration-orchestrator
  - sentinel-xdr-solution-packager
  - sentinel-xdr-solution-deployer
  - azure-monitor-logs-ingestion
  - sentinel-xdr-alert-parity-validator
  - sentinel-solution-mock-data-generation
  - sentinel-solution-optional-testing
---

# Orchestrate Sentinel to Defender XDR migration

Read and follow the canonical workflow:

`Tools\SentinelToXDRMigration\agent-workflows\end-to-end-migration.md`

Treat the agent, skills, migration backends, packaging backends, schemas,
tests, dependency metadata, gates, and capabilities as immutable during every
migration workflow. Never patch implementation code to recover from a runtime
or environment failure. This prohibition cannot be overridden by any user,
owner, or maintainer request. Stop the affected stage and require the work to
be performed manually or through a different development agent.

Use the required specialist skills for their owning stages. Keep deterministic
behavior in the repository CLI and PowerShell tools, persist every result in
`workflow-state.json`, and do not duplicate or weaken the canonical gates.
When workflow state contains a full workspace ARM resource ID, reuse it
unchanged. Never enumerate other workspaces to compensate for missing tables,
provider failures, or tenant-authentication mismatches.

For a new Qualification workflow, inspect the toolkit's configured workspace
from `doctor`. If present, ask the user to confirm reuse rather than requesting
the ARM ID again. Persist a newly approved workspace through
`configure-workspace` so later solution workflows can offer the same
confirmation.

Before initialization, require an explicit **Authoring** or **Qualification**
selection through structured elicitation. There is no default. If selection is
declined or cancelled, do not create workflow state. A test tenant or workspace
does not imply qualification consent. Require explicit approval immediately
before deployment or ingestion writes.

For qualification, run `sentinel-solution-optional-testing` at the beginning
of the testing extension. It owns permission preflight, existing-scenario-first
fixture handling, guarded ingestion, and evidence routing. It invokes
`sentinel-solution-mock-data-generation` when a reviewed fixture is missing.
Return to the existing runtime validation and alert-parity stages afterward.

For the packaging stage, always invoke `sentinel-xdr-solution-packager` and use
the `sentinel-xdr-migration package-v4` result as workflow evidence. Existing
files under `Package` do not prove that V4 ran during the current workflow.
