# Claude Code instructions

For Microsoft Sentinel-to-Defender-XDR migration or authoring work, first read:

`Tools\SentinelToXDRMigration\agent-workflows\end-to-end-migration.md`

Follow that canonical workflow and use the repository CLI and PowerShell
entry points directly. Do not replace deterministic conversion, validation,
packaging, deployment, or parity logic with model-generated approximations.

Default to `authoring`. Ask before optional lab `qualification`; it is not
required for ISV publishing. Use V4 when packaging XDR Detections and V3 only
for legacy Sentinel-only packages. Resume from `workflow-state.json`, preserve
disabled detections, and request explicit approval before writes.
