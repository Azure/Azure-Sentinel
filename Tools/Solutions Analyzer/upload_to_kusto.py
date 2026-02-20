#!/usr/bin/env python3
"""
Upload CSV files to Azure Data Explorer (Kusto) cluster.

This script drops existing tables and re-uploads CSV data to the specified Kusto database.
Uses streaming ingestion for fast uploads (same method as ADX "Get Data" UI).

Can upload:
- Any CSV files specified on the command line
- Solution Analyzer CSV files from the public Azure-Sentinel GitHub repository (--solution-analyzer flag)

Usage:
    # Upload specific CSV files
    python upload_to_kusto.py --cluster <url> --database <db> file1.csv file2.csv
    
    # Upload Solution Analyzer data from GitHub
    python upload_to_kusto.py --cluster <url> --database <db> --solution-analyzer
    
Example:
    python upload_to_kusto.py -c "https://mycluster.westus.kusto.windows.net" -d "MyDb" data.csv
    python upload_to_kusto.py -c "https://mycluster.westus.kusto.windows.net" -d "MyDb" --solution-analyzer

Prerequisites:
    pip install azure-kusto-data azure-kusto-ingest azure-identity pandas requests
"""

import argparse
import csv
import io
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple, Optional, Dict

try:
    from azure.kusto.data import KustoClient, KustoConnectionStringBuilder, DataFormat
    from azure.kusto.data.exceptions import KustoServiceError
    from azure.kusto.ingest import (
        QueuedIngestClient,
        IngestionProperties,
    )
except ImportError as e:
    print(f"Error: Missing required package: {e}")
    print("Install required packages with: pip install azure-kusto-data azure-kusto-ingest azure-identity")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Warning: 'requests' package not installed. --solution-analyzer feature will not work.")
    print("Install with: pip install requests")
    requests = None


# GitHub raw URL base for Solution Analyzer CSVs
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Tools/Solutions%20Analyzer"

# Solution Analyzer CSV files and their default Kusto table names
SOLUTION_ANALYZER_FILES: List[Tuple[str, str]] = [
    ("tables_reference.csv", "solution_analyzer_table_reference_lookup"),
    ("connectors.csv", "solution_analyzer_connectors_lookup"),
    ("tables.csv", "solution_analyzer_tables_lookup"),
    ("solutions.csv", "solution_analyzer_solutions_lookup"),
    ("content_items.csv", "solution_analyzer_content_items_lookup"),
    ("solutions_connectors_tables_mapping_simplified.csv", "solution_analyzer_mapping"),
    ("solutions_connectors_tables_mapping.csv", "solution_analyzer_full_mapping"),
    ("content_tables_mapping.csv", "solution_analyzer_content_tables_mapping"),
    ("parsers.csv", "solution_analyzer_parsers_lookup"),
    ("asim_parsers.csv", "solution_analyzer_asim_parsers_lookup"),
]


def get_azure_cli_token(resource: str = "https://kusto.kusto.windows.net") -> str:
    """Get access token from Azure CLI with longer timeout."""
    import json
    import shutil
    
    # Find az executable
    az_path = shutil.which("az")
    if not az_path:
        # Try common Windows locations
        for path in [
            r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
            r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
        ]:
            if Path(path).exists():
                az_path = path
                break
    
    if not az_path:
        raise RuntimeError("Azure CLI not found. Please install it or add it to PATH.")
    
    cmd = [az_path, "account", "get-access-token", "--resource", resource, "--output", "json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=True)
        if result.returncode != 0:
            raise RuntimeError(f"Azure CLI error: {result.stderr}")
        token_info = json.loads(result.stdout)
        return token_info["accessToken"]
    except subprocess.TimeoutExpired:
        raise RuntimeError("Azure CLI timed out getting token. Check your VPN connection.")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse Azure CLI output: {result.stdout}")
    except Exception as e:
        raise RuntimeError(f"Failed to get Azure CLI token: {e}")


def get_csv_columns_from_file(csv_path: Path) -> List[str]:
    """Read CSV headers from file."""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames)


def get_csv_columns_from_content(content: str) -> List[str]:
    """Read CSV headers from content string."""
    reader = csv.DictReader(io.StringIO(content))
    return list(reader.fieldnames)


def download_csv_from_github(filename: str) -> Optional[str]:
    """Download a CSV file from the GitHub repository."""
    if requests is None:
        print(f"Error: 'requests' package required for --solution-analyzer feature")
        return None
    
    url = f"{GITHUB_RAW_BASE}/{filename}"
    print(f"  Downloading: {url}")
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"  Error downloading {filename}: {e}")
        return None


def drop_table_if_exists(client: KustoClient, database: str, table_name: str) -> bool:
    """Drop table if it exists."""
    try:
        drop_cmd = f".drop table ['{table_name}'] ifexists"
        client.execute_mgmt(database, drop_cmd)
        return True
    except KustoServiceError as e:
        print(f"  Warning: Could not drop table {table_name}: {e}")
        return False


def create_table_and_mapping(client: KustoClient, database: str, table_name: str, columns: List[str]) -> bool:
    """Create table with schema and CSV mapping."""
    try:
        # Create table with all string columns
        column_defs = ", ".join([f"['{col}']: string" for col in columns])
        create_cmd = f".create table ['{table_name}'] ({column_defs})"
        client.execute_mgmt(database, create_cmd)
        
        # Create CSV mapping
        mapping_name = f"{table_name}_csv_mapping"
        mappings = []
        for idx, col in enumerate(columns):
            mappings.append(f'{{"Name": "{col}", "DataType": "string", "Ordinal": {idx}}}')
        mapping_json = "[" + ", ".join(mappings) + "]"
        mapping_cmd = f".create table ['{table_name}'] ingestion csv mapping '{mapping_name}' '{mapping_json}'"
        client.execute_mgmt(database, mapping_cmd)
        
        return True
    except KustoServiceError as e:
        print(f"  Error creating table/mapping: {e}")
        return False


def upload_csv_to_kusto(
    mgmt_client: KustoClient,
    ingest_client: QueuedIngestClient,
    database: str,
    csv_path: Path,
    table_name: str
) -> bool:
    """Upload a CSV file to Kusto using queued ingestion."""
    print(f"\nProcessing: {csv_path.name} -> {table_name}")
    
    if not csv_path.exists():
        print(f"  Error: CSV file not found: {csv_path}")
        return False
    
    file_size = csv_path.stat().st_size
    print(f"  File size: {file_size / 1024:.1f} KB")
    
    # Get columns from CSV
    columns = get_csv_columns_from_file(csv_path)
    print(f"  Columns: {len(columns)}")
    
    # Drop existing table and create new one with mapping
    print(f"  Dropping existing table...")
    drop_table_if_exists(mgmt_client, database, table_name)
    
    print(f"  Creating table and mapping...")
    if not create_table_and_mapping(mgmt_client, database, table_name, columns):
        return False
    
    # Ingest the CSV file using queued ingestion
    mapping_name = f"{table_name}_csv_mapping"
    ingestion_props = IngestionProperties(
        database=database,
        table=table_name,
        data_format=DataFormat.CSV,
        ingestion_mapping_reference=mapping_name,
    )
    
    print(f"  Uploading data...")
    try:
        result = ingest_client.ingest_from_file(str(csv_path), ingestion_properties=ingestion_props)
        print(f"  Ingestion queued successfully")
        return True
    except Exception as e:
        print(f"  Error during ingestion: {e}")
        return False


def upload_csv_content_to_kusto(
    mgmt_client: KustoClient,
    ingest_client: QueuedIngestClient,
    database: str,
    content: str,
    source_name: str,
    table_name: str
) -> bool:
    """Upload CSV content (string) to Kusto using queued ingestion."""
    print(f"\nProcessing: {source_name} -> {table_name}")
    
    content_size = len(content.encode('utf-8'))
    print(f"  Content size: {content_size / 1024:.1f} KB")
    
    # Get columns from CSV content
    columns = get_csv_columns_from_content(content)
    print(f"  Columns: {len(columns)}")
    
    # Drop existing table and create new one with mapping
    print(f"  Dropping existing table...")
    drop_table_if_exists(mgmt_client, database, table_name)
    
    print(f"  Creating table and mapping...")
    if not create_table_and_mapping(mgmt_client, database, table_name, columns):
        return False
    
    # Write content to temp file for ingestion
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        # Ingest the CSV file using queued ingestion
        mapping_name = f"{table_name}_csv_mapping"
        ingestion_props = IngestionProperties(
            database=database,
            table=table_name,
            data_format=DataFormat.CSV,
            ingestion_mapping_reference=mapping_name,
        )
        
        print(f"  Uploading data...")
        result = ingest_client.ingest_from_file(temp_path, ingestion_properties=ingestion_props)
        print(f"  Ingestion queued successfully")
        return True
    except Exception as e:
        print(f"  Error during ingestion: {e}")
        return False
    finally:
        # Clean up temp file
        Path(temp_path).unlink(missing_ok=True)


def derive_table_name(csv_path: Path, table_prefix: str) -> str:
    """Derive a Kusto table name from a CSV filename."""
    # Remove .csv extension and clean up the name
    base_name = csv_path.stem.lower()
    # Replace non-alphanumeric chars with underscores
    clean_name = ''.join(c if c.isalnum() else '_' for c in base_name)
    # Remove consecutive underscores
    while '__' in clean_name:
        clean_name = clean_name.replace('__', '_')
    # Remove leading/trailing underscores
    clean_name = clean_name.strip('_')
    
    if table_prefix:
        return f"{table_prefix}_{clean_name}"
    return clean_name


def main():
    parser = argparse.ArgumentParser(
        description="Upload CSV files to Azure Data Explorer (Kusto) cluster",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload specific CSV files
  python upload_to_kusto.py -c https://cluster.kusto.windows.net -d MyDb data.csv
  
  # Upload multiple CSV files with a table name prefix
  python upload_to_kusto.py -c https://cluster.kusto.windows.net -d MyDb --prefix mydata file1.csv file2.csv
  
  # Upload Solution Analyzer data from GitHub
  python upload_to_kusto.py -c https://cluster.kusto.windows.net -d MyDb --solution-analyzer
  
  # Upload Solution Analyzer data from a local folder
  python upload_to_kusto.py -c https://cluster.kusto.windows.net -d MyDb --solution-analyzer --source-dir ./
  
  # Dry run to see what would be uploaded
  python upload_to_kusto.py -c https://cluster.kusto.windows.net -d MyDb --dry-run data.csv
"""
    )
    parser.add_argument(
        "--cluster", "-c",
        required=True,
        help="Kusto cluster URL (e.g., https://mycluster.region.kusto.windows.net)"
    )
    parser.add_argument(
        "--database", "-d",
        required=True,
        help="Kusto database name"
    )
    parser.add_argument(
        "csv_files",
        nargs="*",
        help="CSV files to upload (each becomes a table)"
    )
    parser.add_argument(
        "--solution-analyzer",
        action="store_true",
        help="Download and upload Solution Analyzer CSVs from the public Azure-Sentinel GitHub repo"
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="Prefix for generated table names (for custom CSV files)"
    )
    parser.add_argument(
        "--source-dir",
        default=None,
        help="Source directory for Solution Analyzer CSVs (local folder instead of GitHub download). Requires --solution-analyzer."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.csv_files and not args.solution_analyzer:
        parser.error("Provide CSV files or use --solution-analyzer flag")
    
    if args.csv_files and args.solution_analyzer:
        parser.error("Cannot specify both CSV files and --solution-analyzer")
    
    if args.source_dir and not args.solution_analyzer:
        parser.error("--source-dir requires --solution-analyzer")
    
    cluster_url = args.cluster
    database = args.database
    
    print(f"Kusto Cluster: {cluster_url}")
    print(f"Database: {database}")
    print()
    
    # Prepare the list of files/content to upload
    files_to_upload: List[Tuple[str, str, Optional[Path], Optional[str]]] = []
    # Format: (display_name, table_name, file_path_or_none, content_or_none)
    
    if args.solution_analyzer:
        source_dir = Path(args.source_dir) if args.source_dir else None
        
        if source_dir:
            print(f"Mode: Solution Analyzer (local folder)")
            print(f"Source: {source_dir.resolve()}")
        else:
            print("Mode: Solution Analyzer (downloading from GitHub)")
            print(f"Source: {GITHUB_RAW_BASE}")
        print()
        
        if args.dry_run:
            print("=== DRY RUN MODE ===\n")
            source_label = "read from local folder" if source_dir else "download"
            print(f"Would {source_label} and upload the following files:\n")
            for filename, table_name in SOLUTION_ANALYZER_FILES:
                if source_dir:
                    csv_path = source_dir / filename
                    status = "  " if csv_path.exists() else " (MISSING)"
                    print(f"  {filename}{status} -> {table_name}")
                else:
                    print(f"  {filename} -> {table_name}")
            print("\nRun without --dry-run to execute.")
            return
        
        if source_dir:
            # Read files from local folder
            missing_files = []
            for filename, table_name in SOLUTION_ANALYZER_FILES:
                csv_path = source_dir / filename
                if csv_path.exists():
                    files_to_upload.append((filename, table_name, csv_path, None))
                else:
                    missing_files.append(filename)
            
            if missing_files:
                print("Error: The following Solution Analyzer CSV files were not found:")
                for f in missing_files:
                    print(f"  - {source_dir / f}")
                sys.exit(1)
        else:
            # Download files from GitHub
            for filename, table_name in SOLUTION_ANALYZER_FILES:
                content = download_csv_from_github(filename)
                if content:
                    files_to_upload.append((filename, table_name, None, content))
                else:
                    print(f"  Warning: Skipping {filename} (download failed)")
    else:
        print(f"Mode: Custom CSV files")
        if args.prefix:
            print(f"Table prefix: {args.prefix}")
        print()
        
        # Process local files
        missing_files = []
        for csv_file in args.csv_files:
            csv_path = Path(csv_file)
            if not csv_path.exists():
                missing_files.append(csv_file)
                continue
            
            table_name = derive_table_name(csv_path, args.prefix)
            files_to_upload.append((csv_path.name, table_name, csv_path, None))
        
        if missing_files:
            print("Error: The following CSV files were not found:")
            for f in missing_files:
                print(f"  - {f}")
            sys.exit(1)
        
        if args.dry_run:
            print("=== DRY RUN MODE ===\n")
            print("Would upload the following files:\n")
            for display_name, table_name, csv_path, _ in files_to_upload:
                if csv_path:
                    columns = get_csv_columns_from_file(csv_path)
                    file_size = csv_path.stat().st_size
                    print(f"  {display_name} ({file_size/1024:.1f} KB) -> {table_name}")
                    print(f"    Columns: {len(columns)}")
            print("\nRun without --dry-run to execute.")
            return
    
    if not files_to_upload:
        print("Error: No files to upload.")
        sys.exit(1)
    
    # Authenticate
    print("Authenticating with Azure CLI...")
    try:
        token = get_azure_cli_token()
        
        # Management client for DDL operations
        mgmt_kcsb = KustoConnectionStringBuilder.with_aad_application_token_authentication(
            cluster_url, token
        )
        mgmt_client = KustoClient(mgmt_kcsb)
        
        # Queued ingest client - derive ingest URL from cluster URL
        ingest_url = cluster_url.replace("https://", "https://ingest-")
        ingest_kcsb = KustoConnectionStringBuilder.with_aad_application_token_authentication(
            ingest_url, token
        )
        ingest_client = QueuedIngestClient(ingest_kcsb)
        
        print("Authentication successful.\n")
    except Exception as e:
        print(f"Error: Failed to authenticate: {e}")
        print("\nMake sure you are logged in with Azure CLI (az login).")
        sys.exit(1)
    
    # Process each file
    success_count = 0
    fail_count = 0
    
    for display_name, table_name, csv_path, content in files_to_upload:
        if csv_path:
            # Local file
            if upload_csv_to_kusto(mgmt_client, ingest_client, database, csv_path, table_name):
                success_count += 1
            else:
                fail_count += 1
        elif content:
            # Downloaded content
            if upload_csv_content_to_kusto(mgmt_client, ingest_client, database, content, display_name, table_name):
                success_count += 1
            else:
                fail_count += 1
    
    print("\n" + "=" * 50)
    print(f"Upload complete: {success_count} succeeded, {fail_count} failed")
    if success_count > 0:
        print("\nNote: Queued ingestion may take a few minutes to complete.")
        print("You can check ingestion status with: .show ingestion failures")


if __name__ == "__main__":
    main()
