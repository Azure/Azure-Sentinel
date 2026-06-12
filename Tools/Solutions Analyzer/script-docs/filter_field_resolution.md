# `filter_field_resolution.yaml` — Filter-Field Attribution Rules

> User-editable configuration consumed by `map_solutions_connectors_tables.py`. Editing this file changes which Sentinel table a given KQL where-predicate is attributed to, without touching Python.

## Purpose

Many KQL queries filter on column names that exist on more than one Sentinel table (e.g. `EventID` is defined on `Event`, `SecurityEvent`, and `WindowsEvent`; `ResourceProvider` is defined on both `AzureActivity` and `AzureDiagnostics`). When the mapper extracts `filter_fields` from a query, it needs to decide which table each predicate belongs to so downstream associations (connector ↔ table, connector ↔ parser, connector ↔ content item) stay accurate.

`filter_field_resolution.yaml` is the table-aware dispatch table that drives this decision for a curated set of well-known field names. Any predicate whose field name is not in this YAML is still picked up by a second, schema-driven pass that uses the documented column catalogs (`la_table_schemas.csv`, `asim_fields.csv`); the YAML governs only the curated pass.

## File location

`Tools/Solutions Analyzer/filter_field_resolution.yaml` (sibling of the mapper script).

The file is lazy-loaded on first use, so edits take effect on the next mapper run without needing to clear caches.

## Top-level structure

```yaml
prefix_groups:
  <tag>:
    - <prefix1>
    - <prefix2>
    ...

fields:
  <FieldName>:
    type: <rule_type>
    ...rule-specific keys...
```

- `prefix_groups` — named lists of table-name prefixes, referenced by `prefix`-type rules. Matching is lower-case `startswith`.
- `fields` — the dispatch table. Keys are field names (case-insensitive). Values are rule objects.

## Field name matching

Field names are matched **case-insensitively** against the left-hand side of each `where` predicate in the query. The YAML uses the conventional Sentinel casing (`DeviceVendor`, `EventID`) purely for readability.

## Rule types

Each field entry must declare a `type`. Five rule types are supported.

### `direct` — fixed attribution

The field is always attributed to a single fixed table, regardless of which tables the query references.

```yaml
DeviceVendor:       { type: direct, table: CommonSecurityLog }
DeviceProduct:      { type: direct, table: CommonSecurityLog }
DeviceEventClassID: { type: direct, table: CommonSecurityLog }
```

Use when the field is unambiguously owned by a single table across the entire Sentinel schema.

### `gated` — attribute only if table is in the query

The field attributes to `table` **only if** `table` is one of the tables referenced by the query. If the table is not in the query, the predicate is ignored (rather than misattributed).

```yaml
Facility:       { type: gated, table: Syslog }
EventName:      { type: gated, table: AWSCloudTrail }
OfficeWorkload: { type: gated, table: OfficeActivity }
```

Use when the field name is generic enough that it might appear on other tables under a different meaning, so attribution should only happen when the "right" table is in scope.

### `priority` — first matching candidate, in order

Try each candidate table in the declared order; pick the first one that appears in the query's tables.

```yaml
EventID:
  type: priority
  candidates: [WindowsEvent, SecurityEvent, Event]

ResourceProvider:
  type: priority
  candidates: [AzureDiagnostics, AzureActivity]
```

Use when several tables share the field but there is a clear preference order (e.g. `WindowsEvent` is preferred over the legacy `Event` table).

### `any_of` — any matching candidate

Like `priority`, but with no ordered preference: any candidate that appears in the query's tables wins. With `prefer_local: true`, candidates that appear in the **current sub-query** (e.g. inside a `union`/`join` branch) are preferred over candidates that only appear in the surrounding global query.

```yaml
ActionType:
  type: any_of
  prefer_local: true
  candidates:
    - DeviceEvents
    - DeviceFileEvents
    - DeviceProcessEvents
    - DeviceNetworkEvents
    - DeviceRegistryEvents
    - DeviceLogonInfo
    - DeviceInfo
    - DeviceImageLoadEvents
    - CloudAppEvents
    - AlertEvidence
    - AlertInfo
    - EmailEvents
    - EmailAttachmentInfo
    - EmailUrlInfo
    - IdentityLogonEvents
    - IdentityQueryEvents
    - IdentityDirectoryEvents
```

Use when several tables share the field and any of them is equally valid (e.g. the MDE/XDR `Device*Events` family).

### `prefix` — match by table-name prefix

Pick the first query table whose name **starts with** any prefix in the named `prefix_groups` entry referenced by `prefix_tag`.

```yaml
prefix_groups:
  asim:
    - asim
    - _asim
    - _im_

fields:
  EventVendor:  { type: prefix, prefix_tag: asim, skip_flag: skip_asim_vendor_product }
  EventProduct: { type: prefix, prefix_tag: asim, skip_flag: skip_asim_vendor_product }
  EventType:    { type: prefix, prefix_tag: asim }
```

Use when attribution depends on a *family* of tables rather than a fixed list (e.g. all ASIM normalized tables, regardless of which specific schema is in play).

## Optional keys

### `skip_flag`

Each rule may declare a `skip_flag` referencing a named boolean in the calling context. When that flag is set, the field is skipped entirely.

The only flag currently consumed is `skip_asim_vendor_product`, which suppresses attribution of `EventVendor` / `EventProduct` when extracting filter fields from an **ASIM parser**. ASIM parsers `extend` these columns rather than filter on them, so they should not contribute to the parser's selection criteria.

To add a new skip flag, both the YAML rule and the caller in `map_solutions_connectors_tables.py` must reference the same flag name; the YAML alone has no effect.

### `prefer_local` (`any_of` only)

When `true`, prefer candidates that appear in the current sub-query (e.g. a `union` arm or `join` side) over candidates that appear only in the surrounding global query.

## How it fits into filter-field extraction

Filter-field extraction runs in two passes:

1. **Curated pass** — every field name in `fields:` is matched against KQL where-predicates and dispatched to a table using the rule above. This pass is what the YAML controls.
2. **Schema-driven pass** — any remaining where-predicate whose field is a documented column of a referenced table (looked up in `la_table_schemas.csv` and `asim_fields.csv`) or a column introduced earlier by `| extend` is also captured.

Output columns affected: `filter_fields` (connectors, parsers, ASIM parsers) and `content_filter_fields` (content items).

## When to edit this file

- A new well-known field name should always be attributed to a specific table — add it as `direct` or `gated`.
- An existing field is being misattributed because the rule's candidate list or order is wrong — fix the list / order.
- A new prefix family of tables (analogous to the ASIM family) needs a single dispatch rule — add a `prefix_groups` entry and reference it via `prefix_tag`.
- A field should be ignored in a specific extraction context — wire a new `skip_flag` (and add the matching boolean in the caller).

If the only thing you need is "this query uses column X of table Y", you generally don't need to edit the YAML — the schema-driven pass will pick it up automatically as long as column X is documented in `la_table_schemas.csv` or `asim_fields.csv`.

## Related files

- [`map_solutions_connectors_tables.md`](map_solutions_connectors_tables.md#filter-field-extraction) — full filter-field extraction documentation.
- [`csv/connectors.md`](csv/connectors.md), [`csv/parsers.md`](csv/parsers.md), [`csv/asim_parsers.md`](csv/asim_parsers.md), [`csv/content_items.md`](csv/content_items.md) — CSV reference pages whose `filter_fields` columns are populated using these rules.
- [`solution_analyzer_overrides.csv`](../solution_analyzer_overrides.csv) — the other user-editable configuration file (per-entity overrides for `collection_method`, `category`, `support_tier`, synthetic connectors, and documentation overrides).
