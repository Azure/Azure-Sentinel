# Session Artifacts — 2026-04-30

Everything specific to the session that diagnosed and fixed the connector
↔ parser/content-item over-association regression. Kept here so it doesn't
pollute the regular tool outputs in `Tools/Solutions Analyzer/`.

**Start here:** [`RESUME-SESSION.md`](RESUME-SESSION.md) — branch / HEAD / PR
references, summary of fixes, file inventory, verification commands, and
outstanding work.

## Contents

| File | Purpose |
|---|---|
| `RESUME-SESSION.md` | Full session-resume notes — read first after a reboot. |
| `selection-criteria.md` | Linked index of every selection-criteria predicate across connectors / parsers / ASIM parsers / content items, with hyperlinks into the `sentinelninja/Solutions Docs/` entity pages. |
| `selection-criteria-association-impact.md` | Per-association block report comparing `associated_connectors` for every ASIM parser and content item between HEAD and the regenerated CSVs. **Final after the parser-call inheritance fix: +74 / −28 ASIM rows; +33 / −285 content rows** (down from +520 / −11 and +608 / −293). |
| `build_selection_criteria.py` | Regenerates `selection-criteria.md` from the CSVs. |
| `build_association_impact.py` | Regenerates `selection-criteria-association-impact.md`. By default reads BEFORE from `git show HEAD:` and AFTER from the working tree; override with `--before-ref` or `--before-dir`. |
| `probe-link.md` | Tiny probe used to validate that markdown links to file paths containing spaces survive the doc generator's HTML conversion (both `<...>`-quoted and percent-encoded forms). |
| `fix-run.log` | Mapper run log from the first verification run after the parser-call inheritance fix. |
| `force-refresh-run.log` | Mapper run log from `--force-refresh=all-offline` rerun. |
| `parser-fix-run.log` | Mapper run log captured by `Tee-Object` during the final verification rerun. |

## Reproducing the reports

```pwsh
cd "C:\Users\ofshezaf\GitHub\Azure-Sentinel\Tools\Solutions Analyzer\.session-2026-04-30"
python build_selection_criteria.py
python build_association_impact.py
```

The rebuilt ASIM-parser numbers match the originals exactly (260 → 306, +74 / −28).
The rebuilt connector and content-item counts may differ slightly because the
original session helper had additional filtering (e.g. excluding deprecated
connectors from the connector listing and solution-bundled rows from the content
diff); per-block content is semantically identical.

## Disposable?

Yes — these are diagnostic outputs, not deliverables. They can be deleted once the
PR with the mapper changes is merged and the impact has been confirmed against the
regenerated `sentinelninja` docs. The two `build_*.py` scripts can be re-run any
time the CSVs change.
