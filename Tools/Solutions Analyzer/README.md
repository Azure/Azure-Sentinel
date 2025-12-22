# Azure Sentinel Solutions Analyzer

This directory contains three complementary tools for analyzing Microsoft Sentinel Solutions:

1. **`solution_connector_tables.py`** - Extracts and maps data connector definitions to their ingestion tables, producing CSV reports with solution metadata
2. **`collect_table_info.py`** - Collects comprehensive table metadata from Microsoft Azure Monitor documentation
3. **`generate_connector_docs.py`** - Generates browsable markdown documentation from the CSV data with AI-rendered setup instructions and enriched table information

## Quick Start

**Pre-generated files are already available in this directory:**
- [`solutions_connectors_tables_mapping.csv`](solutions_connectors_tables_mapping.csv) - Main mapping of connectors to tables with full metadata
- [`solutions_connectors_tables_issues_and_exceptions_report.csv`](solutions_connectors_tables_issues_and_exceptions_report.csv) - Issues and exceptions report
- [`tables_reference.csv`](tables_reference.csv) - Comprehensive table metadata from Azure Monitor documentation

**Connector Reference documentation in the connector-docs/ directory:**

- **[Solutions Index](connector-docs/solutions-index.md)** - All solutions organized alphabetically (with and without connectors)
- **[Connectors Index](connector-docs/connectors-index.md)** - All unique connectors with metadata
- **[Tables Index](connector-docs/tables-index.md)** - All unique tables with solution references, transformation support, and ingestion API compatibility
- **Individual Solution Pages** - Detailed pages for each solution with connector and table information (in [`solutions/`](connector-docs/solutions/) directory)
- **Individual Connector Pages** - Detailed pages for each connector with usage information (in [`connectors/`](connector-docs/connectors/) directory)
- **Individual Table Pages** - Detailed pages for each table with metadata from Azure Monitor documentation (in [`tables/`](connector-docs/tables/) directory)

You can use these files directly without running the scripts. They are kept up-to-date with the Solutions directory.

The documentation includes AI-rendered setup instructions extracted from connector UI definitions.

---

# 1. Solution Connector Tables Analyzer

**Script:** `solution_connector_tables.py`

## Overview

Scans the Solutions directory to:
- Extract table references from connector JSON files (queries, sample queries, data types)
- Resolve parser function references to actual tables
- Flatten solution metadata from SolutionMetadata.json files
- Generate a comprehensive mapping of connectors to tables with full metadata
- **Include ALL solutions in the output**, even those without data connectors (e.g., solutions containing only analytics rules, workbooks, hunting queries, or playbooks)
- Report issues and exceptions for solutions with missing or incomplete definitions

**Note:** Solutions without data connectors are included in the CSV output with empty `connector_id`, `connector_title`, `connector_description`, `connector_publisher`, `connector_files`, and `Table` fields. This ensures complete solution coverage in the documentation while clearly indicating which solutions do not include data ingestion components.

**Important:** This analysis covers connectors managed through Solutions in the Azure-Sentinel GitHub repository. A small number of connectors (such as Microsoft Dataverse, Microsoft Power Automate, Microsoft Power Platform Admin, and SAP connectors) are not managed via Solutions and are therefore not included in this output.

## Prerequisites

- Python 3.7 or higher
- No external dependencies required (optional: json5 for enhanced JSON parsing)

### Optional Dependencies
```bash
pip install json5  # For improved JSON parsing with comments and trailing commas
```

## Running the Script

From the `Tools/Solutions Analyzer` directory:
```bash
python solution_connector_tables.py
```

Or from anywhere in the repository:
```bash
python "Tools/Solutions Analyzer/solution_connector_tables.py" --solutions-dir Solutions
```

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--solutions-dir` | `../../Solutions` | Path to the Solutions directory |
| `--output` | `solutions_connectors_tables_mapping.csv` | Path for the main output CSV file |
| `--report` | `solutions_connectors_tables_issues_and_exceptions_report.csv` | Path for the issues report CSV file |
| `--show-detection-methods` | `False` | Include table_detection_methods column showing how each table was detected |

### Example Usage
```bash
# Run with default settings
python solution_connector_tables.py

# Show detection methods in output
python solution_connector_tables.py --show-detection-methods

# Custom output location
python solution_connector_tables.py --output custom_output.csv --report custom_report.csv
```

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

### 2. solutions_connectors_tables_issues_and_exceptions_report.csv (Issues Report)

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

### Table Detection Methods

The analyzer uses multiple strategies to identify tables, tracked in the `table_detection_methods` column (when enabled):

1. **graphQueries.{index}.baseQuery** - From connector graphQueries
2. **sampleQueries.{index}.query** - From connector sampleQueries  
3. **dataTypes.{index}.lastDataReceivedQuery** - From dataTypes definitions
4. **connectivityCriterias.{index}.value.{sub_index}** - From connectivity criteria queries
5. **logAnalyticsTableId** - Extracted from ARM template variables
6. **parser:{parser_name}** - Resolved from parser function to actual table

### Parser Resolution

When a connector references a parser function (e.g., `ASimDns`):
1. Script locates the parser YAML file in the solution's Parsers directory
2. Extracts the FunctionQuery from the parser
3. Analyzes the query to find actual table references (e.g., `Syslog`, `DnsEvents`)
4. Maps the parser name to the discovered tables
5. Replaces parser reference with actual tables in the output

### Context-Aware Table Detection

The analyzer uses intelligent query parsing to distinguish actual table names from field names:

- **Pipeline Head Detection**: Identifies tables that appear before pipe operators (e.g., `Syslog | where...`)
- **Field Context Filtering**: Excludes identifiers that appear in field-generating contexts (after `| project`, `| extend`, `| parse`)
- **Multi-line Statement Tracking**: Handles complex multi-line queries with proper context awareness
- **Comment Stripping**: Removes KQL comments before analysis to avoid false detections

---

# 2. Table Reference Collector

**Script:** `collect_table_info.py`

## Overview

Collects comprehensive table metadata from Microsoft Azure Monitor documentation sources:

- Azure Monitor Logs table reference
- Microsoft Defender XDR schema reference
- Table feature support information
- Ingestion API compatibility

The collected data enriches the connector documentation with detailed table information including transformation support, basic logs eligibility, and documentation links.

## Prerequisites

- Python 3.7 or higher
- `requests` library for HTTP fetching

```bash
pip install requests
```

## Running the Script

From the `Tools/Solutions Analyzer` directory:

```bash
# Basic run (main pages only)
python collect_table_info.py

# Full run with individual table details
python collect_table_info.py --fetch-details
```

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--output` | `tables_reference.csv` | Path for the output CSV file |
| `--report` | `tables_reference_report.md` | Path for the summary report |
| `--fetch-details` | `False` | Fetch additional details from individual table pages |
| `--max-details` | None | Maximum number of table detail pages to fetch (for testing) |
| `--cache-ttl` | `604800` | Cache time-to-live in seconds (default: 1 week) |
| `--clear-cache` | `False` | Clear all cached files before running |

## Output Files

### tables_reference.csv

Comprehensive CSV with table metadata:

| Column | Description |
|--------|-------------|
| `table_name` | Table name |
| `description` | Table description from documentation |
| `category` | Table category (e.g., Security, Audit, Azure Resources) |
| `solutions` | Associated Log Analytics solutions |
| `resource_types` | Azure resource types that emit to this table |
| `table_type` | Type classification |
| `source_azure_monitor` | Whether table is in Azure Monitor reference |
| `source_defender_xdr` | Whether table is in Defender XDR schema |
| `source_feature_support` | Whether table has feature support info |
| `source_ingestion_api` | Whether table supports ingestion API |
| `azure_monitor_doc_link` | Link to Azure Monitor documentation |
| `defender_xdr_doc_link` | Link to Defender XDR documentation |
| `basic_logs_eligible` | Whether table supports Basic Logs plan |
| `auxiliary_table_eligible` | Whether table can be auxiliary |
| `supports_transformations` | Whether ingestion-time transformations are supported |
| `search_job_support` | Whether search jobs are supported |
| `ingestion_api_supported` | Whether Data Collector API ingestion is supported |
| `retention_default` | Default retention period |
| `retention_max` | Maximum retention period |
| `plan` | Log Analytics plan (Analytics, Basic, etc.) |

### Caching

The script uses file-based caching to minimize network requests:

- Cache files stored in `.cache/` directory
- Default TTL of 1 week (604800 seconds)
- MD5 hash of URL used as cache key
- Use `--clear-cache` to force fresh fetches

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
python solution_connector_tables.py --show-detection-methods
```

This will include the `table_detection_methods` column showing exactly how each table was detected.

---

# 3. Connector Documentation Generator

**Script:** `generate_connector_docs.py`

## Overview

Generates browsable markdown documentation from the CSV data produced by `solution_connector_tables.py` and `collect_table_info.py`. The documentation includes:

- Three index pages (solutions, connectors, tables)
- Individual pages for each solution with connector details
- Individual pages for each connector with table transformation and ingestion API support information
- Individual pages for ALL tables with enriched metadata from Azure Monitor documentation
- **AI-rendered setup instructions** extracted from connector UI definitions

## Output

The script generates the **Microsoft Sentinel Data Connector Reference** documentation in the `connector-docs/` directory:

- **[Solutions Index](connector-docs/solutions-index.md)** - All solutions organized alphabetically (with and without connectors)
- **[Connectors Index](connector-docs/connectors-index.md)** - All unique connectors with metadata
- **[Tables Index](connector-docs/tables-index.md)** - All unique tables with solution references
- **Individual Solution Pages** - Detailed pages for each solution with connector and table information (in [`solutions/`](connector-docs/solutions/) directory)
- **Individual Connector Pages** - Detailed pages for each connector with usage information (in [`connectors/`](connector-docs/connectors/) directory)

See the [connector-docs README](connector-docs/README.md) for full documentation.

## Prerequisites

- Python 3.7 or higher
- Input CSV files (automatically generated if not present):
  - `solutions_connectors_tables_mapping.csv` from `solution_connector_tables.py`
  - `tables_reference.csv` from `collect_table_info.py`

## Running the Script

From the `Tools/Solutions Analyzer` directory:

```bash
# Full run (automatically generates input CSVs first)
python generate_connector_docs.py

# Skip input generation (use existing CSV files)
python generate_connector_docs.py --skip-input-generation
```

The script automatically calls `compare_connector_catalogs.py` and `collect_table_info.py --fetch-details` before generating documentation, unless `--skip-input-generation` is specified.

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--input` | `solutions_connectors_tables_mapping.csv` | Path to connector mapping CSV |
| `--tables-csv` | `tables_reference.csv` | Path to tables reference CSV |
| `--output-dir` | `connector-docs/` | Output directory for documentation |
| `--solutions` | All | Generate docs only for specific solutions |
| `--skip-input-generation` | `False` | Skip running input CSV generation scripts |

## Output Structure

The generated documentation is organized as:

```
connector-docs/
├── README.md                    # Documentation guide
├── solutions-index.md           # Alphabetical list of all solutions
├── connectors-index.md          # Alphabetical list of all connectors
├── tables-index.md              # Alphabetical list of all tables with transformation/API support
├── solutions/                   # Individual solution pages (~480 files)
│   ├── 1password.md
│   ├── aws-cloudfront.md
│   └── ...
├── connectors/                  # Individual connector pages (~520 files)
│   ├── 1passwordeventreporter.md
│   ├── awscloudfront.md
│   └── ...
└── tables/                      # Individual table pages (~825 files)
    ├── securityevent.md
    ├── syslog.md
    └── ...
```

### Generated Content

**Solution Pages** include:
- Solution metadata (publisher, support, categories)
- List of connectors in the solution
- Setup instructions for each connector (AI-rendered)
- Required permissions and prerequisites
- Tables ingested by each connector
- Links to connector definition files

**Connector Pages** include:
- Connector description and metadata
- **AI-rendered setup instructions and permissions** from connector UI definitions with step-by-step guidance
- Required permissions and prerequisites (rendered from Microsoft Sentinel permissions schema)
- List of solutions using this connector
- Tables ingested with transformation and ingestion API support indicators
- Links to GitHub connector definition files

**Table Pages** include:
- Table description from Azure Monitor documentation
- Category and resource types
- Basic Logs eligibility
- Transformation support status
- Ingestion API compatibility
- Search job support
- Retention information
- Links to Azure Monitor and Defender XDR documentation
- List of solutions and connectors using the table

**Index Pages** provide:
- Alphabetical navigation
- Quick statistics
- Cross-references between solutions, connectors, and tables

## AI-Rendered Setup Instructions and Permissions

The "Setup Instructions" and "Permissions" sections in the generated connector documentation are **automatically rendered from connector UI definition files**. These sections interpret the UI-centric JSON structures that define the Azure Portal configuration interface and convert them into readable documentation.

### ⚠️ Important Disclaimer

**These AI-rendered instructions and permissions may not be fully accurate.** They are generated by interpreting UI definition metadata and should always be verified against the actual Microsoft Sentinel portal before implementation. The content provides a helpful starting point but is not a substitute for official documentation or hands-on portal verification.

### How It Works

The rendering process involves several steps:

1. **JSON Parsing**: The script extracts `instructionSteps` and `permissions` objects from connector definition files in the Solutions directory
2. **UI Type Detection**: Each instruction step has a `type` property (e.g., `DataConnectorsGrid`, `ContextPane`, `GCPGrid`) that determines how it should be interpreted
3. **Permissions Schema Parsing**: Permission objects are rendered according to the Microsoft Sentinel permissions schema, including:
   - **resourceProvider**: Azure resource provider permissions with scope, required actions (read/write/delete/action)
   - **customs**: Custom prerequisites with names and descriptions
   - **licenses**: Required Microsoft 365 licenses with friendly names
   - **tenant**: Azure AD tenant permissions with required roles
4. **AI-Powered Rendering**: Specialized handlers for each UI type convert the JSON structure into descriptive markdown:
   - Form fields (textboxes, dropdowns) are described with their purposes and validation requirements
   - Management grids and data selectors are explained with their configuration options
   - Portal-only interfaces are identified and marked with clear indicators
   - Permission requirements are formatted with clear scope and action descriptions
5. **Markdown Formatting**: The rendered content is formatted with emoji indicators, step numbers, and disclaimers

### UI Types Supported

The script includes specialized handlers for connector UI configuration types based on the [official Microsoft Sentinel data connector UI definitions reference](https://learn.microsoft.com/en-us/azure/sentinel/data-connector-ui-definitions-reference#instructionsteps):

**Standard Instruction Types:**

- **OAuthForm**: OAuth authentication forms with client credentials
- **Textbox**: Input fields for text, passwords, numbers, and email addresses
- **Dropdown**: Selection lists with single or multi-select options
- **Markdown**: Formatted text content with links and formatting
- **CopyableLabel**: Text fields with copy-to-clipboard functionality
- **InfoMessage**: Inline information messages with contextual help
- **ConnectionToggleButton**: Connect/disconnect toggle controls
- **InstructionStepsGroup**: Collapsible groups of nested instructions
- **InstallAgent**: Links to Azure portal sections for agent installation (18 link types supported)

**UI-Centric Configuration Types:**

- **DataConnectorsGrid**: Interactive data connector management interface with enable/disable controls
- **ContextPane**: Sidebar configuration panels with detailed settings
- **GCPGrid** / **GCPContextPane**: Google Cloud Platform specific configuration interfaces
- **AADDataTypes**: Azure Active Directory data type selectors
- **MCasDataTypes**: Microsoft Defender for Cloud Apps data type selectors  
- **OfficeDataTypes**: Microsoft 365 data type selectors

Instructions for 74 connectors using these UI-centric configuration interfaces have been enhanced with AI-rendered setup guidance.

### Example Output

Instructions are formatted with:

- 📋 Portal-only interfaces clearly marked
- 📝 Form fields with descriptions and placeholders
- ⚠️ Disclaimers about AI generation and accuracy
- 🔗 Links to GitHub connector definition files

---

## Version History

### v4.0

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
- Added `compare_connector_catalogs.py` script to compare GitHub connectors with Sentinel catalog
- Added `collect_table_info.py` script to collect comprehensive table metadata from Azure Monitor documentation
  - Fetches from Azure Monitor Logs reference, Defender XDR schema, feature support, and ingestion API pages
  - Includes transformation support, basic logs eligibility, retention info, and documentation links
  - Uses file-based caching with configurable TTL (default: 1 week)
- Enhanced `generate_connector_docs.py` with table reference integration:
  - Now automatically calls input generation scripts before documentation generation
  - Added `--tables-csv` argument for tables reference CSV path
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
