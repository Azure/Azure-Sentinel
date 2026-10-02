---
name: sentinel-xdr-rule-converter
description: Convert every Microsoft Sentinel analytic rule in a solution into a Defender XDR Custom Detection YAML under the solution's XDR Detections folder.
---

# Convert Sentinel analytic rules to XDR Detection YAML

Run the CLI from the repository root:

```powershell
python -m sentinel_xdr_migration.cli <command>
```

If the package is not installed, first run:

```powershell
python -m pip install -e Tools\SentinelToXDRMigration
```

## Inputs

- The path to one solution folder under `Solutions/`.
- Optional table, function, and column mappings.

## Workflow

1. Run `sentinel-xdr-migration doctor`.
2. If `firstRun` is true, run
   `sentinel-xdr-migration setup --non-interactive`. Continue offline when
   authentication is unavailable.
3. Run:

   ```powershell
   sentinel-xdr-migration inspect --solution "<solution-path>"
   ```

4. Review the analytic-rule count and source paths.
5. If deterministic rewrites are needed, create
   `Reports/<solution>/sentinel-xdr-migration/migration-config.yaml`.
6. Run:

   ```powershell
   sentinel-xdr-migration convert --solution "<solution-path>"
   ```

7. Do not overwrite conflicting generated files without explicit approval.
8. Report:
   - converted count;
   - needs-review count;
   - conflicts;
   - every warning and error;
   - the generated
     `Reports/<solution>/sentinel-xdr-migration/transformation-report.html`
     path.

The converter must not modify `Analytic Rules` or `Package/mainTemplate.json`.
Generated detections must remain disabled.
`XDR Detections` must contain detection YAML only.
