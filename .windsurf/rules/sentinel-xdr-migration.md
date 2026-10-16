# Sentinel to Defender XDR migration

When working on Sentinel-to-Defender-XDR migration, XDR Detection authoring,
hybrid packaging, or AR/CD qualification, read and follow:

`Tools\SentinelToXDRMigration\agent-workflows\end-to-end-migration.md`

Treat it as the canonical process. Use repository CLI and PowerShell tools,
not prompt-only implementations. Default to authoring and ask before optional
qualification. Deployment, mock ingestion, and parity are not required for
ISV publishing. Use packaging V4 for XDR Detections, preserve disabled
lifecycle state, resume `workflow-state.json`, and obtain explicit approval
before environment writes.
