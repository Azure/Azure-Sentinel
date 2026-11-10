# Sentinel to Defender XDR migration

When working on Sentinel-to-Defender-XDR migration, XDR Detection authoring,
hybrid packaging, or AR/CD qualification, read and follow:

`Tools\SentinelToXDRMigration\agent-workflows\end-to-end-migration.md`

Treat it as the canonical process. Use repository CLI and PowerShell tools,
not prompt-only implementations. Default to `qualification`, with
`--workflow-profile authoring` available as an explicit offline/ISV fallback
when no live lab is available. Use V3.1 through `package-v3-1` for Sentinel and
XDR solution packages, preserve disabled lifecycle state, resume
`workflow-state.json`, and obtain explicit approval before environment writes.
