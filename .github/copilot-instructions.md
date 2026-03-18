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

### For Analytic Rules Files (`Detections/**/*.yaml`, `Solutions/**/Analytic Rules/*.yaml`)
1. **LOAD and USE:** `.github/instructions/detections.instructions.md`
2. Apply ALL validation rules from that file
3. Check all field requirements, MITRE ATT&CK mappings, KQL syntax, and formatting guidelines from that custom instruction file
4. Validate GUID format, rule names, descriptions, severity levels, and other field-based validation rules
5. Do NOT use general instructions for these files - only use the detections custom instructions

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
python generate_connector_docs.py --output-dir "C:\Users\ofshezaf\GitHub\sentinelninja\Solutions Docs" --skip-input-generation
```

**IMPORTANT:** Never run without `--output-dir` flag.

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