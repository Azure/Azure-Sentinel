# Azure Sentinel Solutions Analyzer

This tool analyzes Azure Sentinel Solutions to extract and map data connector definitions to their ingestion tables, producing comprehensive CSV reports for solution metadata analysis.

## Quick Start

**Pre-generated CSV files and documentation are already available in this directory:**
- `solutions_connectors_tables_mapping.csv` - Main mapping of connectors to tables with full metadata
- `solutions_connectors_tables_issues_and_exceptions_report.csv` - Issues and exceptions report
- [`connector-docs/`](connector-docs/) - [Microsoft Sentinel Data Connector Reference](connector-docs/README.md) with browsable indexes by solutions, connectors, and tables

You can use these files directly without running the script. They are kept up-to-date with the Solutions directory.

To regenerate the files with the latest data:
```bash
python solution_connector_tables.py
```

To regenerate the markdown documentation:
```bash
python generate_connector_docs.py
```

## Overview

The analyzer scans the Solutions directory to:
- Extract table references from connector JSON files (queries, sample queries, data types)
- Resolve parser function references to actual tables
- Flatten solution metadata from SolutionMetadata.json files
- Generate a comprehensive mapping of connectors to tables with full metadata
- **Include ALL solutions in the output**, even those without data connectors (e.g., solutions containing only analytics rules, workbooks, hunting queries, or playbooks)
- Report issues and exceptions for solutions with missing or incomplete definitions

**Note:** Solutions without data connectors are included in the CSV output with empty `connector_id`, `connector_title`, `connector_description`, `connector_publisher`, `connector_files`, and `Table` fields. This ensures complete solution coverage in the documentation while clearly indicating which solutions do not include data ingestion components.

## Installation and Requirements

### Prerequisites
- Python 3.7 or higher
- No external dependencies required (optional: json5 for enhanced JSON parsing)

### Optional Dependencies
```bash
pip install json5  # For improved JSON parsing with comments and trailing commas
```

### Running the Script
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

### 1. Microsoft Sentinel Data Connector Reference (connector-docs/)

Browsable markdown documentation generated from the CSV data, providing:

- **[Solutions Index](connector-docs/solutions-index.md)** - All solutions organized alphabetically (with and without connectors)
- **[Connectors Index](connector-docs/connectors-index.md)** - All unique connectors with metadata
- **[Tables Index](connector-docs/tables-index.md)** - All unique tables with solution references
- **Individual Solution Pages** - Detailed pages for each solution with connector and table information (in `solutions/` directory)
- **Individual Connector Pages** - Detailed pages for each connector with usage information (in `connectors/` directory)

See the [connector-docs README](connector-docs/README.md) for full documentation.

### 2. solutions_connectors_tables_mapping.csv (Primary Output)

The main CSV file containing one row per unique combination of solution, connector, and table.

**Note:** Newlines in the `connector_description` field are replaced with `<br>` tags to ensure proper rendering in GitHub's CSV viewer while preserving formatting information.

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

### 3. solutions_connectors_tables_issues_and_exceptions_report.csv (Issues Report)

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

**Note:** `parser_tables_resolved` entries are automatically filtered from the report as they represent successful parser-to-table resolution.

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

## Updating the Script

The script is located at:
```
Tools/Solutions Analyzer/solution_connector_tables.py
```

After modifications, test with:
```bash
cd "Tools/Solutions Analyzer"
python solution_connector_tables.py
```

## Contributing

When adding new detection methods or modifying the logic:
1. Update the `table_detection_methods` tracking in `record_table()` function
2. Test with `--show-detection-methods` flag to verify detection sources
3. Update this README with new detection methods or column descriptions
4. Validate output doesn't introduce false positives (field names detected as tables)

## Version History

- **v1.0** - Initial release with basic table detection
- **v2.0** - Added parser resolution, context-aware detection, enhanced JSON parsing, flattened metadata, GitHub URLs
