# Akamai Guardicore — solution tests

Self-contained structural / regression tests for this solution. They use only the
Python standard library (`unittest`) — no `pip install` needed.

## Run

From the repo root (or anywhere):

```bash
python3 -m unittest discover -s "Solutions/Akamai Guardicore/Tests" -v
# or
python3 "Solutions/Akamai Guardicore/Tests/test_solution.py"
```

## What they guard

| Test group | Invariant / bug guarded                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `TestJsonIsValid` | Every `*.json` in the solution parses.                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `TestNoWorkspaceNamePlaceholder` | No unresolved `{{workspaceName}}` token in the CCF connector files or `mainTemplate.json` — the v3.0.0 defect that 404'd table creation.                                                                                                                                                                                                                                                                                                                 |
| `TestTableNamesAreBare` | The four CCF `_CL` tables use bare resource names in both the source `_Tables.json` and `mainTemplate.json`. (Playbook tables that use `concat(parameters('WorkspaceName'), …)` are intentionally allowed.)                                                                                                                                                                                                                                              |
| `TestNoVersionSelector` | The `centraVersion` dropdown and its `type: array` parameter are fully removed from `mainTemplate.json` — a dangling `centraVersion` reference with no parameter declaration is exactly what produced the earlier `InvalidTemplate` failure, so no `centraVersion` text and no `Dropdown` control may remain.                                                                                                                                            |
| `TestPaging` | Per-endpoint paging is correct. Positive: each poller carries the exact `(offsetParaName, pageSizeParaName, pageSize)` its endpoint needs — the v4.0 `/workflow/projects` poller uses `offset`/`limit` capped at 1000, the three v3.0 pollers use `offset`/`limit` at 1000. Negative: no poller retains version-conditional paging (`centraVersion`, `if(equals`), and the v4.0 projects poller never regresses to `offset`/`limit` or a >100 page size. |
| `TestVersionConsistency` | `_solutionVersion`, `dataConnectorCCPVersion`, the solution manifest `Version`, and a `ReleaseNotes.md` row all match the current version; every `contentSchemaVersion` stays fixed at `3.0.0`.                                                                                                                                                                                                                                                          |
| `TestPackageZipParity` | `Package/<version>.zip` byte-matches the loose `mainTemplate.json` + `createUiDefinition.json`, and no stale version zips linger.                                                                                                                                                                                                                                                                                                                        |
| `TestSourcePackageConsistency` | The CCF source files (`*_ConnectorDefinition.json`, `*_PollingConfig.json`) carry no version `Dropdown` and the same single-version, per-endpoint paging as the packaged `mainTemplate.json`, so re-running the packaging tool reproduces the working template.                                                                                                                                                                                          |
