#!/usr/bin/env python3
"""
Upload Solutions Analyzer CSV files to Azure Data Explorer (Kusto) cluster.

This script drops existing tables and re-uploads CSV data to the specified Kusto database.
Uses streaming ingestion for fast uploads (same method as ADX "Get Data" UI).

Usage:
    python upload_to_kusto.py --cluster <cluster_url> --database <database_name>
    
Example:
    python upload_to_kusto.py --cluster "https://mycluster.westus.kusto.windows.net" --database "MyDatabase"

Prerequisites:
    pip install azure-kusto-data azure-kusto-ingest azure-identity pandas
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Tuple

try:
    from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
    from azure.kusto.data.exceptions import KustoServiceError
    from azure.kusto.ingest import (
        ManagedStreamingIngestClient,
        IngestionProperties,
        DataFormat,
    )
    from azure.identity import DefaultAzureCredential
except ImportError as e:
    print(f"Error: Missing required package: {e}")
    print("Install required packages with: pip install azure-kusto-data azure-kusto-ingest azure-identity")
    sys.exit(1)


# Mapping of CSV files to Kusto table names
TABLE_MAPPINGS: List[Tuple[str, str]] = [
    ("tables_reference.csv", "solution_analyzer_table_reference_lookup"),
    ("connectors.csv", "solution_analyzer_connectors_lookup"),
    ("tables.csv", "solution_analyzer_tables_lookup"),
    ("solutions.csv", "solution_analyzer_solutions_lookup"),
    ("solutions_connectors_tables_mapping_simplified.csv", "solution_analyzer_mapping"),
    ("solutions_connectors_tables_mapping.csv", "solutions_connectors_tables_mapping"),
]


def get_csv_columns(csv_path: Path) -> List[str]:
    """Read CSV headers."""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames)


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
    ingest_client: ManagedStreamingIngestClient,
    database: str,
    csv_path: Path,
    table_name: str
) -> bool:
    """
    Upload a CSV file to Kusto using managed streaming ingestion.
    
    This is fast - similar to the ADX "Get Data" UI approach.
    """
    print(f"\nProcessing: {csv_path.name} -> {table_name}")
    
    if not csv_path.exists():
        print(f"  Error: CSV file not found: {csv_path}")
        return False
    
    file_size = csv_path.stat().st_size
    print(f"  File size: {file_size / 1024:.1f} KB")
    
    # Get columns from CSV
    columns = get_csv_columns(csv_path)
    print(f"  Columns: {len(columns)}")
    
    # Drop existing table and create new one with mapping
    print(f"  Dropping existing table...")
    drop_table_if_exists(mgmt_client, database, table_name)
    
    print(f"  Creating table and mapping...")
    if not create_table_and_mapping(mgmt_client, database, table_name, columns):
        return False
    
    # Ingest the CSV file using streaming ingestion
    mapping_name = f"{table_name}_csv_mapping"
    ingestion_props = IngestionProperties(
        database=database,
        table=table_name,
        data_format=DataFormat.CSV,
        ingestion_mapping_reference=mapping_name,
        flush_immediately=True,  # Don't wait for batching
    )
    
    print(f"  Uploading data (streaming)...")
    try:
        # Use ingest_from_file for streaming ingestion
        result = ingest_client.ingest_from_file(str(csv_path), ingestion_properties=ingestion_props)
        print(f"  Successfully ingested {csv_path.name}")
        return True
    except Exception as e:
        print(f"  Error during ingestion: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Upload Solutions Analyzer CSV files to Kusto cluster (fast streaming ingestion)"
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
        "--csv-dir",
        default=".",
        help="Directory containing CSV files (default: current directory)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    
    csv_dir = Path(args.csv_dir)
    cluster_url = args.cluster
    database = args.database
    
    print(f"Kusto Cluster: {cluster_url}")
    print(f"Database: {database}")
    print(f"CSV Directory: {csv_dir.absolute()}")
    print()
    
    # Check that all CSV files exist
    missing_files = []
    for csv_file, table_name in TABLE_MAPPINGS:
        csv_path = csv_dir / csv_file
        if not csv_path.exists():
            missing_files.append(csv_file)
    
    if missing_files:
        print("Error: The following CSV files are missing:")
        for f in missing_files:
            print(f"  - {f}")
        print("\nRun the mapping script first to generate these files.")
        sys.exit(1)
    
    if args.dry_run:
        print("=== DRY RUN MODE ===")
        print("\nThe following tables would be created/replaced:\n")
        for csv_file, table_name in TABLE_MAPPINGS:
            csv_path = csv_dir / csv_file
            columns = get_csv_columns(csv_path)
            file_size = csv_path.stat().st_size
            print(f"  {csv_file} ({file_size/1024:.1f} KB) -> {table_name}")
            print(f"    Columns: {len(columns)}")
        print("\nRun without --dry-run to execute the upload.")
        return
    
    # Create Kusto clients using DefaultAzureCredential
    print("Authenticating with Azure...")
    try:
        credential = DefaultAzureCredential()
        
        # Management client for DDL operations
        mgmt_kcsb = KustoConnectionStringBuilder.with_azure_token_credential(
            cluster_url, credential
        )
        mgmt_client = KustoClient(mgmt_kcsb)
        
        # Managed streaming ingest client (handles both streaming and queued automatically)
        ingest_kcsb = KustoConnectionStringBuilder.with_azure_token_credential(
            cluster_url, credential
        )
        ingest_client = ManagedStreamingIngestClient.from_dm_kcsb(ingest_kcsb)
        
        print("Authentication successful.\n")
    except Exception as e:
        print(f"Error: Failed to authenticate: {e}")
        print("\nMake sure you are logged in with Azure CLI (az login) or have valid credentials configured.")
        sys.exit(1)
    
    # Process each CSV file
    success_count = 0
    fail_count = 0
    
    for csv_file, table_name in TABLE_MAPPINGS:
        csv_path = csv_dir / csv_file
        if upload_csv_to_kusto(mgmt_client, ingest_client, database, csv_path, table_name):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 50)
    print(f"Upload complete: {success_count} succeeded, {fail_count} failed")


if __name__ == "__main__":
    main()
