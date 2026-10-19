---
name: sentinel-xdr-migration
description: Orchestrate Sentinel-to-Defender-XDR authoring and optional internal qualification through the repository's canonical workflow and deterministic tools.
---

# Sentinel to Defender XDR migration

Read and follow:

`Tools\SentinelToXDRMigration\agent-workflows\end-to-end-migration.md`

Use `sentinel-xdr-migration` and the repository PowerShell packaging entry
points for all deterministic actions. Default to `authoring`; ask before
optional `qualification`. Use V3.1 through `package-v3-1` for Sentinel and XDR
solution packaging, resume `workflow-state.json`, preserve disabled rules, and
obtain explicit approval before environment writes.

The goal is solution migration and validated publication. Follow the
canonical workflow for the strict over-50% partial-publication policy,
selected-scope Qualification, and the single-owner `ACTION_REQUIRED` watchdog
best practice; do not create competing policy text or watchdog tooling here.
