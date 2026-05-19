#!/usr/bin/env python3
"""
ASIM Schema Comparison Tool

Compares ASIM CSV field definitions with documentation to identify discrepancies.
Supports both local files and web URLs for input sources.

Default CSV: https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/ASIM/dev/ASimTester/ASimTester.csv
Default Docs: https://learn.microsoft.com/en-us/azure/sentinel/normalization-about-schemas
"""

import argparse
import csv
import re
import os
import sys
import hashlib
import time
import json
from pathlib import Path
from io import StringIO
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict

# Try to import requests for web URL support
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# Default documentation base URLs
LEARN_BASE_URL = 'https://learn.microsoft.com/en-us/azure/sentinel'
GITHUB_DOCS_RAW_URL = 'https://raw.githubusercontent.com/MicrosoftDocs/azure-docs/main/articles/sentinel'

# Cache configuration
DEFAULT_CACHE_DIR = Path('.cache')
DEFAULT_CACHE_TTL = 3600  # 1 hour in seconds

# Global cache settings (set from command line)
_cache_enabled = True
_cache_dir = DEFAULT_CACHE_DIR
_cache_ttl = DEFAULT_CACHE_TTL

# Schema mapping from schema name to documentation file
SCHEMA_MAPPING = {
    'AlertEvent': 'normalization-schema-alert.md',
    'AuditEvent': 'normalization-schema-audit.md',
    'Authentication': 'normalization-schema-authentication.md',
    'Common': 'normalization-common-fields.md',
    'DhcpEvent': 'normalization-schema-dhcp.md',
    'Dns': 'normalization-schema-dns.md',
    'FileEvent': 'normalization-schema-file-event.md',
    'NetworkSession': 'normalization-schema-network.md',
    'ProcessEvent': 'normalization-schema-process-event.md',
    'RegistryEvent': 'normalization-schema-registry-event.md',
    'UserManagement': 'normalization-schema-user-management.md',
    'WebSession': 'normalization-schema-web.md',
}

# Fields to completely ignore in comparisons (not real fields)
FIELDS_TO_IGNORE = {'Class', 'response_has_ipv4', 'Unix'}

# Registry-specific values to ignore (from Root Keys and Value Types sections)
REGISTRY_NON_FIELDS = {
    'HKEY_LOCAL_MACHINE', 'HKEY_USERS',
    'Reg_None', 'Reg_Sz', 'Reg_Expand_Sz', 'Reg_Binary',
    'Reg_DWord', 'Reg_Multi_Sz', 'Reg_QWord'
}

# Physical types that match logical types
PHYSICAL_TYPES = {'int', 'integer', 'string', 'bool', 'boolean', 'real', 'datetime', 'long', 'dynamic', 'guid'}

# Patterns for specific user IDs documented centrally
SPECIFIC_ID_PATTERNS = [
    r'UserAadId$', r'UserSid$', r'UserAWSId$', r'UserOktaId$', r'Upn$', r'UserPuid$', r'UserUid$'
]

# Type aliases
TYPE_ALIASES = {
    'bool': ['boolean'],
    'boolean': ['bool'],
    'int': ['integer'],
    'integer': ['int'],
    'real': ['latitude', 'longitude'],
    'mac address': ['mac'],
    'mac': ['mac address'],
    'datetime': ['date/time'],
    'date/time': ['datetime'],
    'dnsquerytypename': ['enumerated'],
    'recommendeddnsdomain': ['enumerated'],
    'dnsqueryclassname': ['enumerated'],
    'networkprotocol': ['enumerated'],
}


@dataclass
class FieldInfo:
    """Information about a field from either CSV or documentation."""
    field_class: str = ""
    field_type: str = ""
    source: str = ""
    logical_type: str = ""
    list_of_values: str = ""
    aliased: str = ""
    description: str = ""
    example: str = ""
    note: str = ""
    original_description: str = ""  # Raw description before parsing


def parse_description_field(raw_desc: str) -> tuple:
    """Parse a raw description field and extract description, example, and note.
    
    Returns:
        tuple: (description, example, note)
    """
    if not raw_desc:
        return "", "", ""
    
    description = raw_desc.strip()
    example = ""
    note = ""
    
    # Extract note (typically at the end, after **Note**: or <br><br>**Note**:)
    note_match = re.search(r'(?:<br>\s*)*\*\*Note\*\*\s*:?\s*(.+?)\s*$', description, re.IGNORECASE | re.DOTALL)
    if note_match:
        note = note_match.group(1).strip()
        description = description[:note_match.start()].strip()
    
    # Extract example - multiple patterns (order matters - more specific first):
    # Look for examples that are typically at the end of the description
    example_patterns = [
        # Pattern: "Example: `value`" or "Examples: `value`" at end
        r'(?:<br>\s*)*(?:Example[s]?\s*[:|-]\s*)(.+?)\s*$',
        # Pattern: "e.g:" or "e.g.:" followed by value (with optional backticks)
        r'(?:<br>\s*)*(?:e\.g\.?\s*:\s*)(.+?)\s*$',
        # Pattern: "e.g." followed by one or more backticked values with <br> or spaces
        r'(?:<br>\s*)*e\.g\.(?:<br>)?\s*(.+?)\s*$',
        # Pattern: "For example:" or "for example," at end with backtick value
        r'(?:<br>\s*)*(?:[Ff]or example\s*[:,]?\s*)(`[^`]+`)\s*$',
        # Pattern: Preferred format: ... e.g: `value`
        r'(?:Preferred format\s*:\s*)?(?:<br>\s*)*e\.g\.?\s*:\s*(.+?)\s*$',
    ]
    
    for pattern in example_patterns:
        example_match = re.search(pattern, description, re.IGNORECASE)
        if example_match:
            example = example_match.group(1).strip()
            description = description[:example_match.start()].strip()
            break
    
    # If no example found in description, check if note contains an example at the end
    if not example and note:
        for pattern in example_patterns:
            example_match = re.search(pattern, note, re.IGNORECASE)
            if example_match:
                example = example_match.group(1).strip()
                note = note[:example_match.start()].strip()
                break
    
    # Clean up example - remove <br> tags, backticks, normalize
    if example:
        # Replace <br> with comma or space
        example = re.sub(r'<br\s*/?>\s*', ', ', example)
        # Remove HTML tags
        example = re.sub(r'<[^>]+>', '', example)
        # Remove surrounding backticks but keep internal ones as separators
        example = re.sub(r'^`|`$', '', example)
        # Replace backtick-separated values with commas
        example = re.sub(r'`\s*(?:or|,)?\s*`', ', ', example)
        example = re.sub(r'`', '', example)
        # Normalize whitespace
        example = re.sub(r'\s+', ' ', example).strip()
        # Clean up leading/trailing commas and punctuation
        example = example.strip(',').strip()
    
    # Clean up trailing <br> tags from description only
    description = re.sub(r'(?:<br>\s*)+$', '', description).strip()
    
    # Clean up note - only trailing <br> tags
    note = re.sub(r'(?:<br>\s*)+$', '', note).strip()
    
    return description, example, note


@dataclass
class IssueInfo:
    """Information about an issue found during comparison."""
    issue_type: str  # "Error", "Warning", or "Ignore"
    issue_category: str
    issue_description: str


@dataclass
class ComparisonResult:
    """Results from comparing a single schema."""
    schema: str
    doc_file: str
    csv_field_count: int = 0
    doc_field_count: int = 0
    doc_from_common_fields_count: int = 0
    doc_unique_field_count: int = 0
    matched_unique_field_count: int = 0
    matched_common_refs_count: int = 0
    warnings_from_missing_in_doc: int = 0
    missing_in_doc: List[Dict] = field(default_factory=list)
    missing_in_csv: List[str] = field(default_factory=list)
    type_mismatches: List[Dict] = field(default_factory=list)
    class_mismatches: List[Dict] = field(default_factory=list)
    warnings: List[Dict] = field(default_factory=list)


def get_cache_path(url: str) -> Path:
    """Get the cache file path for a URL."""
    # Create a hash of the URL for the filename
    url_hash = hashlib.md5(url.encode()).hexdigest()
    # Use the last part of the URL path as a readable prefix
    url_parts = url.rstrip('/').split('/')
    readable_name = url_parts[-1] if url_parts else 'unknown'
    # Sanitize the readable name
    readable_name = re.sub(r'[^\w\-.]', '_', readable_name)
    return _cache_dir / f"{readable_name}_{url_hash[:8]}.cache"


def get_cache_metadata_path(cache_path: Path) -> Path:
    """Get the metadata file path for a cache file."""
    return cache_path.with_suffix('.meta')


def is_cache_valid(cache_path: Path) -> bool:
    """Check if a cache file exists and is still valid (not expired)."""
    if not _cache_enabled:
        return False
    
    if not cache_path.exists():
        return False
    
    meta_path = get_cache_metadata_path(cache_path)
    if not meta_path.exists():
        return False
    
    try:
        with open(meta_path, 'r') as f:
            meta = json.load(f)
        cached_time = meta.get('timestamp', 0)
        if time.time() - cached_time > _cache_ttl:
            return False
        return True
    except (json.JSONDecodeError, KeyError):
        return False


def read_from_cache(cache_path: Path) -> Optional[str]:
    """Read content from cache if valid."""
    if not is_cache_valid(cache_path):
        return None
    
    try:
        with open(cache_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
            return f.read()
    except IOError:
        return None


def write_to_cache(cache_path: Path, content: str, url: str) -> None:
    """Write content to cache with metadata."""
    if not _cache_enabled:
        return
    
    try:
        _cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Write content
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Write metadata
        meta_path = get_cache_metadata_path(cache_path)
        with open(meta_path, 'w') as f:
            json.dump({
                'url': url,
                'timestamp': time.time(),
                'size': len(content)
            }, f)
    except IOError:
        pass  # Silently fail on cache write errors


def clear_cache() -> int:
    """Clear all cached files. Returns the number of files deleted."""
    if not _cache_dir.exists():
        return 0
    
    count = 0
    for cache_file in _cache_dir.glob('*.cache'):
        try:
            cache_file.unlink()
            count += 1
        except IOError:
            pass
    
    for meta_file in _cache_dir.glob('*.meta'):
        try:
            meta_file.unlink()
        except IOError:
            pass
    
    return count


def fetch_content(path: str, verbose: bool = False) -> str:
    """Fetch content from a local file or URL, with caching for URLs."""
    if path.startswith('http://') or path.startswith('https://'):
        if not HAS_REQUESTS:
            raise ImportError("The 'requests' library is required for web URLs. Install it with: pip install requests")
        
        # Check cache first
        cache_path = get_cache_path(path)
        cached_content = read_from_cache(cache_path)
        if cached_content is not None:
            if verbose:
                print(f"  [cache hit] {path.split('/')[-1]}")
            return cached_content
        
        # Fetch from web
        if verbose:
            print(f"  [fetching] {path.split('/')[-1]}")
        response = requests.get(path, timeout=30)
        response.raise_for_status()
        content = response.text
        
        # Remove BOM if present (UTF-8 BOM is \ufeff)
        if content.startswith('\ufeff'):
            content = content[1:]
        
        # Write to cache
        write_to_cache(cache_path, content, path)
        
        return content
    else:
        with open(path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
            return f.read()


def fetch_csv_data(csv_path: str) -> List[Dict[str, str]]:
    """Fetch and parse CSV data from a file or URL."""
    content = fetch_content(csv_path)
    reader = csv.DictReader(StringIO(content))
    return list(reader)


def get_doc_urls(doc_name: str, docs_base_url: str) -> Tuple[str, str]:
    """
    Get the documentation URLs for a schema doc file.
    
    Returns:
        Tuple of (display_url, fetch_url) where:
        - display_url is the user-facing URL (Learn page or local path)
        - fetch_url is the URL used to fetch the raw markdown content
    """
    # For GitHub raw URLs, use directly
    if 'raw.githubusercontent.com' in docs_base_url:
        url = f"{docs_base_url.rstrip('/')}/{doc_name}"
        return (url, url)
    
    # For local paths
    if not docs_base_url.startswith('http'):
        path = os.path.join(docs_base_url, doc_name)
        return (path, path)
    
    # For learn.microsoft.com, show Learn URL but fetch from GitHub raw
    doc_name_no_ext = doc_name.replace('.md', '')
    learn_url = f"{LEARN_BASE_URL}/{doc_name_no_ext}"
    fetch_url = f"{GITHUB_DOCS_RAW_URL}/{doc_name}"
    return (learn_url, fetch_url)


def get_schema_urls(docs_base_url: str, verbose: bool = True) -> Dict[str, Tuple[str, str]]:
    """
    Get documentation URLs for all schemas.
    
    Returns:
        Dict mapping schema name to (display_url, fetch_url) tuple
    """
    urls = {}
    for schema_name, doc_file in SCHEMA_MAPPING.items():
        display_url, fetch_url = get_doc_urls(doc_file, docs_base_url)
        urls[schema_name] = (display_url, fetch_url)
    
    if verbose:
        print("\nSchema documentation URLs:")
        print("-" * 80)
        for schema_name in sorted(urls.keys()):
            display_url, fetch_url = urls[schema_name]
            if display_url == fetch_url:
                print(f"  {schema_name}: {display_url}")
            else:
                print(f"  {schema_name}:")
                print(f"    Display: {display_url}")
                print(f"    Fetch:   {fetch_url}")
        print("-" * 80)
        print()
    
    return urls


def get_missing_field_issue_type(field_name: str) -> IssueInfo:
    """Determine issue type for missing fields."""
    for pattern in SPECIFIC_ID_PATTERNS:
        if re.search(pattern, field_name):
            return IssueInfo(
                issue_type="Warning",
                issue_category="SpecificIDsDocumentedCentrally",
                issue_description="Specific IDs documented centrally"
            )
    
    return IssueInfo(
        issue_type="Error",
        issue_category="MissingInDoc",
        issue_description="Field missing in documentation"
    )


def get_type_mismatch_issue_type(field_name: str, csv_type: str, doc_type: str, doc_class: str) -> IssueInfo:
    """Determine issue type for type mismatches."""
    csv_type_norm = csv_type.lower().strip()
    doc_type_norm = doc_type.lower().strip()
    
    # Check if this is Alias in doc but not in CSV (complex alias issue)
    if doc_class == "Alias" and not doc_type.strip():
        return IssueInfo(
            issue_type="Warning",
            issue_category="ComplexAliasNotSupported",
            issue_description="Complex aliases not supported in ASIM tester"
        )
    
    # Check if CSV has logical type and doc has physical type
    if doc_type_norm in PHYSICAL_TYPES and csv_type_norm not in PHYSICAL_TYPES:
        return IssueInfo(
            issue_type="Warning",
            issue_category="LogicalTypeNotInDocs",
            issue_description="Logical type should be added to docs"
        )
    
    # Check for datetime/Date/time equivalence
    if ((csv_type_norm == 'datetime' and doc_type_norm == 'date/time') or
        (csv_type_norm == 'date/time' and doc_type_norm == 'datetime')):
        return IssueInfo(
            issue_type="Ignore",
            issue_category="TypeEquivalent",
            issue_description="datetime and Date/time are equivalent"
        )
    
    # Check if doc says Enumerated but CSV has simple type
    if doc_type_norm == 'enumerated' and csv_type_norm in {'string', 'int', 'integer', 'long', 'real', 'bool', 'boolean'}:
        return IssueInfo(
            issue_type="Warning",
            issue_category="EnumerationNotSupported",
            issue_description="Enumeration type not supported in ASIM tester"
        )
    
    return IssueInfo(
        issue_type="Error",
        issue_category="TypeMismatch",
        issue_description="Type mismatch between CSV and documentation"
    )


def get_class_mismatch_issue_type(field_name: str, csv_class: str, doc_class: str) -> IssueInfo:
    """Determine issue type for class mismatches."""
    csv_class_norm = csv_class.lower().strip()
    doc_class_norm = doc_class.lower().strip()
    
    # Check if doc says Alias but CSV doesn't
    if doc_class_norm == "alias" and csv_class_norm != "alias":
        return IssueInfo(
            issue_type="Warning",
            issue_category="ComplexAliasNotSupported",
            issue_description="Complex aliases not supported in ASIM tester"
        )
    
    # Check if doc says Conditional but CSV says something else
    if doc_class_norm == "conditional" and csv_class_norm != "conditional":
        return IssueInfo(
            issue_type="Warning",
            issue_category="ConditionalNotSupported",
            issue_description="Conditional class not supported in ASIM tester"
        )
    
    return IssueInfo(
        issue_type="Error",
        issue_category="ClassMismatch",
        issue_description="Class mismatch between CSV and documentation"
    )


def parse_doc_fields(content: str, common_fields: Dict[str, FieldInfo], schema_name: str = "") -> Dict[str, FieldInfo]:
    """Parse field definitions from documentation content."""
    fields: Dict[str, FieldInfo] = {}
    
    # For Registry schema, remove the Root Keys and Value Types sections before parsing
    if schema_name == 'RegistryEvent':
        content = re.sub(r'(?ms)###\s*Root\s*[Kk]eys.*?(?=###\s*[A-Z]|##\s*Schema\s*updates|$)', '', content)
        content = re.sub(r'(?ms)###\s*Value\s*[Tt]ypes.*?(?=###\s*[A-Z]|##\s*Schema\s*updates|$)', '', content)
    
    lines = content.split('\n')
    in_standard_log_analytics_section = False
    
    for line in lines:
        # Detect section headers for Standard Log Analytics fields
        if re.match(r'^##\s*Standard Log Analytics fields', line):
            in_standard_log_analytics_section = True
            continue
        if re.match(r'^##\s', line) and in_standard_log_analytics_section:
            in_standard_log_analytics_section = False
        
        # Skip lines that don't look like table rows
        if not re.match(r'^\|.*\|', line):
            continue
        
        # Split by pipe and clean up
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 3:
            continue
        
        # Extract field name from first column (may have anchor tag)
        field_col = parts[1]
        match = re.search(r'\*\*([A-Za-z0-9_]+)\*\*', field_col)
        if match:
            field_name = match.group(1)
            
            if in_standard_log_analytics_section:
                field_type = parts[2].strip()
                field_class = "Mandatory"
                
                # Skip header rows
                if field_name == 'Field' or field_type == 'Type':
                    continue
                
                # Normalize type
                if field_type == 'Date/Time':
                    field_type = 'datetime'
                if field_type == 'String':
                    field_type = 'string'
            else:
                if len(parts) < 4:
                    continue
                
                field_class = parts[2].strip()
                field_type = parts[3].strip()
                
                # Skip header rows
                if field_name == 'Field' or field_class == 'Class':
                    continue
            
            # Skip parser parameters (all lowercase with underscores)
            if re.match(r'^[a-z_]+$', field_name):
                continue
            
            # Skip informational rows
            if field_class == '-' or field_type == '-':
                continue
            
            # Skip fields in ignore lists
            if field_name in FIELDS_TO_IGNORE or field_name in REGISTRY_NON_FIELDS:
                continue
            
            # Extract description from 4th column (5th part after splitting)
            description = ""
            example = ""
            note = ""
            original_description = ""
            if not in_standard_log_analytics_section and len(parts) >= 5:
                raw_desc = parts[4].strip()
                original_description = raw_desc
                description, example, note = parse_description_field(raw_desc)
            
            if field_name and field_class and field_name not in fields:
                fields[field_name] = FieldInfo(
                    field_class=field_class,
                    field_type=field_type,
                    source="SchemaDoc",
                    description=description,
                    example=example,
                    note=note,
                    original_description=original_description
                )
    
    # Pattern: Links to common fields
    pattern = r'-\s*\[([A-Za-z0-9_]+)\]\(normalization-common-fields\.md'
    for match in re.finditer(pattern, content):
        field_name = match.group(1).strip()
        if field_name and field_name not in fields:
            if field_name in common_fields:
                fields[field_name] = FieldInfo(
                    field_class=common_fields[field_name].field_class,
                    field_type=common_fields[field_name].field_type,
                    source="CommonFields",
                    description=common_fields[field_name].description,
                    example=common_fields[field_name].example,
                    note=common_fields[field_name].note,
                    original_description=common_fields[field_name].original_description
                )
            else:
                fields[field_name] = FieldInfo(
                    field_class="Common",
                    field_type="Common",
                    source="CommonFieldsRef"
                )
    
    # Always include TimeGenerated and Type from common fields
    for common_field_name in ['TimeGenerated', 'Type']:
        if common_field_name not in fields and common_field_name in common_fields:
            fields[common_field_name] = FieldInfo(
                field_class=common_fields[common_field_name].field_class,
                field_type=common_fields[common_field_name].field_type,
                source="CommonFieldsImplicit",
                description=common_fields[common_field_name].description,
                example=common_fields[common_field_name].example,
                note=common_fields[common_field_name].note,
                original_description=common_fields[common_field_name].original_description
            )
    
    return fields


def parse_common_fields(docs_path: str, is_web: bool = False) -> Dict[str, FieldInfo]:
    """Parse common fields from the common fields documentation."""
    display_url, fetch_url = get_doc_urls("normalization-common-fields.md", docs_path)
    
    try:
        content = fetch_content(fetch_url)
    except Exception as e:
        print(f"Warning: Common fields file not found at {fetch_url}: {e}")
        return {}
    
    fields: Dict[str, FieldInfo] = {}
    lines = content.split('\n')
    in_standard_log_analytics_section = False
    
    for line in lines:
        # Detect section headers
        if re.match(r'^##\s*Standard Log Analytics fields', line):
            in_standard_log_analytics_section = True
            continue
        if re.match(r'^##\s', line) and in_standard_log_analytics_section:
            in_standard_log_analytics_section = False
        
        # Skip lines that don't look like table rows
        if not re.match(r'^\|.*\|', line):
            continue
        
        # Split by pipe and clean up
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 3:
            continue
        
        # Extract field name
        field_col = parts[1]
        match = re.search(r'\*\*([A-Za-z0-9_]+)\*\*', field_col)
        if match:
            field_name = match.group(1)
            description = ""
            example = ""
            note = ""
            original_description = ""
            
            if in_standard_log_analytics_section:
                field_type = parts[2].strip()
                field_class = "Mandatory"
                
                if field_name == 'Field' or field_type == 'Type':
                    continue
                
                if field_type == 'Date/Time':
                    field_type = 'datetime'
                if field_type == 'String':
                    field_type = 'string'
                    
                # Description is in column 4 for standard log analytics section
                if len(parts) > 3:
                    raw_desc = parts[3].strip()
                    original_description = raw_desc
                    description, example, note = parse_description_field(raw_desc)
            else:
                if len(parts) < 4:
                    continue
                
                field_class = parts[2].strip()
                field_type = parts[3].strip()
                
                if field_name == 'Field' or field_class == 'Class':
                    continue
                    
                # Description is in column 5 for regular common fields
                if len(parts) > 4:
                    raw_desc = parts[4].strip()
                    original_description = raw_desc
                    description, example, note = parse_description_field(raw_desc)
            
            # Skip parser parameters
            if re.match(r'^[a-z_]+$', field_name):
                continue
            
            if field_name in FIELDS_TO_IGNORE:
                continue
            
            if field_name and field_name not in fields:
                fields[field_name] = FieldInfo(
                    field_class=field_class,
                    field_type=field_type,
                    source="CommonFields",
                    description=description,
                    example=example,
                    note=note,
                    original_description=original_description
                )
    
    return fields


def get_network_session_fields(docs_path: str, common_fields: Dict[str, FieldInfo], is_web: bool = False) -> Dict[str, FieldInfo]:
    """Get NetworkSession fields for WebSession comparison."""
    display_url, fetch_url = get_doc_urls("normalization-schema-network.md", docs_path)
    
    try:
        content = fetch_content(fetch_url)
    except Exception as e:
        print(f"Warning: Network schema file not found at {fetch_url}: {e}")
        return {}
    
    return parse_doc_fields(content, common_fields, "NetworkSession")


def format_list_of_values(list_of_values: str, max_items: int = 5) -> str:
    """Format list of values for display."""
    if not list_of_values:
        return ""
    
    values = list_of_values.split('|')
    if len(values) > max_items:
        return ', '.join(values[:max_items]) + f"... (and {len(values) - max_items} more)"
    return ', '.join(values)


def compare_schema(
    schema_name: str,
    csv_data: List[Dict[str, str]],
    docs_path: str,
    common_fields: Dict[str, FieldInfo],
    network_session_fields: Dict[str, FieldInfo],
    schema_urls: Dict[str, Tuple[str, str]],
    is_web: bool = False,
    verbose: bool = True
) -> ComparisonResult:
    """Compare a single schema between CSV and documentation."""
    doc_file = SCHEMA_MAPPING.get(schema_name)
    if not doc_file:
        if verbose:
            print(f"No mapping found for schema: {schema_name}")
        return ComparisonResult(schema=schema_name, doc_file="")
    
    # Get doc content using pre-computed URLs
    display_url, fetch_url = schema_urls.get(schema_name, ("", ""))
    if not fetch_url:
        display_url, fetch_url = get_doc_urls(doc_file, docs_path)
    
    try:
        doc_content = fetch_content(fetch_url)
    except Exception as e:
        if verbose:
            print(f"Documentation file not found: {fetch_url}: {e}")
        return ComparisonResult(schema=schema_name, doc_file=doc_file)
    
    if verbose:
        print(f"\n{'='*40}")
        print(f"Processing schema: {schema_name}")
        print(f"Documentation: {doc_file}")
        print(f"{'='*40}")
    
    # Get CSV fields for this schema
    csv_fields: Dict[str, FieldInfo] = {}
    for row in csv_data:
        if row.get('Schema') == schema_name:
            field_key = row.get('ColumnName', '')
            if field_key in FIELDS_TO_IGNORE:
                continue
            if field_key and field_key not in csv_fields:
                csv_fields[field_key] = FieldInfo(
                    field_type=row.get('ColumnType', ''),
                    field_class=row.get('Class', ''),
                    logical_type=row.get('LogicalType', ''),
                    list_of_values=row.get('ListOfValues', ''),
                    aliased=row.get('Aliased', '')
                )
    
    if verbose:
        print(f"\nCSV has {len(csv_fields)} fields")
    
    # Parse documentation
    doc_fields = parse_doc_fields(doc_content, common_fields, schema_name)
    
    # For WebSession, also include NetworkSession fields
    if schema_name == 'WebSession':
        if verbose:
            print("Adding NetworkSession fields to WebSession comparison...")
        for field_name, field_info in network_session_fields.items():
            if field_name not in doc_fields:
                doc_fields[field_name] = FieldInfo(
                    field_class=field_info.field_class,
                    field_type=field_info.field_type,
                    source="NetworkSessionSchema"
                )
        if verbose:
            print(f"WebSession doc now has {len(doc_fields)} fields (including NetworkSession)")
        
        # Apply WebSession-specific overrides
        if 'DstDomain' in doc_fields:
            doc_fields['DstDomain'].field_class = "Optional"
            if verbose:
                print("  - Applied WebSession override: DstDomain class changed to Optional")
        
        if 'NetworkRuleName' in doc_fields and 'RuleName' not in doc_fields:
            doc_fields['RuleName'] = FieldInfo(
                field_class=doc_fields['NetworkRuleName'].field_class,
                field_type=doc_fields['NetworkRuleName'].field_type,
                source="NetworkSessionSchema-Renamed"
            )
            del doc_fields['NetworkRuleName']
            if verbose:
                print("  - Applied WebSession override: NetworkRuleName renamed to RuleName")
        
        if 'NetworkRuleNumber' in doc_fields and 'RuleNumber' not in doc_fields:
            doc_fields['RuleNumber'] = FieldInfo(
                field_class=doc_fields['NetworkRuleNumber'].field_class,
                field_type=doc_fields['NetworkRuleNumber'].field_type,
                source="NetworkSessionSchema-Renamed"
            )
            del doc_fields['NetworkRuleNumber']
            if verbose:
                print("  - Applied WebSession override: NetworkRuleNumber renamed to RuleNumber")
    
    if verbose:
        print(f"Doc has {len(doc_fields)} field references")
    
    # Initialize result
    result = ComparisonResult(
        schema=schema_name,
        doc_file=doc_file,
        csv_field_count=len(csv_fields),
        doc_field_count=len(doc_fields)
    )
    
    # Track counts
    doc_from_common_fields_count = 0
    csv_matched_common_refs = 0
    
    # Check CSV fields against doc
    for field_name in sorted(csv_fields.keys()):
        csv_field = csv_fields[field_name]
        
        if field_name not in doc_fields:
            # Determine effective type
            effective_type = csv_field.logical_type if csv_field.logical_type else csv_field.field_type
            
            # Determine issue type
            issue_info = get_missing_field_issue_type(field_name)
            
            missing_obj = {
                'Field': field_name,
                'Type': csv_field.field_type,
                'EffectiveType': effective_type,
                'Class': csv_field.field_class,
                'LogicalType': csv_field.logical_type,
                'ListOfValues': format_list_of_values(csv_field.list_of_values),
                'IssueType': issue_info.issue_type,
                'IssueCategory': issue_info.issue_category,
                'IssueDescription': issue_info.issue_description,
            }
            
            if issue_info.issue_type == "Warning":
                result.warnings.append(missing_obj)
                result.warnings_from_missing_in_doc += 1
            else:
                result.missing_in_doc.append(missing_obj)
        else:
            # Track if matched common field reference
            doc_source = doc_fields[field_name].source
            if doc_source in ("CommonFields", "CommonFieldsRef", "NetworkSessionSchema"):
                csv_matched_common_refs += 1
            
            # Determine effective CSV type
            csv_effective_type = csv_field.logical_type if csv_field.logical_type else csv_field.field_type
            doc_type = doc_fields[field_name].field_type
            csv_class = csv_field.field_class
            doc_class = doc_fields[field_name].field_class
            
            # Normalize for comparison
            csv_type_norm = csv_effective_type.lower().strip()
            # Strip parenthetical part from doc type
            doc_type_for_compare = re.sub(r'\s*\([^)]+\)\s*$', '', doc_type)
            doc_type_norm = doc_type_for_compare.lower().strip()
            csv_class_norm = csv_class.split()[0].lower().strip() if csv_class else ""
            doc_class_norm = doc_class.split()[0].lower().strip() if doc_class else ""
            
            # Get type aliases
            csv_type_alt = TYPE_ALIASES.get(csv_type_norm, [csv_type_norm])
            if isinstance(csv_type_alt, str):
                csv_type_alt = [csv_type_alt]
            
            # Skip common fields from type/class comparison
            if doc_fields[field_name].source not in ("CommonFields", "CommonFieldsRef", "CommonFieldsImplicit"):
                doc_type_empty = not doc_type.strip()
                doc_is_alias = doc_class == "Alias"
                
                # Check special cases
                csv_is_generic_enumerated = csv_effective_type == "Enumerated" or csv_field.logical_type == "Enumerated"
                doc_is_specific_enum_type = (re.search(r'(type|name|result|category|action|level)$', doc_type_norm) and 
                                            doc_type_norm != "string")
                
                is_event_schema_version = (field_name == 'EventSchemaVersion' and 
                                          csv_field.logical_type == 'SchemaVersion' and 
                                          doc_type_norm == 'string')
                
                is_datetime_equivalent = ((csv_type_norm == 'datetime' and doc_type_norm == 'date/time') or
                                         (csv_type_norm == 'date/time' and doc_type_norm == 'datetime'))
                
                # Type comparison
                if doc_type_empty and doc_is_alias:
                    pass  # Skip
                elif is_event_schema_version:
                    pass  # Skip
                elif is_datetime_equivalent:
                    pass  # Skip
                elif csv_is_generic_enumerated and doc_is_specific_enum_type:
                    pass  # Skip
                elif csv_type_norm != doc_type_norm and doc_type_norm not in csv_type_alt:
                    issue_info = get_type_mismatch_issue_type(field_name, csv_effective_type, doc_type, doc_class)
                    
                    if issue_info.issue_type != "Ignore":
                        mismatch_obj = {
                            'Field': field_name,
                            'CsvType': csv_field.field_type,
                            'CsvLogicalType': csv_field.logical_type,
                            'CsvEffectiveType': csv_effective_type,
                            'DocType': doc_type,
                            'CsvClass': csv_class,
                            'DocClass': doc_class,
                            'ListOfValues': format_list_of_values(csv_field.list_of_values, 3),
                            'IssueType': issue_info.issue_type,
                            'IssueCategory': issue_info.issue_category,
                            'IssueDescription': issue_info.issue_description,
                        }
                        
                        if issue_info.issue_type == "Warning":
                            result.warnings.append(mismatch_obj)
                        else:
                            result.type_mismatches.append(mismatch_obj)
                
                # Class comparison
                if csv_class_norm != doc_class_norm:
                    issue_info = get_class_mismatch_issue_type(field_name, csv_class, doc_class)
                    
                    class_mismatch_obj = {
                        'Field': field_name,
                        'CsvClass': csv_class,
                        'DocClass': doc_class,
                        'CsvType': csv_field.field_type,
                        'CsvLogicalType': csv_field.logical_type,
                        'IssueType': issue_info.issue_type,
                        'IssueCategory': issue_info.issue_category,
                        'IssueDescription': issue_info.issue_description,
                    }
                    
                    if issue_info.issue_type == "Warning":
                        result.warnings.append(class_mismatch_obj)
                    else:
                        result.class_mismatches.append(class_mismatch_obj)
    
    # Check doc fields against CSV
    for field_name in sorted(doc_fields.keys()):
        if doc_fields[field_name].source in ("CommonFields", "CommonFieldsRef", "NetworkSessionSchema"):
            doc_from_common_fields_count += 1
        
        if field_name not in csv_fields:
            result.missing_in_csv.append(field_name)
    
    # Calculate counts
    result.doc_from_common_fields_count = doc_from_common_fields_count
    result.doc_unique_field_count = result.doc_field_count - doc_from_common_fields_count
    result.matched_common_refs_count = csv_matched_common_refs
    matched_fields = result.csv_field_count - len(result.missing_in_doc) - result.warnings_from_missing_in_doc
    result.matched_unique_field_count = matched_fields - csv_matched_common_refs
    
    # Print results
    if verbose:
        if result.missing_in_doc:
            print(f"\n  Fields in CSV but MISSING in doc (Errors): {len(result.missing_in_doc)}")
            for item in result.missing_in_doc[:10]:
                print(f"    {item['Field']}: {item['EffectiveType']}, {item['Class']}")
        else:
            print("\n  [OK] All CSV fields are documented")
        
        if result.missing_in_csv:
            print(f"\n  Fields in doc but MISSING in CSV: {len(result.missing_in_csv)}")
            for field in result.missing_in_csv[:10]:
                print(f"    {field}")
        else:
            print("\n  [OK] No extra fields in doc")
        
        if result.type_mismatches:
            print(f"\n  TYPE MISMATCHES (Errors): {len(result.type_mismatches)}")
            for item in result.type_mismatches[:10]:
                print(f"    {item['Field']}: CSV={item['CsvEffectiveType']}, Doc={item['DocType']}")
        else:
            print("\n  [OK] All types match")
        
        if result.class_mismatches:
            print(f"\n  CLASS MISMATCHES (Errors): {len(result.class_mismatches)}")
            for item in result.class_mismatches[:10]:
                print(f"    {item['Field']}: CSV={item['CsvClass']}, Doc={item['DocClass']}")
        else:
            print("\n  [OK] All classes match")
        
        if result.warnings:
            print(f"\n  WARNINGS: {len(result.warnings)}")
            by_category = defaultdict(list)
            for w in result.warnings:
                by_category[w['IssueCategory']].append(w['Field'])
            for cat, fields in by_category.items():
                print(f"    {cat}: {len(fields)} - {', '.join(fields[:3])}{'...' if len(fields) > 3 else ''}")
        
        print(f"\n  Field Count Summary:")
        print(f"    CSV: {result.csv_field_count} fields")
        print(f"    Doc: {result.doc_field_count} fields ({result.doc_from_common_fields_count} from common/refs, {result.doc_unique_field_count} unique to this schema)")
    
    return result


def generate_markdown_report(results: List[ComparisonResult]) -> str:
    """Generate the markdown report from comparison results."""
    lines = []
    lines.append("# ASIM Schema Comparison Report")
    lines.append("")
    lines.append("Comparison of CSV field definitions with documentation.")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    
    # Calculate totals
    total_missing = sum(len(r.missing_in_doc) for r in results)
    total_missing_warnings = sum(r.warnings_from_missing_in_doc for r in results)
    total_extra = sum(len(r.missing_in_csv) for r in results)
    total_type_mismatch = sum(len(r.type_mismatches) for r in results)
    total_class_mismatch = sum(len(r.class_mismatches) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)
    
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Schemas Compared | {len(results)} |")
    lines.append(f"| Total Fields Missing in Docs (Errors) | {total_missing} |")
    lines.append(f"| Total Fields Missing in Docs (Warnings) | {total_missing_warnings} |")
    lines.append(f"| Total Fields Missing in CSV | {total_extra} |")
    lines.append(f"| Total Type Mismatches (Errors) | {total_type_mismatch} |")
    lines.append(f"| Total Class Mismatches (Errors) | {total_class_mismatch} |")
    lines.append(f"| Total Warnings | {total_warnings} |")
    lines.append("")
    
    lines.append("### Warning Categories")
    lines.append("")
    lines.append("Warnings are issues that are known limitations or expected based on documentation patterns:")
    lines.append("")
    lines.append("- **SpecificIDsDocumentedCentrally**: User ID fields (e.g., *UserAadId, *UserSid) are documented in a central location")
    lines.append("- **LogicalTypeNotInDocs**: CSV has a logical type but docs show the physical type - logical type should be added to docs")
    lines.append("- **ComplexAliasNotSupported**: Field is marked as Alias in docs but ASIM tester doesn't support complex aliases")
    lines.append("- **ConditionalNotSupported**: Field is marked as Conditional in docs but ASIM tester doesn't support conditional class logic")
    lines.append("")
    
    lines.append("## Schema-by-Schema Analysis")
    
    for result in sorted(results, key=lambda r: r.schema):
        lines.append("")
        lines.append(f"### {result.schema}")
        lines.append("")
        lines.append(f"**Doc File:** `{result.doc_file}`")
        lines.append("")
        lines.append("| Metric | Count |")
        lines.append("|--------|-------|")
        lines.append(f"| CSV Fields | {result.csv_field_count} |")
        lines.append(f"| Doc Fields | {result.doc_field_count} |")
        lines.append(f"| Missing in Doc (Errors) | {len(result.missing_in_doc)} |")
        lines.append(f"| Missing in Doc (Warnings) | {result.warnings_from_missing_in_doc} |")
        lines.append(f"| Missing in CSV | {len(result.missing_in_csv)} |")
        lines.append(f"| Type Mismatches (Errors) | {len(result.type_mismatches)} |")
        lines.append(f"| Class Mismatches (Errors) | {len(result.class_mismatches)} |")
        lines.append(f"| Warnings | {len(result.warnings)} |")
        
        if result.missing_in_doc:
            lines.append("")
            lines.append("#### Fields Missing in Doc (Errors)")
            lines.append("")
            for item in result.missing_in_doc:
                lines.append(f"- `{item['Field']}` ({item['EffectiveType']}, {item['Class']})")
        
        if result.missing_in_csv:
            lines.append("")
            lines.append("#### Fields Missing in CSV")
            lines.append("")
            for field in result.missing_in_csv:
                lines.append(f"- `{field}`")
        
        if result.type_mismatches:
            lines.append("")
            lines.append("#### Type Mismatches (Errors)")
            lines.append("")
            for item in result.type_mismatches:
                lines.append(f"- `{item['Field']}`: CSV={item['CsvEffectiveType']}, Doc={item['DocType']}")
        
        if result.class_mismatches:
            lines.append("")
            lines.append("#### Class Mismatches (Errors)")
            lines.append("")
            for item in result.class_mismatches:
                lines.append(f"- `{item['Field']}`: CSV={item['CsvClass']}, Doc={item['DocClass']}")
        
        if result.warnings:
            lines.append("")
            lines.append("#### Warnings")
            lines.append("")
            
            # Group warnings by category
            by_category = defaultdict(list)
            for w in result.warnings:
                by_category[w['IssueCategory']].append(w)
            
            for category in sorted(by_category.keys()):
                lines.append(f"**{category}:**")
                for warning in by_category[category]:
                    field_info = warning.get('Field', 'Unknown')
                    details = ""
                    if warning.get('CsvEffectiveType') and warning.get('DocType'):
                        details = f" (CSV={warning['CsvEffectiveType']}, Doc={warning['DocType']})"
                    elif warning.get('CsvClass') and warning.get('DocClass'):
                        details = f" (CSV={warning['CsvClass']}, Doc={warning['DocClass']})"
                    elif warning.get('EffectiveType'):
                        details = f" ({warning['EffectiveType']}, {warning['Class']})"
                    lines.append(f"- `{field_info}`{details}")
                lines.append("")
    
    return '\n'.join(lines)


def generate_issues_csv(results: List[ComparisonResult]) -> str:
    """Generate CSV content for all issues."""
    output = StringIO()
    fieldnames = ['Schema', 'Field', 'IssueType', 'IssueCategory', 'IssueDescription',
                  'CsvType', 'CsvLogicalType', 'CsvEffectiveType', 'DocType', 'CsvClass', 'DocClass']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for result in results:
        # Missing in doc
        for item in result.missing_in_doc:
            writer.writerow({
                'Schema': result.schema,
                'Field': item['Field'],
                'IssueType': item['IssueType'],
                'IssueCategory': item['IssueCategory'],
                'IssueDescription': item['IssueDescription'],
                'CsvType': item.get('Type', ''),
                'CsvLogicalType': item.get('LogicalType', ''),
                'CsvEffectiveType': item.get('EffectiveType', ''),
                'DocType': '',
                'CsvClass': item.get('Class', ''),
                'DocClass': '',
            })
        
        # Missing in CSV
        for field in result.missing_in_csv:
            writer.writerow({
                'Schema': result.schema,
                'Field': field,
                'IssueType': 'Error',
                'IssueCategory': 'MissingInCsv',
                'IssueDescription': 'Field in doc but missing in CSV',
                'CsvType': '',
                'CsvLogicalType': '',
                'CsvEffectiveType': '',
                'DocType': '',
                'CsvClass': '',
                'DocClass': '',
            })
        
        # Type mismatches
        for item in result.type_mismatches:
            writer.writerow({
                'Schema': result.schema,
                'Field': item['Field'],
                'IssueType': item['IssueType'],
                'IssueCategory': item['IssueCategory'],
                'IssueDescription': item['IssueDescription'],
                'CsvType': item.get('CsvType', ''),
                'CsvLogicalType': item.get('CsvLogicalType', ''),
                'CsvEffectiveType': item.get('CsvEffectiveType', ''),
                'DocType': item.get('DocType', ''),
                'CsvClass': item.get('CsvClass', ''),
                'DocClass': item.get('DocClass', ''),
            })
        
        # Class mismatches
        for item in result.class_mismatches:
            writer.writerow({
                'Schema': result.schema,
                'Field': item['Field'],
                'IssueType': item['IssueType'],
                'IssueCategory': item['IssueCategory'],
                'IssueDescription': item['IssueDescription'],
                'CsvType': item.get('CsvType', ''),
                'CsvLogicalType': item.get('CsvLogicalType', ''),
                'CsvEffectiveType': '',
                'DocType': '',
                'CsvClass': item.get('CsvClass', ''),
                'DocClass': item.get('DocClass', ''),
            })
        
        # Warnings
        for item in result.warnings:
            writer.writerow({
                'Schema': result.schema,
                'Field': item['Field'],
                'IssueType': item['IssueType'],
                'IssueCategory': item['IssueCategory'],
                'IssueDescription': item['IssueDescription'],
                'CsvType': item.get('CsvType', item.get('Type', '')),
                'CsvLogicalType': item.get('CsvLogicalType', item.get('LogicalType', '')),
                'CsvEffectiveType': item.get('CsvEffectiveType', item.get('EffectiveType', '')),
                'DocType': item.get('DocType', ''),
                'CsvClass': item.get('CsvClass', item.get('Class', '')),
                'DocClass': item.get('DocClass', ''),
            })
    
    return output.getvalue()


def generate_all_fields_csv(results: List[ComparisonResult], csv_data: List[Dict], docs_path: str, 
                           common_fields: Dict[str, FieldInfo], network_session_fields: Dict[str, FieldInfo],
                           is_web: bool = False) -> str:
    """Generate CSV content for all fields."""
    output = StringIO()
    fieldnames = ['Schema', 'Field', 'InDoc', 'InCsv', 'DocClass', 'CsvClass', 
                  'DocType', 'CsvType', 'CsvLogicalType', 'DocSource', 'Description', 'Example', 'Note', 'OriginalDescription']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for schema_name in sorted(SCHEMA_MAPPING.keys()):
        # Get CSV fields
        csv_fields = {}
        for row in csv_data:
            if row.get('Schema') == schema_name:
                field_key = row.get('ColumnName', '')
                if field_key and field_key not in FIELDS_TO_IGNORE:
                    csv_fields[field_key] = {
                        'Type': row.get('ColumnType', ''),
                        'Class': row.get('Class', ''),
                        'LogicalType': row.get('LogicalType', ''),
                    }
        
        # Get doc fields
        doc_file = SCHEMA_MAPPING.get(schema_name)
        display_url, fetch_url = get_doc_urls(doc_file, docs_path)
        
        try:
            doc_content = fetch_content(fetch_url)
            doc_fields = parse_doc_fields(doc_content, common_fields, schema_name)
            
            # Add NetworkSession fields for WebSession
            if schema_name == 'WebSession':
                for field_name, field_info in network_session_fields.items():
                    if field_name not in doc_fields:
                        doc_fields[field_name] = FieldInfo(
                            field_class=field_info.field_class,
                            field_type=field_info.field_type,
                            source="NetworkSessionSchema",
                            description=field_info.description,
                            example=field_info.example,
                            note=field_info.note,
                            original_description=field_info.original_description
                        )
        except Exception:
            doc_fields = {}
        
        # Combine all field names
        all_fields = set(csv_fields.keys()) | set(doc_fields.keys())
        
        for field_name in sorted(all_fields):
            in_csv = field_name in csv_fields
            in_doc = field_name in doc_fields
            
            writer.writerow({
                'Schema': schema_name,
                'Field': field_name,
                'InDoc': 'Yes' if in_doc else 'No',
                'InCsv': 'Yes' if in_csv else 'No',
                'DocClass': doc_fields[field_name].field_class if in_doc else '',
                'CsvClass': csv_fields[field_name]['Class'] if in_csv else '',
                'DocType': doc_fields[field_name].field_type if in_doc else '',
                'CsvType': csv_fields[field_name]['Type'] if in_csv else '',
                'CsvLogicalType': csv_fields[field_name]['LogicalType'] if in_csv else '',
                'DocSource': doc_fields[field_name].source if in_doc else '',
                'Description': doc_fields[field_name].description if in_doc else '',
                'Example': doc_fields[field_name].example if in_doc else '',
                'Note': doc_fields[field_name].note if in_doc else '',
                'OriginalDescription': doc_fields[field_name].original_description if in_doc else '',
            })
    
    return output.getvalue()


def main():
    parser = argparse.ArgumentParser(
        description='ASIM Schema Comparison Tool - Compare CSV field definitions with documentation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use defaults (web sources)
  python compare_asim.py

  # Use local files
  python compare_asim.py --csv ./ASimTester.csv --docs ../articles/sentinel

  # Use custom web URL for CSV
  python compare_asim.py --csv https://example.com/ASimTester.csv

  # Specify output directory
  python compare_asim.py --output ./reports

  # Compare specific schema only
  python compare_asim.py --schema NetworkSession

  # Refresh cache (clear and re-fetch all content)
  python compare_asim.py --refresh-cache

  # Skip cache for this run only (use existing cache next time)
  python compare_asim.py --skip-cache

  # Set cache TTL to 1 day (86400 seconds)
  python compare_asim.py --cache-ttl 86400
"""
    )
    
    parser.add_argument(
        '--csv',
        default='https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/ASIM/dev/ASimTester/ASimTester.csv',
        help='Path or URL to the ASIM CSV file (default: Azure Sentinel GitHub)'
    )
    
    parser.add_argument(
        '--docs',
        default='https://learn.microsoft.com/en-us/azure/sentinel/normalization-about-schemas',
        help='Path to docs folder or URL to ASIM schema docs page (default: Microsoft Learn)'
    )
    
    parser.add_argument(
        '--output',
        default='.',
        help='Output directory for reports (default: current directory)'
    )
    
    parser.add_argument(
        '--schema',
        default='',
        help='Specific schema to compare (default: all schemas)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress verbose output'
    )
    
    parser.add_argument(
        '--refresh-cache',
        action='store_true',
        help='Clear cache and fetch fresh content (repopulates cache for future runs)'
    )
    
    parser.add_argument(
        '--skip-cache',
        action='store_true',
        help='Skip cache for this run only (does not read or write cache, leaves existing cache intact)'
    )
    
    parser.add_argument(
        '--cache-ttl',
        type=int,
        default=DEFAULT_CACHE_TTL,
        metavar='SECONDS',
        help=f'Cache time-to-live in seconds (default: {DEFAULT_CACHE_TTL})'
    )
    
    parser.add_argument(
        '--cache-dir',
        default=str(DEFAULT_CACHE_DIR),
        help=f'Directory for cache files (default: {DEFAULT_CACHE_DIR})'
    )
    
    args = parser.parse_args()
    
    # Configure cache settings
    global _cache_enabled, _cache_dir, _cache_ttl
    _cache_enabled = not args.skip_cache
    _cache_dir = Path(args.cache_dir)
    _cache_ttl = args.cache_ttl
    
    verbose = not args.quiet
    
    # Handle cache refresh
    if args.refresh_cache:
        if verbose:
            print("Refreshing cache...")
        count = clear_cache()
        if verbose:
            print(f"Cleared {count} cached files")
    
    # Determine if using web sources
    csv_is_web = args.csv.startswith('http://') or args.csv.startswith('https://')
    docs_is_web = args.docs.startswith('http://') or args.docs.startswith('https://')
    
    # Set docs path for local or web
    if docs_is_web:
        docs_path = args.docs
    else:
        docs_path = args.docs
    
    if verbose:
        print("ASIM Schema Comparison Tool")
        print("="*40)
        print(f"CSV Source: {args.csv}")
        print(f"Docs Source: {args.docs}")
        print(f"Output: {args.output}")
        if _cache_enabled:
            print(f"Cache: enabled (TTL: {_cache_ttl}s, dir: {_cache_dir})")
        else:
            print("Cache: disabled")
        print()
    
    # Fetch CSV data
    if verbose:
        print("Reading CSV file...")
    csv_data = fetch_csv_data(args.csv)
    
    # Parse common fields
    if verbose:
        print("Parsing common fields...")
    common_fields = parse_common_fields(docs_path, docs_is_web)
    if verbose:
        print(f"Found {len(common_fields)} common fields")
    
    # Parse NetworkSession fields for WebSession comparison
    if verbose:
        print("Parsing NetworkSession fields for WebSession comparison...")
    network_session_fields = get_network_session_fields(docs_path, common_fields, docs_is_web)
    if verbose:
        print(f"Found {len(network_session_fields)} NetworkSession fields")
    
    # Get schema URLs and display them
    schema_urls = get_schema_urls(docs_path, verbose=verbose)
    
    # Determine which schemas to process
    if args.schema:
        schemas = [args.schema]
    else:
        schemas = list(SCHEMA_MAPPING.keys())
    
    # Compare each schema
    results: List[ComparisonResult] = []
    for schema_name in schemas:
        result = compare_schema(
            schema_name=schema_name,
            csv_data=csv_data,
            docs_path=docs_path,
            common_fields=common_fields,
            network_session_fields=network_session_fields,
            schema_urls=schema_urls,
            is_web=docs_is_web,
            verbose=verbose
        )
        if result.doc_file:
            results.append(result)
    
    # Generate outputs
    os.makedirs(args.output, exist_ok=True)
    
    # Markdown report
    report_path = os.path.join(args.output, 'ASIM-Comparison-Detailed-Report.md')
    report_content = generate_markdown_report(results)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    if verbose:
        print(f"\nReport generated: {report_path}")
    
    # Issues CSV
    issues_csv_path = os.path.join(args.output, 'comparison-report-all-issues.csv')
    issues_content = generate_issues_csv(results)
    with open(issues_csv_path, 'w', encoding='utf-8', newline='') as f:
        f.write(issues_content)
    if verbose:
        print(f"Issues CSV report saved to: {issues_csv_path}")
    
    # All fields CSV
    all_fields_path = os.path.join(args.output, 'comparison-report-all-fields.csv')
    all_fields_content = generate_all_fields_csv(
        results, csv_data, docs_path, common_fields, network_session_fields, docs_is_web
    )
    with open(all_fields_path, 'w', encoding='utf-8', newline='') as f:
        f.write(all_fields_content)
    if verbose:
        print(f"All fields CSV report saved to: {all_fields_path}")
    
    if verbose:
        print("\nComparison complete!")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
