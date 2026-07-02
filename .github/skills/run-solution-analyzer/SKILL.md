---
name: run-solution-analyzer
description: "Run the Solutions Analyzer scripts: mapper, documentation generator, ASIM browser. Use when: running solution analyzer, generating CSVs, generating docs, refreshing caches, force-refresh, invalidating caches, generating ASIM browser, running mapper, running collect_table_info, running collect_asim_fields."
---

# Run Solution Analyzer

This skill covers running the Solutions Analyzer locally against this clone of
Azure-Sentinel. Each script writes CSVs or docs to a directory you choose; the
scripts themselves are agnostic to where that directory lives.

If your workflow includes publishing the generated CSVs/docs to additional
repositories, GitHub Pages, or Kusto, those targets are user-specific and
should be recorded in agent memory (workspace or user scope) rather than in
this skill.

## Scripts Overview

| Script                               | Purpose                                                            | Invocation                                        |
| ------------------------------------ | ------------------------------------------------------------------ | ------------------------------------------------- |
| `map_solutions_connectors_tables.py` | Mapper: generates all CSV data                                     | Run directly                                      |
| `generate_connector_docs.py`         | Doc generator: markdown + HTML pages, static + interactive indexes | Run directly                                      |
| `generate_asim_browser.py`           | ASIM browser: interactive HTML schema browser                      | Run directly                                      |
| `upload_to_kusto.py`                 | Upload CSVs to Azure Data Explorer (Kusto) cluster                 | Run directly                                      |
| `collect_table_info.py`              | Fetch table reference data from Microsoft docs                     | Auto-invoked by mapper (`--force-refresh=tables`) |
| `collect_asim_fields.py`             | Fetch ASIM field/schema definitions from Microsoft docs            | Auto-invoked by mapper (`--force-refresh=asim`)   |
| `generate_interactive_docs.py`       | Generate `index.html` and HTML entity pages                        | Auto-invoked by `generate_connector_docs.py`      |

All scripts run from `Tools/Solutions Analyzer`.

## Default Output Location

By default the mapper writes CSVs into `Tools/Solutions Analyzer/` in the
current branch. The doc generator and ASIM browser require an explicit
`--output-dir` so they never pollute the source tree.

## Sync the Working Branch With `origin/master`

**Always do this before any analyzer run.** A working branch that has drifted
from master makes the mapper analyze a stale source tree — every connector
merged to master after the divergence point can appear as a new "added"
connector in subsequent diffs, even though no mapper logic changed.

```powershell
git fetch origin master
git merge origin/master --no-edit
```

- Use `git merge`, not `git rebase`, so subsequent
  `git log --first-parent origin/master` analysis (used by `compare_runs.py`
  and friends) still reflects merge dates correctly.
- Resolve any conflicts before running the mapper.
- Do this even for incremental/docs-only runs: docs link to GitHub paths that
  may have moved.

After merging, verify the working tree is clean of unintended changes:

```powershell
git status --short | Select-Object -First 20
```

## Cache Invalidation Model

The mapper's analysis cache is keyed by `(analysis_type, file_path)` and
stores the source file `mtime`. When a source file is modified (including via
`git merge`), its mtime changes and the entry is automatically re-analyzed on
the next run. **Source-content changes do NOT require `--force-refresh`.**

`--force-refresh` exists for two distinct reasons:

1. **Analyzer logic changed** (mapper code modified) — invalidate cached
   results for the affected analysis types so they get recomputed from current
   source. This is the **local-only** case.
2. **Network-fetched data is stale** — re-fetch tables / marketplace / ASIM
   schema fields from external sources. This is the **network** case and is
   reserved for explicit full refresh.

| Type          | Triggers network fetch?                                    | When to refresh                                        |
| ------------- | ---------------------------------------------------------- | ------------------------------------------------------ |
| `parsers`     | No                                                         | Mapper parser-analysis logic changed                   |
| `solutions`   | No                                                         | Mapper solution-analysis logic changed                 |
| `standalone`  | No                                                         | Mapper standalone-content logic changed                |
| `asim`        | **Yes** — re-runs `collect_asim_fields.py` against MS docs | ASIM analyzer logic changed AND network refresh wanted |
| `marketplace` | Yes — Azure Marketplace API                                | Marketplace data is stale                              |
| `tables`      | **Yes** — re-runs `collect_table_info.py` against MS docs  | Table reference info is stale                          |

Note: `asim` is hybrid — it invalidates the local ASIM-parser analysis cache
**and** re-runs `collect_asim_fields.py`. There is currently no flag to do
only the local half.

### After a `git merge` from master

Default: just run the mapper with no flags. Mtime-based invalidation re-analyzes
every file that changed during the merge:

```powershell
python map_solutions_connectors_tables.py
```

Network-fetched CSVs (`tables_reference.csv`, `asim_fields.csv`,
`asim_entity_fields.csv`, `asim_logical_types.csv`,
`asim_vendors_products.csv`, marketplace cache) will be reused from cache.
That's expected — they shouldn't drift just because master moved forward.

## Full Mapper Run (Invalidating All Caches)

Use only when explicitly asked to do a full/clean run, when "invalidate all
caches" is requested, or when analyzer logic was modified across multiple
analysis types.

```powershell
cd "Tools/Solutions Analyzer"
python map_solutions_connectors_tables.py --force-refresh=all
```

- `--force-refresh=all` clears all 6 cache types (asim, parsers, solutions,
  standalone, marketplace, tables) AND re-runs `collect_asim_fields.py` and
  `collect_table_info.py` against the network.
- `--force-refresh=all-offline` clears `parsers`, `solutions`, `standalone`,
  AND `asim` (which still re-runs `collect_asim_fields.py` despite the name;
  only `marketplace`/`tables` are skipped).
- Multiple types: `--force-refresh=parsers,solutions,standalone` (purely
  local, no network calls).
- Run with `isBackground: false` and `timeout: 0`.
- Do NOT truncate/filter output (no `Select-Object` piping).

**Known issue (as of 2026-04-28):** `collect_asim_fields.py` fails with HTTP
404 because the Microsoft Sentinel docs were migrated out of
`MicrosoftDocs/azure-docs`. The mapper logs a warning and proceeds, leaving
`asim_fields.csv`, `asim_entity_fields.csv`, `asim_logical_types.csv`, and
`asim_vendors_products.csv` empty/stale. Until the script is updated to fetch
from the new source, avoid `--force-refresh=all` and `--force-refresh=asim`
unless you accept stale ASIM schema CSVs.

## Generate Documentation

```powershell
python generate_connector_docs.py --output-dir <DOCS_DIR> [--skip-input-generation] [--html-output-dir <HTML_DIR>] [--html-docs-path <REL_PATH>] [--html-index-url <URL>]
```

- `--output-dir` — **mandatory**, never omit.
- `--skip-input-generation` — skip the embedded mapper invocation when CSVs
  are already fresh.
- `--html-output-dir`, `--html-docs-path`, `--html-index-url` — control where
  `index.html` and the interactive entity pages are written and how they
  link back to the index. These are typically only set when publishing to a
  static-site / GitHub Pages location; defaults are sensible for a local
  preview.
- Run with `isBackground: false` and `timeout: 0`. Do NOT truncate output.

## Generate ASIM Browser

```powershell
python generate_asim_browser.py --output-dir <DIR> [--docs-base-path <REL_PATH>] [--index-url <URL>] [--link-extension <EXT>]
```

`--docs-base-path` and `--index-url` make sense only when the browser is
deployed alongside an interactive docs index. For a standalone local
preview, `--output-dir` alone is enough.

## When to Re-Run the Mapper Before Docs

Run mapper before generating docs if:

- The mapper script itself was modified.
- Any override YAML file in the `overrides/` folder was modified.
- You specifically need to refresh the CSV data.
- You are explicitly asked to run the mapper.

Otherwise, just run the doc generator with `--skip-input-generation`.

## Caching and Logging

- **Cache:** `Tools/Solutions Analyzer/.cache/`
- **Logs:** `Tools/Solutions Analyzer/.logs/`
- **Log file:** `Tools/Solutions Analyzer/.logs/map_solutions_connectors_tables.log`

### Watching Mapper Progress While It Runs

The mapper writes timestamped progress lines (`[ N.Ns] ...`) to its own log
file in real time. To see live status during a run, tail that file directly:

```powershell
Get-Content "Tools/Solutions Analyzer/.logs/map_solutions_connectors_tables.log" -Tail 12
```

**Do NOT rely on `... | Tee-Object -FilePath <log> | Select-Object -Last N`
for live progress.** PowerShell pipelines buffer until the upstream command
finishes, so the Tee'd file stays empty until the entire run completes
(including the post-processing/CSV-write phase, which can be many minutes
after the per-parser progress lines were emitted). The mapper's own
`.logs/map_solutions_connectors_tables.log` is unbuffered and updates within
seconds.

## Upload to Kusto

```powershell
python upload_to_kusto.py -c <cluster-url> -d <database> --solution-analyzer --source-dir ./
```

- `--solution-analyzer` uploads the standard set of CSVs defined in
  `SOLUTION_ANALYZER_FILES`.
- `--source-dir ./` uses local CSVs instead of downloading from GitHub.
- Without `--source-dir`, downloads CSVs from the public Azure-Sentinel
  GitHub repo.
- `--dry-run` shows what would be uploaded without making changes.
- Requires Azure CLI authentication (`az login`).

The cluster URL and database name are environment-specific and not part of
this skill.

## User-Specific Publishing Pipelines

If you maintain a publishing pipeline (e.g. CSV output worktree, separate
docs repository, GitHub Pages site, specific Kusto cluster), record the
concrete paths, URLs, and the order of copy/commit/push steps in agent
memory — for example, in `/memories/repo/` for a workspace-scoped note or in
`/memories/` for a cross-workspace one. The agent should consult that memory
to resolve any placeholders above before running.
