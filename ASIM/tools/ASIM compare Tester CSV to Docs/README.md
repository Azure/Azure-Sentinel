# ASIM Schema Comparison Tool

A Python tool to compare Azure Sentinel Information Model (ASIM) CSV field definitions with the official Microsoft documentation.

## Overview

This tool helps maintain consistency between the ASIM tester CSV file (which defines field schemas) and the official Microsoft documentation. It identifies:

- **Fields missing in documentation** - Fields defined in CSV but not in docs
- **Fields missing in CSV** - Fields documented but not in CSV
- **Type mismatches** - Fields with different types between CSV and docs
- **Class mismatches** - Fields with different class (Mandatory/Recommended/Optional/Alias) between CSV and docs

## Installation

### Requirements

- Python 3.8 or higher
- `requests` library (for web URL support)

### Setup

```bash
# Clone or navigate to the tool directory
cd asim-comparison-tool

# Install dependencies
pip install requests
```

## Usage

### Basic Usage (Web Sources)

By default, the tool fetches data from web sources:

```bash
python compare_asim.py
```

This uses:
- **CSV**: https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/ASIM/dev/ASimTester/ASimTester.csv
- **Docs**: https://learn.microsoft.com/en-us/azure/sentinel/normalization-about-schemas (fetches raw markdown from GitHub)

The script displays the Learn URLs for reference but fetches the raw markdown content from GitHub for parsing.

### Using Local Files

```bash
python compare_asim.py --csv ./ASimTester.csv --docs ../articles/sentinel
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--csv` | Path or URL to the ASIM CSV file | Azure Sentinel GitHub URL |
| `--docs` | Path to docs folder or URL to docs | Microsoft Learn URL |
| `--output` | Output directory for reports | Current directory |
| `--schema` | Specific schema to compare (e.g., `NetworkSession`) | All schemas |
| `--quiet`, `-q` | Suppress verbose output | False |
| `--refresh-cache` | Clear cache and fetch fresh content (repopulates cache) | False |
| `--skip-cache` | Skip cache for this run only (leaves existing cache intact) | False |
| `--cache-ttl` | Cache time-to-live in seconds | 3600 (1 hour) |
| `--cache-dir` | Directory for cache files | `.cache` |

### Examples

```bash
# Compare only the NetworkSession schema
python compare_asim.py --schema NetworkSession

# Use local files and output to a specific directory
python compare_asim.py --csv ./ASimTester.csv --docs ../articles/sentinel --output ./reports

# Quiet mode
python compare_asim.py -q

# Refresh cache (clear and re-fetch all content)
python compare_asim.py --refresh-cache

# Skip cache for this run only
python compare_asim.py --skip-cache

# Set cache TTL to 1 day (86400 seconds)
python compare_asim.py --cache-ttl 86400
```

## Output Files

The tool generates three output files:

### 1. ASIM-Comparison-Detailed-Report.md

A comprehensive markdown report containing:
- Executive summary with total counts
- Schema-by-schema analysis
- Detailed lists of issues and warnings

### 2. comparison-report-all-issues.csv

CSV file with all identified issues:

| Column | Description |
|--------|-------------|
| Schema | Schema name |
| Field | Field name |
| IssueType | Error or Warning |
| IssueCategory | Category of the issue |
| IssueDescription | Human-readable description |
| CsvType | Type in CSV |
| CsvLogicalType | Logical type in CSV |
| CsvEffectiveType | Effective type (logical or physical) |
| DocType | Type in documentation |
| CsvClass | Class in CSV |
| DocClass | Class in documentation |

### 3. comparison-report-all-fields.csv

CSV file with all fields from both sources:

| Column | Description |
|--------|-------------|
| Schema | Schema name |
| Field | Field name |
| InDoc | Yes/No - Is field in documentation |
| InCsv | Yes/No - Is field in CSV |
| DocClass | Class from documentation |
| CsvClass | Class from CSV |
| DocType | Type from documentation |
| CsvType | Type from CSV |
| CsvLogicalType | Logical type from CSV |
| DocSource | Source of doc field (SchemaDoc, CommonFields, etc.) |
| Description | Parsed field description (cleaned, without examples/notes) |
| Example | Extracted example value(s) from documentation |
| Note | Extracted note text from documentation |
| OriginalDescription | Raw description text before parsing (for verification) |

## Caching

The tool caches fetched web content to improve performance on repeated runs.

### Cache Behavior

- **Location**: Cache files are stored in the `.cache` directory by default
- **TTL**: Cached files expire after 1 hour (3600 seconds) by default
- **Format**: Each cached URL creates two files:
  - `filename_hash.cache` - The cached content
  - `filename_hash.meta` - Metadata (URL, timestamp, size)

### Cache Management

```bash
# Refresh cache - clear and re-fetch all content (repopulates for future runs)
python compare_asim.py --refresh-cache

# Skip cache for this run only (leaves existing cache files intact)
python compare_asim.py --skip-cache

# Set cache TTL to 24 hours
python compare_asim.py --cache-ttl 86400

# Use a custom cache directory
python compare_asim.py --cache-dir /tmp/asim-cache
```

### When to Clear Cache

- After documentation updates on Microsoft Learn
- When debugging parsing issues
- When you need the latest content

## Understanding Results

### Issue Types

- **Error**: Real discrepancy that needs attention
- **Warning**: Known limitation or expected pattern

### Warning Categories

| Category | Description |
|----------|-------------|
| SpecificIDsDocumentedCentrally | User ID fields (e.g., `*UserAadId`, `*UserSid`) are documented centrally |
| LogicalTypeNotInDocs | CSV has logical type but docs show physical type |
| ComplexAliasNotSupported | Field is Alias in docs but ASIM tester doesn't support complex aliases |
| ConditionalNotSupported | Field is Conditional in docs but ASIM tester doesn't support this |
| EnumerationNotSupported | Doc shows Enumerated but CSV has simple type (ASIM tester limitation) |

### Schema Inheritance

The tool handles special cases:

- **WebSession**: Inherits fields from NetworkSession schema
  - `DstDomain` class is changed to Optional
  - `NetworkRuleName` is renamed to `RuleName`
  - `NetworkRuleNumber` is renamed to `RuleNumber`

## Supported Schemas

| Schema | Documentation File |
|--------|-------------------|
| AlertEvent | normalization-schema-alert.md |
| AuditEvent | normalization-schema-audit.md |
| Authentication | normalization-schema-authentication.md |
| Common | normalization-common-fields.md |
| DhcpEvent | normalization-schema-dhcp.md |
| Dns | normalization-schema-dns.md |
| FileEvent | normalization-schema-file-event.md |
| NetworkSession | normalization-schema-network.md |
| ProcessEvent | normalization-schema-process-event.md |
| RegistryEvent | normalization-schema-registry-event.md |
| UserManagement | normalization-schema-user-management.md |
| WebSession | normalization-schema-web.md |

## Architecture

The tool consists of the following key components:

### Data Structures

- `FieldInfo`: Information about a field (class, type, source, description, example, note)
- `IssueInfo`: Information about an issue (type, category, description)
- `ComparisonResult`: Results from comparing a single schema

### Key Functions

1. **Caching**
   - `get_cache_path()`: Generate cache file path for a URL
   - `is_cache_valid()`: Check if cache exists and is not expired
   - `read_from_cache()`: Read cached content
   - `write_to_cache()`: Write content to cache with metadata
   - `clear_cache()`: Remove all cached files

2. **Data Fetching**
   - `fetch_content()`: Fetch from local file or URL (with caching)
   - `fetch_csv_data()`: Parse CSV data
   - `parse_common_fields()`: Parse common fields documentation
   - `get_network_session_fields()`: Get NetworkSession fields for WebSession

3. **Parsing**
   - `parse_doc_fields()`: Extract field definitions from markdown tables
   - `parse_description_field()`: Extract description, example, and note from raw text

4. **Comparison**
   - `compare_schema()`: Compare a single schema
   - `get_missing_field_issue_type()`: Categorize missing field issues
   - `get_type_mismatch_issue_type()`: Categorize type mismatch issues
   - `get_class_mismatch_issue_type()`: Categorize class mismatch issues

5. **Reporting**
   - `generate_markdown_report()`: Generate the markdown report
   - `generate_issues_csv()`: Generate issues CSV
   - `generate_all_fields_csv()`: Generate all fields CSV

## Troubleshooting

### Common Issues

**"The 'requests' library is required for web URLs"**
```bash
pip install requests
```

**"Documentation file not found"**
- Check that the docs path is correct
- For web sources, ensure you have internet connectivity
- The tool expects markdown files in the standard Microsoft Docs structure

**No fields found in a schema**
- Check that the CSV contains fields for that schema
- Verify the schema name matches exactly (case-sensitive)

## Contributing

When modifying this tool:

1. Test with both local files and web URLs
2. Verify output matches expected results
3. Update this README if adding new features

## License

This tool is provided as-is for internal documentation maintenance.
