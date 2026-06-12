# ASIM Field Information Collector

**Script:** `collect_asim_fields.py`

## Overview

Collects ASIM (Advanced Security Information Model) field information from three sources and merges them into unified CSV files:

1. **Microsoft Learn documentation** — Schema definitions, entity definitions, logical types, and vendor/product lists parsed from published markdown
2. **ASimTester.csv** — Field definitions used by the ASIM testing framework, providing an independent validation source
3. **table_schemas.csv** — Physical table column schemas from DCR definitions and Azure Monitor documentation

The script produces normalized CSV files that serve as the data source for the ASIM Schema Browser and future ASIM documentation.

## Prerequisites

- Python 3.7 or higher
- `requests` library for HTTP fetching

```bash
pip install requests
```

## Running the Script

From the `Tools/Solutions Analyzer` directory:

```bash
# Full run: collect docs + merge tester + merge physical schemas
python collect_asim_fields.py

# Skip tester merge (docs only + physical schemas)
python collect_asim_fields.py --skip-tester

# Skip physical schema merge (docs only + tester)
python collect_asim_fields.py --skip-physical

# Custom output directory
python collect_asim_fields.py --output ./reports

# Refresh cache and run
python collect_asim_fields.py --refresh-cache

# Custom paths for input CSVs
python collect_asim_fields.py --tester-path /path/to/ASimTester.csv --table-schemas-path /path/to/table_schemas.csv
```

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--output`, `-o` | Script directory | Output directory for CSV and report files |
| `--docs-path` | learn.microsoft.com | Base URL or local path for documentation |
| `--tester-path` | `ASIM/dev/ASimTester/ASimTester.csv` | Path to ASimTester.csv |
| `--table-schemas-path` | `table_schemas.csv` in script directory | Path to table_schemas.csv |
| `--skip-tester` | `False` | Skip merging ASIM tester data |
| `--skip-physical` | `False` | Skip merging physical table schema data |
| `--refresh-cache` | `False` | Clear cache and fetch fresh content |
| `--skip-cache` | `False` | Skip cache for this run only |
| `--cache-ttl` | `604800` (1 week) | Cache time-to-live in seconds |
| `--cache-dir` | `.cache` | Directory for cache files |
| `--no-report` | `False` | Skip generating the summary report |
| `--quiet`, `-q` | `False` | Suppress verbose output |

## Output Files

See [`csv/`](csv/README.md) for full per-file documentation.

| File | Description | Doc |
|------|-------------|-----|
| `asim_fields.csv` | Complete schema field information (docs + tester + physical tables) | [`csv/asim_fields.md`](csv/asim_fields.md) |
| `asim_entity_fields.csv` | Entity field information (User / Device / Application) | [`csv/asim_entity_fields.md`](csv/asim_entity_fields.md) |
| `asim_logical_types.csv` | Logical types with allowed enumerated values | [`csv/asim_logical_types.md`](csv/asim_logical_types.md) |
| `asim_vendors_products.csv` | Allowed `EventVendor` and `EventProduct` values | [`csv/asim_vendors_products.md`](csv/asim_vendors_products.md) |
| `asim_extraction_failures.csv` | Diagnostic report of extraction problems | [`csv/asim_extraction_failures.md`](csv/asim_extraction_failures.md) |
| `asim_fields_summary.md` | Summary report with field counts per schema and discrepancy statistics |  |

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Microsoft Learn Documentation                    │
│  (https://learn.microsoft.com/en-us/azure/sentinel/normalization-*) │
└────────────────────────────────────┬────────────────────────────────┘
                                     │ Fetch (with caching)
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      collect_asim_fields.py                          │
│                                                                      │
│  Phase 1: Collect from Documentation                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ Schema Discovery│  │ Entity Discovery │  │ Logical Type Parser │  │
│  │ (from overview) │  │ (from overview)  │  │ (from overview)     │  │
│  └────────┬────────┘  └────────┬─────────┘  └──────────┬──────────┘  │
│           │                    │                       │             │
│           ▼                    ▼                       ▼             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ Schema Parser   │  │ Entity Parser   │  │ Vendor/Product      │  │
│  │ (per schema doc)│  │ (per entity doc)│  │ Parser              │  │
│  └────────┬────────┘  └────────┬─────────┘  └──────────┬──────────┘  │
│           │                    │                       │             │
│  Phase 2: Merge ASimTester.csv                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │ • Match by (schema, field_name)                              │    │
│  │ • Dedup: only populate tester_* columns when values differ   │    │
│  │ • Create TesterOnly entries for unmatched fields             │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  Phase 3: Merge table_schemas.csv                                   │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │ • Map table names to schemas via ASIM_TABLE_TO_SCHEMA        │    │
│  │ • Exclude _CL and vendor-specific tables                     │    │
│  │ • Dedup: only populate physical_table_type when differs      │    │
│  │ • Create PhysicalTableOnly entries for unmatched columns     │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  Phase 4: Write Output CSVs                                         │
└────────────────────────────────────┬────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           CSV Output Files                           │
│  asim_fields.csv │ asim_entity_fields.csv │ asim_logical_types.csv  │
│  asim_vendors_products.csv │ asim_extraction_failures.csv           │
│  asim_fields_summary.md                                              │
└─────────────────────────────────────────────────────────────────────┘
```

### Phase 1: Documentation Collection

The script fetches ASIM documentation from Microsoft Learn:

1. **Schema Discovery** — Parses `normalization-about-schemas.md` to find schema names, versions, and doc URLs
2. **Schema Parsing** — For each schema, fetches the markdown and extracts field definitions from tables
3. **Entity Collection** — Fetches User, Device, and Application entity definitions
4. **Logical Types** — Extracts logical type definitions with allowed values
5. **Common Fields** — Collects fields shared across all schemas
6. **Post-processing** — Calculates hash aliases, inherits NetworkSession fields into WebSession

### Phase 2: ASIM Tester Merge

Merges data from `ASIM/dev/ASimTester/ASimTester.csv`:

- **Matching**: Fields are matched by `(schema, field_name)` key
- **Deduplication**: Tester columns (`tester_class`, `tester_type`, `tester_logical_type`, `tester_allowed_values`) are only populated when they **differ** from the documentation values, reducing noise
- **`tester_aliased`**: Always populated when present (maps to the `Aliased` column which has no doc equivalent)
- **Tester-only fields**: Fields in the tester but not in docs are added with `source='TesterOnly'`

### Phase 3: Physical Table Schema Merge

Merges data from `table_schemas.csv` (generated by `map_solutions_connectors_tables.py`):

- **Table-to-schema mapping**: Physical ASIM table names (e.g., `ASimDnsActivityLogs`) are mapped to schema names (e.g., `Dns`) using the `ASIM_TABLE_TO_SCHEMA` dictionary
- **Exclusions**: Vendor-specific tables (e.g., `ASimDnsMicrosoftNXLog`) and `_CL` variants are excluded
- **Deduplication**: `physical_table_type` is only populated when it differs from the doc `physical_type`
- **Physical-only fields**: Columns in physical tables but not in docs/tester are added with `source='PhysicalTableOnly'`

### Table-to-Schema Mapping

| Physical Table | Schema |
|---------------|--------|
| `ASimAlertEventLogs` | AlertEvent |
| `ASimAuditEventLogs` | AuditEvent |
| `ASimAuthenticationEventLogs` | Authentication |
| `ASimDhcpEvent`, `ASimDhcpEventLogs` | DhcpEvent |
| `ASimDns`, `ASimDnsActivityLogs` | Dns |
| `ASimFileEventLogs` | FileEvent |
| `ASimNetworkSessionLogs` | NetworkSession |
| `ASimProcessEventLogs` | ProcessEvent |
| `ASimRegistryEventLogs` | RegistryEvent |
| `ASimUserManagementActivityLogs` | UserManagement |
| `ASimWebSessionLogs` | WebSession |

## CSV Field Definitions

See [csv/](csv/README.md) for full per-file column documentation:

- [csv/asim_fields.md](csv/asim_fields.md)
- [csv/asim_entity_fields.md](csv/asim_entity_fields.md)
- [csv/asim_logical_types.md](csv/asim_logical_types.md)
- [csv/asim_vendors_products.md](csv/asim_vendors_products.md)
- [csv/asim_extraction_failures.md](csv/asim_extraction_failures.md)

The sim_fields_summary.md markdown report (not a CSV) contains field counts per schema, fields by source (SchemaDoc, TesterOnly, PhysicalTableOnly, …), fields by class (Mandatory, Recommended, …), and discrepancy counts between the documentation, tester, and physical-table sources.

## Caching

The script uses file-based caching to minimize network requests:

- Cache files stored in `.cache/` directory (consistent with other Solutions Analyzer scripts)
- Default TTL of 1 week (604800 seconds)
- MD5 hash of URL used as cache key
- Use `--refresh-cache` to force fresh fetches
- Use `--skip-cache` to bypass cache for a single run

## Dependencies

- **`requests`** — HTTP library for fetching documentation (install via `pip install requests`)
- **`table_schemas.csv`** — Generated by `map_solutions_connectors_tables.py` (required for Phase 3)
- **`ASimTester.csv`** — Located in the Azure-Sentinel repo at `ASIM/dev/ASimTester/ASimTester.csv` (required for Phase 2)

## Usage in Pipeline

This script is independent of the main documentation generation pipeline. Recommended order:

1. **`collect_table_info.py`** — Generate `tables_reference.csv` and `la_table_schemas.csv`
2. **`map_solutions_connectors_tables.py`** — Generate `table_schemas.csv` (needed for Phase 3)
3. **`collect_asim_fields.py`** — Generate ASIM field CSVs
4. **`generate_asim_browser.py`** — Generate interactive ASIM browser (uses `asim_fields.csv` and `asim_parsers.csv`)
