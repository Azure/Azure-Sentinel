# solution_analyzer_overrides.csv

**Used by:** [`map_solutions_connectors_tables.py`](../map_solutions_connectors_tables.md), [`collect_table_info.py`](../collect_table_info.md), [`generate_connector_docs.py`](../generate_connector_docs.md)
**Granularity:** One row per override rule
**Type:** **Input** — hand-edited override file (not script output)

## Overview

Override rules that let you correct, supplement, or extend the analyzer's automated detection. Used for two distinct things:

1. **Field overrides** — pattern-match an entity (`table`, `connector`, `solution`) and overwrite a field on the matching rows.
2. **Synthetic connectors** — declare a connector that has no discoverable definition file in the repo (e.g., SAP, which uses a Docker agent), so the analyzer treats it as part of a solution.

The default file lives at `Tools/Solutions Analyzer/solution_analyzer_overrides.csv`.

## Use Cases

- **Set `collection_method` to AMA** for tables that the analyzer cannot infer otherwise (e.g., `Syslog`, `CommonSecurityLog`).
- **Apply category labels** by table-name pattern (e.g., `.*AWS.*` → category `AWS`). The raw `category` value feeds the computed `category_primary` taxonomy; to pin the normalized value directly, override `category_primary` (e.g., `Table,<pattern>,category_primary,Cloud`).
- **Mark a solution or connector deprecated** when description-based detection misses it.
- **Redirect the marketplace lookup** for a solution whose live offer differs from its `SolutionMetadata.json` by overriding `solution_publisher_id` and/or `solution_offer_id` (see below).
- **Inject a synthetic connector** for solutions whose connector definition isn't standard JSON in `Data Connectors/` (e.g., SAP).
- **Correct downstream metadata** sourced from upstream documentation that has gaps.

## Columns

| Column | Description |
|--------|-------------|
| `Entity` | Entity type to match: `table`, `connector`, `solution`, or `synthetic_connector` (case insensitive) |
| `Pattern` | Regex pattern matched (full-match, case insensitive) against the entity's key field — `table_name`, `connector_id`, or `solution_name`. For `synthetic_connector`, the pattern is the solution folder name |
| `Field` | Field to override. For `synthetic_connector`, must be one of: `connector_id` (required, starts a new connector group), `title`, `publisher`, `description`, `tables`, `instruction_steps`, `permissions` |
| `Value` | New value. For `tables` (synthetic connectors), use a semicolon-separated list |
| `Comment` | Free-form note explaining why the override exists (not consumed by the analyzer) |

### Pattern matching rules

- Patterns are full-match regex (automatically wrapped with `^` and `$`).
- Pattern matching is case insensitive.
- Use `.*` for wildcards (e.g., `.*AWS.*` matches any table containing "AWS").
- `Field` names must exactly match an existing column in the relevant output.

### Marketplace lookup-key overrides (`solution` entity)

The published status in [`solutions.csv`](solutions.md) is derived from the **public** Azure Marketplace catalog, keyed by the solution's `<solution_publisher_id>.<solution_offer_id>` legacy id. A `solution` override on either `solution_publisher_id` or `solution_offer_id` is applied **before** the marketplace availability check (unlike every other override, which is applied afterward), so it redirects *what* is looked up and lets the public catalog produce the correct `mp_is_published` / `is_published` verdict.

Use it when a solution is live in the marketplace under a different offer than its repo `SolutionMetadata.json` records — a renamed/re-published offer, a publisher hand-off, or a repo folder with no `SolutionMetadata.json` at all. Prefer this over a blanket `is_published=true` override: because the answer still comes from the live catalog, it self-corrects on future marketplace changes. The mapper never calls the authenticated Content Hub APIs; an `is_published` override remains the last resort for content genuinely in the Content Hub but absent from the marketplace catalog.

```csv
Entity,Pattern,Field,Value,Comment
Solution,Farsight DNSDB,solution_publisher_id,domaintoolsllc1647901527537,Republished under DomainTools
Solution,Farsight DNSDB,solution_offer_id,farsight-dnsdb,Republished under DomainTools
```

### Synthetic connector format

Synthetic connectors use multiple rows sharing the same `Pattern` (solution folder name) and grouped by `Field = connector_id`:

| Required `Field` values | Description |
|---|---|
| `connector_id` | Unique identifier; **starts a new connector group** |
| `title` | Display title |
| `publisher` | Publisher name |

| Optional `Field` values | Description |
|---|---|
| `description` | Connector description text |
| `tables` | Semicolon-separated list of table names |
| `instruction_steps` | JSON-encoded setup instructions |
| `permissions` | JSON-encoded permission requirements |

#### Example

```csv
Entity,Pattern,Field,Value,Comment
Table,Syslog,collection_method,AMA,
Table,.*AWS.*,category,AWS,
synthetic_connector,SAP,connector_id,MicrosoftSentinelSAP,SAP uses Docker agent
synthetic_connector,SAP,title,Microsoft Sentinel for SAP,
synthetic_connector,SAP,publisher,Microsoft,
synthetic_connector,SAP,tables,ABAPAuditLog_CL;ABAPChangeDocsLog_CL,
```

> Synthetic connectors are only injected if no connector with the same ID was discovered. They appear in [`connectors.csv`](connectors.md) with `connector_files = synthetic_connector_override`.

See [`map_solutions_connectors_tables.md` › Override System](../map_solutions_connectors_tables.md#override-system) for further details.

## Related CSVs

- [`connectors.csv`](connectors.md) / [`tables.csv`](tables.md) / [`solutions.csv`](solutions.md) — the outputs that this file modifies.
- [`tables_reference.csv`](tables_reference.md) — also subject to this override file (for `support_tier`, `category`, `collection_method`).
