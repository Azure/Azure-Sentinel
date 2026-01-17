# Solution Connector Tables Analyzer

**Script:** `map_solutions_connectors_tables.py`

## Overview

Scans the Azure-Sentinel repository to:
- Extract table references from connector JSON files (queries, sample queries, data types)
- **Extract table references from content items** (analytics rules, hunting queries, playbooks, workbooks, watchlists, summary rules)
- **Collect standalone content from top-level directories** (Detections, Hunting Queries, Workbooks, Playbooks, Summary rules, Watchlists)
- Resolve parser function references to actual tables
- Flatten solution metadata from SolutionMetadata.json files
- Generate a comprehensive mapping of connectors to tables with full metadata
- **Include ALL solutions in the output**, even those without data connectors (e.g., solutions containing only analytics rules, workbooks, hunting queries, or playbooks)
- **Classify content items by source**: Solution (from Solutions/), Standalone (with metadata), or GitHub Only (no metadata)
- Report issues and exceptions for solutions with missing or incomplete definitions

### Content Item Analysis

The script analyzes KQL queries in both solution content items and standalone top-level content to extract table references:

| Content Type | Solution Patterns | Standalone Patterns | Query Fields |
|--------------|-------------------|---------------------|--------------|
| **Analytics Rules** | `Analytic Rules/*.yaml` | `Detections/**/*.yaml` | `query`, `triggerOperator` |
| **Hunting Queries** | `Hunting Queries/*.yaml` | `Hunting Queries/**/*.yaml` | `query` |
| **Playbooks** | `Playbooks/**/*.json` | `Playbooks/*/azuredeploy.json` | Azure Monitor Logs query actions |
| **Workbooks** | `Workbooks/*.json` | `Workbooks/*.json` | `query` fields in workbook steps |
| **Watchlists** | `Watchlists/*.json` | `Watchlists/*/watchlist.json` | Table references in watchlist queries |
| **Summary Rules** | `Summary Rules/*.json` | `Summary rules/**/*.yaml` | Query fields |

For playbooks, the script tracks whether tables are **read from** (Azure Monitor query), **written to** (Send Data action), or both.

**Note:** Solutions without data connectors are included in the CSV output with empty `connector_id`, `connector_title`, `connector_description`, `connector_publisher`, `connector_files`, and `Table` fields. This ensures complete solution coverage in the documentation while clearly indicating which solutions do not include data ingestion components.

**Important:** This analysis covers connectors managed through Solutions in the Azure-Sentinel GitHub repository. A small number of connectors (such as Microsoft Dataverse, Microsoft Power Automate, Microsoft Power Platform Admin, and SAP connectors) are not managed via Solutions and are therefore not included in this output.

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
| `--tables-reference-csv` | `tables_reference.csv` | Path to tables_reference.csv for table metadata |
| `--mapping-csv` | `solutions_connectors_tables_mapping_simplified.csv` | Path for the simplified mapping CSV file |
| `--overrides-csv` | `solution_analyzer_overrides.csv` | Path to overrides CSV file for field value overrides |
| `--show-detection-methods` | `False` | Include table_detection_methods column showing how each table was detected |
| `--skip-marketplace` | `False` | Skip Azure Marketplace availability checking |
| `--refresh-marketplace` | `False` | Force refresh of marketplace cache (ignore cached results) |

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
```

## Override System

Both `map_solutions_connectors_tables.py` and `collect_table_info.py` support an override system that allows you to modify field values in the output based on pattern matching. This is useful for:
- Setting `collection_method` to AMA for specific tables (e.g., Syslog, CommonSecurityLog)
- Assigning categories to tables based on naming patterns (e.g., all AWS* tables → AWS category)
- Correcting or supplementing data that cannot be automatically detected

Both scripts use the same override file (`solution_analyzer_overrides.csv`) by default, ensuring consistent categorization across all outputs.

### Override File Format

The override file is a CSV with the following columns:

| Column | Description |
|--------|-------------|
| `Entity` | Entity type to match: `table`, `connector`, or `solution` (case insensitive) |
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

## Output Files

### 1. solutions_connectors_tables_mapping.csv (Primary Output)

The main CSV file containing one row per unique combination of solution, connector, and table.

**Note:** Newlines in the `connector_description` and `connector_permissions` fields are replaced with `<br>` tags to ensure proper rendering in GitHub's CSV viewer. The `connector_instruction_steps` field uses standard JSON encoding with `\n` for newlines as it contains JSON-formatted data.

#### Column Descriptions

| Column | Description |
|--------|-------------|
| `Table` | The table name (e.g., Syslog, CommonSecurityLog, CustomLog_CL). Empty for solutions without data connectors. |
| `solution_name` | Solution folder name |
| `solution_folder` | GitHub URL to the solution's folder |
| `solution_publisher_id` | Publisher ID from SolutionMetadata.json |
| `solution_offer_id` | Offer ID from SolutionMetadata.json |
| `solution_first_publish_date` | First publication date |
| `solution_last_publish_date` | Last update date |
| `solution_version` | Solution version number |
| `solution_support_name` | Support provider name (e.g., Microsoft, Community) |
| `solution_support_tier` | Support tier (e.g., Microsoft, Partner, Community) |
| `solution_support_link` | Support link URL |
| `solution_author_name` | Author name from metadata |
| `solution_categories` | Comma-separated list of solution categories |
| `connector_id` | Unique connector identifier. Empty for solutions without data connectors. |
| `connector_publisher` | Connector publisher name. Empty for solutions without data connectors. |
| `connector_title` | Connector display title. Empty for solutions without data connectors. |
| `connector_description` | Connector description (newlines replaced with `<br>` for GitHub CSV rendering). Empty for solutions without data connectors. |
| `connector_instruction_steps` | Setup and configuration instructions from connector UI definitions, stored as JSON-encoded string. Rendered in documentation using Microsoft Sentinel UI definitions. Empty for solutions without data connectors. |
| `connector_permissions` | Required permissions and prerequisites from connector UI definitions, stored as JSON-encoded string. Rendered in documentation according to Microsoft Sentinel permissions schema (resourceProvider, customs, licenses, tenant). Empty for solutions without data connectors. |
| `connector_files` | Semicolon-separated list of GitHub URLs to connector definition files. Empty for solutions without data connectors. |
| `is_unique` | `true` if table appears in only one connector file, `false` otherwise |
| `table_detection_methods` | (Optional, with --show-detection-methods) Semicolon-separated list of methods used to detect this table |

#### GitHub Links

All file references are converted to direct GitHub URLs pointing to the master branch:

**solution_folder:**
```
https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/{solution_name}
```

**connector_files:**
```
https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/{solution_name}/Data Connectors/{file_path}
```

### 2. connectors.csv (Connector Details with Collection Method)

Contains one row per unique connector with all connector-specific fields and collection method analysis.

| Column | Description |
|--------|-------------|
| `connector_id` | Unique connector identifier |
| `connector_publisher` | Connector publisher name |
| `connector_title` | Connector display title |
| `connector_description` | Connector description |
| `connector_instruction_steps` | Setup and configuration instructions (JSON) |
| `connector_permissions` | Required permissions (JSON) |
| `connector_id_generated` | `true` if connector ID was auto-generated from title |
| `connector_files` | Semicolon-separated list of GitHub URLs to connector definition files |
| `connector_readme_file` | Path to connector README file (if exists) |
| `collection_method` | Data collection method (see Collection Method Detection) |
| `collection_method_reason` | Explanation of how collection method was determined |
| `event_vendor` | Semicolon-separated list of vendor values extracted from queries |
| `event_product` | Semicolon-separated list of product values extracted from queries |
| `event_vendor_product_by_table` | JSON mapping of tables to vendor/product pairs |
| `filter_fields` | Filter fields extracted from queries (see Filter Fields Detection) |
| `not_in_solution_json` | `true` if connector was found by file scanning but not listed in the Solution JSON |
| `solution_name` | Name of the parent solution |
| `is_deprecated` | `true` if connector title contains "[DEPRECATED]" or "[Deprecated]" |
| `is_published` | `true` if parent solution is published on Azure Marketplace |

### 3. solutions.csv (Solution Details)

Contains one row per solution with all solution-specific metadata. Metadata is sourced from both `SolutionMetadata.json` and `Data/Solution_*.json` files.

| Column | Description |
|--------|-------------|
| `solution_name` | Official solution name from Solution JSON (or folder name if not available) |
| `solution_folder` | GitHub URL to the solution's folder |
| `solution_publisher_id` | Publisher ID from SolutionMetadata.json |
| `solution_offer_id` | Offer ID from SolutionMetadata.json |
| `solution_first_publish_date` | First publication date |
| `solution_last_publish_date` | Last update date |
| `solution_version` | Solution version from Solution JSON or SolutionMetadata.json |
| `solution_support_name` | Support provider name |
| `solution_support_tier` | Support tier (Microsoft, Partner, Community) |
| `solution_support_link` | Support link URL |
| `solution_author_name` | Author name from Solution JSON (e.g., "Microsoft - support@microsoft.com") |
| `solution_categories` | Comma-separated list of solution categories (e.g., "Security - Others, domains") |
| `solution_readme_file` | Path to solution README file (if exists) |
| `solution_logo_url` | URL to solution logo image extracted from HTML img tag in Solution JSON Logo field |
| `solution_description` | Full solution description with HTML/markdown formatting from Solution JSON |
| `solution_dependencies` | Semicolon-separated list of dependent solution IDs from `dependentDomainSolutionIds` |
| `has_connectors` | `true` if solution has data connectors, `false` otherwise |
| `is_published` | `true` if solution is published on Azure Marketplace |
| `marketplace_url` | URL to the solution's Azure Marketplace listing |

**Solution JSON File Selection:**

The script locates Solution JSON files using this algorithm:
1. Look for `Data/` or `data/` folder within the solution directory
2. Find files matching the pattern `Solution_*.json` (e.g., `Solution_1Password.json`)
3. Parse the first matching JSON file to extract Name, Logo, Author, Version, and Description
4. Logo URL is extracted from HTML img tags like `<img src="https://..." width="75px" height="75px">`

### 4. tables.csv (Table Metadata)

Contains one row per unique table referenced by connectors, with metadata from Azure Monitor documentation.

| Column | Description |
|--------|-------------|
| `table_name` | Table name |
| `description` | Table description from Azure Monitor documentation |
| `category` | Table category (e.g., Security, Audit, Azure Resources) |
| `support_tier` | Support tier derived from associated solutions |
| `collection_method` | Data collection method (from tables_reference.csv or overrides) |
| `resource_types` | Azure resource types that emit to this table |
| `source_azure_monitor` | Whether table is in Azure Monitor reference |
| `source_defender_xdr` | Whether table is in Defender XDR schema |
| `azure_monitor_doc_link` | Link to Azure Monitor documentation |
| `defender_xdr_doc_link` | Link to Defender XDR documentation |
| `basic_logs_eligible` | Whether table supports Basic Logs plan |
| `supports_transformations` | Whether ingestion-time transformations are supported |
| `ingestion_api_supported` | Whether Data Collector API ingestion is supported |

> **Note:** Metadata is sourced from `tables_reference.csv`. Tables not found in the reference file will have empty metadata fields. Run `collect_table_info.py` first to populate this data.

### 5. solutions_connectors_tables_mapping_simplified.csv (Simplified Mapping)

A simplified mapping file containing only key fields for linking connectors, tables, and solutions.

| Column | Description |
|--------|-------------|
| `solution_name` | Solution folder name |
| `connector_id` | Connector identifier |
| `table_name` | Table name |

### 6. content_items.csv (Content Item Details)

Contains one row per content item (analytics rule, hunting query, playbook, workbook, parser, watchlist, or summary rule) found in solutions or top-level directories.

| Column | Description |
|--------|-------------|
| `content_id` | Unique identifier for the content item (GUID from YAML/JSON) |
| `content_name` | Display name of the content item |
| `content_type` | Type: `analytic_rule`, `hunting_query`, `playbook`, `workbook`, `parser`, `watchlist`, `summary_rule` |
| `content_description` | Description of the content item |
| `content_file` | Filename of the source file |
| `content_readme_file` | Path to associated README file (if exists) |
| `content_severity` | Severity level (for analytics rules): `High`, `Medium`, `Low`, `Informational` |
| `content_status` | Status field from content item |
| `content_kind` | Kind/type from content item |
| `content_tactics` | MITRE ATT&CK tactics (comma-separated) |
| `content_techniques` | MITRE ATT&CK techniques (comma-separated) |
| `content_required_connectors` | Required data connectors (from requiredDataConnectors field) |
| `content_query_status` | Query status: `has_query`, `no_query`, `query_error` |
| `content_event_vendor` | Event vendor extracted from query filter fields |
| `content_event_product` | Event product extracted from query filter fields |
| `content_filter_fields` | Filter fields extracted from content query (see Filter Fields Detection) |
| `content_github_url` | Direct GitHub URL to the content file (for standalone items only) |
| `content_source` | Source location: `Solution` (from Solutions/), `Standalone` (top-level with metadata), `GitHub Only` (top-level without metadata) |
| `metadata_source_kind` | Source kind from YAML metadata section: `Community`, `Solution`, `Standalone` |
| `metadata_author` | Author name from YAML metadata section |
| `metadata_support_tier` | Support tier from YAML metadata section: `Microsoft`, `Partner`, `Community` |
| `metadata_categories` | Categories/domains from YAML metadata section (comma-separated) |
| `not_in_solution_json` | `true` if item was found by file scanning but not listed in Solution JSON (marked with ⚠️ in docs) |
| `solution_name` | Solution name (empty for standalone content) |
| `solution_folder` | Solution folder path (empty for standalone content) |
| `is_published` | `true` if parent solution is published on Azure Marketplace (empty for standalone content) |

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

### 7. content_tables_mapping.csv (Content Item to Table Mapping)

Contains one row per unique combination of solution, content item, and table. This maps tables found in KQL queries within analytics rules, hunting queries, playbooks, workbooks, watchlists, and summary rules.

| Column | Description |
|--------|-------------|
| `solution_name` | Solution folder name |
| `solution_folder` | Solution folder path |
| `content_type` | Type of content item: `analytic_rule`, `hunting_query`, `playbook`, `workbook`, `watchlist`, `summary_rule` |
| `content_id` | Content item identifier |
| `content_name` | Name or filename of the content item |
| `content_file` | Source filename |
| `table_name` | Table name extracted from the KQL query |
| `table_usage` | Usage indicator for playbooks: `read`, `write`, or `read/write`. Empty for other content types (assumed read). |
| `is_published` | `true` if parent solution is published on Azure Marketplace |

> **Note:** For playbooks, `table_usage` tracks whether the playbook reads from a table (Azure Monitor query), writes to it (Send Data action), or both. Other content types are assumed to only read from tables.

### 8. parsers.csv (Parser Details)

Contains one row per parser (both ASIM and non-ASIM) from solution directories and the legacy `/Parsers/*` directories.

| Column | Description |
|--------|-------------|
| `parser_name` | Parser function name |
| `parser_title` | Display title of the parser |
| `parser_version` | Parser version number |
| `parser_last_updated` | Last update date |
| `parser_category` | Parser category/type |
| `description` | Parser description |
| `tables` | Semicolon-separated list of source tables used by the parser |
| `source_file` | Relative path to the source file |
| `github_url` | Full GitHub URL to the parser definition |
| `solution_name` | Solution name (empty for legacy parsers) |
| `solution_folder` | Solution folder path |
| `location` | Location: `solution` (in Solutions directory) or `legacy` (in top-level /Parsers directory) |
| `file_type` | File type: `yaml`, `kql`, or `txt` |
| `discovered` | `true` if parser was found by file scanning but not listed in Solution JSON (marked with ⚠️ in docs) |

> **Note:** Parsers are collected from both solution `Parsers/` directories and the legacy top-level `/Parsers/*` directories. Legacy parsers are pre-Solutions parsers stored as .txt, .kql, or .yaml files.

### 9. asim_parsers.csv (ASIM Parser Details)

Contains one row per ASIM parser from the `/Parsers/ASim*/Parsers` directories. This includes all ASIM (Advanced Security Information Model) parsers with full metadata.

| Column | Description |
|--------|-------------|
| `parser_name` | Parser function name (e.g., `ASimDnsAzureFirewall`) |
| `equivalent_builtin` | Built-in parser alias (e.g., `_ASim_Dns_AzureFirewall`) |
| `schema` | ASIM schema name (e.g., `Dns`, `NetworkSession`, `Authentication`) |
| `schema_version` | Schema version number |
| `parser_type` | Parser type: `union` (schema-level aggregator), `source` (product-specific), or `empty` (placeholder) |
| `parser_title` | Display title of the parser |
| `parser_version` | Parser version number |
| `parser_last_updated` | Last update date |
| `product_name` | Product/source name (e.g., `Azure Firewall`, `Palo Alto`) |
| `description` | Parser description |
| `tables` | Semicolon-separated list of source tables used by the parser |
| `sub_parsers` | Semicolon-separated list of sub-parser references (for union parsers) |
| `parser_params` | Parser parameters in format `name:type=default` |
| `filter_fields` | Filter fields extracted from parser query (see Filter Fields Detection) |
| `references` | Semicolon-separated list of reference links |
| `source_file` | Relative path to the source YAML file |
| `github_url` | Full GitHub URL to the parser definition |

> **Note:** ASIM parsers are loaded from YAML files in the `/Parsers/ASim*/Parsers` directories. Union parsers aggregate multiple source parsers and typically have empty `tables` but populated `sub_parsers`. Source parsers reference actual Log Analytics tables. The `vim*` (vendor-independent model) parsers are skipped as they are wrappers around the corresponding `ASim*` parsers with identical filters.

### 10. solutions_connectors_tables_issues_and_exceptions_report.csv (Issues Report)

Contains exceptions and issues encountered during analysis.

#### Column Descriptions

| Column | Description |
|--------|-------------|
| `solution_name` | Solution name |
| `solution_folder` | GitHub URL to the solution's folder |
| `connector_id` | Connector ID (if applicable) |
| `connector_title` | Connector title (if applicable) |
| `connector_publisher` | Connector publisher (if applicable) |
| `relevant_file` | GitHub URL to the relevant file (connector or content file depending on issue type) |
| `issue_type` | Issue category (see Issue Types below) |
| `issue` | Detailed description of the issue |

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

## Azure Marketplace Availability

The script checks whether each solution is published on the Azure Marketplace using the Azure Marketplace Catalog API.

### How It Works

1. For each solution, the script constructs a legacy product ID from the `publisher_id` and `offer_id` in `SolutionMetadata.json`
2. It queries the Azure Marketplace Catalog API at `https://catalogapi.azure.com/offers/{legacy_id}`
3. If the API returns a valid response, the solution is marked as published and the marketplace URL is stored

### Caching

To avoid excessive API calls on subsequent runs, marketplace availability results are cached locally:

- **Cache Location:** `.cache/marketplace_availability.csv`
- **Cache Format:** CSV with columns `legacy_id`, `is_published`, `marketplace_url`, `last_checked`
- **Cache Behavior:** 
  - If a solution's legacy ID is found in the cache, the cached result is used (no API call)
  - New solutions not in the cache trigger API calls and are added to the cache
  - Use `--refresh-marketplace` to force refresh all entries

### Command Line Options

| Option | Description |
|--------|-------------|
| `--skip-marketplace` | Skip marketplace checking entirely (outputs will have empty `is_published` and `marketplace_url` fields) |
| `--refresh-marketplace` | Force refresh of marketplace cache, ignoring cached results and re-querying all solutions |

### Output Fields

Marketplace availability adds the following fields to the output:

| File | Field | Description |
|------|-------|-------------|
| `solutions.csv` | `is_published` | `true` if solution is on Azure Marketplace, `false` otherwise |
| `solutions.csv` | `marketplace_url` | Direct URL to the Azure Marketplace listing (empty if not published) |
| `connectors.csv` | `is_published` | `true` if parent solution is published |
| Main mapping CSV | `is_published` | `true` if parent solution is published |

> **Note:** Solutions without valid `publisher_id` and `offer_id` in `SolutionMetadata.json` cannot be checked and will have empty marketplace fields.

## Detection Logic

### Collection Method Detection

The analyzer determines the data collection method used by each connector through comprehensive content analysis. This analysis sets the `collection_method` and `collection_method_reason` columns in `connectors.csv`.

#### Collection Methods

| Method | Description | Detection Criteria |
|--------|-------------|-------------------|
| **Azure Monitor Agent (AMA)** | Modern log collection agent | Title contains "AMA" or "via AMA", ID ends with "ama", `sent_by_ama` field, "Azure Monitor Agent" in description, "CEF via AMA" or "Syslog via AMA" patterns |
| **Log Analytics Agent (MMA)** | Legacy Microsoft Monitoring Agent (deprecated) | Title mentions "Legacy Agent", "omsagent" references, "cef_installer.py" scripts, workspace ID/key patterns, `OmsSolutions` patterns, `InstallAgentOnVirtualMachine`/`InstallAgentOnNonAzure`/`InstallAgentOnLinuxNonAzure` patterns. Special case: connector ID `WindowsFirewall` (without Ama suffix) |
| **Azure Diagnostics** | Azure resource diagnostic settings | "AzureDiagnostics" references in content, "diagnostic settings" in description, `Microsoft.Insights/diagnosticSettings` resource, Azure Policy diagnostics (`policyDefinitionGuid` + `PolicyAssignment`), table category "Azure Resources" |
| **Native** | Built-in Sentinel integrations | `SentinelKinds` property present, Microsoft Defender/365/Entra ID connectors, known native connector IDs (`AzureActivity`, `AzureActiveDirectory`, `Office365`, `MicrosoftDefender`) - skipped if CCF content patterns detected |
| **Codeless Connector Framework (CCF)** | Microsoft's codeless connector platform (CCP/CCF) | `pollingConfig` present, `dcrConfig` with `RestApiPoller`, `GCPAuthConfig`, `dataConnectorDefinitions` (except AMA title connectors), ID contains "CCP"/"CCF"/"Codeless", ID contains "Polling", **CCF Push variant**: `DeployPushConnectorButton` + `HasDataConnectors` (DCR/DCE-based push ingestion) |
| **Azure Function** | Azure Functions-based data collection | Filename contains "FunctionApp"/"function_app"/"_api_function", description mentions "Azure Functions", ID contains "AzureFunction"/"FunctionApp", "Deploy to Azure" + "Function App" patterns, "Azure Function App" in content, Azure Functions pricing references |
| **REST API** | Direct API push/webhook collection | "REST API" in title/description, "push" in title/ID, webhook patterns, HTTP endpoint/trigger references |
| **Unknown (Custom Log)** | Method could not be determined | Only custom log table (`_CL`) references found, no other patterns matched |

#### Detection Priority

The detection algorithm uses a tiered priority system with 11 levels. When a connector explicitly declares its type in the title (e.g., "via AMA"), that takes precedence. Otherwise, patterns are detected in the following order:

| Priority | Detection Category | Detection Patterns |
|----------|-------------------|-------------------|
| **1** | **Explicit AMA/MMA in title** (highest) | Title contains "AMA", "via AMA", ID ends with "ama", title contains "Legacy Agent" or "via Legacy Agent". Special: `WindowsFirewall` connector is MMA. |
| **2** | **Azure Function filename** | Filename contains "FunctionApp"/"function_app"/"_api_function", ID contains "AzureFunction"/"FunctionApp" |
| **3** | **CCF content patterns** | `pollingConfig`, `dcrConfig` with `RestApiPoller`, `GCPAuthConfig`, `dataConnectorDefinitions` (unless AMA title), CCF Push (`DeployPushConnectorButton` + `HasDataConnectors`) |
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
3. Otherwise: Azure Diagnostics > CCF > Azure Function > Native > MMA > AMA > REST API > Unknown

#### CSV Fields Affected

| Field | Description |
|-------|-------------|
| `collection_method` | The detected collection method (in `connectors.csv`) |
| `collection_method_reason` | Explanation of why this method was selected |

> **Key Design Decisions:**
> - **Azure Diagnostics > CCF name**: Connectors with `_CCP` suffix that reference "AzureDiagnostics" are Azure Diagnostics (the CCP suffix indicates the connector was built using the CCF framework, but it still collects via Azure Diagnostics)
> - **CCF content > Azure Function content**: Connectors with `dcrConfig`/`dataConnectorDefinitions` that also have "Deploy Azure Function" patterns are CCF (e.g., OktaSSOv2)
> - **Azure Function filename is strong**: Connectors with "FunctionApp" in the filename are Azure Functions regardless of content patterns
> - **Title-based AMA/MMA is strongest**: When a connector title explicitly includes "AMA" or "Legacy Agent", it overrides all other patterns
> - **MMA content patterns override AMA metadata**: MMA-era patterns like `OmsSolutions` and `InstallAgent*` take precedence over AMA detection from table metadata

### Filter Fields Detection

The analyzer extracts filter field values from KQL queries to identify vendor/product-specific filtering patterns. This helps understand which data sources a connector, parser, or content item targets.

#### Supported Filter Fields

| Field | Canonical Table | Description |
|-------|----------------|-------------|
| `DeviceVendor` | CommonSecurityLog | CEF vendor identifier |
| `DeviceProduct` | CommonSecurityLog | CEF product identifier |
| `EventVendor` | Multiple (ASIM) | ASIM normalized vendor |
| `EventProduct` | Multiple (ASIM) | ASIM normalized product |
| `ResourceType` | AzureDiagnostics | Azure resource type |
| `Category` | AzureDiagnostics | Diagnostic category |
| `EventID` | WindowsEvent/SecurityEvent/Event | Windows event ID |
| `Source` | Event | Windows Event Log source |
| `Provider` | WindowsEvent | Windows event provider |
| `Facility` | Syslog | Syslog facility |
| `ProcessName` | Syslog | Syslog process name |
| `ProcessID` | Syslog | Syslog process ID |
| `SyslogMessage` | Syslog | Syslog message content |

#### Supported Operators

| Operator Category | Operators | Example |
|-------------------|-----------|---------|
| **Equality** | `==`, `=~`, `!=` | `DeviceVendor == "Fortinet"` |
| **In operators** | `in`, `in~`, `!in` | `EventID in (4624, 4625)` |
| **String operators** | `has`, `has_any`, `has_all`, `contains`, `startswith`, `endswith` | `SyslogMessage has "error"` |

> **Note:** `EventID` and `ProcessID` fields only support equality and in operators, not string operators.

#### Detection Logic

The filter field extraction follows these rules:

1. **Table-aware mapping**: When tables in the query are known, fields are mapped to their canonical tables
   - `DeviceVendor`/`DeviceProduct` → CommonSecurityLog
   - `EventVendor`/`EventProduct` → Context-dependent (ASIM tables)
   - `ResourceType`/`Category` → AzureDiagnostics
   - `EventID` → WindowsEvent, SecurityEvent, or Event (based on which is in query)
   - `Facility`/`ProcessName`/`ProcessID`/`SyslogMessage` → Syslog

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

5. **String operator patterns**: Match patterns like `field has "value"` or `field has_any ("val1", "val2")`

#### Output Format

Filter fields are formatted as a semicolon-separated list with the structure:
```
Table:Field=value1,value2;Table:Field=value3
```

Example:
```
CommonSecurityLog:DeviceVendor=Fortinet;CommonSecurityLog:DeviceProduct=FortiGate
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
| `asim_parsers.csv` | `filter_fields` | Filter fields from ASIM parser queries |

> **Note:** For ASIM parsers, `EventVendor` and `EventProduct` fields are skipped because ASIM parsers SET these values (via `extend`) rather than filter by them. The extraction focuses on source-identifying fields like `DeviceVendor`, `Facility`, etc.

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
| **Field Context Filtering** | Excludes identifiers after `\| project`, `\| extend`, `\| parse` operators |

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
