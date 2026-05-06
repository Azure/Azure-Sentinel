---
name: run-solution-analyzer
description: "Run the Solutions Analyzer scripts: mapper, documentation generator, ASIM browser. Use when: running solution analyzer, generating CSVs, generating docs, publishing CSVs, refreshing caches, force-refresh, invalidating caches, generating ASIM browser, running mapper, running collect_table_info, running collect_asim_fields."
---

# Run Solution Analyzer

## Scripts Overview

| Script | Purpose | Invocation |
|--------|---------|------------|
| `map_solutions_connectors_tables.py` | Mapper: generates all CSV data | Run directly |
| `generate_connector_docs.py` | Doc generator: markdown + HTML pages, static + interactive indexes | Run directly |
| `generate_asim_browser.py` | ASIM browser: interactive HTML schema browser | Run directly |
| `upload_to_kusto.py` | Upload CSVs to Azure Data Explorer (Kusto) cluster | Run directly |
| `collect_table_info.py` | Fetch table reference data from Microsoft docs | Auto-invoked by mapper (`--force-refresh=tables`) |
| `collect_asim_fields.py` | Fetch ASIM field/schema definitions from Microsoft docs | Auto-invoked by mapper (`--force-refresh=asim`) |
| `generate_interactive_docs.py` | Generate `index.html` and HTML entity pages | Auto-invoked by `generate_connector_docs.py` |

All scripts run from `Tools/Solutions Analyzer`.

## Output Locations

There are **three distinct output targets** — never confuse them:

| Scenario | Path | What goes here |
|----------|------|----------------|
| **Development** (default) | `Tools/Solutions Analyzer/` | CSVs in the current branch |
| **Publish CSVs** (output worktree) | `C:\Users\ofshezaf\GitHub\Azure-Sentinel-solution-analyzer-output\Tools\Solutions Analyzer` | Mapper-generated CSVs only (separate git worktree). No overrides, no docs, no ad-hoc reports. |
| **Publish CSVs** (sentinelninja) | `C:\Users\ofshezaf\GitHub\sentinelninja\Tools\Solutions Analyzer` | Same mapper-generated CSVs, in the sentinelninja repo for GitHub Pages access. |
| **Documentation** | `C:\Users\ofshezaf\GitHub\sentinelninja\Solutions Docs` | Generated markdown/HTML docs (separate repo) |

**Never generate docs in the Azure-Sentinel repo.**

## Full Run (Invalidating All Caches)

Use when asked to do a full/clean run, or when "invalidate all caches" is requested.

### Step 1: Run Mapper with Force-Refresh

```powershell
cd "Tools/Solutions Analyzer"
python map_solutions_connectors_tables.py --force-refresh=all
```

- `--force-refresh=all` clears all 6 cache types (asim, parsers, solutions, standalone, marketplace, tables)
- `--force-refresh=all-offline` clears all except marketplace and tables (the two network-dependent types)
- Multiple types: `--force-refresh=asim,parsers`
- Run with `isBackground: false` and `timeout: 0`
- Do NOT truncate/filter output (no `Select-Object` piping)

### Step 2: Copy CSVs to Output Worktree and Sentinelninja

Copy **only** mapper-generated CSVs. The canonical list is in `upload_to_kusto.py` → `SOLUTION_ANALYZER_FILES`, plus these additional CSVs from sub-scripts: `la_table_schemas.csv`, `asim_fields.csv`, `asim_entity_fields.csv`, `asim_logical_types.csv`, `asim_vendors_products.csv`.

Copy to **both** targets:
- `C:\Users\ofshezaf\GitHub\Azure-Sentinel-solution-analyzer-output\Tools\Solutions Analyzer`
- `C:\Users\ofshezaf\GitHub\sentinelninja\Tools\Solutions Analyzer`

### Step 3: Generate Documentation

```powershell
python generate_connector_docs.py --output-dir "C:\Users\ofshezaf\GitHub\sentinelninja\Solutions Docs" --skip-input-generation --html-output-dir "C:\Users\ofshezaf\GitHub\sentinelninja" --html-docs-path "Solutions Docs/" --html-index-url "https://oshezaf.github.io/sentinelninja/index.html"
```

Required flags:
- `--output-dir` — **mandatory**, never omit
- `--skip-input-generation` — CSVs are already fresh from Step 1
- `--html-output-dir` — repo root for `index.html` (GitHub Pages)
- `--html-docs-path` — relative path for entity page links
- `--html-index-url` — GitHub Pages URL for nav bar back-links

Run with `isBackground: false` and `timeout: 0`. Do NOT truncate output.

### Step 4: Generate ASIM Browser

```powershell
python generate_asim_browser.py --output-dir "C:\Users\ofshezaf\GitHub\sentinelninja" --docs-base-path "Solutions Docs/" --index-url "https://oshezaf.github.io/sentinelninja/index.html" --link-extension ".html"
```

- Output goes to sentinelninja repo root alongside `index.html`
- `--docs-base-path "Solutions Docs/"` ensures correct relative links to entity pages

## Incremental Run (Using Existing Caches)

Use when only re-generating docs from existing CSVs, or when only specific caches need refreshing.

### Docs Only (CSVs already up-to-date)

Skip the mapper entirely and just run Steps 3 and 4 above.

### Selective Cache Refresh

Use `--force-refresh` with specific types when modifying analysis logic:

| Type | Scope | Network? |
|------|-------|----------|
| `asim` | ASIM parser analysis | No |
| `parsers` | Non-ASIM parser analysis | No |
| `solutions` | Solution content analysis | No |
| `standalone` | Standalone content item analysis | No |
| `marketplace` | Marketplace availability check | Yes |
| `tables` | Table reference info (Microsoft docs) | Yes |

Example: `python map_solutions_connectors_tables.py --force-refresh=asim,parsers`

### When to Re-Run the Mapper Before Docs

Run mapper before generating docs if:
- The mapper script itself was modified
- Any override YAML file in the `overrides/` folder was modified
- You specifically need to refresh the CSV data
- You are explicitly asked to run the mapper

Otherwise, just run the doc generator with `--skip-input-generation`.

## Caching and Logging

- **Cache:** `Tools/Solutions Analyzer/.cache/`
- **Logs:** `Tools/Solutions Analyzer/.logs/`
- **Log file:** `Tools/Solutions Analyzer/.logs/map_solutions_connectors_tables.log`

## Upload to Kusto

```powershell
python upload_to_kusto.py -c <cluster-url> -d <database> --solution-analyzer --source-dir ./
```

- `--solution-analyzer` uploads the standard set of CSVs defined in `SOLUTION_ANALYZER_FILES`
- `--source-dir ./` uses local CSVs instead of downloading from GitHub
- Without `--source-dir`, downloads CSVs from the public Azure-Sentinel GitHub repo
- `--dry-run` shows what would be uploaded without making changes
- Requires Azure CLI authentication (`az login`)
