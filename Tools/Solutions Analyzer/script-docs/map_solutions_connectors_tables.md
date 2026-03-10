# Solution Connector Tables Analyzer

**Script:** `map_solutions_connectors_tables.py`

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Running the Script](#running-the-script)
- [Command Line Options](#command-line-options)
- [Override System](#override-system)
  - [Synthetic Connector Overrides](#synthetic-connector-overrides)
- [Output Files](#output-files)
  - [connectors.csv](#1-connectorscsv-connector-details-with-collection-method)
  - [solutions.csv](#2-solutionscsv-solution-details)
  - [tables.csv](#3-tablescsv-table-metadata)
  - [solutions_connectors_tables_mapping_simplified.csv](#4-solutions_connectors_tables_mapping_simplifiedcsv-simplified-mapping)
  - [content_items.csv](#5-content_itemscsv-content-item-details)
  - [content_tables_mapping.csv](#6-content_tables_mappingcsv-content-item-to-table-mapping)
  - [parsers.csv](#7-parserscsv-parser-details)
  - [asim_parsers.csv](#8-asim_parserscsv-asim-parser-details)
  - [solution_dependencies.csv](#9-solution_dependenciescsv-solution-dependency-mapping)
  - [table_schemas.csv](#10-table_schemascsv-table-column-schemas)
  - [Issues Report](#11-solutions_connectors_tables_issues_and_exceptions_reportcsv-issues-report)
  - [Backward Compatibility](#12-solutions_connectors_tables_mappingcsv-backward-compatibility)
- [Azure Marketplace Availability](#azure-marketplace-availability)
- [Detection Logic](#detection-logic)
  - [Connector Discovery](#connector-discovery)
  - [Collection Method Detection](#collection-method-detection)
  - [Ingestion API Detection](#ingestion-api-detection)
  - [Custom Log V1 (CLv1) Detection](#custom-log-v1-clv1-detection)
  - [Filter Fields Detection](#filter-fields-detection)
  - [Connector Association Algorithm](#connector-association-algorithm)
  - [Parser Resolution](#parser-resolution)
  - [Table Detection Methods](#table-detection-methods)
  - [Context-Aware Table Detection](#context-aware-table-detection)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

The Solution Connector Tables Analyzer is a comprehensive tool that scans the Azure-Sentinel repository to extract, analyze, and document the relationships between Microsoft Sentinel solutions, data connectors, Log Analytics tables, content items, and parsers.

### Key Capabilities

**Data Connector Analysis**
- Extract table references from connector JSON files (queries, sample queries, data types)
- Detect collection methods (AMA, MMA, Azure Diagnostics, CCF, CCF Push, CCF Legacy, Azure Functions, REST API, Native)
- Extract filter fields (DeviceVendor, EventID, Facility, etc.) to identify data sources
- Resolve parser function references to actual underlying tables
- Check Azure Marketplace availability for each solution

**Content Item Analysis**
- Analyze analytics rules, hunting queries, playbooks, workbooks, watchlists, and summary rules
- Extract table references and filter fields from KQL queries
- Classify content by source: Solution, Standalone (community), or GitHub Only (legacy)
- Associate standalone content with matching connectors based on tables and filters

**Parser Analysis**
- Collect parsers from solution directories and legacy `/Parsers/*` directories
- Analyze ASIM parsers with full schema metadata
- Associate parsers with connectors based on shared tables and filter fields
- Support for union parsers and sub-parser resolution

**Solution Metadata**
- Flatten solution metadata from SolutionMetadata.json files
- Include ALL solutions, even those without data connectors
- Track solution support tiers, authors, and categories

### Output

The script generates 11 CSV files providing different views of the data:
- **Entity files**: `connectors.csv`, `solutions.csv`, `tables.csv`, `parsers.csv`, `asim_parsers.csv`
- **Mapping files**: `content_items.csv`, `content_tables_mapping.csv`, `solution_dependencies.csv`, `table_schemas.csv`, `solutions_connectors_tables_mapping_simplified.csv`
- **Reports**: `solutions_connectors_tables_issues_and_exceptions_report.csv`
- **Backward compatibility**: `solutions_connectors_tables_mapping.csv`

### Scope

This analysis covers connectors managed through Solutions in the Azure-Sentinel GitHub repository. For solutions where connectors are defined only as ARM resources in `Package/mainTemplate.json` (not as standalone JSON files in the `Data Connectors` folder), the analyzer uses a mainTemplate fallback mechanism to discover them. Connectors that have no discoverable definition files at all (such as SAP, which uses a Docker agent architecture) can be added via the [synthetic connector override system](#synthetic-connector-overrides).

## Prerequisites

### 1. Clone the Azure-Sentinel Repository

This script analyzes the Solutions directory from the [Azure-Sentinel GitHub repository](https://github.com/Azure/Azure-Sentinel). You must have the repository cloned locally:

```bash
# Clone the repository
git clone https://github.com/Azure/Azure-Sentinel.git

# Or if you already have it, update to latest
cd Azure-Sentinel
git pull origin master
```

The script expects to find the `Solutions/` directory containing Microsoft Sentinel solution definitions.

### 2. Python Environment

- Python 3.7 or higher
- No external dependencies required (optional: json5 for enhanced JSON parsing)

### 3. Table Reference Data (Recommended)

For enriched table metadata (categories, descriptions, transformation support), first run `collect_table_info.py` to generate `tables_reference.csv`:

```bash
python collect_table_info.py
```

The mapping script automatically loads `tables_reference.csv` if present and uses it to:
- Populate table metadata (category, description, resource_types)
- Determine collection method based on table properties (e.g., "Azure Resources" category → Azure Diagnostics)
- Include transformation support and ingestion API compatibility information

See [collect_table_info.md](collect_table_info.md) for details.

### 4. Optional Dependencies

```bash
pip install json5  # For improved JSON parsing with comments and trailing commas
```

## Running the Script

From the `Tools/Solutions Analyzer` directory:
```bash
python map_solutions_connectors_tables.py
```

Or from anywhere in the repository:
```bash
python "Tools/Solutions Analyzer/map_solutions_connectors_tables.py" --solutions-dir Solutions
```

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--solutions-dir` | `../../Solutions` | Path to the Solutions directory |
| `--output` | `solutions_connectors_tables_mapping.csv` | Path for the main output CSV file |
| `--report` | `solutions_connectors_tables_issues_and_exceptions_report.csv` | Path for the issues report CSV file |
| `--connectors-csv` | `connectors.csv` | Path for the connectors output CSV file (with collection method) |
| `--solutions-csv` | `solutions.csv` | Path for the solutions output CSV file |
| `--tables-csv` | `tables.csv` | Path for the tables output CSV file (with metadata) |
| `--content-items-csv` | `content_items.csv` | Path for the content items output CSV file |
| `--content-tables-mapping-csv` | `content_tables_mapping.csv` | Path for the content-to-tables mapping CSV file |
| `--asim-parsers-csv` | `asim_parsers.csv` | Path for the ASIM parsers CSV file |
| `--parsers-csv` | `parsers.csv` | Path for the non-ASIM parsers CSV file |
| `--solution-dependencies-csv` | `solution_dependencies.csv` | Path for the solution dependencies CSV file |
| `--table-schemas-csv` | `table_schemas.csv` | Path for the table schemas CSV file extracted from DCR definitions |
| `--la-table-schemas-csv` | `la_table_schemas.csv` | Path to la_table_schemas.csv containing column schemas from Azure Monitor documentation (generated by `collect_table_info.py`) |
| `--custom-tables-dir` | `.script/tests/KqlvalidationsTests/CustomTables` | Path to CustomTables directory for KQL validation table schemas (only tables not already covered by DCR or docs are included) |
| `--tables-reference-csv` | `tables_reference.csv` | Path to tables_reference.csv for table metadata |
| `--mapping-csv` | `solutions_connectors_tables_mapping_simplified.csv` | Path for the simplified mapping CSV file |
| `--overrides-csv` | `solution_analyzer_overrides.csv` | Path to overrides CSV file for field value overrides |
| `--show-detection-methods` | `False` | Include table_detection_methods column showing how each table was detected |
| `--skip-marketplace` | `False` | Skip Azure Marketplace availability checking |
| `--refresh-marketplace` | `False` | Force refresh of marketplace cache (ignore cached results) |
| `--force-refresh` | `""` | Force re-analysis of specified types, ignoring cached results. Comma-separated list of: `asim`, `parsers`, `solutions`, `standalone`, `marketplace`, `tables`. Use `all` to refresh everything, or `all-offline` to refresh all except network-dependent types. |

### Example Usage

```bash
# Run with default settings
python map_solutions_connectors_tables.py

# Show detection methods in output
python map_solutions_connectors_tables.py --show-detection-methods

# Custom output location
python map_solutions_connectors_tables.py --output custom_output.csv --report custom_report.csv

# Run with custom overrides file
python map_solutions_connectors_tables.py --overrides-csv my_overrides.csv

# Force refresh ASIM and parser analysis
python map_solutions_connectors_tables.py --force-refresh=asim,parsers

# Force refresh table metadata from Microsoft docs
python map_solutions_connectors_tables.py --force-refresh=tables
```

## Override System

The script supports an override system that allows you to modify field values in the output based on pattern matching. This is useful for:
- Setting `collection_method` to AMA for specific tables (e.g., Syslog, CommonSecurityLog)
- Assigning categories to tables based on naming patterns (e.g., all AWS* tables → AWS category)
- Correcting or supplementing data that cannot be automatically detected

The default override file (`solution_analyzer_overrides.csv`) is also used by `collect_table_info.py` and `generate_connector_docs.py` for consistent categorization across all outputs.

### Override File Format

The override file is a CSV with the following columns:

| Column | Description |
|--------|-------------|
| `Entity` | Entity type to match: `table`, `connector`, `solution`, or `synthetic_connector` (case insensitive). See [Synthetic Connector Overrides](#synthetic-connector-overrides) for the special `synthetic_connector` entity type. |
| `Pattern` | Regex pattern to match against the entity's key field (table_name, connector_id, or solution_name) |
| `Field` | The field name to override |
| `Value` | The new value to set |

**Pattern Matching Rules:**
- Patterns are treated as full-match regex (automatically wrapped with `^` and `$`)
- Pattern matching is case insensitive
- Use `.*` for wildcards (e.g., `.*AWS.*` matches any table containing "AWS")
- Field names must exactly match existing columns in the output

### Example Override File

```csv
Entity,Pattern,Field,Value
Table,Syslog,collection_method,AMA
Table,CommonSecurityLog,collection_method,AMA
Table,SecurityEvent,collection_method,AMA
Table,Event,collection_method,AMA
Table,WindowsFirewall,collection_method,AMA
Table,.*AWS.*,category,AWS
Table,.*GCP.*,category,GCP
Table,.*Crowdstrike.*,category,Crowdstrike
Table,.*CRWD.*,category,Crowdstrike
```

This example:
- Sets `collection_method` to "AMA" for common Windows/Syslog tables
- Sets `category` to "AWS" for all tables with "AWS" in their name
- Sets `category` to "GCP" for all tables with "GCP" in their name
- Sets `category` to "Crowdstrike" for tables matching Crowdstrike patterns

### Default Override File

If no `--overrides-csv` argument is provided, the script looks for `solution_analyzer_overrides.csv` in the Tools/Solutions Analyzer directory.

### Synthetic Connector Overrides

In addition to field overrides, the override file supports defining **synthetic connectors** — connectors that have no discoverable definition files in the repository. This is used for connectors that use non-standard architectures (e.g., SAP uses a Docker agent rather than JSON definition files).

#### Format

Synthetic connectors use `Entity = synthetic_connector` and are defined as multiple rows sharing the same `Pattern` (solution folder name) and grouped by `Field = connector_id`:

| Column | Usage for Synthetic Connectors |
|--------|-------------------------------|
| `Entity` | Must be `synthetic_connector` |
| `Pattern` | Solution folder name (e.g., `SAP`) |
| `Field` | One of: `connector_id` (required, starts a new connector group), `title`, `publisher`, `description`, `tables`, `instruction_steps`, `permissions` |
| `Value` | Field value. For `tables`, use semicolon-separated table names (e.g., `Table1_CL;Table2_CL`) |

#### Required Fields

- `connector_id` — unique identifier for the connector (also starts a new connector group)
- `title` — display title
- `publisher` — publisher name

#### Optional Fields

- `description` — connector description text
- `tables` — semicolon-separated list of table names
- `instruction_steps` — JSON-encoded setup instructions
- `permissions` — JSON-encoded permission requirements

#### Example

```csv
Entity,Pattern,Field,Value
synthetic_connector,SAP,connector_id,MicrosoftSentinelSAP,"SAP connector uses Docker agent architecture..."
synthetic_connector,SAP,title,Microsoft Sentinel for SAP,
synthetic_connector,SAP,publisher,Microsoft,
synthetic_connector,SAP,description,"The Microsoft Sentinel solution for SAP allows you to monitor SAP systems...",
synthetic_connector,SAP,tables,ABAPAuditLog_CL;ABAPChangeDocsLog_CL,
```

Synthetic connectors:
- Are only injected if no connector with the same ID was already discovered for the solution
- Appear in output with `connector_files` set to `synthetic_connector_override` and detection method `synthetic_connector_override`
- Trigger a `missing_solution_metadata` issue if the solution lacks a SolutionMetadata.json file

## Output Files

### 1. connectors.csv (Connector Details with Collection Method)

Contains one row per unique connector with all connector-specific fields and collection method analysis.

| Column | Description | Data Source |
|--------|-------------|-------------|
| `connector_id` | Unique connector identifier | Connector JSON `id` field, or generated from title |
| `connector_publisher` | Connector publisher name | Connector JSON `publisher` field |
| `connector_title` | Connector display title | Connector JSON `title` field |
| `connector_description` | Connector description | Connector JSON `descriptionMarkdown` field |
| `connector_instruction_steps` | Setup and configuration instructions (JSON) | Connector JSON `instructionSteps` field |
| `connector_permissions` | Required permissions (JSON) | Connector JSON `permissions` field |
| `connector_id_generated` | `true` if connector ID was auto-generated from title | Computed: `true` when `id` contains `[variables(...)]` |
| `connector_files` | Semicolon-separated list of GitHub URLs to connector definition files | File system scan of Data Connectors folders |
| `connector_readme_file` | Path to connector README file (if exists) | File system scan for `.md` files |
| `collection_method` | Data collection method (see [Collection Method Detection](#collection-method-detection)) | [Multi-pattern analysis](#collection-method-detection) of connector content |
| `collection_method_reason` | Explanation of how collection method was determined | Computed: explains which patterns matched |
| `event_vendor` | Semicolon-separated list of vendor values extracted from queries | [KQL query analysis](#filter-fields-detection) |
| `event_product` | Semicolon-separated list of product values extracted from queries | [KQL query analysis](#filter-fields-detection) |
| `event_vendor_product_by_table` | JSON mapping of tables to vendor/product pairs | [KQL query analysis](#filter-fields-detection) with table context |
| `filter_fields` | Filter fields extracted from queries (see [Filter Fields Detection](#filter-fields-detection)) | [KQL query analysis](#filter-fields-detection) with operator extraction |
| `not_in_solution_json` | `true` if connector was found by file scanning but not listed in the Solution JSON | Comparison: file scan vs Solution JSON content lists |
| `solution_name` | Name of the parent solution | Parent solution folder name |
| `is_deprecated` | `true` if connector title contains "[DEPRECATED]"/"[Deprecated]", connector JSON has `availability.status` of 0, or parent solution is deprecated | Pattern match on connector title + connector JSON `availability.status` field + solution-level deprecation inheritance |
| `deprecation_date` | Date string extracted from connector description (e.g., "Aug 31, 2024") when deprecated; empty if not found | Regex extraction from `descriptionMarkdown` near deprecation keywords; overridable |
| `is_published` | `true` if parent solution is published on Azure Marketplace | Azure Marketplace API query |
| `ccf_config_file` | GitHub URL to the CCF configuration file (for CCF and CCF Push connectors) | File system scan for polling/poller config files |
| `ccf_capabilities` | Semicolon-separated CCF capabilities (auth type, paging, POST, etc.) | Parsed from CCF config JSON |
| `ingestion_api` | Which ingestion API the connector uses: "Log Ingestion API", "HTTP Data Collector API", "Undetermined", or empty | Multi-rule detection: CCF method, Python code scanning, JSON pattern matching, column suffix heuristic |
| `ingestion_api_reason` | Human-readable explanation of how the ingestion API was determined | Auto-generated by detection logic |
| `is_clv1` | `true` if any of the connector's tables use the Custom Log V1 schema format | CLv1 detection (column suffixes or _CL table from AMA/HTTP Data Collector connector) |

### 2. solutions.csv (Solution Details)

Contains one row per solution with all solution-specific metadata. Metadata is sourced from both `SolutionMetadata.json` and `Data/Solution_*.json` files.

| Column | Description | Data Source |
|--------|-------------|-------------|
| `solution_name` | Official solution name from Solution JSON (or folder name if not available) | Solution JSON `Name` field, fallback to folder name |
| `solution_folder` | Solution folder name (matches directory name in Solutions/) | File system: Solutions/ directory listing |
| `solution_github_url` | Full GitHub URL to the solution's folder | Computed from solution_folder |
| `solution_publisher_id` | Publisher ID from SolutionMetadata.json | SolutionMetadata.json `publisherId` |
| `solution_offer_id` | Offer ID from SolutionMetadata.json | SolutionMetadata.json `offerId` |
| `solution_first_publish_date` | First publication date | SolutionMetadata.json `firstPublishDate` |
| `solution_last_publish_date` | Last update date | SolutionMetadata.json `lastPublishDate` |
| `solution_version` | Solution version from Solution JSON or SolutionMetadata.json | Solution JSON `Version` or SolutionMetadata.json `version` |
| `solution_support_name` | Support provider name | SolutionMetadata.json `support.name` |
| `solution_support_tier` | Support tier (Microsoft, Partner, Community) | SolutionMetadata.json `support.tier` |
| `solution_support_link` | Support link URL | SolutionMetadata.json `support.link` |
| `solution_author_name` | Author name from Solution JSON (e.g., "Microsoft") | Solution JSON `Author` field |
| `solution_categories` | Comma-separated list of solution categories (e.g., "Security - Others, domains") | SolutionMetadata.json `categories` |
| `solution_readme_file` | Path to solution README file (if exists) | File system scan for README.md |
| `solution_logo_url` | URL to solution logo image extracted from HTML img tag in Solution JSON Logo field | Solution JSON `Logo` field (HTML img src extraction) |
| `solution_description` | Full solution description with HTML/markdown formatting from Solution JSON | Solution JSON `Description` field |
| `solution_dependencies` | Semicolon-separated list of dependent solution IDs from `dependentDomainSolutionIds` | Solution JSON `dependentDomainSolutionIds` |
| `has_connectors` | `true` if solution has data connectors, `false` otherwise | Computed: checks for Data Connectors folder |
| `is_deprecated` | `true` if solution description contains deprecation language (e.g., "this integration is considered deprecated") | Regex match on Solution JSON `Description` field; overridable |
| `deprecation_date` | Date string extracted from solution description when deprecated; empty if not found | Regex extraction from `Description` near deprecation keywords; overridable |
| `is_published` | `true` if solution is published on Azure Marketplace | Azure Marketplace API query |
| `marketplace_url` | URL to the solution's Azure Marketplace listing | Azure Marketplace API response |
| `mp_is_published` | `true`/`false` — whether solution is published on Azure Marketplace | Azure Marketplace API |
| `mp_url` | Direct URL to the Azure Marketplace listing | Computed from publisher/offer IDs |
| `mp_display_name` | Solution display name on Azure Marketplace | API `displayName` field |
| `mp_summary` | Short summary text from the marketplace listing | API `summary` field |
| `mp_long_summary` | Extended summary text from the marketplace listing | API `longSummary` field |
| `mp_publisher_display_name` | Publisher display name on the marketplace | API `publisherDisplayName` field |
| `mp_is_preview` | `true`/`false` — whether the listing is in preview | API `isPreview` field |
| `mp_is_stop_sell` | `true`/`false` — whether the listing is stop-sell (delisted) | API `isStopSell` field |
| `mp_creation_date` | Marketplace listing creation date (YYYY-MM-DD) | API `creationDate` field |
| `mp_last_modified_date` | Marketplace listing last modification date (YYYY-MM-DD) | API `bigCatLastModifiedDate` field |
| `mp_categories` | Semicolon-separated marketplace category IDs | API `categoryIds` array |
| `mp_keywords` | Semicolon-separated marketplace keywords | API `keywords` array |
| `mp_popularity` | Popularity score (0–1 range, higher = more popular) | API `enrichedData.popularity.azurePortalApps` |
| `mp_rating_average` | Average user rating (0–5 scale) | API `enrichedData.rating.all.averageRating` |
| `mp_rating_count` | Total number of user ratings | API `enrichedData.rating.all.totalRatings` |
| `mp_is_free` | `true`/`false` — whether the first plan is free | API `plans[0].isFree` |
| `mp_is_byol` | `true`/`false` — whether the listing is bring-your-own-license | API `isByol` field |
| `mp_is_microsoft_product` | `true`/`false` — whether the listing is a Microsoft product | API `isMicrosoftProduct` field |
| `mp_last_checked` | Date when marketplace data was last fetched (YYYY-MM-DD) | Computed at query time |

**Solution JSON File Selection:**

The script locates Solution JSON files using this algorithm:
1. Look for `Data/` or `data/` folder within the solution directory
2. Find files matching the pattern `Solution_*.json` (e.g., `Solution_1Password.json`)
3. Parse the first matching JSON file to extract Name, Logo, Author, Version, and Description
4. Logo URL is extracted from HTML img tags like `<img src="https://..." width="75px" height="75px">`

### 3. tables.csv (Table Metadata)

Contains one row per unique table referenced by connectors, with metadata from Azure Monitor documentation and Sentinel reference.

| Column | Description | Data Source |
|--------|-------------|-------------|
| `table_name` | Table name | All sources |
| `description` | Table description from Azure Monitor documentation | `tables_reference.csv` (Azure Monitor pages) |
| `category` | Table category (e.g., Security, Audit, Azure Resources) | `tables_reference.csv` (Azure Monitor tables-category) |
| `support_tier` | Support tier derived from associated solutions. Shows "Various" if table is used by solutions with different tiers. | Derived from `solution_support_tier` of all solutions using this table |
| `collection_method` | Data collection method (from tables_reference.csv or overrides) | `tables_reference.csv`, Override system |
| `resource_types` | Azure resource types that emit to this table | `tables_reference.csv` (Azure Monitor pages) |
| `source_azure_monitor` | Whether table is in Azure Monitor reference | `tables_reference.csv` |
| `source_defender_xdr` | Whether table is in Defender XDR schema | `tables_reference.csv` |
| `azure_monitor_doc_link` | Link to Azure Monitor documentation | `tables_reference.csv` |
| `defender_xdr_doc_link` | Link to Defender XDR documentation | `tables_reference.csv` |
| `basic_logs_eligible` | Whether table supports Basic Logs plan | `tables_reference.csv` (Azure Monitor pages) |
| `supports_transformations` | Whether ingestion-time transformations are supported | `tables_reference.csv` (Tables feature support page, enriched with Sentinel tables/connectors) |
| `ingestion_api_supported` | Whether Data Collector API ingestion is supported | `tables_reference.csv` (Logs Ingestion API page) |
| `lake_only_supported` | Whether lake-only ingestion is supported | `tables_reference.csv` (Sentinel tables/connectors) |
| `is_clv1` | `true` if table uses the Custom Log V1 schema format (type-suffixed columns or _CL table from AMA/HTTP Data Collector connector) | CLv1 detection logic |

> **Note:** Metadata is sourced from `tables_reference.csv`. Tables not found in the reference file will have empty metadata fields. Run `collect_table_info.py` first to populate this data.

### 4. solutions_connectors_tables_mapping_simplified.csv (Simplified Mapping)

A simplified mapping file containing only key fields for linking connectors, tables, and solutions.

| Column | Description | Data Source |
|--------|-------------|-------------|
| `solution_name` | Solution folder name | Parent solution folder |
| `connector_id` | Connector identifier | Connector JSON `id` field |
| `table_name` | Table name | Connector table detection |

### 5. content_items.csv (Content Item Details)

Contains one row per content item (analytics rule, hunting query, playbook, workbook, parser, watchlist, or summary rule) found in solutions or top-level directories.

| Column | Description | Data Source |
|--------|-------------|-------------|
| `content_id` | Unique identifier for the content item (GUID from YAML/JSON) | Content file `id` field |
| `content_name` | Display name of the content item | Content file `name` field |
| `content_type` | Type: `analytic_rule`, `hunting_query`, `playbook`, `workbook`, `parser`, `watchlist`, `summary_rule` | Inferred from file location/structure |
| `content_description` | Description of the content item | Content file `description` field |
| `content_file` | Filename of the source file | File system scan (for both solution and standalone content) |
| `content_readme_file` | Path to associated README file (if exists) | File system scan |
| `content_severity` | Severity level (for analytics rules): `High`, `Medium`, `Low`, `Informational` | Content file `severity` field |
| `content_status` | Status field from content item | Content file `status` field |
| `content_kind` | Kind/type from content item | Content file `kind` field |
| `content_tactics` | MITRE ATT&CK tactics (comma-separated) | Content file `tactics` field |
| `content_techniques` | MITRE ATT&CK techniques (comma-separated) | Content file `techniques` field |
| `content_required_connectors` | Required data connectors (from requiredDataConnectors field) | Content file `requiredDataConnectors` field |
| `content_query_status` | Query status: `has_query`, `no_query`, `query_error` | Computed: query extraction result |
| `content_event_vendor` | Event vendor extracted from query filter fields | [KQL query analysis](#filter-fields-detection) |
| `content_event_product` | Event product extracted from query filter fields | [KQL query analysis](#filter-fields-detection) |
| `content_filter_fields` | Filter fields extracted from content query (see [Filter Fields Detection](#filter-fields-detection)) | [KQL query analysis](#filter-fields-detection) |
| `associated_connectors` | Comma-separated list of connector IDs that provide data matching this content's tables and filter fields (for Standalone/GitHub Only items only) | [Connector Association Algorithm](#connector-association-algorithm) |
| `associated_solutions` | Comma-separated list of solution names associated with the matching connectors (for Standalone/GitHub Only items only) | Derived from associated_connectors |
| `content_github_url` | Direct GitHub URL to the content file (for standalone items only) | Computed from file path |
| `content_source` | Source location: `Solution` (from Solutions/), `Standalone` (top-level with metadata), `GitHub Only` (top-level without metadata) | File location + metadata presence check |
| `metadata_source_kind` | Source kind from YAML metadata section: `Community`, `Solution`, `Standalone` | YAML `metadata.source.kind` field |
| `metadata_author` | Author name from YAML metadata section | YAML `metadata.author` field |
| `metadata_support_tier` | Support tier from YAML metadata section: `Microsoft`, `Partner`, `Community` | YAML `metadata.support.tier` field |
| `metadata_categories` | Categories/domains from YAML metadata section (comma-separated) | YAML `metadata.categories` field |
| `not_in_solution_json` | `true` if item was found by file scanning but not listed in Solution JSON (marked with ⚠️ in docs) | Comparison: file scan vs Solution JSON |
| `solution_name` | Solution name (empty for standalone content) | Parent solution folder |
| `solution_folder` | Solution folder name (empty for standalone content) | Parent solution folder |
| `solution_github_url` | Full GitHub URL to the solution's folder (empty for standalone content) | Computed from solution_folder |
| `is_published` | `true` if parent solution is published on Azure Marketplace (empty for standalone content) | Azure Marketplace API query |

#### Content Source Classification

The `content_source` column classifies content items based on their origin:

| Value | Description | Example |
|-------|-------------|---------|
| **Solution** | Content included in a Solution package in `Solutions/` | Microsoft Sentinel solutions published to Marketplace |
| **Standalone** | Top-level content with YAML `metadata` section | Community contributions with proper metadata |
| **GitHub Only** | Top-level content without `metadata` section | Legacy content not yet classified, stub files |

Standalone items are collected from these top-level directories:
- `Detections/` - Analytic rules (YAML)
- `Hunting Queries/` - Hunting queries (YAML)
- `Workbooks/` - Workbooks (JSON)
- `Playbooks/` - Playbooks (folders with azuredeploy.json)
- `Summary rules/` - Summary rules (YAML)
- `Watchlists/` - Watchlists (folders with watchlist.json)

### 6. content_tables_mapping.csv (Content Item to Table Mapping)

Contains one row per unique combination of solution, content item, and table. This maps tables found in KQL queries within analytics rules, hunting queries, playbooks, workbooks, watchlists, and summary rules.

| Column | Description | Data Source |
|--------|-------------|-------------|
| `solution_name` | Solution name (empty for standalone content) | Parent solution folder |
| `solution_folder` | Solution folder name (empty for standalone content) | Parent solution folder |
| `solution_github_url` | Full GitHub URL to the solution's folder (empty for standalone content) | Computed from solution_folder |
| `content_type` | Type of content item: `analytic_rule`, `hunting_query`, `playbook`, `workbook`, `watchlist`, `summary_rule` | Inferred from file location/structure |
| `content_id` | Content item identifier | Content file `id` field |
| `content_name` | Name or filename of the content item | Content file `name` field or filename |
| `content_file` | Source filename | File system |
| `table_name` | Table name extracted from the KQL query | KQL query parsing with parser resolution |
| `table_usage` | Usage indicator for playbooks: `read`, `write`, or `read/write`. Empty for other content types (assumed read). | Playbook action type analysis |
| `is_published` | `true` if parent solution is published on Azure Marketplace | Azure Marketplace API query |

> **Note:** For playbooks, `table_usage` tracks whether the playbook reads from a table (Azure Monitor query), writes to it (Send Data action), or both. Other content types are assumed to only read from tables.

### 7. parsers.csv (Parser Details)

Contains one row per parser (both ASIM and non-ASIM) from solution directories and the legacy `/Parsers/*` directories.

| Column | Description | Data Source |
|--------|-------------|-------------|
| `parser_name` | Parser function name | YAML `FunctionName` or filename |
| `parser_title` | Display title of the parser | YAML `displayName` or `Title` |
| `parser_version` | Parser version number | YAML `version` or `Version` |
| `parser_last_updated` | Last update date | YAML `lastUpdated` or `Last Updated` |
| `parser_category` | Parser category/type | YAML `category` or `Category` |
| `description` | Parser description | YAML `description` or `Description` |
| `tables` | Semicolon-separated list of source tables used by the parser | [KQL query parsing](#table-detection-methods) of `FunctionQuery` field |
| `source_file` | Relative path to the source file | File system |
| `github_url` | Full GitHub URL to the parser definition | Computed from source_file |
| `solution_name` | Solution name (empty for legacy parsers) | Parent solution folder |
| `solution_folder` | Solution folder name (empty for legacy parsers) | Parent solution folder |
| `solution_github_url` | Full GitHub URL to the solution's folder (empty for legacy parsers) | Computed from solution_folder |
| `location` | Location: `solution` (in Solutions directory) or `legacy` (in top-level /Parsers directory) | File path analysis |
| `file_type` | File type: `yaml`, `kql`, or `txt` | File extension |
| `discovered` | `true` if parser was found by file scanning but not listed in Solution JSON (marked with ⚠️ in docs) | Comparison: file scan vs Solution JSON |

> **Note:** Parsers are collected from both solution `Parsers/` directories and the legacy top-level `/Parsers/*` directories. Legacy parsers are pre-Solutions parsers stored as .txt, .kql, or .yaml files.

### 8. asim_parsers.csv (ASIM Parser Details)

Contains one row per ASIM parser from the `/Parsers/ASim*/Parsers` directories. This includes all ASIM (Advanced Security Information Model) parsers with full metadata.

| Column | Description | Data Source |
|--------|-------------|-------------|
| `parser_name` | Parser function name (e.g., `ASimDnsAzureFirewall`) | YAML `ParserName` field |
| `equivalent_builtin` | Built-in parser alias (e.g., `_ASim_Dns_AzureFirewall`) | YAML `EquivalentBuiltInParser` field |
| `schema` | ASIM schema name (e.g., `Dns`, `NetworkSession`, `Authentication`) | Inferred from folder name (ASim{Schema}) |
| `schema_version` | Schema version number | YAML `Normalization.Version` field |
| `parser_type` | Parser type: `union` (schema-level aggregator), `source` (product-specific), or `empty` (placeholder) | Computed: sub_parsers presence check |
| `parser_title` | Display title of the parser | YAML `Parser.Title` field |
| `parser_version` | Parser version number | YAML `Parser.Version` field |
| `parser_last_updated` | Last update date | YAML `Parser.LastUpdated` field |
| `product_name` | Product/source name (e.g., `Azure Firewall`, `Palo Alto`) | YAML `Normalization.Product` field |
| `description` | Parser description | YAML `Description` field |
| `tables` | Semicolon-separated list of source tables used by the parser | [KQL query parsing](#table-detection-methods) of `ParserQuery` field |
| `sub_parsers` | Semicolon-separated list of sub-parser references (for union parsers) | YAML `Parsers` array field |
| `parser_params` | Parser parameters in format `name:type=default` | YAML `ParserParams` array field |
| `filter_fields` | Filter fields extracted from parser query (see [Filter Fields Detection](#filter-fields-detection)) | [KQL query analysis](#filter-fields-detection) |
| `associated_connectors` | Comma-separated list of connector IDs that provide data matching this parser's tables and filter fields | [Connector Association Algorithm](#connector-association-algorithm) |
| `associated_solutions` | Comma-separated list of solution names associated with the matching connectors | Derived from associated_connectors |
| `references` | Semicolon-separated list of reference links | YAML `References` array field |
| `source_file` | Relative path to the source YAML file | File system |
| `github_url` | Full GitHub URL to the parser definition | Computed from source_file |

> **Note:** ASIM parsers are loaded from YAML files in the `/Parsers/ASim*/Parsers` directories. Union parsers aggregate multiple source parsers and typically have empty `tables` but populated `sub_parsers`. Source parsers reference actual Log Analytics tables. The `vim*` (vendor-independent model) parsers are skipped as they are wrappers around the corresponding `ASim*` parsers with identical filters.

### 9. solution_dependencies.csv (Solution Dependency Mapping)

Contains one row per dependency relationship between solutions. A solution can appear multiple times if it has multiple dependencies. Dependencies are identified from two sources:

1. **Explicit dependencies**: From the `dependentDomainSolutionIds` array in the solution's `SolutionMetadata.json`, which lists `publisherId.offerId` identifiers
2. **ASIM-based dependencies** (optional): When a solution's content items reference ASIM parsers, all solutions whose connectors provide data to those parsers are identified as potential dependencies. These are optional — they represent solutions that *can* provide data through ASIM parsers, not solutions that *must* be installed

| Column | Description | Data Source |
|--------|-------------|-------------|
| `solution_name` | Solution that has the dependency | Parent solution folder |
| `dependency_solution_name` | Solution that is depended upon (resolved from ID for explicit deps) | Resolved from `publisherId.offerId` lookup or ASIM parser associations |
| `dependency_solution_id` | The `publisherId.offerId` identifier (explicit deps only) | `dependentDomainSolutionIds` array |
| `dependency_type` | Type of dependency: `explicit` (required) or `ASIM` (optional — indicates a solution that can provide data through ASIM parsers) | Computed |
| `asim_schema` | ASIM schema name (ASIM deps only, e.g., `NetworkSession`, `Dns`) | Derived from content item table references → ASIM parser schema |

> **Note:** ASIM dependencies are optional — they indicate which solutions *can* provide data, not which *must* be installed. They can generate many rows since a solution using a single ASIM parser (e.g., `_Im_NetworkSession`) will list every solution that provides a connector mapped to that ASIM schema as a potential dependency. Self-dependencies (where a solution depends on itself) are excluded.

### 10. table_schemas.csv (Table Column Schemas)

Contains one row per column per table, combining three data sources:

1. **DCR definitions** — Extracted from `*_DCR.json` (Data Collection Rule) companion files found alongside connector definitions. Provides the ingestion-time stream schema for CCP/CCF connectors.
2. **Azure Monitor documentation** — Extracted from rendered table reference pages on learn.microsoft.com. Provides the documented column schema for native Azure Monitor and Defender XDR tables. This data comes from `la_table_schemas.csv` generated by `collect_table_info.py`.
3. **KQL validation tables** — Extracted from `.script/tests/KqlvalidationsTests/CustomTables/*.json` files. These are table schema definitions used for KQL query validation in the repository's CI pipeline. Only tables not already covered by sources 1 and 2 are included.

| Column | Description | Data Source |
|--------|-------------|-------------|
| `table_name` | Table name | DCR `dataFlows[].outputStream` (prefix stripped) / Documentation / CustomTables JSON |
| `column_name` | Column name | DCR `streamDeclarations[].columns[].name` / Documentation / CustomTables JSON |
| `column_type` | Column data type (e.g., `string`, `datetime`, `dynamic`, `real`, `boolean`, `int`) | DCR `streamDeclarations[].columns[].type` / Documentation / CustomTables JSON |
| `description` | Column description from documentation | Azure Monitor / Defender XDR docs (empty for DCR and KQL validation rows) |
| `source` | Data source: `DCR`, `Azure Monitor docs`, or `KQL validation` | Computed |
| `source_url` | URL to the source file/page (GitHub link for DCR/KQL validation, learn.microsoft.com link for docs) | Computed |
| `stream_name` | Input stream name (e.g., `Custom-MyTable_CL`) | DCR only |
| `connector_id` | Connector ID associated with this DCR file | DCR only |
| `solution_name` | Solution containing the connector | DCR only |
| `dcr_file` | Repository-relative path to the DCR JSON file | DCR only |
| `transform_kql` | KQL transformation applied during ingestion | DCR only |

> **Note:** For DCR-sourced rows, the schema columns represent the *input stream* declaration, not necessarily the final table schema. When a `transform_kql` is present, it may add, remove, rename, or transform columns between the declared stream schema and the output table. The stream name may also differ from the output table name (e.g., `Custom-SlackAudit_CL` → `SlackAuditV2_CL`).

### 11. solutions_connectors_tables_issues_and_exceptions_report.csv (Issues Report)

Contains exceptions and issues encountered during analysis.

#### Column Descriptions

| Column | Description | Data Source |
|--------|-------------|-------------|
| `solution_name` | Solution name | Parent solution folder |
| `solution_folder` | Solution folder name | Parent solution folder |
| `solution_github_url` | Full GitHub URL to the solution's folder | Computed from solution_folder |
| `connector_id` | Connector ID (if applicable) | Connector JSON `id` field |
| `connector_title` | Connector title (if applicable) | Connector JSON `title` field |
| `connector_publisher` | Connector publisher (if applicable) | Connector JSON `publisher` field |
| `relevant_file` | GitHub URL to the relevant file (connector or content file depending on issue type) | Computed from file path |
| `issue_type` | Issue category (see Issue Types below) | Analysis error classification |
| `issue` | Detailed description of the issue | Analysis error details |

#### Issue Types and Handling

| Reason | Description | Primary CSV Impact |
|--------|-------------|-------------------|
| `json_parse_error` | JSON file could not be parsed | Connector excluded entirely |
| `no_table_definitions` | No table tokens detected in connector | Connector excluded from output |
| `parser_tables_only` | All detected tables are parser functions only | Connector excluded (no actual tables found) |
| `partial_parser_tables` | Some tables filtered because they're parser functions | Filtered tables excluded, remaining tables included |
| `table_detection_failed` | Tables detected but validation failed | Connector excluded |
| `missing_connector_json` | Data Connectors folder exists but contains no valid JSON | Solution has no connector entries |
| `missing_solution_metadata` | Solution has connectors but no SolutionMetadata.json | Solution appears with empty metadata fields |

### 12. solutions_connectors_tables_mapping.csv (Backward Compatibility)

This CSV file is maintained for backward compatibility with older scripts and workflows. It contains one row per unique combination of solution, connector, and table, with all metadata denormalized into a single wide table.

> **Note:** For new integrations, prefer using the normalized CSV files (`connectors.csv`, `solutions.csv`, `tables.csv`) which provide cleaner data organization and smaller file sizes.

**Newline handling:** Newlines in the `connector_description` and `connector_permissions` fields are replaced with `<br>` tags to ensure proper rendering in GitHub's CSV viewer. The `connector_instruction_steps` field uses standard JSON encoding with `\n` for newlines.

#### Column Descriptions

| Column | Description | Data Source |
|--------|-------------|-------------|
| `Table` | The table name (e.g., Syslog, CommonSecurityLog, CustomLog_CL). Empty for solutions without data connectors. | Connector table detection |
| `solution_name` | Solution folder name | Parent solution folder |
| `solution_folder` | Solution folder name (matches directory name in Solutions/) | File system |
| `solution_github_url` | Full GitHub URL to the solution's folder | Computed from solution_folder |
| `solution_publisher_id` | Publisher ID from SolutionMetadata.json | SolutionMetadata.json |
| `solution_offer_id` | Offer ID from SolutionMetadata.json | SolutionMetadata.json |
| `solution_first_publish_date` | First publication date | SolutionMetadata.json |
| `solution_last_publish_date` | Last update date | SolutionMetadata.json |
| `solution_version` | Solution version number | Solution JSON or SolutionMetadata.json |
| `solution_support_name` | Support provider name (e.g., Microsoft, Community) | SolutionMetadata.json |
| `solution_support_tier` | Support tier (e.g., Microsoft, Partner, Community) | SolutionMetadata.json |
| `solution_support_link` | Support link URL | SolutionMetadata.json |
| `solution_author_name` | Author name from metadata | Solution JSON |
| `solution_categories` | Comma-separated list of solution categories | SolutionMetadata.json |
| `connector_id` | Unique connector identifier. Empty for solutions without data connectors. | Connector JSON |
| `connector_publisher` | Connector publisher name. Empty for solutions without data connectors. | Connector JSON |
| `connector_title` | Connector display title. Empty for solutions without data connectors. | Connector JSON |
| `connector_description` | Connector description (newlines replaced with `<br>` for GitHub CSV rendering). Empty for solutions without data connectors. | Connector JSON |
| `connector_instruction_steps` | Setup and configuration instructions from connector UI definitions (JSON-encoded). | Connector JSON |
| `connector_permissions` | Required permissions and prerequisites (JSON-encoded). | Connector JSON |
| `connector_files` | Semicolon-separated list of GitHub URLs to connector definition files. | File system scan |
| `is_unique` | `true` if table appears in only one connector file, `false` otherwise | Computed: cross-connector comparison |
| `table_detection_methods` | (Optional, with --show-detection-methods) Semicolon-separated list of methods used to detect this table | Analysis tracking |

## Azure Marketplace Availability

The script queries the Azure Marketplace Catalog API to collect comprehensive metadata for each solution, including availability status, display names, descriptions, popularity, ratings, categories, and publication dates.

### How It Works

1. For each solution, the script constructs a legacy product ID from the `publisher_id` and `offer_id` in `SolutionMetadata.json`
2. It queries the Azure Marketplace Catalog API at `https://catalogapi.azure.com/offers/{legacy_id}?api-version=2018-08-01-beta`
3. If the API returns a valid response, the full response is parsed into 19 `mp_*` fields and cached
4. If the API returns an error or no data, the solution is marked as unpublished with empty metadata fields

### Collected Fields

The following fields are extracted from the API response (all prefixed with `mp_`):

| Field | Description |
|-------|-------------|
| `mp_is_published` | `true`/`false` — whether the solution exists on Azure Marketplace |
| `mp_url` | Direct link to the marketplace listing |
| `mp_display_name` | Marketplace display name (often differs from solution folder name) |
| `mp_summary` | Short description from the listing |
| `mp_long_summary` | Extended description from the listing |
| `mp_publisher_display_name` | Publisher name as shown on marketplace |
| `mp_is_preview` | Whether the listing is in preview |
| `mp_is_stop_sell` | Whether the listing is delisted/stop-sell |
| `mp_creation_date` | Date the marketplace listing was created (YYYY-MM-DD) |
| `mp_last_modified_date` | Date the listing was last modified (YYYY-MM-DD) |
| `mp_categories` | Semicolon-separated marketplace category IDs |
| `mp_keywords` | Semicolon-separated keywords |
| `mp_popularity` | Popularity score (0–1; from `enrichedData.popularity.azurePortalApps`) |
| `mp_rating_average` | Average user rating (0–5; from `enrichedData.rating.all`) |
| `mp_rating_count` | Total number of user ratings |
| `mp_is_free` | Whether the first pricing plan is free |
| `mp_is_byol` | Whether the listing uses bring-your-own-license model |
| `mp_is_microsoft_product` | Whether the listing is flagged as a Microsoft product |
| `mp_last_checked` | Date when this data was last fetched from the API |

### Caching

To avoid excessive API calls on subsequent runs, marketplace data is cached locally:

- **Cache Location:** `.cache/marketplace_data.json`
- **Cache Format:** JSON dictionary keyed by `legacy_id`, each value containing all `mp_*` fields
- **Cache Behavior:** 
  - If a solution's legacy ID is found in the cache, the cached result is used (no API call)
  - New solutions not in the cache trigger API calls and are added to the cache
  - Use `--refresh-marketplace` or `--force-refresh marketplace` to force refresh all entries
- **Migration:** The script automatically migrates from the old CSV cache format (`marketplace_availability.csv`) to the new JSON format on first run

### Command Line Options

| Option | Description |
|--------|-------------|
| `--skip-marketplace` | Skip marketplace checking entirely (outputs will have empty marketplace fields) |
| `--refresh-marketplace` | Force refresh of marketplace cache, ignoring cached results and re-querying all solutions |
| `--force-refresh marketplace` | Same as `--refresh-marketplace` (via the unified `--force-refresh` mechanism) |

### Output Fields

Marketplace data adds the following fields:

| File | Fields | Description |
|------|--------|-------------|
| `solutions.csv` | `is_published`, `marketplace_url` | Legacy fields for backward compatibility |
| `solutions.csv` | All 19 `mp_*` fields | Full marketplace metadata (see table above) |
| `connectors.csv` | `is_published` | `true` if parent solution is published |
| Main mapping CSV | `is_published` | `true` if parent solution is published |

> **Note:** The `is_published` and `marketplace_url` columns are maintained alongside the new `mp_is_published` and `mp_url` fields for backward compatibility. Solutions without valid `publisher_id` and `offer_id` in `SolutionMetadata.json` cannot be checked and will have empty marketplace fields.

## Detection Logic

### Connector Discovery

The analyzer uses a multi-tier approach to discover connectors within each solution:

#### Primary: Data Connectors Folder Scan

The primary discovery method scans JSON files in the solution's `Data Connectors/` folder (or paths listed in the Solution JSON). Each JSON file is searched using a depth-first traversal (`find_connector_objects`) for dictionaries containing the required connector fields (`id`, `publisher`, `title`). When a connector's `id` field contains an ARM template variable reference (e.g., `[variables('_uiConfigId10')]`), the ID is generated from the title by removing spaces and hyphens (e.g., `Microsoft Power Automate` → `MicrosoftPowerAutomate`).

#### Fallback: mainTemplate.json

If the primary scan finds no connectors for a solution (or finds connectors with ARM variable IDs only), the analyzer falls back to scanning `Package/mainTemplate.json`. This handles solutions where connectors are defined only as ARM resources of type `Microsoft.SecurityInsights/dataConnectorDefinitions` rather than as standalone JSON files. The function:

1. Searches for ARM resources with type ending in `dataConnectorDefinitions`
2. Extracts the `connectorUiConfig` from the resource properties
3. Resolves ARM variable references in the `id` and `publisher` fields using title-based generation
4. Extracts tables from the `dataTypes` section (filtering out `{{...}}` template placeholders)
5. Deduplicates against connectors already found by the primary scan using both ID and title matching

This mechanism discovered the Microsoft Dataverse, Microsoft Power Automate, and Microsoft Power Platform Admin Activity connectors from the Microsoft Business Applications solution.

#### Override: Synthetic Connectors

Connectors that have no discoverable definition files at all can be injected via the [synthetic connector override system](#synthetic-connector-overrides). These are only added if no connector with the same ID was already discovered. See [Synthetic Connector Overrides](#synthetic-connector-overrides) for details.

#### Solution Membership

Both mainTemplate and synthetic connectors are classified as **"In Solutions"** (i.e., `not_in_solution_json = false`), not as "Discovered". mainTemplate connectors are ARM resources defined within the solution's package template, and synthetic connectors are explicitly declared as part of a solution via the override CSV. This matches their status as formally documented solution components on Microsoft Learn.

### Collection Method Detection

The analyzer determines the data collection method used by each connector through comprehensive content analysis. This analysis sets the `collection_method` and `collection_method_reason` columns in `connectors.csv`.

#### Collection Methods

| Method | Description | Detection Criteria |
|--------|-------------|-------------------|
| **Azure Monitor Agent (AMA)** | Modern log collection agent | Title contains "AMA" or "via AMA", ID ends with "ama", `sent_by_ama` field, "Azure Monitor Agent" in description, "CEF via AMA" or "Syslog via AMA" patterns |
| **Log Analytics Agent (MMA)** | Legacy Microsoft Monitoring Agent (deprecated) | Title mentions "Legacy Agent", "omsagent" references, "cef_installer.py" scripts, workspace ID/key patterns, `OmsSolutions` patterns, `InstallAgentOnVirtualMachine`/`InstallAgentOnNonAzure`/`InstallAgentOnLinuxNonAzure` patterns. Special case: connector ID `WindowsFirewall` (without Ama suffix) |
| **Azure Diagnostics** | Azure resource diagnostic settings | "AzureDiagnostics" references in content, "diagnostic settings" in description, `Microsoft.Insights/diagnosticSettings` resource, Azure Policy diagnostics (`policyDefinitionGuid` + `PolicyAssignment`), table category "Azure Resources" |
| **Native** | Built-in Sentinel integrations | `SentinelKinds` property present, Microsoft Defender/365/Entra ID connectors, known native connector IDs (`AzureActivity`, `AzureActiveDirectory`, `Office365`, `MicrosoftDefender`) - skipped if CCF content patterns detected |
| **Codeless Connector Framework (CCF)** | Microsoft's codeless connector platform (CCP/CCF) | `pollingConfig` present, `dcrConfig` with `RestApiPoller`, `GCPAuthConfig`, `dataConnectorDefinitions` (except AMA title connectors), ID contains "CCP"/"CCF"/"Codeless", ID contains "Polling" |
| **CCF Push** | CCF Push mode (partner pushes data via DCR/DCE) | `DeployPushConnectorButton` in connector definition (DCR/DCE-based push ingestion) |
| **CCF (Legacy)** | Legacy CCF with embedded pollingConfig | Initially detected as CCF, but reclassified when `pollingConfig` is found in the primary connector JSON and no separate CCF config file exists |
| **Azure Function** | Azure Functions-based data collection | Filename contains "FunctionApp"/"function_app"/"_api_function", description mentions "Azure Functions", ID contains "AzureFunction"/"FunctionApp", "Deploy to Azure" + "Function App" patterns, "Azure Function App" in content, Azure Functions pricing references |
| **REST API** | Direct API push/webhook collection | "REST API" in title/description, "push" in title/ID, webhook patterns, HTTP endpoint/trigger references |
| **Unknown (Custom Log)** | Method could not be determined | Only custom log table (`_CL`) references found, no other patterns matched |

#### Detection Priority

The detection algorithm uses a tiered priority system with 11 levels. When a connector explicitly declares its type in the title (e.g., "via AMA"), that takes precedence. Otherwise, patterns are detected in the following order:

| Priority | Detection Category | Detection Patterns |
|----------|-------------------|-------------------|
| **1** | **Explicit AMA/MMA in title** (highest) | Title contains "AMA", "via AMA", ID ends with "ama", title contains "Legacy Agent" or "via Legacy Agent". Special: `WindowsFirewall` connector is MMA. |
| **2** | **Azure Function filename** | Filename contains "FunctionApp"/"function_app"/"_api_function", ID contains "AzureFunction"/"FunctionApp" |
| **3** | **CCF content patterns** | `pollingConfig`, `dcrConfig` with `RestApiPoller`, `GCPAuthConfig`, `dataConnectorDefinitions` (unless AMA title). **CCF Push**: `DeployPushConnectorButton` (separately classified as "CCF Push") |
| **4** | **Azure Diagnostics** | "AzureDiagnostics" in content, "diagnostic settings" in description, `Microsoft.Insights/diagnosticSettings`, Azure Policy diagnostics. Skipped if Azure Function filename detected. |
| **5** | **CCF name patterns** | ID contains "CCP"/"CCF"/"Codeless", ID contains "Polling". Skipped if Azure Diagnostics patterns found. |
| **6** | **Azure Function content** | "Azure Functions" in description, "Deploy to Azure" + "Function App", Azure Functions pricing. Skipped if CCF content detected. |
| **7** | **Native Microsoft** | `SentinelKinds`, Microsoft Defender/365/Entra ID titles, known native IDs. Skipped if CCF content detected. |
| **8** | **Secondary AMA/MMA** | `sent_by_ama`, "omsagent", "CEF/Syslog via AMA", "cef_installer.py", workspace ID/key, `OmsSolutions`, `InstallAgent*` patterns |
| **9** | **REST API** | "REST API" in title/description, "push"/"webhook"/"http endpoint" patterns |
| **10** | **Table metadata fallback** | Table category "Azure Resources" → Azure Diagnostics, "virtualmachines" in resource_types → AMA. Only if no stronger patterns. |
| **11** | **Custom log fallback** (lowest) | `_CL` table suffix, no other patterns matched |

#### Final Selection Logic

After all patterns are detected, the final method is selected using this priority order:
1. If title explicitly indicates AMA → select AMA
2. If title explicitly indicates MMA → select MMA
3. Otherwise: Azure Diagnostics > CCF Push > CCF > Azure Function > Native > MMA > AMA > REST API > Unknown
4. Post-processing: CCF connectors with `pollingConfig` in primary JSON and no separate config file are reclassified as **CCF (Legacy)**

#### CSV Fields Affected

| Field | Description |
|-------|-------------|
| `collection_method` | The detected collection method (in `connectors.csv`) |
| `collection_method_reason` | Explanation of why this method was selected |
| `ccf_config_file` | GitHub URL to the CCF configuration file (populated for CCF and CCF Push connectors; empty for CCF Legacy) |
| `ccf_capabilities` | Semicolon-separated list of CCF capabilities extracted from the config file or embedded pollingConfig (e.g., `APIKey;Paging;POST`) |

> **Key Design Decisions:**
> - **Azure Diagnostics > CCF name**: Connectors with `_CCP` suffix that reference "AzureDiagnostics" are Azure Diagnostics (the CCP suffix indicates the connector was built using the CCF framework, but it still collects via Azure Diagnostics)
> - **CCF content > Azure Function content**: Connectors with `dcrConfig`/`dataConnectorDefinitions` that also have "Deploy Azure Function" patterns are CCF (e.g., OktaSSOv2)
> - **Azure Function filename is strong**: Connectors with "FunctionApp" in the filename are Azure Functions regardless of content patterns
> - **Title-based AMA/MMA is strongest**: When a connector title explicitly includes "AMA" or "Legacy Agent", it overrides all other patterns
> - **MMA content patterns override AMA metadata**: MMA-era patterns like `OmsSolutions` and `InstallAgent*` take precedence over AMA detection from table metadata

### CCF Configuration and Capabilities

For connectors detected as **CCF** or **CCF Push**, the analyzer locates the CCF configuration file and extracts capabilities from it. For **CCF (Legacy)** connectors, capabilities are extracted from the embedded `pollingConfig`.

#### CCF Config File Discovery

The analyzer searches the connector's directory (and sibling `*_ccp/` directories) for files matching these patterns (in order):
- `*PollingConfig*.json`, `*PollerConfig*.json` — standard CCF poller configs
- `*DataConnectorPoller*.json`, `*dataPoller*.json` — alternative naming
- `*_poller*.json` — older naming convention
- `connectors.json` — modern CCF naming (e.g., Bitwarden)
- `*_dataConnector*.json` (excluding `*connectorDefinition*`) — Push connector configs
- Sibling `*_ccp/` directories — some connectors (e.g., GCP) store configs in a sibling directory with `_ccp` suffix

Files matching skip patterns are excluded: `azuredeploy*`, `mainTemplate*`, `*connectorDefinition*`, `definitions.json`, `*_table.*`, `*_dcr.*`, and common non-config files.

If no separate config file is found but `pollingConfig` exists in the primary connector JSON, the connector is reclassified as **CCF (Legacy)** and capabilities are extracted from the embedded config.

#### CCF Capabilities Extracted

| Capability | Description |
|-----------|-------------|
| **Connector Kind** | Non-default kinds: `GCP`, `AmazonWebServicesS3`, `Push`, `StorageAccountBlobContainer`, `WebSocket`, `OCI`, etc. (`RestApiPoller` is omitted as it's the default) |
| **Auth Type** | Authentication method: `APIKey`, `OAuth2`, `Basic`, `JwtToken`, `Push`, `ServicePrincipal`, `Session`, etc. |
| `Paging` | Whether the connector uses paging to retrieve results |
| `POST` | Whether the connector uses HTTP POST (GET is the default) |
| `MvExpand` | Whether the config uses the MvExpand transformer (`nestedTransformName` containing `MvExpandTransformer`) |
| `Nested` | Whether the config uses nested steps (`stepType: Nested`) |

### Ingestion API Detection

For API-based connectors (CCF Push, Azure Function, REST API, Unknown Custom Log), the analyzer determines whether they use the modern **Log Ingestion API** or the legacy **HTTP Data Collector API** (also known as Log Analytics Data Collector API). CCF and CCF (Legacy) connectors are excluded because their ingestion is platform-managed (Sentinel PaaS) — the connector definition doesn't configure the ingestion API.

This analysis runs in a second pass after table schemas are fully loaded, because the column suffix heuristic requires schema data.

#### Detection Rules (in priority order)

1. **CCF Push** → Always **Log Ingestion API** (DCR-based, solution code pushes data via DCR)
2. **Azure Function** → Scan `*.py` files in the solution's Data Connectors folder for API-specific patterns (excluding vendored directories like `.python_packages`):
   - Log Ingestion API indicators: `LogsIngestionClient`, `azure.monitor.ingestion`, `azure-monitor-ingestion`, `ingestion_endpoint`, `DCR_ID`, `RULE_ID`, `data_collection_rule`
   - HTTP Data Collector API indicators: `SharedKey`, `build_signature`, `api/logs`, `Log-Type`, `LogAnalyticsData`
   - If both detected → "Undetermined" (typically indicates migration in progress)
3. **REST API / Unknown (Custom Log)** → Scan connector JSON for workspace key patterns: `sharedKeys`, `WorkspaceId`, `PrimaryKey` → **HTTP Data Collector API**
4. **Fallback** → Table column suffix heuristic:
   - If >40% of table columns end with type suffixes (`_s`, `_d`, `_b`, `_t`, `_g`) → **HTTP Data Collector API**
   - If table has DCR-sourced schema and <10% type suffixes → **Log Ingestion API**

#### CSV Fields Affected

| Field | Description |
|-------|-------------|
| `ingestion_api` | Detected API: "Log Ingestion API", "HTTP Data Collector API", "Undetermined", or empty if not applicable |
| `ingestion_api_reason` | Human-readable reason for the detection (e.g., "CCF connectors use DCR-based Log Ingestion API") |

### Custom Log V1 (CLv1) Detection

The analyzer identifies tables using the legacy **Custom Log V1** schema format. These are custom log tables originally created through the HTTP Data Collector API, which automatically appends type suffixes (`_s`, `_d`, `_b`, `_t`, `_g`) to column names to indicate data types.

This detection runs after both table schemas and ingestion API detection are complete.

#### Detection Rules

A table is marked as CLv1 (`is_clv1 = true`) if **either** condition is met:

1. **Column suffix heuristic** — More than 40% of the table's non-standard columns end with type suffixes (`_s`, `_d`, `_b`, `_t`, `_g`). Standard columns excluded from the count: `TimeGenerated`, `TenantId`, `Type`, `MG`, `ManagementGroupName`, `SourceSystem`, `_ResourceId`, `_SubscriptionId`.

2. **Connector-based inference** — The table name ends with `_CL` (custom log) AND at least one connector that ingests into this table either:
   - Uses the **AMA** collection method, or
   - Uses the **HTTP Data Collector API** ingestion API

A connector is marked as CLv1 if **any** of its tables are CLv1.

#### CSV Fields Affected

| Field | CSV File | Description |
|-------|----------|-------------|
| `is_clv1` | `tables.csv` | `true` if the table uses CLv1 schema format |
| `is_clv1` | `connectors.csv` | `true` if any of the connector's tables use CLv1 schema format |

### Filter Fields Detection

The analyzer extracts filter field values from KQL queries to identify vendor/product-specific filtering patterns. This helps understand which data sources a connector, parser, or content item targets.

#### Supported Filter Fields

| Field | Canonical Table | Description |
|-------|----------------|-------------|
| `DeviceVendor` | CommonSecurityLog | CEF vendor identifier |
| `DeviceProduct` | CommonSecurityLog | CEF product identifier |
| `DeviceEventClassID` | CommonSecurityLog | CEF event class identifier |
| `EventVendor` | Multiple (ASIM) | ASIM normalized vendor |
| `EventProduct` | Multiple (ASIM) | ASIM normalized product |
| `EventType` | Multiple (ASIM) | ASIM normalized event type |
| `ResourceType` | AzureDiagnostics | Azure resource type |
| `Category` | AzureDiagnostics | Diagnostic category |
| `Resource` | AzureDiagnostics/AzureMetrics/AzureActivity | Azure resource instance name |
| `ResourceProvider` | AzureActivity | Azure resource provider |
| `EventID` | WindowsEvent/SecurityEvent/Event | Windows event ID |
| `Source` | Event | Windows Event Log source |
| `Provider` | WindowsEvent | Windows event provider |
| `Facility` | Syslog | Syslog facility |
| `ProcessName` | Syslog | Syslog process name |
| `ProcessID` | Syslog | Syslog process ID |
| `SyslogMessage` | Syslog | Syslog message content |
| `EventName` | AWSCloudTrail | AWS API event name |
| `ActionType` | DeviceEvents/DeviceFileEvents/etc. | Microsoft Defender XDR action type |
| `OperationName` | AuditLogs/AzureActivity/OfficeActivity/SigninLogs | Azure/M365 operation name |
| `OfficeWorkload` | OfficeActivity | Office 365 workload type |
| `RecordType` | OfficeActivity | Office 365 record type (numeric) |

#### Supported Operators

| Operator Category | Operators | Example |
|-------------------|-----------|---------|
| **Equality** | `==`, `=~`, `!=` | `DeviceVendor == "Fortinet"` |
| **In operators** | `in`, `in~`, `!in`, `!in~` | `EventID in (4624, 4625)` |
| **String operators** | `has`, `has_any`, `has_all`, `contains`, `startswith`, `endswith` | `SyslogMessage has "error"` |
| **Negative string** | `!has`, `!contains`, `!startswith`, `!endswith` | `SyslogMessage !has "debug"` |
| **Case-sensitive** | `has_cs`, `contains_cs`, `startswith_cs`, `endswith_cs` | `ProcessName has_cs "sshd"` |

> **Note:** `EventID`, `ProcessID`, and `RecordType` fields only support equality and in operators, not string operators.

#### Detection Logic

The filter field extraction follows these rules:

1. **Table-aware mapping**: When tables in the query are known, fields are mapped to their canonical tables
   - `DeviceVendor`/`DeviceProduct`/`DeviceEventClassID` → CommonSecurityLog
   - `EventVendor`/`EventProduct`/`EventType` → Context-dependent (ASIM tables)
   - `ResourceType`/`Category` → AzureDiagnostics
   - `Resource` → AzureDiagnostics, AzureMetrics, or AzureActivity (based on which is in query)
   - `ResourceProvider` → AzureActivity
   - `EventID` → WindowsEvent, SecurityEvent, or Event (based on which is in query)
   - `Source` → Event
   - `Provider` → WindowsEvent
   - `Facility`/`ProcessName`/`ProcessID`/`SyslogMessage` → Syslog
   - `EventName` → AWSCloudTrail
   - `ActionType` → DeviceEvents, DeviceFileEvents, DeviceProcessEvents, etc. (MDE/XDR tables)
   - `OperationName` → AuditLogs, AzureActivity, OfficeActivity, SigninLogs (context-dependent)
   - `OfficeWorkload`/`RecordType` → OfficeActivity

2. **ASIM vendor/product skipping**: When `skip_asim_vendor_product=True`, `EventVendor` and `EventProduct` are skipped because ASIM parsers SET these values (not filter by them)

3. **Context filtering**: The extractor skips fields that appear in:
   - `extend` statements (computed fields)
   - `project` statements (output field definitions)
   - Line comments (`//`)
   - Block comments (`/* */`)

4. **In operator value extraction**: Literal values in `in` operators are parsed, supporting:
   - String literals: `in ("value1", "value2")`
   - Integer literals: `in (4624, 4625, 4634)`
   - Case-insensitive: `in~` variant
   - Variable resolution: `let EventList = dynamic([...])` then `EventName in~ (EventList)`

5. **String operator patterns**: Match patterns like `field has "value"` or `field has_any ("val1", "val2")`

6. **Operator folding**: Multiple equality operators for the same field are combined:
   - Multiple `==` values → single `in` operator with comma-separated values
   - Multiple `=~` values → single `in~` operator
   - Case-insensitive values take precedence over case-sensitive for deduplication

#### Output Format

Filter fields are formatted as a pipe-separated (`|`) list with the structure:
```
Table.Field operator "value" | Table.Field operator "value1,value2"
```

Examples:
```
CommonSecurityLog.DeviceVendor == "Fortinet" | CommonSecurityLog.DeviceProduct == "FortiGate"
Syslog.Facility == "authpriv" | Syslog.SyslogMessage has "error"
AzureDiagnostics.Category in "AzureFirewallNetworkRule,AzureFirewallApplicationRule"
AWSCloudTrail.EventName in~ "CreateUser,DeleteUser,AttachUserPolicy"
```

#### CSV Fields Affected

| CSV File | Field | Description |
|----------|-------|-------------|
| `connectors.csv` | `filter_fields` | Filter fields from connector queries |
| `connectors.csv` | `event_vendor` | Extracted vendor values (semicolon-separated) |
| `connectors.csv` | `event_product` | Extracted product values (semicolon-separated) |
| `connectors.csv` | `event_vendor_product_by_table` | JSON mapping of tables to vendor/product pairs |
| `content_items.csv` | `content_filter_fields` | Filter fields from content item queries |
| `content_items.csv` | `content_event_vendor` | Extracted vendor values |
| `content_items.csv` | `content_event_product` | Extracted product values |
| `parsers.csv` | `filter_fields` | Filter fields from solution parser queries |
| `asim_parsers.csv` | `filter_fields` | Filter fields from ASIM parser queries |

> **Note:** For ASIM parsers, `EventVendor` and `EventProduct` fields are skipped because ASIM parsers SET these values (via `extend`) rather than filter by them. The extraction focuses on source-identifying fields like `DeviceVendor`, `Facility`, etc.

### Connector Association Algorithm

For standalone/GitHub Only content items and ASIM parsers, the analyzer automatically associates relevant connectors based on table and filter field matching. This populates the `associated_connectors` and `associated_solutions` fields.

#### Matching Criteria

A connector matches a target (content item or parser) if:

1. **Shared Tables**: The connector and target share at least one table
2. **Filter Subset**: For shared tables, the connector's filter values are a subset of (or equal to) the target's filter values

#### Filter Subset Logic

- A connector with **no filter fields** matches any target using the same table (it provides all data)
- A connector filtering on `DeviceVendor == "Fortinet"` matches targets filtering on `Fortinet` or `Fortinet AND FortiGate`
- A connector filtering on specific products does NOT match targets filtering on different products

#### Cross-Field Override: Category → ResourceType

For AzureDiagnostics, certain `Category` values are known to be produced only by a specific Azure resource type. When a connector filters on `ResourceType` and the target only filters on `Category`, the `CATEGORY_TO_RESOURCE_TYPE` mapping is consulted: if all of the target's Category values map to the connector's ResourceType, the match is allowed (the target is more restrictive).

Currently mapped categories:

| Category | ResourceType |
|----------|-------------|
| `AzureFirewallNetworkRule` | `AZUREFIREWALLS` |
| `AzureFirewallApplicationRule` | `AZUREFIREWALLS` |
| `AzureFirewallNatRule` | `AZUREFIREWALLS` |
| `AzureFirewallThreatIntel` | `AZUREFIREWALLS` |
| `AzureFirewallIdpsSignature` | `AZUREFIREWALLS` |
| `AzureFirewallDnsProxy` | `AZUREFIREWALLS` |

This mapping can be extended for other Azure resource types as needed.

#### Example Matches

| Connector Filters | Target Filters | Match? | Reason |
|-------------------|----------------|--------|--------|
| (none) | `DeviceVendor == "Fortinet"` | ✅ | Connector provides all data |
| `DeviceVendor == "Fortinet"` | `DeviceVendor == "Fortinet"` | ✅ | Exact match |
| `DeviceVendor == "Fortinet"` | `DeviceVendor in "Fortinet,PaloAlto"` | ✅ | Connector subset of target |
| `DeviceVendor == "Fortinet"` | `DeviceVendor == "PaloAlto"` | ❌ | No overlap |
| `DeviceProduct == "FortiGate"` | `DeviceVendor == "Fortinet"` | ❌ | Different field, can't confirm match |
| `ResourceType == "AZUREFIREWALLS"` | `Category == "AzureFirewallNetworkRule"` | ✅ | Category implies ResourceType (override) |

#### Exclusions

The algorithm excludes:
- **Deprecated connectors**: Connectors with `[DEPRECATED]` in title or `availability.status` of 0 in connector JSON
- **Content-only connectors**: Connectors that use data from other connectors (don't ingest data themselves)
- **Excluded tables**: Tables that appear in connector documentation but aren't actually ingested

### Parser Resolution

When a connector references a parser function (e.g., `ASimDns`):
1. Script locates the parser YAML file in the solution's Parsers directory
2. Extracts the FunctionQuery from the parser
3. Analyzes the query to find actual table references (e.g., `Syslog`, `DnsEvents`)
4. Maps the parser name to the discovered tables
5. Replaces parser reference with actual tables in the output

### Table Detection Methods

The analyzer uses a unified KQL query parsing engine (`extract_query_table_tokens()`) to identify tables across all source types: connectors, content items, and parsers. This ensures consistent table detection regardless of the source.

#### Detection Sources by Type

| Source Type | Query Locations | Additional Processing |
|-------------|-----------------|----------------------|
| **Connectors** | `graphQueries.*.baseQuery`, `sampleQueries.*.query`, `dataTypes.*.lastDataReceivedQuery`, `connectivityCriterias.*.value`, ARM template variables | Parser expansion, dataType name/query reconciliation |
| **Content Items** | YAML `query` field, JSON `query` field | ASIM parsers kept as-is, non-ASIM parsers expanded |
| **Solution Parsers** | `FunctionQuery` (YAML), raw query text (.kql/.txt) | Tables extracted, parser names recorded |
| **ASIM Parsers** | `ParserQuery` (YAML) | Sub-parser references tracked separately |

#### Table Detection Method Labels

When enabled with `--show-detection-methods`, the `table_detection_methods` column shows exactly how each table was detected:

| Method Label | Description |
|--------------|-------------|
| `graphQueries.{index}.baseQuery` | From connector graphQueries array |
| `sampleQueries.{index}.query` | From connector sampleQueries array |
| `dataTypes.{index}.lastDataReceivedQuery` | From dataTypes definitions |
| `dataTypes.{index}.name` | From dataTypes name field (when query missing) |
| `connectivityCriterias.{index}.value.{sub_index}` | From connectivity criteria queries |
| `logAnalyticsTableId` | Extracted from ARM template variables |
| `parser:{parser_name}` | Resolved from parser function to actual table |

### Context-Aware Table Detection

The KQL parser uses intelligent query parsing to distinguish actual table names from field names and variables:

#### Parsing Techniques

| Technique | Description |
|-----------|-------------|
| **Let Assignment Tracking** | Tracks `let var = TableName` assignments to avoid treating variables as tables |
| **Pipeline Head Detection** | Identifies tables at the start of pipeline expressions (`TableName \| where...`) |
| **Union Statement Parsing** | Extracts all table names from `union` expressions with comma or parenthesis separators |
| **Inline Pipe Detection** | Handles `TableName \| where` patterns on the same line |
| **Parenthesis/Brace Context** | Detects tables in `(TableName \| ...)` and `{ TableName \| ...}` patterns |
| **ASIM View Detection** | Recognizes `_Im_*` and `_ASim_*` function calls as table references |
| **Comment Stripping** | Removes `//` line comments before analysis |
| **Field Context Filtering** | Excludes identifiers after `\| project`, `\| project-keep`, `\| project-reorder`, `\| extend`, `\| parse` operators |

#### Table Validation

All candidates are filtered through `is_valid_table_candidate()` which:
- Accepts known Azure Monitor tables (from reference data)
- Accepts custom log tables (ending in `_CL`)
- Accepts ASIM views/parsers (`_Im_*`, `_ASim_*`, `im*`, `ASim*`)
- Accepts known parser names (when provided)
- Rejects KQL keywords, operators, and common false positives

### JSON Parsing Tolerance

The analyzer includes enhanced JSON parsing to handle common issues in ARM templates:

- Strips `// comments` from JSON (common in ARM templates)
- Removes trailing commas before `}` or `]`
- Falls back to json5 parser if available for even more tolerance

## Examples

### Example 1: Simple Connector
A connector directly references `Syslog` table in its queries:
```
Table: Syslog
solution_name: ISC Bind
connector_id: ISCBind
table_detection_methods: sampleQueries.0.query;sampleQueries.1.query
```

### Example 2: Parser-Based Connector
A connector references a parser that resolves to actual tables:
```
Table: Syslog
solution_name: Watchguard Firebox
connector_id: WatchguardFirebox
table_detection_methods: parser:WatchGuardFirebox
```

### Example 3: Multiple Tables
A connector ingests to multiple custom log tables:
```
Table: CyfirmaASCertificatesAlerts_CL
solution_name: Cyfirma Cyber Intelligence
connector_id: CyfirmaCyberIntelligence
```

## Troubleshooting

### Common Issues

**Issue**: Script reports "Permission denied" when writing CSV
- **Solution**: Close the CSV file if open in Excel or another application

**Issue**: Some connectors missing from output
- **Solution**: Check the report CSV for the reason (likely no_table_definitions or parser_tables_only)

**Issue**: Parser tables not resolving
- **Solution**: Ensure parser YAML files exist in the solution's Parsers directory with valid FunctionQuery

**Issue**: JSON parse errors for specific connectors
- **Solution**: Install json5 (`pip install json5`) for better tolerance, or fix JSON syntax in the connector file

### Debug Mode

To see which files are being processed:
```bash
python map_solutions_connectors_tables.py --show-detection-methods
```

This will include the `table_detection_methods` column showing exactly how each table was detected.
