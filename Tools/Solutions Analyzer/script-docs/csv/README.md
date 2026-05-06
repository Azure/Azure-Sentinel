# CSV Reference

Per-CSV reference documentation. Each page covers what the CSV contains, how it's produced, what it's good for, and which other CSVs it relates to.

## By generating script

### [`map_solutions_connectors_tables.py`](../map_solutions_connectors_tables.md)

**Entity tables**

- [`connectors.csv`](connectors.md) — one row per connector, with collection method, ingestion API, CCF capabilities, CLv1 status, marketplace status, and filter-field analysis.
- [`solutions.csv`](solutions.md) — one row per solution, with full Marketplace metadata and dependencies.
- [`tables.csv`](tables.md) — one row per table referenced by any connector.
- [`parsers.csv`](parsers.md) — one row per non-ASIM parser (solution + legacy).
- [`asim_parsers.csv`](asim_parsers.md) — one row per ASIM parser, with schema metadata and connector associations.
- [`content_items.csv`](content_items.md) — one row per content item (analytic rules, hunting queries, playbooks, workbooks, parsers, watchlists, summary rules).

**Mapping / edge tables**

- [`solutions_connectors_tables_mapping_simplified.csv`](solutions_connectors_tables_mapping_simplified.md) — three-column edge list (solution × connector × table).
- [`content_tables_mapping.csv`](content_tables_mapping.md) — content-item-to-table edges with `read`/`write` flag for playbooks.
- [`playbook_connectors.csv`](playbook_connectors.md) — Logic App connectors used by each playbook (managed and custom APIs).
- [`solution_dependencies.csv`](solution_dependencies.md) — solution-to-solution dependency edges (explicit + ASIM-derived optional).
- [`table_schemas.csv`](table_schemas.md) — unified table column schemas (DCR + docs + ARM + KQL validation).

**Backward-compatibility / legacy**

- [`solutions_connectors_tables_mapping.csv`](solutions_connectors_tables_mapping.md) — denormalized wide table (legacy).

**Reports**

- [`solutions_connectors_tables_issues_and_exceptions_report.csv`](solutions_connectors_tables_issues_and_exceptions_report.md) — issues encountered while parsing connectors and content.
- [`asim_parsers_unmatched_report.csv`](asim_parsers_unmatched_report.md) — ASIM parsers that couldn't be associated with any connector.

### [`collect_table_info.py`](../collect_table_info.md)

- [`tables_reference.csv`](tables_reference.md) — comprehensive table metadata fetched from Microsoft documentation.
- [`la_table_schemas.csv`](la_table_schemas.md) — column-level schemas from Azure Monitor and Defender XDR docs.

### [`collect_asim_fields.py`](../collect_asim_fields.md)

- [`asim_fields.csv`](asim_fields.md) — complete ASIM schema field catalog (docs + tester + physical tables).
- [`asim_entity_fields.csv`](asim_entity_fields.md) — User / Device / Application entity fields.
- [`asim_logical_types.csv`](asim_logical_types.md) — ASIM logical types and their allowed values.
- [`asim_vendors_products.csv`](asim_vendors_products.md) — allowed `EventVendor` / `EventProduct` values.
- [`asim_extraction_failures.csv`](asim_extraction_failures.md) — diagnostic report of extraction problems.

### Inputs (hand-edited)

- [`solution_analyzer_overrides.csv`](solution_analyzer_overrides.md) — override rules for field correction and synthetic connector injection.

## By role

| Role | CSVs |
|------|------|
| **Entity** | [`connectors`](connectors.md), [`solutions`](solutions.md), [`tables`](tables.md), [`parsers`](parsers.md), [`asim_parsers`](asim_parsers.md), [`content_items`](content_items.md) |
| **Mapping / edges** | [`solutions_connectors_tables_mapping_simplified`](solutions_connectors_tables_mapping_simplified.md), [`content_tables_mapping`](content_tables_mapping.md), [`playbook_connectors`](playbook_connectors.md), [`solution_dependencies`](solution_dependencies.md) |
| **Schema** | [`table_schemas`](table_schemas.md), [`la_table_schemas`](la_table_schemas.md), [`asim_fields`](asim_fields.md), [`asim_entity_fields`](asim_entity_fields.md), [`asim_logical_types`](asim_logical_types.md), [`asim_vendors_products`](asim_vendors_products.md) |
| **Reference** | [`tables_reference`](tables_reference.md) |
| **Report / diagnostic** | [`solutions_connectors_tables_issues_and_exceptions_report`](solutions_connectors_tables_issues_and_exceptions_report.md), [`asim_parsers_unmatched_report`](asim_parsers_unmatched_report.md), [`asim_extraction_failures`](asim_extraction_failures.md) |
| **Legacy / backward-compat** | [`solutions_connectors_tables_mapping`](solutions_connectors_tables_mapping.md) |
| **Input (hand-edited)** | [`solution_analyzer_overrides`](solution_analyzer_overrides.md) |
