# Kusto Uploader

**Script:** `upload_to_kusto.py`

## Overview

Uploads CSV files to Azure Data Explorer (Kusto) clusters. The script drops existing tables and re-uploads CSV data using queued ingestion.

Two modes of operation:
- **Custom CSV Upload**: Upload any CSV file(s) specified on the command line
- **Solution Analyzer Integration**: Download and upload Solution Analyzer CSVs directly from the public Azure-Sentinel GitHub repository

The script automatically detects CSV schema (column names) and creates tables with matching structure. All columns are created as `string` type.

## Prerequisites

- Python 3.7 or higher
- **Azure CLI** - Must be installed and logged in (`az login`)
- Required Python packages:

```bash
pip install azure-kusto-data azure-kusto-ingest azure-identity requests
```

> **Note:** The `requests` package is only required for the `--solution-analyzer` mode.

## Running the Script

From the `Tools/Solutions Analyzer` directory:

```bash
# Upload specific CSV files
python upload_to_kusto.py -c https://mycluster.kusto.windows.net -d MyDatabase data.csv

# Upload multiple CSV files with a table name prefix
python upload_to_kusto.py -c https://mycluster.kusto.windows.net -d MyDatabase --prefix mydata file1.csv file2.csv

# Upload Solution Analyzer data from GitHub
python upload_to_kusto.py -c https://mycluster.kusto.windows.net -d MyDatabase --solution-analyzer

# Upload Solution Analyzer data from a local folder
python upload_to_kusto.py -c https://mycluster.kusto.windows.net -d MyDatabase --solution-analyzer --source-dir ./

# Dry run to see what would be uploaded
python upload_to_kusto.py -c https://mycluster.kusto.windows.net -d MyDatabase --dry-run data.csv
```

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `-c`, `--cluster` | *(required)* | Kusto cluster URL (e.g., `https://mycluster.region.kusto.windows.net`) |
| `-d`, `--database` | *(required)* | Kusto database name |
| `csv_files` | | One or more CSV files to upload (positional arguments) |
| `--solution-analyzer` | `False` | Download and upload Solution Analyzer CSVs from the public Azure-Sentinel GitHub repo |
| `--source-dir` | *(none)* | Source directory for Solution Analyzer CSVs (local folder instead of GitHub download). Requires `--solution-analyzer`. |
| `--prefix` | *(empty)* | Prefix for generated table names (custom CSV mode only) |
| `--dry-run` | `False` | Show what would be done without making changes |

> **Note:** You must provide either CSV files or the `--solution-analyzer` flag, but not both.

## Table Naming

### Custom CSV Mode

Table names are derived from the CSV filename:
- Non-alphanumeric characters are replaced with underscores
- Consecutive and leading/trailing underscores are removed
- Names are lowercased

Examples:
- `my-data-file.csv` → `my_data_file`
- With `--prefix myproject`: `my-data-file.csv` → `myproject_my_data_file`

### Solution Analyzer Mode

When using `--solution-analyzer`, files are downloaded from the Azure-Sentinel GitHub repository and uploaded with predefined table names:

| Source File | Kusto Table |
|-------------|-------------|
| `tables_reference.csv` | `solution_analyzer_table_reference_lookup` |
| `connectors.csv` | `solution_analyzer_connectors_lookup` |
| `tables.csv` | `solution_analyzer_tables_lookup` |
| `solutions.csv` | `solution_analyzer_solutions_lookup` |
| `content_items.csv` | `solution_analyzer_content_items_lookup` |
| `solutions_connectors_tables_mapping_simplified.csv` | `solution_analyzer_mapping` |
| `solutions_connectors_tables_mapping.csv` | `solution_analyzer_full_mapping` |
| `content_tables_mapping.csv` | `solution_analyzer_content_tables_mapping` |
| `parsers.csv` | `solution_analyzer_parsers_lookup` |
| `asim_parsers.csv` | `solution_analyzer_asim_parsers_lookup` |

## Authentication

The script uses Azure CLI authentication to obtain an access token for Kusto. Make sure you are logged in:

```bash
az login
az account show  # Verify your account
```

The token is obtained by running `az account get-access-token` with a 60-second timeout. If the Azure CLI is not found on the PATH, the script checks common Windows installation locations.

## Upload Process

For each CSV file, the script:

1. Reads CSV headers to determine the schema
2. Drops the existing table if it exists
3. Creates a new table with all `string` columns matching the CSV headers
4. Creates a CSV ingestion mapping for the table
5. Uploads the data using Kusto queued ingestion

> **Note:** Queued ingestion may take a few minutes to complete after the script finishes. You can check ingestion status with `.show ingestion failures` in Kusto.

## Example KQL Queries

After uploading Solution Analyzer data, try these queries:

```kql
// Find all connectors for a solution
solution_analyzer_mapping
| where solution_name == "Microsoft 365"
| distinct connector_id, connector_title

// Get connectors by collection method
solution_analyzer_connectors_lookup
| where collection_method == "AMA"
| project connector_id, connector_title

// Find tables and their categories
solution_analyzer_table_reference_lookup
| where isnotempty(category)
| project table_name, category, basic_logs_eligible

// Content items by type
solution_analyzer_content_items_lookup
| summarize count() by content_type
| order by count_ desc
```
