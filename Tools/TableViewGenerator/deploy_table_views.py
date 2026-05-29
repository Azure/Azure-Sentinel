#!/usr/bin/env python3
"""
Deploy Table Views Script

Deploys table view functions to a Log Analytics workspace, but only for tables
that don't already exist in the workspace. This prevents conflicts between
function aliases and existing table names.

Usage:
    python deploy_table_views.py --workspace-id <workspace-id> --resource-id <resource-id> --tables Table1 Table2
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional
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


# ==============================================================================
# Schema Reader - Local JSON Files
# ==============================================================================

def read_schema_from_json_file(file_path: Path) -> Optional[TableSchema]:
    """Read a table schema from a JSON file in CustomTables format."""
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
            return None
            
        return TableSchema(name=table_name, properties=properties)
        
    except (json.JSONDecodeError, Exception):
        return None


def find_local_schema(table_name: str, custom_tables_path: Path) -> Optional[TableSchema]:
    """Search for a table schema in the local CustomTables folder."""
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
    
    table_pattern = rf'<table[^>]*>.*?</table>'
    tables = re.findall(table_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    for table_html in tables:
        row_pattern = r'<tr[^>]*>(.*?)</tr>'
        rows = re.findall(row_pattern, table_html, re.DOTALL | re.IGNORECASE)
        
        for row in rows:
            cell_pattern = r'<td[^>]*>(.*?)</td>'
            cells = re.findall(cell_pattern, row, re.DOTALL | re.IGNORECASE)
            
            if len(cells) >= 2:
                col_name = re.sub(r'<[^>]+>', '', cells[0]).strip()
                col_type = re.sub(r'<[^>]+>', '', cells[1]).strip().lower()
                
                if not col_name or col_name.lower() in ['column name', 'column', 'name', 'field']:
                    continue
                
                type_mapping = {
                    'string': 'string', 'datetime': 'datetime', 'bool': 'bool',
                    'boolean': 'bool', 'int': 'int', 'integer': 'int', 'long': 'long',
                    'real': 'real', 'double': 'real', 'dynamic': 'dynamic',
                    'guid': 'guid', 'timespan': 'timespan', 'decimal': 'decimal'
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
    if is_defender_table(table_name):
        schema = get_schema_from_defender_xdr(table_name)
        if schema:
            return schema
    
    schema = get_schema_from_azure_monitor(table_name)
    if schema:
        return schema
    
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
    
    columns = ", ".join(f"{prop.name}:{prop.type}" for prop in schema.properties)
    return f"datatable({columns})[]"


def generate_bicep_template(
    schemas: Dict[str, TableSchema],
    function_prefix: str = "",
    function_suffix: str = ""
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
    
    return "\n".join(lines)


# ==============================================================================
# Azure CLI Helpers
# ==============================================================================

_az_cli_path: Optional[str] = None


def find_azure_cli() -> Optional[str]:
    """Find the Azure CLI executable."""
    az_path = shutil.which("az")
    if az_path:
        return az_path
    
    if sys.platform == "win32":
        common_paths = [
            Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "Microsoft SDKs" / "Azure" / "CLI2" / "wbin" / "az.cmd",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Azure CLI" / "az.cmd",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages" / "Microsoft.AzureCLI_Microsoft.Winget.Source_8wekyb3d8bbwe" / "az.cmd",
        ]
        for path in common_paths:
            if path.exists():
                return str(path)
    
    return None


def get_az_cli() -> Optional[str]:
    """Get the Azure CLI path (cached)."""
    global _az_cli_path
    if _az_cli_path is None:
        _az_cli_path = find_azure_cli()
    return _az_cli_path


def get_existing_tables(resource_group: str, workspace_name: str, 
                        subscription: Optional[str] = None) -> Set[str]:
    """Get list of existing tables in the workspace using the Tables API."""
    az_cli = get_az_cli()
    if not az_cli:
        print("Warning: Azure CLI not found. Cannot check for existing tables.")
        return set()
    
    cmd = [
        az_cli, "monitor", "log-analytics", "workspace", "table", "list",
        "--resource-group", resource_group,
        "--workspace-name", workspace_name,
        "--output", "json"
    ]
    
    if subscription:
        cmd.extend(["--subscription", subscription])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"Warning: Could not list workspace tables: {result.stderr}")
            return set()
            
        data = json.loads(result.stdout)
        tables = set()
        for table in data:
            if 'name' in table:
                tables.add(table['name'])
        return tables
    
    except subprocess.TimeoutExpired:
        print("Warning: Table list timed out. Proceeding without table check.")
        return set()
    except json.JSONDecodeError:
        print("Warning: Could not parse table list response")
        return set()
    except Exception as e:
        print(f"Warning: Error checking existing tables: {e}")
        return set()


def get_existing_functions(workspace_id: str, resource_group: str, workspace_name: str, 
                           subscription: Optional[str] = None) -> Set[str]:
    """Get list of existing saved search functions in the workspace."""
    az_cli = get_az_cli()
    if not az_cli:
        print("Warning: Azure CLI not found.")
        return set()
    
    cmd = [
        az_cli, "monitor", "log-analytics", "workspace", "saved-search", "list",
        "--resource-group", resource_group,
        "--workspace-name", workspace_name,
        "--output", "json"
    ]
    
    if subscription:
        cmd.extend(["--subscription", subscription])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        functions = set()
        for item in data:
            if 'functionAlias' in item:
                functions.add(item['functionAlias'])
            elif 'properties' in item and 'functionAlias' in item['properties']:
                functions.add(item['properties']['functionAlias'])
        
        return functions
    
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not list saved searches: {e.stderr}")
        return set()
    except json.JSONDecodeError:
        print("Warning: Could not parse saved searches response")
        return set()


def delete_saved_search(resource_group: str, workspace_name: str, saved_search_name: str,
                        subscription: Optional[str] = None) -> bool:
    """Delete a saved search from the workspace."""
    az_cli = get_az_cli()
    if not az_cli:
        print("Error: Azure CLI not found.")
        return False
    
    cmd = [
        az_cli, "monitor", "log-analytics", "workspace", "saved-search", "delete",
        "--resource-group", resource_group,
        "--workspace-name", workspace_name,
        "--name", saved_search_name,
        "--yes"  # Skip confirmation
    ]
    
    if subscription:
        cmd.extend(["--subscription", subscription])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Ignore "not found" errors
        if "not found" not in result.stderr.lower():
            print(f"  Warning: Could not delete {saved_search_name}: {result.stderr}")
            return False
    return True


def get_saved_search_names_for_functions(resource_group: str, workspace_name: str,
                                         function_aliases: List[str],
                                         subscription: Optional[str] = None) -> Dict[str, str]:
    """
    Get the saved search names for functions by their aliases.
    
    Returns a dict mapping function alias to saved search name.
    """
    az_cli = get_az_cli()
    if not az_cli:
        return {}
    
    cmd = [
        az_cli, "monitor", "log-analytics", "workspace", "saved-search", "list",
        "--resource-group", resource_group,
        "--workspace-name", workspace_name,
        "--output", "json"
    ]
    
    if subscription:
        cmd.extend(["--subscription", subscription])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        alias_to_name: Dict[str, str] = {}
        for item in data:
            alias = None
            name = None
            
            # Get function alias
            if 'functionAlias' in item:
                alias = item['functionAlias']
            elif 'properties' in item and 'functionAlias' in item['properties']:
                alias = item['properties']['functionAlias']
            
            # Get saved search name from the id or name field
            if 'name' in item:
                name = item['name']
            elif 'id' in item:
                # Extract name from resource ID
                name = item['id'].split('/')[-1]
            
            if alias and name and alias in function_aliases:
                alias_to_name[alias] = name
        
        return alias_to_name
    
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return {}


def deploy_bicep(bicep_file: Path, resource_group: str, workspace_resource_id: str,
                 subscription: Optional[str] = None) -> bool:
    """Deploy a Bicep template using Azure CLI."""
    az_cli = get_az_cli()
    if not az_cli:
        print("Error: Azure CLI not found.")
        return False
    
    cmd = [
        az_cli, "deployment", "group", "create",
        "--resource-group", resource_group,
        "--template-file", str(bicep_file),
        "--parameters", f"WorkspaceResourceId={workspace_resource_id}"
    ]
    
    if subscription:
        cmd.extend(["--subscription", subscription])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Deployment failed: {result.stderr}")
        return False
    return True


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


def get_table_schema(table_name: str, custom_tables_path: Path, 
                     skip_online: bool = False) -> Optional[TableSchema]:
    """Get table schema from local files or online documentation."""
    schema = find_local_schema(table_name, custom_tables_path)
    if schema:
        return schema
    
    if not skip_online:
        schema = get_schema_online(table_name)
        if schema:
            return schema
    
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Deploy table view functions to Log Analytics, skipping existing tables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --workspace-id <guid> --resource-id <full-resource-id> --tables AWSCloudTrail SecurityEvent
  %(prog)s --workspace-id <guid> --resource-id <full-resource-id> --table-file tables.txt
  %(prog)s --workspace-id <guid> --resource-id <full-resource-id> --tables Table1 --dry-run
        """
    )
    
    # Required parameters
    parser.add_argument(
        '--workspace-id', '-w',
        required=True,
        help='Log Analytics workspace ID (GUID)'
    )
    parser.add_argument(
        '--resource-id', '-r',
        required=True,
        help='Full resource ID of the Log Analytics workspace'
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--tables', '-t',
        nargs='+',
        metavar='TABLE',
        help='One or more table names to create views for'
    )
    input_group.add_argument(
        '--table-file', '-f',
        type=Path,
        metavar='FILE',
        help='File containing table names'
    )
    input_group.add_argument(
        '--schema-files', '-s',
        nargs='+',
        type=Path,
        metavar='FILE',
        help='JSON schema files'
    )
    
    # Optional parameters
    parser.add_argument(
        '--subscription',
        help='Azure subscription name or ID'
    )
    parser.add_argument(
        '--resource-group', '-g',
        help='Resource group name (extracted from resource-id if not provided)'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Save generated Bicep to this file (optional)'
    )
    parser.add_argument(
        '--custom-tables-path', '-c',
        type=Path,
        help='Path to CustomTables folder'
    )
    parser.add_argument(
        '--skip-online',
        action='store_true',
        help='Skip online schema lookup'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deployed without actually deploying'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Deploy even if tables already exist (may cause conflicts)'
    )
    parser.add_argument(
        '--no-redeploy',
        action='store_true',
        help='Skip redeploying existing functions (default: redeploy)'
    )
    parser.add_argument(
        '--skip-checks',
        action='store_true',
        help='Skip checking for existing tables (faster but may cause conflicts)'
    )
    parser.add_argument(
        '--suffix',
        default='',
        help='Suffix for saved search names (default: empty)'
    )
    parser.add_argument(
        '--refresh-cache',
        action='store_true',
        help='Clear schema cache before fetching'
    )
    
    args = parser.parse_args()
    
    # Configure cache
    if args.refresh_cache:
        clear_cache()
    
    # Extract resource group from resource ID if not provided
    resource_group = args.resource_group
    workspace_name = None
    if not resource_group:
        parts = args.resource_id.split('/')
        try:
            rg_idx = parts.index('resourceGroups') + 1
            resource_group = parts[rg_idx]
            ws_idx = parts.index('workspaces') + 1
            workspace_name = parts[ws_idx]
        except (ValueError, IndexError):
            print("Error: Could not parse resource group from resource ID. Use --resource-group.")
            sys.exit(1)
    
    if not workspace_name:
        parts = args.resource_id.split('/')
        try:
            ws_idx = parts.index('workspaces') + 1
            workspace_name = parts[ws_idx]
        except (ValueError, IndexError):
            pass
    
    print("\n==========================================")
    print("   Deploy Table Views to Log Analytics    ")
    print("==========================================\n")
    
    print(f"Workspace ID: {args.workspace_id}")
    print(f"Resource Group: {resource_group}")
    if workspace_name:
        print(f"Workspace Name: {workspace_name}")
    print()
    
    # Get list of existing tables in the workspace
    existing_tables: Set[str] = set()
    existing_functions: Set[str] = set()
    
    if not args.skip_checks and workspace_name:
        print("Checking for existing tables in workspace...")
        existing_tables = get_existing_tables(resource_group, workspace_name, args.subscription)
        if existing_tables:
            print(f"  Found {len(existing_tables)} existing tables")
        else:
            print("  Could not retrieve existing tables (will proceed with all requested tables)")
        
        print("Checking for existing functions...")
        existing_functions = get_existing_functions(
            args.workspace_id, resource_group, workspace_name, args.subscription
        )
        if existing_functions:
            print(f"  Found {len(existing_functions)} existing functions")
    elif args.skip_checks:
        print("Skipping existing table/function checks (--skip-checks)")
    else:
        print("Warning: Could not parse workspace name from resource ID. Skipping table checks.")
    
    # Collect requested table names
    requested_tables: List[str] = []
    
    if args.tables:
        requested_tables = args.tables
    elif args.table_file:
        if not args.table_file.exists():
            print(f"Error: Table file not found: {args.table_file}")
            sys.exit(1)
        content = args.table_file.read_text(encoding='utf-8')
        requested_tables = [t.strip() for t in re.split(r'[,;\r\n]+', content) if t.strip()]
    elif args.schema_files:
        for schema_file in args.schema_files:
            if schema_file.exists():
                schema = read_schema_from_json_file(schema_file)
                if schema:
                    requested_tables.append(schema.name)
    
    print(f"\nRequested tables: {', '.join(requested_tables)}")
    
    # Filter out tables that already exist (unless --force or --redeploy)
    tables_to_deploy: List[str] = []
    functions_to_redeploy: List[str] = []
    skipped_tables: List[str] = []
    
    for table in requested_tables:
        if table in existing_tables and not args.force:
            skipped_tables.append(f"{table} (table exists)")
            continue
        
        if table in existing_functions:
            if not args.no_redeploy:
                functions_to_redeploy.append(table)
                tables_to_deploy.append(table)
            elif not args.force:
                skipped_tables.append(f"{table} (function exists)")
            else:
                tables_to_deploy.append(table)
            continue
        
        tables_to_deploy.append(table)
    
    if skipped_tables:
        print(f"\nSkipping (already exist):")
        for t in skipped_tables:
            print(f"  - {t}")
    
    if functions_to_redeploy:
        print(f"\nFunctions to redeploy: {', '.join(functions_to_redeploy)}")
    
    if not tables_to_deploy:
        print("\nNo tables to deploy - all requested tables already exist.")
        sys.exit(0)
    
    print(f"\nTables to deploy: {', '.join(tables_to_deploy)}")
    
    # Get schemas for tables to deploy
    custom_tables_path = args.custom_tables_path or get_default_custom_tables_path()
    schemas: Dict[str, TableSchema] = {}
    
    print("\nFetching schemas...")
    for table_name in tables_to_deploy:
        schema = get_table_schema(table_name, custom_tables_path, args.skip_online)
        if schema:
            schemas[table_name] = schema
            print(f"  {table_name}: {len(schema.properties)} columns")
        else:
            print(f"  {table_name}: Schema not found (skipping)")
    
    if not schemas:
        print("\nError: No valid schemas found for any requested tables.")
        sys.exit(1)
    
    # Generate Bicep template
    print("\nGenerating Bicep template...")
    bicep_content = generate_bicep_template(schemas, function_suffix=args.suffix)
    
    # Save to file if requested
    if args.output:
        args.output.write_text(bicep_content, encoding='utf-8')
        print(f"  Saved to: {args.output}")
    
    # Dry run - just show what would be deployed
    if args.dry_run:
        print("\n--- DRY RUN - No deployment ---")
        if functions_to_redeploy:
            print(f"Would delete and redeploy {len(functions_to_redeploy)} function(s):")
            for table_name in functions_to_redeploy:
                print(f"  - {table_name}{args.suffix} (alias: {table_name})")
        new_functions = [t for t in schemas if t not in functions_to_redeploy]
        if new_functions:
            print(f"Would deploy {len(new_functions)} new function(s):")
            for table_name in new_functions:
                print(f"  - {table_name}{args.suffix} (alias: {table_name})")
        print("\nBicep template preview:")
        print("-" * 40)
        lines = bicep_content.split('\n')
        for line in lines[:50]:
            print(line)
        if len(lines) > 50:
            print(f"... ({len(lines) - 50} more lines)")
        sys.exit(0)
    
    # Delete existing functions if redeploying
    if functions_to_redeploy and workspace_name:
        print(f"\nDeleting {len(functions_to_redeploy)} existing function(s) for redeployment...")
        
        # Get the saved search names for the functions we want to delete
        alias_to_name = get_saved_search_names_for_functions(
            resource_group, workspace_name, functions_to_redeploy, args.subscription
        )
        
        for table_name in functions_to_redeploy:
            saved_search_name = alias_to_name.get(table_name)
            if saved_search_name:
                print(f"  Deleting: {saved_search_name}")
                delete_saved_search(resource_group, workspace_name, saved_search_name, args.subscription)
            else:
                # Try with the expected name pattern
                expected_name = f"{table_name}{args.suffix}"
                print(f"  Deleting: {expected_name}")
                delete_saved_search(resource_group, workspace_name, expected_name, args.subscription)
    
    # Deploy
    print("\nDeploying to Azure...")
    
    if args.output:
        bicep_file = args.output
    else:
        fd, temp_path = tempfile.mkstemp(suffix='.bicep')
        os.write(fd, bicep_content.encode('utf-8'))
        os.close(fd)
        bicep_file = Path(temp_path)
    
    try:
        success = deploy_bicep(bicep_file, resource_group, args.resource_id, args.subscription)
        
        if success:
            print("\n✓ Deployment succeeded!")
            print(f"  Created {len(schemas)} function(s):")
            for table_name in schemas:
                print(f"    - {table_name}")
        else:
            print("\n✗ Deployment failed")
            sys.exit(1)
    finally:
        if not args.output and bicep_file.exists():
            bicep_file.unlink()


if __name__ == '__main__':
    main()
