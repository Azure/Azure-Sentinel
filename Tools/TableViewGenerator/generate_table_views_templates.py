#!/usr/bin/env python3
"""
Table View Template Generator

Generates Bicep templates that deploy KQL functions to a Log Analytics workspace,
emulating tables using the datatable operator.

This tool creates Bicep templates for deploying empty table views (KQL functions 
using datatable) to a Log Analytics workspace. This is useful for testing parsers 
and queries against table schemas without requiring actual data.

Usage:
    python generate_table_views_templates.py -t SigninLogs SecurityEvent
    python generate_table_views_templates.py -f tables.txt -o myViews.bicep
    python generate_table_views_templates.py -s schema1.json schema2.json
"""

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

# ==============================================================================
# Schema Classes
# ==============================================================================

@dataclass
class ColumnProperty:
    """Represents a column in a table schema."""
    name: str
    type: str


@dataclass
class TableSchema:
    """Represents a table schema with its columns."""
    name: str
    properties: List[ColumnProperty] = field(default_factory=list)


# ==============================================================================
# Cache Configuration
# ==============================================================================

_cache_enabled = True
_cache_ttl = 604800  # 1 week in seconds
_cache_dir = Path(__file__).parent / ".cache"


def configure_cache(enabled: bool = True, cache_ttl: int = 604800, cache_dir: Optional[Path] = None):
    """Configure cache settings."""
    global _cache_enabled, _cache_ttl, _cache_dir
    _cache_enabled = enabled
    _cache_ttl = cache_ttl
    if cache_dir:
        _cache_dir = cache_dir


def _get_cache_path(url: str) -> Path:
    """Get the cache file path for a URL."""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return _cache_dir / f"{url_hash}.cache"


def _read_from_cache(url: str) -> Optional[str]:
    """Read content from cache if valid."""
    if not _cache_enabled:
        return None
    
    cache_path = _get_cache_path(url)
    if not cache_path.exists():
        return None
    
    # Check if cache is expired
    mtime = cache_path.stat().st_mtime
    age = datetime.now().timestamp() - mtime
    if age > _cache_ttl:
        return None
    
    try:
        return cache_path.read_text(encoding='utf-8')
    except Exception:
        return None


def _write_to_cache(url: str, content: str):
    """Write content to cache."""
    if not _cache_enabled:
        return
    
    try:
        _cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = _get_cache_path(url)
        cache_path.write_text(content, encoding='utf-8')
    except Exception:
        pass  # Cache write failures are non-fatal


def clear_cache() -> int:
    """Clear all cached files. Returns number of files cleared."""
    if not _cache_dir.exists():
        return 0
    
    count = 0
    for cache_file in _cache_dir.glob("*.cache"):
        try:
            cache_file.unlink()
            count += 1
        except Exception:
            pass
    return count


def get_cache_stats() -> dict:
    """Get cache statistics."""
    if not _cache_dir.exists():
        return {'count': 0, 'size': 0, 'size_mb': 0, 'enabled': _cache_enabled}
    
    files = list(_cache_dir.glob("*.cache"))
    total_size = sum(f.stat().st_size for f in files)
    
    return {
        'count': len(files),
        'size': total_size,
        'size_mb': round(total_size / (1024 * 1024), 2),
        'enabled': _cache_enabled,
        'ttl_seconds': _cache_ttl,
        'cache_dir': str(_cache_dir)
    }


# ==============================================================================
# Schema Reader - Local JSON Files
# ==============================================================================

def read_schema_from_json_file(file_path: Path) -> Optional[TableSchema]:
    """
    Read a table schema from a JSON file in CustomTables format.
    
    Args:
        file_path: Path to the JSON schema file
        
    Returns:
        TableSchema if successful, None otherwise
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        data = json.loads(content)
        
        # Case-insensitive key lookup helper
        def get_key_case_insensitive(d: dict, key: str):
            key_lower = key.lower()
            for k in d:
                if k.lower() == key_lower:
                    return d[k]
            return None
        
        table_name = get_key_case_insensitive(data, 'Name') or file_path.stem
        properties_data = get_key_case_insensitive(data, 'Properties') or []
        
        properties = []
        for prop in properties_data:
            prop_name = get_key_case_insensitive(prop, 'Name')
            prop_type = get_key_case_insensitive(prop, 'Type')
            if prop_name and prop_type:
                properties.append(ColumnProperty(name=prop_name, type=prop_type))
        
        if not properties:
            print(f"    Warning: No properties found in {file_path}")
            return None
            
        return TableSchema(name=table_name, properties=properties)
        
    except json.JSONDecodeError as e:
        print(f"    Warning: Invalid JSON in {file_path}: {e}")
        return None
    except Exception as e:
        print(f"    Warning: Failed to read {file_path}: {e}")
        return None


def find_local_schema(table_name: str, custom_tables_path: Path) -> Optional[TableSchema]:
    """
    Search for a table schema in the local CustomTables folder.
    """
    if not custom_tables_path.exists():
        return None
    
    # Try exact match first
    exact_path = custom_tables_path / f"{table_name}.json"
    if exact_path.exists():
        return read_schema_from_json_file(exact_path)
    
    # Try case-insensitive search
    table_name_lower = table_name.lower()
    for json_file in custom_tables_path.glob("*.json"):
        if json_file.stem.lower() == table_name_lower:
            return read_schema_from_json_file(json_file)
    
    return None


def list_available_schemas(custom_tables_path: Path) -> List[str]:
    """List all available table schemas in the CustomTables folder."""
    if not custom_tables_path.exists():
        return []
    return sorted([f.stem for f in custom_tables_path.glob("*.json")])


# ==============================================================================
# Schema Reader - Online Documentation
# ==============================================================================

# Tables known to be in Defender XDR documentation
DEFENDER_XDR_TABLES = {
    'AADSignInEventsBeta', 'AADSpnSignInEventsBeta', 'AlertEvidence', 'AlertInfo',
    'BehaviorEntities', 'BehaviorInfo', 'CloudAppEvents', 'DeviceEvents',
    'DeviceFileCertificateInfo', 'DeviceFileEvents', 'DeviceImageLoadEvents',
    'DeviceInfo', 'DeviceLogonEvents', 'DeviceNetworkEvents', 'DeviceNetworkInfo',
    'DeviceProcessEvents', 'DeviceRegistryEvents', 'DeviceTvmHardwareFirmware',
    'DeviceTvmInfoGathering', 'DeviceTvmInfoGatheringKB', 'DeviceTvmSecureConfigurationAssessment',
    'DeviceTvmSecureConfigurationAssessmentKB', 'DeviceTvmSoftwareEvidenceBeta',
    'DeviceTvmSoftwareInventory', 'DeviceTvmSoftwareVulnerabilities',
    'DeviceTvmSoftwareVulnerabilitiesKB', 'EmailAttachmentInfo', 'EmailEvents',
    'EmailPostDeliveryEvents', 'EmailUrlInfo', 'ExposureGraphEdges', 'ExposureGraphNodes',
    'IdentityDirectoryEvents', 'IdentityInfo', 'IdentityLogonEvents', 'IdentityQueryEvents',
    'UrlClickEvents'
}


def is_defender_table(table_name: str) -> bool:
    """Check if a table is documented in Defender XDR."""
    return table_name in DEFENDER_XDR_TABLES


def _fetch_url_content(url: str) -> Optional[str]:
    """Fetch content from URL with caching."""
    # Check cache first
    cached = _read_from_cache(url)
    if cached:
        return cached
    
    try:
        with urlopen(url, timeout=30) as response:
            content = response.read().decode('utf-8')
            _write_to_cache(url, content)
            return content
    except (URLError, HTTPError):
        return None


def _parse_microsoft_docs_table(html_content: str, table_name: str) -> List[ColumnProperty]:
    """Parse Microsoft documentation HTML to extract table schema."""
    properties = []
    
    # Find the table section
    table_pattern = rf'<table[^>]*>.*?</table>'
    tables = re.findall(table_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    for table_html in tables:
        # Look for rows with column name and type
        row_pattern = r'<tr[^>]*>(.*?)</tr>'
        rows = re.findall(row_pattern, table_html, re.DOTALL | re.IGNORECASE)
        
        for row in rows:
            # Extract cell contents
            cell_pattern = r'<td[^>]*>(.*?)</td>'
            cells = re.findall(cell_pattern, row, re.DOTALL | re.IGNORECASE)
            
            if len(cells) >= 2:
                # Clean up cell contents
                col_name = re.sub(r'<[^>]+>', '', cells[0]).strip()
                col_type = re.sub(r'<[^>]+>', '', cells[1]).strip().lower()
                
                # Skip header rows or empty rows
                if not col_name or col_name.lower() in ['column name', 'column', 'name', 'field']:
                    continue
                
                # Normalize type names
                type_mapping = {
                    'string': 'string',
                    'datetime': 'datetime',
                    'bool': 'bool',
                    'boolean': 'bool',
                    'int': 'int',
                    'integer': 'int',
                    'long': 'long',
                    'real': 'real',
                    'double': 'real',
                    'dynamic': 'dynamic',
                    'guid': 'guid',
                    'timespan': 'timespan',
                    'decimal': 'decimal'
                }
                
                normalized_type = type_mapping.get(col_type, 'string')
                properties.append(ColumnProperty(name=col_name, type=normalized_type))
    
    return properties


def get_schema_from_azure_monitor(table_name: str) -> Optional[TableSchema]:
    """Get table schema from Azure Monitor log reference."""
    url = f"https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/{table_name.lower()}"
    content = _fetch_url_content(url)
    
    if not content:
        return None
    
    properties = _parse_microsoft_docs_table(content, table_name)
    
    if properties:
        return TableSchema(name=table_name, properties=properties)
    return None


def get_schema_from_defender_xdr(table_name: str) -> Optional[TableSchema]:
    """Get table schema from Defender XDR documentation."""
    # Convert CamelCase to kebab-case for URL
    kebab_name = re.sub(r'([a-z])([A-Z])', r'\1-\2', table_name).lower()
    url = f"https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-{kebab_name}-table"
    
    content = _fetch_url_content(url)
    if not content:
        return None
    
    properties = _parse_microsoft_docs_table(content, table_name)
    
    if properties:
        return TableSchema(name=table_name, properties=properties)
    return None


def get_schema_online(table_name: str) -> Optional[TableSchema]:
    """Get table schema from online Microsoft documentation."""
    # Determine which documentation source to try first
    if is_defender_table(table_name):
        schema = get_schema_from_defender_xdr(table_name)
        if schema:
            return schema
    
    # Try Azure Monitor reference
    schema = get_schema_from_azure_monitor(table_name)
    if schema:
        return schema
    
    # If it wasn't identified as a Defender table, try Defender anyway
    if not is_defender_table(table_name):
        schema = get_schema_from_defender_xdr(table_name)
        if schema:
            return schema
    
    return None


# ==============================================================================
# Template Generation
# ==============================================================================

def generate_datatable_kql(schema: TableSchema) -> str:
    """Generate the datatable KQL expression for a table schema."""
    if not schema.properties:
        return "datatable() []"
    
    columns = ", ".join(
        f"{prop.name}:{prop.type}" 
        for prop in schema.properties
    )
    
    return f"datatable({columns})[]"


def generate_bicep_template(
    schemas: Dict[str, TableSchema],
    output_path: Optional[str] = None,
    function_prefix: str = "",
    function_suffix: str = "_view"
) -> str:
    """Generate a Bicep template for deploying table view functions."""
    
    lines = [
        "// Bicep template for deploying KQL table view functions",
        "// Generated by TableViewGenerator",
        f"// Generated on: {datetime.now().isoformat()}",
        "",
        "@description('The resource ID of the Log Analytics workspace')",
        "param WorkspaceResourceId string",
        "",
        "// Extract workspace name from resource ID",
        "var workspaceName = last(split(WorkspaceResourceId, '/'))",
        ""
    ]
    
    for idx, (table_name, schema) in enumerate(schemas.items()):
        function_name = f"{function_prefix}{table_name}{function_suffix}"
        kql_query = generate_datatable_kql(schema)
        
        # Escape single quotes in KQL for Bicep string
        escaped_query = kql_query.replace("'", "''")
        
        lines.extend([
            f"resource savedSearch{idx} 'Microsoft.OperationalInsights/workspaces/savedSearches@2020-08-01' = {{",
            f"  name: '${{workspaceName}}/{function_name}'",
            f"  properties: {{",
            f"    displayName: '{table_name}'",
            f"    category: 'TableViews'",
            f"    query: '{escaped_query}'",
            f"    functionAlias: '{table_name}'",
            f"    functionParameters: ''",
            f"    version: 2",
            f"  }}",
            f"}}",
            ""
        ])
    
    content = "\n".join(lines)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return content


def generate_arm_template(
    schemas: Dict[str, TableSchema],
    output_path: Optional[str] = None,
    function_prefix: str = "",
    function_suffix: str = "_view"
) -> str:
    """Generate an ARM JSON template for deploying table view functions."""
    
    resources = []
    
    for table_name, schema in schemas.items():
        function_name = f"{function_prefix}{table_name}{function_suffix}"
        kql_query = generate_datatable_kql(schema)
        
        resource = {
            "type": "Microsoft.OperationalInsights/workspaces/savedSearches",
            "apiVersion": "2020-08-01",
            "name": f"[concat(last(split(parameters('WorkspaceResourceId'), '/')), '/{function_name}')]",
            "properties": {
                "displayName": table_name,
                "category": "TableViews",
                "query": kql_query,
                "functionAlias": table_name,
                "functionParameters": "",
                "version": 2
            }
        }
        resources.append(resource)
    
    template = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "metadata": {
            "description": "ARM template for deploying KQL table view functions",
            "generator": "TableViewGenerator",
            "generatedOn": datetime.now().isoformat()
        },
        "parameters": {
            "WorkspaceResourceId": {
                "type": "string",
                "metadata": {
                    "description": "The resource ID of the Log Analytics workspace"
                }
            }
        },
        "resources": resources
    }
    
    json_content = json.dumps(template, indent=2)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json_content)
    
    return json_content


def generate_kql_only(
    schemas: Dict[str, TableSchema],
    output_path: Optional[str] = None,
    function_prefix: str = "",
    function_suffix: str = "_view"
) -> str:
    """Generate KQL function definitions without deployment template."""
    
    lines = [
        "// KQL function definitions for table views",
        "// Generated by TableViewGenerator",
        "// Use these in Log Analytics queries or copy to saved functions",
        ""
    ]
    
    for table_name, schema in schemas.items():
        function_name = f"{function_prefix}{table_name}{function_suffix}"
        kql_query = generate_datatable_kql(schema)
        
        lines.extend([
            f"// Function: {function_name}",
            f"let {function_name} = () {{",
            f"    {kql_query}",
            f"}};",
            ""
        ])
    
    content = "\n".join(lines)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return content


# ==============================================================================
# Main CLI
# ==============================================================================

def get_default_custom_tables_path() -> Path:
    """Get the default path to CustomTables folder."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    custom_tables_path = repo_root / ".script" / "tests" / "KqlvalidationsTests" / "CustomTables"
    
    if custom_tables_path.exists():
        return custom_tables_path
    
    return Path(".")


def get_table_schema(
    table_name: str,
    custom_tables_path: Path,
    skip_online_search: bool = False
) -> Optional[TableSchema]:
    """Get table schema from various sources."""
    print(f"  Looking up schema for: {table_name}", end="")
    
    # 1. Try local CustomTables folder first
    schema = find_local_schema(table_name, custom_tables_path)
    if schema:
        print(f" - Found in local CustomTables folder")
        return schema
    
    # 2. Try online sources if not skipped
    if not skip_online_search:
        print(f" - Checking online...", end="")
        schema = get_schema_online(table_name)
        if schema:
            print(f" Found online")
            return schema
        print(f" Not found")
    else:
        print(f" - Not found locally")
    
    return None


def parse_table_list_file(file_path: Path) -> List[str]:
    """Parse a file containing table names (comma, semicolon, or newline separated)."""
    content = file_path.read_text(encoding='utf-8')
    table_names = re.split(r'[,;\r\n]+', content)
    return [name.strip() for name in table_names if name.strip()]


def main():
    parser = argparse.ArgumentParser(
        description="Generate Bicep templates for KQL table view functions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -t SigninLogs SecurityEvent
  %(prog)s -f tables.txt -o myViews.bicep
  %(prog)s -s schema1.json schema2.json
  %(prog)s -t DeviceEvents --prefix Test_ --suffix ""
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '-t', '--tables',
        nargs='+',
        metavar='TABLE',
        help='One or more table names to generate views for'
    )
    input_group.add_argument(
        '-f', '--table-file',
        type=Path,
        metavar='FILE',
        help='File containing table names (comma, semicolon, or newline separated)'
    )
    input_group.add_argument(
        '-s', '--schema-files',
        nargs='+',
        type=Path,
        metavar='FILE',
        help='JSON schema files in CustomTables format'
    )
    
    # Output options
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=Path('./tableViews.bicep'),
        metavar='FILE',
        help='Output file path (default: ./tableViews.bicep)'
    )
    parser.add_argument(
        '--format',
        choices=['bicep', 'arm', 'kql'],
        default='bicep',
        help='Output format (default: bicep)'
    )
    
    # Schema lookup options
    parser.add_argument(
        '-c', '--custom-tables-path',
        type=Path,
        metavar='PATH',
        help='Path to CustomTables folder containing JSON schema files'
    )
    parser.add_argument(
        '--skip-online',
        action='store_true',
        help='Skip searching online documentation for table schemas'
    )
    
    # Function naming options
    parser.add_argument(
        '--prefix',
        default='',
        metavar='STR',
        help='Prefix for function names (default: empty)'
    )
    parser.add_argument(
        '--suffix',
        default='',
        metavar='STR',
        help='Suffix for function names (default: empty)'
    )
    
    # Cache options
    parser.add_argument(
        '--refresh-cache',
        action='store_true',
        help='Clear cache and fetch fresh content from online sources'
    )
    parser.add_argument(
        '--skip-cache',
        action='store_true',
        help='Skip cache for this run only (do not read or write cache)'
    )
    parser.add_argument(
        '--cache-ttl',
        type=int,
        default=604800,
        metavar='SECONDS',
        help='Cache time-to-live in seconds (default: 604800 = 1 week)'
    )
    
    args = parser.parse_args()
    
    # Configure cache
    if args.refresh_cache:
        count = clear_cache()
        print(f"Cleared {count} cached files")
    
    configure_cache(
        enabled=not args.skip_cache,
        cache_ttl=args.cache_ttl
    )
    
    # Print banner
    print("\n=====================================")
    print("   Table View Template Generator     ")
    print("=====================================\n")
    
    # Determine CustomTables path
    custom_tables_path = args.custom_tables_path or get_default_custom_tables_path()
    
    # Collect table schemas
    table_schemas: Dict[str, TableSchema] = {}
    
    if args.tables:
        # Process table names
        print(f"Processing table names: {', '.join(args.tables)}")
        for table_name in args.tables:
            schema = get_table_schema(table_name, custom_tables_path, args.skip_online)
            if schema:
                table_schemas[table_name] = schema
            else:
                print(f"  WARNING: Could not find schema for table: {table_name}")
    
    elif args.table_file:
        # Process table list file
        if not args.table_file.exists():
            print(f"ERROR: Table file not found: {args.table_file}")
            sys.exit(1)
        
        print(f"Processing table list file: {args.table_file}")
        table_names = parse_table_list_file(args.table_file)
        print(f"  Found {len(table_names)} table(s) in file")
        
        for table_name in table_names:
            schema = get_table_schema(table_name, custom_tables_path, args.skip_online)
            if schema:
                table_schemas[table_name] = schema
            else:
                print(f"  WARNING: Could not find schema for table: {table_name}")
    
    elif args.schema_files:
        # Process schema files
        print("Processing schema files...")
        for schema_file in args.schema_files:
            if not schema_file.exists():
                print(f"  WARNING: Schema file not found: {schema_file}")
                continue
            
            print(f"  Loading: {schema_file}")
            schema = read_schema_from_json_file(schema_file)
            if schema:
                table_schemas[schema.name] = schema
                print(f"    Loaded {schema.name} ({len(schema.properties)} columns)")
            else:
                print(f"  WARNING: Could not parse schema file: {schema_file}")
    
    # Validate we have schemas
    if not table_schemas:
        print("\nERROR: No valid table schemas found. Exiting.")
        sys.exit(1)
    
    # Display found schemas
    print(f"\nFound schemas for {len(table_schemas)} table(s):")
    for name in sorted(table_schemas.keys()):
        col_count = len(table_schemas[name].properties)
        print(f"  - {name} ({col_count} columns)")
    
    # Generate template
    print(f"\nGenerating {args.format.upper()} template...")
    
    if args.format == 'arm':
        template_content = generate_arm_template(
            table_schemas,
            function_prefix=args.prefix,
            function_suffix=args.suffix
        )
        output_path = args.output.with_suffix('.json') if args.output.suffix == '.bicep' else args.output
    elif args.format == 'kql':
        template_content = generate_kql_only(
            table_schemas,
            function_prefix=args.prefix,
            function_suffix=args.suffix
        )
        output_path = args.output.with_suffix('.kql') if args.output.suffix == '.bicep' else args.output
    else:
        template_content = generate_bicep_template(
            table_schemas,
            function_prefix=args.prefix,
            function_suffix=args.suffix
        )
        output_path = args.output
    
    # Write output file
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(template_content, encoding='utf-8')
    
    print(f"\n{args.format.upper()} template generated successfully!")
    print(f"Output file: {output_path}")
    
    # Summary
    print("\n--- Summary ---")
    print(f"Tables processed: {len(table_schemas)}")
    print("Functions created:")
    for name in sorted(table_schemas.keys()):
        print(f"  - {args.prefix}{name}{args.suffix}")
    
    print("\nTo deploy the template, use:")
    print(f'  az deployment group create --resource-group <rg-name> --template-file "{output_path}" --parameters WorkspaceResourceId=<workspace-resource-id>')
    print()


if __name__ == '__main__':
    main()
