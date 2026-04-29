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

When working with the Solutions Analyzer tools in `Tools/Solutions Analyzer/`, follow the dedicated skills under `.github/skills/`:

- **`run-solution-analyzer`** — running the mapper, doc generator, ASIM browser, and `upload_to_kusto`; output locations; force-refresh and caching.
- **`update-solution-analyzer`** — modifying scripts, updating `script-docs/`, README changelog rules, CSV output sync with `upload_to_kusto.py`, and static/interactive index plus markdown/HTML entity page synchronization.
