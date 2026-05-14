---
name: update-solution-analyzer
description: "Guidelines for modifying Solutions Analyzer scripts. Use when: editing mapper, doc generator, interactive docs, ASIM browser, collect_table_info, collect_asim_fields, upload_to_kusto, or any script in Tools/Solutions Analyzer/. Covers: keeping docs in sync, index synchronization, entity page synchronization, CSV output changes, script documentation updates."
---

# Update Solution Analyzer Scripts

## Before Modifying a Script

Always review the relevant script documentation in `Tools/Solutions Analyzer/script-docs/` first.

## Script Documentation Updates

When updating a script, update the corresponding doc in `script-docs/` to reflect:
- Script parameters added or changed
- Output file changes (new/renamed/removed CSV columns)
- Changes to analysis methods or logic

## README Changelog

Update the `## Version History` section in `Tools/Solutions Analyzer/README.md`:
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
