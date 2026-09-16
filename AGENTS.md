# Repository agent instructions

When a request involves Sentinel-to-Defender-XDR migration, XDR Detections,
hybrid solution packaging, or AR/CD qualification:

1. Read and follow
   `Tools\SentinelToXDRMigration\agent-workflows\end-to-end-migration.md`.
2. Treat that file as the canonical workflow; do not redefine its stages or
   gates in this adapter.
3. Keep deterministic work in the repository Python and PowerShell tools.
4. Default to the `authoring` profile.
5. Ask before selecting optional `qualification`; deployment, mock ingestion,
   and alert parity are not ISV publishing requirements.
6. Use packaging V4 for XDR Detections. V3 is Sentinel-only.
7. Resume from `workflow-state.json` and record artifacts and evidence.
8. Require explicit approval immediately before any environment write.
