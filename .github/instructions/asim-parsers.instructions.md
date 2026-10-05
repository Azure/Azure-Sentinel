---
applyTo: "Parsers/ASim*/Parsers/ASim*.yaml,Parsers/ASim*/Parsers/vim*.yaml"
---

# ASIM Parser Review Instructions

## Overview

Use these instructions when reviewing Azure Sentinel Information Model (ASIM) parser files. Review ASIM parsers for KQL performance, efficiency, and best practices.

Determine whether each changed file is a parameterless, parameterized, or ingestion-time parser, then apply the corresponding review rules below. These ASIM-specific instructions take precedence over the generic parser instructions.

## Pull Request and File Review Scope

1. Identify every added or modified ASIM parser YAML file and classify it by parser type:
   - Parameterless parsers are prefixed with `ASim`.
   - Parameterized parsers are prefixed with `vim`.
2. For each added or modified parser, verify that its corresponding changelog was added or updated in the same pull request:
   - Derive the changelog path by replacing the parser directory and `.yaml` extension with `CHANGELOG/<ParserFileName>.md`. For example, `Parsers/ASimAuthentication/Parsers/ASimAuthenticationAADManagedIdentity.yaml` corresponds to `Parsers/ASimAuthentication/CHANGELOG/ASimAuthenticationAADManagedIdentity.md`.
   - A newly added parser must have a newly added changelog.
   - A modified existing parser must have its existing changelog updated.
   - Match parser and changelog filenames exactly, including the `ASim` or `vim` prefix and casing.
   - Apply `.github/instructions/asim-changelogs.instructions.md` when reviewing the corresponding changelog.
   - Report a missing, unchanged, or incorrectly paired changelog as a review finding for that parser.
3. Extract `ParserQuery` from each parser being reviewed.
4. For a parameterized parser, also extract `ParserParams` and compare the parser with its parameterless counterpart.

## Parameterless Parsers (`ASim*.yaml`)

Review the extracted `ParserQuery` for all of the following:

### Query Flow

- **Filter, parse, map:** Verify that the query filters early on native columns, performs parsing next, and maps fields last.
- **Field mapping operators:** Use `project-rename` for direct source-column mappings. Use `extend` only for calculated or normalized fields. Flag `extend` when `project-rename` would suffice.
- **No `project-away`:** Flag `project-away` used to remove unmapped columns. Require `project` instead so source schema changes do not unintentionally change parser output.

### Source and Row Integrity

- **One event source:** Verify that the parser reads event records from one declared source table.
- **No event enrichment or correlation:** Flag a second read of the source table, self-joins, event-record correlation, workspace-table or watchlist references, `externaldata`, or any other external tabular source.
- **Allow static local mappings:** Query-local mappings defined with `datatable` and applied with `lookup` are allowed. Verify that each lookup key is unique so the lookup cannot fan out a source record.
- **Leave unavailable fields unmapped:** If a field cannot be produced from the current source row or a static local mapping, it must remain unmapped rather than be enriched from event data.
- **At most one output row per source row:** Flag any operator or expression that fans out one source record into multiple normalized records. Treat fan-out as a connector or source event-shape issue rather than supporting it in the parser.
- **No `mv-*` operators:** Flag every KQL operator whose name starts with `mv-`, including `mv-expand` and `mv-apply`. Use scalar dynamic-value access or another scalar expression. Leave a field unmapped if it cannot be mapped without row expansion.
- **No aggregation or deduplication:** Flag `summarize`, `distinct`, `arg_min`, `arg_max`, or equivalent operations that aggregate, reaggregate, correlate, deduplicate, combine, or collapse event records. Each source record must be normalized independently.

Treat same-table or cross-table event enrichment, row fan-out, any `mv-*` operator, and event-record aggregation or reaggregation as 🔴 High priority.

### Parameters and Placeholder Fields

- **`pack` parameter:** If the query uses `AdditionalFields`, require a `pack: bool = false` parameter. Users must be able to avoid populating `AdditionalFields` when it is not needed.
- **Applicable placeholder fields:** Determine the complete applicable field set from the target schema and the `Common` rows in `ASimTester.csv`.
- **Required placeholder fields:** Verify that the parser includes every defined `*EntityKey` and `*AdditionalIds` field, plus `AdditionalEntities` when it is defined.
- **Exact names and casing:** Placeholder names and casing must match `ASimTester.csv`. Generic names such as `entityKey` or `AdditionalIds` are invalid.
- **Placeholder values:** Every `*EntityKey` must be an empty string. Every `*AdditionalIds` field and `AdditionalEntities` must be an empty dynamic array until mappings are defined.

### KQL Performance

- Prefer high-performance parsing operators such as `split`, `parse-kv`, and `parse`.
- Flag regular expressions when a simpler parsing operator can perform the same work.
- Flag unnecessary `let` statements, redundant filters, calculations performed too early, or operations that can be reordered to reduce processing.

## Parameterized Parsers (`vim*.yaml`)

Review the parameterized parser after reviewing its parameterless counterpart. Do not repeat issues already reported for the parameterless parser. Focus on filtering and parameter-specific logic introduced by the `vim` parser.

Review `ParserParams` and `ParserQuery` for all of the following:

1. **Parameter placement:** Apply parameter filters as early as possible, before parsing or field calculations.
2. **Filter efficiency:** Use native columns and indexed fields where possible.
3. **Redundant computation:** Flag calculated fields or parsing operations performed before a parameter filter when they can be moved after it.
4. **Parameter completeness:** Verify that the parameters support efficient filtering for common use cases.
5. **Parameter usage:** Verify that every declared parameter appears in the query.
6. **Parameters without source columns:** Do not flag a filter that only checks `array_length(<param>) == 0`, or an equivalent expression, when the source data has no corresponding column. This is valid. Flag a parameter as unused only when it is completely absent from the query.
7. **Placeholder consistency:** Compare placeholder fields and values with the parameterless parser:
   - Report a field missing from both parsers only in the parameterless parser review.
   - Report only differences introduced by the parameterized parser, such as a placeholder that is omitted, renamed, or populated when the parameterless parser defines it correctly.
   - Do not accept a matching omission; ensure it is reported in the parameterless parser review.
8. **Prohibited-pattern consistency:** Report same-table or cross-table event enrichment, fan-out, `mv-*`, or event-record aggregation or reaggregation introduced only by the parameterized parser as 🔴 High priority.
   - Query-local static `datatable` and `lookup` mappings are allowed.
   - If the same violation exists in both parser versions, report it only in the parameterless parser review.

## Review Findings and Priority

Return findings as a Markdown table:

| # | Priority | Issue | Suggestion |
|---|----------|-------|------------|

- **Priority** must be one of: 🔴 High, 🟡 Medium, or 🟢 Low.
- **Issue** must concisely describe the identified problem.
- **Suggestion** must provide a specific, actionable fix.
- Do not add a row for a category with no findings.
- If the parser has no issues, return one row stating `No issues found`.
- For parameterized parsers, include only issues specific to filtering or parameter logic and differences introduced by that parser.
