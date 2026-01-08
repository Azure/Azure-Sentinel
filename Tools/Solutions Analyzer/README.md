# Azure Sentinel Solutions Analyzer

This directory contains five complementary tools for analyzing Microsoft Sentinel Solutions:

1. **[`map_solutions_connectors_tables.py`](script-docs/map_solutions_connectors_tables.md)** - Extracts and maps data connector definitions to their ingestion tables, producing CSV reports with solution metadata
2. **[`collect_table_info.py`](script-docs/collect_table_info.md)** - Collects comprehensive table metadata from Microsoft Azure Monitor documentation
3. **[`generate_connector_docs.py`](script-docs/generate_connector_docs.md)** - Generates browsable markdown documentation from the CSV data with AI-rendered setup instructions and enriched table information
4. **[`generate_solutions_with_connectors_report.py`](script-docs/generate_solutions_with_connectors_report.md)** - Generates summary reports of solutions with connectors in markdown and CSV formats
5. **[`solution_analyzer_upload_to_kusto.py`](script-docs/upload_to_kusto.md)** - Uploads the generated CSV files to Azure Data Explorer (Kusto) for querying and analysis

## Prerequisites

### Clone the Azure-Sentinel Repository

The main analysis script (`map_solutions_connectors_tables.py`) and documentation generator require the [Azure-Sentinel GitHub repository](https://github.com/Azure/Azure-Sentinel) to be cloned locally:

```bash
# Clone the repository
git clone https://github.com/Azure/Azure-Sentinel.git

# Navigate to the Tools directory
cd Azure-Sentinel/Tools/Solutions\ Analyzer

# Keep the repository updated
git pull origin master
```

### Python Environment

- Python 3.7 or higher
- Required packages vary by script (see individual documentation)

**Quick install for all scripts:**
```bash
pip install requests json5 azure-kusto-data azure-kusto-ingest azure-identity
```

## Quick Start

**Pre-generated files are already available in this directory:**
- [`solutions_connectors_tables_mapping.csv`](solutions_connectors_tables_mapping.csv) - Main mapping of connectors to tables with full metadata
- [`connectors.csv`](connectors.csv) - All connectors with collection method analysis
- [`solutions.csv`](solutions.csv) - All solutions with metadata
- [`tables.csv`](tables.csv) - All tables with solution/connector references
- [`content_tables_mapping.csv`](content_tables_mapping.csv) - **NEW:** Mapping of content items (analytics rules, playbooks, etc.) to tables with read/write indicators
- [`solutions_connectors_tables_mapping_simplified.csv`](solutions_connectors_tables_mapping_simplified.csv) - Simplified mapping with key fields only
- [`solutions_connectors_tables_issues_and_exceptions_report.csv`](solutions_connectors_tables_issues_and_exceptions_report.csv) - Issues and exceptions report
- [`tables_reference.csv`](tables_reference.csv) - Comprehensive table metadata from Azure Monitor documentation

**📍 Connector Reference Documentation (External Repository):**

> **Note:** The generated documentation has been moved to a separate repository to reduce the size of the Azure-Sentinel repo.
> 
> 🔗 **Full documentation:** [https://github.com/oshezaf/sentinelninja/tree/main/Solutions%20Docs](https://github.com/oshezaf/sentinelninja/tree/main/Solutions%20Docs)

| Documentation | Direct Link |
|:--------------|:------------|
| **Solutions Index** | [View Solutions](https://github.com/oshezaf/sentinelninja/blob/main/Solutions%20Docs/solutions-index.md) |
| **Connectors Index** | [View Connectors](https://github.com/oshezaf/sentinelninja/blob/main/Solutions%20Docs/connectors-index.md) |
| **Tables Index** | [View Tables](https://github.com/oshezaf/sentinelninja/blob/main/Solutions%20Docs/tables-index.md) |
| **Content Index** | [View Content Items](https://github.com/oshezaf/sentinelninja/blob/main/Solutions%20Docs/content/content-index.md) |

You can also generate documentation locally using the `--output-dir` parameter (see below).

The documentation includes AI-rendered setup instructions extracted from connector UI definitions.

## Running the Scripts

### Recommended Order

For a complete refresh of all data:

```bash
# 1. Collect table metadata from Azure Monitor docs
python collect_table_info.py

# 2. Generate connector/solution/table mappings (uses tables_reference.csv)
python map_solutions_connectors_tables.py

# 3. Generate documentation to a specific location
python generate_connector_docs.py --skip-input-generation --output-dir "path/to/output"
```

Or let the documentation generator handle everything:

```bash
# This automatically runs steps 1-2 before generating docs
python generate_connector_docs.py --output-dir "path/to/output"
```

### Command Line Options for generate_connector_docs.py

| Option | Description |
|:-------|:------------|
| `--output-dir <path>` | Output directory for generated documentation (default: connector-docs/) |
| `--skip-input-generation` | Skip running input CSV generation scripts |
| `--solutions <name1> <name2>` | Generate docs only for specific solutions |
| `--solutions-dir <path>` | Path to Solutions directory for reading additional markdown |

### Quick Reference

| Script | Purpose | Key Output |
|--------|---------|------------|
| [`collect_table_info.py`](script-docs/collect_table_info.md) | Fetch table metadata from Azure Monitor docs | `tables_reference.csv` |
| [`map_solutions_connectors_tables.py`](script-docs/map_solutions_connectors_tables.md) | Map connectors and content items to tables | `connectors.csv`, `tables.csv`, `solutions.csv`, `content_items.csv`, `content_tables_mapping.csv` |
| [`generate_connector_docs.py`](script-docs/generate_connector_docs.md) | Generate markdown documentation | `connector-docs/` directory |
| [`generate_solutions_with_connectors_report.py`](script-docs/generate_solutions_with_connectors_report.md) | Generate solutions summary report | `solutions_with_connectors_report.md`, `solutions_with_connectors.csv` |
| [`upload_to_kusto.py`](script-docs/upload_to_kusto.md) | Upload CSVs to Kusto | Kusto tables |

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Azure Monitor Documentation                      │
│   (tables-category, tables-feature-support, Defender XDR schema)    │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │   collect_table_info.py  │
                    └──────────────────────────┘
                                   │
                                   ▼
                      ┌────────────────────────┐
                      │  tables_reference.csv  │
                      └────────────────────────┘
                                   │
┌─────────────────────────────┐    │
│   Azure-Sentinel Solutions  │    │
│   (Solutions/ directory)    │    │
└─────────────────────────────┘    │
              │                    │
              ▼                    ▼
   ┌───────────────────────────────────────┐
   │   map_solutions_connectors_tables.py  │
   └───────────────────────────────────────┘
              │
              ▼
   ┌─────────────────────────────────────┐
   │  connectors.csv, tables.csv,        │
   │  solutions.csv, mapping CSVs        │
   └─────────────────────────────────────┘
              │
              ▼
   ┌───────────────────────────────────────┐
   │      generate_connector_docs.py       │
   └───────────────────────────────────────┘
              │
              ▼
   ┌───────────────────────────────────────┐
   │   connector-docs/ (Markdown docs)     │
   └───────────────────────────────────────┘
```

## Override System

Both `map_solutions_connectors_tables.py` and `collect_table_info.py` support an override system that allows you to modify field values in the output based on pattern matching. The override file (`solution_analyzer_overrides.csv`) uses regex patterns to match entities and set field values.

Example use cases:
- Set `collection_method` to AMA for specific tables (e.g., Syslog, CommonSecurityLog)
- Assign `category` to tables based on naming patterns (e.g., all AWS* tables → AWS)
- Set `support_tier` for tables based on their associated solutions

See [Override System documentation](script-docs/map_solutions_connectors_tables.md#override-system) for details.

## Documentation

- **[Solution Connector Tables Analyzer](script-docs/map_solutions_connectors_tables.md)** - Full documentation for the main mapping script
- **[Table Reference Collector](script-docs/collect_table_info.md)** - Documentation for the Azure Monitor metadata collector
- **[Connector Documentation Generator](script-docs/generate_connector_docs.md)** - Documentation for the markdown generator
- **[Kusto Upload Script](script-docs/upload_to_kusto.md)** - Documentation for uploading to Azure Data Explorer

---

## Version History

### v6.0 - Solution Logos, Descriptions, and Enhanced Metadata

**The solution documentation now includes information from the `Data/Solution_*.json` files in addition to `SolutionMetadata.json`:**
- **Solution logos** now appear on solution pages and in the solutions index for visual identification
- **Solution descriptions**, **Dependencies** and **Author Information** are included in each solution page.
- **Official solution names** from Solution JSON are used (may differ from folder names)
- **Summary rules** now supported as a new content type

Items found by scanning but not listed in Solution JSON are marked with ⚠️ in documentation

**New CSV Fields in solutions.csv:**
- `solution_logo_url`: URL to the solution's logo image
- `solution_description`: Full solution description
- `solution_version`: Version from Solution JSON
- `solution_author_name`: Author name from Solution JSON
- `solution_dependencies`: Semicolon-separated list of dependent solution IDs 

**Bug Fixes:**
- Content item filenames use hash-based uniqueness to prevent collisions
- Fixed Solution JSON key variant handling (e.g., `AnalyticsRules` vs `Analytic Rules`)
- Excluded Images, Templates, and Training folders from content scanning

### v5.2 - Bug Fixes and Improvements

- Fixed `sanitize_filename()` to handle Windows-invalid characters (`: * ? " < > |`), enabling ~20 previously-missing content files
- Fixed content item filename collisions by including solution name and adding collision detection
- Fixed table page case-insensitive filename collisions on Windows
- Improved index page statistics with accurate table counts and content item metrics

### v5.1 - Documentation Overrides and Additional Information

**Documentation-Only Overrides:**
- Added support for `additional_information` field in override CSV for curated documentation links
- Tables, connectors, and solution pages now display Additional Information sections with links to Microsoft Learn documentation
- DOC_OVERRIDES dictionary supports table, connector, and solution entity types with regex pattern matching

### v5.0

**Content Item Documentation:**
- Added individual documentation pages for each content item (analytics rules, hunting queries, playbooks, workbooks, etc.)
- Each content item page includes: description, type, solution link, severity, tactics, techniques, tables used, and source file link
- New Content Index page (`content-index.md`) provides overview with links to type-specific indexes
- Type-specific index pages: `analytic-rules.md`, `hunting-queries.md`, `playbooks.md`, `workbooks.md`, `parsers.md`, `watchlists.md`
- Analytic rules (2000+ items) have letter-based sub-pages (`analytic-rules-a.md`, etc.) for better navigation
- Other content types use per-letter sections within a single page with proper anchor links
- All content item references across solution and table pages now link to their dedicated documentation pages

**Content Item Table Extraction:**
- Added table extraction from solution content items (analytics rules, hunting queries, playbooks, workbooks, watchlists, summary rules)
- Extracts tables from KQL queries in YAML files (Detections, Hunting Queries) and JSON files (Playbooks, Workbooks)
- Solution pages now show tables used by each content item type
- Playbook tables show read/write usage indicators: `(read)`, `(write)`, `(read/write)`
- Solution README.md files are now included in solution documentation pages
- **Internal Use Tables**: Custom tables (_CL suffix) that are written by playbooks AND read by non-playbook content (analytics, hunting, workbooks) are marked as "Internal Use Tables"

**Table Index Improvements:**
- Tables index now includes ALL tables from Azure Monitor reference (`tables_reference.csv`), even if not used by any solution or connector
- Index shows 1900+ tables (800+ ingested by connectors, 1000+ referenced by content only)
- Tables can have empty solutions/connectors columns if they exist in Azure Monitor but aren't used by any Sentinel solution

**Documentation Formatting:**
- Content item table lists now use line breaks (`<br>`) instead of commas for better readability
- Solutions/connectors lists in table documentation pages now use bullet points
- Playbook tables display usage indicators showing if tables are read from, written to, or both
- Navigation on all pages now includes Content Index link

### v4.2

- Added `solution_analyzer_upload_to_kusto.py` script to upload CSV files to Azure Data Explorer (Kusto)
  - Uses managed streaming ingestion for fast uploads (same method as ADX "Get Data" UI)
  - Creates 6 lookup tables: table reference, connectors, tables, solutions, mapping, and full mapping
  - Supports Azure CLI authentication via DefaultAzureCredential
  - Includes dry-run mode for previewing changes
- Added **override system** for customizing output field values
  - Override file uses CSV format with Entity, Pattern, Field, Value columns
  - Supports regex pattern matching (case insensitive, full match) including negative lookbehind
  - Can override fields in tables, connectors, or solutions data
  - Example use cases: set collection_method to AMA for specific tables, categorize tables by naming pattern
  - Added `--overrides-csv` command line argument to both `map_solutions_connectors_tables.py` and `collect_table_info.py`
  - Both scripts share the same override file (`solution_analyzer_overrides.csv`) for consistent categorization
- Added `support_tier` and `collection_method` columns to `tables.csv` and `tables_reference.csv`
  - `support_tier` derived from associated solutions
  - `collection_method` determined from resource_types (virtualmachines → AMA) and overrides
- Changed `--fetch-details` to `--skip-details` in `collect_table_info.py` (details fetched by default)
- Split documentation into separate files per script in `script-docs/` directory
- Added detailed prerequisites section with repository cloning instructions

### v4.1

- Added additional documentation sources for generated documentation:
  - Solution pages now include Release Notes from `ReleaseNotes.md` files in solution directories
  - Connector pages now include associated markdown documentation (any `.md` file) when available
- Improved connector documentation file association with multiple strategies:
  - Dedicated subfolder: Any `.md` file in connector's subfolder (prefers README.md)
  - Filename match: `.md` files containing connector name in the filename
  - Single-connector fallback: Any `.md` file when solution has only one connector
- Added `--solutions-dir` command line argument for configurable solution directory path
- Improved collection method detection priority:
  - Fixed WindowsFirewall to correctly detect as MMA (special case)
  - Fixed OktaSSOv2 to correctly detect as CCF (content patterns now higher priority)
  - Fixed Azure `_CCP` connectors to correctly detect as Azure Diagnostics
  - Separated CCF detection into content patterns (high priority) and name patterns (lower)
  - Azure Diagnostics patterns now checked before CCF name-based patterns

### v4.0

- Added comprehensive collection method detection for connectors
  - Analyzes connector ID, title, description, JSON content, and filename patterns
  - Detects: Codeless Connector Framework (CCF/CCP), Azure Function, Azure Monitor Agent (AMA), Log Analytics Agent (MMA), Azure Diagnostics, REST API, Native integrations
  - Includes detection reason explaining how method was determined
- Added new CSV outputs for better data organization:
  - `connectors.csv` - All connectors keyed by connector_id with collection method
  - `solutions.csv` - All solutions keyed by solution_name with metadata
  - `tables.csv` - All tables keyed by table_name with solution/connector counts
  - `solutions_connectors_tables_mapping_simplified.csv` - Simplified mapping with key fields only
- Collection method information available in `connectors.csv` and connector documentation
- Enhanced `generate_connector_docs.py` to display collection method in connector index and pages
- Added support for multiple Data Connectors folder naming conventions:
  - `Data Connectors` (standard, with space)
  - `DataConnectors` (no space) - adds solutions such as Alibaba Cloud, CyberArkEPM, IronNet IronDefense, MarkLogicAudit, Open Systems, PDNS Block Data Connector, SlashNext
  - `Data Connector` (singular) - adds IoTOTThreatMonitoringwithDefenderforIoT
- Added handling for ARM template variable references in connector `id` field
  - Connectors with `[variables(...)]` in id now generate ID from title
  - Adds connectors such as 1Password, CiscoMeraki, Cortex XDR, CustomLogsAma, GCP Audit Logs, Okta SSO
- Added `connector_id_generated` column to track when connector ID was auto-generated from title
- Added connectors with `no_table_definitions` to output with empty table field (previously excluded)
  - Adds connectors such as Azure Resource Graph, Microsoft 365 Assets, Microsoft Entra ID Assets
- Added `collect_table_info.py` script to collect comprehensive table metadata from Azure Monitor documentation
  - Fetches from Azure Monitor Logs reference, Defender XDR schema, feature support, and ingestion API pages
  - Includes transformation support, basic logs eligibility, retention info, and documentation links
  - Uses file-based caching with configurable TTL (default: 1 week)
- Enhanced `generate_connector_docs.py` with table reference integration:
  - Now automatically calls input generation scripts before documentation generation
  - Added `--tables-csv` argument for tables reference CSV path
  - Added `--connectors-csv` argument for connectors CSV path (collection method)
  - Added `--skip-input-generation` flag to use existing CSV files
  - Tables index now shows transformation and ingestion API support columns
  - Individual table pages generated for ALL tables (not just multi-solution tables)
  - Table pages include enriched metadata: description, category, basic logs eligibility, transformation support, ingestion API support, retention info, and documentation links
  - Connector pages now show transformation and ingestion API support for each table

### v3.0

- Added `connector_instruction_steps` and `connector_permissions` fields to CSV output
- Added AI-rendered connector setup instructions from UI definitions
- Added individual table detail pages for tables with multiple solutions or connectors
- Improved tables index with limited inline display and clickable "+X more" links

### v2.0

- Added parser resolution and context-aware table detection
- Enhanced JSON parsing tolerance for malformed connector definitions
- Flattened metadata extraction from nested solution structures
- Added GitHub URLs for all file references
- Improved error handling and validation

### v1.0

- Initial release with basic table detection from connector JSON files
- CSV output with solution, connector, and table mappings
- Issues and exceptions reporting
