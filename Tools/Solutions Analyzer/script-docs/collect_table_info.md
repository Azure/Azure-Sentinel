# Table Reference Collector

**Script:** `collect_table_info.py`

## Overview

Collects comprehensive table metadata from Microsoft documentation sources:

- Azure Monitor Logs table reference
- Microsoft Defender XDR schema reference
- Table feature support information
- Ingestion API compatibility
- Microsoft Sentinel data connectors reference (lake-only ingestion, DCR support)

The collected data is saved to `tables_reference.csv` which is used by:
- **`map_solutions_connectors_tables.py`** - To enrich table metadata in `tables.csv` and determine collection methods
- **`generate_connector_docs.py`** - To include table metadata in the generated documentation

## Prerequisites

- Python 3.7 or higher
- `requests` library for HTTP fetching

```bash
pip install requests
```

> **Note:** This script does not require the Azure-Sentinel repository to be cloned - it fetches data directly from Microsoft documentation.

## Running the Script

From the `Tools/Solutions Analyzer` directory:

```bash
# Full run (fetches individual table details, uses cache)
python collect_table_info.py

# Quick run (skip individual table pages)
python collect_table_info.py --skip-details
```

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--output`, `-o` | Script directory | Output directory for CSV and report files |
| `--skip-details` | `False` | Skip fetching details from individual table pages (faster but less data) |
| `--max-details` | `0` (all) | Maximum number of table detail pages to fetch (0=all, useful for testing) |
| `--refresh-cache` | `False` | Clear cache and fetch fresh content |
| `--skip-cache` | `False` | Skip cache for this run only |
| `--cache-ttl` | `604800` | Cache time-to-live in seconds (default: 1 week) |
| `--cache-dir` | `.cache` | Directory for cache files |
| `--overrides-csv` | `solution_analyzer_overrides.csv` | Path to overrides CSV file for field value overrides |
| `--quiet`, `-q` | `False` | Suppress verbose output |

## Output Files

See [`csv/`](csv/README.md) for full per-file documentation.

| File | Description | Doc |
|------|-------------|-----|
| `tables_reference.csv` | Comprehensive table metadata fetched from Microsoft documentation | [`csv/tables_reference.md`](csv/tables_reference.md) |
| `la_table_schemas.csv` | Column-level schemas from Azure Monitor and Defender XDR rendered HTML pages (only when `--skip-details` is **not** used) | [`csv/la_table_schemas.md`](csv/la_table_schemas.md) |

## Transformation Support Enrichment

The `supports_transformations` field is populated from two sources:
1. **Primary**: [Tables Feature Support](https://learn.microsoft.com/azure/azure-monitor/logs/tables-feature-support) page
2. **Fallback**: [Sentinel Tables/Connectors Reference](https://learn.microsoft.com/azure/sentinel/data-connectors-reference) (used when primary source has no data)

When both sources have data for a table, the script validates consistency and generates a `transformation_support_mismatch_report.md` file if any discrepancies are found.

## Custom Log Table Rules

Custom log tables (tables with a `_CL` suffix) are not listed in Microsoft's standard reference documentation, so their capabilities cannot be determined from the parsed sources. The following rules are applied after merging all sources:

- **Ingestion API**: All `_CL` tables are marked as supporting the Ingestion API (`ingestion_api_supported = Yes`), since custom log tables are created via DCR-based ingestion.
- **Transformations**: `_CL` tables that support lake-only ingestion are also marked as supporting transformations, since lake-only ingestion requires DCR pipeline support which includes transformations.

## Override System

The script supports the same override system as `map_solutions_connectors_tables.py`. Overrides can be used to:
- Set `collection_method` for specific tables
- Set `support_tier` for specific tables
- Assign `category` values based on table name patterns

See [map_solutions_connectors_tables.md](map_solutions_connectors_tables.md#override-system) for details on the override file format.

## Caching

The script uses file-based caching to minimize network requests:

- Cache files stored in `.cache/` directory
- Default TTL of 1 week (604800 seconds)
- MD5 hash of URL used as cache key
- Use `--clear-cache` to force fresh fetches

### Caching Benefits

- Faster subsequent runs (seconds vs minutes)
- Reduced load on Microsoft documentation servers
- Consistent results during development/testing

### Managing the Cache

```bash
# Clear cache and fetch fresh data
python collect_table_info.py --refresh-cache

# Use shorter cache TTL (e.g., 1 day = 86400 seconds)
python collect_table_info.py --cache-ttl 86400
```

## Data Sources

The script collects table information from the following Microsoft documentation pages:

| Source | URL | Information Collected |
|--------|-----|----------------------|
| Azure Monitor Tables (by category) | [tables-category](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables-category) | Table names, categories, documentation links |
| Individual Table Reference Pages | [tables/{tablename}](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/) | Description, categories, solutions, resource types, basic log eligibility |
| Rendered Table Reference Pages | [tables/{tablename}](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/) (HTML) | Column names, types, descriptions (for `la_table_schemas.csv`) |
| Defender XDR Schema | [advanced-hunting-schema-tables](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-schema-tables) | Table names, descriptions, Defender documentation links |
| Rendered Defender XDR Pages | [advanced-hunting-{tablename}-table](https://learn.microsoft.com/en-us/defender-xdr/) (HTML) | Column names, types, descriptions (for `la_table_schemas.csv`) |
| Tables Feature Support | [tables-feature-support](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tables-feature-support) | Tables that support ingestion-time transformations |
| Logs Ingestion API | [logs-ingestion-api-overview](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview) | Tables that support ingestion via Data Collector API |
| Sentinel Tables/Connectors | [sentinel-tables-connectors](https://learn.microsoft.com/en-us/azure/sentinel/data-connectors-reference) (include file) | DCR support and lake-only ingestion support |

## Collection Method Detection

When `--skip-details` is not used, the script determines `collection_method` based on table properties:

1. **resource_types contains "virtualmachines"** → `AMA` (Azure Monitor Agent)
2. **category is "Azure Resources"** → `Azure Diagnostics`
3. **Overrides** → Values from `solution_analyzer_overrides.csv`

This information is then used by `map_solutions_connectors_tables.py` when determining collection methods for connectors.

## Usage in Pipeline

The recommended order of script execution:

1. **`collect_table_info.py`** - Generate `tables_reference.csv` (table metadata) and `la_table_schemas.csv` (column schemas)
2. **`map_solutions_connectors_tables.py`** - Generate connector mappings (uses `tables_reference.csv` and `la_table_schemas.csv`)
3. **`generate_connector_docs.py`** - Generate documentation (uses all CSVs)

The documentation generator (`generate_connector_docs.py`) automatically runs the first two scripts if needed, unless `--skip-input-generation` is specified.
