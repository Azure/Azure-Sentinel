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

### tables_reference.csv

Comprehensive CSV with table metadata:

| Column | Description | Data Source |
|--------|-------------|-------------|
| `table_name` | Table name | All sources |
| `description` | Table description from documentation | Azure Monitor individual pages, Defender XDR schema |
| `category` | Table category (e.g., Security, Audit, Azure Resources) | Azure Monitor tables-category |
| `support_tier` | Support tier (from overrides) | Override system |
| `collection_method` | Data collection method (from resource_types or overrides) | Azure Monitor individual pages, Override system |
| `solutions` | Associated Log Analytics solutions | Azure Monitor individual pages |
| `resource_types` | Azure resource types that emit to this table | Azure Monitor individual pages |
| `table_type` | Table type (e.g., Microsoft, Azure, Custom) | Azure Monitor individual pages |
| `source_azure_monitor` | Whether table is in Azure Monitor reference | Azure Monitor tables-category |
| `source_defender_xdr` | Whether table is in Defender XDR schema | Defender XDR schema |
| `xdr_only` | Whether table is only available in Defender XDR (not in Azure Monitor) | Computed (in XDR but not Azure Monitor) |
| `source_feature_support` | Whether table has feature support info | Tables feature support |
| `source_ingestion_api` | Whether table supports ingestion API | Logs Ingestion API overview |
| `source_sentinel_tables` | Whether table has Sentinel connector reference info | Sentinel tables/connectors include |
| `azure_monitor_doc_link` | Link to Azure Monitor documentation | Azure Monitor tables-category |
| `defender_xdr_doc_link` | Link to Defender XDR documentation | Defender XDR schema |
| `basic_logs_eligible` | Whether table supports Basic Logs plan | Azure Monitor individual pages |
| `supports_transformations` | Whether ingestion-time transformations are supported | Tables feature support (primary), Sentinel tables/connectors (fallback) |
| `ingestion_api_supported` | Whether Data Collector API ingestion is supported | Logs Ingestion API overview |
| `lake_only_supported` | Whether lake-only ingestion is supported | Sentinel tables/connectors include |

## Transformation Support Enrichment

The `supports_transformations` field is populated from two sources:
1. **Primary**: [Tables Feature Support](https://learn.microsoft.com/azure/azure-monitor/logs/tables-feature-support) page
2. **Fallback**: [Sentinel Tables/Connectors Reference](https://learn.microsoft.com/azure/sentinel/data-connectors-reference) (used when primary source has no data)

When both sources have data for a table, the script validates consistency and generates a `transformation_support_mismatch_report.md` file if any discrepancies are found.

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
| Defender XDR Schema | [advanced-hunting-schema-tables](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-schema-tables) | Table names, descriptions, Defender documentation links |
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

1. **`collect_table_info.py`** - Generate `tables_reference.csv` with Azure Monitor metadata
2. **`map_solutions_connectors_tables.py`** - Generate connector mappings (uses `tables_reference.csv`)
3. **`generate_connector_docs.py`** - Generate documentation (uses both CSVs)

The documentation generator (`generate_connector_docs.py`) automatically runs the first two scripts if needed, unless `--skip-input-generation` is specified.
