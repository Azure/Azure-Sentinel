from __future__ import annotations

import csv
import json
import os
import re
import argparse
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union
from urllib.parse import quote

try:
    import urllib.request
    import urllib.error
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False

try:
    import json5  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    json5 = None

GITHUB_REPO_URL = "https://github.com/Azure/Azure-Sentinel/blob/master"
AZURE_MARKETPLACE_API_URL = "https://catalogapi.azure.com/offers"
AZURE_MARKETPLACE_API_VERSION = "2018-08-01-beta"

# Icons for documentation output
NOT_PUBLISHED_ICON = "⚠️"  # Warning icon for unpublished solutions

# Regex patterns for query parsing
PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([^}]+?)\s*\}\}")
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_.]+")
ARM_VARIABLE_PATTERN = re.compile(r"\[\s*variables\(\s*['\"]([^'\"]+)['\"]\s*\)\s*\]\s*", re.IGNORECASE)
UNION_KEYWORD_PATTERN = re.compile(r"\bunion\b", re.IGNORECASE)
LET_ASSIGNMENT_PATTERN = re.compile(r"\blet\s+([A-Za-z0-9_]+)\s*=\s*([A-Za-z0-9_.]+)", re.IGNORECASE)
LINE_COMMENT_PATTERN = re.compile(r"(?m)^\s*//.*$")
FIELD_GENERATING_PATTERN = re.compile(
    r'^\s*\|\s*(?:extend|project|project-away|project-keep|project-rename|project-reorder|'
    r'summarize|make-series|mv-expand|mv-apply|evaluate)',
    re.IGNORECASE
)

# Legacy pattern for extracting vendor/product (kept for backwards compatibility)
# Matches patterns like: DeviceVendor == "value", DeviceVendor =~ "value", DeviceVendor = "value"
VENDOR_PRODUCT_PATTERN = re.compile(
    r'\b(DeviceVendor|DeviceProduct|EventVendor|EventProduct)\s*==?~?\s*["\']([^"\']+)["\']',
    re.IGNORECASE
)

# Comprehensive filter fields to extract from queries
# Format: field_name -> canonical_table (the table this field is typically found in)
# None means the table is determined by context or the field applies to multiple tables
FILTER_FIELDS = {
    # CommonSecurityLog fields
    'DeviceVendor': 'CommonSecurityLog',
    'DeviceProduct': 'CommonSecurityLog',
    'DeviceEventClassID': 'CommonSecurityLog',
    # ASIM fields (used in normalized tables)
    'EventVendor': None,  # Multiple tables
    'EventProduct': None,  # Multiple tables
    'EventType': None,  # Multiple ASIM tables
    # AzureDiagnostics / AzureActivity fields
    'ResourceType': 'AzureDiagnostics',
    'Category': 'AzureDiagnostics',
    'ResourceProvider': None,  # Both AzureDiagnostics and AzureActivity (determined by context)
    # Windows event fields
    'EventID': None,  # WindowsEvent, SecurityEvent, or Event (determined by context)
    'EventLog': 'Event',  # Event table EventLog field (the Windows event log channel, e.g., "MSExchange Management")
    'Source': 'Event',  # Event table Source field (e.g., "Service Control Manager")
    'Provider': 'WindowsEvent',  # WindowsEvent Provider field
    # Syslog fields
    'Facility': 'Syslog',
    'ProcessName': 'Syslog',
    'ProcessID': 'Syslog',
    'SyslogMessage': 'Syslog',
    # AWSCloudTrail fields
    'EventName': 'AWSCloudTrail',
    # Microsoft Defender XDR / M365 Defender fields
    'ActionType': None,  # DeviceEvents, DeviceFileEvents, DeviceProcessEvents, etc.
    # Office 365 / Microsoft 365 fields
    'OperationName': None,  # AuditLogs, AzureActivity, OfficeActivity, SigninLogs
    'OfficeWorkload': 'OfficeActivity',
    'RecordType': 'OfficeActivity',
}

# Fields that only use equality operators (==, =~, in)
EQUALITY_ONLY_FIELDS = {'EventID', 'RecordType'}  # Numeric fields restricted to equality operators

# Fields that can use string operators (has, contains, startswith, etc.)
# All string-based filter fields support these operators
STRING_OPERATOR_FIELDS = set(FILTER_FIELDS.keys()) - {'EventID', 'ProcessID', 'RecordType'}

# Pattern to extract simple equality comparisons: field == "value", field =~ "value", field = "value"
# Also handles negative: field != "value"
# Captures the operator used
FILTER_EQUALITY_PATTERN = re.compile(
    r'\b(' + '|'.join(FILTER_FIELDS.keys()) + r')\s*(!?==?~?)\s*["\']([^"\']+)["\']',
    re.IGNORECASE
)

# Pattern to extract numeric equality comparisons: EventID == 4625, RecordType == 15
# Applies to numeric fields like EventID and RecordType
FILTER_NUMERIC_PATTERN = re.compile(
    r'\b(EventID|RecordType)\s*(!?==?)\s*(\d+)',
    re.IGNORECASE
)

# Pattern to extract 'in' operator with literal list: field in ("val1", "val2", ...)
# Also handles in~, !in, !in~ for case-insensitive and negative matching
FILTER_IN_LITERAL_PATTERN = re.compile(
    r'\b(' + '|'.join(FILTER_FIELDS.keys()) + r')\s+(!?in~?)\s*\(([^)]+)\)',
    re.IGNORECASE
)

# String operators for all string-based filter fields
# Pattern: field has "value", field !has "value", field contains "value", etc.
# Operators: has, has_cs, has_any, has_all, contains, contains_cs, startswith, startswith_cs, 
#            endswith, endswith_cs, matches regex
# Also handles negative operators: !has, !has_cs, !contains, !contains_cs, !startswith, !endswith
FILTER_STRING_OP_PATTERN = re.compile(
    r'\b(' + '|'.join(STRING_OPERATOR_FIELDS) + r')\s+'
    r'(!?(?:has_all|has_any|has_cs|has|contains_cs|contains|startswith_cs|startswith|endswith_cs|endswith|matches\s+regex))\s*'
    r'[\(\s]*["\']([^"\']+)["\']',
    re.IGNORECASE
)

# Pattern for has_all and has_any with multiple values: field has_all ('val1', 'val2', ...)
FILTER_STRING_MULTI_OP_PATTERN = re.compile(
    r'\b(' + '|'.join(STRING_OPERATOR_FIELDS) + r')\s+'
    r'(!?(?:has_all|has_any))\s*\(([^)]+)\)',
    re.IGNORECASE
)

# Tables that use vendor/product fields for source identification
VENDOR_PRODUCT_TABLES = {
    'commonsecuritylog': ('DeviceVendor', 'DeviceProduct'),
}

# Folders in the Solutions directory that should be excluded (not actual solutions)
EXCLUDED_SOLUTION_FOLDERS = {
    'images',       # Contains logo images only
    'templates',    # Contains solution templates
    'training',     # Training materials
}

# Content-only connectors that don't actually ingest data
# These provide analytics content/hunting capabilities using data from other connectors
# They should be excluded from ASIM parser/content item association
CONTENT_ONLY_CONNECTORS = {
    'cyborgsecurity_hunter',  # Cyborg Security HUNTER - provides hunting content, uses SecurityEvent from Windows Security Events
}

# Connectors whose sample queries reference other tables for JOIN examples
# These should only match parsers for their primary table, not the joined tables
# Format: connector_id (lowercase) -> set of table names to EXCLUDE from matching
CONNECTOR_EXCLUDE_TABLES = {
    'threatintelligence': {'commonsecuritylog', 'signinlogs'},  # Sample queries show JOIN examples with these tables
}

# ASim tables use EventVendor/EventProduct
ASIM_TABLE_PREFIXES = ('asim', '_asim', '_im_')

# Global log file handle (set in main())
_log_file = None
_log_start_time = None


def log_print(message: str, end: str = "\n") -> None:
    """
    Print a message to both console and log file with timestamp.
    
    Args:
        message: The message to print
        end: String to append at the end (default: newline)
    """
    global _log_file, _log_start_time
    
    # Calculate elapsed time
    if _log_start_time:
        elapsed = datetime.now() - _log_start_time
        elapsed_str = f"[{elapsed.total_seconds():7.1f}s]"
    else:
        elapsed_str = "[       ]"
    
    # Format the timestamped message
    timestamped_message = f"{elapsed_str} {message}"
    
    # Print to console
    print(timestamped_message, end=end)
    
    # Write to log file if available
    if _log_file:
        _log_file.write(timestamped_message + end)
        _log_file.flush()  # Ensure immediate write


def init_logging(log_path: Path) -> None:
    """
    Initialize logging to a file.
    
    Args:
        log_path: Path to the log file
    """
    global _log_file, _log_start_time
    _log_start_time = datetime.now()
    try:
        _log_file = log_path.open("w", encoding="utf-8")
        log_print(f"Log started at {_log_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        log_print(f"Log file: {log_path}")
    except Exception as e:
        print(f"Warning: Could not create log file {log_path}: {e}")
        _log_file = None


def close_logging() -> None:
    """Close the log file."""
    global _log_file
    if _log_file:
        log_print(f"Log ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        _log_file.close()
        _log_file = None


# =============================================================================
# File Analysis Caching Infrastructure
# =============================================================================

# Global cache storage
_file_analysis_cache: Dict[str, Dict[str, Any]] = {}
_cache_path: Optional[Path] = None
_force_refresh_types: Set[str] = set()

# Analysis types that can be cached
# Offline types (no network access needed): asim, parsers, solutions, standalone
# Online types (require network access): marketplace, tables
ANALYSIS_TYPES = {
    "asim": "ASIM parser analysis",
    "parsers": "Non-ASIM parser analysis",
    "solutions": "Solution content analysis",
    "standalone": "Standalone content item analysis",
    "marketplace": "Marketplace availability check",
    "tables": "Table reference info from Microsoft docs",
}

# Analysis types that require network access
ONLINE_ANALYSIS_TYPES = {"marketplace", "tables"}


def init_cache(cache_dir: Path, force_refresh: str = "") -> None:
    """
    Initialize the file analysis cache.
    
    Args:
        cache_dir: Directory to store cache files
        force_refresh: Comma-separated list of analysis types to force refresh
                       (e.g., "asim,parsers", "all" to refresh everything,
                       or "all-offline" to refresh all except network-dependent types)
    """
    global _file_analysis_cache, _cache_path, _force_refresh_types
    
    cache_dir.mkdir(parents=True, exist_ok=True)
    _cache_path = cache_dir / "file_analysis_cache.json"
    
    # Parse force-refresh types
    if force_refresh:
        force_refresh_lower = force_refresh.lower()
        if force_refresh_lower == "all":
            _force_refresh_types = set(ANALYSIS_TYPES.keys())
        elif force_refresh_lower == "all-offline":
            # Refresh all types except those requiring network access
            _force_refresh_types = set(ANALYSIS_TYPES.keys()) - ONLINE_ANALYSIS_TYPES
        else:
            _force_refresh_types = {t.strip().lower() for t in force_refresh.split(",")}
            invalid_types = _force_refresh_types - set(ANALYSIS_TYPES.keys())
            if invalid_types:
                log_print(f"Warning: Unknown analysis types for force-refresh: {invalid_types}")
                log_print(f"  Valid types: {', '.join(ANALYSIS_TYPES.keys())}")
            _force_refresh_types = _force_refresh_types & set(ANALYSIS_TYPES.keys())
    
    # Load existing cache
    if _cache_path.exists() and not _force_refresh_types:
        try:
            with _cache_path.open("r", encoding="utf-8") as f:
                _file_analysis_cache = json.load(f)
            log_print(f"Loaded analysis cache with {len(_file_analysis_cache)} entries")
        except Exception as e:
            log_print(f"Warning: Could not load cache file: {e}")
            _file_analysis_cache = {}
    elif _force_refresh_types:
        # Load cache but mark specific types for refresh
        if _cache_path.exists():
            try:
                with _cache_path.open("r", encoding="utf-8") as f:
                    _file_analysis_cache = json.load(f)
                # Remove entries for force-refreshed types
                keys_to_remove = []
                for key in _file_analysis_cache:
                    if _file_analysis_cache[key].get("analysis_type") in _force_refresh_types:
                        keys_to_remove.append(key)
                for key in keys_to_remove:
                    del _file_analysis_cache[key]
                log_print(f"Force-refreshing analysis types: {', '.join(_force_refresh_types)}")
                log_print(f"  Removed {len(keys_to_remove)} cached entries, {len(_file_analysis_cache)} remaining")
            except Exception:
                _file_analysis_cache = {}
        else:
            _file_analysis_cache = {}
        
        # If 'tables' is being refreshed, also clear the collect_table_info cache files and re-run collection
        if "tables" in _force_refresh_types:
            _run_collect_table_info(cache_dir)


def _run_collect_table_info(cache_dir: Path) -> None:
    """Run collect_table_info.py to refresh table reference data.
    
    This clears the cache files and re-runs the collection script to get fresh data.
    """
    script_dir = Path(__file__).parent
    collect_script = script_dir / "collect_table_info.py"
    
    if not collect_script.exists():
        log_print(f"  Warning: collect_table_info.py not found at {collect_script}")
        return
    
    log_print(f"  Running collect_table_info.py to refresh table reference data...")
    
    try:
        # Run the collect_table_info.py script with --refresh-cache
        result = subprocess.run(
            [sys.executable, str(collect_script), "--refresh-cache", "--cache-dir", str(cache_dir)],
            capture_output=True,
            text=True,
            cwd=str(script_dir)
        )
        
        if result.returncode == 0:
            # Count lines in output for summary
            output_lines = [line for line in result.stdout.strip().split('\n') if line]
            log_print(f"  collect_table_info.py completed successfully")
            # Print key output lines (skip verbose details)
            for line in output_lines:
                if 'Wrote' in line or 'Total unique tables' in line:
                    log_print(f"    {line.strip()}")
        else:
            log_print(f"  Warning: collect_table_info.py returned non-zero exit code: {result.returncode}")
            if result.stderr:
                log_print(f"    Error: {result.stderr[:500]}")
    except Exception as e:
        log_print(f"  Warning: Failed to run collect_table_info.py: {e}")


def _clear_table_info_cache(cache_dir: Path) -> None:
    """Clear the collect_table_info.py cache files (.cache and .meta files)."""
    if not cache_dir.exists():
        return
    
    count = 0
    for cache_file in cache_dir.glob('*.cache'):
        try:
            cache_file.unlink()
            count += 1
        except IOError:
            pass
    
    for meta_file in cache_dir.glob('*.meta'):
        try:
            meta_file.unlink()
        except IOError:
            pass
    
    if count > 0:
        log_print(f"  Cleared {count} table info cache files")


def save_cache() -> None:
    """Save the file analysis cache to disk."""
    global _file_analysis_cache, _cache_path
    
    if _cache_path:
        try:
            with _cache_path.open("w", encoding="utf-8") as f:
                json.dump(_file_analysis_cache, f, indent=2, default=str)
            log_print(f"Saved analysis cache with {len(_file_analysis_cache)} entries")
        except Exception as e:
            log_print(f"Warning: Could not save cache file: {e}")


def get_file_mtime(file_path: Path) -> float:
    """Get file modification time as a timestamp."""
    try:
        return file_path.stat().st_mtime
    except Exception:
        return 0.0


def get_cached_analysis(file_path: Path, analysis_type: str) -> Optional[Dict[str, Any]]:
    """
    Get cached analysis result for a file if it's still valid.
    
    Args:
        file_path: Path to the file
        analysis_type: Type of analysis (e.g., "asim", "parsers", "solutions")
    
    Returns:
        Cached analysis result dict, or None if cache is invalid/missing
    """
    global _file_analysis_cache, _force_refresh_types
    
    # If this type is being force-refreshed, always return None
    if analysis_type in _force_refresh_types:
        return None
    
    cache_key = f"{analysis_type}:{file_path}"
    
    if cache_key not in _file_analysis_cache:
        return None
    
    cached = _file_analysis_cache[cache_key]
    cached_mtime = cached.get("file_mtime", 0)
    current_mtime = get_file_mtime(file_path)
    
    # If file was modified, cache is invalid
    if current_mtime > cached_mtime:
        return None
    
    return cached.get("result")


def set_cached_analysis(file_path: Path, analysis_type: str, result: Dict[str, Any]) -> None:
    """
    Cache analysis result for a file.
    
    Args:
        file_path: Path to the file
        analysis_type: Type of analysis (e.g., "asim", "parsers", "solutions")
        result: Analysis result to cache
    """
    global _file_analysis_cache
    
    cache_key = f"{analysis_type}:{file_path}"
    _file_analysis_cache[cache_key] = {
        "file_path": str(file_path),
        "analysis_type": analysis_type,
        "file_mtime": get_file_mtime(file_path),
        "cached_at": datetime.now().isoformat(),
        "result": result,
    }


def extract_let_block_for_table(query: str, table_name: str) -> Optional[str]:
    """
    Extract the let statement block that directly references a specific table.
    
    For ASIM parsers, filters like Facility and ProcessName are in the let block
    that references Syslog directly, not in subsequent blocks that reference
    the let variable.
    
    Example:
        let SyslogParsed = (
            Syslog
            | where Facility == "authpriv"  <- This is the relevant filter
            | where ProcessName in (...)
        );
        
        SyslogParsed
        | where SyslogMessage startswith "..."  <- This is parsing, not filtering
    
    Args:
        query: The full KQL query string
        table_name: The table name to find (e.g., "Syslog")
    
    Returns:
        The let statement block containing the table, or None if not found
    """
    if not query or not table_name:
        return None
    
    table_lower = table_name.lower()
    
    # Pattern to match let statements: let varname = (...) or let varname = {...}
    # We need to find the one that directly references our table
    let_pattern = re.compile(
        r'let\s+(\w+)\s*=\s*[\(\{]',
        re.IGNORECASE
    )
    
    for match in let_pattern.finditer(query):
        start_pos = match.end() - 1  # Position of opening ( or {
        open_char = query[start_pos]
        close_char = ')' if open_char == '(' else '}'
        
        # Find the matching closing bracket
        depth = 1
        pos = start_pos + 1
        while pos < len(query) and depth > 0:
            if query[pos] == open_char:
                depth += 1
            elif query[pos] == close_char:
                depth -= 1
            pos += 1
        
        if depth == 0:
            # Extract the block content
            block_content = query[start_pos + 1:pos - 1]
            
            # Check if this block directly references our table
            # The table should appear at the beginning of a line or after a newline/whitespace
            # Pattern: start of block or newline, then optional whitespace, then table name
            table_pattern = re.compile(
                r'(?:^|\n)\s*' + re.escape(table_name) + r'\b',
                re.IGNORECASE
            )
            if table_pattern.search(block_content):
                return block_content
    
    return None


def extract_vendor_product_from_query(query: str, table_name: Optional[str] = None) -> Dict[str, Set[str]]:
    """
    Extract DeviceVendor/DeviceProduct or EventVendor/EventProduct values from a KQL query.
    
    Args:
        query: The KQL query string to parse
        table_name: Optional table name to help determine which fields to look for
    
    Returns:
        Dictionary with keys 'vendor' and 'product', each containing a set of found values
    """
    if not query:
        return {'vendor': set(), 'product': set()}
    
    result = {'vendor': set(), 'product': set()}
    
    # Find all matches
    for match in VENDOR_PRODUCT_PATTERN.finditer(query):
        field_name = match.group(1).lower()
        value = match.group(2).strip()
        
        if not value:
            continue
        
        if field_name in ('devicevendor', 'eventvendor'):
            result['vendor'].add(value)
        elif field_name in ('deviceproduct', 'eventproduct'):
            result['product'].add(value)
    
    return result


def extract_filter_fields_from_query(query: str, tables_in_query: Optional[Set[str]] = None, 
                                       skip_asim_vendor_product: bool = False,
                                       limit_to_table_let_block: Optional[str] = None) -> Dict[str, Dict[str, List[Tuple[str, str]]]]:
    """
    Extract filter field values from a KQL query for identifying data sources.
    
    Supports:
    - Equality operators: field == "value", field =~ "value", field = "value"
    - Negative operators: field != "value", field !in (...)
    - In operator with literal list: field in ("val1", "val2")
    - In operator with case-insensitive: field in~ ("val1", "val2")
    - String operators for Syslog: has, has_any, has_all, contains, startswith, endswith
    - Negative string operators: !has, !contains, !startswith, !endswith
    
    Args:
        query: The KQL query string to parse
        tables_in_query: Optional set of table names found in the query (for context)
        skip_asim_vendor_product: If True, skip extraction of EventVendor/EventProduct
                                   (useful for ASIM parsers which SET rather than filter on these)
        limit_to_table_let_block: If provided, only extract from the let statement that
                                   directly references this table (useful for ASIM parsers
                                   where Syslog filters are in one let block and SyslogMessage
                                   parsing patterns are in subsequent union blocks)
    
    Returns:
        Dict mapping table name -> { field_name -> list of (operator, value) tuples }
        Table name is inferred from the field or marked as 'Unknown' if ambiguous
    
    Example output:
        {
            'CommonSecurityLog': {'DeviceVendor': [('==', 'Palo Alto Networks')]},
            'Syslog': {'Facility': [('==', 'authpriv')], 'SyslogMessage': [('has', 'error'), ('contains', 'warning')]},
        }
    """
    if not query:
        return {}
    
    # If limit_to_table_let_block is specified, extract and use only that block
    # This is useful for ASIM parsers where filters like Facility are in the let block
    # that references Syslog directly, not in subsequent parsing blocks
    effective_query = query
    if limit_to_table_let_block:
        let_block = extract_let_block_for_table(query, limit_to_table_let_block)
        if let_block:
            effective_query = let_block
        # If no let block found, continue with full query
    
    result: Dict[str, Dict[str, List[Tuple[str, str]]]] = {}
    tables_lower = {t.lower() for t in (tables_in_query or set())}
    
    # Extract tables that appear in THIS specific query (not from all queries in connector)
    # This helps disambiguate when multiple queries reference different MDE tables
    local_tables: Set[str] = set()
    local_table_pattern = re.compile(r'^\s*(\w+)\s*[\|\n]', re.MULTILINE)
    for match in local_table_pattern.finditer(effective_query):
        potential_table = match.group(1)
        if potential_table.lower() not in ('let', 'union', 'print', 'range', 'datatable', 'where', 'project', 'extend', 'summarize'):
            local_tables.add(potential_table)
    # Also check for union members: union Table1, Table2
    union_pattern = re.compile(r'\bunion\s+([A-Za-z_][A-Za-z0-9_]*(?:\s*,\s*[A-Za-z_][A-Za-z0-9_]*)*)', re.IGNORECASE)
    for match in union_pattern.finditer(effective_query):
        for tbl in match.group(1).split(','):
            tbl = tbl.strip()
            if tbl and tbl.lower() not in ('let', 'union', 'print', 'range', 'datatable'):
                local_tables.add(tbl)
    local_tables_lower = {t.lower() for t in local_tables}
    
    def add_filter_value(field_name: str, operator: str, value: str) -> None:
        """Helper to add a filter value with operator to the result dict."""
        if not value.strip():
            return
        
        value = value.strip()
        
        # Skip workbook parameter placeholders like {DeviceProduct}, {TypeTimeChart}
        if value.startswith('{') and value.endswith('}'):
            return  # This is a workbook parameter, not a literal value
        
        field_lower = field_name.lower()
        
        # Determine the table this filter applies to
        table_name = None
        
        # DeviceVendor/DeviceProduct/DeviceEventClassID -> CommonSecurityLog
        if field_lower in ('devicevendor', 'deviceproduct', 'deviceeventclassid'):
            table_name = 'CommonSecurityLog'
        # EventVendor/EventProduct -> look for ASIM tables
        # Skip if skip_asim_vendor_product is True (ASIM parsers SET these, not filter on them)
        elif field_lower in ('eventvendor', 'eventproduct'):
            if skip_asim_vendor_product:
                return  # Skip - ASIM parsers SET these values, not filter on them
            # Check if query references known ASIM tables - REQUIRE an actual ASIM table
            for t in (tables_in_query or set()):  # Use original case
                if t.lower().startswith(ASIM_TABLE_PREFIXES):
                    table_name = t  # Use the original case from the query
                    break
            if not table_name:
                return  # Skip - no ASIM table found, likely a SET not a filter
        # ResourceType/Category -> AzureDiagnostics (only if AzureDiagnostics is in the query)
        elif field_lower == 'resourcetype':
            # ResourceType is fairly specific to AzureDiagnostics
            if 'azurediagnostics' in tables_lower:
                table_name = 'AzureDiagnostics'
            else:
                return  # Skip - ResourceType without AzureDiagnostics context is likely unrelated
        elif field_lower == 'category':
            # Category is a common field name - only attribute to AzureDiagnostics if that table is present
            if 'azurediagnostics' in tables_lower:
                table_name = 'AzureDiagnostics'
            else:
                return  # Skip - generic "category" field is not what we're looking for
        # EventID -> WindowsEvent or SecurityEvent (check which is in query)
        elif field_lower == 'eventid':
            if 'windowsevent' in tables_lower:
                table_name = 'WindowsEvent'
            elif 'securityevent' in tables_lower:
                table_name = 'SecurityEvent'
            elif 'event' in tables_lower:
                table_name = 'Event'
            else:
                # Skip - EventID without a known Windows event table context
                return
        # Source -> Event table (e.g., Source == "Service Control Manager")
        elif field_lower == 'source':
            if 'event' in tables_lower:
                table_name = 'Event'
            else:
                return  # Skip - Source without Event table context
        # EventLog -> Event table (e.g., EventLog == "MSExchange Management")
        elif field_lower == 'eventlog':
            if 'event' in tables_lower:
                table_name = 'Event'
            else:
                return  # Skip - EventLog without Event table context
        # Provider -> WindowsEvent table
        elif field_lower == 'provider':
            if 'windowsevent' in tables_lower:
                table_name = 'WindowsEvent'
            else:
                return  # Skip - Provider without WindowsEvent table context
        # Syslog fields
        elif field_lower in ('facility', 'processname', 'processid', 'syslogmessage'):
            if 'syslog' in tables_lower:
                table_name = 'Syslog'
            else:
                return  # Skip - Syslog field without Syslog table context
        # AWSCloudTrail fields
        elif field_lower == 'eventname':
            if 'awscloudtrail' in tables_lower:
                table_name = 'AWSCloudTrail'
            else:
                return  # Skip - EventName without AWSCloudTrail table context
        # ASIM EventType field
        elif field_lower == 'eventtype':
            # EventType is used in ASIM tables - check for ASIM tables in query
            for t in (tables_in_query or set()):
                if t.lower().startswith(ASIM_TABLE_PREFIXES):
                    table_name = t
                    break
            if not table_name:
                return  # Skip - EventType without ASIM table context
        # AzureActivity / AzureDiagnostics fields (ResourceProvider is used in both)
        elif field_lower == 'resourceprovider':
            # ResourceProvider is used in both AzureDiagnostics (e.g., "MICROSOFT.BATCH") 
            # and AzureActivity (e.g., "Microsoft.Compute")
            if 'azurediagnostics' in tables_lower:
                table_name = 'AzureDiagnostics'
            elif 'azureactivity' in tables_lower:
                table_name = 'AzureActivity'
            else:
                return  # Skip - ResourceProvider without AzureDiagnostics or AzureActivity table context
        # Microsoft Defender XDR / MDE ActionType field
        elif field_lower == 'actiontype':
            # ActionType is used in Defender XDR tables (DeviceEvents, DeviceFileEvents, etc.)
            mde_tables = {'deviceevents', 'devicefileevents', 'deviceprocessevents', 'devicenetworkevents',
                          'deviceregistryevents', 'devicelogoninfo', 'deviceinfo', 'deviceimageloadevents',
                          'cloudappevents', 'alertevidence', 'alertinfo', 'emailevents', 'emailattachmentinfo',
                          'emailurlinfo', 'identitylogonevents', 'identityqueryevents', 'identitydirectoryevents'}
            # IMPORTANT: First check tables in THIS query, not all tables from all queries
            # This prevents misattributing filters when multiple queries reference different MDE tables
            for t in local_tables:
                if t.lower() in mde_tables:
                    table_name = t
                    break
            # Fall back to global tables only if no local match
            if not table_name:
                for t in (tables_in_query or set()):
                    if t.lower() in mde_tables:
                        table_name = t
                        break
            if not table_name:
                return  # Skip - ActionType without MDE/XDR table context
        # Office 365 / Microsoft 365 OperationName field
        elif field_lower == 'operationname':
            # OperationName appears in AuditLogs, AzureActivity, OfficeActivity, SigninLogs
            operation_tables = {'auditlogs', 'azureactivity', 'officeactivity', 'signinlogs', 
                                'aaborerrorlogs', 'aadnoninteractiveusersigninlogs', 'aadserviceprincipalsigninlogs',
                                'aadmanagedidentitysigninlogs', 'aadriskyusers', 'aadprovisioninglogs'}
            for t in (tables_in_query or set()):
                if t.lower() in operation_tables:
                    table_name = t
                    break
            if not table_name:
                return  # Skip - OperationName without matching table context
        # OfficeActivity fields
        elif field_lower == 'officeworkload':
            if 'officeactivity' in tables_lower:
                table_name = 'OfficeActivity'
            else:
                return  # Skip - OfficeWorkload without OfficeActivity table context
        elif field_lower == 'recordtype':
            if 'officeactivity' in tables_lower:
                table_name = 'OfficeActivity'
            else:
                return  # Skip - RecordType without OfficeActivity table context
        else:
            return  # Unknown field, skip
        
        # Normalize field name to proper casing
        field_proper = next((f for f in FILTER_FIELDS if f.lower() == field_lower), field_name)
        
        # Normalize operator (remove spaces, lowercase)
        op_normalized = operator.lower().replace(' ', '')
        
        if table_name not in result:
            result[table_name] = {}
        if field_proper not in result[table_name]:
            result[table_name][field_proper] = []
        
        # Add (operator, value) tuple if not already present
        entry = (op_normalized, value)
        if entry not in result[table_name][field_proper]:
            result[table_name][field_proper].append(entry)
    
    def parse_literal_values(values_str: str) -> List[str]:
        """Parse a comma-separated list of values, extracting quoted strings."""
        values = []
        # Match quoted strings (single or double quotes)
        quote_pattern = re.compile(r'["\']([^"\']*)["\']')
        for match in quote_pattern.finditer(values_str):
            val = match.group(1).strip()
            if val:
                values.append(val)
        return values
    
    def parse_numeric_values(values_str: str) -> List[str]:
        """Parse a comma-separated list of numeric values."""
        values = []
        # Match integers
        num_pattern = re.compile(r'(\d+)')
        for match in num_pattern.finditer(values_str):
            val = match.group(1).strip()
            if val:
                values.append(val)
        return values
    
    def is_in_extend_or_project(q: str, match_start: int) -> bool:
        """Check if a match position is preceded by extend or project on the same line."""
        line_start = q.rfind('\n', 0, match_start) + 1
        preceding_text = q[line_start:match_start].lower()
        # Check if 'extend' or 'project' appears after the last pipe on this line
        last_pipe = preceding_text.rfind('|')
        if last_pipe >= 0:
            after_pipe = preceding_text[last_pipe:]
        else:
            after_pipe = preceding_text
        return 'extend' in after_pipe or 'project' in after_pipe
    
    # Extract equality comparisons: field == "value", field =~ "value", field != "value"
    # But skip if this is an extend/project statement (setting a value, not filtering)
    for match in FILTER_EQUALITY_PATTERN.finditer(effective_query):
        field_name = match.group(1)
        operator = match.group(2)
        value = match.group(3).strip()
        
        # Skip if this is in an extend or project statement
        if is_in_extend_or_project(effective_query, match.start()):
            continue
        
        add_filter_value(field_name, operator, value)
    
    # Extract numeric equality comparisons: EventID == 4625, RecordType == 15
    for match in FILTER_NUMERIC_PATTERN.finditer(effective_query):
        field_name = match.group(1)  # EventID or RecordType
        operator = match.group(2)
        value = match.group(3).strip()
        add_filter_value(field_name, operator, value)
    
    # Extract 'in' operator with literal list: field in ("val1", "val2"), field !in (...)
    for match in FILTER_IN_LITERAL_PATTERN.finditer(effective_query):
        field_name = match.group(1)
        operator = match.group(2)  # 'in' or 'in~'
        values_str = match.group(3)
        
        # Check if this looks like literal values or a table/variable reference
        # Literal values: contain quotes like ("val1", "val2") or ('val1', 'val2')
        # Table/variable: no quotes, just an identifier like (TableName) or (variable)
        if '"' in values_str or "'" in values_str:
            # Parse literal values
            values = parse_literal_values(values_str)
            # Use 'in' as operator with all values comma-separated
            if values:
                add_filter_value(field_name, operator, ','.join(values))
        elif field_name.lower() in ('eventid', 'recordtype'):
            # EventID and RecordType can have numeric in-list: EventID in (4625, 4688), RecordType in (15, 25)
            values = parse_numeric_values(values_str)
            if values:
                add_filter_value(field_name, operator, ','.join(values))
        elif field_name.lower() == 'eventname':
            # EventName can reference a variable: EventName in~ (EventNameList)
            # Try to resolve the variable from let statements in the query
            var_name = values_str.strip()
            if var_name and var_name.isidentifier():
                # Look for let statement: let EventNameList = dynamic([...]);
                let_pattern = re.compile(
                    r'let\s+' + re.escape(var_name) + r'\s*=\s*dynamic\s*\(\s*\[([^\]]+)\]\s*\)',
                    re.IGNORECASE
                )
                let_match = let_pattern.search(effective_query)
                if let_match:
                    # Extract values from dynamic array
                    array_content = let_match.group(1)
                    values = parse_literal_values(array_content)
                    if values:
                        add_filter_value(field_name, operator, ','.join(values))
                else:
                    # Try alternative patterns:
                    # 1. let var = datatable(col:type) ["val1", "val2", ...]
                    datatable_pattern = re.compile(
                        r'let\s+' + re.escape(var_name) + r'\s*=\s*datatable\s*\([^)]*\)\s*\[([^\]]+)\]',
                        re.IGNORECASE | re.DOTALL
                    )
                    datatable_match = datatable_pattern.search(effective_query)
                    if datatable_match:
                        array_content = datatable_match.group(1)
                        values = parse_literal_values(array_content)
                        if values:
                            add_filter_value(field_name, operator, ','.join(values))
        # else: it's a table or variable reference we can't resolve, skip
    
    # Extract string operator patterns: SyslogMessage has "value", !has "value", etc.
    for match in FILTER_STRING_OP_PATTERN.finditer(effective_query):
        field_name = match.group(1)
        operator = match.group(2)
        value = match.group(3).strip()
        
        # Skip if this is in an extend or project statement
        if is_in_extend_or_project(effective_query, match.start()):
            continue
        
        add_filter_value(field_name, operator, value)
    
    # Extract has_all/has_any with multiple values: SyslogMessage has_all ('val1', 'val2', ...)
    for match in FILTER_STRING_MULTI_OP_PATTERN.finditer(effective_query):
        field_name = match.group(1)
        operator = match.group(2)  # 'has_all', 'has_any', '!has_all', '!has_any'
        values_str = match.group(3)
        
        # Skip if this is in an extend or project statement
        if is_in_extend_or_project(effective_query, match.start()):
            continue
        
        # Parse quoted values
        values = parse_literal_values(values_str)
        if values:
            # Use the operator with all values comma-separated
            add_filter_value(field_name, operator, ','.join(values))
    
    return result


def format_filter_fields(filter_data: Dict[str, Dict[str, List[Tuple[str, str]]]]) -> str:
    """
    Format filter field data into a unified string format.
    
    Folds multiple equality operators (==, =~) for the same table.field into a single
    'in' operator with comma-separated values for more compact output.
    
    Args:
        filter_data: Dict from extract_filter_fields_from_query()
                     Structure: {table_name: {field_name: [(operator, value), ...]}}
    
    Returns:
        String in format: table.field operator "value" | table.field in "val1,val2" | ...
        Equality operators are folded: multiple == become 'in', multiple =~ become 'in~'
    
    Example:
        Input with multiple ==: Category == "A", Category == "B", Category == "C"
        Output: AzureDiagnostics.Category in "A,B,C"
    """
    if not filter_data:
        return ""
    
    parts = []
    for table_name in sorted(filter_data.keys()):
        fields = filter_data[table_name]
        for field_name in sorted(fields.keys()):
            entries = fields[field_name]
            
            # Group entries by operator for folding
            # Operators that can be folded: == -> in, =~ -> in~
            equality_values = []      # For == operator
            equality_ci_values = []   # For =~ operator (case-insensitive)
            other_entries = []        # Other operators (has, contains, etc.)
            
            for operator, value in entries:
                op_lower = operator.lower()
                if op_lower == '==' or op_lower == '=':
                    equality_values.append(value)
                elif op_lower == '=~':
                    equality_ci_values.append(value)
                elif op_lower == 'in' and ',' in value:
                    # Already an 'in' with multiple values - merge into equality_values
                    equality_values.extend(value.split(','))
                elif op_lower == 'in~' and ',' in value:
                    # Already an 'in~' with multiple values - merge into equality_ci_values
                    equality_ci_values.extend(value.split(','))
                elif op_lower == 'in':
                    # Single value 'in' - treat as equality
                    equality_values.append(value)
                elif op_lower == 'in~':
                    # Single value 'in~' - treat as case-insensitive equality
                    equality_ci_values.append(value)
                else:
                    other_entries.append((operator, value))
            
            # Deduplicate: if a value exists in both case-sensitive and case-insensitive,
            # keep only the case-insensitive version (it's more permissive)
            equality_ci_set = set(equality_ci_values)
            equality_values = [v for v in equality_values if v not in equality_ci_set]
            
            # Format folded equality values (case-sensitive only, after dedup)
            if equality_values:
                # Deduplicate and sort
                unique_values = sorted(set(equality_values))
                if len(unique_values) == 1:
                    parts.append(f'{table_name}.{field_name} == "{unique_values[0]}"')
                else:
                    parts.append(f'{table_name}.{field_name} in "{",".join(unique_values)}"')
            
            # Format folded case-insensitive equality values
            if equality_ci_values:
                # Deduplicate and sort
                unique_values = sorted(set(equality_ci_values))
                if len(unique_values) == 1:
                    parts.append(f'{table_name}.{field_name} =~ "{unique_values[0]}"')
                else:
                    parts.append(f'{table_name}.{field_name} in~ "{",".join(unique_values)}"')
            
            # Optimize other_entries: for has_all, if one value set is a subset of another,
            # keep only the subset (more general filter)
            # E.g., has_all "A" and has_all "A,B" -> keep only has_all "A"
            optimized_entries = _optimize_string_op_entries(other_entries)
            
            # Format other operators (after optimization)
            for operator, value in sorted(optimized_entries, key=lambda x: (x[0], x[1])):
                parts.append(f'{table_name}.{field_name} {operator} "{value}"')
    
    return ' | '.join(parts)


def _optimize_string_op_entries(entries: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    Optimize string operator entries by removing redundant filters.
    
    For has_all: if one value set is a subset of another, keep only the subset
                 (the more general filter). E.g., has_all "A" subsumes has_all "A,B"
    For has_any: if one value set is a superset of another, keep only the superset
                 (the more general filter). E.g., has_any "A,B" subsumes has_any "A"
    For has/contains/startswith/endswith: if same value with different case sensitivity,
                 keep case-insensitive (e.g., keep 'has' over 'has_cs' for same value)
    """
    if not entries:
        return entries
    
    # Group by operator type
    has_all_entries = []
    has_any_entries = []
    has_entries = []      # case-insensitive
    has_cs_entries = []   # case-sensitive
    contains_entries = []
    contains_cs_entries = []
    startswith_entries = []
    startswith_cs_entries = []
    endswith_entries = []
    endswith_cs_entries = []
    other = []
    
    for op, val in entries:
        op_lower = op.lower()
        if op_lower == 'has_all':
            has_all_entries.append(val)
        elif op_lower == 'has_any':
            has_any_entries.append(val)
        elif op_lower == 'has':
            has_entries.append(val)
        elif op_lower == 'has_cs':
            has_cs_entries.append(val)
        elif op_lower == 'contains':
            contains_entries.append(val)
        elif op_lower == 'contains_cs':
            contains_cs_entries.append(val)
        elif op_lower == 'startswith':
            startswith_entries.append(val)
        elif op_lower == 'startswith_cs':
            startswith_cs_entries.append(val)
        elif op_lower == 'endswith':
            endswith_entries.append(val)
        elif op_lower == 'endswith_cs':
            endswith_cs_entries.append(val)
        else:
            other.append((op, val))
    
    result = []
    
    # Optimize has_all: keep only minimal subsets
    if has_all_entries:
        # Convert comma-separated values to sets
        value_sets = [set(v.split(',')) for v in has_all_entries]
        # Remove sets that are supersets of other sets
        minimal_sets = []
        for i, s in enumerate(value_sets):
            is_superset = False
            for j, other_s in enumerate(value_sets):
                if i != j and s > other_s:  # s is a proper superset of other_s
                    is_superset = True
                    break
            if not is_superset:
                minimal_sets.append(s)
        # Deduplicate and convert back
        seen = set()
        for s in minimal_sets:
            key = ','.join(sorted(s))
            if key not in seen:
                seen.add(key)
                result.append(('has_all', key))
    
    # Optimize has_any: keep only maximal supersets
    if has_any_entries:
        value_sets = [set(v.split(',')) for v in has_any_entries]
        maximal_sets = []
        for i, s in enumerate(value_sets):
            is_subset = False
            for j, other_s in enumerate(value_sets):
                if i != j and s < other_s:  # s is a proper subset of other_s
                    is_subset = True
                    break
            if not is_subset:
                maximal_sets.append(s)
        seen = set()
        for s in maximal_sets:
            key = ','.join(sorted(s))
            if key not in seen:
                seen.add(key)
                result.append(('has_any', key))
    
    # For has/has_cs: if same value exists in both, keep only case-insensitive
    has_set = set(has_entries)
    has_cs_filtered = [v for v in has_cs_entries if v not in has_set]
    for v in sorted(set(has_entries)):
        result.append(('has', v))
    for v in sorted(set(has_cs_filtered)):
        result.append(('has_cs', v))
    
    # Same for contains
    contains_set = set(contains_entries)
    contains_cs_filtered = [v for v in contains_cs_entries if v not in contains_set]
    for v in sorted(set(contains_entries)):
        result.append(('contains', v))
    for v in sorted(set(contains_cs_filtered)):
        result.append(('contains_cs', v))
    
    # Same for startswith
    startswith_set = set(startswith_entries)
    startswith_cs_filtered = [v for v in startswith_cs_entries if v not in startswith_set]
    for v in sorted(set(startswith_entries)):
        result.append(('startswith', v))
    for v in sorted(set(startswith_cs_filtered)):
        result.append(('startswith_cs', v))
    
    # Same for endswith
    endswith_set = set(endswith_entries)
    endswith_cs_filtered = [v for v in endswith_cs_entries if v not in endswith_set]
    for v in sorted(set(endswith_entries)):
        result.append(('endswith', v))
    for v in sorted(set(endswith_cs_filtered)):
        result.append(('endswith_cs', v))
    
    # Add remaining entries
    result.extend(other)
    
    return result


def get_filter_fields_by_table(queries: List[str], tables_in_queries: Optional[Set[str]] = None,
                                skip_asim_vendor_product: bool = False) -> Dict[str, Dict[str, List[Tuple[str, str]]]]:
    """
    Extract filter fields from multiple queries, aggregating by table.
    
    Args:
        queries: List of KQL query strings
        tables_in_queries: Optional set of all tables referenced in the queries
        skip_asim_vendor_product: If True, skip extraction of EventVendor/EventProduct
    
    Returns:
        Aggregated filter data across all queries
    """
    result: Dict[str, Dict[str, List[Tuple[str, str]]]] = {}
    
    for query in queries:
        filter_data = extract_filter_fields_from_query(query, tables_in_queries, skip_asim_vendor_product)
        for table_name, fields in filter_data.items():
            if table_name not in result:
                result[table_name] = {}
            for field_name, entries in fields.items():
                if field_name not in result[table_name]:
                    result[table_name][field_name] = []
                for entry in entries:
                    if entry not in result[table_name][field_name]:
                        result[table_name][field_name].append(entry)
    
    return result


def extract_all_queries_from_connector(data: Any) -> List[str]:
    """
    Extract all query strings from a connector JSON structure.
    Looks in graphQueries, sampleQueries, dataTypes, and connectivityCriterias.
    
    Args:
        data: The parsed connector JSON data
    
    Returns:
        List of query strings found in the connector definition
    """
    queries: List[str] = []
    
    if not isinstance(data, dict):
        return queries
    
    # graphQueries - contains baseQuery
    for gq in data.get('graphQueries', []):
        if isinstance(gq, dict):
            base_query = gq.get('baseQuery', '')
            if base_query:
                queries.append(base_query)
    
    # sampleQueries - contains query
    for sq in data.get('sampleQueries', []):
        if isinstance(sq, dict):
            query = sq.get('query', '')
            if query:
                queries.append(query)
    
    # dataTypes - contains lastDataReceivedQuery or query
    for dt in data.get('dataTypes', []):
        if isinstance(dt, dict):
            query = dt.get('lastDataReceivedQuery', '') or dt.get('query', '')
            if query:
                queries.append(query)
    
    # connectivityCriterias - contains value which can be a list of queries
    for cc in data.get('connectivityCriterias', []):
        if isinstance(cc, dict):
            value = cc.get('value', [])
            if isinstance(value, list):
                for v in value:
                    if isinstance(v, str) and v.strip():
                        queries.append(v)
            elif isinstance(value, str) and value.strip():
                queries.append(value)
    
    return queries


def get_connector_vendor_product(data: Any) -> Dict[str, Set[str]]:
    """
    Extract all vendor/product values from a connector's queries.
    
    Args:
        data: The parsed connector JSON data
    
    Returns:
        Dictionary with 'vendor' and 'product' sets containing all found values
    """
    result = {'vendor': set(), 'product': set()}
    
    queries = extract_all_queries_from_connector(data)
    for query in queries:
        vp = extract_vendor_product_from_query(query)
        result['vendor'].update(vp['vendor'])
        result['product'].update(vp['product'])
    
    return result


def get_connector_vendor_product_by_table(data: Any) -> Dict[str, Dict[str, Set[str]]]:
    """
    Extract vendor/product values from a connector's queries, grouped by table name.
    
    Args:
        data: The parsed connector JSON data
    
    Returns:
        Dictionary mapping table names to their vendor/product values.
        Example: {'CommonSecurityLog': {'vendor': {'Cisco'}, 'product': {'ASA'}}}
    """
    result: Dict[str, Dict[str, Set[str]]] = {}
    
    queries = extract_all_queries_from_connector(data)
    
    # Pattern to extract table name from query (first table-like identifier after FROM or at the start)
    # This handles: "TableName | where ...", "TableName\n| where ...", etc.
    table_pattern = re.compile(r'^\s*(\w+)\s*[\|\n]', re.MULTILINE)
    
    for query in queries:
        # Try to extract the table name from the query
        table_match = table_pattern.search(query)
        if table_match:
            table_name = table_match.group(1)
            
            # Skip if it looks like a KQL keyword
            if table_name.lower() in ('let', 'union', 'print', 'range', 'datatable'):
                continue
            
            # Extract vendor/product from this query
            vp = extract_vendor_product_from_query(query)
            
            if vp['vendor'] or vp['product']:
                if table_name not in result:
                    result[table_name] = {'vendor': set(), 'product': set()}
                result[table_name]['vendor'].update(vp['vendor'])
                result[table_name]['product'].update(vp['product'])
    
    return result


def get_connector_filter_fields(data: Any, known_tables: Optional[Set[str]] = None) -> Dict[str, Dict[str, Set[str]]]:
    """
    Extract all filter fields from a connector's queries.
    
    This is the comprehensive replacement for get_connector_vendor_product,
    extracting not just DeviceVendor/DeviceProduct but also:
    - EventVendor/EventProduct (for ASIM)
    - ResourceType/Category (for AzureDiagnostics)
    - EventID (for WindowsEvent/SecurityEvent)
    
    Args:
        data: The parsed connector JSON data
        known_tables: Optional set of tables the connector is known to use (e.g., from table mappings).
                      This helps when queries use parser functions instead of direct table references.
    
    Returns:
        Aggregated filter data: Dict[table_name][field_name] = set of values
    """
    queries = extract_all_queries_from_connector(data)
    
    # First pass: identify all tables in all queries
    all_tables: Set[str] = set()
    table_pattern = re.compile(r'^\s*(\w+)\s*[\|\n]', re.MULTILINE)
    for query in queries:
        table_match = table_pattern.search(query)
        if table_match:
            table_name = table_match.group(1)
            if table_name.lower() not in ('let', 'union', 'print', 'range', 'datatable'):
                all_tables.add(table_name)
    
    # Include known tables from table mappings (helps when queries use parser functions)
    if known_tables:
        all_tables.update(known_tables)
    
    # Second pass: extract filter fields with table context
    return get_filter_fields_by_table(queries, all_tables)


def parse_filter_fields_string(filter_fields_str: str) -> Dict[str, Dict[str, Set[str]]]:
    """
    Parse a filter_fields string back into a structured format.
    
    Args:
        filter_fields_str: String in format "Table.Field operator \"value\" | ..."
        
    Returns:
        Structured dict: {table_name: {field_name: set of values}}
        Note: Operators are ignored - only table, field, and values are extracted.
    """
    result: Dict[str, Dict[str, Set[str]]] = {}
    
    if not filter_fields_str:
        return result
    
    # Split by ' | ' separator
    parts = filter_fields_str.split(' | ')
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # Extract Table.Field from the beginning
        # Pattern: Table.Field operator "value" or Table.Field operator "val1,val2"
        # Find first space which separates Table.Field from operator
        space_idx = part.find(' ')
        if space_idx <= 0:
            continue
        
        table_field = part[:space_idx]
        if '.' not in table_field:
            continue
        
        dot_idx = table_field.find('.')
        table_name = table_field[:dot_idx]
        field_name = table_field[dot_idx + 1:]
        
        if not table_name or not field_name:
            continue
        
        # Normalize table name to lowercase for comparison
        table_name_lower = table_name.lower()
        
        # Extract value(s) from quotes
        # Look for "..." pattern
        quote_pattern = re.compile(r'"([^"]+)"')
        quote_match = quote_pattern.search(part)
        if not quote_match:
            continue
        
        values_str = quote_match.group(1)
        
        # Split comma-separated values
        values = [v.strip() for v in values_str.split(',') if v.strip()]
        
        # Add to result
        if table_name_lower not in result:
            result[table_name_lower] = {}
        if field_name not in result[table_name_lower]:
            result[table_name_lower][field_name] = set()
        result[table_name_lower][field_name].update(values)
    
    return result


def is_filter_subset(connector_filters: Dict[str, Dict[str, Set[str]]], 
                     target_filters: Dict[str, Dict[str, Set[str]]],
                     shared_tables: Set[str]) -> bool:
    """
    Check if connector filters are a subset of target filters for shared tables.
    
    A connector matches a target (parser/content) if for each shared table:
    - All connector filter field values are contained within the target's filter values
    - If the connector filters on a field that the target doesn't filter on, no match
      (the target expects different data than what the connector provides)
    
    Args:
        connector_filters: Parsed filter fields from connector
        target_filters: Parsed filter fields from parser/content item
        shared_tables: Set of table names shared between connector and target (lowercase)
        
    Returns:
        True if connector filters are a subset (or equal) to target filters for shared tables
    """
    if not shared_tables:
        return False
    
    # For each shared table, check if connector filters are subset of target filters
    for table in shared_tables:
        conn_table_filters = connector_filters.get(table, {})
        target_table_filters = target_filters.get(table, {})
        
        # If connector has no filters for this table, that's fine (matches all)
        if not conn_table_filters:
            continue
        
        # Check each field the connector filters on
        for field_name, conn_values in conn_table_filters.items():
            target_values = target_table_filters.get(field_name, set())
            
            # If target doesn't filter on this field, the connector's filter is orthogonal
            # to the target's expectations - no match (they're looking for different data)
            if not target_values:
                return False
            
            # Connector values must be a subset of target values
            # Case-insensitive comparison for string values
            conn_values_lower = {v.lower() for v in conn_values}
            target_values_lower = {v.lower() for v in target_values}
            
            if not conn_values_lower.issubset(target_values_lower):
                return False
    
    return True


def find_matching_connectors(target_tables: Set[str], 
                              target_filter_fields_str: str,
                              connectors_data: List[Dict[str, Any]],
                              connector_tables_map: Dict[str, List[str]] = None) -> List[Tuple[str, str, str]]:
    """
    Find connectors that match a target (parser/content item) based on shared tables and filters.
    
    A connector matches if:
    1. It shares at least one table with the target
    2. For shared tables, the connector's filter values are a subset of (or equal to) the target's filter values
       (A connector with no filter fields matches any target using the same table)
    
    Args:
        target_tables: Set of table names used by the target (lowercase normalized)
        target_filter_fields_str: Filter fields string from the target
        connectors_data: List of connector dictionaries with 'connector_id', 'filter_fields', etc.
        connector_tables_map: Optional mapping of connector_id -> list of table names
        
    Returns:
        List of (connector_id, connector_title, solution_name) tuples for matching connectors
    """
    matches: List[Tuple[str, str, str]] = []
    
    if not target_tables:
        return matches
    
    if connector_tables_map is None:
        connector_tables_map = {}
    
    # Parse target filters
    target_filters = parse_filter_fields_string(target_filter_fields_str)
    
    # Normalize target tables to lowercase
    target_tables_lower = {t.lower() for t in target_tables}
    
    for connector in connectors_data:
        connector_id = connector.get('connector_id', '')
        connector_title = connector.get('connector_title', '')
        solution_name = connector.get('solution_name', '')
        
        # Skip deprecated connectors
        if connector.get('is_deprecated', '').lower() == 'true':
            continue
        
        # Skip content-only connectors (they use data from other connectors, not ingest it)
        if connector_id.lower() in CONTENT_ONLY_CONNECTORS:
            continue
        
        # Parse connector filter fields to find tables
        conn_filter_str = connector.get('filter_fields', '')
        conn_filters = parse_filter_fields_string(conn_filter_str)
        
        # Get connector tables - try multiple sources:
        # 1. From filter_fields (tables are the keys)
        # 2. From event_vendor_product_by_table
        # 3. From connector_tables_map (main mapping data)
        conn_tables = set(conn_filters.keys())
        
        # If connector has no filter fields, check if we can infer tables from event_vendor_product_by_table
        if not conn_tables:
            evp_by_table = connector.get('event_vendor_product_by_table', '')
            if evp_by_table:
                for part in evp_by_table.split(' | '):
                    if ':' in part:
                        table = part.split(':')[0].strip().lower()
                        if table:
                            conn_tables.add(table)
        
        # If still no tables, get from connector_tables_map
        if not conn_tables:
            mapping_tables = connector_tables_map.get(connector_id, [])
            conn_tables = {t.lower() for t in mapping_tables}
        
        if not conn_tables:
            continue
        
        # Exclude tables that are only referenced in JOIN examples (not actual ingested tables)
        excluded_tables = CONNECTOR_EXCLUDE_TABLES.get(connector_id.lower(), set())
        conn_tables = conn_tables - excluded_tables
        
        if not conn_tables:
            continue
        
        # Check for shared tables
        shared_tables = target_tables_lower & conn_tables
        
        if not shared_tables:
            continue
        
        # Check if connector filters are subset of target filters
        # Note: A connector with no filters matches any target (it provides all data from the table)
        if is_filter_subset(conn_filters, target_filters, shared_tables):
            matches.append((connector_id, connector_title, solution_name))
    
    return matches


def associate_connectors_to_items(
    items: List[Dict[str, Any]],
    connectors_data: List[Dict[str, Any]],
    connector_tables_map: Dict[str, List[str]] = None,
    tables_key: str = 'tables',
    filter_fields_key: str = 'filter_fields',
    item_type_name: str = 'items',
    name_key: str = 'parser_name',
    connector_assoc_overrides: List[ConnectorAssociationOverride] = None,
) -> None:
    """
    Associate connectors to items (ASIM parsers or content items) based on shared tables and filters.
    
    Adds 'associated_connectors' and 'associated_solutions' fields to each item.
    
    Args:
        items: List of item dictionaries (ASIM parsers or content items)
        connectors_data: List of connector dictionaries
        connector_tables_map: Optional mapping of connector_id -> list of table names
        tables_key: Key name for tables field in items
        filter_fields_key: Key name for filter fields in items
        item_type_name: Name for progress display (e.g., 'ASIM parsers', 'content items')
        name_key: Key name for item name (for override matching)
        connector_assoc_overrides: List of connector association overrides
    """
    if connector_tables_map is None:
        connector_tables_map = {}
    if connector_assoc_overrides is None:
        connector_assoc_overrides = []
    
    total_items = len(items)
    for idx, item in enumerate(items, 1):
        # Progress heartbeat every 500 items or at start
        if idx == 1 or idx % 500 == 0:
            log_print(f"    Processing {item_type_name}: {idx}/{total_items}...")
        # Get tables for this item
        tables_str = item.get(tables_key, '')
        if isinstance(tables_str, str):
            tables = {t.strip().lower() for t in tables_str.split(',') if t.strip()}
        elif isinstance(tables_str, (list, set)):
            tables = {str(t).lower() for t in tables_str}
        else:
            tables = set()
        
        # Get item name for override matching
        item_name = item.get(name_key, '')
        
        # Check for connector association overrides first
        override_result = apply_connector_association_override(tables, item_name, connector_assoc_overrides)
        if override_result:
            # Apply the override - use the forced connector and solution
            connector_id, solution_name = override_result
            item['associated_connectors'] = connector_id
            item['associated_solutions'] = solution_name if solution_name else ''
            continue
        
        # Get filter fields for this item
        filter_fields_str = item.get(filter_fields_key, '')
        
        # Find matching connectors
        matches = find_matching_connectors(tables, filter_fields_str, connectors_data, connector_tables_map)
        
        # Extract unique connector IDs and solution names
        connector_ids = sorted(set(m[0] for m in matches))
        solution_names = sorted(set(m[2] for m in matches if m[2]))
        
        # Add to item
        item['associated_connectors'] = ', '.join(connector_ids)
        item['associated_solutions'] = ', '.join(solution_names)


# Token validation sets
PARSER_NAME_KEYS = {"functionname", "functionalias"}

# Minimal blocklist - only tokens that could cause specific issues
# Most validation is now done via whitelist (tables_reference.csv) + _CL suffix check
BLOCKED_TOKENS = {
    # Incomplete or invalid _CL patterns
    "_cl",
    "_indicators_cl",
    # Template placeholders
    "{{graphqueriestablename}}",
}

# Known tables from tables_reference.csv - loaded at runtime
KNOWN_TABLES_LOWER: Set[str] = set()
# Mapping from lowercase table name to proper case (as defined in tables_reference.csv)
KNOWN_TABLES_PROPER_CASE: Dict[str, str] = {}


def load_known_tables(script_dir: Path) -> Tuple[Set[str], Dict[str, str]]:
    """
    Load known table names from tables_reference.csv.
    
    Args:
        script_dir: Path to the directory containing tables_reference.csv
    
    Returns:
        Tuple of (set of lowercase table names, dict mapping lowercase to proper case)
    """
    tables_file = script_dir / "tables_reference.csv"
    known_tables: Set[str] = set()
    proper_case_map: Dict[str, str] = {}
    
    if tables_file.exists():
        with open(tables_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                table_name = row.get("table_name", "").strip()
                if table_name:
                    lower_name = table_name.lower()
                    known_tables.add(lower_name)
                    proper_case_map[lower_name] = table_name
    
    return known_tables, proper_case_map


def normalize_table_case(table_name: str) -> str:
    """
    Normalize a table name to its proper case as defined in tables_reference.csv.
    
    Args:
        table_name: The table name to normalize
        
    Returns:
        The properly-cased table name, or the original if not found in reference
    """
    if not table_name:
        return table_name
    lower_name = table_name.lower()
    return KNOWN_TABLES_PROPER_CASE.get(lower_name, table_name)


PIPE_BLOCK_COMMANDS = {
    "project",
    "project-away",
    "project-rename",
    "extend",
    "summarize",
    "sort",
    "order",
    "top",
    "take",
    "limit",
    "parse",
}


def is_valid_table_candidate(
    token: Optional[str],
    *,
    allow_parser_names: bool = False,
    known_parser_names: Optional[Set[str]] = None,
) -> bool:
    """
    Check if a token is a valid table candidate.
    
    Uses tables_reference.csv as the authoritative source for known Azure Monitor tables,
    plus allows custom log tables (ending with _CL), ASIM parser functions, and
    solution-specific parser names.
    
    Args:
        token: The token to validate
        allow_parser_names: If True, also allow names ending with _parser
        known_parser_names: Optional set of known parser names (normalized to lowercase)
                           that should be treated as valid table candidates
    
    Returns:
        True if the token is a valid table candidate, False otherwise
    """
    if not isinstance(token, str):
        return False
    cleaned = token.strip()
    if not cleaned:
        return False
    lowered = cleaned.lower()
    
    # Reject tokens in the minimal blocklist
    if lowered in BLOCKED_TOKENS:
        return False
    
    # Reject numeric values and time spans
    if lowered.isdigit():
        return False
    if re.fullmatch(r"\d+[smhd]", lowered):
        return False
    if cleaned[0].isdigit():
        return False
    
    # Filter out ARM template expressions (e.g., @{if(...), variables('...'), parameters('...'))
    if '@{' in cleaned or '@(' in cleaned:
        return False
    if cleaned.startswith("@") or cleaned.startswith("variables(") or cleaned.startswith("parameters("):
        return False
    
    # Filter out bracket expressions and ARM parameter references
    if cleaned.startswith("[") or "parameters(" in lowered or "variables(" in lowered:
        return False
    
    # Filter out Logic App expressions
    if "triggerbody()" in lowered or "body(" in lowered:
        return False
    
    # Filter names that start with dot
    if cleaned.startswith("."):
        return False
    
    # Filter names that are too short (less than 3 chars)
    if len(cleaned) < 3:
        return False
    
    # Allow custom log tables (ending with _CL)
    if lowered.endswith("_cl"):
        return True
    
    # Allow ASIM view functions that start with _Im_ or _ASim_ (e.g., _Im_Dns, _ASim_NetworkSession)
    # Also allow without underscore prefix (e.g., imDns, ASimNetworkSession, imProcessCreate)
    # But exclude ASIM helper functions like _ASIM_GetUsernameType, _ASIM_LookupDnsQueryType
    # Also exclude ASIM empty parsers like _Im_WebSession_Empty, _Im_Dns_Empty
    if lowered.startswith("_im_") or lowered.startswith("_asim_"):
        # Check if this is an empty parser (ends with _empty)
        if lowered.endswith("_empty"):
            return False  # Empty parsers only contain datatable definitions
        # Check if this is a helper function (contains verb patterns after prefix)
        # _im_ is 4 chars, _asim_ is 6 chars
        after_prefix = lowered[6:] if lowered.startswith("_asim_") else lowered[4:]
        helper_verbs = ("get", "lookup", "resolve", "check", "build", "extract", "parse")
        if any(after_prefix.startswith(verb) for verb in helper_verbs):
            return False  # This is a helper function, not a table/view
        return True
    
    # Allow ASIM parser functions without underscore prefix (imDns, ASimNetworkSession, imProcessCreate)
    # These are commonly used view functions that wrap ASIM parsers
    if lowered.startswith("im") or lowered.startswith("asim"):
        # Verify it looks like an ASIM parser (has a schema name after prefix)
        # Examples: imDns, imNetworkSession, ASimProcessEvent, imProcessCreate
        if len(lowered) > 4:  # At least "im" + something meaningful
            return True
    
    # Reject other names starting with underscore (except _CL which was handled above)
    if lowered.startswith("_"):
        return False
    
    # Reject parser function names unless explicitly allowed
    if lowered.endswith("_parser") and not allow_parser_names:
        return False
    
    # Check if the token is a known parser name (solution-specific parsers)
    if known_parser_names and lowered in known_parser_names:
        return True
    
    # Check if the table is in the known tables reference list
    if KNOWN_TABLES_LOWER and lowered in KNOWN_TABLES_LOWER:
        return True
    
    # If KNOWN_TABLES_LOWER is not loaded yet (e.g., during module import),
    # fall back to allowing names that don't look like obvious variables
    if not KNOWN_TABLES_LOWER:
        # Basic heuristic: reject obvious KQL variable patterns
        # This is only used as fallback when tables_reference.csv hasn't been loaded
        obvious_variable_prefixes = ('filtered', 'aggregated', 'temp', 'tmp', 'my')
        for prefix in obvious_variable_prefixes:
            if lowered.startswith(prefix):
                return False
        return True
    
    # Table not in known tables list - reject it
    return False


def is_true_table_name(value: Optional[str]) -> bool:
    return isinstance(value, str) and value.strip().lower().endswith("_cl")


def prefers_asim_name(value: Optional[str]) -> bool:
    return isinstance(value, str) and value.strip().lower().startswith("asim")


PLURAL_TABLE_CORRECTIONS = {
    "securityevents": "SecurityEvent",
    "windowsevents": "WindowsEvent",
}


# Connector association override - parsed from main overrides file
# Entity=connector_association, Pattern=table(s), Field=match_type, Value=connector_id|solution_name
class ConnectorAssociationOverride:
    """Represents a rule for overriding connector associations for parsers/content items.
    
    Parsed from the main overrides file with Entity='connector_association':
    - Field specifies match type: 'tables_only', 'tables_include', or 'name_pattern'
    - Pattern is the table names (comma-separated) or regex for name matching
    - Value is 'connector_id|solution_name'
    """
    def __init__(self, match_type: str, pattern: str, value: str):
        self.match_type = match_type.lower().strip()  # 'tables_only', 'tables_include', 'name_pattern'
        self.pattern = pattern.strip()
        
        # Parse connector_id and solution_name from value (format: connector_id|solution_name)
        parts = value.split('|', 1)
        self.connector_id = parts[0].strip() if parts else ''
        self.solution_name = parts[1].strip() if len(parts) > 1 else ''
        
        # For table-based overrides, parse the table list
        if self.match_type in ('tables_only', 'tables_include'):
            self.tables = {t.strip().lower() for t in self.pattern.split(',') if t.strip()}
            self.regex = None
        else:
            # For name_pattern, compile regex
            self.tables = set()
            try:
                self.regex = re.compile(f"^{self.pattern}$", re.IGNORECASE)
            except re.error:
                self.regex = None
    
    def matches(self, item_tables: Set[str], item_name: str = '') -> bool:
        """Check if an item matches this override rule."""
        if self.match_type == 'tables_only':
            return item_tables == self.tables and len(item_tables) > 0
        elif self.match_type == 'tables_include':
            return bool(item_tables & self.tables)
        elif self.match_type == 'name_pattern':
            return self.regex is not None and bool(self.regex.match(item_name))
        return False


def apply_connector_association_override(
    item_tables: Set[str],
    item_name: str,
    overrides: List[ConnectorAssociationOverride]
) -> Optional[Tuple[str, str]]:
    """Check if any connector association override applies to an item.
    
    Args:
        item_tables: Set of table names (lowercase) used by the item
        item_name: Name of the item
        overrides: List of ConnectorAssociationOverride objects
        
    Returns:
        Tuple of (connector_id, solution_name) if an override matches, None otherwise
    """
    for override in overrides:
        if override.matches(item_tables, item_name):
            return (override.connector_id, override.solution_name)
    return None


# Override system types
class Override:
    """Represents a single override rule from the overrides CSV."""
    def __init__(self, entity: str, pattern: str, field: str, value: str):
        self.entity = entity.lower().strip()
        self.pattern = pattern.strip()
        self.field = field.strip()
        self.value = value
        # Compile regex with anchors for full match, case insensitive
        try:
            self.regex = re.compile(f"^{self.pattern}$", re.IGNORECASE)
        except re.error:
            self.regex = None
    
    def matches(self, key: str) -> bool:
        """Check if the key matches this override's pattern."""
        if self.regex is None:
            return False
        return bool(self.regex.match(key))


def load_overrides(overrides_path: Path) -> List[Override]:
    """Load overrides from CSV file.
    
    CSV format: Entity,Pattern,Field,Value
    - Entity: table, connector, solution, or connector_association (case insensitive)
    - Pattern: regex pattern to match against key (full match, case insensitive)
    - Field: the field to override (for connector_association: match type like 'tables_only')
    - Value: the new value (for connector_association: 'connector_id|solution_name')
    """
    overrides: List[Override] = []
    if not overrides_path.exists():
        return overrides
    
    try:
        # Use utf-8-sig to handle BOM (Byte Order Mark) from Excel
        with overrides_path.open("r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                entity = row.get("Entity", "").strip()
                pattern = row.get("Pattern", "").strip()
                field = row.get("Field", "").strip()
                value = row.get("Value", "")
                
                # Skip empty rows and connector_association (handled separately)
                if not entity or not pattern or not field:
                    continue
                if entity.lower() == 'connector_association':
                    continue  # Skip - these are handled by load_connector_association_overrides
                
                overrides.append(Override(entity, pattern, field, value))
    except Exception as e:
        print(f"Warning: Could not load overrides from {overrides_path}: {e}")
    
    return overrides


def load_connector_association_overrides(overrides_path: Path) -> List[ConnectorAssociationOverride]:
    """Load connector association overrides from the main overrides CSV file.
    
    These are rows with Entity='connector_association':
    - Pattern: table names (comma-separated) or regex for name matching
    - Field: match type ('tables_only', 'tables_include', 'name_pattern')
    - Value: 'connector_id|solution_name'
    
    Returns:
        List of ConnectorAssociationOverride objects
    """
    overrides: List[ConnectorAssociationOverride] = []
    if not overrides_path.exists():
        return overrides
    
    try:
        with overrides_path.open("r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                entity = row.get("Entity", "").strip()
                pattern = row.get("Pattern", "").strip()
                field = row.get("Field", "").strip()  # This is the match type
                value = row.get("Value", "")
                
                # Only process connector_association entries
                if entity.lower() != 'connector_association':
                    continue
                if not pattern or not field or not value:
                    continue
                
                overrides.append(ConnectorAssociationOverride(field, pattern, value))
    except Exception as e:
        print(f"Warning: Could not load connector association overrides from {overrides_path}: {e}")
    
    return overrides


def apply_overrides_to_row(
    row: Dict[str, str],
    overrides: List[Override],
    entity_type: str,
    key_field: str
) -> Dict[str, str]:
    """Apply matching overrides to a row.
    
    Args:
        row: The data row to modify
        overrides: List of Override objects
        entity_type: 'table', 'connector', or 'solution'
        key_field: The field name to use for pattern matching (e.g., 'table_name', 'connector_id')
    
    Returns:
        Modified row with overrides applied
    """
    key_value = row.get(key_field, "")
    if not key_value:
        return row
    
    for override in overrides:
        if override.entity != entity_type.lower():
            continue
        if override.matches(key_value):
            # Apply the override
            if override.field in row:
                row[override.field] = override.value
    
    return row


def apply_overrides_to_data(
    data: List[Dict[str, str]],
    overrides: List[Override],
    entity_type: str,
    key_field: str
) -> List[Dict[str, str]]:
    """Apply overrides to all rows in a dataset.
    
    Args:
        data: List of data rows
        overrides: List of Override objects
        entity_type: 'table', 'connector', or 'solution'
        key_field: The field name to use for pattern matching
    
    Returns:
        Modified data with overrides applied
    """
    return [apply_overrides_to_row(row, overrides, entity_type, key_field) for row in data]


def apply_plural_table_fix(name: str) -> Tuple[str, Optional[str]]:
    lowered = name.lower()
    corrected = PLURAL_TABLE_CORRECTIONS.get(lowered)
    if corrected and corrected != name:
        return corrected, name
    return name, None


def safe_relative(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> Optional[Any]:
    """
    Read and parse JSON file with tolerance for common syntax issues.
    Attempts to strip JSON comments and trailing commas before parsing.
    """
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            content = handle.read()
        
        # Try standard JSON first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Attempt to clean common issues
            # 1. Strip line comments (// ...)
            lines = content.splitlines()
            cleaned_lines = []
            for line in lines:
                # Remove // comments but preserve URLs (http://, https://)
                if '//' in line:
                    # Check if it's a comment (not part of a URL)
                    parts = line.split('//')
                    if len(parts) > 1:
                        # Keep the part before // if it doesn't look like a URL
                        before = parts[0]
                        if not before.rstrip().endswith(':'):
                            cleaned_lines.append(before)
                            continue
                cleaned_lines.append(line)
            
            cleaned_content = '\n'.join(cleaned_lines)
            
            # 2. Attempt to fix trailing commas before } or ]
            import re
            cleaned_content = re.sub(r',(\s*[}\]])', r'\1', cleaned_content)
            
            # Try parsing cleaned content
            try:
                return json.loads(cleaned_content)
            except json.JSONDecodeError:
                pass
        
        # Fallback to json5 if available
        if json5 is not None:
            try:
                with path.open("r", encoding="utf-8-sig") as handle:
                    return json5.load(handle)
            except Exception as secondary_error:
                print(f"Failed to read {path}: {secondary_error}")
                return None
        
        # If all attempts failed, report the original error
        with path.open("r", encoding="utf-8-sig") as handle:
            json.load(handle)  # This will raise the original error
            
    except json.JSONDecodeError as primary_error:
        print(f"Failed to read {path}: {primary_error}")
        return None
    except Exception as exc:
        print(f"Failed to read {path}: {exc}")
        return None


def remove_string_literals(text: str) -> str:
    """
    Remove string literals from KQL query text to avoid false positives in table extraction.
    
    Handles:
    - Double-quoted strings: "text here"
    - Single-quoted strings: 'text here'
    - Verbatim strings: @"text here" (backslash is NOT an escape in these)
    - Multi-line strings with escaped quotes
    
    Args:
        text: The KQL query text
        
    Returns:
        Text with string literals replaced by empty placeholders
    """
    if not text:
        return text
    
    result = []
    i = 0
    in_string = False
    string_char = None
    is_verbatim = False  # Track if we're in a @"..." verbatim string
    
    while i < len(text):
        char = text[i]
        
        if not in_string:
            if char in '"\'':
                # Check for multi-char string prefix like @" for verbatim strings
                if i > 0 and text[i-1] == '@':
                    # Remove the @ as well (it was already added)
                    if result and result[-1] == '@':
                        result.pop()
                    is_verbatim = True
                else:
                    is_verbatim = False
                in_string = True
                string_char = char
                result.append(' ')  # Replace string with space to preserve token boundaries
            else:
                result.append(char)
        else:
            # Inside a string
            if not is_verbatim and char == '\\' and i + 1 < len(text):
                # Escape sequence - skip the next character (only for non-verbatim strings)
                i += 1
            elif char == string_char:
                # End of string
                in_string = False
                string_char = None
                is_verbatim = False
            # Don't add any characters from inside the string
        
        i += 1
    
    return ''.join(result)


def remove_datatable_content(text: str) -> str:
    """
    Remove the content inside datatable() declarations to prevent false positive table detection.
    
    datatable() in KQL has column names that look like table names (e.g., "Operation: string"),
    which can be falsely detected as table references.
    
    This function replaces datatable(...)[...] with empty strings to avoid this.
    """
    if not text or 'datatable' not in text.lower():
        return text
    
    # Pattern to match datatable(column definitions)[data array]
    # We need to handle nested parentheses and brackets
    result = []
    i = 0
    text_lower = text.lower()
    
    while i < len(text):
        # Check if we're at the start of "datatable"
        if text_lower[i:i+9] == 'datatable':
            # Find the opening parenthesis
            paren_start = text.find('(', i + 9)
            if paren_start == -1:
                result.append(text[i])
                i += 1
                continue
            
            # Check that there's only whitespace between "datatable" and "("
            between = text[i+9:paren_start].strip()
            if between:
                # There's something between datatable and (, not a datatable declaration
                result.append(text[i])
                i += 1
                continue
            
            # Find matching closing parenthesis (handling nested)
            depth = 1
            pos = paren_start + 1
            while pos < len(text) and depth > 0:
                if text[pos] == '(':
                    depth += 1
                elif text[pos] == ')':
                    depth -= 1
                pos += 1
            
            if depth != 0:
                # Unbalanced parentheses, skip this
                result.append(text[i])
                i += 1
                continue
            
            paren_end = pos - 1
            
            # Look for optional [ ] data array after the parenthesis
            bracket_end = paren_end
            # Skip whitespace and newlines
            skip_pos = paren_end + 1
            while skip_pos < len(text) and text[skip_pos] in ' \t\n\r':
                skip_pos += 1
            
            if skip_pos < len(text) and text[skip_pos] == '[':
                # Find matching closing bracket
                depth = 1
                pos = skip_pos + 1
                while pos < len(text) and depth > 0:
                    if text[pos] == '[':
                        depth += 1
                    elif text[pos] == ']':
                        depth -= 1
                    pos += 1
                if depth == 0:
                    bracket_end = pos - 1
            
            # Skip the entire datatable(...) or datatable(...)[...]
            i = bracket_end + 1
            continue
        
        result.append(text[i])
        i += 1
    
    return ''.join(result)


def remove_line_comments(text: str) -> str:
    if not text:
        return text
    return LINE_COMMENT_PATTERN.sub("", text)


def strip_pipe_command_blocks(text: str) -> str:
    if not text:
        return text
    lines = text.splitlines()
    result: List[str] = []
    skip_block = False
    for line in lines:
        stripped = line.lstrip()
        if skip_block:
            if stripped.startswith("|"):
                skip_block = False
            # Also reset skip_block on statement boundaries:
            # - Lines starting with }; (end of let function body)
            # - Lines starting with }); or ); (end of function call)
            # - Lines that look like standalone table names (potential pipeline heads)
            elif stripped.startswith("};") or stripped.startswith("});") or stripped.startswith(");"):
                skip_block = False
            # Check if line looks like a table name (word followed by nothing or just whitespace)
            # This helps catch pipeline heads like "TableName" on their own line
            elif TOKEN_PATTERN.fullmatch(stripped.rstrip(";")):
                skip_block = False
            # Reset on lines that start with "union" (union statements after pipe blocks)
            elif stripped.lower().startswith("union"):
                skip_block = False
            # Reset on lines that start with "let" (new variable assignments)
            elif stripped.lower().startswith("let "):
                skip_block = False
            else:
                continue
        if stripped.startswith("|"):
            command_parts = stripped[1:].lstrip().split()
            keyword = command_parts[0].lower() if command_parts else ""
            extended_keyword = keyword
            if keyword in {"order", "sort"} and len(command_parts) > 1:
                extended_keyword = f"{keyword} {command_parts[1].lower()}"
            if keyword in PIPE_BLOCK_COMMANDS or extended_keyword in {"order by", "sort by"}:
                # Only skip subsequent lines if this pipe command doesn't end with semicolon
                # A semicolon indicates the statement is complete
                if not stripped.rstrip().endswith(";"):
                    skip_block = True
                continue
        result.append(line)
    return "\n".join(result)


def detect_pipeline_heads(
    text: str,
    *,
    assigned_variables: Set[str],
    allow_parser_tokens: bool,
    known_parser_names: Optional[Set[str]] = None,
) -> Set[str]:
    """
    Detect table names that appear as pipeline heads by analyzing query structure.
    Uses context-aware validation to distinguish tables from field names without whitelisting.
    
    Args:
        text: The query text to analyze
        assigned_variables: Set of variable names assigned via 'let' statements
        allow_parser_tokens: If True, allow names ending with _parser
        known_parser_names: Optional set of known parser names (normalized to lowercase)
    """
    if not text:
        return set()
    tokens: Set[str] = set()
    lines = text.splitlines()
    total = len(lines)
    
    # Pattern for operators that generate fields (subset of FIELD_GENERATING_PATTERN)
    # These specific operators indicate field context where identifiers on subsequent lines
    # are likely field names rather than table names
    pipeline_field_pattern = re.compile(
        r"^\s*\|\s*(project|extend|parse|mv-expand|mv-apply|summarize)\b",
        re.IGNORECASE
    )
    
    # Track if we're inside a multi-line field-generating statement
    in_field_context = False
    
    for idx, line in enumerate(lines):
        stripped = line.strip()
        
        # Any line starting with | resets the field context first
        if stripped.startswith("|"):
            in_field_context = False
            # Then check if this line starts a new field-generating operation
            if pipeline_field_pattern.match(line):
                in_field_context = True
            # But if this line also ends with a statement boundary, reset context
            # This handles cases like "| summarize make_set(x));" where the pipe line
            # ends a let function, so the next lines are in a new context
            if stripped.endswith(");") or stripped.endswith("});") or stripped.endswith("};"):
                in_field_context = False
            continue
        
        # Reset field context on statement boundaries (end of let functions, etc.)
        if stripped.startswith("};") or stripped.startswith("});") or stripped.startswith(");") or stripped == "}":
            in_field_context = False
        # Reset on lines that start with "let" (new variable assignments indicate new statement)
        if stripped.lower().startswith("let "):
            in_field_context = False
        # Reset on lines that start with "union" (union statements)
        if stripped.lower().startswith("union"):
            in_field_context = False
        
        # Skip lines in field context that don't start with |
        if in_field_context:
            continue
        
        # Now check for pipeline head candidates (non-pipe lines)
        if not stripped:
            continue
        
        candidate = stripped.rstrip(";").strip()
        if not candidate:
            continue
        if not TOKEN_PATTERN.fullmatch(candidate):
            continue
        lowered = candidate.lower()
        if lowered in assigned_variables:
            continue
        
        # Check if followed by pipe (pipeline head pattern)
        next_idx = idx + 1
        while next_idx < total and lines[next_idx].strip() == "":
            next_idx += 1
        
        if next_idx < total and lines[next_idx].lstrip().startswith("|"):
            if is_valid_table_candidate(candidate, allow_parser_names=allow_parser_tokens, known_parser_names=known_parser_names):
                tokens.add(candidate)
    
    return tokens


def find_value_by_key(obj: Any, key: str) -> Optional[str]:
    if isinstance(obj, dict):
        for k, value in obj.items():
            if k == key and isinstance(value, str):
                return value
            result = find_value_by_key(value, key)
            if isinstance(result, str):
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = find_value_by_key(item, key)
            if isinstance(result, str):
                return result
    return None


def substitute_placeholders(text: str, root: Any, cache: Dict[str, Optional[str]]) -> str:
    def _replace(match: re.Match[str]) -> str:
        placeholder = match.group(1).strip()
        if placeholder not in cache:
            cache[placeholder] = find_value_by_key(root, placeholder)
        replacement = cache.get(placeholder)
        return replacement.strip() if isinstance(replacement, str) else ""

    return PLACEHOLDER_PATTERN.sub(_replace, text)


def extract_table_token(
    raw_text: Any,
    root: Any,
    cache: Dict[str, Optional[str]],
    *,
    allow_parser_tokens: bool = False,
) -> Optional[str]:
    if not isinstance(raw_text, str):
        return None
    cleaned = raw_text.strip()
    if not cleaned:
        return None
    cleaned = remove_line_comments(cleaned)
    cleaned = substitute_placeholders(cleaned, root, cache)
    for match in TOKEN_PATTERN.finditer(cleaned):
        token = match.group(0)
        if not token:
            continue
        if token.lower() == "variables":
            continue
        resolved_token = resolve_table_token_reference(token, root, cache)
        if resolved_token:
            token = resolved_token
        return token
    return None


def extract_query_table_tokens(
    raw_text: Any,
    root: Any,
    cache: Dict[str, Optional[str]],
    *,
    allow_parser_tokens: bool = False,
    known_parser_names: Optional[Set[str]] = None,
) -> Set[str]:
    """
    Extract table names from a KQL query.
    
    Args:
        raw_text: The query text to analyze
        root: Root object for resolving references
        cache: Cache for resolved references
        allow_parser_tokens: If True, allow names ending with _parser
        known_parser_names: Optional set of known parser names (normalized to lowercase)
    
    Returns:
        Set of table names found in the query
    """
    tokens: Set[str] = set()
    if not isinstance(raw_text, str):
        token = extract_table_token(raw_text, root, cache, allow_parser_tokens=allow_parser_tokens)
        if token:
            tokens.add(token)
        return tokens
    cleaned = raw_text.strip()
    if not cleaned:
        return tokens
    without_comments = remove_line_comments(cleaned)
    without_strings = remove_string_literals(without_comments)  # Remove string literals to avoid false positives
    without_datatable = remove_datatable_content(without_strings)  # Remove datatable() content to avoid false positives
    pruned = strip_pipe_command_blocks(without_datatable)
    substituted = substitute_placeholders(pruned, root, cache)

    assigned_variables: Set[str] = set()
    for match in LET_ASSIGNMENT_PATTERN.finditer(substituted):
        variable_name = match.group(1).strip().lower()
        candidate = match.group(2).strip()
        if candidate and is_valid_table_candidate(candidate, allow_parser_names=allow_parser_tokens, known_parser_names=known_parser_names):
            candidate_lower = candidate.lower()
            if candidate_lower not in assigned_variables:
                tokens.add(candidate)
        if variable_name:
            assigned_variables.add(variable_name)

    # Detect tables in union statements
    # Union can have tables separated by commas or in parentheses
    if UNION_KEYWORD_PATTERN.search(substituted):
        for match in TOKEN_PATTERN.finditer(substituted):
            candidate = match.group(0)
            lowered = candidate.lower()
            # Skip union keywords and boolean values
            if lowered in {"union", "isfuzzy", "true", "false"}:
                continue
            # Skip variable references
            if lowered in assigned_variables:
                continue
            # Accept any valid table candidate (known tables, _CL tables, ASIM views)
            if is_valid_table_candidate(candidate, allow_parser_names=allow_parser_tokens, known_parser_names=known_parser_names):
                tokens.add(candidate)

    pipeline_tokens = detect_pipeline_heads(
        without_strings,
        assigned_variables=assigned_variables,
        allow_parser_tokens=allow_parser_tokens,
        known_parser_names=known_parser_names,
    )
    tokens.update(pipeline_tokens)
    
    # Detect inline pipeline patterns: TableName | where ...
    # This handles cases where table and pipe are on the SAME line (with optional leading whitespace)
    # Use [^\S\n]* instead of \s* to match whitespace but not newlines
    inline_pipe_pattern = re.compile(r'^[^\S\n]*([A-Za-z_][A-Za-z0-9_]*)[^\S\n]*\|', re.MULTILINE)
    for match in inline_pipe_pattern.finditer(without_strings):
        candidate = match.group(1)
        lowered = candidate.lower()
        if lowered not in assigned_variables:
            if is_valid_table_candidate(candidate, allow_parser_names=allow_parser_tokens, known_parser_names=known_parser_names):
                tokens.add(candidate)
    
    # Detect tables in parentheses followed by pipe: (TableName | ...
    # This handles patterns like let x = (AzureDiagnostics | where ...)
    paren_pipe_pattern = re.compile(r'\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\n?\s*\|', re.MULTILINE)
    for match in paren_pipe_pattern.finditer(without_strings):
        candidate = match.group(1)
        lowered = candidate.lower()
        if lowered not in assigned_variables:
            if is_valid_table_candidate(candidate, allow_parser_names=allow_parser_tokens, known_parser_names=known_parser_names):
                tokens.add(candidate)
    
    # Detect tables in braces followed by pipe: { TableName | ...
    # This handles patterns like let parser = (disabled:bool=false) { CommonSecurityLog | where ...
    brace_pipe_pattern = re.compile(r'\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\n?\s*\|', re.MULTILINE)
    for match in brace_pipe_pattern.finditer(without_strings):
        candidate = match.group(1)
        lowered = candidate.lower()
        if lowered not in assigned_variables:
            if is_valid_table_candidate(candidate, allow_parser_names=allow_parser_tokens, known_parser_names=known_parser_names):
                tokens.add(candidate)
    
    # Detect ASIM view function calls: _Im_Dns(...), _ASim_NetworkSession(...)
    # These are called like functions but reference underlying tables
    asim_view_pattern = re.compile(r'(_Im_[A-Za-z0-9_]+|_ASim_[A-Za-z0-9_]+)\s*\(', re.IGNORECASE)
    for match in asim_view_pattern.finditer(without_strings):
        view_name = match.group(1)
        tokens.add(view_name)
    
    token = extract_table_token(raw_text, root, cache, allow_parser_tokens=allow_parser_tokens)
    if token and is_valid_table_candidate(token, allow_parser_names=allow_parser_tokens, known_parser_names=known_parser_names):
        tokens.add(token)
    return {
        token
        for token in tokens
        if is_valid_table_candidate(token, allow_parser_names=allow_parser_tokens, known_parser_names=known_parser_names)
        or (allow_parser_tokens and isinstance(token, str) and token.lower().endswith("_parser"))
    }


def extract_tables_from_table_json(table_json_path: Path) -> Dict[str, Dict[str, Any]]:
    """
    Extract table names from *_Table.json files.
    
    These files define Log Analytics custom tables and contain the table name
    in the "name" field at the root level or nested under "properties.schema".
    
    Args:
        table_json_path: Path to the *_Table.json file
        
    Returns:
        Dictionary mapping table names to their metadata
    """
    tables: Dict[str, Dict[str, Any]] = {}
    
    data = read_json(table_json_path)
    if data is None:
        return tables
    
    def extract_name(obj: Any) -> Optional[str]:
        if isinstance(obj, dict):
            # Direct "name" field
            name = obj.get("name")
            if isinstance(name, str) and name.strip():
                # Check it looks like a table name (not a DCR or resource name)
                name_clean = name.strip()
                # Trust names in _Table.json files - only filter obvious non-tables
                if name_clean and not name_clean.startswith("[") and not name_clean.startswith("{{"):
                    return name_clean
            # Nested under properties.schema.name
            props = obj.get("properties")
            if isinstance(props, dict):
                schema = props.get("schema")
                if isinstance(schema, dict):
                    schema_name = schema.get("name")
                    if isinstance(schema_name, str) and schema_name.strip():
                        name_clean = schema_name.strip()
                        # Trust names in _Table.json files - only filter obvious non-tables
                        if name_clean and not name_clean.startswith("[") and not name_clean.startswith("{{"):
                            return name_clean
        return None
    
    # Handle both single object and array formats
    if isinstance(data, list):
        for item in data:
            table_name = extract_name(item)
            if table_name:
                tables[table_name] = {
                    "has_mismatch": False,
                    "actual_table": None,
                    "sources": {"table_json_file"},
                }
    else:
        table_name = extract_name(data)
        if table_name:
            tables[table_name] = {
                "has_mismatch": False,
                "actual_table": None,
                "sources": {"table_json_file"},
            }
    
    return tables


def extract_tables_from_dcr_json(dcr_json_path: Path) -> Dict[str, Dict[str, Any]]:
    """
    Extract table names from *_DCR.json files (Data Collection Rule definitions).
    
    DCR files contain table names in the "outputStream" parameter within dataFlows.
    The value is prefixed with "Microsoft-" or "Custom-" which should be stripped.
    
    Args:
        dcr_json_path: Path to the *_DCR.json file
        
    Returns:
        Dictionary mapping table names to their metadata
    """
    tables: Dict[str, Dict[str, Any]] = {}
    
    data = read_json(dcr_json_path)
    if data is None:
        return tables
    
    def extract_output_streams(obj: Any) -> Set[str]:
        """Extract table names from outputStream fields in a DCR object."""
        found_tables: Set[str] = set()
        
        if isinstance(obj, dict):
            # Check dataFlows array
            data_flows = obj.get("dataFlows") or obj.get("properties", {}).get("dataFlows")
            if isinstance(data_flows, list):
                for flow in data_flows:
                    if isinstance(flow, dict):
                        output_stream = flow.get("outputStream")
                        if isinstance(output_stream, str):
                            # Strip "Microsoft-" or "Custom-" prefix
                            table_name = output_stream.strip()
                            if table_name.startswith("Microsoft-"):
                                table_name = table_name[len("Microsoft-"):]
                            elif table_name.startswith("Custom-"):
                                table_name = table_name[len("Custom-"):]
                            
                            # Skip if it looks like an expression or placeholder
                            if table_name and not table_name.startswith("[") and not table_name.startswith("{{"):
                                # Trust tables from DCR files - don't require them to be in known tables list
                                found_tables.add(table_name)
            
            # Also check nested properties
            props = obj.get("properties")
            if isinstance(props, dict):
                found_tables.update(extract_output_streams(props))
        
        return found_tables
    
    # Handle both single object and array formats
    if isinstance(data, list):
        for item in data:
            for table_name in extract_output_streams(item):
                tables[table_name] = {
                    "has_mismatch": False,
                    "actual_table": None,
                    "sources": {"dcr_json_file"},
                }
    else:
        for table_name in extract_output_streams(data):
            tables[table_name] = {
                "has_mismatch": False,
                "actual_table": None,
                "sources": {"dcr_json_file"},
            }
    
    return tables


def find_companion_table_files(connector_json_path: Path) -> Tuple[List[Path], List[Path]]:
    """
    Find *_Table.json and *_DCR.json files in the same directory as a connector JSON.
    
    These companion files often contain table definitions that aren't embedded
    in the connector definition itself (common with CCP/CCF connectors).
    
    Args:
        connector_json_path: Path to the connector JSON file
        
    Returns:
        Tuple of (table_json_paths, dcr_json_paths)
    """
    parent_dir = connector_json_path.parent
    table_files: List[Path] = []
    dcr_files: List[Path] = []
    
    for file_path in parent_dir.glob("*.json"):
        name_lower = file_path.name.lower()
        if name_lower.endswith("_table.json"):
            table_files.append(file_path)
        elif name_lower.endswith("_dcr.json"):
            dcr_files.append(file_path)
    
    return table_files, dcr_files


# CCF config file name patterns (lowercased for matching)
CCF_CONFIG_PATTERNS: List[str] = [
    "pollingconfig",
    "pollerconfig",
    "dataconnectorpoller",
    "datapoller",
    "_poller",
]


def find_ccf_config_file(connector_json_path: Path) -> Optional[Path]:
    """
    Find the CCF configuration file (polling/poller config) in the same directory
    as a connector definition JSON file, or in sibling *_ccp directories.
    
    CCF config files contain the actual polling/push configuration and are typically
    named with patterns like *_PollingConfig.json, *_PollerConfig.json,
    *_DataConnectorPoller.json, dataPoller.json, *_poller*.json, or connectors.json.
    Some connectors store their config in a sibling directory with a _ccp suffix.
    
    Args:
        connector_json_path: Path to the connector JSON file (usually the
            connectorDefinition file)
        
    Returns:
        Path to the CCF config file if found, None otherwise
    """
    parent_dir = connector_json_path.parent
    
    # Files to skip when searching for config files
    skip_patterns = [
        "connectordefinition", "definitions.json", "_table.", "_dcr.",
        "function.json", "host.json", "proxies.json",
    ]
    
    def _is_skip_file(name_lower: str) -> bool:
        return any(skip in name_lower for skip in skip_patterns)
    
    def _search_dir_for_config(search_dir: Path) -> Optional[Path]:
        """Search a directory for CCF config files."""
        for file_path in search_dir.glob("*.json"):
            name_lower = file_path.name.lower()
            if _is_skip_file(name_lower):
                continue
            # Check named patterns
            if any(pattern in name_lower for pattern in CCF_CONFIG_PATTERNS):
                return file_path
        # Fallback: connectors.json (used by some modern CCF connectors like Bitwarden)
        connectors_json = search_dir / "connectors.json"
        if connectors_json.exists():
            return connectors_json
        # Fallback: *_dataConnector.json files (Push connectors use this pattern)
        for file_path in search_dir.glob("*.json"):
            name_lower = file_path.name.lower()
            if _is_skip_file(name_lower):
                continue
            if "dataconnector" in name_lower:
                return file_path
        return None
    
    # First search in the same directory
    result = _search_dir_for_config(parent_dir)
    if result:
        return result
    
    # Search sibling directories with _ccp suffix (e.g., GCPAuditLogs_ccp/)
    for sibling_dir in parent_dir.parent.iterdir():
        if sibling_dir.is_dir() and sibling_dir.name.lower().endswith('_ccp'):
            result = _search_dir_for_config(sibling_dir)
            if result:
                return result
    
    return None


def _find_field_values(obj: Any, field_name: str) -> List[Any]:
    """Recursively find all values for a given field name in a nested JSON structure."""
    results: List[Any] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == field_name:
                results.append(v)
            results.extend(_find_field_values(v, field_name))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(_find_field_values(item, field_name))
    return results


def extract_legacy_ccf_capabilities(json_content: str) -> List[str]:
    """
    Extract CCF capabilities from embedded pollingConfig in a connector's primary JSON.
    
    Legacy CCF connectors have their polling configuration embedded directly in the
    ARM template under properties.pollingConfig, rather than in a separate config file.
    
    Analyzes the pollingConfig to identify:
    - Authentication method (APIKey, OAuth2, Basic, JwtToken, etc.)
    - Whether paging is configured
    - HTTP method if POST (GET is default/implied)
    
    Args:
        json_content: Full JSON text of the connector's primary ARM template
    
    Returns:
        List of capability strings (e.g., ["OAuth2", "Paging", "POST"])
    """
    try:
        data = json.loads(json_content)
    except Exception:
        return []
    
    # Find pollingConfig in ARM template resources
    polling_configs = _find_field_values(data, 'pollingConfig')
    if not polling_configs:
        return []
    
    capabilities: List[str] = []
    auth_types_seen: Set[str] = set()
    has_paging = False
    has_post = False
    
    for pc in polling_configs:
        if not isinstance(pc, dict):
            continue
        
        # Auth section
        auth = pc.get('auth', {})
        if isinstance(auth, dict):
            auth_type = auth.get('authType', '') or auth.get('type', '')
            if auth_type:
                auth_types_seen.add(auth_type)
        
        # Request section - may have paging and HTTP method
        request = pc.get('request', {})
        if isinstance(request, dict):
            http_method = request.get('httpMethod', '').upper()
            if http_method == 'POST':
                has_post = True
        
        # Paging section
        paging = pc.get('paging', {})
        if paging and isinstance(paging, dict) and len(paging) > 0:
            has_paging = True
    
    for auth_type in sorted(auth_types_seen):
        capabilities.append(auth_type)
    if has_paging:
        capabilities.append('Paging')
    if has_post:
        capabilities.append('POST')
    
    return capabilities


def extract_ccf_capabilities(config_path: Path) -> List[str]:
    """
    Extract CCF capabilities from a CCF configuration file.
    
    Analyzes the JSON configuration to identify:
    - Connector kind (RestApiPoller, Push, GCP, AmazonWebServicesS3, etc.)
    - Authentication method (APIKey, OAuth2, Basic, JwtToken, Push, Session, etc.)
    - Whether paging is configured
    - HTTP method if POST (GET is default/implied)
    - Whether MvExpand transform is used (nestedTransformName contains MvExpandTransformer)
    - Whether nested steps are used (stepType: Nested)
    
    Args:
        config_path: Path to the CCF config JSON file
        
    Returns:
        List of capability strings (e.g., ["RestApiPoller", "OAuth2", "Paging", "POST"])
    """
    try:
        data = json.loads(config_path.read_text(encoding='utf-8'))
    except Exception:
        return []
    
    capabilities: List[str] = []
    kinds_seen: Set[str] = set()
    auth_types_seen: Set[str] = set()
    has_paging = False
    has_post = False
    has_mvexpand = False
    has_nested = False
    
    # Handle both single object and array of objects
    items = data if isinstance(data, list) else [data]
    
    for item in items:
        if not isinstance(item, dict):
            continue
        
        # Extract kind
        kind = item.get('kind', '')
        if kind:
            kinds_seen.add(kind)
        
        # Get properties (capabilities are in properties for ARM templates, or at top level)
        props = item.get('properties', item)
        if not isinstance(props, dict):
            continue
        
        # Extract auth type
        auth = props.get('auth', {})
        if isinstance(auth, dict):
            auth_type = auth.get('type', '')
            if auth_type:
                auth_types_seen.add(auth_type)
        
        # Check for paging
        paging = props.get('paging', {})
        if paging and isinstance(paging, dict) and paging.get('type'):
            has_paging = True
        elif paging and isinstance(paging, dict) and len(paging) > 0:
            has_paging = True
        
        # Check HTTP method
        request = props.get('request', {})
        if isinstance(request, dict):
            http_method = request.get('httpMethod', '').upper()
            if http_method == 'POST':
                has_post = True
    
    # Deep search for MvExpand: nestedTransformName containing "MvExpandTransformer"
    for val in _find_field_values(data, 'nestedTransformName'):
        if isinstance(val, str) and 'MvExpandTransformer' in val:
            has_mvexpand = True
            break
    
    # Deep search for Nested steps: stepType == "Nested"
    for val in _find_field_values(data, 'stepType'):
        if val == 'Nested':
            has_nested = True
            break
    
    # Build ordered capability list
    # 1. Kind (if not RestApiPoller, which is the default/common kind)
    for kind in sorted(kinds_seen):
        if kind != 'RestApiPoller':
            capabilities.append(kind)
    
    # 2. Auth types (skip "Push" if kind is Push - redundant)
    for auth_type in sorted(auth_types_seen):
        if auth_type == 'Push' and 'Push' in kinds_seen:
            continue
        capabilities.append(auth_type)
    
    # 3. Other capabilities
    if has_paging:
        capabilities.append('Paging')
    if has_post:
        capabilities.append('POST')
    if has_mvexpand:
        capabilities.append('MvExpand')
    if has_nested:
        capabilities.append('Nested')
    
    return capabilities


def resolve_table_token_reference(token: str, root: Any, cache: Dict[str, Optional[str]]) -> Optional[str]:
    key = token.strip()
    if not key:
        return None
    if key not in cache:
        cache[key] = find_value_by_key(root, key)
    value = cache.get(key)
    if isinstance(value, str):
        variables = root.get("variables") if isinstance(root, dict) else None
        resolved = _resolve_arm_reference(value, variables) or value
        cleaned = resolved.strip().strip('"').strip("'")
        if cleaned and cleaned.lower() != key.lower():
            return cleaned
    return None


def extract_tables(data: Any) -> Dict[str, Dict[str, Any]]:
    tables: Dict[str, Dict[str, Any]] = {}
    cache: Dict[str, Optional[str]] = {}

    def build_method_label(path: Iterable[Any]) -> str:
        parts: List[str] = []
        for segment in path:
            if segment is None:
                continue
            if isinstance(segment, str):
                cleaned = segment.strip()
                if cleaned:
                    parts.append(cleaned)
            else:
                parts.append(str(segment))
        return ".".join(parts) if parts else "unknown"

    def record_table(
        name: Optional[str],
        *,
        mismatch: bool = False,
        actual: Optional[str] = None,
        method: str = "unknown",
    ) -> None:
        canonical_name = name.strip() if isinstance(name, str) else ""
        actual_clean = actual.strip() if isinstance(actual, str) else None
        method_label = method or "unknown"

        if mismatch:
            if actual_clean and is_true_table_name(actual_clean):
                canonical_name = actual_clean
                mismatch = False
                actual_clean = None
            elif is_true_table_name(canonical_name):
                mismatch = False
                actual_clean = None
            elif actual_clean and prefers_asim_name(actual_clean):
                canonical_name = actual_clean
                mismatch = False
                actual_clean = None
            elif prefers_asim_name(canonical_name):
                mismatch = False
                actual_clean = None
            elif actual_clean:
                canonical_name = actual_clean
                mismatch = False
                actual_clean = None

        if not canonical_name and actual_clean:
            canonical_name = actual_clean
            mismatch = False
            actual_clean = None

        if not canonical_name:
            return

        canonical_name, plural_source = apply_plural_table_fix(canonical_name)

        entry = tables.setdefault(canonical_name, {"has_mismatch": False, "actual_table": None, "sources": set()})
        entry["has_mismatch"] = entry["has_mismatch"] or mismatch
        if mismatch and actual_clean:
            entry["actual_table"] = actual_clean
        if plural_source:
            plural_list = entry.setdefault("plural_sources", [])
            if plural_source not in plural_list:
                plural_list.append(plural_source)
        sources: Set[str] = entry.setdefault("sources", set())
        sources.add(method_label)

    def walk(obj: Any, key_path: Tuple[Any, ...] = ()):  # noqa: ANN401
        if isinstance(obj, dict):
            for key, value in obj.items():
                lower_key = key.lower()
                current_path = key_path + (key,)
                method_label = build_method_label(current_path)
                if lower_key == "basequery" or lower_key == "query":
                    tokens = extract_query_table_tokens(value, data, cache, allow_parser_tokens=True)
                    if tokens:
                        for token in tokens:
                            record_table(token, method=method_label)
                    else:
                        record_table(
                            extract_table_token(value, data, cache, allow_parser_tokens=True),
                            method=method_label,
                        )
                elif key == "dataTypes" and isinstance(value, list):
                    for idx, item in enumerate(value):
                        if isinstance(item, dict):
                            item_path = current_path + (str(idx),)
                            name_method = build_method_label(item_path + ("name",))
                            name_token = extract_table_token(
                                item.get("name"),
                                data,
                                cache,
                                allow_parser_tokens=True,
                            )
                            query_key = "lastDataReceivedQuery" if item.get("lastDataReceivedQuery") else "query"
                            query_field = item.get("lastDataReceivedQuery") or item.get("query")
                            query_method = build_method_label(item_path + (query_key,))
                            query_tokens = list(
                                extract_query_table_tokens(
                                    query_field,
                                    data,
                                    cache,
                                    allow_parser_tokens=True,
                                )
                            )
                            primary_actual = query_tokens[0] if query_tokens else None
                            if not primary_actual:
                                primary_actual = extract_table_token(
                                    query_field,
                                    data,
                                    cache,
                                    allow_parser_tokens=True,
                                )
                            mismatch = False
                            if name_token and primary_actual and name_token.lower() != primary_actual.lower():
                                mismatch = True
                            record_table(
                                name_token or primary_actual,
                                mismatch=mismatch,
                                actual=primary_actual,
                                method=name_method if name_token else query_method,
                            )
                            for extra_table in query_tokens[1:]:
                                record_table(extra_table, method=query_method)
                walk(value, current_path)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                walk(item, key_path + (str(idx),))

    walk(data)
    return tables



def find_connector_objects(data: Any) -> List[Dict[str, Any]]:
    """Find connector objects and extract description, instructionSteps, and permissions if present."""
    connectors: List[Dict[str, Any]] = []
    stack = [data]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            if {"id", "publisher", "title"}.issubset(current.keys()):
                id_value = current.get("id")
                publisher_value = current.get("publisher")
                title_value = current.get("title")
                # Allow connectors where title is a valid string (most important for display)
                # id and publisher may contain ARM variable references which we can resolve later
                if (
                    isinstance(id_value, str)
                    and isinstance(publisher_value, str)
                    and isinstance(title_value, str)
                    and "[variables(" not in title_value.lower()  # title must be literal
                ):
                    # Extract description, instructionSteps, and permissions if available
                    connector_copy = current.copy()
                    connector_copy["id_generated"] = False
                    # Resolve id if it's a variable reference - use a fallback based on title
                    if "[variables(" in id_value.lower():
                        # Try to create a reasonable id from the title
                        connector_copy["id"] = title_value.replace(" ", "").replace("-", "")
                        connector_copy["id_generated"] = True
                    # Resolve publisher if it's a variable reference - mark as unknown
                    if "[variables(" in publisher_value.lower():
                        connector_copy["publisher"] = "Unknown (ARM variable)"
                    if "descriptionMarkdown" in current:
                        connector_copy["description"] = current["descriptionMarkdown"]
                    if "instructionSteps" in current:
                        # Store instructionSteps as JSON-encoded string
                        connector_copy["instructionSteps"] = json.dumps(current["instructionSteps"])
                    if "permissions" in current:
                        # Store permissions as JSON-encoded string
                        connector_copy["permissions"] = json.dumps(current["permissions"])
                    connectors.append(connector_copy)
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
    return connectors


def find_connector_readme(solution_dir: Path) -> str:
    """
    Find README.md file in Data Connectors folder for a solution.
    Returns relative path within Data Connectors folder, or empty string if not found.
    
    Args:
        solution_dir: Path to the solution directory
    
    Returns:
        Relative path to README file within Data Connectors folder, or empty string
    """


def find_solution_json(solution_dir: Path) -> Optional[Dict[str, Any]]:
    """
    Find and read the Solution_*.json file from the Data folder.
    
    The Solution JSON contains metadata like Name, Logo, Author, Version, Description,
    and lists of content items. This is more accurate than SolutionMetadata.json for
    some fields.
    
    Args:
        solution_dir: Path to the solution directory
    
    Returns:
        Parsed JSON content or None if not found
    """
    # Check both "Data" and "data" folders (case-insensitive)
    for data_folder_name in ["Data", "data"]:
        data_dir = solution_dir / data_folder_name
        if not data_dir.exists():
            continue
        
        # Find Solution_*.json file
        for json_path in data_dir.glob("Solution_*.json"):
            data = read_json(json_path)
            if data and isinstance(data, dict):
                return data
    
    return None


def extract_logo_url(logo_html: str) -> str:
    """
    Extract the URL from an HTML img tag.
    
    Args:
        logo_html: HTML img tag like '<img src="https://..." width="75px" height="75px">'
    
    Returns:
        The src URL or empty string if not found
    """
    if not logo_html:
        return ""
    
    # Match src="..." or src='...'
    match = re.search(r'src\s*=\s*["\']([^"\']+)["\']', logo_html, re.IGNORECASE)
    if match:
        return match.group(1)
    return ""
    for dc_folder_name in ["Data Connectors", "DataConnectors", "Data Connector"]:
        dc_dir = solution_dir / dc_folder_name
        if not dc_dir.exists():
            continue
        # Look for README.md or any .md file directly in Data Connectors folder
        md_files = [f for f in dc_dir.glob('*.md') if f.is_file()]
        if md_files:
            # Prefer README.md if it exists
            for md_file in md_files:
                if md_file.stem.lower() == 'readme':
                    return f"{dc_folder_name}/{md_file.name}"
            # Otherwise use the first .md file
            return f"{dc_folder_name}/{md_files[0].name}"
    return ""


def collect_solution_info(solution_dir: Path) -> Dict[str, str]:
    """
    Collect solution metadata from both SolutionMetadata.json and Solution_*.json files.
    Uses caching based on key file modification times.
    
    The Solution JSON (in Data folder) provides:
    - Name (official name, may differ from folder name)
    - Logo (HTML img tag with URL)
    - Author
    - Version  
    - Description
    
    The SolutionMetadata.json provides:
    - publisherId, offerId
    - firstPublishDate, lastPublishDate
    - support information
    - categories
    """
    # Check cache first - use SolutionMetadata.json as the cache key file
    metadata_path = solution_dir / "SolutionMetadata.json"
    cache_key_file = metadata_path if metadata_path.exists() else solution_dir
    
    cached = get_cached_analysis(cache_key_file, "solutions")
    if cached is not None:
        return cached
    
    # Read SolutionMetadata.json for publishing metadata
    metadata = read_json(metadata_path) if metadata_path.exists() else {}
    if not isinstance(metadata, dict):
        metadata = {}
    
    # Read Solution_*.json from Data folder for richer metadata
    solution_json = find_solution_json(solution_dir)
    if solution_json is None:
        solution_json = {}
    
    # Flatten support object from SolutionMetadata.json
    support = metadata.get("support", {})
    if not isinstance(support, dict):
        support = {}
    
    # Flatten author object from SolutionMetadata.json (legacy)
    author = metadata.get("author", {})
    if not isinstance(author, dict):
        author = {}
    
    # Extract categories as comma-separated string
    categories = metadata.get("categories", {})
    if isinstance(categories, dict):
        category_keys = [k for k in categories.keys() if categories.get(k)]
        categories_str = ",".join(category_keys)
    else:
        categories_str = ""
    
    # Find README file for the solution (at solution root level)
    solution_readme_file = ""
    for readme_name in ["README.md", "readme.md", "Readme.md", "README.MD"]:
        readme_path = solution_dir / readme_name
        if readme_path.exists():
            solution_readme_file = readme_name
            break
    
    # Get name from Solution JSON (preferred) or fall back to folder name
    solution_name = solution_json.get("Name", "") or solution_dir.name
    
    # Extract logo URL from HTML img tag
    logo_html = solution_json.get("Logo", "")
    logo_url = extract_logo_url(logo_html)
    
    # Get author from Solution JSON (preferred) or SolutionMetadata.json
    solution_author = solution_json.get("Author", "") or author.get("name", "")
    
    # Get version from Solution JSON (preferred) or SolutionMetadata.json
    solution_version = solution_json.get("Version", "") or metadata.get("version", "")
    
    # Get description from Solution JSON (strip HTML/markdown for CSV)
    description = solution_json.get("Description", "")
    
    # Get dependencies from Solution JSON
    dependencies = solution_json.get("dependentDomainSolutionIds", [])
    if isinstance(dependencies, list):
        dependencies_str = ";".join(str(d) for d in dependencies if d)
    else:
        dependencies_str = ""
    
    result = {
        "solution_name": solution_name,
        "solution_folder": solution_dir.name,
        "solution_github_url": f"{GITHUB_REPO_URL}/Solutions/{quote(solution_dir.name)}",
        "solution_publisher_id": metadata.get("publisherId", ""),
        "solution_offer_id": metadata.get("offerId", ""),
        "solution_first_publish_date": metadata.get("firstPublishDate", ""),
        "solution_last_publish_date": metadata.get("lastPublishDate", ""),
        "solution_version": solution_version,
        "solution_support_name": support.get("name", ""),
        "solution_support_tier": support.get("tier", ""),
        "solution_support_link": support.get("link", ""),
        "solution_author_name": solution_author,
        "solution_categories": categories_str,
        "solution_readme_file": solution_readme_file,
        "solution_logo_url": logo_url,
        "solution_description": description,
        "solution_dependencies": dependencies_str,
    }
    
    # Cache the result
    set_cached_analysis(cache_key_file, "solutions", result)
    
    return result


# Marketplace cache filename (stored in .cache folder)
MARKETPLACE_CACHE_FILENAME = "marketplace_availability.csv"


def load_marketplace_cache(cache_dir: Path) -> Dict[str, Tuple[bool, str, str]]:
    """
    Load marketplace availability cache from CSV file.
    
    Args:
        cache_dir: Path to the cache directory
        
    Returns:
        Dictionary mapping legacy_id (publisher.offer) to (is_published, marketplace_url, last_checked) tuples
    """
    cache_file = cache_dir / MARKETPLACE_CACHE_FILENAME
    cache: Dict[str, Tuple[bool, str, str]] = {}
    
    if not cache_file.exists():
        return cache
    
    try:
        with cache_file.open("r", encoding="utf-8", newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                legacy_id = row.get('legacy_id', '')
                if legacy_id:
                    is_published = row.get('is_published', 'true').lower() == 'true'
                    marketplace_url = row.get('marketplace_url', '')
                    last_checked = row.get('last_checked', '')
                    cache[legacy_id] = (is_published, marketplace_url, last_checked)
    except Exception as e:
        print(f"Warning: Could not load marketplace cache: {e}")
    
    return cache


def save_marketplace_cache(cache_dir: Path, cache: Dict[str, Tuple[bool, str, str]]) -> None:
    """
    Save marketplace availability cache to CSV file.
    
    Args:
        cache_dir: Path to the cache directory
        cache: Dictionary mapping legacy_id to (is_published, marketplace_url, last_checked) tuples
    """
    cache_file = cache_dir / MARKETPLACE_CACHE_FILENAME
    
    # Ensure cache directory exists
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        with cache_file.open("w", encoding="utf-8", newline='') as f:
            fieldnames = ['legacy_id', 'is_published', 'marketplace_url', 'last_checked']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for legacy_id in sorted(cache.keys()):
                is_published, marketplace_url, last_checked = cache[legacy_id]
                writer.writerow({
                    'legacy_id': legacy_id,
                    'is_published': 'true' if is_published else 'false',
                    'marketplace_url': marketplace_url,
                    'last_checked': last_checked,
                })
    except Exception as e:
        print(f"Warning: Could not save marketplace cache: {e}")


def check_marketplace_availability(publisher_id: str, offer_id: str) -> Tuple[bool, str]:
    """
    Check if a solution is available on Azure Marketplace.
    
    Args:
        publisher_id: The publisher ID from SolutionMetadata.json
        offer_id: The offer ID from SolutionMetadata.json
        
    Returns:
        Tuple of (is_published, marketplace_url)
        - is_published: True if found on marketplace, False otherwise
        - marketplace_url: URL to the marketplace listing if found, empty string otherwise
    """
    if not HAS_URLLIB:
        return True, ""  # Assume published if we can't check
        
    if not publisher_id or not offer_id:
        return False, ""  # Can't check without both IDs
    
    # Build the API URL
    legacy_id = f"{publisher_id}.{offer_id}"
    api_url = f"{AZURE_MARKETPLACE_API_URL}/{legacy_id}?api-version={AZURE_MARKETPLACE_API_VERSION}"
    
    try:
        request = urllib.request.Request(api_url)
        request.add_header('Accept', 'application/json')
        
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status == 200:
                # Solution found on marketplace
                marketplace_url = f"https://azuremarketplace.microsoft.com/en-us/marketplace/apps/{legacy_id}"
                return True, marketplace_url
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Solution not found on marketplace
            return False, ""
        # Other HTTP errors - assume published to avoid false negatives
        return True, ""
    except Exception:
        # Network errors, timeouts, etc. - assume published to avoid false negatives
        return True, ""
    
    return True, ""


def check_all_solutions_marketplace(
    solutions_info: Dict[str, Dict[str, str]],
    cache_dir: Path,
    force_refresh: bool = False
) -> Dict[str, Tuple[bool, str]]:
    """
    Check marketplace availability for all solutions, using cache when available.
    
    Args:
        solutions_info: Dictionary mapping solution names to their info dictionaries
        cache_dir: Path to the cache directory for storing/loading cached results
        force_refresh: If True, ignore cache and check all solutions fresh
        
    Returns:
        Dictionary mapping solution names to (is_published, marketplace_url) tuples
    """
    results: Dict[str, Tuple[bool, str]] = {}
    total = len(solutions_info)
    
    # Load existing cache
    cache = load_marketplace_cache(cache_dir) if not force_refresh else {}
    
    # Track stats
    cache_hits = 0
    api_calls = 0
    today = datetime.now().strftime('%Y-%m-%d')
    
    log_print(f"Checking marketplace availability for {total} solutions...")
    if cache and not force_refresh:
        log_print(f"  Using cached results from {cache_dir / MARKETPLACE_CACHE_FILENAME}")
    elif force_refresh:
        log_print(f"  Force refresh enabled - checking all solutions via API")
    
    for i, (solution_name, info) in enumerate(sorted(solutions_info.items()), 1):
        publisher_id = info.get('solution_publisher_id', '')
        offer_id = info.get('solution_offer_id', '')
        
        # Check cache first
        if publisher_id and offer_id:
            legacy_id = f"{publisher_id}.{offer_id}"
            if legacy_id in cache:
                is_published, marketplace_url, _ = cache[legacy_id]
                results[solution_name] = (is_published, marketplace_url)
                cache_hits += 1
                continue
        
        # Not in cache, make API call
        is_published, marketplace_url = check_marketplace_availability(publisher_id, offer_id)
        results[solution_name] = (is_published, marketplace_url)
        api_calls += 1
        
        # Update cache
        if publisher_id and offer_id:
            legacy_id = f"{publisher_id}.{offer_id}"
            cache[legacy_id] = (is_published, marketplace_url, today)
        
        # Progress indicator every 25 API calls or every 100 solutions processed
        if api_calls > 0 and api_calls % 25 == 0:
            log_print(f"    [{i}/{total}] Made {api_calls} API calls, {cache_hits} cache hits...")
    
    # Save updated cache
    if api_calls > 0:
        save_marketplace_cache(cache_dir, cache)
        log_print(f"  Updated marketplace cache with {api_calls} new entries")
    
    # Count unpublished
    unpublished_count = sum(1 for is_pub, _ in results.values() if not is_pub)
    log_print(f"  Results: {cache_hits} from cache, {api_calls} API calls")
    log_print(f"  Found {unpublished_count} unpublished solutions out of {total}")
    
    return results


def collect_all_parsers_detailed(
    repo_root: Path,
    solutions_dir: Path,
) -> Tuple[List[Dict[str, Any]], Set[str], Dict[str, Set[str]]]:
    """Collect all non-ASIM parsers with detailed metadata.
    
    Collects parsers from:
    1. Top-level /Parsers/* directories (legacy parsers)
    2. Solution-specific Parsers/Parser directories
    
    Returns:
        Tuple of (parser_records, parser_names, parser_table_map)
        - parser_records: List of detailed parser metadata dicts
        - parser_names: Set of all parser names
        - parser_table_map: Dict mapping parser names to their tables
    """
    parser_records: List[Dict[str, Any]] = []
    all_names: Set[str] = set()
    all_tables_by_parser: Dict[str, Set[str]] = defaultdict(set)
    
    # First pass: collect all parser names from all sources for cross-reference
    log_print("  Pass 1: Collecting parser names for cross-reference...")
    # Legacy parsers
    legacy_parsers_dir = repo_root / "Parsers"
    legacy_parser_count = 0
    if legacy_parsers_dir.exists():
        legacy_subdirs = [d for d in legacy_parsers_dir.iterdir() if d.is_dir() and not d.name.lower().startswith('asim')]
        for subdir in legacy_subdirs:
            for file_path in subdir.iterdir():
                if not file_path.is_file():
                    continue
                suffix = file_path.suffix.lower()
                name_lower = file_path.name.lower()
                if name_lower.startswith('readme') or 'sample' in name_lower:
                    continue
                if suffix in ('.txt', '.kql', '.yaml', '.yml'):
                    names = _extract_legacy_parser_names(file_path)
                    all_names.update(names)
                    legacy_parser_count += 1
    log_print(f"    Found {legacy_parser_count} legacy parser files in /Parsers/*/")
    
    # Solution parsers
    solution_parser_count = 0
    if solutions_dir.exists():
        for solution_dir in solutions_dir.iterdir():
            if not solution_dir.is_dir():
                continue
            for parser_folder in ["Parsers", "Parser"]:
                parsers_dir = solution_dir / parser_folder
                if not parsers_dir.exists():
                    continue
                for yaml_path in list(parsers_dir.rglob("*.yml")) + list(parsers_dir.rglob("*.yaml")):
                    names, _ = _extract_parser_details_from_file(yaml_path)
                    all_names.update(names)
                    solution_parser_count += 1
    log_print(f"    Found {solution_parser_count} solution parser files in Solutions/*/Parsers/")
    
    # Build normalized parser names for table extraction
    parser_names_normalized = {normalize_parser_name(p) for p in all_names}
    log_print(f"  Collected {len(all_names)} unique parser names")
    
    # Second pass: collect detailed metadata
    log_print("  Pass 2: Extracting detailed metadata...")
    # Legacy parsers from /Parsers/*
    legacy_record_count = 0
    if legacy_parsers_dir.exists():
        legacy_subdirs = [d for d in legacy_parsers_dir.iterdir() if d.is_dir() and not d.name.lower().startswith('asim')]
        for subdir in legacy_subdirs:
            for file_path in subdir.iterdir():
                if not file_path.is_file():
                    continue
                suffix = file_path.suffix.lower()
                name_lower = file_path.name.lower()
                if name_lower.startswith('readme') or 'sample' in name_lower:
                    continue
                if suffix in ('.txt', '.kql', '.yaml', '.yml'):
                    record = _extract_parser_record(
                        file_path, 
                        repo_root,
                        solution_name="",
                        solution_folder="",
                        parser_names_normalized=parser_names_normalized,
                    )
                    if record:
                        parser_records.append(record)
                        legacy_record_count += 1
                        for name in record.get("parser_names", []):
                            all_names.add(name)
                            name_lower = name.lower()
                            tables = record.get("tables", "")
                            if tables:
                                all_tables_by_parser[name_lower].update(t.strip() for t in tables.split(",") if t.strip())
    log_print(f"    Processed {legacy_record_count} legacy parser records")
    
    # Solution parsers
    solution_record_count = 0
    if solutions_dir.exists():
        solution_dirs = [d for d in solutions_dir.iterdir() if d.is_dir()]
        log_print(f"    Scanning {len(solution_dirs)} solutions for parsers...")
        for sol_idx, solution_dir in enumerate(sorted(solution_dirs, key=lambda p: p.name.lower()), 1):
            solution_folder = solution_dir.name
            # Get solution name from metadata
            solution_info = collect_solution_info(solution_dir)
            solution_name = solution_info.get("solution_name", solution_folder)
            
            # Load Solution JSON to check if parsers are documented
            solution_json = find_solution_json(solution_dir)
            json_items = get_content_items_from_solution_json(solution_json)
            json_parser_basenames = json_items.get("parser", set())
            
            solution_parsers_found = 0
            for parser_folder in ["Parsers", "Parser"]:
                parsers_dir = solution_dir / parser_folder
                if not parsers_dir.exists():
                    continue
                for parser_path in list(parsers_dir.rglob("*.yml")) + list(parsers_dir.rglob("*.yaml")) + list(parsers_dir.rglob("*.kql")) + list(parsers_dir.rglob("*.txt")):
                    # Skip readme and sample files
                    name_lower = parser_path.name.lower()
                    if name_lower.startswith('readme') or 'sample' in name_lower:
                        continue
                    record = _extract_parser_record(
                        parser_path,
                        repo_root,
                        solution_name=solution_name,
                        solution_folder=solution_folder,
                        parser_names_normalized=parser_names_normalized,
                    )
                    if record:
                        # Check if parser is in Solution JSON (discovered vs documented)
                        basename_lower = parser_path.name.lower()
                        record["discovered"] = "true" if basename_lower not in json_parser_basenames else "false"
                        parser_records.append(record)
                        solution_record_count += 1
                        solution_parsers_found += 1
                        for name in record.get("parser_names", []):
                            all_names.add(name)
                            name_lower = name.lower()
                            tables = record.get("tables", "")
                            if tables:
                                all_tables_by_parser[name_lower].update(t.strip() for t in tables.split(",") if t.strip())
            
            # Log progress every 50 solutions or if this solution had parsers
            if sol_idx % 50 == 0:
                log_print(f"    [{sol_idx}/{len(solution_dirs)}] Processed {solution_record_count} solution parsers so far")
    log_print(f"    Processed {solution_record_count} solution parser records")
    
    return parser_records, all_names, dict(all_tables_by_parser)


def _extract_parser_record(
    file_path: Path,
    repo_root: Path,
    solution_name: str,
    solution_folder: str,
    parser_names_normalized: Set[str],
) -> Optional[Dict[str, Any]]:
    """Extract detailed parser record from a parser file.
    
    Returns a dict with parser metadata suitable for CSV export.
    Uses caching to avoid re-processing unchanged files.
    """
    # Check cache first
    cached = get_cached_analysis(file_path, "parsers")
    if cached is not None:
        # Update solution info in cached result (may have changed)
        cached["solution_name"] = solution_name
        cached["solution_folder"] = solution_folder
        cached["solution_github_url"] = f"{GITHUB_REPO_URL}/Solutions/{quote(solution_folder)}" if solution_folder else ""
        cached["location"] = "solution" if solution_folder else "legacy"
        return cached
    
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return None
    
    suffix = file_path.suffix.lower()
    is_yaml = suffix in ('.yaml', '.yml')
    
    # Extract parser names
    if is_yaml:
        lines = content.splitlines()
        parser_names = list(_extract_parser_names_from_lines(lines))
        queries = _extract_function_queries_from_lines(lines)
        query = "\n".join(queries) if queries else ""
    else:
        parser_names = list(_extract_legacy_parser_names(file_path))
        query = _extract_legacy_parser_query(file_path)
    
    if not parser_names:
        # Use filename as fallback
        parser_names = [file_path.stem]
    
    # Extract tables from query
    tables: Set[str] = set()
    if query:
        tables = extract_query_table_tokens(
            query, {}, {},
            allow_parser_tokens=True,
            known_parser_names=parser_names_normalized,
        )
    
    # Filter out non-table tokens (variable names, etc.)
    valid_tables = {t for t in tables if is_valid_table_candidate(t)}
    
    # Extract filter fields from the parser query
    filter_fields_str = ""
    if query:
        ff = extract_filter_fields_from_query(query, valid_tables)
        filter_fields_str = format_filter_fields(ff)
    
    # Extract additional metadata from YAML files
    title = ""
    version = ""
    last_updated = ""
    category = ""
    description = ""
    
    if is_yaml:
        for line in content.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip().strip('"\'').lower()
            value = _strip_quoted(value.split("#", 1)[0])
            
            if key == "title" and not title:
                title = value
            elif key == "version" and not version:
                version = value
            elif key == "lastupdated" and not last_updated:
                last_updated = value
            elif key == "category" and not category:
                category = value
            elif key == "description" and not description:
                description = value[:500] if value else ""  # Limit description length
    
    # Build relative path and GitHub URL
    try:
        rel_path = file_path.relative_to(repo_root)
        source_file = str(rel_path).replace("\\", "/")
        # URL-encode path components for GitHub URL (spaces become %20, etc.)
        encoded_parts = [quote(part, safe='') for part in source_file.split('/')]
        encoded_path = '/'.join(encoded_parts)
        github_url = f"https://github.com/Azure/Azure-Sentinel/blob/master/{encoded_path}"
    except ValueError:
        source_file = file_path.name
        github_url = ""
    
    # Determine parser location type
    if solution_folder:
        location = "solution"
    else:
        location = "legacy"
    
    record = {
        "parser_name": parser_names[0] if parser_names else file_path.stem,
        "parser_names": parser_names,
        "parser_title": title or parser_names[0] if parser_names else file_path.stem,
        "parser_version": version,
        "parser_last_updated": last_updated,
        "parser_category": category,
        "description": description,
        "tables": ", ".join(sorted(valid_tables)),
        "filter_fields": filter_fields_str,
        "source_file": source_file,
        "github_url": github_url,
        "solution_name": solution_name,
        "solution_folder": solution_folder,
        "solution_github_url": f"{GITHUB_REPO_URL}/Solutions/{quote(solution_folder)}" if solution_folder else "",
        "location": location,
        "file_type": suffix.lstrip('.'),
        "discovered": "false",  # Default to false, set to true for solution parsers not in Solution JSON
    }
    
    # Cache the result (without solution-specific fields that may change)
    cache_record = {k: v for k, v in record.items() if k not in ("solution_name", "solution_folder", "solution_github_url", "location")}
    set_cached_analysis(file_path, "parsers", cache_record)
    
    return record


def write_parsers_csv(parser_records: List[Dict[str, Any]], output_path: Path) -> None:
    """Write parser records to CSV file."""
    if not parser_records:
        log_print("  No parser records to write")
        return
    
    fieldnames = [
        "parser_name",
        "parser_title",
        "parser_version",
        "parser_last_updated",
        "parser_category",
        "description",
        "tables",
        "filter_fields",
        "source_file",
        "github_url",
        "solution_name",
        "solution_folder",
        "solution_github_url",
        "location",
        "file_type",
        "discovered",
    ]
    
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore', quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for record in parser_records:
            writer.writerow(record)
    
    log_print(f"  Wrote {len(parser_records)} parser records to {output_path}")


def collect_legacy_parsers(parsers_dir: Path) -> Tuple[Set[str], Dict[str, Set[str]]]:
    """Collect parser names and their table mappings from the top-level Parsers directory.
    
    These are legacy parsers (pre-Solutions) stored as .txt, .kql, or .yaml files.
    Parser names are extracted from:
    - The filename (without extension) for .txt and .kql files
    - Comments like "alias as ParserName" or "alias of ParserName" in .txt files  
    - FunctionName/FunctionAlias fields in .yaml files
    
    Args:
        parsers_dir: Path to the top-level Parsers directory
        
    Returns:
        Tuple of (parser_names, parser_to_tables_map)
    """
    names: Set[str] = set()
    tables_by_parser: Dict[str, Set[str]] = defaultdict(set)
    
    if not parsers_dir.exists():
        return names, tables_by_parser
    
    # Collect all parser files (skip README, sample data, and config files)
    parser_files: List[Path] = []
    for subdir in parsers_dir.iterdir():
        if not subdir.is_dir():
            continue
        for file_path in subdir.iterdir():
            if not file_path.is_file():
                continue
            suffix = file_path.suffix.lower()
            name_lower = file_path.name.lower()
            # Skip readme, sample data, and config files
            if name_lower.startswith('readme') or 'sample' in name_lower:
                continue
            if suffix in ('.txt', '.kql', '.yaml', '.yml'):
                parser_files.append(file_path)
    
    # First pass: collect all parser names
    for file_path in parser_files:
        parser_names_found = _extract_legacy_parser_names(file_path)
        names.update(parser_names_found)
    
    # Build normalized parser names for the second pass
    parser_names_normalized = {normalize_parser_name(p) for p in names}
    
    # Second pass: extract tables with knowledge of all parser names
    for file_path in parser_files:
        parser_names_found = _extract_legacy_parser_names(file_path)
        if not parser_names_found:
            continue
        
        query = _extract_legacy_parser_query(file_path)
        if not query:
            continue
            
        parser_tables: Set[str] = set()
        parser_tables.update(extract_query_table_tokens(
            query, {}, {},
            allow_parser_tokens=True,
            known_parser_names=parser_names_normalized,
        ))
        
        if not parser_tables:
            continue
            
        for parser_name in parser_names_found:
            lowered = parser_name.lower()
            if lowered:
                tables_by_parser.setdefault(lowered, set()).update(parser_tables)
    
    return names, tables_by_parser


def _extract_legacy_parser_names(file_path: Path) -> Set[str]:
    """Extract parser name(s) from a legacy parser file.
    
    For .txt and .kql files:
    - Look for comments like "alias as ParserName" or "alias of ParserName"
    - Fall back to filename without extension
    
    For .yaml files:
    - Look for FunctionName or FunctionAlias fields
    """
    names: Set[str] = set()
    suffix = file_path.suffix.lower()
    
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return names
    
    if suffix in ('.yaml', '.yml'):
        # Use existing YAML parser extraction
        lines = content.splitlines()
        names.update(_extract_parser_names_from_lines(lines))
    else:
        # For .txt and .kql files, look for alias comments
        # Patterns: "alias as ParserName", "alias of ParserName"  
        import re
        alias_patterns = [
            r'alias\s+(?:as|of)\s+(\w+)',  # "alias as X" or "alias of X"
            r'function\s+name\s+(?:and\s+)?alias\s+(?:as|of)?\s*(\w+)',  # "function name and alias as X"
        ]
        for pattern in alias_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                names.add(match.group(1))
        
        # Fall back to filename if no alias found in comments
        if not names:
            # Remove extension and use as name
            stem = file_path.stem
            if stem and not stem.lower().startswith('readme'):
                names.add(stem)
    
    return names


def _extract_legacy_parser_query(file_path: Path) -> str:
    """Extract the KQL query from a legacy parser file.
    
    For .txt and .kql files: Return the file content (it's the query)
    For .yaml files: Extract from FunctionQuery field
    """
    suffix = file_path.suffix.lower()
    
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return ""
    
    if suffix in ('.yaml', '.yml'):
        # Use existing YAML parser extraction
        lines = content.splitlines()
        queries = _extract_function_queries_from_lines(lines)
        return "\n".join(queries)
    else:
        # For .txt and .kql files, the content IS the query
        # Strip comment lines for cleaner processing
        lines = content.splitlines()
        query_lines = []
        for line in lines:
            stripped = line.strip()
            # Skip comment-only lines
            if stripped.startswith('//'):
                continue
            query_lines.append(line)
        return "\n".join(query_lines)


def collect_parser_metadata(solution_dir: Path) -> Tuple[Set[str], Dict[str, Set[str]]]:
    """Collect parser names and their table mappings from solution's Parsers directory.
    
    Supports both 'Parsers' and 'Parser' folder names.
    """
    names: Set[str] = set()
    tables_by_parser: Dict[str, Set[str]] = defaultdict(set)
    
    # Support both "Parsers" (common) and "Parser" (some solutions) folder naming
    parsers_dirs = [
        solution_dir / "Parsers",
        solution_dir / "Parser",
    ]
    
    for parsers_dir in parsers_dirs:
        if not parsers_dir.exists():
            continue

        # First pass: collect all parser names
        for yaml_path in list(parsers_dir.rglob("*.yml")) + list(parsers_dir.rglob("*.yaml")):
            parser_names_found, _ = _extract_parser_details_from_file(yaml_path)
            names.update(parser_names_found)
    
    # Build normalized parser names for the second pass
    # This allows union parsers to reference sub-parsers
    parser_names_normalized = {normalize_parser_name(p) for p in names}
    
    for parsers_dir in parsers_dirs:
        if not parsers_dir.exists():
            continue

        # Second pass: extract tables with knowledge of all parser names
        for yaml_path in list(parsers_dir.rglob("*.yml")) + list(parsers_dir.rglob("*.yaml")):
            parser_names_found, function_queries = _extract_parser_details_from_file(yaml_path)
            if not parser_names_found and not function_queries:
                continue
            parser_tables: Set[str] = set()
            for query in function_queries:
                # Pass known parser names so sub-parser references are recognized
                parser_tables.update(extract_query_table_tokens(
                    query, {}, {},
                    allow_parser_tokens=True,
                    known_parser_names=parser_names_normalized,
                ))
            if not parser_tables:
                continue
            for parser_name in parser_names_found:
                lowered = parser_name.lower()
                if lowered:
                    tables_by_parser.setdefault(lowered, set()).update(parser_tables)

    return names, tables_by_parser


def _strip_quoted(value: str) -> str:
    value = value.strip()
    if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
        return value[1:-1]
    return value


def _extract_parser_details_from_file(path: Path) -> Tuple[Set[str], List[str]]:
    names: Set[str] = set()
    queries: List[str] = []
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return names, queries
    lines = content.splitlines()
    names.update(_extract_parser_names_from_lines(lines))
    queries.extend(_extract_function_queries_from_lines(lines))
    return names, queries


def _extract_parser_names_from_lines(lines: List[str]) -> Set[str]:
    names: Set[str] = set()
    for raw_line in lines:
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        key = key.strip().strip("\"'")
        if key.lower() not in PARSER_NAME_KEYS:
            continue
        cleaned = _strip_quoted(value.split("#", 1)[0])
        if cleaned:
            names.add(cleaned)
    return names


def _extract_function_queries_from_lines(lines: List[str]) -> List[str]:
    queries: List[str] = []
    idx = 0
    total = len(lines)
    while idx < total:
        line = lines[idx]
        stripped = line.strip()
        if ":" not in line:
            idx += 1
            continue
        key, value = line.split(":", 1)
        if key.strip().lower() != "functionquery":
            idx += 1
            continue
        remainder = value.strip()
        if remainder and not remainder.startswith(("|", ">")):
            queries.append(_strip_quoted(remainder))
            idx += 1
            continue
        block, new_index = _capture_block_scalar(lines, idx)
        if block:
            queries.append(block)
        idx = new_index + 1
    return queries


def _capture_block_scalar(lines: List[str], start_index: int) -> Tuple[str, int]:
    buffer: List[str] = []
    block_indent: Optional[int] = None
    idx = start_index + 1
    total = len(lines)
    while idx < total:
        line = lines[idx]
        stripped = line.rstrip("\n")
        if stripped.strip() == "" and block_indent is None:
            buffer.append("")
            idx += 1
            continue
        current_indent = len(line) - len(line.lstrip(" "))
        if block_indent is None and stripped.strip() != "":
            block_indent = current_indent
        if block_indent is not None and stripped.strip() != "" and current_indent < block_indent:
            break
        if block_indent is None:
            buffer.append("")
        else:
            buffer.append(line[block_indent:])
        idx += 1
    joined = "\n".join(buffer).rstrip("\n")
    return joined, idx - 1 if idx <= total else total - 1


def load_asim_parsers(repo_root: Path) -> Tuple[Set[str], Dict[str, Set[str]], Dict[str, str]]:
    """
    Load ASIM parsers from /Parsers/ASim*/Parsers directories.
    
    Returns:
        - parser_names: Set of all ASIM parser names (both ParserName and EquivalentBuiltInParser)
        - parser_table_map: Dict mapping parser name (lowercased) to tables/sub-parsers it references
        - parser_alias_map: Dict mapping EquivalentBuiltInParser to ParserName (both lowercased)
    """
    try:
        import yaml
    except ImportError:
        log_print("  Warning: PyYAML not installed, skipping ASIM parser loading")
        return set(), {}, {}
    
    parsers_dir = repo_root / "Parsers"
    parser_names: Set[str] = set()
    parser_table_map: Dict[str, Set[str]] = defaultdict(set)
    parser_alias_map: Dict[str, str] = {}  # Maps EquivalentBuiltInParser -> ParserName
    
    if not parsers_dir.exists():
        return parser_names, parser_table_map, parser_alias_map
    
    # Find all ASim* directories
    asim_dirs = [d for d in parsers_dir.iterdir() if d.is_dir() and d.name.startswith("ASim")]
    
    for asim_dir in asim_dirs:
        parsers_subdir = asim_dir / "Parsers"
        if not parsers_subdir.exists():
            continue
        
        for yaml_path in list(parsers_subdir.glob("*.yaml")) + list(parsers_subdir.glob("*.yml")):
            try:
                content = yaml_path.read_text(encoding="utf-8")
                data = yaml.safe_load(content)
                if not isinstance(data, dict):
                    continue
                
                parser_name = data.get("ParserName", "")
                equivalent_builtin = data.get("EquivalentBuiltInParser", "")
                parser_query = data.get("ParserQuery", "")
                sub_parsers = data.get("Parsers", [])  # List of sub-parser references
                
                if parser_name:
                    parser_names.add(parser_name)
                    parser_name_lower = parser_name.lower()
                    
                    # Extract tables from the parser query
                    if parser_query:
                        tables = extract_query_table_tokens(parser_query, {}, {})
                        parser_table_map[parser_name_lower].update(tables)
                    
                    # Add sub-parser references (these will be expanded recursively later)
                    if isinstance(sub_parsers, list):
                        for sub_parser in sub_parsers:
                            if isinstance(sub_parser, str) and sub_parser.strip():
                                parser_table_map[parser_name_lower].add(sub_parser.strip())
                
                # Map the EquivalentBuiltInParser to the ParserName
                if equivalent_builtin and parser_name:
                    parser_names.add(equivalent_builtin)
                    equivalent_lower = equivalent_builtin.lower()
                    parser_name_lower = parser_name.lower()
                    parser_alias_map[equivalent_lower] = parser_name_lower
                    # Also make the equivalent name point to the same tables
                    if parser_name_lower in parser_table_map:
                        parser_table_map[equivalent_lower] = parser_table_map[parser_name_lower]
                    
            except Exception:
                continue
    
    return parser_names, dict(parser_table_map), parser_alias_map


def _process_asim_parser_file(
    yaml_path: Path,
    schema_name: str,
    repo_root: Path,
) -> Optional[Dict[str, Any]]:
    """
    Process a single ASIM parser YAML file and return the parser record.
    Uses caching to avoid re-processing unchanged files.
    
    Args:
        yaml_path: Path to the YAML file
        schema_name: The ASIM schema name (e.g., "Dns", "NetworkSession")
        repo_root: Root of the repository
        
    Returns:
        Parser record dict, or None if the file should be skipped
    """
    try:
        import yaml
    except ImportError:
        return None
    
    # Check cache first
    cached = get_cached_analysis(yaml_path, "asim")
    if cached is not None:
        return cached
    
    try:
        content = yaml_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        if not isinstance(data, dict):
            return None
        
        # Extract all available fields
        parser_info = data.get("Parser", {}) if isinstance(data.get("Parser"), dict) else {}
        product_info = data.get("Product", {}) if isinstance(data.get("Product"), dict) else {}
        normalization_info = data.get("Normalization", {}) if isinstance(data.get("Normalization"), dict) else {}
        references = data.get("References", []) if isinstance(data.get("References"), list) else []
        
        parser_name = data.get("ParserName", "")
        equivalent_builtin = data.get("EquivalentBuiltInParser", "")
        parser_query = data.get("ParserQuery", "")
        
        # Skip vim* parsers - they have the same filters as their ASim* equivalents
        if parser_name.lower().startswith('vim'):
            set_cached_analysis(yaml_path, "asim", None)
            return None
        
        sub_parsers = data.get("Parsers", [])
        parser_params = data.get("ParserParams", [])
        description = data.get("Description", "")
        
        # Skip if no parser name
        if not parser_name:
            set_cached_analysis(yaml_path, "asim", None)
            return None
        
        # Extract tables from the parser query
        tables: Set[str] = set()
        if parser_query:
            tables = extract_query_table_tokens(parser_query, {}, {})
        
        # Handle sub-parser references
        sub_parsers_list = []
        if isinstance(sub_parsers, list):
            for sub_parser in sub_parsers:
                if isinstance(sub_parser, str) and sub_parser.strip():
                    sub_parsers_list.append(sub_parser.strip())
        
        # Determine parser type
        parser_type = "source"
        if sub_parsers_list:
            parser_type = "union"
        elif parser_name.lower().endswith("empty") or "empty" in yaml_path.name.lower():
            parser_type = "empty"
        
        # Format references as semicolon-separated list
        ref_links = []
        for ref in references:
            if isinstance(ref, dict):
                title = ref.get("Title", "")
                link = ref.get("Link", "")
                if title and link:
                    ref_links.append(f"[{title}]({link})")
                elif link:
                    ref_links.append(link)
        
        # Format parser params
        params_list = []
        if isinstance(parser_params, list):
            for param in parser_params:
                if isinstance(param, dict):
                    param_name = param.get("Name", "")
                    param_type = param.get("Type", "")
                    param_default = param.get("Default", "")
                    if param_name:
                        params_list.append(f"{param_name}:{param_type}={param_default}")
        
        # Extract filter fields from the parser query
        filter_fields_str = ""
        if parser_query:
            limit_table = None
            if 'Syslog' in tables:
                limit_table = 'Syslog'
            ff = extract_filter_fields_from_query(
                parser_query, tables,
                skip_asim_vendor_product=True,
                limit_to_table_let_block=limit_table
            )
            filter_fields_str = format_filter_fields(ff)
        
        # Build the record
        record = {
            "parser_name": parser_name,
            "equivalent_builtin": equivalent_builtin,
            "schema": normalization_info.get("Schema", schema_name),
            "schema_version": normalization_info.get("Version", ""),
            "parser_type": parser_type,
            "parser_title": parser_info.get("Title", ""),
            "parser_version": parser_info.get("Version", ""),
            "parser_last_updated": parser_info.get("LastUpdated", ""),
            "product_name": product_info.get("Name", ""),
            "description": description.strip() if description else "",
            "tables": ";".join(sorted(tables)) if tables else "",
            "sub_parsers": ";".join(sub_parsers_list) if sub_parsers_list else "",
            "parser_params": ";".join(params_list) if params_list else "",
            "filter_fields": filter_fields_str,
            "references": ";".join(ref_links) if ref_links else "",
            "source_file": str(yaml_path.relative_to(repo_root)),
            "github_url": f"https://github.com/Azure/Azure-Sentinel/blob/master/{yaml_path.relative_to(repo_root).as_posix()}",
        }
        
        # Cache the result
        set_cached_analysis(yaml_path, "asim", record)
        return record
        
    except Exception:
        return None


def load_asim_parsers_detailed(repo_root: Path) -> Tuple[List[Dict[str, Any]], Set[str], Dict[str, Set[str]], Dict[str, str]]:
    """
    Load ASIM parsers from /Parsers/ASim*/Parsers directories with full metadata for CSV export.
    
    Returns:
        - parser_records: List of dicts with all parser metadata for CSV export
        - parser_names: Set of all ASIM parser names (both ParserName and EquivalentBuiltInParser)
        - parser_table_map: Dict mapping parser name (lowercased) to tables/sub-parsers it references
        - parser_alias_map: Dict mapping EquivalentBuiltInParser to ParserName (both lowercased)
    """
    try:
        import yaml
    except ImportError:
        log_print("  Warning: PyYAML not installed, skipping ASIM parser loading")
        return [], set(), {}, {}
    
    parsers_dir = repo_root / "Parsers"
    parser_records: List[Dict[str, Any]] = []
    parser_names: Set[str] = set()
    parser_table_map: Dict[str, Set[str]] = defaultdict(set)
    parser_alias_map: Dict[str, str] = {}
    
    if not parsers_dir.exists():
        return parser_records, parser_names, parser_table_map, parser_alias_map
    
    # Find all ASim* directories
    asim_dirs = [d for d in parsers_dir.iterdir() if d.is_dir() and d.name.startswith("ASim")]
    log_print(f"  Found {len(asim_dirs)} ASIM schema directories")
    
    for dir_idx, asim_dir in enumerate(sorted(asim_dirs), 1):
        parsers_subdir = asim_dir / "Parsers"
        if not parsers_subdir.exists():
            continue
        
        # Extract schema name from directory (e.g., "ASimDns" -> "Dns", "ASimNetworkSession" -> "NetworkSession")
        schema_name = asim_dir.name
        if schema_name.startswith("ASim"):
            schema_name = schema_name[4:]  # Remove "ASim" prefix
        
        yaml_files = sorted(list(parsers_subdir.glob("*.yaml")) + list(parsers_subdir.glob("*.yml")))
        log_print(f"  [{dir_idx}/{len(asim_dirs)}] Processing {asim_dir.name}: {len(yaml_files)} parser files")
        
        cache_hits = 0
        for yaml_path in yaml_files:
            # Use helper function with caching
            record = _process_asim_parser_file(yaml_path, schema_name, repo_root)
            if record is None:
                continue
            
            # Check if this was a cache hit (record already existed)
            cached = get_cached_analysis(yaml_path, "asim")
            if cached is not None:
                cache_hits += 1
            
            parser_records.append(record)
            
            # Extract parser names and table mappings from the record
            pname = record.get("parser_name", "")
            equivalent_builtin = record.get("equivalent_builtin", "")
            tables_str = record.get("tables", "")
            sub_parsers_str = record.get("sub_parsers", "")
            
            if pname:
                parser_names.add(pname)
                parser_name_lower = pname.lower()
                
                # Add tables
                if tables_str:
                    for t in tables_str.split(";"):
                        if t.strip():
                            parser_table_map[parser_name_lower].add(t.strip())
                
                # Add sub-parsers
                if sub_parsers_str:
                    for sp in sub_parsers_str.split(";"):
                        if sp.strip():
                            parser_table_map[parser_name_lower].add(sp.strip())
                
                # Handle equivalent builtin
                if equivalent_builtin:
                    parser_names.add(equivalent_builtin)
                    equivalent_lower = equivalent_builtin.lower()
                    parser_alias_map[equivalent_lower] = parser_name_lower
                    if parser_name_lower in parser_table_map:
                        parser_table_map[equivalent_lower] = parser_table_map[parser_name_lower]
        
        if cache_hits > 0:
            log_print(f"    ({cache_hits} from cache)")
    
    return parser_records, parser_names, dict(parser_table_map), parser_alias_map


def write_asim_parsers_csv(parser_records: List[Dict[str, Any]], output_path: Path) -> None:
    """Write ASIM parser records to CSV file."""
    if not parser_records:
        log_print("  No ASIM parser records to write")
        return
    
    fieldnames = [
        "parser_name",
        "equivalent_builtin",
        "schema",
        "schema_version",
        "parser_type",
        "parser_title",
        "parser_version",
        "parser_last_updated",
        "product_name",
        "description",
        "tables",
        "sub_parsers",
        "parser_params",
        "filter_fields",
        "associated_connectors",
        "associated_solutions",
        "references",
        "source_file",
        "github_url",
    ]
    
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for record in parser_records:
            writer.writerow(record)
    
    log_print(f"  Wrote {len(parser_records)} ASIM parser records to {output_path}")


def normalize_parser_name(name: str) -> str:
    """
    Normalize a parser name for consistent lookups.
    
    Handles:
    - ASIM parsers with inconsistent underscore prefixes (_ASim_* vs ASim_*)
    - Parser names with file extensions (.kql, .yaml, .txt)
    
    This normalizes to lowercase form without underscore prefix or extensions.
    """
    lowered = name.lower()
    # Remove common file extensions
    for ext in ('.kql', '.yaml', '.yml', '.txt'):
        if lowered.endswith(ext):
            lowered = lowered[:-len(ext)]
            break
    # Remove leading underscore (ASIM naming variation)
    if lowered.startswith('_'):
        return lowered[1:]
    return lowered


def is_parser_name(name: str, parser_names_normalized: Set[str]) -> bool:
    """Check if a name matches a known parser name (handling underscore variations)."""
    normalized = normalize_parser_name(name)
    return normalized in parser_names_normalized


def expand_parser_tables(parser_name: str, parser_table_map: Dict[str, Set[str]], max_depth: int = 5) -> Set[str]:
    """
    Expand a parser name to its underlying tables by recursively resolving sub-parsers.
    
    Handles parser naming variations:
    - ASIM parsers: _ASim_* / ASim_* (underscore prefix variations)
    - File extensions: parser.kql / parser (extension variations)
    """
    visited: Set[str] = set()
    
    def _normalize_parser_key(name: str) -> List[str]:
        """Return possible key variations for a parser name."""
        lowered = name.lower()
        keys = [lowered]
        
        # Strip common file extensions to get base name
        base = lowered
        has_extension = False
        for ext in ('.kql', '.yaml', '.yml', '.txt'):
            if base.endswith(ext):
                base = base[:-len(ext)]
                has_extension = True
                keys.append(base)
                break
        
        # If no extension, try adding common extensions
        if not has_extension:
            for ext in ('.kql', '.yaml', '.yml'):
                keys.append(base + ext)
        
        # Add underscore prefix variations for all forms
        for key in list(keys):  # Iterate over copy since we're modifying
            if key.startswith('_'):
                keys.append(key[1:])
            else:
                keys.append('_' + key)
        
        return list(set(keys))  # Deduplicate

    def _walk(name: str, depth: int) -> Set[str]:
        lowered = name.lower()
        if not lowered or lowered in visited or depth > max_depth:
            return set()
        visited.add(lowered)
        
        # Try different key variations
        direct = None
        for key in _normalize_parser_key(name):
            if key in parser_table_map:
                direct = parser_table_map[key]
                break
        
        if not direct:
            return set()
        resolved: Set[str] = set()
        for candidate in direct:
            candidate_lower = candidate.lower()
            # Check if candidate is a parser using normalized keys
            is_parser = any(k in parser_table_map for k in _normalize_parser_key(candidate))
            if is_parser:
                resolved.update(_walk(candidate, depth + 1))
            else:
                resolved.add(candidate)
        return resolved or set(direct)

    return _walk(parser_name, 0)


def _collect_values_for_key(obj: Any, key: str) -> List[str]:
    values: List[str] = []

    def walk(node: Any) -> None:  # noqa: ANN401
        if isinstance(node, dict):
            for current_key, value in node.items():
                if current_key == key and isinstance(value, str):
                    values.append(value)
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(obj)
    return values


def _resolve_arm_reference(value: Optional[str], variables: Optional[Dict[str, Any]], depth: int = 0) -> Optional[str]:
    if not isinstance(value, str) or depth > 5:
        return None
    trimmed = value.strip().strip('"').strip("'")
    if not trimmed:
        return None
    match = ARM_VARIABLE_PATTERN.fullmatch(trimmed)
    if match and isinstance(variables, dict):
        lookup_key = match.group(1)
        replacement = variables.get(lookup_key)
        if isinstance(replacement, str):
            return _resolve_arm_reference(replacement, variables, depth + 1) or replacement.strip()
        return None
    if trimmed.startswith("[") and trimmed.endswith("]"):
        return None
    return trimmed


def extract_log_analytics_tables(data: Any) -> Set[str]:
    tables: Set[str] = set()
    variables = data.get("variables") if isinstance(data, dict) else None
    for raw_value in _collect_values_for_key(data, "logAnalyticsTableId"):
        resolved = _resolve_arm_reference(raw_value, variables) or raw_value.strip()
        cleaned = resolved.strip('"').strip("'") if isinstance(resolved, str) else ""
        if cleaned:
            tables.add(cleaned)
    return tables


def determine_collection_method(
    connector_id: str,
    connector_title: str,
    connector_description: str,
    json_content: Optional[str] = None,
    filename: Optional[str] = None,
    table_metadata: Optional[List[Dict[str, str]]] = None,
) -> Tuple[str, str, List[Tuple[str, str]]]:
    """
    Determine the data collection method based on connector metadata, JSON content, and table metadata.
    
    Collection Methods:
    - CCF (Codeless Connector Framework): Uses pollingConfig, RestApiPoller, CCP/CCF patterns
    - Azure Function: Uses Azure Functions to collect and ingest data
    - AMA (Azure Monitor Agent): Uses Azure Monitor Agent for CEF/Syslog collection
    - MMA (Log Analytics Agent): Legacy agent using workspace ID/key
    - Azure Diagnostics: Uses Azure diagnostic settings
    - REST API: Direct REST API integration
    - Native: Built-in Microsoft integrations
    
    Detection Priority:
    1. Explicit AMA/MMA in title (strongest indicator)
    2. Azure Diagnostics patterns
    3. Native Microsoft integrations
    4. CCF patterns (content-based)
    5. Azure Function patterns
    6. REST API patterns
    7. Table metadata fallback
    
    Args:
        connector_id: The connector identifier
        connector_title: The connector title
        connector_description: The connector description
        json_content: Optional JSON content from the connector definition file
        filename: Optional filename of the connector definition
        table_metadata: Optional list of table metadata dicts with 'category' and 'resource_types'
    
    Returns:
        Tuple of (collection_method, detection_reason, all_matches)
        where all_matches is a list of (method, reason) for all detected methods
    """
    # Normalize inputs for case-insensitive matching
    conn_id_lower = (connector_id or "").lower()
    conn_title_lower = (connector_title or "").lower()
    conn_desc_lower = (connector_description or "").lower()
    content = json_content or ""
    file_lower = (filename or "").lower()
    
    # Track all matching methods for reporting
    all_matches: List[Tuple[str, str]] = []
    
    # === PRIORITY 1: Explicit AMA/MMA in title only (strongest indicator) ===
    # Only title-based detection - must be explicit in connector name
    title_indicates_ama = ('AMA' in connector_title or 'via AMA' in connector_title or
                           'ama' in conn_id_lower.split('-') or conn_id_lower.endswith('ama'))
    title_indicates_mma = ('Legacy Agent' in connector_title or 'via Legacy Agent' in connector_title)
    
    # Special case: WindowsFirewall (without Ama suffix) is MMA
    if connector_id == 'WindowsFirewall':
        title_indicates_mma = True
    
    if title_indicates_ama:
        all_matches.append(("AMA", "Title/ID indicates AMA"))
    if title_indicates_mma:
        all_matches.append(("MMA", "Title mentions Legacy Agent"))
    
    # === PRIORITY 2: Azure Function Detection - FILENAME ONLY ===
    # Only filename-based detection at this priority - content patterns are lower
    is_azure_function_filename = False
    if 'functionapp' in file_lower or 'function_app' in file_lower or '_api_function' in file_lower:
        all_matches.append(("Azure Function", "Filename indicates Azure Function"))
        is_azure_function_filename = True
    if 'azurefunction' in conn_id_lower or 'functionapp' in conn_id_lower:
        all_matches.append(("Azure Function", "ID contains AzureFunction/FunctionApp"))
        is_azure_function_filename = True
    
    # === PRIORITY 3: CCF Content Detection (strong patterns - before Azure Diagnostics) ===
    is_ccf_content = False
    # CCF Push variant - uses DCR/DCE for partner push ingestion
    is_ccf_push = False
    if 'DeployPushConnectorButton' in content:
        all_matches.append(("CCF Push", "CCF Push connector (DCR/DCE based)"))
        is_ccf_push = True
        is_ccf_content = True
    # Check content-based patterns (more reliable than name-based)
    if 'pollingConfig' in content:
        all_matches.append(("CCF", "Has pollingConfig"))
        is_ccf_content = True
    if 'dcrConfig' in content and '"type"' in content and 'RestApiPoller' in content:
        all_matches.append(("CCF", "Has dcrConfig with RestApiPoller"))
        is_ccf_content = True
    if 'GCPAuthConfig' in content:
        all_matches.append(("CCF", "Has GCPAuthConfig"))
        is_ccf_content = True
    # dataConnectorDefinitions - but not if AMA is in title
    if 'dataConnectorDefinitions' in content and not title_indicates_ama:
        all_matches.append(("CCF", "Uses dataConnectorDefinitions"))
        is_ccf_content = True
    
    # === PRIORITY 4: Azure Diagnostics patterns (before CCF name patterns) ===
    is_azure_diagnostics = False
    if not is_azure_function_filename:
        if 'AzureDiagnostics' in content or 'diagnostic settings' in conn_desc_lower:
            all_matches.append(("Azure Diagnostics", "References Azure Diagnostics"))
            is_azure_diagnostics = True
        if 'Microsoft.Insights/diagnosticSettings' in content:
            all_matches.append(("Azure Diagnostics", "Uses diagnostic settings resource"))
            is_azure_diagnostics = True
        if 'policyDefinitionGuid' in content and 'PolicyAssignment' in content:
            all_matches.append(("Azure Diagnostics", "Uses Azure Policy for diagnostics"))
            is_azure_diagnostics = True
    
    # === PRIORITY 5: CCF Name-based Detection (lower priority - after Azure Diagnostics) ===
    # Only use name-based CCF if no Azure Diagnostics patterns found
    is_ccf_name = False
    if not is_azure_diagnostics:
        if ('ccp' in conn_id_lower or 'ccf' in conn_id_lower or 'codeless' in conn_title_lower):
            all_matches.append(("CCF", "ID/title contains CCP/CCF/Codeless"))
            is_ccf_name = True
        if 'polling' in conn_id_lower and 'function' not in conn_id_lower:
            all_matches.append(("CCF", "ID contains Polling pattern (CCF)"))
            is_ccf_name = True
    
    is_ccf = is_ccf_content or is_ccf_name
    
    # === PRIORITY 6: Azure Function Content Detection (lower priority) ===
    # Content-based Azure Function patterns - only if not already detected as CCF content
    is_azure_function_content = False
    if not is_ccf_content:
        if 'azure functions' in conn_desc_lower:
            all_matches.append(("Azure Function", "Description mentions Azure Functions"))
            is_azure_function_content = True
        if 'Deploy to Azure' in content and 'Function App' in content:
            all_matches.append(("Azure Function", "Deploy Azure Function pattern"))
            is_azure_function_content = True
        if 'Azure Function App' in content:
            all_matches.append(("Azure Function", "Content mentions Azure Function App"))
            is_azure_function_content = True
        if 'azure-functions' in content.lower() and 'pricing/details/functions' in content.lower():
            all_matches.append(("Azure Function", "References Azure Functions pricing"))
            is_azure_function_content = True
    
    is_azure_function = is_azure_function_filename or is_azure_function_content
    
    # === PRIORITY 7: Native Microsoft Integration (skip if CCF content detected) ===
    # Native patterns are broad, so only use if no CCF content patterns found
    is_native = False
    if not is_ccf_content:
        if 'SentinelKinds' in content:
            all_matches.append(("Native", "Uses SentinelKinds (Native integration)"))
            is_native = True
        if any(x in connector_title for x in ['Microsoft Defender', 'Microsoft 365', 'Office 365', 'Microsoft Entra ID']):
            all_matches.append(("Native", "Microsoft native integration"))
            is_native = True
        if any(x in connector_id for x in ['AzureActivity', 'AzureActiveDirectory', 'Office365', 'MicrosoftDefender']):
            all_matches.append(("Native", "Known native connector ID"))
            is_native = True
    
    # === PRIORITY 8: Additional AMA/MMA patterns (lower priority) ===
    if 'Azure Monitor Agent' in connector_description and 'AMA' in content:
        all_matches.append(("AMA", "Description mentions Azure Monitor Agent"))
    if 'sent_by_ama' in content:
        all_matches.append(("AMA", "Uses sent_by_ama field"))
    if 'CEF via AMA' in content or 'Syslog via AMA' in content:
        all_matches.append(("AMA", "References CEF/Syslog via AMA"))
    if 'cef_installer.py' in content:
        all_matches.append(("MMA", "Uses CEF installer script"))
    if 'omsagent' in content.lower():
        all_matches.append(("MMA", "References omsagent"))
    if 'Install the agent' in content and 'Syslog' in content and 'AMA' not in content:
        all_matches.append(("MMA", "Syslog with agent installation (no AMA)"))
    if ('workspaceId' in content.lower() and 'sharedKeys' in content.lower() and 
        'Azure Function' not in connector_description):
        all_matches.append(("MMA", "Uses workspace ID/key pattern"))
    
    # MMA-specific patterns: OmsSolutions and InstallAgentOn* instructions
    # These are MMA-era patterns that indicate the connector uses the legacy agent
    if '"solutionName"' in content and 'OmsSolutions' in content:
        all_matches.append(("MMA", "Uses OmsSolutions (MMA-era technology)"))
    if '"linkType":' in content and ('InstallAgentOnVirtualMachine' in content or 
                                      'InstallAgentOnNonAzure' in content or
                                      'InstallAgentOnLinuxNonAzure' in content):
        all_matches.append(("MMA", "Uses InstallAgent patterns (MMA-era)"))
    
    # === PRIORITY 9: REST API patterns ===
    if 'REST API' in connector_title or 'REST API' in connector_description:
        all_matches.append(("REST API", "Title/description mentions REST API"))
    if 'push' in conn_title_lower or 'push' in conn_id_lower:
        all_matches.append(("REST API", "Push connector (REST API based)"))
    if 'webhook' in conn_title_lower or ('webhook' in conn_desc_lower and 'http' in conn_desc_lower):
        all_matches.append(("REST API", "Webhook pattern (REST API based)"))
    if 'http endpoint' in conn_desc_lower or 'http trigger' in conn_desc_lower:
        all_matches.append(("REST API", "HTTP endpoint/trigger (REST API)"))
    
    # === PRIORITY 10: Table metadata-based detection (lowest content-based priority) ===
    # Only use if no stronger patterns detected - this is a fallback
    if table_metadata and not is_azure_function and not is_ccf and not is_native and not is_azure_diagnostics:
        for table_info in table_metadata:
            category = table_info.get('category', '')
            resource_types = table_info.get('resource_types', '').lower()
            
            # Azure Resources category -> Azure Diagnostics
            if category == 'Azure Resources':
                all_matches.append(("Azure Diagnostics", f"Table category is 'Azure Resources'"))
                break  # Only add once
            
            # virtualmachines in resource_types -> AMA
            if 'virtualmachines' in resource_types:
                all_matches.append(("AMA", f"Table resource_types includes 'virtualmachines'"))
                break  # Only add once
    
    # === PRIORITY 11: Custom log fallback ===
    if '_CL' in content and not all_matches:
        all_matches.append(("Unknown (Custom Log)", "Custom log table - needs analysis"))
    
    # Determine final method based on priority
    # Priority order reflects detection order - higher = selected first
    # Title-based AMA/MMA > Azure Function (filename) > CCF (content) > Azure Diagnostics > CCF (name) > Azure Function (content) > Native > AMA/MMA (content) > REST API
    # MMA from content patterns (OmsSolutions, InstallAgent) should take precedence over AMA from table metadata
    priority_order = ["Azure Diagnostics", "CCF Push", "CCF", "Azure Function", "Native", "MMA", "AMA", "REST API", "Unknown (Custom Log)", "Unknown"]
    
    # Special case: If title explicitly indicates AMA/MMA, prioritize that
    if title_indicates_ama:
        priority_order = ["AMA"] + [m for m in priority_order if m != "AMA"]
    elif title_indicates_mma:
        priority_order = ["MMA"] + [m for m in priority_order if m != "MMA"]
    
    if all_matches:
        # Select based on priority
        for method in priority_order:
            for match in all_matches:
                if match[0] == method:
                    return match[0], match[1], all_matches
    
    return "Unknown", "Method not detected", all_matches

def add_issue(
    issues: List[Dict[str, str]],
    *,
    solution_name: str,
    solution_folder: str,
    reason: str,
    details: str,
    connector_id: str = "",
    connector_title: str = "",
    connector_publisher: str = "",
    relevant_file: str = "",
) -> None:
    issues.append({
        "solution_name": solution_name,
        "solution_folder": solution_folder,
        "connector_id": connector_id,
        "connector_title": connector_title,
        "connector_publisher": connector_publisher,
        "relevant_file": relevant_file,
        "reason": reason,
        "details": details,
    })


# ============================================================================
# Content Items Extraction (Analytics Rules, Hunting Queries, Workbooks, etc.)
# ============================================================================

# Content type folder name variations (within solution directories)
CONTENT_TYPE_FOLDERS: Dict[str, List[str]] = {
    "analytic_rule": ["Analytic Rules", "Analytical Rules", "Analytics Rules"],
    "hunting_query": ["Hunting Queries"],
    "workbook": ["Workbooks", "Workbook"],
    "playbook": ["Playbooks", "Playbook"],
    "parser": ["Parsers", "Parser"],
    "watchlist": ["Watchlists"],
    "summary_rule": ["Summary Rules", "Summary rules"],
}

# Standalone content directories at repo root level
# Maps content type to (directory name, file type: 'yaml', 'json', or 'folder')
STANDALONE_CONTENT_DIRS: Dict[str, Tuple[str, str]] = {
    "analytic_rule": ("Detections", "yaml"),
    "hunting_query": ("Hunting Queries", "yaml"),
    "workbook": ("Workbooks", "json"),
    "playbook": ("Playbooks", "folder"),  # Each playbook is a folder
    "summary_rule": ("Summary rules", "yaml"),
    "watchlist": ("Watchlists", "folder"),  # Each watchlist is a folder
}

# Patterns that indicate a stub file (content moved to solutions)
STUB_FILE_PATTERNS = [
    r"moved\s+to\s+(new\s+)?location",
    r"as\s+part\s+of\s+content\s+migration",
    r"this\s+file\s+(is|has\s+been)\s+moved",
    r"content\s+has\s+been\s+migrated",
]

# Mapping from Solution JSON keys to our internal content types
# Some Solution JSONs use alternate key names (e.g., "AnalyticsRules" vs "Analytic Rules")
# so we support multiple keys per content type (case-insensitive matching applied at runtime)
SOLUTION_JSON_CONTENT_KEYS: Dict[str, List[str]] = {
    "analytic_rule": ["Analytic Rules", "AnalyticsRules", "Analytics Rules", "analyticRules"],
    "hunting_query": ["Hunting Queries", "HuntingQueries", "huntingQueries"],
    "workbook": ["Workbooks", "WorkBooks", "workbooks"],
    "playbook": ["Playbooks", "playbooks"],
    "parser": ["Parsers", "parsers"],
    "watchlist": ["Watchlists", "watchlists"],
    "data_connector": ["Data Connectors", "DataConnectors", "dataConnectors"],
    "summary_rule": ["SummaryRules", "Summary Rules", "summaryRules"],
}

def get_content_items_from_solution_json(solution_json: Optional[Dict[str, Any]]) -> Dict[str, Set[str]]:
    """
    Extract the list of content items from a Solution JSON file.
    
    The Solution JSON contains lists of content files for each content type.
    This function extracts and normalizes these file paths for comparison.
    
    Args:
        solution_json: Parsed Solution JSON data, or None if not found
    
    Returns:
        Dictionary mapping content type to set of normalized basenames (lowercase)
    """
    if not solution_json:
        return {}
    
    result: Dict[str, Set[str]] = {}
    
    for content_type, json_keys in SOLUTION_JSON_CONTENT_KEYS.items():
        basenames: Set[str] = set()
        # Try each possible key name for this content type
        for json_key in json_keys:
            items = solution_json.get(json_key, [])
            if items and isinstance(items, list):
                for item_path in items:
                    if isinstance(item_path, str) and item_path.strip():
                        # Normalize: extract basename and lowercase for comparison
                        basename = os.path.basename(item_path.strip()).lower()
                        if basename:
                            basenames.add(basename)
        if basenames:
            result[content_type] = basenames
    
    return result


def read_yaml_safe(path: Path) -> Optional[Dict[str, Any]]:
    """Read a YAML file safely, handling common issues."""
    try:
        import yaml
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        # Fallback to basic parsing if PyYAML not available
        return _parse_yaml_basic(path)
    except Exception as e:
        # Try basic parsing as fallback
        result = _parse_yaml_basic(path)
        if result:
            return result
        return None


def _parse_yaml_basic(path: Path) -> Optional[Dict[str, Any]]:
    """Basic YAML parsing for simple key: value structures."""
    try:
        content = path.read_text(encoding="utf-8")
        result: Dict[str, Any] = {}
        current_key = None
        multiline_value: List[str] = []
        in_multiline = False
        
        for line in content.splitlines():
            # Skip comments
            if line.strip().startswith("#"):
                continue
            
            # Check for multiline continuation
            if in_multiline:
                if line.startswith("  ") or line.startswith("\t"):
                    multiline_value.append(line.strip())
                    continue
                else:
                    # End of multiline
                    if current_key:
                        result[current_key] = "\n".join(multiline_value)
                    in_multiline = False
                    multiline_value = []
            
            # Parse key: value
            if ":" in line and not line.strip().startswith("-"):
                parts = line.split(":", 1)
                key = parts[0].strip().strip("'\"")
                value = parts[1].strip() if len(parts) > 1 else ""
                
                # Check for multiline indicator
                if value == "|" or value == ">":
                    current_key = key
                    in_multiline = True
                    multiline_value = []
                elif value.startswith("'") or value.startswith('"'):
                    result[key] = value.strip("'\"")
                elif value:
                    result[key] = value
                else:
                    current_key = key
        
        # Handle any remaining multiline content
        if in_multiline and current_key:
            result[current_key] = "\n".join(multiline_value)
        
        return result if result else None
    except Exception:
        return None


def extract_queries_from_workbook(data: Dict[str, Any]) -> List[str]:
    """Extract all KQL queries from a workbook JSON structure."""
    queries: List[str] = []
    
    def traverse(obj: Any) -> None:
        if isinstance(obj, dict):
            # Look for query fields
            if "query" in obj and isinstance(obj["query"], str):
                query = obj["query"]
                # Workbook queries often have \r\n or escaped characters
                query = query.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", "\t")
                queries.append(query)
            for value in obj.values():
                traverse(value)
        elif isinstance(obj, list):
            for item in obj:
                traverse(item)
    
    traverse(data)
    return queries


def is_stub_file(data: Dict[str, Any]) -> bool:
    """
    Check if a YAML file is a stub pointing to content moved to a solution.
    
    Stub files typically have:
    - Minimal fields (usually just id, name, description, version)
    - Description containing phrases like "moved to new location" or "content migration"
    - No query field
    
    Args:
        data: Parsed YAML data
        
    Returns:
        True if this is a stub file that should be ignored
    """
    if not isinstance(data, dict):
        return False
    
    # Check if it has a query - if it does, it's not a stub
    if data.get("query"):
        return False
    
    # Check description for stub patterns
    description = data.get("description", "")
    if isinstance(description, str):
        desc_lower = description.lower()
        for pattern in STUB_FILE_PATTERNS:
            if re.search(pattern, desc_lower, re.IGNORECASE):
                return True
    
    return False


def extract_yaml_metadata(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract metadata section from a YAML content file.
    
    The metadata section indicates the content is a standalone Content Hub item.
    Format:
        metadata:
            source:
                kind: Community|Solution
            author:
                name: Author Name
            support:
                tier: Community|Partner|Microsoft
            categories:
                domains: [ "Security - Others" ]
    
    Args:
        data: Parsed YAML data
        
    Returns:
        Dict with extracted metadata fields, empty if no metadata section
    """
    result = {
        "metadata_source_kind": "",
        "metadata_author": "",
        "metadata_support_tier": "",
        "metadata_categories": "",
    }
    
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        return result
    
    # Extract source kind
    source = metadata.get("source")
    if isinstance(source, dict):
        result["metadata_source_kind"] = source.get("kind", "")
    
    # Extract author
    author = metadata.get("author")
    if isinstance(author, dict):
        result["metadata_author"] = author.get("name", "")
    
    # Extract support tier
    support = metadata.get("support")
    if isinstance(support, dict):
        result["metadata_support_tier"] = support.get("tier", "")
    
    # Extract categories
    categories = metadata.get("categories")
    if isinstance(categories, dict):
        domains = categories.get("domains", [])
        if isinstance(domains, list):
            result["metadata_categories"] = ";".join(str(d) for d in domains)
    
    return result


def extract_content_item_from_yaml(
    yaml_path: Path,
    content_type: str,
    solution_name: str,
    solution_folder: str,
) -> Optional[Dict[str, Any]]:
    """Extract content item metadata and query from a YAML file.
    Uses caching to avoid re-processing unchanged files."""
    
    # Check cache first
    cached = get_cached_analysis(yaml_path, "standalone")
    if cached is not None:
        # Update solution info in cached result
        cached["solution_name"] = solution_name
        cached["solution_folder"] = solution_folder
        cached["solution_github_url"] = f"{GITHUB_REPO_URL}/Solutions/{quote(solution_folder)}" if solution_folder else ""
        return cached
    
    data = read_yaml_safe(yaml_path)
    if not data:
        return None
    
    # Extract common fields
    item_id = data.get("id", "")
    name = data.get("name", yaml_path.stem)
    description = data.get("description", "")
    if isinstance(description, str):
        description = description.replace("\n", " ").replace("\r", "").strip()
    
    # Get query
    query = data.get("query", "")
    if isinstance(query, str):
        query = query.strip()
    
    # Determine query status for analytic rules and hunting queries
    query_status = "has_query"
    if content_type in ("analytic_rule", "hunting_query"):
        if not query:
            # No query present - check if retired or deprecated
            desc_lower = description.lower() if description else ""
            name_lower = name.lower() if name else ""
            
            if "retired" in desc_lower or "retired" in name_lower:
                query_status = "retired"
            elif "deprecated" in desc_lower or "deprecated" in name_lower:
                query_status = "deprecated"
            elif "moved" in desc_lower or "replaced" in desc_lower:
                query_status = "moved_or_replaced"
            else:
                query_status = "missing_query"
    
    # Get required data connectors
    required_connectors: List[str] = []
    req_dc = data.get("requiredDataConnectors", [])
    if isinstance(req_dc, list):
        for dc in req_dc:
            if isinstance(dc, dict) and "connectorId" in dc:
                required_connectors.append(dc["connectorId"])
    
    # Get tactics and techniques (for analytics/hunting)
    tactics = data.get("tactics", [])
    if isinstance(tactics, list):
        tactics = ",".join(tactics)
    else:
        tactics = str(tactics) if tactics else ""
    
    techniques = data.get("relevantTechniques", [])
    if isinstance(techniques, list):
        techniques = ",".join(techniques)
    else:
        techniques = str(techniques) if techniques else ""
    
    # Get severity (for analytics)
    severity = data.get("severity", "")
    
    # Get status
    status = data.get("status", "")
    
    # Get kind (for analytics rules)
    kind = data.get("kind", "")
    
    # Extract vendor/product from query (legacy)
    vp = extract_vendor_product_from_query(query) if query else {'vendor': set(), 'product': set()}
    
    # Detect tables in the query for context (enables proper EventID/EventName attribution)
    tables_in_query: Set[str] = set()
    if query:
        # Pattern 1: Table at start of line followed by pipe or newline
        # e.g., "AWSCloudTrail\n| where ..."
        table_pattern1 = re.compile(r'^\s*(\w+)\s*[\|\n]', re.MULTILINE)
        for match in table_pattern1.finditer(query):
            table_name = match.group(1)
            if table_name.lower() not in ('let', 'union', 'print', 'range', 'datatable'):
                tables_in_query.add(table_name)
        
        # Pattern 2: Table after let assignment: let VarName = TableName
        # e.g., "let EventInfo = AWSCloudTrail"
        table_pattern2 = re.compile(r'let\s+\w+\s*=\s*(\w+)\s*[\|\n]', re.MULTILINE | re.IGNORECASE)
        for match in table_pattern2.finditer(query):
            table_name = match.group(1)
            if table_name.lower() not in ('let', 'union', 'print', 'range', 'datatable', 'dynamic', 'pack', 'bag_pack', 'materialize'):
                tables_in_query.add(table_name)
    
    # Extract comprehensive filter fields (new)
    ff = extract_filter_fields_from_query(query, tables_in_query) if query else {}
    filter_fields_str = format_filter_fields(ff)
    
    result = {
        "content_id": item_id,
        "content_name": name,
        "content_type": content_type,
        "content_description": description[:500] if description else "",  # Truncate long descriptions
        "content_file": yaml_path.name,
        "content_readme_file": "",  # YAML content items don't typically have README files
        "content_severity": severity,
        "content_status": status,
        "content_kind": kind,
        "content_tactics": tactics,
        "content_techniques": techniques,
        "content_required_connectors": ",".join(required_connectors),
        "content_query": query,
        "content_query_status": query_status,
        "content_event_vendor": ";".join(sorted(vp['vendor'])) if vp['vendor'] else "",
        "content_event_product": ";".join(sorted(vp['product'])) if vp['product'] else "",
        "content_filter_fields": filter_fields_str,
        "solution_name": solution_name,
        "solution_folder": solution_folder,
        "solution_github_url": f"{GITHUB_REPO_URL}/Solutions/{quote(solution_folder)}" if solution_folder else "",
    }
    
    # Cache the result (without solution-specific fields that may change)
    cache_record = {k: v for k, v in result.items() if k not in ("solution_name", "solution_folder", "solution_github_url")}
    set_cached_analysis(yaml_path, "standalone", cache_record)
    
    return result


def extract_content_item_from_workbook(
    json_path: Path,
    solution_name: str,
    solution_folder: str,
) -> Optional[Dict[str, Any]]:
    """Extract content item metadata from a workbook JSON file.
    Uses caching to avoid re-processing unchanged files."""
    
    # Check cache first
    cached = get_cached_analysis(json_path, "standalone")
    if cached is not None:
        # Update solution info in cached result
        cached["solution_name"] = solution_name
        cached["solution_folder"] = solution_folder
        cached["solution_github_url"] = f"{GITHUB_REPO_URL}/Solutions/{quote(solution_folder)}" if solution_folder else ""
        return cached
    
    data = read_json(json_path)
    if not data:
        return None
    
    # Skip ARM template files (azuredeploy*.json)
    if json_path.name.lower().startswith("azuredeploy"):
        return None
    
    # Skip ARM deployment templates - they have $schema field and are NOT actual workbooks
    # Real workbooks have "version": "Notebook/1.0" at the root level
    if isinstance(data, dict):
        # Check for ARM template schema - these are deployment wrappers, not workbook content
        if "$schema" in data:
            schema_val = data.get("$schema", "")
            if isinstance(schema_val, str) and "deploymentTemplate" in schema_val:
                return None
        
        # Verify this is actually a workbook (has "version": "Notebook/..." or contains "items" array)
        version = data.get("version", "")
        has_items = "items" in data
        if not (version.startswith("Notebook/") or has_items):
            # Not a valid workbook structure
            return None
    
    # Use filename as workbook name (workbooks don't have reliable metadata)
    name = json_path.stem
    
    # Extract all queries from the workbook
    queries = extract_queries_from_workbook(data) if isinstance(data, dict) else []
    combined_query = "\n---\n".join(queries) if queries else ""
    
    # Extract vendor/product from combined queries (legacy)
    vp = {'vendor': set(), 'product': set()}
    for q in queries:
        qvp = extract_vendor_product_from_query(q)
        vp['vendor'].update(qvp['vendor'])
        vp['product'].update(qvp['product'])
    
    # Detect tables across all queries for context (enables proper EventID attribution)
    all_tables: Set[str] = set()
    if queries:
        table_pattern = re.compile(r'^\s*(\w+)\s*[\|\n]', re.MULTILINE)
        for q in queries:
            for match in table_pattern.finditer(q):
                table_name = match.group(1)
                if table_name.lower() not in ('let', 'union', 'print', 'range', 'datatable'):
                    all_tables.add(table_name)
    
    # Extract comprehensive filter fields (new)
    ff = get_filter_fields_by_table(queries, all_tables) if queries else {}
    filter_fields_str = format_filter_fields(ff)
    
    result = {
        "content_id": "",  # Workbooks typically don't have an ID in the JSON
        "content_name": name,
        "content_type": "workbook",
        "content_description": "",  # Description not used for workbooks
        "content_file": json_path.name,
        "content_readme_file": "",  # Workbooks don't typically have README files
        "content_severity": "",
        "content_status": "",
        "content_kind": "",
        "content_tactics": "",
        "content_techniques": "",
        "content_required_connectors": "",
        "content_query": combined_query,
        "content_query_status": "has_query" if combined_query else "no_query",
        "content_event_vendor": ";".join(sorted(vp['vendor'])) if vp['vendor'] else "",
        "content_event_product": ";".join(sorted(vp['product'])) if vp['product'] else "",
        "content_filter_fields": filter_fields_str,
        "solution_name": solution_name,
        "solution_folder": solution_folder,
        "solution_github_url": f"{GITHUB_REPO_URL}/Solutions/{quote(solution_folder)}" if solution_folder else "",
    }
    
    # Cache the result (without solution-specific fields that may change)
    cache_record = {k: v for k, v in result.items() if k not in ("solution_name", "solution_folder", "solution_github_url")}
    set_cached_analysis(json_path, "standalone", cache_record)
    
    return result


def extract_playbook_queries_and_tables(data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """
    Extract KQL queries and write-to tables from a playbook (Logic App) JSON structure.
    
    Returns:
        Tuple of (queries, write_tables):
        - queries: List of KQL query strings from /queryData steps
        - write_tables: List of table names from /api/logs steps (Log-Type header)
    """
    queries: List[str] = []
    write_tables: List[str] = []
    
    def traverse(obj: Any) -> None:
        if isinstance(obj, dict):
            # Check if this is an ApiConnection action
            if obj.get("type") == "ApiConnection":
                inputs = obj.get("inputs", {})
                if isinstance(inputs, dict):
                    path = inputs.get("path", "")
                    
                    # Query step: /queryData or /queryDataV2
                    if path in ("/queryData", "/queryDataV2"):
                        body = inputs.get("body", "")
                        if isinstance(body, str) and body.strip():
                            # Clean up the query - may have escaped newlines
                            query = body.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", "\t")
                            queries.append(query)
                    
                    # Write to table step: /api/logs
                    elif path == "/api/logs":
                        headers = inputs.get("headers", {})
                        if isinstance(headers, dict):
                            log_type = headers.get("Log-Type", "")
                            if isinstance(log_type, str) and log_type.strip():
                                # Log-Type is the table name (without _CL suffix typically added by LA)
                                table_name = log_type.strip()
                                if not table_name.endswith("_CL"):
                                    table_name = f"{table_name}_CL"
                                if table_name not in write_tables:
                                    write_tables.append(table_name)
            
            # Continue traversing
            for value in obj.values():
                traverse(value)
        elif isinstance(obj, list):
            for item in obj:
                traverse(item)
    
    traverse(data)
    return queries, write_tables


def extract_content_item_from_playbook(
    json_path: Path,
    solution_name: str,
    solution_folder: str,
) -> Optional[Dict[str, Any]]:
    """Extract content item metadata from a playbook (Logic App) JSON file."""
    data = read_json(json_path)
    if not data:
        return None
    
    # Playbooks are ARM templates or Logic App definitions
    if not isinstance(data, dict):
        return None
    
    # Check if this is a valid Logic App (playbook)
    # Valid playbooks must have a Microsoft.Logic/workflows resource (ARM template format)
    # or a definition with triggers/actions (Logic App definition format)
    is_logic_app = False
    
    if "resources" in data:
        resources = data.get("resources", [])
        if isinstance(resources, list):
            for resource in resources:
                if isinstance(resource, dict):
                    res_type = resource.get("type", "")
                    # Check if this is a Logic App workflow
                    if res_type == "Microsoft.Logic/workflows":
                        is_logic_app = True
                        break
    
    # Check for Logic App definition format (non-ARM)
    if not is_logic_app and "definition" in data:
        definition = data.get("definition", {})
        if isinstance(definition, dict) and ("triggers" in definition or "actions" in definition):
            is_logic_app = True
    
    # If this is not a Logic App, skip it
    if not is_logic_app:
        return None
    
    name = None
    description = ""
    
    # Priority 1: metadata.title (most reliable for display name)
    if "metadata" in data:
        meta = data["metadata"]
        if isinstance(meta, dict):
            if "title" in meta:
                name = meta.get("title")
            description = meta.get("description", "")
    
    # Priority 2: parameters.PlaybookName.defaultValue (only if no metadata title)
    if not name and "parameters" in data:
        params = data["parameters"]
        if isinstance(params, dict):
            if "PlaybookName" in params:
                param_def = params["PlaybookName"]
                if isinstance(param_def, dict):
                    name = param_def.get("defaultValue")
    
    # Priority 3: Use parent folder name if file is azuredeploy.json
    if not name:
        if json_path.stem.lower() == "azuredeploy":
            # Use the parent folder name as the playbook name
            name = json_path.parent.name
        else:
            name = json_path.stem
    
    # Clean up description - replace newlines with space for single-line display
    if description:
        description = " ".join(description.split())
    
    # Always look for README.md file in the playbook folder
    readme_file = ""
    playbook_folder = json_path.parent
    
    # Look for README files in the playbook folder
    for readme_name in ["readme.md", "README.md", "Readme.md", "readme.MD", "README.MD"]:
        candidate = playbook_folder / readme_name
        if candidate.exists():
            # Store the relative path to the README file (will be updated by caller)
            readme_file = readme_name
            
            # If no description from metadata, extract from README
            if not description:
                try:
                    with candidate.open("r", encoding="utf-8", errors="ignore") as f:
                        readme_content = f.read()
                    
                    # Extract description from README
                    # Skip the title (first # line) and get the first paragraph
                    lines = readme_content.split('\n')
                    content_lines = []
                    in_content = False
                    
                    for line in lines:
                        stripped = line.strip()
                        # Skip title lines (start with #)
                        if stripped.startswith('#'):
                            if in_content:
                                break  # Stop at next header
                            continue
                        # Skip empty lines at the beginning
                        if not stripped and not in_content:
                            continue
                        # Skip image links and badges
                        if stripped.startswith('![') or stripped.startswith('[!['):
                            continue
                        # Skip HTML comments
                        if stripped.startswith('<!--'):
                            continue
                        # Start collecting content
                        if stripped:
                            in_content = True
                            content_lines.append(stripped)
                        elif in_content:
                            # Empty line after content - stop at first paragraph
                            break
                    
                    if content_lines:
                        description = " ".join(content_lines)
                        # Clean up markdown formatting
                        description = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', description)  # Remove links
                        description = re.sub(r'\*\*([^*]+)\*\*', r'\1', description)  # Remove bold
                        description = re.sub(r'\*([^*]+)\*', r'\1', description)  # Remove italic
                        description = re.sub(r'`([^`]+)`', r'\1', description)  # Remove code
                        description = " ".join(description.split())  # Normalize whitespace
                except Exception:
                    pass  # Ignore errors reading README
            break
    
    # content_file will be overwritten by the caller with the full relative path
    content_file = json_path.name
    
    # Extract queries and write-to tables from the playbook
    queries, write_tables = extract_playbook_queries_and_tables(data)
    combined_query = "\n---\n".join(queries) if queries else ""
    write_tables_str = ",".join(write_tables) if write_tables else ""
    
    # Extract vendor/product from combined queries (legacy)
    vp = {'vendor': set(), 'product': set()}
    for q in queries:
        qvp = extract_vendor_product_from_query(q)
        vp['vendor'].update(qvp['vendor'])
        vp['product'].update(qvp['product'])
    
    # Extract comprehensive filter fields (new)
    ff = get_filter_fields_by_table(queries) if queries else {}
    filter_fields_str = format_filter_fields(ff)
    
    return {
        "content_id": "",
        "content_name": name,
        "content_type": "playbook",
        "content_description": description[:500] if description else "",
        "content_file": content_file,
        "content_readme_file": readme_file,  # New field for README file path
        "content_severity": "",
        "content_status": "",
        "content_kind": "",
        "content_tactics": "",
        "content_techniques": "",
        "content_required_connectors": "",
        "content_query": combined_query,
        "content_query_status": "has_query" if combined_query else "no_query",
        "content_event_vendor": ";".join(sorted(vp['vendor'])) if vp['vendor'] else "",
        "content_event_product": ";".join(sorted(vp['product'])) if vp['product'] else "",
        "content_filter_fields": filter_fields_str,
        "content_write_tables": write_tables_str,
        "solution_name": solution_name,
        "solution_folder": solution_folder,
        "solution_github_url": f"{GITHUB_REPO_URL}/Solutions/{quote(solution_folder)}" if solution_folder else "",
    }


def collect_content_items(
    solution_dir: Path,
    solution_name: str,
    solution_folder: str,
    solution_json: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Collect all content items from a solution directory.
    
    Uses file system scanning as the primary discovery method, then checks each
    discovered item against the Solution JSON to determine if it's documented.
    Also adds placeholder items for items listed in Solution JSON but not found
    by file scanning.
    
    Args:
        solution_dir: Path to the solution directory
        solution_name: Display name of the solution
        solution_folder: Folder name of the solution
        solution_json: Optional parsed Solution JSON data for checking documentation status
    
    Returns:
        List of content item dictionaries with 'not_in_solution_json' field indicating items found by scanning but not in Solution JSON
    """
    content_items: List[Dict[str, Any]] = []
    
    # Get the set of items listed in Solution JSON for comparison
    json_items = get_content_items_from_solution_json(solution_json)
    
    for content_type, folder_names in CONTENT_TYPE_FOLDERS.items():
        # Get the set of basenames for this content type from Solution JSON
        json_basenames = json_items.get(content_type, set())
        
        for folder_name in folder_names:
            content_dir = solution_dir / folder_name
            if not content_dir.exists():
                continue
            
            if content_type in ["analytic_rule", "hunting_query", "parser", "summary_rule"]:
                # YAML-based content
                for yaml_path in list(content_dir.rglob("*.yaml")) + list(content_dir.rglob("*.yml")):
                    item = extract_content_item_from_yaml(yaml_path, content_type, solution_name, solution_folder)
                    if item:
                        # Calculate relative path within the content folder
                        try:
                            rel_path = yaml_path.relative_to(content_dir)
                            item["content_file"] = str(rel_path).replace("\\", "/")
                        except ValueError:
                            pass
                        # Check if item is in Solution JSON
                        basename_lower = yaml_path.name.lower()
                        item["not_in_solution_json"] = "true" if basename_lower not in json_basenames else "false"
                        content_items.append(item)
                        
            elif content_type == "workbook":
                # JSON-based content (workbooks)
                for json_path in content_dir.rglob("*.json"):
                    # Skip ARM templates
                    if json_path.name.lower().startswith("azuredeploy"):
                        continue
                    item = extract_content_item_from_workbook(json_path, solution_name, solution_folder)
                    if item:
                        # Check if item is in Solution JSON
                        basename_lower = json_path.name.lower()
                        item["not_in_solution_json"] = "true" if basename_lower not in json_basenames else "false"
                        content_items.append(item)
                        
            elif content_type == "playbook":
                # JSON-based content (playbooks/Logic Apps)
                for json_path in content_dir.rglob("*.json"):
                    item = extract_content_item_from_playbook(json_path, solution_name, solution_folder)
                    if item:
                        # Calculate relative path from content folder (Playbooks folder)
                        try:
                            rel_path = json_path.relative_to(content_dir)
                            item["content_file"] = str(rel_path).replace("\\", "/")
                            # Update readme file path to include the folder
                            if item.get("content_readme_file"):
                                readme_rel_path = json_path.parent / item["content_readme_file"]
                                readme_rel = readme_rel_path.relative_to(content_dir)
                                item["content_readme_file"] = str(readme_rel).replace("\\", "/")
                        except ValueError:
                            pass
                        # Check if item is in Solution JSON
                        basename_lower = json_path.name.lower()
                        item["not_in_solution_json"] = "true" if basename_lower not in json_basenames else "false"
                        content_items.append(item)
                        
            elif content_type == "watchlist":
                # Watchlists are typically JSON
                for json_path in content_dir.rglob("*.json"):
                    data = read_json(json_path)
                    if data:
                        name = json_path.stem
                        if isinstance(data, dict):
                            name = data.get("name", name) or data.get("displayName", name)
                        # Check if item is in Solution JSON
                        basename_lower = json_path.name.lower()
                        not_in_json = "true" if basename_lower not in json_basenames else "false"
                        content_items.append({
                            "content_id": "",
                            "content_name": name,
                            "content_type": "watchlist",
                            "content_description": "",
                            "content_file": json_path.name,
                            "content_readme_file": "",  # Watchlists don't have README files
                            "content_severity": "",
                            "content_status": "",
                            "content_kind": "",
                            "content_tactics": "",
                            "content_techniques": "",
                            "content_required_connectors": "",
                            "content_query": "",
                            "content_query_status": "no_query",  # Watchlists don't have queries
                            "content_event_vendor": "",
                            "content_event_product": "",
                            "content_filter_fields": "",  # Watchlists don't have filter fields
                            "not_in_solution_json": not_in_json,
                            "solution_name": solution_name,
                            "solution_folder": solution_folder,
                        })
    
    return content_items


def collect_standalone_content_items(repo_root: Path) -> List[Dict[str, Any]]:
    """
    Collect standalone content items from top-level repository directories.
    
    These are content items that exist outside of Solutions:
    - Detections/ - Analytic rules
    - Hunting Queries/ - Hunting queries  
    - Workbooks/ - Workbook definitions
    - Playbooks/ - Playbook folders
    - Summary rules/ - Summary rules
    - Watchlists/ - Watchlist folders
    
    Items with a metadata section are marked as "Standalone" (Content Hub items).
    Items without metadata are marked as "GitHub Only".
    Stub files (pointing to items moved to solutions) are skipped.
    
    Args:
        repo_root: Path to repository root
        
    Returns:
        List of content item dictionaries with content_source field
    """
    content_items: List[Dict[str, Any]] = []
    
    for content_type, (dir_name, file_type) in STANDALONE_CONTENT_DIRS.items():
        content_dir = repo_root / dir_name
        if not content_dir.exists():
            continue
        
        dir_start_count = len(content_items)
        
        if file_type == "yaml":
            # Process YAML files (Detections, Hunting Queries, Summary Rules)
            yaml_files = list(content_dir.rglob("*.yaml")) + list(content_dir.rglob("*.yml"))
            total_files = len(yaml_files)
            log_print(f"  Processing {dir_name}/: {total_files} YAML files...")
            
            for i, yaml_path in enumerate(yaml_files, 1):
                if i % 500 == 0:
                    log_print(f"    {dir_name}/: {i}/{total_files} files processed, {len(content_items) - dir_start_count} items found...")
                
                # Skip README files and templates
                if yaml_path.name.lower().startswith("readme") or yaml_path.name.lower() == "query_template.md":
                    continue
                
                data = read_yaml_safe(yaml_path)
                if not data or not isinstance(data, dict):
                    continue
                
                # Skip stub files
                if is_stub_file(data):
                    continue
                
                # Extract the content item
                # Calculate relative path from content directory
                try:
                    rel_path = yaml_path.relative_to(content_dir)
                    content_folder = str(rel_path.parent).replace("\\", "/") if rel_path.parent != Path(".") else ""
                except ValueError:
                    content_folder = ""
                
                item = extract_content_item_from_yaml(
                    yaml_path, content_type, 
                    solution_name="",  # No solution
                    solution_folder=""
                )
                if not item:
                    continue
                
                # Extract metadata to determine if Standalone or GitHub Only
                metadata = extract_yaml_metadata(data)
                has_metadata = bool(metadata.get("metadata_source_kind") or metadata.get("metadata_author"))
                
                # Set content source
                item["content_source"] = "Standalone" if has_metadata else "GitHub Only"
                
                # Add metadata fields
                item["metadata_source_kind"] = metadata.get("metadata_source_kind", "")
                item["metadata_author"] = metadata.get("metadata_author", "")
                item["metadata_support_tier"] = metadata.get("metadata_support_tier", "")
                item["metadata_categories"] = metadata.get("metadata_categories", "")
                
                # Set standalone-specific fields
                item["content_file"] = str(yaml_path.relative_to(content_dir)).replace("\\", "/")
                item["content_github_url"] = f"{GITHUB_REPO_URL}/{dir_name}/{quote(str(yaml_path.relative_to(content_dir)).replace(chr(92), '/'))}"
                item["not_in_solution_json"] = ""  # Not applicable for standalone
                # Only set solution_name for Standalone items with metadata
                item["solution_name"] = "Standalone Content" if has_metadata else ""
                item["solution_folder"] = dir_name if has_metadata else ""
                
                content_items.append(item)
                
        elif file_type == "json":
            # Process JSON files (Workbooks)
            json_files = list(content_dir.glob("*.json"))
            log_print(f"  Processing {dir_name}/: {len(json_files)} JSON files...")
            
            for json_path in json_files:
                # Skip README and metadata files
                if json_path.name.lower().startswith("readme") or json_path.name.lower() == "workbooksmetadata.json":
                    continue
                
                item = extract_content_item_from_workbook(
                    json_path,
                    solution_name="",
                    solution_folder=""
                )
                if not item:
                    continue
                
                # Workbooks don't have YAML metadata - check for metadata JSON
                # Mark as GitHub Only by default (no metadata section in JSON workbooks)
                item["content_source"] = "GitHub Only"
                item["metadata_source_kind"] = ""
                item["metadata_author"] = ""
                item["metadata_support_tier"] = ""
                item["metadata_categories"] = ""
                item["content_github_url"] = f"{GITHUB_REPO_URL}/{dir_name}/{quote(json_path.name)}"
                item["not_in_solution_json"] = ""
                # GitHub Only items don't belong to a specific solution
                item["solution_name"] = ""
                item["solution_folder"] = ""
                
                content_items.append(item)
                
        elif file_type == "folder":
            # Process folder-based content (Playbooks, Watchlists)
            folders = [f for f in content_dir.iterdir() if f.is_dir() and not f.name.startswith(".") and f.name.lower() != "templates"]
            log_print(f"  Processing {dir_name}/: {len(folders)} folders...")
            
            for i, item_folder in enumerate(folders, 1):
                if i % 100 == 0:
                    log_print(f"    {dir_name}/: {i}/{len(folders)} folders processed, {len(content_items) - dir_start_count} items found...")
                
                if content_type == "playbook":
                    # Look for azuredeploy.json or other Logic App JSON files
                    json_files = list(item_folder.rglob("*.json"))
                    for json_path in json_files:
                        item = extract_content_item_from_playbook(
                            json_path,
                            solution_name="",
                            solution_folder=""
                        )
                        if not item:
                            continue
                        
                        # Playbooks have metadata in their ARM template
                        # Check for metadata section
                        data = read_json(json_path)
                        has_metadata = False
                        if isinstance(data, dict) and "metadata" in data:
                            meta = data["metadata"]
                            if isinstance(meta, dict) and (meta.get("title") or meta.get("author")):
                                has_metadata = True
                                item["metadata_author"] = meta.get("author", {}).get("name", "") if isinstance(meta.get("author"), dict) else ""
                                item["metadata_support_tier"] = meta.get("support", {}).get("tier", "") if isinstance(meta.get("support"), dict) else ""
                        
                        item["content_source"] = "Standalone" if has_metadata else "GitHub Only"
                        item["metadata_source_kind"] = ""
                        item["metadata_categories"] = ""
                        
                        try:
                            rel_path = json_path.relative_to(content_dir)
                            item["content_file"] = str(rel_path).replace("\\", "/")
                            item["content_github_url"] = f"{GITHUB_REPO_URL}/{dir_name}/{quote(str(rel_path).replace(chr(92), '/'))}"
                        except ValueError:
                            item["content_github_url"] = ""
                        
                        item["not_in_solution_json"] = ""
                        # Only set solution_name for Standalone items with metadata
                        item["solution_name"] = "Standalone Content" if has_metadata else ""
                        item["solution_folder"] = dir_name if has_metadata else ""
                        
                        content_items.append(item)
                        
                elif content_type == "watchlist":
                    # Look for JSON files in watchlist folders
                    json_files = list(item_folder.glob("*.json"))
                    for json_path in json_files:
                        data = read_json(json_path)
                        if not data:
                            continue
                        
                        name = item_folder.name
                        if isinstance(data, dict):
                            name = data.get("name", name) or data.get("displayName", name)
                        
                        try:
                            rel_path = json_path.relative_to(content_dir)
                            content_file = str(rel_path).replace("\\", "/")
                            github_url = f"{GITHUB_REPO_URL}/{dir_name}/{quote(str(rel_path).replace(chr(92), '/'))}"
                        except ValueError:
                            content_file = json_path.name
                            github_url = ""
                        
                        content_items.append({
                            "content_id": "",
                            "content_name": name,
                            "content_type": "watchlist",
                            "content_description": "",
                            "content_file": content_file,
                            "content_readme_file": "",
                            "content_severity": "",
                            "content_status": "",
                            "content_kind": "",
                            "content_tactics": "",
                            "content_techniques": "",
                            "content_required_connectors": "",
                            "content_query": "",
                            "content_query_status": "no_query",
                            "content_event_vendor": "",
                            "content_event_product": "",
                            "content_filter_fields": "",
                            "content_source": "GitHub Only",
                            "content_github_url": github_url,
                            "metadata_source_kind": "",
                            "metadata_author": "",
                            "metadata_support_tier": "",
                            "metadata_categories": "",
                            "not_in_solution_json": "",
                            "solution_name": "",
                            "solution_folder": "",
                        })
        
        # Log summary for this directory
        dir_items_found = len(content_items) - dir_start_count
        if dir_items_found > 0:
            log_print(f"    {dir_name}/: completed, {dir_items_found} items found")
    
    return content_items


def extract_tables_from_content_query(
    query: str,
    parser_names: Set[str],
    parser_table_map: Dict[str, Set[str]],
    return_rejected: bool = False,
    return_parser_map: bool = False,
) -> Union[Set[str], Tuple[Set[str], Set[str]], Tuple[Set[str], Set[str], Dict[str, str]]]:
    """Extract table names from a content item's KQL query.
    
    ASIM parsers (starting with _Im_ or _ASim_) are kept as-is and NOT expanded
    to their underlying tables. This allows documentation to show which parsers
    a content item uses rather than the expanded table list.
    
    Non-ASIM parsers (e.g., solution-specific parsers) are still expanded to their
    underlying tables so documentation shows actual data sources.
    
    Args:
        query: The KQL query to extract tables from
        parser_names: Set of known parser names
        parser_table_map: Mapping of parser names to their underlying tables
        return_rejected: If True, also return rejected table candidates
        return_parser_map: If True, also return mapping of table -> source parser name
        
    Returns:
        If return_rejected is False and return_parser_map is False: Set of valid table names
        If return_rejected is True and return_parser_map is False: Tuple of (valid tables, rejected candidates)
        If return_rejected is True and return_parser_map is True: Tuple of (valid tables, rejected candidates, table_to_parser_map)
    """
    if not query:
        if return_rejected and return_parser_map:
            return (set(), set(), {})
        elif return_rejected:
            return (set(), set())
        else:
            return set()
    
    # Build normalized parser names set for validation
    parser_names_normalized = {normalize_parser_name(p) for p in parser_names}
    parser_table_map_normalized = {normalize_parser_name(k): v for k, v in parser_table_map.items()}
    
    # Build reverse mapping from normalized to original parser name for lookup
    normalized_to_original = {normalize_parser_name(p): p for p in parser_names}
    
    # Use existing query parsing infrastructure, passing known parser names
    # so they're recognized as valid candidates for extraction
    cache: Dict[str, Optional[str]] = {}
    tables = extract_query_table_tokens(
        query, {}, cache,
        allow_parser_tokens=True,
        known_parser_names=parser_names_normalized,
    )
    
    # Process tables - keep ASIM parsers as-is, expand other parsers
    result_tables: Set[str] = set()
    # Track which tables came from which parser (resolved_table -> source_parser)
    table_to_parser: Dict[str, str] = {}
    
    # Helper to check if a name is an ASIM parser/view
    # Matches: _Im_*, _ASim_*, im*, Im*, asim*, ASim* (with or without underscore prefix)
    def is_asim_parser(name: str) -> bool:
        lowered = name.lower() if name else ""
        return (lowered.startswith("_im_") or lowered.startswith("_asim_") or
                lowered.startswith("im") or lowered.startswith("asim"))
    
    for table in tables:
        lowered = table.lower() if table else ""
        # Check if this is an ASIM parser (with or without underscore prefix)
        if is_asim_parser(table):
            # Keep ASIM parser as-is, don't expand
            result_tables.add(table)
        else:
            table_normalized = normalize_parser_name(table)
            if table_normalized in parser_names_normalized or table_normalized in parser_table_map_normalized:
                # This is a non-ASIM parser, expand recursively to underlying tables
                derived_tables = expand_parser_tables(table, parser_table_map)
                if derived_tables:
                    result_tables.update(derived_tables)
                    # Track that these tables came from this parser
                    # Use original parser name (not normalized) for display
                    original_parser = normalized_to_original.get(table_normalized, table)
                    for derived_table in derived_tables:
                        # Only track if not already tracked (first parser wins)
                        if derived_table not in table_to_parser:
                            table_to_parser[derived_table] = original_parser
                else:
                    # Keep the parser name if we can't expand it
                    result_tables.add(table)
            else:
                result_tables.add(table)
    
    # Filter tables through is_valid_table_candidate to remove helper functions
    valid_tables = {t for t in result_tables if is_valid_table_candidate(t)}
    # Also filter table_to_parser to only include valid tables
    valid_table_to_parser = {t: p for t, p in table_to_parser.items() if t in valid_tables}
    
    if return_rejected and return_parser_map:
        # Filter out ASIM Empty parsers from rejected tables - these are expected infrastructure
        # patterns used as schema placeholders, not actual unknown tables
        rejected_tables = {
            t for t in (result_tables - valid_tables)
            if not (t.lower().endswith("_empty") and 
                    (t.lower().startswith("_im_") or t.lower().startswith("_asim_")))
        }
        return valid_tables, rejected_tables, valid_table_to_parser
    elif return_rejected:
        # Filter out ASIM Empty parsers from rejected tables - these are expected infrastructure
        # patterns used as schema placeholders, not actual unknown tables
        rejected_tables = {
            t for t in (result_tables - valid_tables)
            if not (t.lower().endswith("_empty") and 
                    (t.lower().startswith("_im_") or t.lower().startswith("_asim_")))
        }
        return valid_tables, rejected_tables
    return valid_tables


def parse_args(default_repo_root: Path) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract connector metadata and table usage per solution")
    parser.add_argument(
        "--solutions-dir",
        type=Path,
        default=default_repo_root / "Solutions",
        help="Path to the Solutions directory (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "solutions_connectors_tables_mapping.csv",
        help="Path for the generated CSV file (default: %(default)s)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "solutions_connectors_tables_issues_and_exceptions_report.csv",
        help="Path for the no-table issues report file (default: %(default)s)",
    )
    parser.add_argument(
        "--connectors-csv",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "connectors.csv",
        help="Path for the connectors CSV file with collection methods (default: %(default)s)",
    )
    parser.add_argument(
        "--solutions-csv",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "solutions.csv",
        help="Path for the solutions CSV file (default: %(default)s)",
    )
    parser.add_argument(
        "--tables-csv",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "tables.csv",
        help="Path for the tables CSV file (default: %(default)s)",
    )
    parser.add_argument(
        "--tables-reference-csv",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "tables_reference.csv",
        help="Path to tables_reference.csv for table metadata (default: %(default)s)",
    )
    parser.add_argument(
        "--mapping-csv",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "solutions_connectors_tables_mapping_simplified.csv",
        help="Path for the simplified mapping CSV file (default: %(default)s)",
    )
    parser.add_argument(
        "--show-detection-methods",
        action="store_true",
        default=False,
        help="Include table_detection_methods column in output CSV (default: False)",
    )
    parser.add_argument(
        "--overrides-csv",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "solution_analyzer_overrides.csv",
        help="Path to overrides CSV file for field value overrides (default: %(default)s)",
    )
    parser.add_argument(
        "--content-items-csv",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "content_items.csv",
        help="Path for the content items CSV file (default: %(default)s)",
    )
    parser.add_argument(
        "--content-tables-mapping-csv",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "content_tables_mapping.csv",
        help="Path for the content items to tables mapping CSV file (default: %(default)s)",
    )
    parser.add_argument(
        "--asim-parsers-csv",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "asim_parsers.csv",
        help="Path for the ASIM parsers CSV file (default: %(default)s)",
    )
    parser.add_argument(
        "--parsers-csv",
        type=Path,
        default=default_repo_root / "Tools" / "Solutions Analyzer" / "parsers.csv",
        help="Path for the non-ASIM parsers CSV file (default: %(default)s)",
    )
    parser.add_argument(
        "--force-refresh",
        type=str,
        default="",
        help=(
            "Force re-analysis of specified types, ignoring cached results. "
            "Comma-separated list of: asim, parsers, solutions, standalone, marketplace, tables. "
            "Use 'all' to refresh everything, or 'all-offline' to refresh all except "
            "network-dependent types (marketplace, tables). Example: --force-refresh=asim,parsers"
        ),
    )
    return parser.parse_args()


def main() -> None:
    global KNOWN_TABLES_LOWER, KNOWN_TABLES_PROPER_CASE
    # Script is in Tools/Solutions Analyzer, repo root is 2 levels up
    repo_root = Path(__file__).resolve().parents[2]
    script_dir = Path(__file__).resolve().parent
    args = parse_args(repo_root)

    # Initialize logging - log file goes to .logs folder (separate from cache)
    logs_dir = script_dir / ".logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "map_solutions_connectors_tables.log"
    init_logging(log_path)

    # Initialize file analysis cache (separate .cache folder)
    cache_dir = script_dir / ".cache"
    init_cache(cache_dir, args.force_refresh)

    # Load known tables from tables_reference.csv for whitelist-based table validation
    KNOWN_TABLES_LOWER, KNOWN_TABLES_PROPER_CASE = load_known_tables(script_dir)
    if KNOWN_TABLES_LOWER:
        log_print(f"Loaded {len(KNOWN_TABLES_LOWER)} known table names from tables_reference.csv")

    solutions_dir = args.solutions_dir.resolve()
    if not solutions_dir.exists() or not solutions_dir.is_dir():
        raise SystemExit(f"Solutions directory not found: {solutions_dir}")

    output_path = args.output.resolve()
    output_parent = output_path.parent
    output_parent.mkdir(parents=True, exist_ok=True)

    report_path = args.report.resolve()
    report_parent = report_path.parent
    report_parent.mkdir(parents=True, exist_ok=True)

    # Load ASIM parsers with full metadata for CSV export and parser expansion
    log_print("Loading ASIM parsers from /Parsers/ASim*/Parsers...")
    asim_parser_records, asim_parser_names, asim_parser_table_map, asim_alias_map = load_asim_parsers_detailed(repo_root)
    log_print(f"  Loaded {len(asim_parser_records)} ASIM parser records, {len(asim_parser_names)} parser names, {len(asim_parser_table_map)} parser mappings")
    
    # Load all non-ASIM parsers with detailed metadata
    log_print("Loading non-ASIM parsers from /Parsers/*/ and Solutions/*/Parsers/...")
    all_parser_records, all_parser_names, all_parser_table_map = collect_all_parsers_detailed(repo_root, solutions_dir)
    log_print(f"  Loaded {len(all_parser_records)} parser records, {len(all_parser_names)} parser names, {len(all_parser_table_map)} parser mappings")
    
    # For backwards compatibility, also load legacy parsers the old way
    legacy_parsers_dir = repo_root / "Parsers"
    legacy_parser_names, legacy_parser_table_map = collect_legacy_parsers(legacy_parsers_dir)
    
    # Merge all parsers (ASIM takes precedence)
    global_parser_names = all_parser_names | asim_parser_names
    global_parser_table_map = {**all_parser_table_map, **asim_parser_table_map}
    
    # Note: ASIM parsers CSV writing moved to after connectors_data is built
    # to allow connector association to be computed first
    asim_parsers_csv_path = args.asim_parsers_csv.resolve()
    
    # Write non-ASIM parsers CSV
    parsers_csv_path = args.parsers_csv.resolve()
    write_parsers_csv(all_parser_records, parsers_csv_path)

    # Load tables_reference.csv early for use in collection method detection
    tables_reference: Dict[str, Dict[str, str]] = {}
    tables_reference_path = args.tables_reference_csv.resolve()
    if tables_reference_path.exists():
        with tables_reference_path.open("r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                table_name = row.get('table_name', '')
                if table_name:
                    tables_reference[table_name] = row

    # Load overrides from CSV file
    overrides: List[Override] = load_overrides(args.overrides_csv.resolve())
    if overrides:
        log_print(f"Loaded {len(overrides)} override(s) from {args.overrides_csv}")

    grouped_rows: Dict[Tuple[str, ...], Dict[str, bool]] = defaultdict(dict)
    row_key_metadata: Dict[Tuple[str, ...], Dict[str, str]] = {}
    combo_with_non_azure: Set[Tuple[str, str, str]] = set()
    missing_connector_json: List[str] = []
    missing_metadata_with_connectors: List[str] = []

    solution_rows_kept: Dict[str, int] = defaultdict(int)
    solution_parser_skipped: Dict[str, Set[str]] = defaultdict(set)
    issues: List[Dict[str, str]] = []
    
    # Content items tracking
    all_content_items: List[Dict[str, Any]] = []
    content_table_mappings: List[Dict[str, str]] = []
    
    # Track connector documentation status (filename -> not_in_solution_json)
    connector_not_in_solution_json: Dict[str, str] = {}
    
    # Track all solutions and identify those without any connectors
    all_solutions_info: Dict[str, Dict[str, str]] = {}
    solutions_without_connectors: Set[str] = set()

    # Get list of solution directories for progress tracking
    solution_dirs = sorted([p for p in solutions_dir.iterdir() if p.is_dir() and p.name.lower() not in EXCLUDED_SOLUTION_FOLDERS], key=lambda p: p.name.lower())
    total_solutions = len(solution_dirs)
    log_print(f"\nProcessing {total_solutions} solution directories...")
    
    for solution_idx, solution_dir in enumerate(solution_dirs, 1):
        # Progress checkpoint every 50 solutions
        if solution_idx % 50 == 0 or solution_idx == 1:
            log_print(f"  [{solution_idx}/{total_solutions}] Processing {solution_dir.name}...")
        solution_info = collect_solution_info(solution_dir.resolve())
        
        # Store all solution info for later processing
        all_solutions_info[solution_info["solution_name"]] = solution_info
        
        has_metadata = (solution_dir / "SolutionMetadata.json").exists()
        solution_parser_names, solution_parser_table_map = collect_parser_metadata(solution_dir.resolve())
        
        # Merge solution parsers with global parsers (ASIM + legacy)
        # ASIM parsers take precedence, then legacy parsers, then solution-specific parsers
        parser_names = solution_parser_names | global_parser_names
        parser_table_map = {**solution_parser_table_map, **global_parser_table_map}
        # Normalize parser names for lookups (handles underscore prefix variations)
        parser_names_lower = {normalize_parser_name(name) for name in parser_names if name}
        
        # Read Solution JSON for content item comparison
        solution_json = find_solution_json(solution_dir.resolve())
        
        # Collect content items for this solution
        solution_content_items = collect_content_items(
            solution_dir.resolve(),
            solution_info["solution_name"],
            solution_info["solution_folder"],
            solution_json=solution_json,
        )
        
        # Extract tables from content queries and build mappings
        # Consolidate read/write usage per table per content item
        for item in solution_content_items:
            # Track table usage for this content item: table_name -> set of usages
            item_table_usage: Dict[str, set] = defaultdict(set)
            
            # Extract read tables from queries, also get rejected candidates and parser mappings
            query = item.get("content_query", "")
            table_to_parser: Dict[str, str] = {}  # Track which parser each table came from
            if query:
                tables, rejected_tables, table_to_parser = extract_tables_from_content_query(
                    query, parser_names, parser_table_map, return_rejected=True, return_parser_map=True
                )
                for table in tables:
                    if is_valid_table_candidate(table):
                        item_table_usage[table].add("read")
                
                # Log rejected table candidates as issues
                if rejected_tables:
                    # Construct the file path with content type folder for GitHub URL
                    content_type = item.get("content_type", "")
                    content_file = item.get("content_file", "")
                    # Map content_type to its folder name
                    content_type_folder_map = {
                        "analytic_rule": "Analytic Rules",
                        "hunting_query": "Hunting Queries", 
                        "workbook": "Workbooks",
                        "playbook": "Playbooks",
                        "parser": "Parsers",
                        "watchlist": "Watchlists",
                        "summary_rule": "Summary Rules",
                    }
                    folder_name = content_type_folder_map.get(content_type, "")
                    if folder_name and content_file:
                        relevant_file_path = f"{folder_name}/{content_file}"
                    else:
                        relevant_file_path = content_file
                    
                    add_issue(
                        issues,
                        solution_name=item["solution_name"],
                        solution_folder=item.get("solution_folder", ""),
                        connector_id="",
                        connector_title="",
                        connector_publisher="",
                        relevant_file=relevant_file_path,
                        reason="content_unknown_table",
                        details=f"{item['content_type']} '{item['content_name']}' references unknown tables: {', '.join(sorted(rejected_tables))}",
                    )
            
            # Extract write tables (from playbooks)
            write_tables_str = item.get("content_write_tables", "")
            if write_tables_str:
                for table in write_tables_str.split(","):
                    table = table.strip()
                    if table and is_valid_table_candidate(table):
                        item_table_usage[table].add("write")
            
            # Now emit one row per table with consolidated usage
            for table, usages in item_table_usage.items():
                # Determine usage string: read, write, or read/write
                if "read" in usages and "write" in usages:
                    usage_str = "read/write"
                elif "write" in usages:
                    usage_str = "write"
                else:
                    usage_str = "read"
                
                # Get the source parser name if this table came from a parser
                source_parser = table_to_parser.get(table, "")
                
                # Normalize table name to proper case from reference
                normalized_table = normalize_table_case(table)
                
                content_table_mappings.append({
                    "solution_name": item["solution_name"],
                    "solution_folder": item.get("solution_folder", ""),
                    "solution_github_url": item.get("solution_github_url", ""),
                    "content_type": item["content_type"],
                    "content_id": item.get("content_id", ""),
                    "content_name": item["content_name"],
                    "content_file": item.get("content_file", ""),
                    "table_name": normalized_table,
                    "table_usage": usage_str,
                    "source_parser": source_parser,
                })
            
            # Remove query and write_tables from output to keep CSV manageable
            item_for_csv = {k: v for k, v in item.items() if k not in ("content_query", "content_write_tables")}
            
            # Mark solution-sourced content items
            item_for_csv["content_source"] = "Solution"
            item_for_csv["content_github_url"] = ""  # Will be empty for solution items (use solution_folder)
            item_for_csv["metadata_source_kind"] = ""
            item_for_csv["metadata_author"] = ""
            item_for_csv["metadata_support_tier"] = ""
            item_for_csv["metadata_categories"] = ""
            
            all_content_items.append(item_for_csv)
        
        # Get connector files listed in Solution JSON for comparison
        json_connector_basenames = get_content_items_from_solution_json(solution_json).get("data_connector", set())
        
        # Support "Data Connectors" (preferred), "DataConnectors", and "Data Connector" (singular) folder naming
        data_connectors_dirs = [
            solution_dir / "Data Connectors",
            solution_dir / "DataConnectors",
            solution_dir / "Data Connector",
        ]
        has_valid_connector = False
        has_data_connectors_dir = False

        for data_connectors_dir in data_connectors_dirs:
            if not data_connectors_dir.exists():
                continue
            has_data_connectors_dir = True
            for json_path in sorted(data_connectors_dir.rglob("*.json")):
                # Track connector documentation status
                basename_lower = json_path.name.lower()
                not_in_json = "true" if basename_lower not in json_connector_basenames else "false"
                # Build a unique key using solution folder and relative path
                connector_file_key = f"{solution_info['solution_folder']}:{json_path.name}"
                connector_not_in_solution_json[connector_file_key] = not_in_json
                
                data = read_json(json_path)
                if data is None:
                    # Log JSON parsing failure as an issue
                    relative_path = safe_relative(json_path, data_connectors_dir)
                    issues.append({
                        "solution_name": solution_info["name"],
                        "solution_folder": solution_info["folder"],
                        "connector_id": "",
                        "connector_title": "",
                        "connector_publisher": "",
                        "connector_file": str(relative_path),
                        "reason": "json_parse_error",
                        "details": f"Failed to parse JSON file: {json_path.name}",
                    })
                    continue
                connector_entries = find_connector_objects(data)
                if not connector_entries:
                    continue
                has_valid_connector = True
                
                # === Table extraction with priority ordering ===
                # Priority 1: *_Table.json companion files
                # Priority 2: *_DCR.json companion files  
                # Priority 3: Query analysis from connector JSON
                
                table_map: Dict[str, Dict[str, Any]] = {}
                tables_from_companion_files = False
                
                # Check for companion Table and DCR files
                table_json_files, dcr_json_files = find_companion_table_files(json_path)
                
                # Priority 1: Extract from *_Table.json files
                # Trust tables from companion files - they are explicitly defined
                for table_json_path in table_json_files:
                    table_tables = extract_tables_from_table_json(table_json_path)
                    for tbl_name, tbl_info in table_tables.items():
                        if tbl_name.lower() != "let" and tbl_name.strip():
                            if tbl_name not in table_map:
                                tbl_info["from_companion_file"] = True  # Mark as trusted
                                table_map[tbl_name] = tbl_info
                                tables_from_companion_files = True
                            else:
                                # Merge sources
                                existing_sources = table_map[tbl_name].get("sources", set())
                                if isinstance(existing_sources, set):
                                    existing_sources.update(tbl_info.get("sources", set()))
                
                # Priority 2: Extract from *_DCR.json files
                # Trust tables from companion files - they are explicitly defined
                for dcr_json_path in dcr_json_files:
                    dcr_tables = extract_tables_from_dcr_json(dcr_json_path)
                    for tbl_name, tbl_info in dcr_tables.items():
                        if tbl_name.lower() != "let" and tbl_name.strip():
                            if tbl_name not in table_map:
                                tbl_info["from_companion_file"] = True  # Mark as trusted
                                table_map[tbl_name] = tbl_info
                                tables_from_companion_files = True
                            else:
                                # Merge sources
                                existing_sources = table_map[tbl_name].get("sources", set())
                                if isinstance(existing_sources, set):
                                    existing_sources.update(tbl_info.get("sources", set()))
                
                # Priority 3: Query analysis from connector JSON
                query_tables = {k: v for k, v in extract_tables(data).items() if k.lower() != "let"}
                for tbl_name, tbl_info in query_tables.items():
                    # Accept both valid tables and known parser names (parsers will be expanded later)
                    tbl_name_normalized = normalize_parser_name(tbl_name)
                    if is_valid_table_candidate(tbl_name) or tbl_name_normalized in parser_names_lower:
                        if tbl_name not in table_map:
                            table_map[tbl_name] = tbl_info
                        else:
                            # Merge sources
                            existing_sources = table_map[tbl_name].get("sources", set())
                            if isinstance(existing_sources, set):
                                existing_sources.update(tbl_info.get("sources", set()))
                
                log_table_candidates = extract_log_analytics_tables(data)
                used_loganalytics_fallback = False
                had_raw_table_definitions = bool(table_map)
                if not table_map and log_table_candidates:
                    used_loganalytics_fallback = True
                    for table_name in log_table_candidates:
                        table_map[table_name] = {
                            "has_mismatch": False,
                            "actual_table": None,
                            "sources": {"logAnalyticsTableId"},
                        }
                if parser_names_lower:
                    for info in table_map.values():
                        actual_name = info.get("actual_table")
                        if actual_name and normalize_parser_name(actual_name) in parser_names_lower:
                            info["has_mismatch"] = False
                            info["actual_table"] = None
                table_entries = list(table_map.items())
                relative_path = safe_relative(json_path, data_connectors_dir)
                is_azuredeploy = json_path.name.lower().startswith("azuredeploy")
                for entry in connector_entries:
                    connector_id = entry.get("id", "")
                    connector_publisher = entry.get("publisher", "")
                    connector_title = entry.get("title", "")
                    connector_id_generated = entry.get("id_generated", False)
                    # Replace newlines with <br> for GitHub CSV rendering
                    connector_description = entry.get("description", "").replace("\n", "<br>").replace("\r", "")
                    connector_instruction_steps = entry.get("instructionSteps", "")
                    connector_permissions = entry.get("permissions", "")
                    had_table_definitions = had_raw_table_definitions
                    parser_filtered_tables: Set[str] = set()
                    parser_expansion_details: Dict[str, Set[str]] = {}
                    produced_rows = 0
                    total_table_entries = len(table_entries)

                    effective_table_entries: List[Tuple[str, Dict[str, Any]]] = []
                    for original_name, table_info in table_entries:
                        if not isinstance(original_name, str) or not original_name:
                            continue
                        lowered = normalize_parser_name(original_name)
                        if lowered and lowered in parser_names_lower:
                            original_sources = set(table_info.get("sources") or [])
                            derived_tables = expand_parser_tables(original_name, parser_table_map)
                            if derived_tables:
                                parser_expansion_details[original_name] = derived_tables
                                for derived_table in sorted(derived_tables):
                                    if not is_valid_table_candidate(derived_table):
                                        continue
                                    derived_sources = set(original_sources)
                                    derived_sources.add(f"parser:{original_name}")
                                    effective_table_entries.append((
                                        derived_table,
                                        {
                                            "has_mismatch": False,
                                            "actual_table": None,
                                            "sources": derived_sources,
                                        },
                                    ))
                                continue
                            solution_parser_skipped[solution_info["solution_name"]].add(original_name)
                            parser_filtered_tables.add(original_name)
                            continue
                        # Trust tables from companion files even if not in known tables list
                        if not table_info.get("from_companion_file") and not is_valid_table_candidate(original_name):
                            continue
                        effective_table_entries.append((original_name, table_info))

                    if (
                        effective_table_entries
                        and log_table_candidates
                        and not used_loganalytics_fallback
                    ):
                        extracted_lower = {
                            name.lower()
                            for name, _ in effective_table_entries
                            if isinstance(name, str)
                        }
                        extracted_names = sorted(
                            name for name, _ in effective_table_entries if isinstance(name, str)
                        )
                        for log_name in log_table_candidates:
                            if log_name.lower() not in extracted_lower:
                                add_issue(
                                    issues,
                                    solution_name=solution_info["solution_name"],
                                    solution_folder=solution_info["solution_folder"],
                                    connector_id=connector_id,
                                    connector_title=connector_title,
                                    connector_publisher=connector_publisher,
                                    relevant_file=relative_path,
                                    reason="loganalytics_mismatch",
                                    details=f"logAnalyticsTableId '{log_name}' differs from detected table tokens {extracted_names}",
                                )

                    for table_name, table_info in effective_table_entries:
                        # Trust tables from companion files even if not in known tables list
                        if table_name and not table_info.get("from_companion_file") and not is_valid_table_candidate(table_name):
                            continue
                        if table_name and normalize_parser_name(table_name) in parser_names_lower:
                            continue
                        if not table_name:
                            continue
                        plural_sources = table_info.get("plural_sources") or []
                        mismatch = table_info.get("has_mismatch", False)
                        actual_name = table_info.get("actual_table")
                        if plural_sources:
                            plural_list = ", ".join(sorted(plural_sources))
                            add_issue(
                                issues,
                                solution_name=solution_info["solution_name"],
                                solution_folder=solution_info["solution_folder"],
                                connector_id=connector_id,
                                connector_title=connector_title,
                                connector_publisher=connector_publisher,
                                relevant_file=relative_path,
                                reason="plural_table_name",
                                details=f"Plural table name(s) {plural_list} replaced with '{table_name}'.",
                            )
                        # Normalize table name to proper case from reference
                        normalized_table_name = normalize_table_case(table_name)
                        row_key = (
                            solution_info["solution_name"],
                            solution_info["solution_folder"],
                            solution_info["solution_publisher_id"],
                            solution_info["solution_offer_id"],
                            solution_info["solution_first_publish_date"],
                            solution_info["solution_last_publish_date"],
                            solution_info["solution_version"],
                            solution_info["solution_support_name"],
                            solution_info["solution_support_tier"],
                            solution_info["solution_support_link"],
                            solution_info["solution_author_name"],
                            solution_info["solution_categories"],
                            connector_id,
                            connector_publisher,
                            connector_title,
                            connector_description,
                            connector_instruction_steps,
                            connector_permissions,
                            connector_id_generated,
                            normalized_table_name,
                        )
                        combo_key = (solution_info["solution_name"], connector_id, normalized_table_name)
                        if not is_azuredeploy:
                            combo_with_non_azure.add(combo_key)

                        existing_flag = grouped_rows[row_key].get(relative_path)
                        if existing_flag is None or (existing_flag and not is_azuredeploy):
                            grouped_rows[row_key][relative_path] = is_azuredeploy
                        metadata_entry = row_key_metadata.setdefault(row_key, {
                            "table_detection_methods": set(),
                        })
                        sources = table_info.get("sources")
                        if sources:
                            existing_sources: Set[str] = metadata_entry.setdefault("table_detection_methods", set())
                            if isinstance(sources, set):
                                existing_sources.update(sources)
                            else:
                                existing_sources.update(set(sources))
                        produced_rows += 1

                    if parser_expansion_details:
                        expansion_messages = []
                        for parser_name in sorted(parser_expansion_details.keys()):
                            resolved_tables = ", ".join(sorted(parser_expansion_details[parser_name]))
                            expansion_messages.append(f"{parser_name}: {resolved_tables}")
                        add_issue(
                            issues,
                            solution_name=solution_info["solution_name"],
                            solution_folder=solution_info["solution_folder"],
                            connector_id=connector_id,
                            connector_title=connector_title,
                            connector_publisher=connector_publisher,
                            relevant_file=relative_path,
                            reason="parser_tables_resolved",
                            details="Parser functions expanded to tables -> " + "; ".join(expansion_messages),
                        )

                    if produced_rows == 0:
                        if not had_table_definitions:
                            reason = "no_table_definitions"
                            details = "Connector definition did not expose any table tokens."
                            # Still include connector in output with empty table
                            row_key = (
                                solution_info["solution_name"],
                                solution_info["solution_folder"],
                                solution_info["solution_publisher_id"],
                                solution_info["solution_offer_id"],
                                solution_info["solution_first_publish_date"],
                                solution_info["solution_last_publish_date"],
                                solution_info["solution_version"],
                                solution_info["solution_support_name"],
                                solution_info["solution_support_tier"],
                                solution_info["solution_support_link"],
                                solution_info["solution_author_name"],
                                solution_info["solution_categories"],
                                connector_id,
                                connector_publisher,
                                connector_title,
                                connector_description,
                                connector_instruction_steps,
                                connector_permissions,
                                connector_id_generated,
                                "",  # Empty table name
                            )
                            existing_flag = grouped_rows[row_key].get(relative_path)
                            if existing_flag is None or (existing_flag and not is_azuredeploy):
                                grouped_rows[row_key][relative_path] = is_azuredeploy
                            produced_rows += 1
                        elif parser_filtered_tables and len(parser_filtered_tables) == total_table_entries:
                            reason = "parser_tables_only"
                            tables_list = ", ".join(sorted(parser_filtered_tables))
                            details = f"All table tokens correspond to parser functions: {tables_list}"
                        elif parser_filtered_tables:
                            reason = "partial_parser_tables"
                            tables_list = ", ".join(sorted(parser_filtered_tables))
                            details = f"Parser tables removed output rows: {tables_list}"
                        else:
                            reason = "table_detection_failed"
                            details = "Table tokens were detected but none could be emitted."
                        if used_loganalytics_fallback and reason == "no_table_definitions":
                            details = "No table tokens detected; emitted tables solely from logAnalyticsTableId values but still filtered."
                        # Log all issues including no_table_definitions to track items without detected tables
                        add_issue(
                            issues,
                            solution_name=solution_info["solution_name"],
                            solution_folder=solution_info["solution_folder"],
                            connector_id=connector_id,
                            connector_title=connector_title,
                            connector_publisher=connector_publisher,
                            relevant_file=relative_path,
                            reason=reason,
                            details=details,
                        )

        if has_data_connectors_dir and not has_valid_connector:
            missing_connector_json.append(solution_dir.name)
            add_issue(
                issues,
                solution_name=solution_info["solution_name"],
                solution_folder=solution_info["solution_folder"],
                reason="missing_connector_json",
                details="Data Connectors folder exists but contains no readable connector JSON files.",
            )
        if not has_metadata and has_valid_connector:
            missing_metadata_with_connectors.append(solution_dir.name)
            add_issue(
                issues,
                solution_name=solution_info["solution_name"],
                solution_folder=solution_info["solution_folder"],
                reason="missing_solution_metadata",
                details="Solution contains connectors but is missing SolutionMetadata.json.",
            )
        
        # Track solutions that truly have no connectors (no Data Connectors dir or no valid connectors)
        if not has_data_connectors_dir or not has_valid_connector:
            solutions_without_connectors.add(solution_info["solution_name"])

    # Add rows for solutions without any connectors
    for solution_name in sorted(solutions_without_connectors):
        solution_info = all_solutions_info[solution_name]
        # Create a row with solution info but empty connector and table fields
        row_key = (
            solution_info["solution_name"],
            solution_info["solution_folder"],
            solution_info["solution_publisher_id"],
            solution_info["solution_offer_id"],
            solution_info["solution_first_publish_date"],
            solution_info["solution_last_publish_date"],
            solution_info["solution_version"],
            solution_info["solution_support_name"],
            solution_info["solution_support_tier"],
            solution_info["solution_support_link"],
            solution_info["solution_author_name"],
            solution_info["solution_categories"],
            "",  # connector_id
            "",  # connector_publisher
            "",  # connector_title
            "",  # connector_description
            "",  # connector_instruction_steps
            "",  # connector_permissions
            False,  # connector_id_generated
            "",  # table_name
        )
        grouped_rows[row_key] = {}  # Empty file map for solutions without connectors

    rows: List[Dict[str, str]] = []
    
    # Track unique connectors for connectors.csv with collection method info
    connector_info_map: Dict[str, Dict[str, Any]] = {}
    # Track connector -> json_content for collection method detection
    connector_json_content: Dict[str, Tuple[str, str]] = {}  # connector_id -> (json_content, filename)
    
    for row_key in sorted(grouped_rows.keys()):
        path_map = grouped_rows[row_key]
        combo_key = (row_key[0], row_key[12], row_key[19])  # solution_name, connector_id, table_name
        non_azure_files = sorted([path for path, is_azure in path_map.items() if not is_azure])
        if non_azure_files:
            file_list = non_azure_files
        elif combo_key in combo_with_non_azure:
            continue
        else:
            file_list = sorted(path_map.keys())
        
        # Convert file paths to GitHub URLs
        github_urls = []
        for file_path in file_list:
            # Convert backslashes to forward slashes and prepend Solutions/
            normalized = file_path.replace("\\", "/")
            # URL encode all path components to handle spaces
            github_url = f"{GITHUB_REPO_URL}/Solutions/{quote(row_key[1])}/{quote('Data Connectors')}/{quote(normalized)}"
            github_urls.append(github_url)
        
        support_info = row_key_metadata.get(row_key, {"table_detection_methods": set()})
        
        # Build row data WITHOUT collection_method for main CSV (to match master branch format)
        row_data = {
            "Table": row_key[19],
            "solution_name": row_key[0],
            "solution_folder": row_key[1],
            "solution_github_url": f"{GITHUB_REPO_URL}/Solutions/{quote(row_key[1])}",
            "solution_publisher_id": row_key[2],
            "solution_offer_id": row_key[3],
            "solution_first_publish_date": row_key[4],
            "solution_last_publish_date": row_key[5],
            "solution_version": row_key[6],
            "solution_support_name": row_key[7],
            "solution_support_tier": row_key[8],
            "solution_support_link": row_key[9],
            "solution_author_name": row_key[10],
            "solution_categories": row_key[11],
            "connector_id": row_key[12],
            "connector_publisher": row_key[13],
            "connector_title": row_key[14],
            "connector_description": row_key[15],
            "connector_instruction_steps": row_key[16],
            "connector_permissions": row_key[17],
            "connector_id_generated": "true" if row_key[18] else "false",
            "connector_files": ";".join(github_urls),
            "is_unique": "true" if len(file_list) == 1 else "false",
        }
        
        # Only add detection methods if flag is set
        if args.show_detection_methods:
            row_data["table_detection_methods"] = ";".join(sorted(support_info.get("table_detection_methods", set()))) if support_info.get("table_detection_methods") else ""
        
        rows.append(row_data)
        solution_rows_kept[row_key[0]] += 1
        
        # Track connector info for connectors.csv
        connector_id = row_key[12]
        if connector_id and connector_id not in connector_info_map:
            # Check if any connector file is documented in Solution JSON
            # Extract filenames from the GitHub URLs and check against our tracking
            solution_folder = row_key[1]
            connector_files_list = github_urls
            is_documented = False
            for github_url in connector_files_list:
                # Extract filename from GitHub URL
                filename = github_url.split('/')[-1] if github_url else ""
                connector_file_key = f"{solution_folder}:{filename}"
                if connector_not_in_solution_json.get(connector_file_key) == "false":
                    is_documented = True
                    break
            not_in_json = "false" if is_documented else "true"
            
            connector_info_map[connector_id] = {
                'connector_id': connector_id,
                'connector_publisher': row_key[13],
                'connector_title': row_key[14],
                'connector_description': row_key[15],
                'connector_instruction_steps': row_key[16],
                'connector_permissions': row_key[17],
                'connector_id_generated': "true" if row_key[18] else "false",
                'connector_files': ";".join(github_urls),
                'solution_name': row_key[0],  # First solution name (can be multiple)
                'solution_folder': row_key[1],  # Solution folder for README lookup
                'not_in_solution_json': not_in_json,
            }

    # Build connector -> tables mapping BEFORE filter field extraction
    # This allows filter fields to use the connector's known tables as context
    connector_tables_map: Dict[str, List[str]] = defaultdict(list)
    for row in rows:
        connector_id = row.get('connector_id', '')
        table_name = row.get('Table', '')
        if connector_id and table_name:
            connector_tables_map[connector_id].append(table_name)

    # Now analyze collection methods for all connectors
    # We need to read JSON files again to get content for analysis
    # Also extract vendor/product information from connector queries
    connector_vendor_product: Dict[str, Dict[str, Set[str]]] = {}  # connector_id -> {'vendor': set, 'product': set}
    connector_vendor_product_by_table: Dict[str, Dict[str, Dict[str, Set[str]]]] = {}  # connector_id -> {table_name -> {'vendor': set, 'product': set}}
    connector_filter_fields: Dict[str, Dict[str, Dict[str, Set[str]]]] = {}  # connector_id -> {table_name -> {field_name -> set of values}}
    connector_ccf_config: Dict[str, Tuple[str, Path]] = {}  # connector_id -> (github_url, local_path)
    
    log_print(f"\nAnalyzing connector collection methods and filter fields...")
    for solution_dir in sorted([p for p in solutions_dir.iterdir() if p.is_dir() and p.name.lower() not in EXCLUDED_SOLUTION_FOLDERS], key=lambda p: p.name.lower()):
        for dc_folder_name in ["Data Connectors", "DataConnectors", "Data Connector"]:
            data_connectors_dir = solution_dir / dc_folder_name
            if not data_connectors_dir.exists():
                continue
            for json_path in sorted(data_connectors_dir.rglob("*.json")):
                # Skip non-connector files
                filename = json_path.name.lower()
                if filename in ['function.json', 'host.json', 'proxies.json', 'local.settings.json']:
                    continue
                try:
                    content = json_path.read_text(encoding='utf-8')
                    data = read_json(json_path)
                    if data is None:
                        continue
                    connector_entries = find_connector_objects(data)
                    for entry in connector_entries:
                        conn_id = entry.get('id', '')
                        if conn_id:
                            if conn_id not in connector_json_content:
                                connector_json_content[conn_id] = (content, json_path.name)
                            # Extract vendor/product from connector queries (aggregated) - legacy
                            vp = get_connector_vendor_product(data)
                            if vp['vendor'] or vp['product']:
                                if conn_id not in connector_vendor_product:
                                    connector_vendor_product[conn_id] = {'vendor': set(), 'product': set()}
                                connector_vendor_product[conn_id]['vendor'].update(vp['vendor'])
                                connector_vendor_product[conn_id]['product'].update(vp['product'])
                            # Extract vendor/product per table - legacy
                            vp_by_table = get_connector_vendor_product_by_table(data)
                            if vp_by_table:
                                if conn_id not in connector_vendor_product_by_table:
                                    connector_vendor_product_by_table[conn_id] = {}
                                for table_name, table_vp in vp_by_table.items():
                                    if table_name not in connector_vendor_product_by_table[conn_id]:
                                        connector_vendor_product_by_table[conn_id][table_name] = {'vendor': set(), 'product': set()}
                                    connector_vendor_product_by_table[conn_id][table_name]['vendor'].update(table_vp['vendor'])
                                    connector_vendor_product_by_table[conn_id][table_name]['product'].update(table_vp['product'])
                            # Extract comprehensive filter fields (new)
                            # Pass the connector's known tables for context (helps when queries use parser functions)
                            known_tables = set(connector_tables_map.get(conn_id, []))
                            ff = get_connector_filter_fields(data, known_tables)
                            if ff:
                                if conn_id not in connector_filter_fields:
                                    connector_filter_fields[conn_id] = {}
                                for table_name, fields in ff.items():
                                    if table_name not in connector_filter_fields[conn_id]:
                                        connector_filter_fields[conn_id][table_name] = {}
                                    for field_name, values in fields.items():
                                        if field_name not in connector_filter_fields[conn_id][table_name]:
                                            connector_filter_fields[conn_id][table_name][field_name] = set()
                                        connector_filter_fields[conn_id][table_name][field_name].update(values)
                            # Find CCF config file in the same directory
                            if conn_id not in connector_ccf_config:
                                ccf_config = find_ccf_config_file(json_path)
                                if ccf_config:
                                    # Build GitHub URL for the config file
                                    rel_path = ccf_config.relative_to(solutions_dir)
                                    parts = rel_path.parts
                                    github_url = f"{GITHUB_REPO_URL}/Solutions/" + "/".join(quote(p) for p in parts)
                                    connector_ccf_config[conn_id] = (github_url, ccf_config)
                except Exception:
                    continue
    
    # Build connectors with collection method info
    connectors_data: List[Dict[str, str]] = []
    
    for connector_id, info in sorted(connector_info_map.items()):
        json_content, filename = connector_json_content.get(connector_id, ("", ""))
        
        # Get table metadata for this connector's tables
        table_metadata_list = []
        for table_name in connector_tables_map.get(connector_id, []):
            if table_name in tables_reference:
                table_metadata_list.append(tables_reference[table_name])
        
        collection_method, detection_reason, all_matches = determine_collection_method(
            connector_id=info['connector_id'],
            connector_title=info['connector_title'],
            connector_description=info['connector_description'],
            json_content=json_content,
            filename=filename,
            table_metadata=table_metadata_list if table_metadata_list else None,
        )
        
        # Get vendor/product info for this connector (legacy)
        vp_info = connector_vendor_product.get(connector_id, {'vendor': set(), 'product': set()})
        
        # Get per-table vendor/product info - serialize as JSON (legacy)
        vp_by_table = connector_vendor_product_by_table.get(connector_id, {})
        # Convert sets to lists for JSON serialization
        vp_by_table_serialized = {}
        for table_name, table_vp in vp_by_table.items():
            vp_by_table_serialized[table_name] = {
                'vendor': sorted(table_vp['vendor']),
                'product': sorted(table_vp['product'])
            }
        
        # Get comprehensive filter fields (new unified format)
        ff = connector_filter_fields.get(connector_id, {})
        filter_fields_str = format_filter_fields(ff)
        
        # Find connector README file
        solution_folder = info.get('solution_folder', '')
        connector_readme_file = ''
        if solution_folder:
            solution_dir = solutions_dir / solution_folder
            readme_rel_path = find_connector_readme(solution_dir)
            if readme_rel_path:
                connector_readme_file = f"Solutions/{quote(solution_folder)}/{readme_rel_path}"
        
        # Determine if connector is deprecated based on title
        connector_title = info['connector_title']
        is_deprecated = '[DEPRECATED]' in connector_title.upper() or connector_title.startswith('[Deprecated]')
        
        # Get CCF config file and extract capabilities
        ccf_config_url = ''
        ccf_capabilities_str = ''
        if collection_method in ('CCF', 'CCF Push'):
            ccf_info = connector_ccf_config.get(connector_id)
            if ccf_info:
                ccf_config_url, ccf_config_path = ccf_info
                capabilities = extract_ccf_capabilities(ccf_config_path)
                ccf_capabilities_str = ';'.join(capabilities) if capabilities else ''
            elif 'pollingConfig' in json_content:
                # Legacy CCF: pollingConfig embedded in primary connector JSON, no separate config
                collection_method = 'CCF (Legacy)'
                detection_reason = 'CCF with embedded pollingConfig (no separate config file)'
                capabilities = extract_legacy_ccf_capabilities(json_content)
                ccf_capabilities_str = ';'.join(capabilities) if capabilities else ''
        
        connectors_data.append({
            'connector_id': info['connector_id'],
            'connector_publisher': info['connector_publisher'],
            'connector_title': info['connector_title'],
            'connector_description': info['connector_description'],
            'connector_instruction_steps': info['connector_instruction_steps'],
            'connector_permissions': info['connector_permissions'],
            'connector_id_generated': info['connector_id_generated'],
            'connector_files': info['connector_files'],
            'connector_readme_file': connector_readme_file,
            'collection_method': collection_method,
            'collection_method_reason': detection_reason,
            'event_vendor': ';'.join(sorted(vp_info['vendor'])) if vp_info['vendor'] else '',
            'event_product': ';'.join(sorted(vp_info['product'])) if vp_info['product'] else '',
            'event_vendor_product_by_table': json.dumps(vp_by_table_serialized) if vp_by_table_serialized else '',
            'filter_fields': filter_fields_str,
            'not_in_solution_json': info.get('not_in_solution_json', 'false'),
            'solution_name': info.get('solution_name', ''),
            'is_deprecated': 'true' if is_deprecated else 'false',
            'ccf_config_file': ccf_config_url,
            'ccf_capabilities': ccf_capabilities_str,
        })
    
    # Check marketplace availability (always runs, uses cache by default)
    # Use --force-refresh=marketplace to refresh the cache
    marketplace_status: Dict[str, Tuple[bool, str]] = {}
    cache_dir = script_dir / ".cache"
    marketplace_status = check_all_solutions_marketplace(
        all_solutions_info, 
        cache_dir, 
        force_refresh=("marketplace" in _force_refresh_types)
    )
    
    # Add is_published to content items based on their solution's marketplace status
    for item in all_content_items:
        solution_name = item.get('solution_name', '')
        is_pub, _ = marketplace_status.get(solution_name, (True, ""))
        item['is_published'] = 'true' if is_pub else 'false'
    
    # Add is_published to content table mappings
    for mapping in content_table_mappings:
        solution_name = mapping.get('solution_name', '')
        is_pub, _ = marketplace_status.get(solution_name, (True, ""))
        mapping['is_published'] = 'true' if is_pub else 'false'
    
    # Add is_published to connectors data
    for connector in connectors_data:
        solution_name = connector.get('solution_name', '')
        is_pub, _ = marketplace_status.get(solution_name, (True, ""))
        connector['is_published'] = 'true' if is_pub else 'false'
    
    # Add is_published to main mapping rows
    for row in rows:
        solution_name = row.get('solution_name', '')
        is_pub, _ = marketplace_status.get(solution_name, (True, ""))
        row['is_published'] = 'true' if is_pub else 'false'
    
    # Collect standalone content items from top-level directories
    log_print("\nCollecting standalone content items from top-level directories...")
    standalone_items = collect_standalone_content_items(repo_root)
    
    # Add is_published status to standalone items (standalone items are not in marketplace)
    for item in standalone_items:
        item['is_published'] = ''  # Not applicable for standalone items
    
    # Extract table mappings from standalone content items
    for item in standalone_items:
        query = item.get('content_query', '')
        write_tables_raw = item.get('content_write_tables', '')
        # content_write_tables is a comma-separated string, not a list
        write_tables = [t.strip() for t in write_tables_raw.split(',') if t.strip()] if write_tables_raw else []
        if query or write_tables:
            # Extract read tables from query using global parsers
            read_tables, _ = extract_tables_from_content_query(
                query, global_parser_names, global_parser_table_map, return_rejected=True
            )
            for table in read_tables:
                # Normalize table name to proper case from reference
                normalized_table = normalize_table_case(table)
                content_table_mappings.append({
                    "solution_name": item.get("solution_name", "Standalone Content"),
                    "solution_folder": item.get("solution_folder", ""),
                    "solution_github_url": item.get("solution_github_url", ""),
                    "content_type": item.get("content_type", ""),
                    "content_id": item.get("content_id", ""),
                    "content_name": item.get("content_name", ""),
                    "content_file": item.get("content_file", ""),
                    "table_name": normalized_table,
                    "table_usage": "read",
                    "is_published": "",  # Not applicable
                })
            # Add write tables
            for table in write_tables:
                usage = "read/write" if table in read_tables else "write"
                # Normalize table name to proper case from reference
                normalized_table = normalize_table_case(table)
                content_table_mappings.append({
                    "solution_name": item.get("solution_name", "Standalone Content"),
                    "solution_folder": item.get("solution_folder", ""),
                    "solution_github_url": item.get("solution_github_url", ""),
                    "content_type": item.get("content_type", ""),
                    "content_id": item.get("content_id", ""),
                    "content_name": item.get("content_name", ""),
                    "content_file": item.get("content_file", ""),
                    "table_name": normalized_table,
                    "table_usage": usage,
                    "is_published": "",
                })
        
        # Remove query and write_tables from output for CSV
        item.pop('content_query', None)
        item.pop('content_write_tables', None)
    
    # Merge standalone items with solution content items
    all_content_items.extend(standalone_items)
    log_print(f"  Added {len(standalone_items)} standalone content items")
    
    # Associate connectors to ASIM parsers and standalone/GitHub Only content items
    # This matches items to connectors based on shared tables and filter field subsets
    log_print("\nAssociating connectors to ASIM parsers and content items...")
    
    # Load connector association overrides from the main overrides file
    overrides_path = script_dir / "solution_analyzer_overrides.csv"
    connector_assoc_overrides = load_connector_association_overrides(overrides_path)
    if connector_assoc_overrides:
        log_print(f"  Loaded {len(connector_assoc_overrides)} connector association override(s)")
    
    # Associate connectors to ASIM parsers
    # ASIM parsers use 'tables' (semicolon-separated) and 'filter_fields' keys
    # Convert semicolon-separated tables to comma-separated for consistency
    for parser in asim_parser_records:
        tables_str = parser.get('tables', '')
        if tables_str:
            # Convert semicolon-separated to comma-separated
            parser['tables_for_matching'] = tables_str.replace(';', ',')
        else:
            parser['tables_for_matching'] = ''
    
    associate_connectors_to_items(
        asim_parser_records, 
        connectors_data,
        connector_tables_map=connector_tables_map,
        tables_key='tables_for_matching',
        filter_fields_key='filter_fields',
        item_type_name='ASIM parsers',
        name_key='parser_name',
        connector_assoc_overrides=connector_assoc_overrides
    )
    
    # Remove temporary key
    for parser in asim_parser_records:
        parser.pop('tables_for_matching', None)
    
    parsers_with_connectors = sum(1 for p in asim_parser_records if p.get('associated_connectors'))
    log_print(f"  Associated {parsers_with_connectors} ASIM parsers with connectors")
    
    # Generate report of ASIM parsers without connector associations
    unmatched_parsers_report_path = args.output.parent / "asim_parsers_unmatched_report.csv"
    unmatched_parsers = []
    for parser in asim_parser_records:
        if not parser.get('associated_connectors'):
            # Determine reason for no match
            tables_str = parser.get('tables', '')
            filter_fields_str = parser.get('filter_fields', '')
            parser_type = parser.get('parser_type', '')
            sub_parsers = parser.get('sub_parsers', '')
            
            # Determine the reason
            if parser_type == 'union':
                reason = "Union parser (uses sub-parsers, not direct tables)"
            elif parser_type == 'empty':
                reason = "Empty parser (placeholder only)"
            elif not tables_str:
                reason = "No tables detected"
            else:
                # Check if any connector uses the same tables
                parser_tables = {t.strip().lower() for t in tables_str.replace(';', ',').split(',') if t.strip()}
                matching_connectors_for_table = []
                for table in parser_tables:
                    for conn_id, conn_tables in connector_tables_map.items():
                        if table in [t.lower() for t in conn_tables]:
                            matching_connectors_for_table.append((table, conn_id))
                
                if not matching_connectors_for_table:
                    reason = f"No connectors provide tables: {tables_str}"
                else:
                    # There are connectors for the table, but filter mismatch
                    reason = f"Filter mismatch - parser uses: {filter_fields_str or 'no filters'}"
            
            unmatched_parsers.append({
                'parser_name': parser.get('parser_name', ''),
                'parser_type': parser_type,
                'tables': tables_str,
                'filter_fields': filter_fields_str,
                'sub_parsers': sub_parsers,
                'reason': reason,
            })
    
    if unmatched_parsers:
        with unmatched_parsers_report_path.open("w", encoding="utf-8", newline="") as f:
            fieldnames = ['parser_name', 'parser_type', 'tables', 'filter_fields', 'sub_parsers', 'reason']
            writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(unmatched_parsers)
        log_print(f"  Wrote {len(unmatched_parsers)} unmatched ASIM parsers to {unmatched_parsers_report_path.name}")
    
    # Write ASIM parsers CSV (now with association data)
    write_asim_parsers_csv(asim_parser_records, asim_parsers_csv_path)
    
    # Associate connectors to standalone/GitHub Only content items
    # Content items use content_table_mappings for tables and 'content_filter_fields' key
    # Build a lookup of content item -> tables from content_table_mappings
    content_item_tables: Dict[str, Set[str]] = {}
    for mapping in content_table_mappings:
        content_name = mapping.get('content_name', '')
        content_source = ''
        # Find source from all_content_items
        for item in all_content_items:
            if item.get('content_name') == content_name:
                content_source = item.get('content_source', '')
                break
        # Only process Standalone and GitHub Only items
        if content_source in ('Standalone', 'GitHub Only'):
            table = mapping.get('table_name', '')
            if content_name and table:
                if content_name not in content_item_tables:
                    content_item_tables[content_name] = set()
                content_item_tables[content_name].add(table)
    
    # Add tables to content items and associate connectors
    standalone_count = 0
    for item in all_content_items:
        source = item.get('content_source', '')
        if source in ('Standalone', 'GitHub Only'):
            # Get tables for this item
            content_name = item.get('content_name', '')
            tables = content_item_tables.get(content_name, set())
            # Temporarily add tables for matching
            item['_tables'] = ','.join(sorted(tables))
            standalone_count += 1
        else:
            item['_tables'] = ''
            # Solution content items don't need association (they have solution_name)
            item['associated_connectors'] = ''
            item['associated_solutions'] = ''
    
    # Associate connectors to standalone/GitHub Only items
    standalone_items_only = [i for i in all_content_items if i.get('content_source') in ('Standalone', 'GitHub Only')]
    associate_connectors_to_items(
        standalone_items_only,
        connectors_data,
        connector_tables_map=connector_tables_map,
        tables_key='_tables',
        filter_fields_key='content_filter_fields',
        item_type_name='standalone content items',
        name_key='content_name',
        connector_assoc_overrides=connector_assoc_overrides
    )
    
    # Clean up temporary keys
    for item in all_content_items:
        item.pop('_tables', None)
    
    items_with_connectors = sum(1 for i in standalone_items_only if i.get('associated_connectors'))
    log_print(f"  Associated {items_with_connectors} standalone/GitHub Only content items with connectors")
    
    # Build solutions data
    solutions_data: List[Dict[str, str]] = []
    for solution_name, info in sorted(all_solutions_info.items()):
        # Build full path to README if it exists
        readme_file = info.get('solution_readme_file', '')
        if readme_file:
            readme_full_path = f"Solutions/{quote(info['solution_folder'])}/{readme_file}"
        else:
            readme_full_path = ""
        
        # Get marketplace status if available
        is_published = True
        marketplace_url = ""
        if marketplace_status:
            is_published, marketplace_url = marketplace_status.get(solution_name, (True, ""))
        
        solutions_data.append({
            'solution_name': info['solution_name'],
            'solution_folder': info['solution_folder'],
            'solution_github_url': f"{GITHUB_REPO_URL}/Solutions/{quote(info['solution_folder'])}",
            'solution_publisher_id': info['solution_publisher_id'],
            'solution_offer_id': info['solution_offer_id'],
            'solution_first_publish_date': info['solution_first_publish_date'],
            'solution_last_publish_date': info['solution_last_publish_date'],
            'solution_version': info['solution_version'],
            'solution_support_name': info['solution_support_name'],
            'solution_support_tier': info['solution_support_tier'],
            'solution_support_link': info['solution_support_link'],
            'solution_author_name': info['solution_author_name'],
            'solution_categories': info['solution_categories'],
            'solution_readme_file': readme_full_path,
            'solution_logo_url': info.get('solution_logo_url', ''),
            'solution_description': info.get('solution_description', ''),
            'solution_dependencies': info.get('solution_dependencies', ''),
            'has_connectors': 'true' if solution_name not in solutions_without_connectors else 'false',
            'is_published': 'true' if is_published else 'false',
            'marketplace_url': marketplace_url,
        })
    
    # Build tables data from tables_reference.csv metadata (tables_reference was loaded early)
    # Collect all unique tables from connector data AND content items
    # Normalize table names to proper case from tables_reference.csv to avoid duplicates
    all_tables: Set[str] = set()
    for row in rows:
        table = row.get('Table', '')
        if table:
            all_tables.add(normalize_table_case(table))
    # Also add tables from content items (includes custom tables written by playbooks)
    for mapping in content_table_mappings:
        table = mapping.get('table_name', '')
        if table:
            all_tables.add(normalize_table_case(table))
    
    # Apply solution overrides to rows early, before building table_support_tiers
    # This ensures solution-level overrides (like support_tier fixes) affect derived table data
    if overrides:
        rows = apply_overrides_to_data(rows, overrides, 'solution', 'solution_name')
    
    # Build table -> support_tier mapping from solution data
    # For each table, collect all unique support tiers from associated solutions
    table_support_tiers: Dict[str, Set[str]] = {}
    for row in rows:
        table = row.get('Table', '')
        support_tier = row.get('solution_support_tier', '')
        if table and support_tier:
            if table not in table_support_tiers:
                table_support_tiers[table] = set()
            table_support_tiers[table].add(support_tier)
    
    # Build tables data with metadata from tables_reference.csv
    tables_data: List[Dict[str, str]] = []
    for table_name in sorted(all_tables):
        ref = tables_reference.get(table_name, {})
        
        # Determine support_tier based on associated solutions
        tiers = table_support_tiers.get(table_name, set())
        if len(tiers) == 0:
            support_tier = ''
        elif len(tiers) == 1:
            support_tier = next(iter(tiers))
        else:
            support_tier = 'Various'
        
        # Use collection_method from tables_reference.csv if available
        collection_method = ref.get('collection_method', '')
        
        tables_data.append({
            'table_name': table_name,
            'description': ref.get('description', ''),
            'category': ref.get('category', ''),
            'support_tier': support_tier,
            'collection_method': collection_method,
            'resource_types': ref.get('resource_types', ''),
            'source_azure_monitor': ref.get('source_azure_monitor', ''),
            'source_defender_xdr': ref.get('source_defender_xdr', ''),
            'azure_monitor_doc_link': ref.get('azure_monitor_doc_link', ''),
            'defender_xdr_doc_link': ref.get('defender_xdr_doc_link', ''),
            'basic_logs_eligible': ref.get('basic_logs_eligible', ''),
            'supports_transformations': ref.get('supports_transformations', ''),
            'ingestion_api_supported': ref.get('ingestion_api_supported', ''),
        })
    
    # Build simplified mapping (key fields only)
    mapping_data: List[Dict[str, str]] = []
    seen_mappings: Set[Tuple[str, str, str]] = set()
    for row in rows:
        key = (row['solution_name'], row.get('connector_id', ''), row.get('Table', ''))
        if key not in seen_mappings:
            seen_mappings.add(key)
            mapping_data.append({
                'solution_name': row['solution_name'],
                'connector_id': row.get('connector_id', ''),
                'table_name': row.get('Table', ''),
            })

    # Apply overrides to all data sets
    if overrides:
        # Apply table overrides (key field is 'Table' in rows, 'table_name' in tables_data)
        rows = apply_overrides_to_data(rows, overrides, 'table', 'Table')
        tables_data = apply_overrides_to_data(tables_data, overrides, 'table', 'table_name')
        mapping_data = apply_overrides_to_data(mapping_data, overrides, 'table', 'table_name')
        
        # Apply connector overrides
        connectors_data = apply_overrides_to_data(connectors_data, overrides, 'connector', 'connector_id')
        rows = apply_overrides_to_data(rows, overrides, 'connector', 'connector_id')
        
        # Apply solution overrides (rows already had solution overrides applied earlier for table_support_tiers)
        solutions_data = apply_overrides_to_data(solutions_data, overrides, 'solution', 'solution_name')
        # Also apply solution overrides to connectors, content items, and content table mappings
        # This ensures is_published overrides are consistently applied across all data sets
        connectors_data = apply_overrides_to_data(connectors_data, overrides, 'solution', 'solution_name')
        all_content_items = apply_overrides_to_data(all_content_items, overrides, 'solution', 'solution_name')
        content_table_mappings = apply_overrides_to_data(content_table_mappings, overrides, 'solution', 'solution_name')
        
        log_print(f"Applied overrides to data")

    # Identify internal use tables: custom tables (_CL) written by playbooks AND used by non-playbook content
    # These are solution-specific data storage tables (e.g., summarization tables for DNS/Network/Web Essentials)
    # Standard Sentinel tables (SecurityAlert, SecurityIncident, etc.) are NOT internal even if solutions write to them
    table_playbook_writers: Dict[str, Set[str]] = defaultdict(set)  # table -> solutions with playbooks that write
    table_nonplaybook_readers: Dict[str, Set[str]] = defaultdict(set)  # table -> solutions with non-playbook content that reads
    for mapping in content_table_mappings:
        table = mapping.get('table_name', '')
        solution = mapping.get('solution_name', '')
        content_type = mapping.get('content_type', '')
        usage = mapping.get('table_usage', 'read')
        if table and solution:
            # Track playbooks that write
            if content_type == 'playbook' and usage in ('write', 'read/write'):
                table_playbook_writers[table].add(solution)
            # Track non-playbook content that reads (analytics, hunting, workbooks)
            if content_type != 'playbook' and usage in ('read', 'read/write'):
                table_nonplaybook_readers[table].add(solution)
    
    internal_tables: Set[str] = set()
    for table in table_playbook_writers:
        # Only custom tables (_CL suffix) can be internal - these are created by solutions
        # Standard Sentinel tables (SecurityAlert, SecurityIncident, IdentityInfo, etc.) are not internal
        if not table.endswith('_CL'):
            continue
        writing_solutions = table_playbook_writers[table]
        reading_solutions = table_nonplaybook_readers.get(table, set())
        # If any solution both writes (via playbook) and reads (via non-playbook content), it's internal
        if writing_solutions & reading_solutions:
            internal_tables.add(table)
    
    # Update tables_data category to "Internal" for internal tables
    if internal_tables:
        for table_entry in tables_data:
            if table_entry['table_name'] in internal_tables:
                table_entry['category'] = 'Internal'
        log_print(f"Identified {len(internal_tables)} internal use tables (custom tables written by playbooks AND used by non-playbook content)")

    # Write main CSV (without collection_method to match master branch format)
    fieldnames = [
        "Table",
        "solution_name",
        "solution_folder",
        "solution_github_url",
        "solution_publisher_id",
        "solution_offer_id",
        "solution_first_publish_date",
        "solution_last_publish_date",
        "solution_version",
        "solution_support_name",
        "solution_support_tier",
        "solution_support_link",
        "solution_author_name",
        "solution_categories",
        "connector_id",
        "connector_publisher",
        "connector_title",
        "connector_description",
        "connector_instruction_steps",
        "connector_permissions",
        "connector_id_generated",
        "connector_files",
        "is_unique",
        "is_published",
    ]
    
    if args.show_detection_methods:
        fieldnames.append("table_detection_methods")

    with output_path.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)
    
    # Write connectors.csv
    connectors_fieldnames = [
        'connector_id',
        'connector_publisher',
        'connector_title',
        'connector_description',
        'connector_instruction_steps',
        'connector_permissions',
        'connector_id_generated',
        'connector_files',
        'connector_readme_file',
        'collection_method',
        'collection_method_reason',
        'event_vendor',
        'event_product',
        'event_vendor_product_by_table',
        'filter_fields',
        'not_in_solution_json',
        'solution_name',
        'is_deprecated',
        'is_published',
        'ccf_config_file',
        'ccf_capabilities',
    ]
    connectors_path = args.connectors_csv.resolve()
    with connectors_path.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=connectors_fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(connectors_data)
    
    # Write solutions.csv
    solutions_fieldnames = [
        'solution_name',
        'solution_folder',
        'solution_github_url',
        'solution_publisher_id',
        'solution_offer_id',
        'solution_first_publish_date',
        'solution_last_publish_date',
        'solution_version',
        'solution_support_name',
        'solution_support_tier',
        'solution_support_link',
        'solution_author_name',
        'solution_categories',
        'solution_readme_file',
        'solution_logo_url',
        'solution_description',
        'solution_dependencies',
        'has_connectors',
        'is_published',
        'marketplace_url',
    ]
    solutions_path = args.solutions_csv.resolve()
    with solutions_path.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=solutions_fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(solutions_data)
    
    # Write tables.csv
    tables_fieldnames = [
        'table_name',
        'description',
        'category',
        'support_tier',
        'collection_method',
        'resource_types',
        'source_azure_monitor',
        'source_defender_xdr',
        'azure_monitor_doc_link',
        'defender_xdr_doc_link',
        'basic_logs_eligible',
        'supports_transformations',
        'ingestion_api_supported',
    ]
    tables_path = args.tables_csv.resolve()
    with tables_path.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=tables_fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(tables_data)
    
    # Write simplified mapping CSV
    mapping_fieldnames = ['solution_name', 'connector_id', 'table_name']
    mapping_path = args.mapping_csv.resolve()
    with mapping_path.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=mapping_fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(mapping_data)
    
    # Write content items CSV
    content_items_fieldnames = [
        'content_id',
        'content_name',
        'content_type',
        'content_description',
        'content_file',
        'content_readme_file',
        'content_github_url',
        'content_severity',
        'content_status',
        'content_kind',
        'content_tactics',
        'content_techniques',
        'content_required_connectors',
        'content_query_status',
        'content_event_vendor',
        'content_event_product',
        'content_filter_fields',
        'associated_connectors',
        'associated_solutions',
        'content_source',
        'metadata_source_kind',
        'metadata_author',
        'metadata_support_tier',
        'metadata_categories',
        'not_in_solution_json',
        'solution_name',
        'solution_folder',
        'solution_github_url',
        'is_published',
    ]
    content_items_path = args.content_items_csv.resolve()
    with content_items_path.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=content_items_fieldnames, quoting=csv.QUOTE_ALL, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_content_items)
    
    # Write content-to-tables mapping CSV
    content_tables_fieldnames = ['solution_name', 'solution_folder', 'solution_github_url', 'content_type', 'content_id', 'content_name', 'content_file', 'table_name', 'table_usage', 'source_parser', 'is_published']
    content_tables_path = args.content_tables_mapping_csv.resolve()
    with content_tables_path.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=content_tables_fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(content_table_mappings)

    report_fieldnames = [
        "solution_name",
        "solution_folder",
        "solution_github_url",
        "connector_id",
        "connector_title",
        "connector_publisher",
        "relevant_file",
        "reason",
        "details",
    ]
    
    # Filter out parser_tables_resolved and add GitHub URLs to relevant_file
    filtered_issues = []
    for issue in issues:
        if issue.get("reason") == "parser_tables_resolved":
            continue
        # Add solution_github_url field (keep solution_folder as folder name)
        solution_folder_raw = issue.get("solution_folder", "")
        if solution_folder_raw:
            issue["solution_github_url"] = f"{GITHUB_REPO_URL}/Solutions/{quote(solution_folder_raw)}"
        # Convert relevant_file path to GitHub URL if present
        if issue.get("relevant_file"):
            normalized = issue["relevant_file"].replace("\\", "/")
            reason = issue.get("reason", "")
            if reason == "content_unknown_table":
                # Content files: use the full path from content_file which includes the folder type
                issue["relevant_file"] = f"{GITHUB_REPO_URL}/Solutions/{quote(solution_folder_raw)}/{quote(normalized)}"
            else:
                # Connector files: always in Data Connectors folder
                issue["relevant_file"] = f"{GITHUB_REPO_URL}/Solutions/{quote(solution_folder_raw)}/Data Connectors/{quote(normalized)}"
        filtered_issues.append(issue)
    
    with report_path.open("w", encoding="utf-8", newline="") as report_file:
        writer = csv.DictWriter(report_file, fieldnames=report_fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(filtered_issues)

    # Print summary
    if missing_connector_json:
        log_print("Solutions with Data Connectors folder but no connector JSON detected:")
        for name in missing_connector_json:
            log_print(f" - {name}")
    else:
        log_print("All Data Connectors folders contained connector definitions.")

    if missing_metadata_with_connectors:
        log_print("Solutions containing connectors but missing SolutionMetadata.json:")
        for name in missing_metadata_with_connectors:
            log_print(f" - {name}")
    else:
        log_print("All connector-producing solutions include SolutionMetadata.json.")

    solutions_missing_due_to_parsers = [
        name
        for name, skipped_tables in solution_parser_skipped.items()
        if skipped_tables and solution_rows_kept.get(name, 0) == 0
    ]
    if solutions_missing_due_to_parsers:
        log_print("Solutions skipped entirely because tables map to parser functions:")
        for name in sorted(solutions_missing_due_to_parsers):
            skipped_list = ", ".join(sorted(solution_parser_skipped[name]))
            log_print(f" - {name} (parser tables: {skipped_list})")

    # Print collection method distribution
    method_counts: Dict[str, int] = defaultdict(int)
    for conn in connectors_data:
        method_counts[conn['collection_method']] += 1
    
    log_print(f"\nCollection Method Distribution ({len(connectors_data)} connectors):")
    log_print("-" * 50)
    for method, count in sorted(method_counts.items(), key=lambda x: -x[1]):
        pct = (count / len(connectors_data) * 100) if connectors_data else 0
        log_print(f"  {method:30} {count:4} ({pct:.1f}%)")
    
    # Print content type distribution
    content_type_counts: Dict[str, int] = defaultdict(int)
    for item in all_content_items:
        content_type_counts[item['content_type']] += 1
    
    log_print(f"\nContent Type Distribution ({len(all_content_items)} items):")
    log_print("-" * 50)
    for ctype, count in sorted(content_type_counts.items(), key=lambda x: -x[1]):
        pct = (count / len(all_content_items) * 100) if all_content_items else 0
        log_print(f"  {ctype:30} {count:4} ({pct:.1f}%)")

    # Print content source distribution (Solution vs Standalone vs GitHub Only)
    content_source_counts: Dict[str, int] = defaultdict(int)
    for item in all_content_items:
        source = item.get('content_source', 'Unknown')
        content_source_counts[source] += 1
    
    log_print(f"\nContent Source Distribution ({len(all_content_items)} items):")
    log_print("-" * 50)
    for source, count in sorted(content_source_counts.items(), key=lambda x: -x[1]):
        pct = (count / len(all_content_items) * 100) if all_content_items else 0
        log_print(f"  {source:30} {count:4} ({pct:.1f}%)")

    # Generate filter fields findings report
    filter_fields_report_path = args.output.parent / "filter_fields_findings.md"
    
    # Collect filter field statistics
    connector_ff_count = sum(1 for c in connectors_data if c.get('filter_fields'))
    content_ff_count = sum(1 for c in all_content_items if c.get('content_filter_fields'))
    parser_ff_count = sum(1 for p in asim_parser_records if p.get('filter_fields'))
    
    # Aggregate filter field patterns across all sources
    all_filter_patterns: Dict[str, int] = defaultdict(int)  # pattern -> count
    
    def extract_table_field_pattern(part: str) -> Optional[str]:
        """Extract table.field from a filter part like 'Table.Field == "value"'."""
        part = part.strip()
        if not part:
            return None
        # Pattern format: Table.Field operator "value"
        # Find the first space after table.field to isolate the table.field part
        space_idx = part.find(' ')
        if space_idx > 0:
            return part[:space_idx].strip()
        return None
    
    for c in connectors_data:
        ff = c.get('filter_fields', '')
        if ff:
            for part in ff.split(' | '):
                pattern = extract_table_field_pattern(part)
                if pattern:
                    all_filter_patterns[pattern] += 1
    
    for item in all_content_items:
        ff = item.get('content_filter_fields', '')
        if ff:
            for part in ff.split(' | '):
                pattern = extract_table_field_pattern(part)
                if pattern:
                    all_filter_patterns[pattern] += 1
    
    for p in asim_parser_records:
        ff = p.get('filter_fields', '')
        if ff:
            for part in ff.split(' | '):
                pattern = extract_table_field_pattern(part)
                if pattern:
                    all_filter_patterns[pattern] += 1
    
    # Write the report
    with filter_fields_report_path.open("w", encoding="utf-8") as f:
        f.write("# Filter Fields Extraction Report\n\n")
        f.write("This report summarizes the filter field values extracted from queries across connectors, content items, and ASIM parsers.\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"| Source Type | Total Items | With Filter Fields | Percentage |\n")
        f.write(f"|-------------|-------------|-------------------|------------|\n")
        f.write(f"| Connectors | {len(connectors_data)} | {connector_ff_count} | {connector_ff_count/len(connectors_data)*100:.1f}% |\n" if connectors_data else "")
        f.write(f"| Content Items | {len(all_content_items)} | {content_ff_count} | {content_ff_count/len(all_content_items)*100:.1f}% |\n" if all_content_items else "")
        f.write(f"| ASIM Parsers | {len(asim_parser_records)} | {parser_ff_count} | {parser_ff_count/len(asim_parser_records)*100:.1f}% |\n" if asim_parser_records else "")
        
        f.write("\n## Filter Field Patterns Found\n\n")
        f.write("The following table.field combinations were detected in queries:\n\n")
        f.write("| Table.Field | Occurrences |\n")
        f.write("|-------------|-------------|\n")
        for pattern, count in sorted(all_filter_patterns.items(), key=lambda x: (-x[1], x[0])):
            f.write(f"| {pattern} | {count} |\n")
        
        f.write("\n## Filter Field Format\n\n")
        f.write("Filter fields are stored in the format:\n")
        f.write("```\n")
        f.write('table.field operator "value(s)" | table.field operator "value" | ...\n')
        f.write("```\n\n")
        f.write("Supported operators:\n")
        f.write("- Equality: `==`, `=~` (case-insensitive), `!=`\n")
        f.write("- Set membership: `in`, `in~` (case-insensitive), `!in`, `!in~`\n")
        f.write("- String matching: `has`, `has_cs`, `contains`, `contains_cs`, `startswith`, `startswith_cs`, `endswith`, `endswith_cs`\n")
        f.write("- Multi-value string: `has_any`, `has_all`\n")
        f.write("- Negative string: `!has`, `!contains`, `!startswith`, `!endswith`\n")
        f.write("- Regex: `matches regex`\n\n")
        f.write("Multiple values for in/has_any/has_all operators are comma-separated inside the quotes.\n\n")
        
        f.write("## Fields Extracted\n\n")
        f.write("The following fields are extracted from queries:\n\n")
        f.write("| Field | Typical Table | Purpose |\n")
        f.write("|-------|---------------|--------|\n")
        f.write("| DeviceVendor | CommonSecurityLog | CEF source vendor |\n")
        f.write("| DeviceProduct | CommonSecurityLog | CEF source product |\n")
        f.write("| EventVendor | ASIM tables | Normalized source vendor |\n")
        f.write("| EventProduct | ASIM tables | Normalized source product |\n")
        f.write("| ResourceType | AzureDiagnostics | Azure resource type |\n")
        f.write("| Category | AzureDiagnostics | Log category |\n")
        f.write("| EventID | WindowsEvent/SecurityEvent/Event | Windows event identifier |\n")
        f.write("| Source | Event | Event log source (e.g., Service Control Manager) |\n")
        f.write("| Provider | WindowsEvent | Windows event provider |\n")
        f.write("| Facility | Syslog | Syslog facility (e.g., auth, authpriv, cron) |\n")
        f.write("| ProcessName | Syslog | Process that generated the log |\n")
        f.write("| ProcessID | Syslog | Process ID |\n")
        f.write("| SyslogMessage | Syslog | Message content (uses string operators: has, contains, etc.) |\n")
        
        # Full listings with file links
        f.write("\n---\n\n")
        f.write("# Full Listings\n\n")
        
        # Connectors with filter fields
        f.write("## Connectors with Filter Fields\n\n")
        connector_with_ff = [c for c in connectors_data if c.get('filter_fields')]
        if connector_with_ff:
            f.write(f"Total: {len(connector_with_ff)} connectors\n\n")
            f.write("| Connector ID | Title | Filter Fields | File |\n")
            f.write("|--------------|-------|---------------|------|\n")
            for c in sorted(connector_with_ff, key=lambda x: x.get('connector_id', '')):
                conn_id = c.get('connector_id', '')
                title = c.get('connector_title', '').replace('|', '\\|')[:60]
                ff = c.get('filter_fields', '').replace('|', ' \\| ')
                # Get first file from the list
                files = c.get('connector_files', '')
                first_file = files.split(';')[0] if files else ''
                if first_file:
                    file_link = f"[Link]({first_file})"
                else:
                    file_link = ""
                f.write(f"| {conn_id} | {title} | {ff} | {file_link} |\n")
        else:
            f.write("No connectors with filter fields found.\n")
        
        # Content Items with filter fields - grouped by solution
        f.write("\n## Content Items with Filter Fields\n\n")
        content_with_ff = [c for c in all_content_items if c.get('content_filter_fields')]
        if content_with_ff:
            f.write(f"Total: {len(content_with_ff)} content items\n\n")
            
            # Group by solution
            by_solution: Dict[str, List[Dict]] = defaultdict(list)
            for c in content_with_ff:
                sol = c.get('solution_name', 'Unknown')
                by_solution[sol].append(c)
            
            for sol_name in sorted(by_solution.keys()):
                items = by_solution[sol_name]
                f.write(f"### {sol_name}\n\n")
                f.write("| Type | Name | Filter Fields | File |\n")
                f.write("|------|------|---------------|------|\n")
                for c in sorted(items, key=lambda x: (x.get('content_type', ''), x.get('content_name', ''))):
                    ctype = c.get('content_type', '')
                    name = c.get('content_name', '').replace('|', '\\|')[:50]
                    ff = c.get('content_filter_fields', '').replace('|', ' \\| ')
                    sol_folder = c.get('solution_folder', '')
                    content_file = c.get('content_file', '')
                    # Build GitHub link
                    if sol_folder and content_file:
                        # Determine content type folder
                        type_folders = {
                            'analytic_rule': 'Analytic Rules',
                            'hunting_query': 'Hunting Queries',
                            'workbook': 'Workbooks',
                            'playbook': 'Playbooks',
                            'parser': 'Parsers',
                        }
                        type_folder = type_folders.get(ctype, ctype.replace('_', ' ').title())
                        file_url = f"https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/{quote(sol_folder)}/{quote(type_folder)}/{quote(content_file)}"
                        file_link = f"[{content_file}]({file_url})"
                    else:
                        file_link = content_file
                    f.write(f"| {ctype} | {name} | {ff} | {file_link} |\n")
                f.write("\n")
        else:
            f.write("No content items with filter fields found.\n")
        
        # ASIM Parsers with filter fields
        f.write("\n## ASIM Parsers with Filter Fields\n\n")
        parser_with_ff = [p for p in asim_parser_records if p.get('filter_fields')]
        if parser_with_ff:
            f.write(f"Total: {len(parser_with_ff)} parsers\n\n")
            
            # Group by schema
            by_schema: Dict[str, List[Dict]] = defaultdict(list)
            for p in parser_with_ff:
                schema = p.get('schema', 'Unknown')
                by_schema[schema].append(p)
            
            for schema_name in sorted(by_schema.keys()):
                parsers = by_schema[schema_name]
                f.write(f"### {schema_name} Schema\n\n")
                f.write("| Parser Name | Product | Filter Fields | File |\n")
                f.write("|-------------|---------|---------------|------|\n")
                for p in sorted(parsers, key=lambda x: x.get('parser_name', '')):
                    pname = p.get('parser_name', '')
                    product = p.get('product_name', '').replace('|', '\\|')[:30]
                    ff = p.get('filter_fields', '').replace('|', ' \\| ')
                    github_url = p.get('github_url', '')
                    source_file = p.get('source_file', '')
                    if github_url:
                        file_link = f"[{source_file.split('/')[-1]}]({github_url})"
                    else:
                        file_link = source_file
                    f.write(f"| {pname} | {product} | {ff} | {file_link} |\n")
                f.write("\n")
        else:
            f.write("No ASIM parsers with filter fields found.\n")
    
    log_print(f"\nFilter fields report: {connector_ff_count} connectors, {content_ff_count} content items, {parser_ff_count} parsers")
    log_print(f"Wrote filter fields report to {safe_relative(filter_fields_report_path, repo_root)}")

    log_print(f"\nWrote {len(rows)} rows to {safe_relative(output_path, repo_root)}")
    log_print(f"Wrote {len(connectors_data)} connectors to {safe_relative(connectors_path, repo_root)}")
    log_print(f"Wrote {len(solutions_data)} solutions to {safe_relative(solutions_path, repo_root)}")
    log_print(f"Wrote {len(tables_data)} tables to {safe_relative(tables_path, repo_root)}")
    log_print(f"Wrote {len(mapping_data)} mappings to {safe_relative(mapping_path, repo_root)}")
    log_print(f"Wrote {len(all_content_items)} content items to {safe_relative(content_items_path, repo_root)}")
    log_print(f"Wrote {len(content_table_mappings)} content-table mappings to {safe_relative(content_tables_path, repo_root)}")
    log_print(f"Logged {len(issues)} connector issues to {safe_relative(report_path, repo_root)}")

    # Save the file analysis cache
    save_cache()

    # Close logging
    close_logging()


if __name__ == "__main__":
    main()
