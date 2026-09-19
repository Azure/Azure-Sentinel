---
name: sentinel-xdr-migration
description: Orchestrate Sentinel-to-Defender-XDR authoring and optional internal qualification through the repository's canonical workflow and deterministic tools.
---

# Sentinel to Defender XDR migration

Read and follow:

`Tools\SentinelToXDRMigration\agent-workflows\end-to-end-migration.md`

Use `sentinel-xdr-migration` and the repository PowerShell packaging entry
points for all deterministic actions. Default to `authoring`; ask before
optional `qualification`. Use V4 for XDR Detection packaging, resume
`workflow-state.json`, preserve disabled rules, and obtain explicit approval
before environment writes.
