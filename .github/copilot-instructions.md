# GitHub Copilot Instructions for Azure-Sentinel Repository

# Copilot Pull Request Review Guidelines

When reviewing pull requests, follow these rules strictly.

## IMPORTANT: Load Custom Instructions Based on File Type

**Before reviewing any file, CHECK if it matches these patterns:**

### For Solution Metadata Files (`Solutions/**/SolutionMetadata.json`)
1. **LOAD and USE:** `.github/instructions/solution-metadata.instructions.md`
2. Apply ALL guidelines from that file
3. Check all validation rules, required fields, and review focus areas from that custom instruction file
4. Do NOT use general instructions for these files - only use the solution-metadata custom instructions

### For Solution Data Files (`Solutions/**/Data/Solution_*.json`)
1. **LOAD and USE:** `.github/instructions/solution-data.instructions.md`
2. Apply ALL guidelines from that file
3. Check all validation rules, required fields, and review focus areas from that custom instruction file
4. Do NOT use general instructions for these files - only use the solution-data custom instructions

### For Release Notes Files (`Solutions/**/ReleaseNotes.md`)
1. **LOAD and USE:** `.github/instructions/releasenotes.instructions.md`
2. Apply ALL validation rules from that file (path, table structure, version format/order, DD-MM-YYYY date format)
3. If this is the **only changed file in the PR**, still run full Release Notes validation and add findings
4. Do NOT use generic fallback comments for these files

### For Analytic Rules Files (`Detections/**/*.yaml`, `Detections/**/*.yml`, `Solutions/**/Analytic Rules/*.yaml`, `Solutions/**/Analytic Rules/*.yml`)
1. **LOAD and USE:** `.github/instructions/detections.instructions.md`
2. Apply ALL validation rules from that file
3. Check all field requirements, MITRE ATT&CK mappings, KQL syntax, and formatting guidelines from that custom instruction file
4. Validate GUID format, rule names, descriptions, severity levels, and other field-based validation rules
5. Do NOT use general instructions for these files - only use the detections custom instructions

### For Hunting Queries Files (`Hunting Queries/**/*.yaml`, `Solutions/**/Hunting Queries/*.yaml`)
1. **LOAD and USE:** `.github/instructions/huntingqueries.instructions.md`
2. Apply ALL guidelines from that file
3. Verify all required fields are present and properly formatted
4. Do NOT use general instructions for these files - only use the huntingqueries custom instructions

### For Playbooks Files (`Playbooks/**/*.json`, `Playbooks/**/README.md`, `Solutions/**/Playbooks/**/*.json`, `Solutions/**/Playbooks/**/README.md`)
1. **LOAD and USE:** `.github/instructions/playbooks.instructions.md`
2. Apply ALL guidelines from that file
3. Validate ARM template structure, metadata fields, parameters, and README requirements from that custom instruction file
4. Check all required sections in README.md and ARM template metadata
5. Do NOT use general instructions for these files - only use the playbooks custom instructions

### For Workbooks Files (`Workbooks/*.json`, `Solutions/**/Workbooks/*.json`)
1. **LOAD and USE:** `.github/instructions/workbook.instructions.md`
2. Apply ALL guidelines from that file
3. Validate workbook JSON structure, required fields, items array, and metadata requirements from that custom instruction file
4. Check all required top-level fields and item structure validation
5. Do NOT use general instructions for these files - only use the workbook custom instructions

### For Parser Files (`Parsers/**/*.yaml`, `Parsers/**/*.yml`, `Solutions/**/Parsers/**/*.yaml`, `Solutions/**/Parsers/**/*.yml`)
1. **LOAD and USE:** `.github/instructions/parsers.instructions.md`
2. Apply ALL guidelines from that file
3. Validate parser syntax, KQL accuracy, YAML structure, and all required fields from that custom instruction file
4. Do NOT use general instructions for these files - only use the parsers custom instructions

---

## Files and folders to ignore
Do NOT review or add comments for changes in the following paths:

- Solutions/**/Data Connectors/**
- Solutions/**/Package/**

If files from these paths appear in the PR, completely skip them and do not generate comments.

## Solutions Analyzer Tools

When working with the Solutions Analyzer tools in `Tools/Solutions Analyzer/`:

### Output Locations

There are THREE different output scenarios - **never confuse them**:

1. **Default (development):** CSVs are written to `Tools/Solutions Analyzer/` in the current branch
   - This is the normal case when developing/testing
   - **Never generate documentation here**

2. **Output worktree (publishing CSVs):** `C:\Users\ofshezaf\GitHub\Azure-Sentinel-solution-analyzer-output\Tools\Solutions Analyzer`
   - Only use this when **specifically requested** to "publish CSVs to the output branch"
   - This is a separate git worktree for the CSV output branch
   - **Only CSVs go here, never documentation**

3. **Documentation output:** `C:\Users\ofshezaf\GitHub\sentinelninja\Solutions Docs`
   - This is where generated markdown documentation goes
   - This is in a **separate repository** (sentinelninja)
   - Empty the target folder before generating new docs

### Key Rules

- **Never generate docs locally** in the Azure-Sentinel repository
- **Generate docs only in the sentinelninja repo** when asked or needed
- **For official CSV releases**, generate CSVs **only** in the solution analyzer output worktree
- Always use `--output-dir` flag when running `generate_connector_docs.py`

### Running Scripts

#### Mapper Script
```powershell
cd "Tools/Solutions Analyzer"
python map_solutions_connectors_tables.py
```

**Note:** Do NOT truncate or filter the output (e.g., do not pipe through `Select-Object`). The script prints timestamped progress messages to the console that the user needs to see. Run with `isBackground: false` and `timeout: 0` so the full output is visible.

#### Documentation Generator
```powershell
python generate_connector_docs.py --output-dir "C:\Users\ofshezaf\GitHub\sentinelninja\Solutions Docs" --skip-input-generation --html-output-dir "C:\Users\ofshezaf\GitHub\sentinelninja" --html-docs-path "Solutions Docs/" --html-index-url "https://oshezaf.github.io/sentinelninja/index.html"
```

**IMPORTANT:** Never run without `--output-dir` flag.

**IMPORTANT:** Always use `--html-output-dir`, `--html-docs-path`, and `--html-index-url` when generating docs to the sentinelninja repo. The interactive index.html must be at the repo root (`C:\Users\ofshezaf\GitHub\sentinelninja`) for GitHub Pages. Use a relative `--html-docs-path` (e.g. `"Solutions Docs/"`) so that both the interactive index links and the HTML entity pages are served directly from GitHub Pages. When `--html-output-dir` is set and `--html-docs-path` is relative, the generator automatically produces HTML versions of all markdown entity pages alongside the `.md` files and updates index.html links to point to the `.html` versions. Use the GitHub Pages URL for `--html-index-url` so that the navigation bar on both HTML entity pages and static markdown pages links back to the interactive index.

**IMPORTANT:** Do NOT truncate or filter the output (e.g., do not pipe through `Select-Object`). Run with `isBackground: false` and `timeout: 0` so the full output is visible to the user.

**IMPORTANT:** Always use `--skip-input-generation` unless you specifically need to regenerate the input CSVs (mapper + collect_table_info). Without this flag, the doc generator will re-run those scripts automatically, which is slow and unnecessary if the CSVs are already up-to-date.

**IMPORTANT:** Run the mapper script before generating docs if:
- The mapper script itself was modified, OR
- Any override YAML file in the `overrides/` folder was modified (including adding, editing, or removing `additional_connectors` entries), OR
- You specifically need to refresh the CSV data, OR
- You are explicitly asked to run the mapper

### Caching and Logging

- **Cache:** `.cache/` folder for analysis caching
- **Logs:** `.logs/` folder for log files

**Log file:** `Tools/Solutions Analyzer/.logs/map_solutions_connectors_tables.log`

Use `--force-refresh` with these types when modifying analysis logic:
- `asim` - ASIM parser analysis
- `parsers` - Non-ASIM parser analysis
- `solutions` - Solution content analysis
- `standalone` - Standalone content item analysis
- `marketplace` - Marketplace availability check (requires network)
- `tables` - Table reference info (requires network)

### Script Documentation

**Before updating a script:** Always review the relevant script documentation in `Tools/Solutions Analyzer/docs/` first.

**When updating a script**, update the corresponding script doc to reflect:
- Any script parameters added or changed
- Any output file changes, including changes to CSV files (new columns, renamed columns, removed columns)
- Any changes to analysis methods or logic
- Update the primary readme.md if needed and add the change to the change log. Do not add a version if the previous version as manifested by the changelog, was not committed yet.
- When adding or removing a CSV output file from the mapper, also update `upload_to_kusto.py` to add or remove the file from the `SOLUTION_ANALYZER_FILES` list.

### Static and Interactive Index Synchronization

The documentation generator produces **two parallel sets of index pages** that must stay in sync:

1. **Static indexes** (`generate_connector_docs.py`): Markdown index pages — `solutions-index.md`, `connectors-index.md`, `tables-index.md`, `content/content-index.md`, etc.
2. **Interactive index** (`generate_interactive_docs.py`): HTML page with DataTables.js — `index.html` with tabs for Solutions, Connectors, Tables, and Content.

**When modifying any index generation logic**, apply the same change to BOTH the static and interactive indexes:
- Data filtering/inclusion rules (e.g., which connectors or tables to show)
- Status classification logic (Active/Deprecated/Unpublished/Discovered)
- Icon usage and legend entries
- Special-case handling (e.g., placeholder names like `<PlaybookName>`, "GitHub Only" solution name)
- Link generation (e.g., collection method links, content item links, parser routing)
- Column additions or removals
- Description cleanup (quote stripping, truncation)

### Markdown and HTML Entity Page Synchronization

The documentation generator produces **both static markdown and HTML versions** of every entity page. When modifying entity page content (solution pages, connector pages, table pages, content item pages, parser pages, statistics page, etc.), ensure the change is reflected in **both outputs**:

- **Markdown pages** (`generate_connector_docs.py`): The primary data source — all content, counts, tables, and formatting are defined here.
- **HTML entity pages** (`generate_interactive_docs.py` → `_generate_html_pages()`): Auto-generated from the markdown pages via Python `markdown` library. Changes to markdown content flow through automatically, but changes to link rewriting, heading structure, or HTML-specific formatting may need updates in `_generate_html_pages()`.

In most cases, changing `generate_connector_docs.py` is sufficient because HTML pages are derived from the markdown. But if the change involves navigation, link targets, or HTML-specific rendering (e.g., DataTables on schema tables), also update `generate_interactive_docs.py`.
