#!/usr/bin/env python3
"""
ASIM Field Information Collector

Collects field information from ASIM (Advanced Security Information Model) 
documentation and outputs a consolidated CSV. Merges data from three sources:

1. **Documentation** - Schema documentation from Microsoft Learn
2. **ASIM Tester** - Field definitions from ASimTester.csv
3. **Physical Tables** - Table schemas from table_schemas.csv

Sources:
- Schema list: https://learn.microsoft.com/en-us/azure/sentinel/normalization-about-schemas
- Common Fields: https://learn.microsoft.com/en-us/azure/sentinel/normalization-common-fields
- Schema documentation files from Microsoft Sentinel documentation
- ASIM Tester CSV: ASIM/dev/ASimTester/ASimTester.csv
- Physical table schemas: table_schemas.csv (collected by collect_table_info.py)

The list of schemas is dynamically fetched from the ASIM schemas overview page.
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
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field as dataclass_field

# Try to import requests for web URL support
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Default documentation base URLs
LEARN_BASE_URL = 'https://learn.microsoft.com/en-us/azure/sentinel'
GITHUB_DOCS_RAW_URL = 'https://raw.githubusercontent.com/MicrosoftDocs/azure-docs/main/articles/sentinel'

# Schema list documentation URL (source of truth for available schemas and entities)
SCHEMA_LIST_DOC = 'normalization-about-schemas.md'

# Common fields documentation file
COMMON_FIELDS_DOC = 'normalization-common-fields.md'

# Cache configuration
DEFAULT_CACHE_DIR = Path('.cache')
DEFAULT_CACHE_TTL = 604800  # 1 week in seconds

# Global cache settings (set from command line)
_cache_enabled = True
_cache_dir = DEFAULT_CACHE_DIR
_cache_ttl = DEFAULT_CACHE_TTL

# Fields to completely ignore (not real fields)
FIELDS_TO_IGNORE = {'Class', 'response_has_ipv4', 'Unix'}

# Registry-specific values to ignore (from Root Keys and Value Types sections)
REGISTRY_NON_FIELDS = {
    'HKEY_LOCAL_MACHINE', 'HKEY_USERS',
    'Reg_None', 'Reg_Sz', 'Reg_Expand_Sz', 'Reg_Binary',
    'Reg_DWord', 'Reg_Multi_Sz', 'Reg_QWord'
}

# KQL Scalar Data Types (physical types)
# From: https://learn.microsoft.com/en-us/kusto/query/scalar-data-types/
KQL_PHYSICAL_TYPES = {
    'bool', 'boolean',
    'datetime', 'date',
    'decimal',
    'dynamic',
    'guid', 'uuid', 'uniqueid',
    'int',
    'long',
    'real', 'double',
    'string',
    'timespan', 'time',
}

# Hash field types that indicate a field contains hash values
HASH_FIELD_TYPES = {'MD5', 'SHA1', 'SHA256', 'SHA512', 'IMPHASH', 'SHA'}

# ---------------------------------------------------------------------------
# Schema Field Overrides
# ---------------------------------------------------------------------------
# Overrides handle differences between schemas that are described textually
# in the documentation but are not captured by the standard field parsing.
#
# Structure:  schema_name → list of override dicts.
#
# Each override dict supports the following keys:
#   "rename":  (old_name, new_name)
#       Rename a field: old_name is replaced by new_name.  If old_name does
#       not exist the rename is silently skipped.
#   "set":  dict of FieldInfo attribute names → values
#       After a rename (or on the field identified by "field"), set/override
#       the listed attributes.
#   "field":  field_name
#       Used without "rename" to modify an existing field in place.
#   "source_note":  str
#       Short text appended to the note attribute explaining why the override
#       was applied.  Defaults to the doc_url if not provided.
#
# Reference:
#   WebSession "Network session fields" section states:
#   https://learn.microsoft.com/azure/sentinel/normalization-schema-web#network-session-fields
#     - NetworkRuleName → RuleName
#     - NetworkRuleNumber → RuleNumber
# ---------------------------------------------------------------------------
SCHEMA_FIELD_OVERRIDES: Dict[str, list] = {
    'WebSession': [
        {
            'rename': ('NetworkRuleName', 'RuleName'),
            'source_note': 'Renamed from NetworkRuleName per WebSession schema doc.',
        },
        {
            'rename': ('NetworkRuleNumber', 'RuleNumber'),
            'source_note': 'Renamed from NetworkRuleNumber per WebSession schema doc.',
        },
    ],
}

# Mapping from physical ASIM table names to schema names
# Used when merging data from table_schemas.csv
ASIM_TABLE_TO_SCHEMA = {
    'ASimAlertEventLogs': 'AlertEvent',
    'ASimAuditEventLogs': 'AuditEvent',
    'ASimAuthenticationEventLogs': 'Authentication',
    'ASimDhcpEventLogs': 'DhcpEvent',
    'ASimDhcpEvent': 'DhcpEvent',
    'ASimDnsActivityLogs': 'Dns',
    'ASimDns': 'Dns',
    'ASimFileEventLogs': 'FileEvent',
    'ASimNetworkSessionLogs': 'NetworkSession',
    'ASimProcessEventLogs': 'ProcessEvent',
    'ASimRegistryEventLogs': 'RegistryEvent',
    'ASimUserManagementActivityLogs': 'UserManagement',
    'ASimWebSessionLogs': 'WebSession',
}

# Subset tables to exclude (vendor-specific or _CL variants)
ASIM_TABLE_EXCLUDE_PATTERNS = [
    re.compile(r'_CL$'),           # Custom log variants
    re.compile(r'SonicWallFirewall$'),  # Vendor-specific tables
    re.compile(r'MicrosoftNXLog$'),     # Vendor-specific tables
]


@dataclass
class LogicalTypeInfo:
    """Information about an ASIM logical type with enumerated values."""
    name: str
    physical_type: str = ""
    description: str = ""
    allowed_values: str = ""  # Pipe-separated list of allowed values
    doc_url: str = ""


@dataclass
class VendorProductInfo:
    """Information about an ASIM vendor and its products."""
    vendor: str
    products: List[str]
    doc_url: str = ""


@dataclass
class EntityInfo:
    """Information about an ASIM entity type."""
    name: str
    doc_file: str
    display_name: str = ""


@dataclass
class EntityFieldInfo:
    """Information about an entity field from documentation."""
    entity: str = ""
    section: str = ""  # Section within the entity doc (e.g., "The user ID and scope")
    field_name: str = ""
    field_class: str = ""
    physical_type: str = ""  # KQL physical type (string, int, bool, etc.)
    logical_type: str = ""  # ASIM logical type (Hostname, IP address, Enumerated, etc.)
    description: str = ""
    example: str = ""
    note: str = ""
    aliased_field: str = ""  # For Alias fields: the field(s) being aliased
    allowed_values: str = ""  # For Enumerated fields: pipe-separated list of values
    original_description: str = ""
    doc_url: str = ""
    type_mismatch: str = ""  # Non-empty if parenthetical type doesn't match derived type


@dataclass
class FieldInfo:
    """Information about a field from documentation, with optional tester and physical schema data."""
    schema: str = ""
    field_name: str = ""
    field_class: str = ""
    physical_type: str = ""  # KQL physical type (string, int, bool, etc.)
    logical_type: str = ""  # ASIM logical type (Hostname, IP address, Enumerated, etc.)
    source: str = ""  # SchemaDoc, CommonFields, CommonFieldsRef, etc.
    description: str = ""
    example: str = ""
    note: str = ""
    aliased_field: str = ""  # For Alias fields: the field(s) being aliased
    allowed_values: str = ""  # For Enumerated fields: pipe-separated list of values
    original_description: str = ""  # Raw description before parsing
    doc_url: str = ""
    type_mismatch: str = ""  # Non-empty if parenthetical type doesn't match derived type
    # Section-based entity/role/group information
    section_title: str = ""  # Original section title from documentation
    entity: str = ""  # user, device, application, process, or empty
    role: str = ""  # src, dst, target, actor, acting, parent, dvc, or empty
    field_group: str = ""  # entity, inspection, schema, common
    schema_type: str = ""  # 'event' or 'entity' (from schema list section)
    conditional_on: str = ""  # For Conditional fields: the field this depends on
    # ASIM Tester data (merged from ASimTester.csv)
    in_tester: bool = False
    tester_class: str = ""  # Only populated if different from field_class
    tester_type: str = ""  # Only populated if different from physical_type
    tester_logical_type: str = ""  # Only populated if different from logical_type
    tester_allowed_values: str = ""  # Only populated if different from allowed_values
    tester_aliased: str = ""  # The Aliased column from tester (conditional dependency)
    # Physical table schema data (merged from table_schemas.csv)
    in_physical_table: bool = False
    physical_table_type: str = ""  # Only populated if different from physical_type
    physical_table_names: str = ""  # Pipe-separated list of tables containing this field


@dataclass
class ExtractionFailure:
    """Information about a field where alias/enumerated/type extraction failed."""
    source_type: str = ""  # "schema" or "entity"
    source_name: str = ""  # Schema name or entity name
    field_name: str = ""
    field_class: str = ""
    physical_type: str = ""
    logical_type: str = ""
    failure_type: str = ""  # "alias", "enumerated", or "type_mismatch"
    original_description: str = ""
    mismatch_message: str = ""  # Details about type mismatch


# =============================================================================
# Caching
# =============================================================================

def get_cache_path(url: str) -> Path:
    """Get the cache file path for a URL."""
    url_hash = hashlib.md5(url.encode()).hexdigest()  # CodeQL [SM02167] MD5 used for cache key generation, not for cryptographic security purposes
    url_parts = url.rstrip('/').split('/')
    readable_name = url_parts[-1] if url_parts else 'unknown'
    readable_name = re.sub(r'[^\w\-.]', '_', readable_name)
    return _cache_dir / f"{readable_name}_{url_hash[:8]}.cache"


def get_cache_metadata_path(cache_path: Path) -> Path:
    """Get the metadata file path for a cache file."""
    return cache_path.with_suffix('.meta')


def is_cache_valid(cache_path: Path) -> bool:
    """Check if a cache file exists and is still valid."""
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
        with open(cache_path, 'r', encoding='utf-8-sig') as f:
            return f.read()
    except IOError:
        return None


def write_to_cache(cache_path: Path, content: str, url: str) -> None:
    """Write content to cache with metadata."""
    if not _cache_enabled:
        return
    
    try:
        _cache_dir.mkdir(parents=True, exist_ok=True)
        
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        meta_path = get_cache_metadata_path(cache_path)
        with open(meta_path, 'w') as f:
            json.dump({
                'url': url,
                'timestamp': time.time(),
                'size': len(content)
            }, f)
    except IOError:
        pass


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


# =============================================================================
# Content Fetching
# =============================================================================

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


# =============================================================================
# Schema and Entity Discovery
# =============================================================================

@dataclass
class SchemaInfo:
    """Information about an ASIM schema."""
    name: str
    doc_file: str
    version: str = ""
    status: str = ""
    schema_type: str = "event"  # 'event' or 'entity'


def fetch_schema_list(docs_base_url: str, verbose: bool = False) -> Dict[str, SchemaInfo]:
    """Fetch and parse the list of schemas from the ASIM schemas overview page.
    
    Parses both the Activity/Event Schemas and Entity Schemas sections,
    tagging each with its schema_type ('event' or 'entity').
    """
    schemas: Dict[str, SchemaInfo] = {}
    
    display_url, fetch_url = get_doc_urls(SCHEMA_LIST_DOC, docs_base_url)
    
    if verbose:
        print(f"\nFetching schema list from {SCHEMA_LIST_DOC}...")
    
    try:
        content = fetch_content(fetch_url, verbose=verbose)
    except Exception as e:
        print(f"Error: Could not fetch schema list from {fetch_url}: {e}")
        return schemas
    
    # Track which section we're in based on markdown headings.
    # Default to 'event'; switch to 'entity' when we hit the Entity Schemas heading.
    current_type = 'event'
    section_pattern = re.compile(r'^#+\s+(.+)', re.IGNORECASE)
    row_pattern = re.compile(r'^\|\s*\[([^\]]+)\]\(([^)]+\.md)\)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|')
    
    for line in content.split('\n'):
        stripped = line.strip()
        
        # Detect section headings
        heading_match = section_pattern.match(stripped)
        if heading_match:
            heading_text = heading_match.group(1).strip().lower()
            if 'entity' in heading_text and 'schema' in heading_text:
                current_type = 'entity'
            elif 'schema' in heading_text and ('activity' in heading_text or 'event' in heading_text):
                current_type = 'event'
            # Other headings (Field naming, Common fields, etc.) end the schema tables
            elif current_type in ('event', 'entity') and 'schema' not in heading_text:
                pass  # Keep current_type for non-schema headings within a section
        
        # Match schema table rows
        match = row_pattern.match(stripped)
        if match:
            display_name = match.group(1).strip()
            doc_file = match.group(2).strip()
            version = match.group(3).strip()
            status = match.group(4).strip()
            
            schema_name = display_name.replace(' ', '')
            if schema_name == 'DNSActivity':
                schema_name = 'Dns'
            elif schema_name == 'DHCPActivity':
                schema_name = 'DhcpEvent'
            elif schema_name == 'FileActivity':
                schema_name = 'FileEvent'
            elif schema_name == 'AuthenticationEvent':
                schema_name = 'Authentication'
            
            if doc_file == 'normalization-schema.md':
                doc_file = 'normalization-schema-network.md'
            
            schemas[schema_name] = SchemaInfo(
                name=schema_name,
                doc_file=doc_file,
                version=version,
                status=status,
                schema_type=current_type,
            )
    
    event_count = sum(1 for s in schemas.values() if s.schema_type == 'event')
    entity_count = sum(1 for s in schemas.values() if s.schema_type == 'entity')
    if verbose:
        print(f"  Found {len(schemas)} schemas ({event_count} event, {entity_count} entity)")
    
    return schemas


def fetch_entity_list(docs_base_url: str, verbose: bool = False) -> Dict[str, EntityInfo]:
    """Fetch and parse the list of entities from the ASIM schemas overview page."""
    entities: Dict[str, EntityInfo] = {}
    
    display_url, fetch_url = get_doc_urls(SCHEMA_LIST_DOC, docs_base_url)
    
    if verbose:
        print(f"\nFetching entity list from {SCHEMA_LIST_DOC}...")
    
    try:
        content = fetch_content(fetch_url, verbose=verbose)
    except Exception as e:
        print(f"Error: Could not fetch entity list from {fetch_url}: {e}")
        return entities
    
    pattern = r'\[([^\]]+Entity)\]\((normalization-entity-[a-z-]+)(?:\.md)?\)'
    
    for match in re.finditer(pattern, content):
        display_name = match.group(1).strip()
        doc_file = match.group(2).strip()
        
        full_match = match.group(0)
        if '#' in full_match:
            continue
        
        if not doc_file.endswith('.md'):
            doc_file = doc_file + '.md'
        
        entity_name = display_name.replace(' Entity', '').replace('The ', '').strip()
        
        if entity_name not in entities:
            entities[entity_name] = EntityInfo(
                name=entity_name,
                doc_file=doc_file,
                display_name=display_name
            )
    
    if verbose:
        print(f"  Found {len(entities)} entities")
    
    return entities


# =============================================================================
# Logical Types
# =============================================================================

def fetch_logical_types(docs_base_url: str, verbose: bool = False) -> Dict[str, LogicalTypeInfo]:
    """Fetch and parse logical types with their allowed values from the ASIM schemas overview page."""
    logical_types: Dict[str, LogicalTypeInfo] = {}
    
    display_url, fetch_url = get_doc_urls(SCHEMA_LIST_DOC, docs_base_url)
    
    if verbose:
        print(f"\nFetching logical types from {SCHEMA_LIST_DOC}...")
    
    try:
        content = fetch_content(fetch_url, verbose=verbose)
    except Exception as e:
        print(f"Error: Could not fetch logical types from {fetch_url}: {e}")
        return logical_types
    
    table_pattern = r'^\|\s*\*\*([A-Za-z]+)\*\*\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|'
    anchor_pattern = r'^\|\s*(?:<a\s+name="([^"]+)"[^>]*>\s*</a>)?\s*\*\*([A-Za-z]+)\*\*\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|'
    
    in_logical_types_section = False
    
    for line in content.split('\n'):
        if re.match(r'^##\s*Logical\s+types', line, re.IGNORECASE):
            in_logical_types_section = True
            continue
        
        if in_logical_types_section and re.match(r'^##\s+', line) and not re.match(r'^##\s*Logical\s+types', line, re.IGNORECASE):
            in_logical_types_section = False
            continue
        
        if not in_logical_types_section:
            continue
        
        if not line.strip().startswith('|'):
            continue
        
        if '---' in line or ('Data type' in line and 'Physical type' in line):
            continue
        
        match = re.match(anchor_pattern, line.strip())
        if match:
            anchor_name = match.group(1) or ""
            type_name = match.group(2).strip()
            physical_type = match.group(3).strip()
            description = match.group(4).strip()
            
            allowed_values = []
            values_match = re.search(r'(?:Possible|Supported|Allowed)\s+values\s+(?:include|are)\s*:?\s*(.+?)(?:\.\s*For|\s*$)', description, re.IGNORECASE | re.DOTALL)
            if values_match:
                values_section = values_match.group(1)
                backtick_values = re.findall(r'`([^`]+)`', values_section)
                allowed_values.extend(backtick_values)
            
            logical_types[type_name] = LogicalTypeInfo(
                name=type_name,
                physical_type=physical_type,
                description=description,
                allowed_values='|'.join(allowed_values),
                doc_url=display_url + '#' + type_name.lower() if anchor_name else display_url
            )
            continue
        
        match = re.match(table_pattern, line.strip())
        if match:
            type_name = match.group(1).strip()
            physical_type = match.group(2).strip()
            description = match.group(3).strip()
            
            if type_name in logical_types:
                continue
            
            logical_types[type_name] = LogicalTypeInfo(
                name=type_name,
                physical_type=physical_type,
                description=description,
                allowed_values='',
                doc_url=display_url
            )
    
    # Add entity type values
    entity_type_values = {
        'DvcIdType': ['MDEid', 'AzureResourceId', 'MD4IoTid', 'VMConnectionId', 'AwsVpcId', 'VectraId', 'Other'],
        'DomainType': ['FQDN', 'Windows'],
        'UserIdType': ['SID', 'UID', 'AADID', 'OktaId', 'AWSId', 'PUID', 'SalesforceId'],
        'UsernameType': ['UPN', 'Windows', 'DN', 'Simple', 'AWSId'],
        'UserType': ['Regular', 'Machine', 'Admin', 'System', 'Application', 'Service Principal', 'Service', 'Anonymous', 'Other'],
        'AppType': ['Process', 'Service', 'Resource', 'URL', 'SaaS application', 'CSP', 'Other'],
    }
    
    entity_type_docs = {
        'DvcIdType': ('normalization-entity-device.md', '#dvcidtype'),
        'DomainType': ('normalization-entity-device.md', '#domaintype'),
        'UserIdType': ('normalization-entity-user.md', '#useridtype'),
        'UsernameType': ('normalization-entity-user.md', '#usernametype'),
        'UserType': ('normalization-entity-user.md', '#usertype'),
        'AppType': ('normalization-entity-application.md', '#apptype'),
    }
    
    for type_name, expected_values in entity_type_values.items():
        entity_display_url, _ = get_doc_urls(entity_type_docs[type_name][0], docs_base_url)
        anchor = entity_type_docs[type_name][1]
        
        if type_name in logical_types:
            logical_types[type_name].allowed_values = '|'.join(expected_values)
            logical_types[type_name].doc_url = entity_display_url + anchor
        else:
            logical_types[type_name] = LogicalTypeInfo(
                name=type_name,
                physical_type='Enumerated',
                description=f"The type of {type_name.replace('Type', '')}",
                allowed_values='|'.join(expected_values),
                doc_url=entity_display_url + anchor
            )
    
    if verbose:
        print(f"  Found {len(logical_types)} logical types")
    
    return logical_types


def write_logical_types_csv(logical_types: Dict[str, LogicalTypeInfo], output_path: Path) -> None:
    """Write logical types to a CSV file."""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'name', 'physical_type', 'allowed_values', 'description', 'doc_url'
        ])
        writer.writeheader()
        
        for lt in sorted(logical_types.values(), key=lambda x: x.name):
            writer.writerow({
                'name': lt.name,
                'physical_type': lt.physical_type,
                'allowed_values': lt.allowed_values,
                'description': lt.description,
                'doc_url': lt.doc_url,
            })
    
    print(f"Wrote {len(logical_types)} logical types to {output_path}")


# =============================================================================
# Vendors and Products
# =============================================================================

def clean_vendor_product_value(value: str) -> str:
    """Clean a vendor or product value by removing markdown formatting."""
    value = re.sub(r'`([^`]*)`', r'\1', value)
    value = re.sub(r'<br>\s*', '', value)
    value = value.strip()
    return value


def fetch_vendors_products(docs_base_url: str, verbose: bool = False) -> Tuple[Set[str], Set[str]]:
    """Fetch the list of allowed vendors and products from the common fields documentation."""
    if verbose:
        print("Fetching vendors and products from normalization-common-fields.md...")
    
    display_url, fetch_url = get_doc_urls('normalization-common-fields.md', docs_base_url)
    
    try:
        content = fetch_content(fetch_url, verbose=verbose)
    except Exception as e:
        if verbose:
            print(f"  Warning: Failed to fetch vendors/products: {e}")
        return set(), set()
    
    vendors = set()
    products = set()
    
    vendors_section_match = re.search(r'##\s*Vendors\s+and\s+products.*?(?=^##\s|\Z)', content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if not vendors_section_match:
        if verbose:
            print("  Warning: Could not find 'Vendors and products' section")
        return set(), set()
    
    vendors_section = vendors_section_match.group(0)
    vendors_section = re.sub(r'\n(?!\|)', ' ', vendors_section)
    
    for line in vendors_section.split('\n'):
        line = line.strip()
        if not line.startswith('|'):
            continue
        
        parts = [p.strip() for p in line.split('|')]
        parts = [p for p in parts if p]
        
        if len(parts) < 2:
            continue
        
        vendor = parts[0]
        products_cell = parts[1]
        
        if vendor in ('', 'Vendor', '---', '--') or '---' in vendor or '--' in vendor:
            continue
        
        if vendor.startswith('-') or vendor.startswith('`-'):
            continue
        
        vendor = clean_vendor_product_value(vendor)
        if vendor and not vendor.startswith('-'):
            vendors.add(vendor)
        
        product_parts = re.split(r'<br>\s*-\s*|-\s*', products_cell)
        for p in product_parts:
            p = clean_vendor_product_value(p)
            if p and p not in ('', '-'):
                products.add(p)
    
    if verbose:
        print(f"  Found {len(vendors)} vendors and {len(products)} products")
    
    return vendors, products


def write_vendors_products_csv(vendors: Set[str], products: Set[str], output_path: Path, doc_url: str = "") -> None:
    """Write vendors and products to a CSV file."""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['type', 'value', 'doc_url'])
        writer.writeheader()
        
        for vendor in sorted(vendors):
            writer.writerow({'type': 'EventVendor', 'value': vendor, 'doc_url': doc_url})
        
        for product in sorted(products):
            writer.writerow({'type': 'EventProduct', 'value': product, 'doc_url': doc_url})
    
    print(f"Wrote {len(vendors)} vendors and {len(products)} products to {output_path}")


# =============================================================================
# Logical Type Reference Expansion
# =============================================================================

def expand_logical_type_references(
    fields: List[FieldInfo],
    logical_types: Dict[str, 'LogicalTypeInfo'],
    verbose: bool = False
) -> int:
    """Post-process fields to expand 'Logical Type:X' references in allowed_values."""
    expanded_count = 0
    
    for field in fields:
        if not field.allowed_values or not field.allowed_values.startswith("Logical Type:"):
            continue
        
        type_name = field.allowed_values[len("Logical Type:"):].strip()
        
        if not field.logical_type or field.logical_type == 'Enumerated':
            field.logical_type = type_name
        
        if type_name in logical_types and logical_types[type_name].allowed_values:
            field.allowed_values = logical_types[type_name].allowed_values
            expanded_count += 1
            if verbose:
                print(f"    Expanded {field.schema}.{field.field_name}: {type_name} -> {field.allowed_values[:50]}...")
        else:
            if verbose:
                print(f"    Warning: {field.schema}.{field.field_name} references '{type_name}' but no values found")
            field.allowed_values = ""
    
    return expanded_count


def expand_entity_logical_type_references(
    fields: List[EntityFieldInfo],
    logical_types: Dict[str, 'LogicalTypeInfo'],
    verbose: bool = False
) -> int:
    """Post-process entity fields to expand 'Logical Type:X' references in allowed_values."""
    expanded_count = 0
    
    for field in fields:
        if not field.allowed_values or not field.allowed_values.startswith("Logical Type:"):
            continue
        
        type_name = field.allowed_values[len("Logical Type:"):].strip()
        
        if not field.logical_type or field.logical_type == 'Enumerated':
            field.logical_type = type_name
        
        if type_name in logical_types and logical_types[type_name].allowed_values:
            field.allowed_values = logical_types[type_name].allowed_values
            expanded_count += 1
            if verbose:
                print(f"    Expanded {field.entity}.{field.field_name}: {type_name} -> {field.allowed_values[:50]}...")
        else:
            if verbose:
                print(f"    Warning: {field.entity}.{field.field_name} references '{type_name}' but no values found")
            field.allowed_values = ""
    
    return expanded_count


# =============================================================================
# Entity Field Parsing
# =============================================================================

def parse_entity_fields(content: str, entity_name: str, doc_url: str = "") -> List[EntityFieldInfo]:
    """Parse field definitions from entity documentation content."""
    fields: List[EntityFieldInfo] = []
    
    lines = content.split('\n')
    current_section = ""
    
    for line in lines:
        section_match = re.match(r'^##\s+(.+)$', line)
        if section_match:
            current_section = section_match.group(1).strip()
            continue
        
        if not re.match(r'^\|.*\|', line):
            continue
        
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 4:
            continue
        
        field_col = parts[1]
        
        if 'Field' in field_col and ('Class' in parts[2] or 'Type' in parts[2] or '---' in parts[2]):
            continue
        if '---' in field_col:
            continue
        
        if 'Value' in field_col or 'Type Name' in field_col:
            continue
        
        field_names = []
        
        bold_matches = re.findall(r'\*\*([A-Za-z0-9_]+)\*\*', field_col)
        if bold_matches:
            field_names.extend(bold_matches)
        else:
            clean_field_col = re.sub(r'<br\s*/?>', ', ', field_col)
            for part in clean_field_col.split(','):
                name = part.strip()
                if re.match(r'^[A-Z][a-zA-Z0-9]+$', name):
                    field_names.append(name)
        
        if not field_names:
            continue
        
        field_class = parts[2].strip() if len(parts) > 2 else ""
        field_type = parts[3].strip() if len(parts) > 3 else ""
        
        valid_classes = {'Optional', 'Mandatory', 'Recommended', 'Conditional', 'Alias'}
        if field_class not in valid_classes:
            continue
        
        physical_type, logical_type, type_mismatch = split_field_type(field_type)
        
        description = ""
        example = ""
        note = ""
        aliased_field = ""
        allowed_values = ""
        original_description = ""
        if len(parts) > 4:
            raw_desc = parts[4].strip()
            original_description = raw_desc
            description, example, note, aliased_field, allowed_values, _ = parse_description_field(raw_desc, field_class, field_type)
        
        for field_name in field_names:
            if field_name and field_name not in FIELDS_TO_IGNORE:
                fields.append(EntityFieldInfo(
                    entity=entity_name,
                    section=current_section,
                    field_name=field_name,
                    field_class=field_class,
                    physical_type=physical_type,
                    logical_type=logical_type,
                    description=description,
                    example=example,
                    note=note,
                    aliased_field=aliased_field,
                    allowed_values=allowed_values,
                    original_description=original_description,
                    doc_url=doc_url,
                    type_mismatch=type_mismatch
                ))
    
    return fields


def collect_all_entity_fields(docs_base_url: str, verbose: bool = False) -> List[EntityFieldInfo]:
    """Collect all fields from all entity documentation pages."""
    all_fields: List[EntityFieldInfo] = []
    
    entities = fetch_entity_list(docs_base_url, verbose=verbose)
    
    if not entities:
        print("Warning: No entities found.")
        return all_fields
    
    for entity_name, entity_info in entities.items():
        if verbose:
            print(f"\nFetching {entity_name} entity...")
        
        display_url, fetch_url = get_doc_urls(entity_info.doc_file, docs_base_url)
        
        try:
            content = fetch_content(fetch_url, verbose=verbose)
        except Exception as e:
            print(f"Warning: Could not fetch {entity_name} entity from {fetch_url}: {e}")
            continue
        
        entity_fields = parse_entity_fields(content, entity_name, display_url)
        
        if verbose:
            print(f"  Found {len(entity_fields)} fields in {entity_name} entity")
        
        all_fields.extend(entity_fields)
    
    all_fields = calculate_hash_aliases_for_entities(all_fields, verbose=verbose)
    
    return all_fields


def calculate_hash_aliases_for_entities(fields: List[EntityFieldInfo], verbose: bool = False) -> List[EntityFieldInfo]:
    """Calculate hash field aliases for Hash-type alias fields in entities."""
    fields_by_entity: Dict[str, List[EntityFieldInfo]] = {}
    for field in fields:
        if field.entity not in fields_by_entity:
            fields_by_entity[field.entity] = []
        fields_by_entity[field.entity].append(field)
    
    updated_fields = []
    hash_aliases_calculated = 0
    
    def is_hash_alias_field(field: EntityFieldInfo) -> bool:
        if field.field_class != 'Alias':
            return False
        if field.aliased_field:
            return False
        if field.logical_type in HASH_FIELD_TYPES:
            return True
        if field.field_name.endswith('Hash'):
            return True
        return False
    
    for field in fields:
        if is_hash_alias_field(field):
            hash_fields = []
            for entity_field in fields_by_entity.get(field.entity, []):
                if entity_field.logical_type in HASH_FIELD_TYPES and entity_field.field_class != 'Alias':
                    hash_fields.append(entity_field.field_name)
            
            if hash_fields:
                updated_field = EntityFieldInfo(
                    entity=field.entity,
                    section=field.section,
                    field_name=field.field_name,
                    field_class=field.field_class,
                    physical_type=field.physical_type,
                    logical_type=field.logical_type,
                    description=field.description,
                    example=field.example,
                    note=field.note,
                    aliased_field='|'.join(sorted(hash_fields)),
                    allowed_values=field.allowed_values,
                    original_description=field.original_description,
                    doc_url=field.doc_url,
                    type_mismatch=field.type_mismatch
                )
                updated_fields.append(updated_field)
                hash_aliases_calculated += 1
                if verbose:
                    print(f"  Calculated entity hash alias for {field.entity}.{field.field_name}: {updated_field.aliased_field}")
            else:
                updated_fields.append(field)
        else:
            updated_fields.append(field)
    
    if verbose and hash_aliases_calculated > 0:
        print(f"\nCalculated entity hash aliases for {hash_aliases_calculated} fields")
    
    return updated_fields


def write_entity_fields_csv(fields: List[EntityFieldInfo], output_path: Path) -> None:
    """Write entity field information to CSV."""
    fieldnames = [
        'entity', 'section', 'field_name', 'field_class', 'physical_type',
        'logical_type', 'aliased_field', 'allowed_values', 'description',
        'example', 'note', 'doc_url', 'original_description',
    ]
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for field in sorted(fields, key=lambda f: (f.entity, f.section, f.field_name)):
            writer.writerow({
                'entity': field.entity,
                'section': field.section,
                'field_name': field.field_name,
                'field_class': field.field_class,
                'physical_type': field.physical_type,
                'logical_type': field.logical_type,
                'aliased_field': field.aliased_field,
                'allowed_values': field.allowed_values,
                'description': field.description,
                'example': field.example,
                'note': field.note,
                'doc_url': field.doc_url,
                'original_description': field.original_description,
            })
    
    print(f"Wrote {len(fields)} entity fields to {output_path}")


# =============================================================================
# Field Name Entity/Role Inference
# =============================================================================

def infer_entity_from_field_name(field_name: str) -> Tuple[str, str]:
    """Infer entity type and role from field name prefix."""
    if not field_name:
        return '', ''
    
    prefix_map = [
        ('TargetApp', 'application', 'target'),
        ('SrcApp', 'application', 'src'),
        ('DstApp', 'application', 'dst'),
        ('ActingUser', 'user', 'actor'),
        ('TargetUser', 'user', 'target'),
        ('Actor', 'user', 'actor'),
        ('Acting', 'process', 'acting'),
        ('Parent', 'process', 'parent'),
        ('Intermediary', 'device', 'intermediary'),
        ('Remote', 'device', 'remote'),
        ('Local', 'device', 'local'),
        ('Target', 'device', 'target'),
        ('Dvc', 'device', 'dvc'),
        ('Src', 'device', 'src'),
        ('Dst', 'device', 'dst'),
    ]
    
    for prefix, entity, role in prefix_map:
        if field_name.startswith(prefix):
            return entity, role
    
    return '', ''


# =============================================================================
# Section Title Parsing
# =============================================================================

def parse_section_title(section_title: str) -> Tuple[str, str, str]:
    """Parse a section title to extract entity, role, and field group."""
    if not section_title:
        return "", "", ""
    
    title = section_title.strip()
    title = re.sub(r'^#+\s*', '', title)
    title = re.sub(r'<a\s+name=[^>]+>\s*</a>', '', title)
    title = re.sub(r'<a\s+name=[^>]+>', '', title)
    title = title.strip().lower()
    
    entity = ""
    role = ""
    field_group = ""
    
    if 'inspection' in title:
        field_group = "inspection"
        return entity, role, field_group
    elif 'common' in title:
        field_group = "common"
    elif any(x in title for x in ['-specific', 'session fields', 'event fields',
                                   'audit fields', 'dhcp fields', 'dns fields',
                                   'network session fields', 'web session fields',
                                   'file fields', 'registry fields', 'alert fields']):
        field_group = "schema"
    elif 'aliases' in title:
        field_group = "schema"
    else:
        field_group = ""
    
    if 'user' in title:
        entity = "user"
    elif 'device' in title or 'system' in title:
        entity = "device"
    elif 'application' in title or 'app ' in title:
        entity = "application"
    elif 'process' in title:
        entity = "process"
    
    if 'source' in title or title.startswith('src'):
        role = "src"
    elif 'destination' in title or title.startswith('dst'):
        role = "dst"
    elif 'target' in title:
        role = "target"
    elif 'actor' in title:
        role = "actor"
    elif 'acting' in title:
        role = "acting"
    elif 'parent' in title:
        role = "parent"
    elif 'dvc' in title or 'device fields' == title or 'reporting device' in title:
        role = "dvc"
    elif 'intermediary' in title:
        role = "intermediary"
    elif 'local' in title:
        role = "local"
    elif 'remote' in title:
        role = "remote"
    
    if role and not entity:
        if role in ('actor', 'target'):
            entity = "user"
        elif role in ('src', 'dst', 'dvc', 'intermediary', 'local', 'remote'):
            entity = "device"
        elif role in ('acting', 'parent'):
            entity = "process"
    
    if (entity or role) and not field_group:
        field_group = "entity"
    
    if not field_group:
        if 'other' in title:
            field_group = "schema"
        elif 'url' in title:
            field_group = "schema"
        elif 'fields' in title:
            field_group = "schema"
    
    return entity, role, field_group


# =============================================================================
# Field Type Parsing
# =============================================================================

def split_field_type(field_type: str) -> Tuple[str, str, str]:
    """Split a field type into physical and logical type components."""
    if not field_type:
        return "", "", ""
    
    field_type = field_type.strip()
    field_type_lower = field_type.lower()
    
    if field_type_lower in KQL_PHYSICAL_TYPES:
        return field_type_lower, "", ""
    
    paren_match = re.match(r'^(.+?)\s*\((\w+)\)$', field_type)
    parenthetical_physical = ""
    if paren_match:
        field_type = paren_match.group(1).strip()
        parenthetical_physical = paren_match.group(2).strip().lower()
        if parenthetical_physical == 'integer':
            parenthetical_physical = 'int'
    
    logical_to_physical = {
        'Boolean': 'bool',
        'Enumerated': 'string',
        'IP address': 'string',
        'IP Address': 'string',
        'MAC': 'string',
        'MAC address': 'string',
        'MAC Address': 'string',
        'FQDN': 'string',
        'Hostname': 'string',
        'Domain': 'string',
        'DomainType': 'string',
        'Username': 'string',
        'UsernameType': 'string',
        'UserIdType': 'string',
        'UserType': 'string',
        'AppType': 'string',
        'DeviceType': 'string',
        'DvcIdType': 'string',
        'MD5': 'string',
        'SHA1': 'string',
        'SHA256': 'string',
        'SHA512': 'string',
        'SHA': 'string',
        'IMPHASH': 'string',
        'Country': 'string',
        'Region': 'string',
        'City': 'string',
        'Latitude': 'real',
        'Longitude': 'real',
        'ConfidenceLevel': 'int',
        'RiskLevel': 'int',
        'SchemaVersion': 'string',
        'ProcessId': 'string',
        'URL': 'string',
        'DnsQueryClassName': 'string',
        'GUID': 'string',
        'Hexadecimal': 'string',
    }
    
    mismatch_message = ""
    if field_type in logical_to_physical:
        derived_physical = logical_to_physical[field_type]
        if parenthetical_physical and parenthetical_physical != derived_physical:
            mismatch_message = f"Parenthetical type '{parenthetical_physical}' doesn't match derived type '{derived_physical}'"
        return derived_physical, field_type, mismatch_message
    
    if field_type == 'String':
        if parenthetical_physical and parenthetical_physical != 'string':
            mismatch_message = f"Parenthetical type '{parenthetical_physical}' doesn't match derived type 'string'"
        return 'string', '', mismatch_message
    if field_type == 'Int':
        if parenthetical_physical and parenthetical_physical != 'int':
            mismatch_message = f"Parenthetical type '{parenthetical_physical}' doesn't match derived type 'int'"
        return 'int', '', mismatch_message
    if field_type == 'Long':
        return 'long', '', ""
    if field_type == 'Bool':
        return 'bool', '', ""
    if field_type == 'DateTime' or field_type == 'Date/Time' or field_type_lower == 'date/time':
        return 'datetime', '', ""
    if field_type == 'Real' or field_type == 'Double':
        return 'real', '', ""
    if field_type == 'Dynamic':
        return 'dynamic', '', ""
    
    if field_type_lower == 'integer':
        return 'int', '', ""
    
    if parenthetical_physical:
        return parenthetical_physical, field_type, ""
    return 'string', field_type, ""


# =============================================================================
# Description Field Parsing
# =============================================================================

def extract_aliased_field(description: str) -> Tuple[str, str]:
    """Extract the aliased field name from an alias field description."""
    if not description:
        return "", description
    
    aliased_fields = []
    cleaned_desc = description
    
    # Pattern 1a: "Alias or friendly name for `FieldName` field"
    pattern1a = r'[Aa]lias\s+(?:or\s+friendly\s+name\s+)?for\s+`([A-Za-z0-9_]+)`(?:\s+field)?\.?'
    match1a = re.search(pattern1a, description)
    if match1a:
        aliased_fields.append(match1a.group(1))
        cleaned_desc = re.sub(pattern1a, '', cleaned_desc).strip()
    
    # Pattern 1b: "Alias for [FieldName](#anchor)" with markdown link
    pattern1b = r'[Aa]lias\s+(?:or\s+friendly\s+name\s+)?for\s+\[([A-Za-z0-9_]+)\]\([^)]+\)'
    match1b = re.search(pattern1b, description)
    if match1b:
        field = match1b.group(1)
        if field not in aliased_fields:
            aliased_fields.append(field)
        cleaned_desc = re.sub(pattern1b, '', cleaned_desc).strip()
    
    # Pattern 2: "Alias to [FieldName](#fieldname)" or "Alias to `FieldName`"
    pattern2 = r'[Aa]lias\s+to\s+(?:the\s+)?(?:\[([A-Za-z0-9_]+)\]\([^)]+\)|`([A-Za-z0-9_]+)`)'
    for match in re.finditer(pattern2, description):
        field = match.group(1) or match.group(2)
        if field and field not in aliased_fields:
            aliased_fields.append(field)
    if aliased_fields and re.search(pattern2, cleaned_desc):
        cleaned_desc = re.sub(r'[Aa]lias\s+to\s+(?:the\s+)?(?:\[[^\]]+\]\([^)]+\)|`[^`]+`)\.?\s*', '', cleaned_desc).strip()
    
    # Pattern 2b: "Alias to either [Field1], [Field2], or [Field3]"
    pattern2b = r'[Aa]lias\s+to\s+either\s+(.+?)(?:,\s*whichever|\.|\s*$)'
    match2b = re.search(pattern2b, description, re.IGNORECASE)
    if match2b:
        alias_part = match2b.group(1)
        field_matches = re.findall(r'\[([A-Za-z0-9_]+)\]\([^)]+\)', alias_part)
        for field in field_matches:
            if field not in aliased_fields:
                aliased_fields.append(field)
    
    # Pattern 3: "may alias the [Field1](#field1), [Field2](#field2)"
    pattern3 = r'(?:may|can|might)\s+alias\s+(?:the\s+)?(?:either\s+)?(.+?)(?:\s+fields?)?\.?(?:<br>|$)'
    match3 = re.search(pattern3, description, re.IGNORECASE)
    if match3:
        alias_part = match3.group(1)
        field_matches = re.findall(r'\[([A-Za-z0-9_]+)\]\([^)]+\)', alias_part)
        for field in field_matches:
            if field not in aliased_fields:
                aliased_fields.append(field)
    
    # Pattern 4a: "Either the value of [FieldName](#anchor) or the value of [FieldName2](#anchor2)"
    pattern4a = r'[Ee]ither\s+(?:the\s+value\s+of\s+)?\[([A-Za-z0-9_]+)\]\([^)]+\)\s+or\s+(?:the\s+value\s+of\s+)?\[([A-Za-z0-9_]+)\]\([^)]+\)'
    match4a = re.search(pattern4a, description)
    if match4a:
        for field in [match4a.group(1), match4a.group(2)]:
            if field and field not in aliased_fields:
                aliased_fields.append(field)
    
    # Pattern 4b: Same with backticks
    pattern4b = r'[Ee]ither\s+(?:the\s+value\s+of\s+)?`([A-Za-z0-9_]+)`\s+or\s+(?:the\s+value\s+of\s+)?`([A-Za-z0-9_]+)`'
    match4b = re.search(pattern4b, description)
    if match4b:
        for field in [match4b.group(1), match4b.group(2)]:
            if field and field not in aliased_fields:
                aliased_fields.append(field)
    
    # Pattern 4c: Plain text
    pattern4c = r'[Ee]ither\s+(?:the\s+value\s+of\s+)?([A-Z][a-zA-Z0-9_]+)\s+or\s+(?:the\s+value\s+of\s+)?([A-Z][a-zA-Z0-9_]+)'
    match4c = re.search(pattern4c, description)
    if match4c:
        for field in [match4c.group(1), match4c.group(2)]:
            if field and field not in aliased_fields:
                aliased_fields.append(field)
    
    # Pattern 5: "can alias the [Field1], [Field2], [Field3], or [Field4] fields"
    pattern5 = r'(?:These\s+fields\s+)?can\s+alias\s+(?:the\s+)?(.+?)(?:\s+fields?)?\.?(?:<br>|$)'
    match5 = re.search(pattern5, description, re.IGNORECASE)
    if match5:
        alias_part = match5.group(1)
        field_matches = re.findall(r'\[([A-Za-z0-9_]+)\]\([^)]+\)', alias_part)
        for field in field_matches:
            if field not in aliased_fields:
                aliased_fields.append(field)
    
    # Pattern 6: Comma-separated list of markdown links at start
    if not aliased_fields:
        link_list_pattern = r'^(?:\[([A-Za-z0-9_]+)\]\([^)]+\)(?:\s*,\s*|\s+or\s+|\s+and\s+))+'
        if re.match(link_list_pattern, description.strip()):
            field_matches = re.findall(r'\[([A-Za-z0-9_]+)\]\([^)]+\)', description)
            for field in field_matches:
                if field not in aliased_fields:
                    aliased_fields.append(field)
    
    cleaned_desc = re.sub(r'^[\s,.\-:]+|[\s,.\-:]+$', '', cleaned_desc).strip()
    cleaned_desc = re.sub(r'<br>\s*<br>', '<br>', cleaned_desc)
    cleaned_desc = re.sub(r'^<br>\s*|<br>\s*$', '', cleaned_desc).strip()
    
    return '|'.join(aliased_fields), cleaned_desc


def extract_allowed_values(description: str) -> Tuple[str, str]:
    """Extract allowed values from an enumerated field description."""
    if not description:
        return "", description
    
    allowed_values = []
    cleaned_desc = description
    values_section_start = -1
    values_section_end = -1
    
    # Check for logical type references FIRST
    logical_type_names = [
        'DomainType', 'DvcIdType', 'DeviceType',
        'UserIdType', 'UsernameType', 'UserType',
        'AppType', 'HashType', 'FilePathType'
    ]
    
    for type_name in logical_type_names:
        ref_pattern = rf'refer\s+to\s+\[{type_name}\]\([^)]+\)'
        if re.search(ref_pattern, description, re.IGNORECASE):
            return f"Logical Type:{type_name}", cleaned_desc
        
        ref_pattern2 = rf'list\s+of\s+allowed\s+values.*?(?:refer|see)\s+to\s+\[{type_name}\]\([^)]+\)'
        if re.search(ref_pattern2, description, re.IGNORECASE | re.DOTALL):
            return f"Logical Type:{type_name}", cleaned_desc
        
        ref_pattern3 = rf'(?:For\s+more\s+information|see)\s*,?\s+\[{type_name}\]\([^)]+\)'
        if re.search(ref_pattern3, description, re.IGNORECASE):
            if not re.search(r'`[A-Za-z0-9_]+`', description):
                return f"Logical Type:{type_name}", cleaned_desc
    
    generic_type_pattern = r'(?:refer|see)\s+to\s+\[([A-Za-z]+Type)\]\([^)]+\)'
    generic_match = re.search(generic_type_pattern, description, re.IGNORECASE)
    if generic_match:
        type_name = generic_match.group(1)
        return f"Logical Type:{type_name}", cleaned_desc
    
    # Pattern 1: "Supported values are/include:"
    pattern1 = r'[Ss]upported\s+values\s+(?:are|include)\s*:?\s*(.+?)(?=<br><br>|\*\*Note\*\*|$)'
    match1 = re.search(pattern1, description, re.DOTALL)
    if match1:
        values_section = match1.group(1)
        values_section_start = match1.start()
        values_section_end = match1.end()
        backtick_values = re.findall(r'`([^`]+)`', values_section)
        bold_values = re.findall(r'\*\*([^*]+)\*\*', values_section)
        for v in backtick_values + bold_values:
            clean_v = v.split(':')[0].strip() if ':' in v else v.strip()
            if clean_v and clean_v not in allowed_values:
                allowed_values.append(clean_v)
        
        if not allowed_values:
            bullet_values = re.findall(r'<br>\s*-\s*([A-Za-z][A-Za-z0-9\s]*?)(?=<br>|\.|,\s*$|$)', values_section)
            for v in bullet_values:
                v = v.strip()
                if v and v not in allowed_values:
                    allowed_values.append(v)
    
    # Pattern 2: "Valid values are:"
    pattern2 = r'[Vv]alid\s+values\s+are\s*:?\s*(.+?)(?:\.|<br>|$)'
    match2 = re.search(pattern2, description)
    if match2 and not allowed_values:
        values_section = match2.group(1)
        values_section_start = match2.start()
        values_section_end = match2.end()
        backtick_values = re.findall(r'`([^`]+)`', values_section)
        bold_values = re.findall(r'\*\*([^*]+)\*\*', values_section)
        for v in backtick_values + bold_values:
            if v and v not in allowed_values:
                allowed_values.append(v)
    
    # Pattern 3: "One of the following values:"
    pattern3 = r'[Oo]ne\s+of\s+the\s+following\s+values\s*:?\s*(.+?)(?:\.|<br><br>|$)'
    match3 = re.search(pattern3, description)
    if match3 and not allowed_values:
        values_section = match3.group(1)
        values_section_start = match3.start()
        values_section_end = match3.end()
        backtick_values = re.findall(r'`([^`]+)`', values_section)
        bold_values = re.findall(r'\*\*([^*]+)\*\*', values_section)
        for v in backtick_values + bold_values:
            if v and v not in allowed_values:
                allowed_values.append(v)
    
    # Pattern 4: "The list of allowed values is"
    pattern4 = r'(?:[Tt]he\s+)?list\s+of\s+allowed\s+values\s+is\s*:?\s*(.+?)(?:\.|<br>|$)'
    match4 = re.search(pattern4, description)
    if match4 and not allowed_values:
        values_section = match4.group(1)
        backtick_values = re.findall(r'`([^`]+)`', values_section)
        for v in backtick_values:
            if v and v not in allowed_values:
                allowed_values.append(v)
    
    # Pattern 5: "Possible values include:"
    pattern5 = r'[Pp]ossible\s+values\s+(?:include|are)\s*:?\s*(.+?)(?:\.|<br><br>|$)'
    match5 = re.search(pattern5, description)
    if match5 and not allowed_values:
        values_section = match5.group(1)
        backtick_values = re.findall(r'`([^`]+)`', values_section)
        for v in backtick_values:
            if v and v not in allowed_values:
                allowed_values.append(v)
    
    # Pattern 6: "the allowed values are:"
    pattern6 = r'(?:the\s+)?allowed\s+values\s+are\s*:?\s*(.+?)(?=<br><br>|$)'
    match6 = re.search(pattern6, description, re.IGNORECASE | re.DOTALL)
    if match6 and not allowed_values:
        values_section = match6.group(1)
        backtick_values = re.findall(r'`([^`]+)`', values_section)
        for v in backtick_values:
            if v and v not in allowed_values:
                allowed_values.append(v)
        if not allowed_values:
            bullet_values = re.findall(r'<br>\s*-\s*(?:\*\*)?([A-Za-z0-9_\s]+?)(?:\*\*)?(?:<br>|$|,)', values_section)
            for v in bullet_values:
                v = v.strip()
                if v and v not in allowed_values:
                    allowed_values.append(v)
    
    # Pattern 7: "Allowed values include:"
    pattern7 = r'[Aa]llowed\s+values\s+(?:include|are)\s*:?\s*(.+?)(?=<br><br>|\*\*Note\*\*|$)'
    match7 = re.search(pattern7, description, re.DOTALL)
    if match7 and not allowed_values:
        values_section = match7.group(1)
        backtick_values = re.findall(r'`([^`]+)`', values_section)
        for v in backtick_values:
            if v and v not in allowed_values:
                allowed_values.append(v)
        if not allowed_values:
            bullet_values = re.findall(r'<br>\s*-\s*(?:\*\*)?([A-Za-z0-9_\s]+?)(?:\*\*)?(?:<br>|$|,)', values_section)
            for v in bullet_values:
                v = v.strip()
                if v and v not in allowed_values:
                    allowed_values.append(v)
    
    # Pattern 7b: Bulleted list with mixed backtick and plain values
    if not allowed_values:
        bullet_section_match = re.search(r'(?:[Ss]upported|[Vv]alid|[Aa]llowed)\s+values.*?(?:include|are)\s*:?\s*(.+?)(?=<br><br>|\*\*Note\*\*|$)', description, re.DOTALL)
        if bullet_section_match:
            values_section = bullet_section_match.group(1)
            if '<br>-' in values_section or '<br> -' in values_section:
                all_backticks = re.findall(r'`([^`]+)`', values_section)
                for v in all_backticks:
                    if v and v not in allowed_values:
                        allowed_values.append(v)
    
    # Pattern 8: "The value is either `X` or `Y`"
    pattern8 = r'[Tt]he\s+value\s+is\s+(?:either\s+)?(.+?)(?:\.|<br>|$)'
    match8 = re.search(pattern8, description)
    if match8 and not allowed_values:
        values_section = match8.group(1)
        backtick_values = re.findall(r'`([^`]+)`', values_section)
        if len(backtick_values) >= 1:
            for v in backtick_values:
                if v and v not in allowed_values:
                    allowed_values.append(v)
    
    # Pattern 8b: "one of the values `X`, `Y`, or `Z`"
    pattern8b = r'(?:one\s+of\s+the\s+)?values?\s+(`[^`]+`(?:,\s*`[^`]+`)*(?:,?\s*or\s+`[^`]+`)?)'
    match8b = re.search(pattern8b, description, re.IGNORECASE)
    if match8b and not allowed_values:
        values_section = match8b.group(1)
        backtick_values = re.findall(r'`([^`]+)`', values_section)
        if len(backtick_values) >= 1:
            for v in backtick_values:
                if v and v not in allowed_values:
                    allowed_values.append(v)
    
    # Pattern 9: FALLBACK - Extract all backticked values as potential enum values
    if not allowed_values:
        example_indicators = ['e.g.', 'e.g:', 'example:', 'example,', 'for example', 'Example:']
        has_example_indicator = any(ind.lower() in description.lower() for ind in example_indicators)
        
        if not has_example_indicator:
            all_backticks = re.findall(r'`([^`]+)`', description)
            potential_values = []
            for v in all_backticks:
                if '#' in v or '/' in v or v.startswith('http'):
                    continue
                if re.match(r'^[A-Z][a-zA-Z]+(?:Field|Type|Id|Name|Addr|Address)$', v):
                    continue
                if v and v not in potential_values:
                    potential_values.append(v)
            
            if 1 <= len(potential_values) <= 10:
                allowed_values = potential_values
    
    # Remove values section from description
    if allowed_values and values_section_start >= 0:
        section_pattern = r'[Ss]upported\s+values\s+(?:are|include)\s*:?\s*.+?(?=<br><br>|\*\*Note\*\*|$)'
        cleaned_desc = re.sub(section_pattern, '', cleaned_desc, flags=re.DOTALL).strip()
        cleaned_desc = re.sub(r'[Vv]alid\s+values\s+are\s*:?\s*.+?(?:\.|<br>|$)', '', cleaned_desc).strip()
        cleaned_desc = re.sub(r'[Oo]ne\s+of\s+the\s+following\s+values\s*:?\s*.+?(?:\.|<br><br>|$)', '', cleaned_desc).strip()
    
    cleaned_desc = re.sub(r'^[\s,.\-:]+|[\s,.\-:]+$', '', cleaned_desc).strip()
    cleaned_desc = re.sub(r'<br>\s*<br>', '<br>', cleaned_desc)
    cleaned_desc = re.sub(r'^<br>\s*|<br>\s*$', '', cleaned_desc).strip()
    
    return '|'.join(allowed_values), cleaned_desc


def parse_description_field(raw_desc: str, field_class: str = "", field_type: str = "") -> Tuple[str, str, str, str, str, str]:
    """Parse a raw description field and extract description, example, note, aliased_field, allowed_values, and conditional_on."""
    if not raw_desc:
        return "", "", "", "", "", ""
    
    description = raw_desc.strip()
    example = ""
    note = ""
    aliased_field = ""
    allowed_values = ""
    conditional_on = ""
    
    # Extract note
    note_match = re.search(r'(?:<br>\s*)*\*\*Note\*\*\s*:?\s*(.+?)\s*$', description, re.IGNORECASE | re.DOTALL)
    if note_match:
        note = note_match.group(1).strip()
        description = description[:note_match.start()].strip()
    
    # Extract aliased field
    if field_class == 'Alias' or 'alias' in description.lower():
        aliased_field, description = extract_aliased_field(description)
    
    # Extract allowed values
    if field_type == 'Enumerated' or 'enumerated' in field_type.lower():
        allowed_values, description = extract_allowed_values(description)
    
    if not allowed_values and ('supported values' in description.lower() or
                                'valid values' in description.lower() or
                                'allowed values' in description.lower()):
        allowed_values, description = extract_allowed_values(description)
    
    # Extract example
    example_patterns = [
        r'(?:<br>\s*)*(?:Example[s]?\s*[:|-]\s*)(.+?)\s*$',
        r'(?:<br>\s*)*(?:e\.g\.?\s*:\s*)(.+?)\s*$',
        r'(?:<br>\s*)*e\.g\.(?:<br>)?\s*(.+?)\s*$',
        r'(?:<br>\s*)*[Ff]or\s+example[:\s,]*(.+?)\s*$',
        r'(?:Preferred format\s*:\s*)?(?:<br>\s*)*e\.g\.?\s*:\s*(.+?)\s*$',
    ]
    
    for pattern in example_patterns:
        example_match = re.search(pattern, description, re.IGNORECASE)
        if example_match:
            example = example_match.group(1).strip()
            description = description[:example_match.start()].strip()
            break
    
    if not example and note:
        for pattern in example_patterns:
            note_example_match = re.search(pattern, note, re.IGNORECASE)
            if note_example_match:
                example = note_example_match.group(1).strip()
                note = note[:note_example_match.start()].strip()
                break
    
    # Clean up example
    if example:
        example = re.sub(r'^e\.g\.?\s*:?\s*', '', example, flags=re.IGNORECASE).strip()
        example = re.sub(r'<br\s*/?>', ' ', example).strip()
        example = re.sub(r'`([^`]*)`', r'\1', example)
        example = re.sub(r'\s+', ' ', example).strip()
        if example.endswith('.'):
            example = example[:-1].strip()
    
    # Extract conditional_on
    if field_class == 'Conditional':
        conditional_patterns = [
            r'(?:This field is )?[Rr]equired if (?:the )?\[([^\]]+)\]\([^)]+\)(?: field)? is (?:used|populated)',
            r'[Rr]equired (?:when|if) (?:the )?\[([^\]]+)\]\([^)]+\)',
            r'[Tt]he type of (?:the )?(?:ID|name|value|domain|scope)? ?stored in (?:the )?\[([^\]]+)\]\([^)]+\)',
            r'[Tt]he type of (?:the )?(?:user |device |source |target |actor )?(?:ID|name|value|domain|scope)? ?stored in (?:the )?\[([^\]]+)\]\([^)]+\)',
            r'[Tt]he type (?:associated with|for) (?:the )?\[([^\]]+)\]\([^)]+\)',
            r'[Mm]andatory if `([^`]+)` is (?:populated|used)',
            r'stored in (?:the )?(?:\[)?([A-Z][A-Za-z0-9]+)(?:\])?(?:\([^)]+\))? (?:alias )?field',
            r'[Rr]equired if (?:the )?(\w+)(?: field)? is (?:used|populated)',
        ]
        for pattern in conditional_patterns:
            cond_match = re.search(pattern, raw_desc)
            if cond_match:
                conditional_on = cond_match.group(1).strip()
                break
    
    # Clean up
    description = re.sub(r'(?:<br>\s*)+$', '', description).strip()
    description = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', description)
    description = re.sub(r'\s+[Ff]or\s*$', '', description).strip()
    description = re.sub(r'[,;:]\s*$', '', description).strip()
    note = re.sub(r'(?:<br>\s*)+$', '', note).strip()
    note = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', note)
    
    return description, example, note, aliased_field, allowed_values, conditional_on


# =============================================================================
# Schema Field Parsing
# =============================================================================

def parse_common_fields(docs_path: str, verbose: bool = False) -> Dict[str, FieldInfo]:
    """Parse common fields from the common fields documentation."""
    display_url, fetch_url = get_doc_urls(COMMON_FIELDS_DOC, docs_path)
    
    try:
        content = fetch_content(fetch_url, verbose=verbose)
    except Exception as e:
        print(f"Warning: Common fields file not found at {fetch_url}: {e}")
        return {}
    
    fields: Dict[str, FieldInfo] = {}
    lines = content.split('\n')
    in_standard_log_analytics_section = False
    
    current_section_title = ""
    current_entity = ""
    current_role = ""
    current_field_group = "common"
    
    for line in lines:
        section_match = re.match(r'^(#{2,4})\s+(.+)$', line)
        if section_match:
            section_level = len(section_match.group(1))
            section_text = section_match.group(2).strip()
            
            if section_level == 2 and 'standard log analytics' in section_text.lower():
                in_standard_log_analytics_section = True
                current_section_title = section_text
                current_entity, current_role, current_field_group = "", "", "common"
                continue
            elif section_level == 2 and in_standard_log_analytics_section:
                in_standard_log_analytics_section = False
            
            if section_level >= 3:
                current_section_title = section_text
                current_entity, current_role, current_field_group = parse_section_title(line)
                if not current_field_group:
                    current_field_group = "common"
            continue
        
        if not re.match(r'^\|.*\|', line):
            continue
        
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 3:
            continue
        
        field_col = parts[1]
        match = re.search(r'\*\*([A-Za-z0-9_]+)\*\*', field_col)
        if match:
            field_name = match.group(1)
            description = ""
            example = ""
            note = ""
            original_description = ""
            aliased_field = ""
            allowed_values = ""
            conditional_on = ""
            
            if in_standard_log_analytics_section:
                field_type = parts[2].strip()
                field_class = "Mandatory"
                
                if field_name == 'Field' or field_type == 'Type':
                    continue
                
                if field_type == 'Date/Time':
                    field_type = 'datetime'
                if field_type == 'String':
                    field_type = 'string'
                
                if len(parts) > 3:
                    raw_desc = parts[3].strip()
                    original_description = raw_desc
                    description, example, note, aliased_field, allowed_values, conditional_on = parse_description_field(raw_desc, field_class, field_type)
            else:
                if len(parts) < 4:
                    continue
                
                field_class = parts[2].strip()
                field_type = parts[3].strip()
                
                if field_name == 'Field' or field_class == 'Class':
                    continue
                
                if len(parts) > 4:
                    raw_desc = parts[4].strip()
                    original_description = raw_desc
                    description, example, note, aliased_field, allowed_values, conditional_on = parse_description_field(raw_desc, field_class, field_type)
            
            if re.match(r'^[a-z_]+$', field_name):
                continue
            
            if field_name in FIELDS_TO_IGNORE:
                continue
            
            physical_type, logical_type, type_mismatch = split_field_type(field_type)
            
            if field_name and field_name not in fields:
                fields[field_name] = FieldInfo(
                    schema="Common",
                    field_name=field_name,
                    field_class=field_class,
                    physical_type=physical_type,
                    logical_type=logical_type,
                    source="CommonFields",
                    description=description,
                    example=example,
                    note=note,
                    aliased_field=aliased_field,
                    allowed_values=allowed_values,
                    original_description=original_description,
                    doc_url=display_url,
                    type_mismatch=type_mismatch,
                    section_title=current_section_title,
                    entity=current_entity,
                    role=current_role,
                    field_group=current_field_group,
                    conditional_on=conditional_on
                )
    
    return fields


def parse_schema_fields(content: str, schema_name: str, common_fields: Dict[str, FieldInfo],
                        doc_url: str = "") -> Dict[str, FieldInfo]:
    """Parse field definitions from schema documentation content."""
    fields: Dict[str, FieldInfo] = {}
    
    if schema_name == 'RegistryEvent':
        content = re.sub(r'(?ms)###\s*Root\s*[Kk]eys.*?(?=###\s*[A-Z]|##\s*Schema\s*updates|$)', '', content)
        content = re.sub(r'(?ms)###\s*Value\s*[Tt]ypes.*?(?=###\s*[A-Z]|##\s*Schema\s*updates|$)', '', content)
    
    lines = content.split('\n')
    in_standard_log_analytics_section = False
    
    current_section_title = ""
    current_entity = ""
    current_role = ""
    current_field_group = ""
    
    for line in lines:
        section_match = re.match(r'^(#{2,4})\s+(.+)$', line)
        if section_match:
            section_level = len(section_match.group(1))
            section_text = section_match.group(2).strip()
            
            if section_level == 2 and 'standard log analytics' in section_text.lower():
                in_standard_log_analytics_section = True
                current_section_title = section_text
                current_entity, current_role, current_field_group = "", "", "common"
                continue
            elif section_level == 2 and in_standard_log_analytics_section:
                in_standard_log_analytics_section = False
            
            if section_level >= 3:
                current_section_title = section_text
                current_entity, current_role, current_field_group = parse_section_title(line)
            continue
        
        if not re.match(r'^\|.*\|', line):
            continue
        
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 3:
            continue
        
        field_col = parts[1]
        match = re.search(r'\*\*([A-Za-z0-9_]+)\*\*', field_col)
        if match:
            field_name = match.group(1)
            
            if in_standard_log_analytics_section:
                field_type = parts[2].strip()
                field_class = "Mandatory"
                
                if field_name == 'Field' or field_type == 'Type':
                    continue
                
                if field_type == 'Date/Time':
                    field_type = 'datetime'
                if field_type == 'String':
                    field_type = 'string'
                
                description = ""
                example = ""
                note = ""
                aliased_field = ""
                allowed_values = ""
                original_description = ""
                conditional_on = ""
                if len(parts) > 3:
                    raw_desc = parts[3].strip()
                    original_description = raw_desc
                    description, example, note, aliased_field, allowed_values, conditional_on = parse_description_field(raw_desc, field_class, field_type)
            else:
                if len(parts) < 4:
                    continue
                
                field_class = parts[2].strip()
                field_type = parts[3].strip()
                
                if field_name == 'Field' or field_class == 'Class':
                    continue
                
                valid_classes = {'Optional', 'Mandatory', 'Recommended', 'Conditional', 'Alias'}
                if field_class not in valid_classes:
                    continue
                
                description = ""
                example = ""
                note = ""
                aliased_field = ""
                allowed_values = ""
                original_description = ""
                conditional_on = ""
                if len(parts) >= 5:
                    raw_desc = parts[4].strip()
                    original_description = raw_desc
                    description, example, note, aliased_field, allowed_values, conditional_on = parse_description_field(raw_desc, field_class, field_type)
            
            if re.match(r'^[a-z_]+$', field_name):
                continue
            
            if field_class == '-' or field_type == '-':
                continue
            
            if field_name in FIELDS_TO_IGNORE or field_name in REGISTRY_NON_FIELDS:
                continue
            
            physical_type, logical_type, type_mismatch = split_field_type(field_type)
            
            if field_name and field_class and field_name not in fields:
                if field_name == 'EventSchema':
                    allowed_values = schema_name
                    if not logical_type:
                        logical_type = 'Enumerated'
                
                final_entity = current_entity
                final_role = current_role
                if not final_entity and not final_role:
                    inferred_entity, inferred_role = infer_entity_from_field_name(field_name)
                    if inferred_entity:
                        final_entity = inferred_entity
                        final_role = inferred_role
                
                fields[field_name] = FieldInfo(
                    schema=schema_name,
                    field_name=field_name,
                    field_class=field_class,
                    physical_type=physical_type,
                    logical_type=logical_type,
                    source="SchemaDoc",
                    description=description,
                    example=example,
                    note=note,
                    aliased_field=aliased_field,
                    allowed_values=allowed_values,
                    original_description=original_description,
                    doc_url=doc_url,
                    type_mismatch=type_mismatch,
                    section_title=current_section_title,
                    entity=final_entity,
                    role=final_role,
                    field_group=current_field_group,
                    conditional_on=conditional_on
                )
    
    # Handle common field references
    pattern = r'-\s*\[([A-Za-z0-9_]+)\]\(normalization-common-fields\.md'
    for cmatch in re.finditer(pattern, content):
        field_name = cmatch.group(1).strip()
        if field_name and field_name not in fields:
            if field_name in common_fields:
                common_field = common_fields[field_name]
                fields[field_name] = FieldInfo(
                    schema=schema_name,
                    field_name=field_name,
                    field_class=common_field.field_class,
                    physical_type=common_field.physical_type,
                    logical_type=common_field.logical_type,
                    source="CommonFieldsRef",
                    description=common_field.description,
                    example=common_field.example,
                    note=common_field.note,
                    aliased_field=common_field.aliased_field,
                    allowed_values=common_field.allowed_values,
                    original_description=common_field.original_description,
                    doc_url=common_field.doc_url,
                    type_mismatch=common_field.type_mismatch,
                    section_title=common_field.section_title,
                    entity=common_field.entity,
                    role=common_field.role,
                    field_group="common",
                    conditional_on=common_field.conditional_on
                )
            else:
                fields[field_name] = FieldInfo(
                    schema=schema_name,
                    field_name=field_name,
                    field_class="Common",
                    physical_type="",
                    logical_type="",
                    source="CommonFieldsRef",
                    doc_url=doc_url,
                    field_group="common"
                )
    
    # Always include TimeGenerated and Type from common fields
    for common_field_name in ['TimeGenerated', 'Type']:
        if common_field_name not in fields and common_field_name in common_fields:
            common_field = common_fields[common_field_name]
            fields[common_field_name] = FieldInfo(
                schema=schema_name,
                field_name=common_field_name,
                field_class=common_field.field_class,
                physical_type=common_field.physical_type,
                logical_type=common_field.logical_type,
                source="CommonFieldsImplicit",
                description=common_field.description,
                example=common_field.example,
                note=common_field.note,
                aliased_field=common_field.aliased_field,
                allowed_values=common_field.allowed_values,
                original_description=common_field.original_description,
                doc_url=common_field.doc_url,
                type_mismatch=common_field.type_mismatch,
                section_title=common_field.section_title,
                entity=common_field.entity,
                role=common_field.role,
                field_group="common",
                conditional_on=common_field.conditional_on
            )
    
    return fields


# =============================================================================
# Schema Field Overrides Application
# =============================================================================

def _apply_schema_overrides(
    all_fields: List[FieldInfo],
    verbose: bool = False,
) -> None:
    """Apply SCHEMA_FIELD_OVERRIDES to collected fields (in-place).

    Supports:
      - "rename": (old, new) — renames a field within its schema.
      - "field" + "set": modify attributes of an existing field.
      - "source_note": appended to the field's note.
    """
    if not SCHEMA_FIELD_OVERRIDES:
        return

    total_applied = 0
    for schema, overrides in SCHEMA_FIELD_OVERRIDES.items():
        for ovr in overrides:
            rename = ovr.get('rename')
            field_name = ovr.get('field')
            attrs = ovr.get('set', {})
            source_note = ovr.get('source_note', '')

            target = None
            if rename:
                old_name, new_name = rename
                for f in all_fields:
                    if f.schema == schema and f.field_name == old_name:
                        target = f
                        break
                if target is None:
                    continue
                target.field_name = new_name
            elif field_name:
                for f in all_fields:
                    if f.schema == schema and f.field_name == field_name:
                        target = f
                        break
                if target is None:
                    continue

            if target is None:
                continue

            # Apply attribute overrides
            for attr, val in attrs.items():
                if hasattr(target, attr):
                    setattr(target, attr, val)

            if source_note:
                existing = target.note or ''
                if source_note not in existing:
                    target.note = (existing + ' ' + source_note).strip()

            total_applied += 1

    if verbose and total_applied:
        print(f"  Applied {total_applied} schema field overrides")


# =============================================================================
# Field Collection and Post-Processing
# =============================================================================

def collect_all_fields(docs_base_url: str, verbose: bool = False) -> List[FieldInfo]:
    """Collect all fields from all schemas."""
    all_fields: List[FieldInfo] = []
    
    schemas = fetch_schema_list(docs_base_url, verbose=verbose)
    
    if not schemas:
        print("Error: No schemas found. Check the documentation source.")
        return all_fields
    
    if verbose:
        print("\nFetching Common fields...")
    common_fields = parse_common_fields(docs_base_url, verbose=verbose)
    
    if verbose:
        print(f"  Found {len(common_fields)} common fields")
    
    for field_info in common_fields.values():
        all_fields.append(field_info)
    
    schema_fields_by_name: Dict[str, Dict[str, FieldInfo]] = {}
    for schema_name, schema_info in schemas.items():
        if verbose:
            print(f"\nFetching {schema_name} schema (v{schema_info.version}, {schema_info.status})...")
        
        display_url, fetch_url = get_doc_urls(schema_info.doc_file, docs_base_url)
        
        try:
            content = fetch_content(fetch_url, verbose=verbose)
        except Exception as e:
            print(f"Warning: Could not fetch {schema_name} schema from {fetch_url}: {e}")
            continue
        
        schema_fields = parse_schema_fields(content, schema_name, common_fields, display_url)
        schema_fields_by_name[schema_name] = schema_fields
        
        if verbose:
            print(f"  Found {len(schema_fields)} fields in {schema_name}")
        
        for field_info in schema_fields.values():
            field_info.schema_type = schema_info.schema_type
            all_fields.append(field_info)
    
    # Schema inheritance: WebSession extends NetworkSession
    if 'NetworkSession' in schema_fields_by_name and 'WebSession' in schema_fields_by_name:
        network_fields = schema_fields_by_name['NetworkSession']
        web_fields = schema_fields_by_name['WebSession']
        inherited_count = 0
        
        for field_name, network_field in network_fields.items():
            if field_name not in web_fields:
                inherited_field = FieldInfo(
                    schema='WebSession',
                    field_name=network_field.field_name,
                    field_class=network_field.field_class,
                    physical_type=network_field.physical_type,
                    logical_type=network_field.logical_type,
                    source='InheritedFromNetworkSession',
                    description=network_field.description,
                    example=network_field.example,
                    note=network_field.note,
                    aliased_field=network_field.aliased_field,
                    allowed_values=network_field.allowed_values,
                    original_description=network_field.original_description,
                    doc_url=network_field.doc_url,
                    type_mismatch=network_field.type_mismatch,
                    section_title=network_field.section_title,
                    entity=network_field.entity,
                    role=network_field.role,
                    field_group=network_field.field_group,
                    schema_type=schemas.get('WebSession', SchemaInfo(name='', doc_file='')).schema_type,
                    conditional_on=network_field.conditional_on
                )
                all_fields.append(inherited_field)
                inherited_count += 1
        
        if verbose and inherited_count > 0:
            print(f"\n  WebSession inherited {inherited_count} fields from NetworkSession")
    
    # Apply schema field overrides (renames, class changes, etc.)
    _apply_schema_overrides(all_fields, verbose=verbose)
    
    # Post-process: Calculate hash aliases
    all_fields = calculate_hash_aliases(all_fields, verbose=verbose)
    
    return all_fields


def calculate_hash_aliases(fields: List[FieldInfo], verbose: bool = False) -> List[FieldInfo]:
    """Calculate hash field aliases for Hash-type alias fields."""
    fields_by_schema: Dict[str, List[FieldInfo]] = {}
    for field in fields:
        if field.schema not in fields_by_schema:
            fields_by_schema[field.schema] = []
        fields_by_schema[field.schema].append(field)
    
    updated_fields = []
    hash_aliases_calculated = 0
    
    def is_hash_alias_field(field: FieldInfo) -> bool:
        if field.field_class != 'Alias':
            return False
        if field.aliased_field:
            return False
        if field.logical_type in HASH_FIELD_TYPES:
            return True
        if field.field_name.endswith('Hash'):
            return True
        return False
    
    for field in fields:
        if is_hash_alias_field(field):
            hash_fields = []
            for schema_field in fields_by_schema.get(field.schema, []):
                if schema_field.logical_type in HASH_FIELD_TYPES and schema_field.field_class != 'Alias':
                    hash_fields.append(schema_field.field_name)
            
            if hash_fields:
                updated_field = FieldInfo(
                    schema=field.schema,
                    field_name=field.field_name,
                    field_class=field.field_class,
                    physical_type=field.physical_type,
                    logical_type=field.logical_type,
                    source=field.source,
                    description=field.description,
                    example=field.example,
                    note=field.note,
                    aliased_field='|'.join(sorted(hash_fields)),
                    allowed_values=field.allowed_values,
                    original_description=field.original_description,
                    doc_url=field.doc_url,
                    type_mismatch=field.type_mismatch,
                    section_title=field.section_title,
                    entity=field.entity,
                    role=field.role,
                    field_group=field.field_group if field.field_group else "schema",
                    conditional_on=field.conditional_on
                )
                updated_fields.append(updated_field)
                hash_aliases_calculated += 1
                if verbose:
                    print(f"  Calculated hash alias for {field.schema}.{field.field_name}: {updated_field.aliased_field}")
            else:
                updated_fields.append(field)
        else:
            updated_fields.append(field)
    
    if verbose and hash_aliases_calculated > 0:
        print(f"\nCalculated hash aliases for {hash_aliases_calculated} fields")
    
    return updated_fields


# =============================================================================
# ASimTester.csv Merge
# =============================================================================

def load_asim_tester_data(tester_path: Path, verbose: bool = False) -> Dict[Tuple[str, str], dict]:
    """Load ASimTester.csv and return a dict keyed by (schema, field_name).
    
    The tester CSV has columns: ColumnName, ColumnType, Class, Schema, LogicalType, ListOfValues, Aliased.
    
    Returns:
        Dict mapping (schema, field_name) to a dict with tester column values.
    """
    if not tester_path.exists():
        if verbose:
            print(f"  Warning: ASimTester.csv not found at {tester_path}")
        return {}
    
    tester_data: Dict[Tuple[str, str], dict] = {}
    
    with open(tester_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            schema = row.get('Schema', '').strip()
            field_name = row.get('ColumnName', '').strip()
            if schema and field_name:
                tester_data[(schema, field_name)] = {
                    'class': row.get('Class', '').strip(),
                    'type': row.get('ColumnType', '').strip(),
                    'logical_type': row.get('LogicalType', '').strip(),
                    'allowed_values': row.get('ListOfValues', '').strip(),
                    'aliased': row.get('Aliased', '').strip(),
                }
    
    if verbose:
        schemas = set(k[0] for k in tester_data.keys())
        print(f"  Loaded {len(tester_data)} tester field entries across {len(schemas)} schemas")
    
    return tester_data


def merge_tester_data(fields: List[FieldInfo], tester_data: Dict[Tuple[str, str], dict], verbose: bool = False) -> int:
    """Merge ASimTester.csv data into FieldInfo objects.
    
    For each field, if there's a matching tester entry (by schema + field_name):
    - Set in_tester = True
    - Only populate tester_* columns if they differ from the doc values (dedup)
    - Always populate tester_aliased (maps to Aliased column, similar to conditional_on)
    
    Returns:
        Number of fields matched from the tester.
    """
    matched = 0
    
    for field in fields:
        key = (field.schema, field.field_name)
        tester = tester_data.get(key)
        
        if tester is None:
            continue
        
        field.in_tester = True
        matched += 1
        
        # tester_class: only set if different from doc field_class
        if tester['class'] and tester['class'] != field.field_class:
            field.tester_class = tester['class']
        
        # tester_type: only set if different from doc physical_type
        if tester['type'] and tester['type'] != field.physical_type:
            field.tester_type = tester['type']
        
        # tester_logical_type: only set if different from doc logical_type
        if tester['logical_type'] and tester['logical_type'] != field.logical_type:
            field.tester_logical_type = tester['logical_type']
        
        # tester_allowed_values: only set if different from doc allowed_values
        if tester['allowed_values'] and tester['allowed_values'] != field.allowed_values:
            field.tester_allowed_values = tester['allowed_values']
        
        # tester_aliased: always set if present (conditional dependency info)
        if tester['aliased']:
            field.tester_aliased = tester['aliased']
    
    if verbose:
        print(f"  Matched {matched} fields from tester data")
    
    return matched


def find_tester_only_fields(fields: List[FieldInfo], tester_data: Dict[Tuple[str, str], dict], verbose: bool = False) -> List[FieldInfo]:
    """Find fields that exist in ASimTester.csv but not in the documentation.
    
    These are fields that the tester knows about but that were not found in any schema doc.
    They are added as new FieldInfo entries with source='TesterOnly'.
    
    Returns:
        List of new FieldInfo objects for tester-only fields.
    """
    # Build set of (schema, field_name) from existing fields
    doc_keys = set((f.schema, f.field_name) for f in fields)
    
    new_fields: List[FieldInfo] = []
    
    for (schema, field_name), tester in tester_data.items():
        if (schema, field_name) in doc_keys:
            continue
        
        # This field exists only in the tester
        new_field = FieldInfo(
            schema=schema,
            field_name=field_name,
            field_class=tester['class'],
            physical_type=tester['type'],
            logical_type=tester['logical_type'],
            source='TesterOnly',
            allowed_values=tester['allowed_values'],
            in_tester=True,
            tester_aliased=tester['aliased'],
        )
        new_fields.append(new_field)
    
    if verbose and new_fields:
        schemas = set(f.schema for f in new_fields)
        print(f"  Found {len(new_fields)} tester-only fields across {len(schemas)} schemas")
    
    return new_fields


# =============================================================================
# Entity Extension Fields
# =============================================================================

# Role prefixes used when prepending entity fields to create schema fields.
# Ordered longest-first so greedy prefix stripping works correctly.
# NOTE: "TargetUser" / "ActingUser" are NOT real role prefixes — they are
# false matches caused by user entity field names starting with "User"
# (e.g. TargetUsername = Target + Username, not TargetUser + name).
ENTITY_ROLE_PREFIXES = [
    'Acting', 'Actor', 'Target', 'Intermediary',
    'Parent', 'Src', 'Dst', 'Dvc', 'Local', 'Remote',
]

# Device entity fields where an extra "Dvc" is inserted between role prefix and
# base name (e.g. Scope → SrcDvcScope, ScopeId → SrcDvcScopeId).
_DEVICE_DVC_INSERT_FIELDS = {'Scope', 'ScopeId'}

# Leading entity-type token in entity field names.  When checking whether an
# entity extension field duplicates an existing schema field, we also try
# stripping this token (e.g. "User" from "UserScope" → "Scope") and checking
# if prefix + stripped_name already exists (e.g. ActorScope).
_ENTITY_TYPE_PREFIX = {
    'user': 'User',
    'device': 'Dvc',
    'application': 'App',
}


def _build_entity_field_lookup(entity_fields: List[EntityFieldInfo]) -> Dict[str, Dict[str, EntityFieldInfo]]:
    """Build entity_type (lower) → {field_name_lower: EntityFieldInfo} lookup."""
    lookup: Dict[str, Dict[str, EntityFieldInfo]] = {}
    for ef in entity_fields:
        entity_lower = ef.entity.lower()
        lookup.setdefault(entity_lower, {})
        lookup[entity_lower][ef.field_name.lower()] = ef
    return lookup


def _entity_role_pairs_for_schema(
    schema_fields: List[FieldInfo],
    entity_lookup: Dict[str, Dict[str, 'EntityFieldInfo']],
) -> Dict[Tuple[str, str], Set[str]]:
    """Return {(entity, role): set_of_prefixes} for documented fields in a schema.

    Only considers fields with source in SchemaDoc / CommonFields* / Inherited,
    ensuring we derive role prefixes from authoritative data.

    Fields with an entity but no role are treated as role="" with prefix "",
    provided the field name matches a known entity field name (confirming the
    entity attribution).
    """
    authoritative_sources = {
        'SchemaDoc', 'CommonFields', 'CommonFieldsRef',
        'CommonFieldsImplicit', 'InheritedFromNetworkSession',
    }
    pairs: Dict[Tuple[str, str], Set[str]] = {}
    for f in schema_fields:
        if f.source not in authoritative_sources:
            continue
        if not f.entity:
            continue
        if f.role:
            key = (f.entity, f.role)
            if key not in pairs:
                pairs[key] = set()
            # Derive the prefix used for this field by matching against known prefixes
            for prefix in ENTITY_ROLE_PREFIXES:
                if f.field_name.startswith(prefix):
                    pairs[key].add(prefix)
                    break
        else:
            # Empty role — verify the field name matches an entity field directly
            entity_fields_map = entity_lookup.get(f.entity, {})
            if f.field_name.lower() in entity_fields_map:
                key = (f.entity, '')
                if key not in pairs:
                    pairs[key] = set()
                pairs[key].add('')  # empty prefix
    return pairs


def _generate_prefixed_name(prefix: str, entity_field_name: str, entity_type: str) -> str:
    """Generate a prefixed field name from an entity field and role prefix.

    Handles special cases for the Device entity:
    - "Scope" and "ScopeId" need "Dvc" inserted between non-Dvc role prefixes
      (e.g. Src + Scope → SrcDvcScope) but use DvcScope for the Dvc role.
    - Dvc-prefixed entity fields (DvcId, DvcAction, …) already embed the "Dvc"
      token, so when the role prefix is also "Dvc" we return the name as-is to
      avoid doubling (DvcId, not DvcDvcId).
    """
    if entity_type == 'device':
        if entity_field_name in _DEVICE_DVC_INSERT_FIELDS:
            if prefix and prefix != 'Dvc':
                return prefix + 'Dvc' + entity_field_name
            elif prefix == 'Dvc':
                return 'Dvc' + entity_field_name  # e.g. DvcScope
            else:
                return entity_field_name  # empty prefix → Scope as-is
        elif entity_field_name.startswith('Dvc') and prefix == 'Dvc':
            # Entity field already carries the Dvc token — don't double it
            return entity_field_name
    return prefix + entity_field_name


def apply_entity_extensions(
    all_fields: List[FieldInfo],
    entity_fields: List[EntityFieldInfo],
    verbose: bool = False,
) -> Tuple[int, List[FieldInfo]]:
    """Reclassify TesterOnly fields that are entity extensions and generate new
    entity extension fields for schemas.

    For each schema, identifies which (entity, role) pairs are used, then:
    1. Reclassifies TesterOnly fields whose names match prefixed entity field
       names → source becomes "EntityExtension", entity/role are populated.
    2. Generates new FieldInfo entries for entity fields that are neither in the
       schema documentation nor the tester.

    Args:
        all_fields: All collected fields (modified in-place for reclassification).
        entity_fields: Entity field definitions from entity documentation.
        verbose: Enable progress output.

    Returns:
        (reclassified_count, new_fields) tuple.
    """
    entity_lookup = _build_entity_field_lookup(entity_fields)

    # Build per-schema field index and entity/role pairs
    fields_by_schema: Dict[str, List[FieldInfo]] = {}
    for f in all_fields:
        fields_by_schema.setdefault(f.schema, []).append(f)

    # Exclude entity-alias fields that represent the entity itself (Src, Dst, Dvc etc.)
    entity_alias_names = {'Src', 'Dst', 'Dvc', 'Process'}

    reclassified = 0
    new_fields: List[FieldInfo] = []

    for schema, schema_fields in fields_by_schema.items():
        if schema == 'Common':
            continue

        # Identify entity/role pairs and their prefixes
        role_pairs = _entity_role_pairs_for_schema(schema_fields, entity_lookup)
        if not role_pairs:
            continue

        # Build existing field name set for this schema
        existing_names = {f.field_name for f in schema_fields}
        # Also build lower-case lookup for case-insensitive matching
        existing_lower = {f.field_name.lower() for f in schema_fields}

        # For each entity/role/prefix combination, generate expected field names
        for (entity_type, role), prefixes in role_pairs.items():
            entity_base_fields = entity_lookup.get(entity_type, {})
            if not entity_base_fields:
                continue

            for prefix in prefixes:
                for ef_name_lower, ef_info in entity_base_fields.items():
                    # Skip entity-level aliases (Src, Dst, Dvc, Process)
                    if ef_info.field_name in entity_alias_names:
                        continue

                    candidate = _generate_prefixed_name(prefix, ef_info.field_name, entity_type)

                    # Skip empty prefix — bare entity fields without a role
                    # prefix should not be added or reclassified in event schemas.
                    if not prefix:
                        continue

                    if candidate.lower() in existing_lower:
                        # Field exists — check if it's TesterOnly and should
                        # be reclassified
                        for f in schema_fields:
                            if f.field_name.lower() == candidate.lower() and f.source == 'TesterOnly':
                                f.source = 'EntityExtension'
                                if not f.entity:
                                    f.entity = entity_type
                                if not f.role:
                                    f.role = role
                                if not f.description and ef_info.description:
                                    f.description = ef_info.description
                                if not f.doc_url and ef_info.doc_url:
                                    f.doc_url = ef_info.doc_url
                                reclassified += 1
                                break
                    else:
                        # Skip generating new fields for empty prefix (no role).
                        # These would be bare entity field names (e.g. SimpleUsername)
                        # that don't belong in event schemas without a role prefix.
                        if not prefix:
                            continue

                        # Before generating, check if stripping the entity-
                        # type prefix yields a field that already exists.
                        # e.g. Actor + UserScope → ActorUserScope; stripped
                        # variant ActorScope may already be in SchemaDoc.
                        etp = _ENTITY_TYPE_PREFIX.get(entity_type, '')
                        if etp and ef_info.field_name.startswith(etp):
                            stripped_base = ef_info.field_name[len(etp):]
                            if stripped_base:  # non-empty after stripping
                                alt = _generate_prefixed_name(prefix, stripped_base, entity_type)
                                if alt.lower() in existing_lower:
                                    continue  # concept already covered

                        # New entity extension field — add it
                        new_field = FieldInfo(
                            schema=schema,
                            field_name=candidate,
                            field_class=ef_info.field_class,
                            physical_type=ef_info.physical_type,
                            logical_type=ef_info.logical_type,
                            source='EntityExtension',
                            description=ef_info.description,
                            example=ef_info.example,
                            note=ef_info.note,
                            aliased_field=ef_info.aliased_field,
                            allowed_values=ef_info.allowed_values,
                            doc_url=ef_info.doc_url,
                            entity=entity_type,
                            role=role,
                        )
                        new_fields.append(new_field)
                        # Add to existing set so we don't create duplicates
                        existing_names.add(candidate)
                        existing_lower.add(candidate.lower())

    # ── Fallback reclassification ────────────────────────────────────────
    # Remaining TesterOnly fields may belong to entity/role combinations
    # that were not detected from the schema's authoritative fields
    # (e.g. ActorDNUsername in AlertEvent where Actor/user isn't documented).
    # Try all known role prefixes and match the remainder against any entity
    # field to reclassify them.  Empty prefix is excluded — bare entity field
    # names without a role (e.g. SimpleUsername) should not appear in event
    # schemas.
    fallback_reclassified = 0
    remaining_tester = [f for f in all_fields if f.source == 'TesterOnly']
    prefixes_to_try = ENTITY_ROLE_PREFIXES  # role prefix required

    for f in remaining_tester:
        matched = False
        for prefix in prefixes_to_try:
            if prefix and not f.field_name.startswith(prefix):
                continue
            remainder = f.field_name[len(prefix):]
            if not remainder:
                continue
            # Check against all entity types
            for entity_type, entity_fields_map in entity_lookup.items():
                # Direct match: remainder == entity field name
                # e.g. ActorUserUpn → strip "Actor" → "UserUpn" matches User.UserUpn
                if remainder.lower() in entity_fields_map:
                    ef_info = entity_fields_map[remainder.lower()]
                    f.source = 'EntityExtension'
                    if not f.entity:
                        f.entity = entity_type
                    if not f.role:
                        f.role = prefix.lower() if prefix else ''
                    if not f.description and ef_info.description:
                        f.description = ef_info.description
                    if not f.doc_url and ef_info.doc_url:
                        f.doc_url = ef_info.doc_url
                    fallback_reclassified += 1
                    matched = True
                    break
                # Shortened match: try inserting entity-type prefix
                # e.g. ActorUpn → strip "Actor" → "Upn", try "User"+"Upn" = "UserUpn"
                etp = _ENTITY_TYPE_PREFIX.get(entity_type, '')
                if etp and (etp + remainder).lower() in entity_fields_map:
                    ef_info = entity_fields_map[(etp + remainder).lower()]
                    f.source = 'EntityExtension'
                    if not f.entity:
                        f.entity = entity_type
                    if not f.role:
                        f.role = prefix.lower() if prefix else ''
                    if not f.description and ef_info.description:
                        f.description = ef_info.description
                    if not f.doc_url and ef_info.doc_url:
                        f.doc_url = ef_info.doc_url
                    fallback_reclassified += 1
                    matched = True
                    break
            if matched:
                break

    reclassified += fallback_reclassified

    if verbose:
        print(f"  Reclassified {reclassified} TesterOnly fields as entity extensions"
              f" ({reclassified - fallback_reclassified} primary + {fallback_reclassified} fallback)")
        if new_fields:
            schemas = set(f.schema for f in new_fields)
            print(f"  Generated {len(new_fields)} new entity extension fields across {len(schemas)} schemas")

    return reclassified, new_fields


# =============================================================================
# Physical Table Schema Merge (table_schemas.csv)
# =============================================================================

def load_physical_table_schemas(table_schemas_path: Path, verbose: bool = False) -> Dict[Tuple[str, str], dict]:
    """Load table_schemas.csv and return ASIM table data keyed by (schema_name, column_name).
    
    Maps physical table names to ASIM schema names using ASIM_TABLE_TO_SCHEMA.
    Excludes vendor-specific and _CL table variants.
    
    Returns:
        Dict mapping (schema_name, column_name) to a dict with:
        - 'type': the column type from the physical table
        - 'tables': set of table names containing this column
    """
    if not table_schemas_path.exists():
        if verbose:
            print(f"  Warning: table_schemas.csv not found at {table_schemas_path}")
        return {}
    
    # Intermediate: group by (schema, column) -> collect table names and types
    schema_columns: Dict[Tuple[str, str], dict] = {}
    skipped_tables = set()
    mapped_tables = set()
    
    with open(table_schemas_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            table_name = row.get('table_name', '').strip()
            column_name = row.get('column_name', '').strip()
            column_type = row.get('column_type', '').strip()
            
            if not table_name or not column_name:
                continue
            
            # Only process ASIM tables
            if not table_name.startswith('ASim'):
                continue
            
            # Exclude vendor-specific and _CL variants
            if any(p.search(table_name) for p in ASIM_TABLE_EXCLUDE_PATTERNS):
                skipped_tables.add(table_name)
                continue
            
            # Map table name to schema name
            schema_name = ASIM_TABLE_TO_SCHEMA.get(table_name)
            if not schema_name:
                skipped_tables.add(table_name)
                continue
            
            mapped_tables.add(table_name)
            key = (schema_name, column_name)
            
            if key not in schema_columns:
                schema_columns[key] = {'type': column_type, 'tables': set()}
            schema_columns[key]['tables'].add(table_name)
            # Use the type from the first table encountered (they should be consistent)
    
    if verbose:
        schemas_found = set(k[0] for k in schema_columns.keys())
        print(f"  Loaded {len(schema_columns)} physical table columns across {len(schemas_found)} schemas")
        print(f"  Mapped tables: {sorted(mapped_tables)}")
        if skipped_tables:
            print(f"  Skipped tables: {sorted(skipped_tables)}")
    
    return schema_columns


def merge_physical_schemas(fields: List[FieldInfo], physical_data: Dict[Tuple[str, str], dict], verbose: bool = False) -> int:
    """Merge physical table schema data into FieldInfo objects.
    
    For each field, if there's a matching physical table column:
    - Set in_physical_table = True
    - Set physical_table_names to the pipe-separated list of tables
    - Only populate physical_table_type if it differs from doc physical_type (dedup)
    
    Returns:
        Number of fields matched from physical schemas.
    """
    matched = 0
    
    for field in fields:
        key = (field.schema, field.field_name)
        physical = physical_data.get(key)
        
        if physical is None:
            continue
        
        field.in_physical_table = True
        field.physical_table_names = '|'.join(sorted(physical['tables']))
        matched += 1
        
        # physical_table_type: only set if different from doc physical_type
        if physical['type'] and physical['type'] != field.physical_type:
            field.physical_table_type = physical['type']
    
    if verbose:
        print(f"  Matched {matched} fields from physical table schemas")
    
    return matched


def find_physical_only_fields(fields: List[FieldInfo], physical_data: Dict[Tuple[str, str], dict], verbose: bool = False) -> List[FieldInfo]:
    """Find fields that exist in physical tables but not in the documentation or tester.
    
    Filters out Log Analytics system columns that appear in all tables but are not
    ASIM fields (e.g., _BilledSize, TenantId, SourceSystem).
    
    Returns:
        List of new FieldInfo objects for physical-table-only fields.
    """
    # Log Analytics system columns that appear in all tables but are not ASIM fields
    LA_SYSTEM_FIELDS = {
        'TenantId', 'SourceSystem', 'MG', 'ManagementGroupName',
        'Computer', 'RawData', 'TimeGenerated',
    }
    
    doc_keys = set((f.schema, f.field_name) for f in fields)
    
    new_fields: List[FieldInfo] = []
    skipped_count = 0
    
    for (schema, field_name), physical in physical_data.items():
        if (schema, field_name) in doc_keys:
            continue
        
        # Skip system columns starting with underscore (_BilledSize, _IsBillable, etc.)
        if field_name.startswith('_'):
            skipped_count += 1
            continue
        
        # Skip known Log Analytics system fields
        if field_name in LA_SYSTEM_FIELDS:
            skipped_count += 1
            continue
        
        new_field = FieldInfo(
            schema=schema,
            field_name=field_name,
            physical_type=physical['type'],
            source='PhysicalTableOnly',
            in_physical_table=True,
            physical_table_names='|'.join(sorted(physical['tables'])),
        )
        new_fields.append(new_field)
    
    if verbose:
        if new_fields:
            schemas = set(f.schema for f in new_fields)
            print(f"  Found {len(new_fields)} physical-table-only fields across {len(schemas)} schemas")
        if skipped_count:
            print(f"  Skipped {skipped_count} Log Analytics system columns")
    
    return new_fields


# =============================================================================
# CSV Output
# =============================================================================

def write_fields_csv(fields: List[FieldInfo], output_path: Path) -> None:
    """Write field information to CSV, including tester and physical table columns."""
    fieldnames = [
        'schema',
        'schema_type',
        'field_name',
        'field_class',
        'physical_type',
        'logical_type',
        'entity',
        'role',
        'field_group',
        'source',
        'aliased_field',
        'allowed_values',
        'conditional_on',
        'description',
        'example',
        'note',
        'doc_url',
        'section_title',
        'original_description',
        # Tester data columns
        'in_tester',
        'tester_class',
        'tester_type',
        'tester_logical_type',
        'tester_allowed_values',
        'tester_aliased',
        # Physical table columns
        'in_physical_table',
        'physical_table_type',
        'physical_table_names',
    ]
    
    # Exclude TesterOnly fields — these are fields found in the tester CSV
    # but not in docs or entity extensions; they may be tester artifacts.
    fields = [f for f in fields if f.source != 'TesterOnly']

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for field in sorted(fields, key=lambda f: (f.schema, f.field_name)):
            writer.writerow({
                'schema': field.schema,
                'schema_type': field.schema_type,
                'field_name': field.field_name,
                'field_class': field.field_class,
                'physical_type': field.physical_type,
                'logical_type': field.logical_type,
                'entity': field.entity,
                'role': field.role,
                'field_group': field.field_group,
                'source': field.source,
                'aliased_field': field.aliased_field,
                'allowed_values': field.allowed_values,
                'conditional_on': field.conditional_on,
                'description': field.description,
                'example': field.example,
                'note': field.note,
                'doc_url': field.doc_url,
                'section_title': field.section_title,
                'original_description': field.original_description,
                'in_tester': 'True' if field.in_tester else '',
                'tester_class': field.tester_class,
                'tester_type': field.tester_type,
                'tester_logical_type': field.tester_logical_type,
                'tester_allowed_values': field.tester_allowed_values,
                'tester_aliased': field.tester_aliased,
                'in_physical_table': 'True' if field.in_physical_table else '',
                'physical_table_type': field.physical_table_type,
                'physical_table_names': field.physical_table_names,
            })
    
    print(f"Wrote {len(fields)} fields to {output_path}")


# =============================================================================
# Extraction Failures
# =============================================================================

def collect_extraction_failures(schema_fields: List[FieldInfo], entity_fields: List[EntityFieldInfo]) -> List[ExtractionFailure]:
    """Collect fields where alias, enumerated, or type extraction failed."""
    failures: List[ExtractionFailure] = []
    
    field_values_by_schema: Dict[str, Dict[str, str]] = {}
    common_enum_fields: Dict[str, FieldInfo] = {}
    
    for field in schema_fields:
        if field.schema == 'Common':
            if field.logical_type == 'Enumerated':
                common_enum_fields[field.field_name] = field
        else:
            if field.field_name not in field_values_by_schema:
                field_values_by_schema[field.field_name] = {}
            field_values_by_schema[field.field_name][field.schema] = field.allowed_values
    
    for field in schema_fields:
        if field.field_class == 'Alias' and not field.aliased_field:
            failures.append(ExtractionFailure(
                source_type='schema', source_name=field.schema,
                field_name=field.field_name, field_class=field.field_class,
                physical_type=field.physical_type, logical_type=field.logical_type,
                failure_type='alias', original_description=field.original_description
            ))
        
        if field.logical_type == 'Enumerated' and not field.allowed_values:
            if field.schema == 'Common':
                schema_values = field_values_by_schema.get(field.field_name, {})
                if schema_values:
                    schemas_with_values = sum(1 for v in schema_values.values() if v)
                    if schemas_with_values == len(schema_values) and len(schema_values) > 0:
                        continue
            
            failures.append(ExtractionFailure(
                source_type='schema', source_name=field.schema,
                field_name=field.field_name, field_class=field.field_class,
                physical_type=field.physical_type, logical_type=field.logical_type,
                failure_type='enumerated', original_description=field.original_description
            ))
        
        if field.type_mismatch:
            failures.append(ExtractionFailure(
                source_type='schema', source_name=field.schema,
                field_name=field.field_name, field_class=field.field_class,
                physical_type=field.physical_type, logical_type=field.logical_type,
                failure_type='type_mismatch', original_description=field.original_description,
                mismatch_message=field.type_mismatch
            ))
    
    for field in entity_fields:
        if field.field_class == 'Alias' and not field.aliased_field:
            failures.append(ExtractionFailure(
                source_type='entity', source_name=field.entity,
                field_name=field.field_name, field_class=field.field_class,
                physical_type=field.physical_type, logical_type=field.logical_type,
                failure_type='alias', original_description=field.original_description
            ))
        
        if field.logical_type == 'Enumerated' and not field.allowed_values:
            failures.append(ExtractionFailure(
                source_type='entity', source_name=field.entity,
                field_name=field.field_name, field_class=field.field_class,
                physical_type=field.physical_type, logical_type=field.logical_type,
                failure_type='enumerated', original_description=field.original_description
            ))
        
        if field.type_mismatch:
            failures.append(ExtractionFailure(
                source_type='entity', source_name=field.entity,
                field_name=field.field_name, field_class=field.field_class,
                physical_type=field.physical_type, logical_type=field.logical_type,
                failure_type='type_mismatch', original_description=field.original_description,
                mismatch_message=field.type_mismatch
            ))
    
    return failures


def write_extraction_failures_csv(failures: List[ExtractionFailure], output_path: Path) -> None:
    """Write extraction failures to CSV."""
    fieldnames = [
        'source_type', 'source_name', 'field_name', 'field_class',
        'physical_type', 'logical_type', 'failure_type',
        'mismatch_message', 'original_description',
    ]
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for failure in sorted(failures, key=lambda f: (f.source_type, f.source_name, f.field_name)):
            writer.writerow({
                'source_type': failure.source_type,
                'source_name': failure.source_name,
                'field_name': failure.field_name,
                'field_class': failure.field_class,
                'physical_type': failure.physical_type,
                'logical_type': failure.logical_type,
                'failure_type': failure.failure_type,
                'mismatch_message': failure.mismatch_message,
                'original_description': failure.original_description,
            })
    
    print(f"Wrote {len(failures)} extraction failures to {output_path}")


# =============================================================================
# Summary Report
# =============================================================================

def generate_summary_report(fields: List[FieldInfo]) -> str:
    """Generate a summary report of collected fields."""
    lines = []
    lines.append("# ASIM Field Collection Summary")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    
    schema_counts: Dict[str, int] = {}
    for field in fields:
        schema_counts[field.schema] = schema_counts.get(field.schema, 0) + 1
    
    lines.append(f"Total fields collected: {len(fields)}")
    lines.append(f"Schemas processed: {len(schema_counts)}")
    lines.append("")
    
    # Count by source
    source_counts: Dict[str, int] = {}
    for field in fields:
        source_counts[field.source] = source_counts.get(field.source, 0) + 1
    
    # Tester and physical table stats
    tester_count = sum(1 for f in fields if f.in_tester)
    physical_count = sum(1 for f in fields if f.in_physical_table)
    tester_only = sum(1 for f in fields if f.source == 'TesterOnly')
    physical_only = sum(1 for f in fields if f.source == 'PhysicalTableOnly')
    
    lines.append(f"Fields matched in ASIM Tester: {tester_count}")
    lines.append(f"Fields matched in physical tables: {physical_count}")
    if tester_only:
        lines.append(f"Fields only in tester (not in docs): {tester_only}")
    if physical_only:
        lines.append(f"Fields only in physical tables (not in docs): {physical_only}")
    lines.append("")
    
    lines.append("## Fields per Schema")
    lines.append("")
    lines.append("| Schema | Field Count |")
    lines.append("|--------|-------------|")
    
    for schema_name in sorted(schema_counts.keys()):
        lines.append(f"| {schema_name} | {schema_counts[schema_name]} |")
    
    lines.append("")
    
    lines.append("## Fields by Source")
    lines.append("")
    lines.append("| Source | Field Count |")
    lines.append("|--------|-------------|")
    
    for source in sorted(source_counts.keys()):
        lines.append(f"| {source} | {source_counts[source]} |")
    
    lines.append("")
    
    # Count by class
    class_counts: Dict[str, int] = {}
    for field in fields:
        field_class = field.field_class or "(empty)"
        class_counts[field_class] = class_counts.get(field_class, 0) + 1
    
    lines.append("## Fields by Class")
    lines.append("")
    lines.append("| Class | Field Count |")
    lines.append("|-------|-------------|")
    
    for field_class in sorted(class_counts.keys()):
        lines.append(f"| {field_class} | {class_counts[field_class]} |")
    
    # Add tester diff summary
    tester_class_diff = sum(1 for f in fields if f.tester_class)
    tester_type_diff = sum(1 for f in fields if f.tester_type)
    tester_logical_diff = sum(1 for f in fields if f.tester_logical_type)
    tester_values_diff = sum(1 for f in fields if f.tester_allowed_values)
    physical_type_diff = sum(1 for f in fields if f.physical_table_type)
    
    if any([tester_class_diff, tester_type_diff, tester_logical_diff, tester_values_diff, physical_type_diff]):
        lines.append("")
        lines.append("## Discrepancies")
        lines.append("")
        lines.append("| Discrepancy | Count |")
        lines.append("|-------------|-------|")
        if tester_class_diff:
            lines.append(f"| Tester class differs from docs | {tester_class_diff} |")
        if tester_type_diff:
            lines.append(f"| Tester type differs from docs | {tester_type_diff} |")
        if tester_logical_diff:
            lines.append(f"| Tester logical type differs from docs | {tester_logical_diff} |")
        if tester_values_diff:
            lines.append(f"| Tester allowed values differ from docs | {tester_values_diff} |")
        if physical_type_diff:
            lines.append(f"| Physical table type differs from docs | {physical_type_diff} |")
    
    return '\n'.join(lines)


# =============================================================================
# Main
# =============================================================================

def main():
    # Determine the repo root (Azure-Sentinel) relative to this script
    script_dir = Path(__file__).parent.resolve()
    # Script is at Tools/Solutions Analyzer/collect_asim_fields.py
    # Repo root is two levels up
    repo_root = script_dir.parent.parent
    
    parser = argparse.ArgumentParser(
        description='Collect ASIM field information from documentation, ASIM tester, and physical table schemas',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with defaults (fetch from learn.microsoft.com, merge tester + physical schemas)
  python collect_asim_fields.py

  # Refresh cache and run
  python collect_asim_fields.py --refresh-cache

  # Custom output directory
  python collect_asim_fields.py --output ./reports

  # Skip tester and physical schema merging
  python collect_asim_fields.py --skip-tester --skip-physical

  # Use local documentation files
  python collect_asim_fields.py --docs-path ./local-docs

  # Specify custom paths for tester and table schemas
  python collect_asim_fields.py --tester-path /path/to/ASimTester.csv --table-schemas-path /path/to/table_schemas.csv
"""
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=script_dir,
        help='Output directory for CSV and report (default: script directory)'
    )
    
    parser.add_argument(
        '--docs-path',
        type=str,
        default=LEARN_BASE_URL,
        help=f'Base URL or local path for documentation (default: {LEARN_BASE_URL})'
    )
    
    parser.add_argument(
        '--tester-path',
        type=Path,
        default=repo_root / 'ASIM' / 'dev' / 'ASimTester' / 'ASimTester.csv',
        help='Path to ASimTester.csv (default: ASIM/dev/ASimTester/ASimTester.csv in repo root)'
    )
    
    parser.add_argument(
        '--table-schemas-path',
        type=Path,
        default=script_dir / 'table_schemas.csv',
        help='Path to table_schemas.csv (default: table_schemas.csv in script directory)'
    )
    
    parser.add_argument(
        '--skip-tester',
        action='store_true',
        help='Skip merging ASIM tester data'
    )
    
    parser.add_argument(
        '--skip-physical',
        action='store_true',
        help='Skip merging physical table schema data'
    )
    
    parser.add_argument(
        '--refresh-cache',
        action='store_true',
        help='Clear cache and fetch fresh content'
    )
    
    parser.add_argument(
        '--skip-cache',
        action='store_true',
        help='Skip cache for this run only'
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
        type=Path,
        default=DEFAULT_CACHE_DIR,
        help=f'Directory for cache files (default: {DEFAULT_CACHE_DIR})'
    )
    
    parser.add_argument(
        '--no-report',
        action='store_true',
        help='Skip generating the summary report markdown file'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress verbose output'
    )
    
    args = parser.parse_args()
    
    # Configure cache
    global _cache_enabled, _cache_dir, _cache_ttl
    _cache_enabled = not args.skip_cache
    _cache_dir = args.cache_dir
    _cache_ttl = args.cache_ttl
    
    verbose = not args.quiet
    
    # Handle cache refresh
    if args.refresh_cache:
        if verbose:
            print("Clearing cache...")
        deleted = clear_cache()
        if verbose:
            print(f"  Deleted {deleted} cached files")
    
    if verbose:
        print("=" * 60)
        print("ASIM Field Information Collector")
        print("=" * 60)
        print(f"\nDocumentation source: {args.docs_path}")
        print(f"Output directory: {args.output}")
        print(f"Cache enabled: {_cache_enabled}")
        if _cache_enabled:
            print(f"Cache TTL: {_cache_ttl} seconds ({_cache_ttl // 3600} hours)")
            print(f"Cache directory: {_cache_dir}")
        if not args.skip_tester:
            print(f"ASIM Tester: {args.tester_path}")
        if not args.skip_physical:
            print(f"Table schemas: {args.table_schemas_path}")
    
    # ── Phase 1: Collect documentation fields ──
    try:
        all_fields = collect_all_fields(args.docs_path, verbose=verbose)
    except Exception as e:
        print(f"Error collecting fields: {e}")
        return 1
    
    if not all_fields:
        print("No fields collected. Check your documentation source.")
        return 1
    
    if verbose:
        print(f"\n{'=' * 60}")
        print(f"Total schema fields collected: {len(all_fields)}")
    
    # Collect entity fields
    try:
        entity_fields = collect_all_entity_fields(args.docs_path, verbose=verbose)
    except Exception as e:
        print(f"Error collecting entity fields: {e}")
        entity_fields = []
    
    if entity_fields and verbose:
        print(f"\n{'=' * 60}")
        print(f"Total entity fields collected: {len(entity_fields)}")
    
    # Fetch logical types
    try:
        logical_types = fetch_logical_types(args.docs_path, verbose=verbose)
    except Exception as e:
        print(f"Error fetching logical types: {e}")
        logical_types = {}
    
    if logical_types and verbose:
        print(f"  Logical types with values: {sum(1 for lt in logical_types.values() if lt.allowed_values)}")
    
    # Post-process: Expand logical type references
    if logical_types:
        if verbose:
            print(f"\n{'=' * 60}")
            print("Expanding logical type references...")
        
        schema_expanded = expand_logical_type_references(all_fields, logical_types, verbose=False)
        if verbose:
            print(f"  Schema fields expanded: {schema_expanded}")
        
        if entity_fields:
            entity_expanded = expand_entity_logical_type_references(entity_fields, logical_types, verbose=False)
            if verbose:
                print(f"  Entity fields expanded: {entity_expanded}")
    
    # ── Phase 2: Merge ASIM Tester data ──
    if not args.skip_tester:
        if verbose:
            print(f"\n{'=' * 60}")
            print("Merging ASIM Tester data...")
        
        tester_data = load_asim_tester_data(args.tester_path, verbose=verbose)
        
        if tester_data:
            merge_tester_data(all_fields, tester_data, verbose=verbose)
            
            # Find fields only in tester
            tester_only_fields = find_tester_only_fields(all_fields, tester_data, verbose=verbose)
            if tester_only_fields:
                all_fields.extend(tester_only_fields)
    
    # ── Phase 2b: Entity extension fields ──
    if entity_fields:
        if verbose:
            print(f"\n{'=' * 60}")
            print("Applying entity extension fields...")
        
        reclassified, new_entity_ext_fields = apply_entity_extensions(
            all_fields, entity_fields, verbose=verbose
        )
        if new_entity_ext_fields:
            all_fields.extend(new_entity_ext_fields)
    
    # ── Phase 3: Merge physical table schemas ──
    if not args.skip_physical:
        if verbose:
            print(f"\n{'=' * 60}")
            print("Merging physical table schemas...")
        
        physical_data = load_physical_table_schemas(args.table_schemas_path, verbose=verbose)
        
        if physical_data:
            merge_physical_schemas(all_fields, physical_data, verbose=verbose)
            
            # Find fields only in physical tables
            physical_only_fields = find_physical_only_fields(all_fields, physical_data, verbose=verbose)
            if physical_only_fields:
                all_fields.extend(physical_only_fields)
    
    # ── Phase 4: Write outputs ──
    # Backfill schema_type for fields added by downstream stages (tester, entity
    # extensions, physical tables) that didn't go through the schema loop.
    schema_type_lookup: Dict[str, str] = {}
    for f in all_fields:
        if f.schema_type and f.schema not in schema_type_lookup:
            schema_type_lookup[f.schema] = f.schema_type
    for f in all_fields:
        if not f.schema_type and f.schema in schema_type_lookup:
            f.schema_type = schema_type_lookup[f.schema]

    args.output.mkdir(parents=True, exist_ok=True)
    
    csv_path = args.output / 'asim_fields.csv'
    write_fields_csv(all_fields, csv_path)
    
    if entity_fields:
        entity_csv_path = args.output / 'asim_entity_fields.csv'
        write_entity_fields_csv(entity_fields, entity_csv_path)
    
    if logical_types:
        logical_types_csv_path = args.output / 'asim_logical_types.csv'
        write_logical_types_csv(logical_types, logical_types_csv_path)
    
    try:
        vendors, products = fetch_vendors_products(args.docs_path, verbose=verbose)
    except Exception as e:
        print(f"Error fetching vendors/products: {e}")
        vendors, products = set(), set()
    
    if vendors or products:
        display_url, _ = get_doc_urls('normalization-common-fields.md', args.docs_path)
        vendors_products_csv_path = args.output / 'asim_vendors_products.csv'
        write_vendors_products_csv(vendors, products, vendors_products_csv_path,
                                   doc_url=display_url + "#vendors-and-products")
    
    # Extraction failures
    failures = collect_extraction_failures(all_fields, entity_fields)
    if failures:
        failures_csv_path = args.output / 'asim_extraction_failures.csv'
        write_extraction_failures_csv(failures, failures_csv_path)
        if verbose:
            alias_failures = sum(1 for f in failures if f.failure_type == 'alias')
            enum_failures = sum(1 for f in failures if f.failure_type == 'enumerated')
            type_mismatch_failures = sum(1 for f in failures if f.failure_type == 'type_mismatch')
            print(f"  ({alias_failures} alias, {enum_failures} enumerated, {type_mismatch_failures} type mismatch failures)")
    
    if not args.no_report:
        report_content = generate_summary_report(all_fields)
        report_path = args.output / 'asim_fields_summary.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        if verbose:
            print(f"Wrote summary report to {report_path}")
    
    if verbose:
        print("\nDone!")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
