# Azure Sentinel Solutions Analyzer

This directory contains two complementary tools for analyzing Microsoft Sentinel Solutions:

1. **`solution_connector_tables.py`** - Extracts and maps data connector definitions to their ingestion tables, producing CSV reports with solution metadata
2. **`generate_connector_docs.py`** - Generates browsable markdown documentation from the CSV data with AI-rendered setup instructions

## Quick Start

**Pre-generated files are already available in this directory:**
- [`solutions_connectors_tables_mapping.csv`](solutions_connectors_tables_mapping.csv) - Main mapping of connectors to tables with full metadata
- [`solutions_connectors_tables_issues_and_exceptions_report.csv`](solutions_connectors_tables_issues_and_exceptions_report.csv) - Issues and exceptions report

You can use these files directly without running the scripts. They are kept up-to-date with the Solutions directory.

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

# 2. Connector Documentation Generator

**Script:** `generate_connector_docs.py`

## Overview

Generates browsable markdown documentation from the CSV data produced by `solution_connector_tables.py`. The documentation includes:

- Three index pages (solutions, connectors, tables)
- Individual pages for each solution with connector details
- Individual pages for each connector with usage information
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
- Pre-generated CSV file from `solution_connector_tables.py`
- No external dependencies required

## Running the Script

From the `Tools/Solutions Analyzer` directory:

```bash
python generate_connector_docs.py
```

The script reads `solutions_connectors_tables_mapping.csv` and generates all documentation in the `connector-docs/` directory.

## Output Structure

The generated documentation is organized as:

```
connector-docs/
├── README.md                    # Documentation guide
├── solutions-index.md           # Alphabetical list of all solutions
├── connectors-index.md          # Alphabetical list of all connectors
├── tables-index.md              # Alphabetical list of all tables
├── solutions/                   # Individual solution pages (477 files)
│   ├── 1password.md
│   ├── aws-cloudfront.md
│   └── ...
└── connectors/                  # Individual connector pages (503 files)
    ├── 1passwordeventreporter.md
    ├── awscloudfront.md
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
- Tables ingested by the connector
- Links to GitHub connector definition files

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

## v1.0

- Initial release with basic table detection from connector JSON files
- CSV output with solution, connector, and table mappings
- Issues and exceptions reporting
