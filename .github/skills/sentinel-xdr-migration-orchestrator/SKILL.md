---
name: sentinel-xdr-migration-orchestrator
description: Orchestrate conversion of a Microsoft Sentinel solution into Defender XDR Custom Detection YAML by using repository utilities and available runtime providers.
requiredSkills:
  - sentinel-xdr-rule-converter
  - sentinel-xdr-detection-validator
---

# Migrate a Microsoft Sentinel solution to XDR Detection YAML

## Scope

This milestone creates and validates `XDR Detections/*.yaml`.

It does not:

- generate or modify ARM templates;
- deploy analytic rules or Custom Detections;
- generate or ingest mock data;
- convert workbooks;
- compare generated alerts.

## Workflow

1. If the package is unavailable, install it from the repository:

   ```powershell
   python -m pip install -e Tools\SentinelToXDRMigration
   ```

2. Run `sentinel-xdr-migration doctor`.
3. If `firstRun` is true, run
   `sentinel-xdr-migration setup --non-interactive`.
4. Inspect the official Triage MCP capabilities. Prefer its advertised tools
   for every supported runtime query operation, including
   `RunAdvancedHuntingQuery`. This check is separate from `doctor`, because MCP
   authentication belongs to the agent host rather than the Python CLI.
5. Ask before launching interactive CLI or MCP sign-in. Continue with offline
   conversion if authentication is declined or unavailable.
6. Confirm the solution path.
7. Use `sentinel-xdr-rule-converter`; conversion always runs locally and does
   not depend on MCP.
8. Review every `needsReview` result. Never present it as XDR-ready.
9. Use `sentinel-xdr-detection-validator`. Prefer Triage MCP for supported
   original Sentinel and Advanced Hunting queries. Fall back to Log Analytics
   CLI/API for Sentinel queries and the Graph CLI for Advanced Hunting only
   when the MCP lacks the capability or has a provider-level failure, never
   for genuine KQL failures.
10. Report:
   - source analytic rules;
   - generated detection files;
   - deterministic rewrites;
   - provenance status;
   - Sentinel and Advanced Hunting execution status;
   - unresolved parity gaps.

An XDR-ready result requires valid YAML, no conversion errors, successful
runtime execution on both platforms, and reviewed entity mappings.
