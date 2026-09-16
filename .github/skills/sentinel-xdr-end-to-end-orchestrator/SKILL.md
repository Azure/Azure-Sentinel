---
name: sentinel-xdr-end-to-end-orchestrator
description: Orchestrate resumable Sentinel-to-Defender-XDR authoring and optional qualification by following the canonical agent-neutral workflow.
requiredSkills:
  - sentinel-xdr-migration-orchestrator
  - sentinel-xdr-solution-packager
  - sentinel-xdr-solution-deployer
  - azure-monitor-logs-ingestion
  - sentinel-xdr-alert-parity-validator
---

# Orchestrate Sentinel to Defender XDR migration

Read and follow the canonical workflow:

`Tools\SentinelToXDRMigration\agent-workflows\end-to-end-migration.md`

Use the required specialist skills for their owning stages. Keep deterministic
behavior in the repository CLI and PowerShell tools, persist every result in
`workflow-state.json`, and do not duplicate or weaken the canonical gates.

Default to `authoring`. Ask before selecting optional `qualification`; a test
tenant or workspace does not imply consent. Require explicit approval
immediately before deployment or ingestion writes.
