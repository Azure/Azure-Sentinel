---
applyTo: "**/*.ps1"
---

- This project uses PowerShell 7.0+ with strict mode (`$ErrorActionPreference = 'Stop'`).
- All Azure REST calls go through the `Invoke-ArmRequest` helper using ARM bearer tokens from `Get-ArmToken`.
- The script supports both interactive and non-interactive (`-NonInteractive`) modes.
- Use `#Requires` statements for module/version dependencies, not inline checks.
- Avoid comments in code unless explaining complex algorithms.
- Use `Write-Step`, `Write-Info`, `Write-Ok`, `Write-Warn2`, `Write-Err` for user-facing output — never raw `Write-Host` for status.
- Return structured `[PSCustomObject]` results to the pipeline.
- Export CSV with `-NoTypeInformation -Encoding UTF8`.
