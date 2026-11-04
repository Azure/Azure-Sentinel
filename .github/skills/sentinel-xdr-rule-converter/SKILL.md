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
   `Solutions/<solution>/Logs/sentinel-xdr-migration/<run-id>/migration-config.yaml`.
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
     `Solutions/<solution>/Logs/sentinel-xdr-migration/<run-id>/transformation-report.html`
     path.

## Best-effort entity mapping

Do not stop a batch or ask for a per-rule decision solely because a Sentinel
entity identifier has no exact Defender XDR mapping. Select the best supported
mapping from the source identifiers and columns actually emitted by the query,
preserve the original value as an alert `customDetails` output-column binding,
and mark the assumption for human review in conversion provenance. For example,
an available `Host.FullName` may be provisionally mapped to the supported
`hosts.nameColumn`; keep the original output column in custom details and
explicitly state that this is an assumption, not proven host identity or parity.
Prefer a directly supported matching identifier when present; never invent a
projected column, unsupported Graph field, or data transformation.

Best-effort entity review is nonblocking for conversion, structural validation,
and read-only runtime query/schema tests, so large batches can continue without
per-rule pauses. It remains visibly pending and hash-bound to the source and
converted query. It is not an acceptance or review decision and does not clear
other findings. Missing/projected-away values, conflicting bindings, custom
detail limits, malformed content, or other technical/KQL failures retain their
normal errors and gates. Do not package or deploy content with unresolved
review flags; query execution and preserved custom details do not prove entity
correlation or alert parity.

The converter must not modify `Analytic Rules` or `Package/mainTemplate.json`.
Generated detections must remain disabled.
`XDR Detections` must contain detection YAML only.

New detections receive an independent top-level `version: 3.1.0`; source
Sentinel versions remain unchanged in `contentProvenance.source.version`.
The XDR release must be a `major.minor.patch` string in `[3.1.0, 4.0.0)`.
Regeneration preserves a valid existing XDR version for the same source rule,
including with `--overwrite`. Invalid versions or mismatched source identities
are conflicts and must not be silently reset. Older YAML without its own version
fails validation/packaging; after reviewing manual edits and obtaining overwrite
approval, reconvert with `--overwrite` to initialize `3.1.0`, or explicitly author
the independent XDR version. Do not change schema/API versions or source AR
versions to satisfy the XDR release bounds.
