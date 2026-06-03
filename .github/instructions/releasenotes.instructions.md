---
applyTo: "Solutions/**/ReleaseNotes.md"
---

# Release Notes Instructions

## File Location
- **Path:** `Solutions/{SolutionName}/ReleaseNotes.md`
- **Naming:** Exactly `ReleaseNotes.md` (case-sensitive)
- **Format:** Markdown file with a markdown table

## Required Table Structure

Exactly three columns in this order:
1. **Version** - Semantic versioning format (X.Y.Z)
2. **Date Modified (DD-MM-YYYY)** - Release date in DD-MM-YYYY format
3. **Change History** - Description of changes in this version

## Validation Rules

| Rule | Requirement | Invalid Example | Valid Example |
|------|-------------|-----------------|---------------|
| **Version Format** | Must be X.Y.Z (semantic versioning with 3 parts) | `3.0`, `v3.0.0`, `3` | `3.0.0`, `3.0.1`, `2.1.5` |
| **Version Ordering** | Versions must be in descending order (newest first) | 3.0.0, 3.0.1, 3.0.2 | 3.0.2, 3.0.1, 3.0.0 |
| **Date Format** | Must be DD-MM-YYYY with hyphens | `2026-05-02`, `05/02/2026`, `05-02-26` | `02-05-2026`, `25-12-2024` |
| **Column Header 1** | Exactly `**Version**` | `Version`, `version`, `**Versions**` | `**Version**` |
| **Column Header 2** | Exactly `**Date Modified (DD-MM-YYYY)**` | `Date (DD-MM-YYY)`, `Date Modified` | `**Date Modified (DD-MM-YYYY)**` |
| **Column Header 3** | Exactly `**Change History**` | `Changes`, `History`, `**Change Log**` | `**Change History**` |
| **Change History** | Must not be empty or contain only whitespace | Empty cell, `-`, spaces only | Clear description of what changed |
| **No Duplicates** | Each version must appear only once | 3.0.1 appears twice | Each version appears once |
| **All 3 Columns Present** | Table must have exactly 3 columns, no more, no less | 2 columns or 4 columns | Exactly 3 columns |

## When to Update Release Notes

Release notes **MUST be updated** for any of the following changes:

- **Content changes**: Modifications to Analytical Rules, Hunting Queries, Workbooks, Data Connectors, or any other solution content
- **Package folder changes**: ANY changes to files in `Solutions/{SolutionName}/Package/` folder (metadata, configurations, solution settings)
- **Parser/Function updates**: Changes to KQL parsers or custom functions
- **Documentation updates**: Updates to README or other documentation files
- **Bug fixes**: Any bug fixes to existing content
- **Performance improvements**: Optimizations to queries or logic
- **New content**: Addition of new Analytical Rules, Workbooks, Hunting Queries, etc.
- **Deprecated content**: Marking components as deprecated or removing content

Release notes are **NOT required** for:
- Changes only to non-solution files (e.g., standalone scripts outside Solutions folder)
- Documentation-only PRs that don't affect solution content

**Important:** If your PR includes changes to `Solutions/{SolutionName}/Package/` folder, updating ReleaseNotes.md is mandatory. Failure to update release notes when package folder changes will result in PR review failure.

## Best Practices

- **Clear descriptions:** Specify which component changed (e.g., "Updated query in **Analytical Rule**", "Fixed bug in **Data Connector**")
- **Be concise:** Keep descriptions brief but informative - 1-2 sentences maximum
- **Include context:** Mention what the change affects (e.g., performance, functionality, compatibility)
- **Consistent component naming:** Use same terminology throughout (e.g., "Analytical Rule" not "Detection Rule")
- **List newest first:** Always arrange versions in descending order for readability
- **No empty rows:** Don't skip versions - include all releases in the table
- **Avoid generic terms:** Instead of "Updated", specify what was updated and why (e.g., "Updated query in Analytical Rule to improve performance by reducing unnecessary joins")

### Valid ReleaseNotes.md Example

**File:** `Solutions/**/ReleaseNotes.md`

```markdown
| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
|---|---|---|
| 3.1.2 | 16-03-2026 | Updated **Analytical Rule** for better threat detection accuracy |
| 3.1.1 | 10-03-2026 | Fixed timeout issue in **Hunting Query** - optimized KQL performance |
| 3.1.0 | 05-03-2026 | Added new **Workbook** dashboard for security metrics visualization |
| 3.0.2 | 25-02-2026 | Deprecated legacy **Data Connector** configuration |
| 3.0.1 | 15-02-2026 | Updated **Parser** to handle new field formats |
| 3.0.0 | 01-01-2026 | Initial release with core security content |
```

### What Makes This Valid
- ✅ File located at `Solutions/**/ReleaseNotes.md`
- ✅ Exactly 3 columns with correct headers
- ✅ All versions follow X.Y.Z format: `3.1.2`, `3.1.1`, etc.
- ✅ Versions in descending order (newest first)
- ✅ All dates in DD-MM-YYYY format with hyphens
- ✅ Each change history entry is specific about what component changed
- ✅ No empty cells
- ✅ No duplicate versions

