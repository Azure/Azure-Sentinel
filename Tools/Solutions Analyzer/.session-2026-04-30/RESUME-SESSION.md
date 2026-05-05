# Resume Session — Solutions Analyzer

This file captures everything needed to pick up the in-flight work after a reboot. The
conversation that produced these changes targeted **selection-criteria-driven connector ↔
parser/content-item association** in the mapper, plus reporting + docs around it.

## Where you left off

- **Branch:** `tools/solutions-analyzer/telemetry`
- **HEAD at handoff:** `698b96a`
- **Active PR:** [#14140 — Solutions Analyzer v7.9 → v9.6](https://github.com/Azure/Azure-Sentinel/pull/14140) (now drafting v9.8 changes)
- **Repo:** `c:\Users\ofshezaf\GitHub\Azure-Sentinel`
- **Docs output repo (sibling):** `c:\Users\ofshezaf\GitHub\sentinelninja\` (`Solutions Docs/` subfolder)
- **CSV output worktree:** `C:\Users\ofshezaf\GitHub\Azure-Sentinel-solution-analyzer-output\Tools\Solutions Analyzer` (branch `tools/solutions-analyzer/output`)

All changes are **uncommitted** in the Azure-Sentinel working tree — verify with
`git status --short "Tools/Solutions Analyzer/"`.

> This file lives in [`Tools/Solutions Analyzer/.session-2026-04-30/`](./) — the
> folder collecting all session-specific intermediary files (impact reports,
> ad-hoc probes, run logs, and the rebuild scripts that produced the reports).
> See [`README.md`](README.md) for the inventory.

## What was done in this session

Three related fixes in [`map_solutions_connectors_tables.py`](../map_solutions_connectors_tables.py),
all motivated by spurious connector ↔ parser/content-item associations on
`CommonSecurityLog` and similar shared tables:

1. **CCF v3 envelope query extraction** — `extract_all_queries_from_connector` now also
   scans `properties.connectorUiConfig` and `resources[*].properties.connectorUiConfig`,
   and accepts both `connectivityCriteria` (CCF v3 singular) and `connectivityCriterias`
   (legacy plural). Without this, CCF v3 connectors yielded no `filter_fields`.

2. **Deprecated connectors no longer skipped during association** —
   `associate_connectors_to_items` no longer drops `is_deprecated=true` connectors before
   matching. They still keep their flag, but reappear as `associated_connectors` for
   targets whose criteria they satisfy (e.g. `SentinelOne` ↔ `ASimAuthenticationSentinelOne`).

3. **Connector filter inheritance from parser-function calls** — when a connector's
   query is just a parser-function name (`ClarotyEvent`, `CiscoSEGEvent`, `IllumioCoreEvent`,
   `OSSECEvent`, `NetwrixAuditor`, etc.), `get_connector_filter_fields` now resolves the
   leading identifier against a `parser_filter_map` (built from `parsers.csv` +
   `asim_parsers.csv`, with ASIM `equivalent_builtin` aliases) and inherits the parser's
   `filter_fields` predicates onto the connector. This was the dominant source of false
   positives.

### Measured impact (after rerun)

| Metric | Before | After |
|---|---|---|
| ASIM-parser `associated_connectors` delta vs HEAD | +520 / −11 | **+74 / −28** |
| Content-item `associated_connectors` delta vs HEAD | +608 / −293 | **+33 / −285** |
| Impact-report file size | ~781 KB | ~262 KB |

Verified that `Claroty`, `CiscoSEG`, `IllumioCore`, `OSSEC`, `Netwrix`, `Barracuda`,
`FireEyeNX` etc. now publish proper `filter_fields` in `connectors.csv`.

## Files touched

All paths below are relative to this file (`Tools/Solutions Analyzer/.session-2026-04-30/`).

| Path | Status | Reason |
|---|---|---|
| [`../map_solutions_connectors_tables.py`](../map_solutions_connectors_tables.py) | modified | The 3 fixes above |
| [`../connectors.csv`](../connectors.csv) and the other CSVs in `Tools/Solutions Analyzer/` | regenerated | After mapper rerun |
| [`selection-criteria.md`](selection-criteria.md) | new (in this folder) | Linked index of all selection criteria across connectors / parsers / ASIM / content |
| [`selection-criteria-association-impact.md`](selection-criteria-association-impact.md) | new (in this folder) | Per-association block layout showing added/removed associations vs HEAD with side-by-side filter columns |
| [`build_selection_criteria.py`](build_selection_criteria.py) | new (in this folder) | Rebuild script for `selection-criteria.md` |
| [`build_association_impact.py`](build_association_impact.py) | new (in this folder) | Rebuild script for `selection-criteria-association-impact.md` (BEFORE snapshot via `git show HEAD:`) |
| [`probe-link.md`](probe-link.md) | new (in this folder) | Tiny probe used to validate markdown angle-bracket vs percent-encoded relative links |
| `*.log` (this folder) | new (in this folder) | Mapper run logs (`fix-run.log`, `force-refresh-run.log`, `parser-fix-run.log`) |
| [`../script-docs/map_solutions_connectors_tables.md`](../script-docs/map_solutions_connectors_tables.md) | modified | New "Pass 8 — parser-call inheritance" item under Filter Fields Detection; CCF v3 envelope note in Detection Sources; Exclusions updated for deprecated handling |
| [`../script-docs/csv/connectors.md`](../script-docs/csv/connectors.md) | modified | `filter_fields` now mentions parser-function inheritance |
| [`../README.md`](../README.md) | modified | v9.8 changelog: parser-call inheritance, CCF v3 envelopes, deprecated-connector association behavior |
| [`../../../.github/skills/run-solution-analyzer/SKILL.md`](../../../.github/skills/run-solution-analyzer/SKILL.md) | modified | Earlier in session — Tee-Object pipeline-buffering tip for watching mapper progress |

`compare_runs.py` and `script-docs/compare_runs.md` are also untracked from the same
session series — those are intended to be **committed** as a new tool, not moved into
the session folder.

## Key code locations

- `extract_all_queries_from_connector` — CCF v3 envelope traversal (~line 1448)
- `associate_connectors_to_items` — deprecation-skip removed (~line 1872)
- `get_connector_filter_fields` — `parser_filter_map: Optional[Dict[str, str]] = None`
  parameter; **third pass** parses `Parser | <Table>.<Field> <op> "<value>"` predicates
  per query when the leading identifier is a known parser (~line 1589)
- `parser_filter_map` construction in `main()` — runs after `collect_all_parsers_detailed(...)`,
  populated from `all_parser_records` + `asim_parser_records` (lowercased
  `parser_name → filter_fields_str`, with `equivalent_builtin` aliases via `setdefault`)
- Call site: `ff = get_connector_filter_fields(data, known_tables, parser_filter_map)`
  (~line 8642)

## How to verify quickly

```pwsh
cd "C:\Users\ofshezaf\GitHub\Azure-Sentinel\Tools\Solutions Analyzer"
. ..\..\.venv\Scripts\Activate.ps1
python -c "
import csv
conns = {r['connector_id']: r for r in csv.DictReader(open('connectors.csv', encoding='utf-8'))}
for cid in ['Claroty','CiscoSEG','IllumioCoreCef','OSSEC','Netwrix','Barracuda','FireEyeNX']:
    if cid in conns:
        print(cid, '->', conns[cid].get('filter_fields','') or '(empty)')
"
```

Each connector should print a non-empty `filter_fields` containing the inherited
`CommonSecurityLog.DeviceVendor =~ "..."` (or similar) predicate.

## Outstanding work

1. **Commit & push** the mapper change + regenerated CSVs + doc updates on
   `tools/solutions-analyzer/telemetry`. Suggested message:
   `mapper: connector filter inheritance from parser calls + CCF v3 envelopes + keep deprecated connectors in associations (v9.8)`.
2. **Regenerate sentinelninja docs** (so entity pages reflect the new connector
   `filter_fields` and corrected associations):
   ```pwsh
   cd "C:\Users\ofshezaf\GitHub\Azure-Sentinel\Tools\Solutions Analyzer"
   python generate_connector_docs.py `
     --output-dir "C:\Users\ofshezaf\GitHub\sentinelninja\Solutions Docs" `
     --skip-input-generation `
     --html-output-dir "C:\Users\ofshezaf\GitHub\sentinelninja" `
     --html-docs-path "Solutions Docs/" `
     --html-index-url "https://oshezaf.github.io/sentinelninja/index.html"
   ```
   Then `git add -A && git commit && git push` in the sentinelninja repo.
3. **Cosmetic residuals** (low priority — not blocking):
   - `ASimAuditEventAWSCloudTrail ↔ AWS` impact row shows `(none)` shared tables —
     `AWSCloudTrail` is missing from that connector's table mapping.
   - `ASimAuditEventCrowdStrikeFalconHost ↔ CrowdStrikeFalconEndpointProtection` shows an
     empty connector predicate — that connector's `baseQuery` may not be a recognized
     parser-function call.

## Reproducing the reports

Both `selection-criteria.md` and `selection-criteria-association-impact.md` are
regenerable from the CSVs via the rebuild scripts in this folder:

```pwsh
cd "C:\Users\ofshezaf\GitHub\Azure-Sentinel\Tools\Solutions Analyzer\.session-2026-04-30"
python build_selection_criteria.py
python build_association_impact.py    # BEFORE = git show HEAD: ; AFTER = working tree
```

`build_association_impact.py` accepts `--before-ref <commit>` or `--before-dir <path>`
to compare against a different snapshot. Note: the rebuilt connector / content-item
counts can differ slightly from the originals, because the original session helper had
extra filtering (e.g. excluding deprecated connectors and solution-bundled content
rows). The ASIM-parser counts match exactly (260 → 306, +74 / −28), and the per-block
content remains semantically identical.

## Resume checklist (paste into next chat)

> I'm resuming work on `Tools/Solutions Analyzer/`. Read
> `Tools/Solutions Analyzer/.session-2026-04-30/RESUME-SESSION.md` for full context.
> Branch is `tools/solutions-analyzer/telemetry`, HEAD `698b96a`, PR #14140. The
> mapper has 3 uncommitted fixes (CCF v3 envelopes, deprecated-connector association,
> parser-call filter inheritance) plus regenerated CSVs and updated docs. Next steps
> are: commit & push on Azure-Sentinel, then regenerate sentinelninja docs and commit
> there.
