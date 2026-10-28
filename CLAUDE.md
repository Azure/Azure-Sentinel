# Claude Code instructions

For Microsoft Sentinel-to-Defender-XDR migration or authoring work, first read:

`Tools\SentinelToXDRMigration\agent-workflows\end-to-end-migration.md`

Follow that canonical workflow and use the repository CLI and PowerShell
entry points directly. Do not replace deterministic conversion, validation,
packaging, deployment, or parity logic with model-generated approximations.

Default to `qualification`, with `--workflow-profile authoring` available as an
explicit offline/ISV fallback when no live lab is available. Use V3.1 through
`package-v3-1` for Sentinel and XDR solution packages. Resume from
`workflow-state.json`, preserve disabled detections, and request explicit
approval before writes.
