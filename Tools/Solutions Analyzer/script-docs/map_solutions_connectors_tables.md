# Solution Connector Tables Analyzer

**Script:** `map_solutions_connectors_tables.py`

## Overview

Scans the Solutions directory to:
- Extract table references from connector JSON files (queries, sample queries, data types)
- **Extract table references from content items** (analytics rules, hunting queries, playbooks, workbooks, watchlists, summary rules)
- Resolve parser function references to actual tables
- Flatten solution metadata from SolutionMetadata.json files
- Generate a comprehensive mapping of connectors to tables with full metadata
- **Include ALL solutions in the output**, even those without data connectors (e.g., solutions containing only analytics rules, workbooks, hunting queries, or playbooks)
- Report issues and exceptions for solutions with missing or incomplete definitions

### Content Item Analysis

The script analyzes KQL queries in solution content items to extract table references:

| Content Type | File Patterns | Query Fields |
|--------------|---------------|--------------|
| **Analytics Rules** | `Analytic Rules/*.yaml`, `Detections/*.yaml` | `query`, `triggerOperator` |
| **Hunting Queries** | `Hunting Queries/*.yaml` | `query` |
| **Playbooks** | `Playbooks/**/*.json` | Azure Monitor Logs query actions |
| **Workbooks** | `Workbooks/*.json` | `query` fields in workbook steps |
| **Watchlists** | `Watchlists/*.json` | Table references in watchlist queries |
| **Summary Rules** | `Summary Rules/*.json` | Query fields |

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
| `--content-tables-mapping-csv` | `content_tables_mapping.csv` | Path for the content-to-tables mapping CSV file |
| `--tables-reference-csv` | `tables_reference.csv` | Path to tables_reference.csv for table metadata |
| `--mapping-csv` | `solutions_connectors_tables_mapping_simplified.csv` | Path for the simplified mapping CSV file |
| `--overrides-csv` | `solution_analyzer_overrides.csv` | Path to overrides CSV file for field value overrides |
| `--show-detection-methods` | `False` | Include table_detection_methods column showing how each table was detected |

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
| `collection_method` | Data collection method (see Collection Method Detection below) |
| `collection_method_reason` | Explanation of how collection method was determined |

### 3. solutions.csv (Solution Details)

Contains one row per solution with all solution-specific metadata.

| Column | Description |
|--------|-------------|
| `solution_name` | Solution folder name |
| `solution_folder` | GitHub URL to the solution's folder |
| `solution_publisher_id` | Publisher ID from SolutionMetadata.json |
| `solution_offer_id` | Offer ID from SolutionMetadata.json |
| `solution_first_publish_date` | First publication date |
| `solution_last_publish_date` | Last update date |
| `solution_version` | Solution version number |
| `solution_support_name` | Support provider name |
| `solution_support_tier` | Support tier |
| `solution_support_link` | Support link URL |
| `solution_author_name` | Author name from metadata |
| `solution_categories` | Comma-separated list of solution categories |
| `has_connectors` | `true` if solution has data connectors, `false` otherwise |

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

### 6. content_tables_mapping.csv (Content Item to Table Mapping)

Contains one row per unique combination of solution, content item, and table. This maps tables found in KQL queries within analytics rules, hunting queries, playbooks, workbooks, watchlists, and summary rules.

| Column | Description |
|--------|-------------|
| `solution_name` | Solution folder name |
| `content_type` | Type of content item: `AnalyticsRule`, `HuntingQuery`, `Playbook`, `Workbook`, `Watchlist`, `SummaryRule` |
| `content_name` | Name or filename of the content item |
| `table_name` | Table name extracted from the KQL query |
| `table_usage` | Usage indicator for playbooks: `read`, `write`, or `read/write`. Empty for other content types (assumed read). |

> **Note:** For playbooks, `table_usage` tracks whether the playbook reads from a table (Azure Monitor query), writes to it (Send Data action), or both. Other content types are assumed to only read from tables.

### 7. solutions_connectors_tables_issues_and_exceptions_report.csv (Issues Report)

Contains exceptions and issues encountered during analysis.

#### Column Descriptions

| Column | Description |
|--------|-------------|
| `solution_name` | Solution name |
| `solution_folder` | GitHub URL to the solution's folder |
| `connector_id` | Connector ID (if applicable) |
| `connector_title` | Connector title (if applicable) |
| `connector_publisher` | Connector publisher (if applicable) |
| `connector_file` | GitHub URL to the connector file |
| `reason` | Issue category (see Issue Types below) |
| `details` | Detailed description of the issue |

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

## Detection Logic

### Collection Method Detection

The analyzer determines the data collection method used by each connector through comprehensive content analysis. Collection methods are classified as:

| Method | Description | Detection Criteria |
|--------|-------------|-------------------|
| **Azure Monitor Agent (AMA)** | Modern log collection agent | Title contains "AMA" or "via AMA", ID ends with "ama", Azure Monitor Agent deployment references, `sent_by_ama` field |
| **Log Analytics Agent (MMA)** | Legacy Microsoft Monitoring Agent (deprecated) | Title mentions "Legacy Agent", "omsagent" references, "cef_installer.py" scripts, workspace ID/key patterns |
| **Azure Diagnostics** | Azure resource diagnostic settings | "AzureDiagnostics" references in content, "diagnostic settings" in description, `Microsoft.Insights/diagnosticSettings` resource, Azure Policy diagnostics, table category "Azure Resources" |
| **Native** | Built-in Sentinel integrations | `SentinelKinds` property present, Microsoft 365/Defender/Entra ID native integrations, known native connector IDs (only when CCF patterns not present) |
| **Codeless Connector Framework (CCF)** | Microsoft's codeless connector platform (CCP/CCF) | `pollingConfig` present, `dcrConfig` with `RestApiPoller`, `GCPAuthConfig`, `dataConnectorDefinitions` (except AMA title connectors), ID contains "CCP"/"CCF"/"Codeless", **CCF Push variant**: `DeployPushConnectorButton` with `HasDataConnectors` (DCR/DCE-based push ingestion) |
| **Azure Function** | Azure Functions-based data collection | Filename contains "FunctionApp"/"function_app"/"_api_function", description mentions "Azure Functions", ID contains "AzureFunction"/"FunctionApp", function app deployment patterns |
| **REST API** | Direct API push/webhook collection | "REST API" in title/description, webhook/HTTP endpoint patterns, "Push" in connector title |
| **Unknown (Custom Log)** | Method could not be determined | Only custom log table (`_CL`) references found, no other patterns matched |

### Detection Priority

The detection algorithm uses a tiered priority system to ensure accurate classification. When a connector explicitly declares its type in the title (e.g., "via AMA"), that takes precedence. Otherwise, the most specific detection patterns are prioritized over generic ones:

1. **Explicit AMA/MMA in title** (highest priority) - Title/ID explicitly states the agent type (e.g., "via AMA", "via Legacy Agent", ID ends with "ama"). Special case: `WindowsFirewall` (without Ama suffix) is treated as MMA.
2. **Azure Function filename patterns** - Filename contains "FunctionApp"/"function_app"/"_api_function", ID contains "AzureFunction"/"FunctionApp"
3. **CCF content patterns** - `pollingConfig`, `dcrConfig` with RestApiPoller, `GCPAuthConfig`, `dataConnectorDefinitions` (unless AMA title), CCF Push variant (`DeployPushConnectorButton` + `HasDataConnectors`)
4. **Azure Diagnostics patterns** - References to "AzureDiagnostics" table, "diagnostic settings" in description, `Microsoft.Insights/diagnosticSettings` resource, Azure Policy diagnostics (skipped if Azure Function filename detected)
5. **CCF name-based patterns** (lower than Azure Diagnostics) - ID contains "CCP"/"CCF"/"Codeless", ID contains "Polling" (skipped if Azure Diagnostics patterns found)
6. **Azure Function content patterns** (lower than CCF content) - "Azure Functions" in description, "Deploy to Azure" with "Function App", Azure Functions pricing references (skipped if CCF content detected)
7. **Native Microsoft integrations** - `SentinelKinds` property, Microsoft Defender/365/Entra ID connectors (skipped if CCF content detected)
8. **Additional AMA/MMA patterns** - Secondary indicators like `sent_by_ama`, `omsagent`, workspace keys
9. **REST API patterns** - Push/webhook/HTTP endpoint references
10. **Table metadata fallback** - Uses table category from Azure Monitor reference (e.g., "Azure Resources" → Azure Diagnostics, "virtualmachines" in resource_types → AMA) - only applied when no Azure Function, CCF, Native, or Azure Diagnostics patterns detected
11. **Custom log fallback** (lowest priority) - `_CL` table suffix indicates custom log

> **Key Design Decisions:**
> - **Azure Diagnostics > CCF name**: Connectors with `_CCP` suffix that reference "AzureDiagnostics" are Azure Diagnostics (the CCP suffix indicates the connector was built using the CCF framework, but it still collects via Azure Diagnostics)
> - **CCF content > Azure Function content**: Connectors with `dcrConfig`/`dataConnectorDefinitions` that also have "Deploy Azure Function" patterns are CCF (e.g., OktaSSOv2)
> - **Azure Function filename is strong**: Connectors with "FunctionApp" in the filename are Azure Functions regardless of content patterns
> - **Title-based AMA/MMA is strongest**: When a connector title explicitly includes "AMA" or "Legacy Agent", it overrides all other patterns

> **Note:** When multiple patterns match, the system selects based on priority order.

### Parser Resolution

When a connector references a parser function (e.g., `ASimDns`):
1. Script locates the parser YAML file in the solution's Parsers directory
2. Extracts the FunctionQuery from the parser
3. Analyzes the query to find actual table references (e.g., `Syslog`, `DnsEvents`)
4. Maps the parser name to the discovered tables
5. Replaces parser reference with actual tables in the output

### Table Detection Methods

The analyzer uses multiple strategies to identify tables, tracked in the `table_detection_methods` column (when enabled):

1. **graphQueries.{index}.baseQuery** - From connector graphQueries
2. **sampleQueries.{index}.query** - From connector sampleQueries  
3. **dataTypes.{index}.lastDataReceivedQuery** - From dataTypes definitions
4. **connectivityCriterias.{index}.value.{sub_index}** - From connectivity criteria queries
5. **logAnalyticsTableId** - Extracted from ARM template variables
6. **parser:{parser_name}** - Resolved from parser function to actual table

### Context-Aware Table Detection

The analyzer uses intelligent query parsing to distinguish actual table names from field names:

- **Pipeline Head Detection**: Identifies tables that appear before pipe operators (e.g., `Syslog | where...`)
- **Field Context Filtering**: Excludes identifiers that appear in field-generating contexts (after `| project`, `| extend`, `| parse`)
- **Multi-line Statement Tracking**: Handles complex multi-line queries with proper context awareness
- **Comment Stripping**: Removes KQL comments before analysis to avoid false detections

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
