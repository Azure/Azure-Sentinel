---
name: update-solution-analyzer
description: "MANDATORY guidelines for ANY edit to ANY file under Tools/Solutions Analyzer/ — including the mapper (map_solutions_connectors_tables.py), doc generator (generate_connector_docs.py), interactive docs (generate_interactive_docs.py), ASIM browser, collect_table_info, collect_asim_fields, upload_to_kusto, compare_runs, solution_analyzer_overrides.csv, filter_field_resolution.yaml, or any other script/config in that folder. Use when: editing/modifying/refactoring/fixing/renaming/tweaking ANY logic in those files, even one-line fixes such as renaming a classification, escaping a character, adjusting a regex, adding an override row, suppressing a false positive, or changing a constant. Covers: keeping script-docs in sync, README Version History changelog rules (required for feature/behavior changes; optional for small bug fixes), CSV output sync with upload_to_kusto.py, static/interactive index synchronization, and markdown/HTML entity page synchronization."
---

# Update Solution Analyzer Scripts

## Before Modifying a Script

Always review the relevant script documentation in `Tools/Solutions Analyzer/script-docs/` first. For changes to a CSV output file's columns or semantics, also review the corresponding per-CSV reference page in `Tools/Solutions Analyzer/script-docs/csv/` (one file per CSV).

## Script Documentation Updates

When updating a script, update the corresponding doc in `script-docs/` to reflect:

- Script parameters added or changed
- Output file changes — for new/renamed/removed CSV columns, **edit the per-CSV page in `script-docs/csv/<csv-name>.md`** (the script doc only lists CSVs as a summary table with links; it does not duplicate column tables)
- Changes to analysis methods or logic
- New CSV output: create a new page under `script-docs/csv/`, add a row to the summary table in the script doc, and add the new CSV to `script-docs/csv/README.md` (both the "By generating script" and "By role" sections)

## README Changelog

**Required for feature additions and behavior changes; optional for small bug fixes.** New features, changed analysis logic, new/renamed/removed CSV columns, parameter changes, and other user-visible behavior changes must appear in the changelog. Pure bug fixes — such as correcting a typo, fixing a crash, escape-character tweaks, regex corrections, or one-line fixes that restore intended behavior without changing it — may be logged at your discretion but are not required.

When a changelog entry is warranted, update the `## Version History` section in `Tools/Solutions Analyzer/README.md`:

- Add the change under the **latest version heading** at the top of the changelog
- If the latest version has not been committed yet (i.e., it already has uncommitted changes in the changelog), add to that existing version — do **not** create a new version entry
- If the latest version was already committed, create a new version entry with an incremented version number and a short descriptive title
- Each entry should be a bullet under a bold category heading (e.g., `**Fix Name:**`)
- Be concise but specific: state what changed, why, and what the user-visible impact is

## CSV Output Changes

When adding or removing a CSV output file from the mapper:

- Update `upload_to_kusto.py` → `SOLUTION_ANALYZER_FILES` list to add/remove the file

## Static and Interactive Index Synchronization

The documentation generator produces **two parallel sets of index pages** that must stay in sync:

1. **Static indexes** (`generate_connector_docs.py`): Markdown index pages — `solutions-index.md`, `connectors-index.md`, `tables-index.md`, `content/content-index.md`, etc.
2. **Interactive index** (`generate_interactive_docs.py`): HTML page with DataTables.js — `index.html` with tabs for Solutions, Connectors, Tables, and Content.

**When modifying any index generation logic**, apply the same change to BOTH:

- Data filtering/inclusion rules (which connectors or tables to show)
- Status classification logic (Active/Deprecated/Unpublished/Discovered)
- Icon usage and legend entries
- Special-case handling (placeholder names like `<PlaybookName>`, "GitHub Only" solution name)
- Link generation (collection method links, content item links, parser routing)
- Column additions or removals
- Description cleanup (quote stripping, truncation)

## Markdown and HTML Entity Page Synchronization

The doc generator produces **both static markdown and HTML versions** of every entity page.

- **Markdown pages** (`generate_connector_docs.py`): Primary data source — all content, counts, tables, and formatting are defined here.
- **HTML entity pages** (`generate_interactive_docs.py` → `_generate_html_pages()`): Auto-generated from markdown via Python `markdown` library.

In most cases, changing `generate_connector_docs.py` is sufficient because HTML pages derive from markdown. But if the change involves:

- Navigation or link targets
- HTML-specific rendering (e.g., DataTables on schema tables)
- Heading structure changes

...also update `generate_interactive_docs.py`.
