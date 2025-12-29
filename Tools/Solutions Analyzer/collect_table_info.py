#!/usr/bin/env python3
"""
Collect Table Information from Microsoft Documentation

This script collects information about Azure Monitor and Microsoft Sentinel tables
from multiple Microsoft documentation sources and outputs a consolidated CSV.

Sources:
1. Azure Monitor Reference Tables (by category)
   https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables-category

2. Microsoft Defender XDR Advanced Hunting Schema
   https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-schema-tables

3. Azure Monitor Tables Feature Support
   https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tables-feature-support

4. Azure Monitor Logs Ingestion API Supported Tables
   https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview#supported-tables

Additional potential sources (for future enhancement):
- Azure Resource Graph tables
- Microsoft Sentinel data connectors documentation
- Log Analytics workspace table schemas via API
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
from dataclasses import dataclass, field
from html.parser import HTMLParser

# Try to import requests for web URL support
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Try to import BeautifulSoup for better HTML parsing
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

# Default documentation URLs (using learn.microsoft.com directly)
AZURE_MONITOR_TABLES_CATEGORY = 'https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables-category'
AZURE_MONITOR_TABLES_CATEGORY_RAW = 'https://raw.githubusercontent.com/MicrosoftDocs/azure-monitor-docs/main/articles/azure-monitor/reference/tables-category.md'

DEFENDER_XDR_SCHEMA = 'https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-schema-tables'
DEFENDER_XDR_SCHEMA_RAW = 'https://raw.githubusercontent.com/MicrosoftDocs/defender-docs/main/defender-xdr/advanced-hunting-schema-tables.md'

TABLES_FEATURE_SUPPORT = 'https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tables-feature-support'
TABLES_FEATURE_SUPPORT_RAW = 'https://raw.githubusercontent.com/MicrosoftDocs/azure-monitor-docs/main/articles/azure-monitor/logs/tables-feature-support.md'

INGESTION_API_OVERVIEW = 'https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview'
INGESTION_API_OVERVIEW_RAW = 'https://raw.githubusercontent.com/MicrosoftDocs/azure-monitor-docs/main/articles/azure-monitor/logs/logs-ingestion-api-overview.md'

# Azure Monitor table reference base URL
AZURE_MONITOR_TABLE_REF_BASE = 'https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/'
AZURE_MONITOR_TABLE_REF_RAW_BASE = 'https://raw.githubusercontent.com/MicrosoftDocs/azure-monitor-docs/main/articles/azure-monitor/reference/tables/'

# Cache configuration
DEFAULT_CACHE_DIR = Path('.cache')
DEFAULT_CACHE_TTL = 604800  # 1 week in seconds

# Global cache settings
_cache_enabled = True
_cache_dir = DEFAULT_CACHE_DIR
_cache_ttl = DEFAULT_CACHE_TTL


@dataclass
class TableInfo:
    """Information about a Log Analytics / Sentinel table."""
    table_name: str
    description: str = ""
    category: str = ""
    solutions: str = ""
    resource_types: str = ""
    
    # Source tracking
    source_azure_monitor: bool = False
    source_defender_xdr: bool = False
    source_feature_support: bool = False
    source_ingestion_api: bool = False
    
    # Links
    azure_monitor_doc_link: str = ""
    defender_xdr_doc_link: str = ""
    
    # Feature support attributes
    basic_logs_eligible: str = ""
    auxiliary_table_eligible: str = ""
    supports_transformations: str = ""
    search_job_support: str = ""
    
    # Ingestion API support
    ingestion_api_supported: bool = False
    
    # Table attributes from Azure Monitor reference
    table_type: str = ""  # Microsoft, Custom, etc.
    retention_default: str = ""
    retention_max: str = ""
    plan: str = ""  # Analytics, Basic, etc.


def get_cache_path(url: str) -> Path:
    """Get the cache file path for a URL."""
    url_hash = hashlib.md5(url.encode()).hexdigest()
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


def fetch_content(url: str, verbose: bool = False) -> str:
    """Fetch content from a URL with caching."""
    if not HAS_REQUESTS:
        raise ImportError("The 'requests' library is required. Install it with: pip install requests")
    
    cache_path = get_cache_path(url)
    cached_content = read_from_cache(cache_path)
    if cached_content is not None:
        if verbose:
            print(f"  [cache hit] {url.split('/')[-1]}")
        return cached_content
    
    if verbose:
        print(f"  [fetching] {url.split('/')[-1]}")
    
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    content = response.text
    
    # Remove BOM if present
    if content.startswith('\ufeff'):
        content = content[1:]
    
    write_to_cache(cache_path, content, url)
    return content


def parse_markdown_table(content: str, table_start_pattern: str = None) -> List[List[str]]:
    """Parse a markdown table from content."""
    lines = content.split('\n')
    tables = []
    current_table = []
    in_table = False
    found_start = table_start_pattern is None
    
    for line in lines:
        # Check for table start pattern if specified
        if table_start_pattern and not found_start:
            if table_start_pattern.lower() in line.lower():
                found_start = True
            continue
        
        # Detect table rows
        if re.match(r'^\s*\|.*\|', line):
            # Skip separator rows
            if re.match(r'^\s*\|[-:\s|]+\|', line):
                in_table = True
                continue
            
            if in_table or '|' in line:
                # Parse table row
                parts = [p.strip() for p in line.split('|')]
                # Remove empty first and last elements from split
                if parts and not parts[0]:
                    parts = parts[1:]
                if parts and not parts[-1]:
                    parts = parts[:-1]
                if parts:
                    current_table.append(parts)
                    in_table = True
        elif in_table and current_table:
            # End of table
            tables.append(current_table)
            current_table = []
            in_table = False
            if table_start_pattern:
                break  # Only get first table after pattern
    
    if current_table:
        tables.append(current_table)
    
    return tables[0] if tables else []


def extract_table_links_from_markdown(content: str) -> Dict[str, str]:
    """Extract table names and their documentation links from markdown content."""
    table_links = {}
    
    # Pattern: [TableName](link) or [TableName](/path/to/table)
    pattern = r'\[([A-Za-z0-9_]+)\]\(([^)]+)\)'
    
    for match in re.finditer(pattern, content):
        table_name = match.group(1)
        link = match.group(2)
        
        # Only include if it looks like a table reference
        if table_name and table_name[0].isupper():
            # Normalize link
            if link.startswith('/'):
                link = 'https://learn.microsoft.com' + link
            elif not link.startswith('http'):
                link = AZURE_MONITOR_TABLE_REF_BASE + link
            
            table_links[table_name] = link
    
    return table_links


def parse_azure_monitor_tables_category(content: str, verbose: bool = False) -> Dict[str, TableInfo]:
    """Parse the Azure Monitor tables-category page (from raw markdown)."""
    tables = {}
    
    current_category = ""
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # Detect category headers (## or ### in markdown)
        header_match = re.match(r'^#{2,3}\s+(.+)', line)
        if header_match:
            potential_category = header_match.group(1).strip()
            # Skip non-category headers
            if potential_category.lower() not in ['feedback', 'additional resources', 'additional links', 
                                                    'table of contents', 'next steps', 'related content',
                                                    'azure monitor log analytics log tables organized by category']:
                current_category = potential_category
            continue
        
        # Find table links in markdown format
        # Format: - [TableName](./tables/tablename.md) or [TableName](tables/tablename.md)
        table_pattern = r'\[([A-Za-z0-9_]+)\]\(\./tables/([^)]+)\.md\)'
        for match in re.finditer(table_pattern, line):
            table_name = match.group(1)
            table_file = match.group(2)
            
            if table_name not in tables:
                tables[table_name] = TableInfo(
                    table_name=table_name,
                    category=current_category,
                    source_azure_monitor=True,
                    azure_monitor_doc_link=f"{AZURE_MONITOR_TABLE_REF_BASE}{table_file}"
                )
            elif current_category and not tables[table_name].category:
                tables[table_name].category = current_category
        
        # Also try format without ./
        table_pattern2 = r'\[([A-Za-z0-9_]+)\]\(tables/([^)]+)\.md\)'
        for match in re.finditer(table_pattern2, line):
            table_name = match.group(1)
            table_file = match.group(2)
            
            if table_name not in tables:
                tables[table_name] = TableInfo(
                    table_name=table_name,
                    category=current_category,
                    source_azure_monitor=True,
                    azure_monitor_doc_link=f"{AZURE_MONITOR_TABLE_REF_BASE}{table_file}"
                )
    
    if verbose:
        print(f"  Found {len(tables)} tables from Azure Monitor reference")
    
    return tables


def parse_defender_xdr_schema(content: str, verbose: bool = False) -> Dict[str, TableInfo]:
    """Parse the Defender XDR advanced hunting schema page (from raw markdown)."""
    tables = {}
    
    # Find table entries in markdown tables
    # Format: | [TableName](tablename.md) | Description |
    # or: | TableName | Description |
    lines = content.split('\n')
    in_table = False
    
    for line in lines:
        # Detect table header separator
        if re.match(r'^\s*\|[-:\s|]+\|', line):
            in_table = True
            continue
        
        if not in_table or '|' not in line:
            continue
        
        # Try to extract from markdown table row with link
        # Format: | **[TableName](link.md)** | Description |  (bold formatting)
        # or: | [TableName](link.md) | Description |  (no bold)
        # May include (Preview) suffix after the link
        match = re.search(r'\|\s*\*?\*?\[([A-Za-z0-9_]+)\]\(([^)]+)\)\*?\*?\s*(?:\(Preview\))?\s*\|\s*([^|]+)\|', line)
        if match:
            table_name = match.group(1)
            link = match.group(2)
            description = match.group(3).strip()
            
            # Normalize link
            if not link.startswith('http'):
                link = f"https://learn.microsoft.com/en-us/defender-xdr/{link.replace('.md', '')}"
            
            tables[table_name] = TableInfo(
                table_name=table_name,
                description=description,
                source_defender_xdr=True,
                defender_xdr_doc_link=link
            )
            continue
        
        # Try plain table format: | TableName | Description |
        parts = [p.strip() for p in line.split('|')]
        parts = [p for p in parts if p]  # Remove empty parts
        
        if len(parts) >= 2:
            table_name = parts[0]
            description = parts[1] if len(parts) > 1 else ""
            
            # Skip headers
            if table_name.lower() in ['table name', 'table', 'name', '']:
                continue
            
            # Clean up table name (remove any markdown formatting)
            table_name = re.sub(r'[\[\]`*]', '', table_name).strip()
            
            if table_name and table_name[0].isupper():
                tables[table_name] = TableInfo(
                    table_name=table_name,
                    description=description,
                    source_defender_xdr=True,
                    defender_xdr_doc_link=f"https://learn.microsoft.com/en-us/defender-xdr/{table_name.lower()}"
                )
    
    if verbose:
        print(f"  Found {len(tables)} tables from Defender XDR schema")
    
    return tables


def parse_tables_feature_support(content: str, verbose: bool = False) -> Dict[str, Dict]:
    """Parse the tables-feature-support page."""
    feature_info = {}
    
    # Find the main feature support table
    # Headers typically: Table | Basic logs | Auxiliary | Transformations | Search Jobs
    
    lines = content.split('\n')
    in_table = False
    headers = []
    
    for line in lines:
        if re.match(r'^\s*\|[-:\s|]+\|', line):
            in_table = True
            continue
        
        if in_table and '|' in line:
            parts = [p.strip() for p in line.split('|')]
            parts = [p for p in parts if p]  # Remove empty parts
            
            if not parts:
                continue
            
            # First row after separator might be headers
            if not headers and any(h.lower() in ['table', 'name'] for h in parts):
                headers = [h.lower() for h in parts]
                continue
            
            # Extract table name from first column
            table_name_match = re.search(r'\[([A-Za-z0-9_]+)\]', parts[0])
            if table_name_match:
                table_name = table_name_match.group(1)
            else:
                table_name = parts[0].strip()
            
            if not table_name or table_name.lower() == 'table':
                continue
            
            # Build feature dict
            features = {
                'basic_logs': '',
                'auxiliary': '',
                'transformations': '',
                'search_jobs': ''
            }
            
            # Map columns to features based on position or headers
            for i, part in enumerate(parts[1:], 1):
                # Clean checkmarks and other markers
                value = part.strip()
                if '✓' in value or '✔' in value or 'Yes' in value:
                    value = 'Yes'
                elif '✗' in value or '✖' in value or 'No' in value:
                    value = 'No'
                
                if i == 1:
                    features['basic_logs'] = value
                elif i == 2:
                    features['auxiliary'] = value
                elif i == 3:
                    features['transformations'] = value
                elif i == 4:
                    features['search_jobs'] = value
            
            feature_info[table_name] = features
        elif in_table and not '|' in line:
            in_table = False
    
    if verbose:
        print(f"  Found feature support info for {len(feature_info)} tables")
    
    return feature_info


def parse_ingestion_api_tables(content: str, verbose: bool = False) -> Set[str]:
    """Parse the Logs Ingestion API supported tables section."""
    supported_tables = set()
    
    # Look for the "Supported tables" section
    in_section = False
    
    lines = content.split('\n')
    for line in lines:
        # Find section header
        if 'supported tables' in line.lower() and '#' in line:
            in_section = True
            continue
        
        # End of section (next major header)
        if in_section and re.match(r'^##\s', line):
            break
        
        if in_section:
            # Find table names in markdown links with <br> separators
            # Pattern: * [TableName](/azure/azure-monitor/reference/tables/tablename)<br>
            # or just: * TableName<br>
            link_pattern = r'\*\s*\[([A-Za-z0-9_]+)\]\([^)]+\)'
            for match in re.finditer(link_pattern, line):
                table_name = match.group(1)
                if table_name and table_name[0].isupper():
                    supported_tables.add(table_name)
            
            # Plain table names without links
            plain_pattern = r'\*\s*([A-Za-z][A-Za-z0-9_]+)(?:<br>|$)'
            for match in re.finditer(plain_pattern, line):
                table_name = match.group(1).strip()
                if table_name and table_name[0].isupper() and not table_name.startswith('['):
                    supported_tables.add(table_name)
            
            # Also check for list items
            list_match = re.match(r'^\s*[-*]\s*`?([A-Za-z0-9_]+)`?', line)
            if list_match:
                table_name = list_match.group(1)
                if table_name and table_name[0].isupper():
                    supported_tables.add(table_name)
    
    if verbose:
        print(f"  Found {len(supported_tables)} tables supported by Ingestion API")
    
    return supported_tables


def fetch_table_details(table_name: str, verbose: bool = False) -> Dict:
    """Fetch detailed information about a table from its reference page."""
    details = {
        'description': '',
        'table_type': '',
        'retention_default': '',
        'retention_max': '',
        'plan': '',
        'solutions': '',
        'resource_types': '',
        'categories': '',
        'basic_log': '',
        'ingestion_transformation': ''
    }
    
    # Construct URL for table reference
    table_file = table_name.lower()
    url = f"{AZURE_MONITOR_TABLE_REF_RAW_BASE}{table_file}.md"
    
    try:
        content = fetch_content(url, verbose=False)
    except Exception as e:
        if verbose:
            print(f"    Could not fetch details for {table_name}: {e}")
        return details
    
    # Parse YAML front matter if present
    yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if yaml_match:
        yaml_content = yaml_match.group(1)
        # Extract description from YAML
        desc_match = re.search(r'description:\s*(.+)', yaml_content)
        if desc_match:
            details['description'] = desc_match.group(1).strip().strip('"\'')
    
    # Parse table attributes section
    # Format: |**Attribute**|**Value**| or |Attribute|Value|
    # Extract all attribute rows
    attr_patterns = [
        (r'\|\s*\*?\*?Resource types\*?\*?\s*\|\s*([^|]+)\|', 'resource_types'),
        (r'\|\s*\*?\*?Categories\*?\*?\s*\|\s*([^|]+)\|', 'categories'),
        (r'\|\s*\*?\*?Solutions\*?\*?\s*\|\s*([^|]+)\|', 'solutions'),
        (r'\|\s*\*?\*?Basic log\*?\*?\s*\|\s*([^|]+)\|', 'basic_log'),
        (r'\|\s*\*?\*?Ingestion-time transformation\*?\*?\s*\|\s*([^|]+)\|', 'ingestion_transformation'),
        (r'\|\s*\*?\*?Table type\*?\*?\s*\|\s*([^|]+)\|', 'table_type'),
    ]
    
    for pattern, key in attr_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            # Clean up markdown formatting
            value = re.sub(r'\*\*([^*]+)\*\*', r'\1', value)  # Remove bold
            value = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', value)  # Remove links
            # Convert <br> tags to commas for multi-value fields
            value = re.sub(r'<br\s*/?>', ', ', value)
            value = re.sub(r'\s*,\s*', ', ', value)  # Normalize comma spacing
            value = re.sub(r',\s*,', ',', value)  # Remove empty items (consecutive commas)
            value = re.sub(r'\s*,\s*', ', ', value)  # Re-normalize comma spacing
            details[key] = value.strip().strip(',')
    
    # If description not found in YAML, try to extract from content
    # The first paragraph after the title heading is usually the description
    if not details['description']:
        # Look for content between title and ## Table attributes
        desc_match = re.search(r'^#\s+[A-Za-z0-9_]+\s*\n+(.+?)(?=\n##|\n\|)', content, re.MULTILINE | re.DOTALL)
        if desc_match:
            desc = desc_match.group(1).strip()
            # Clean up markdown
            desc = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', desc)  # Remove links
            if len(desc) > 10:
                details['description'] = desc
    
    return details


def merge_table_info(tables: Dict[str, TableInfo], 
                      defender_tables: Dict[str, TableInfo],
                      feature_info: Dict[str, Dict],
                      ingestion_tables: Set[str]) -> Dict[str, TableInfo]:
    """Merge table information from all sources."""
    
    # Start with Azure Monitor tables
    merged = dict(tables)
    
    # Merge Defender XDR tables
    for table_name, info in defender_tables.items():
        if table_name in merged:
            # Update existing entry
            if info.description and not merged[table_name].description:
                merged[table_name].description = info.description
            elif info.description:
                # Defender description might be more concise, use it
                merged[table_name].description = info.description
            merged[table_name].source_defender_xdr = True
            merged[table_name].defender_xdr_doc_link = info.defender_xdr_doc_link
        else:
            # Add new entry
            merged[table_name] = info
    
    # Merge feature support info
    for table_name, features in feature_info.items():
        if table_name in merged:
            merged[table_name].source_feature_support = True
            merged[table_name].basic_logs_eligible = features.get('basic_logs', '')
            merged[table_name].auxiliary_table_eligible = features.get('auxiliary', '')
            merged[table_name].supports_transformations = features.get('transformations', '')
            merged[table_name].search_job_support = features.get('search_jobs', '')
        else:
            # Add new entry with just feature info
            merged[table_name] = TableInfo(
                table_name=table_name,
                source_feature_support=True,
                basic_logs_eligible=features.get('basic_logs', ''),
                auxiliary_table_eligible=features.get('auxiliary', ''),
                supports_transformations=features.get('transformations', ''),
                search_job_support=features.get('search_jobs', '')
            )
    
    # Mark ingestion API supported tables
    for table_name in ingestion_tables:
        if table_name in merged:
            merged[table_name].source_ingestion_api = True
            merged[table_name].ingestion_api_supported = True
        else:
            merged[table_name] = TableInfo(
                table_name=table_name,
                source_ingestion_api=True,
                ingestion_api_supported=True
            )
    
    return merged


def write_tables_csv(tables: Dict[str, TableInfo], output_path: Path) -> None:
    """Write table information to CSV."""
    fieldnames = [
        'table_name',
        'description',
        'category',
        'solutions',
        'resource_types',
        'table_type',
        'source_azure_monitor',
        'source_defender_xdr',
        'source_feature_support',
        'source_ingestion_api',
        'azure_monitor_doc_link',
        'defender_xdr_doc_link',
        'basic_logs_eligible',
        'auxiliary_table_eligible',
        'supports_transformations',
        'search_job_support',
        'ingestion_api_supported',
        'retention_default',
        'retention_max',
        'plan'
    ]
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        
        for table_name in sorted(tables.keys()):
            info = tables[table_name]
            writer.writerow({
                'table_name': info.table_name,
                'description': info.description,
                'category': info.category,
                'solutions': info.solutions,
                'resource_types': info.resource_types,
                'table_type': info.table_type,
                'source_azure_monitor': 'Yes' if info.source_azure_monitor else 'No',
                'source_defender_xdr': 'Yes' if info.source_defender_xdr else 'No',
                'source_feature_support': 'Yes' if info.source_feature_support else 'No',
                'source_ingestion_api': 'Yes' if info.source_ingestion_api else 'No',
                'azure_monitor_doc_link': info.azure_monitor_doc_link,
                'defender_xdr_doc_link': info.defender_xdr_doc_link,
                'basic_logs_eligible': info.basic_logs_eligible,
                'auxiliary_table_eligible': info.auxiliary_table_eligible,
                'supports_transformations': info.supports_transformations,
                'search_job_support': info.search_job_support,
                'ingestion_api_supported': 'Yes' if info.ingestion_api_supported else 'No',
                'retention_default': info.retention_default,
                'retention_max': info.retention_max,
                'plan': info.plan
            })
    
    print(f"Wrote {len(tables)} tables to {output_path}")


def generate_report_md(tables: Dict[str, TableInfo], output_path: Path) -> None:
    """Generate a markdown report summarizing the table information."""
    
    # Calculate statistics
    total_tables = len(tables)
    azure_monitor_count = sum(1 for t in tables.values() if t.source_azure_monitor)
    defender_xdr_count = sum(1 for t in tables.values() if t.source_defender_xdr)
    feature_support_count = sum(1 for t in tables.values() if t.source_feature_support)
    ingestion_api_count = sum(1 for t in tables.values() if t.ingestion_api_supported)
    
    # Count by category
    categories = {}
    for t in tables.values():
        cat = t.category or 'Uncategorized'
        categories[cat] = categories.get(cat, 0) + 1
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Azure Monitor and Sentinel Tables Reference\n\n")
        f.write(f"*Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        f.write("## Table of Contents\n\n")
        f.write("- [Summary Statistics](#summary-statistics)\n")
        f.write("- [Tables by Category](#tables-by-category)\n")
        f.write("- [Data Sources](#data-sources)\n")
        f.write("\n---\n\n")
        
        f.write("## Summary Statistics\n\n")
        f.write("| Metric | Count |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Total Tables | {total_tables} |\n")
        f.write(f"| In Azure Monitor Reference | {azure_monitor_count} |\n")
        f.write(f"| In Defender XDR Schema | {defender_xdr_count} |\n")
        f.write(f"| With Feature Support Info | {feature_support_count} |\n")
        f.write(f"| Supported by Ingestion API | {ingestion_api_count} |\n")
        f.write("\n")
        
        f.write("## Tables by Category\n\n")
        f.write("| Category | Table Count |\n")
        f.write("|----------|-------------|\n")
        for cat in sorted(categories.keys()):
            f.write(f"| {cat} | {categories[cat]} |\n")
        f.write("\n")
        
        f.write("## Data Sources\n\n")
        f.write("This reference combines information from the following Microsoft documentation:\n\n")
        f.write(f"1. **Azure Monitor Reference Tables** - [{AZURE_MONITOR_TABLES_CATEGORY}]({AZURE_MONITOR_TABLES_CATEGORY})\n")
        f.write(f"2. **Defender XDR Advanced Hunting Schema** - [{DEFENDER_XDR_SCHEMA}]({DEFENDER_XDR_SCHEMA})\n")
        f.write(f"3. **Tables Feature Support** - [{TABLES_FEATURE_SUPPORT}]({TABLES_FEATURE_SUPPORT})\n")
        f.write(f"4. **Logs Ingestion API Overview** - [{INGESTION_API_OVERVIEW}]({INGESTION_API_OVERVIEW})\n")
        f.write("\n")
        
        f.write("### Additional Sources for Future Enhancement\n\n")
        f.write("- Azure Resource Graph tables\n")
        f.write("- Microsoft Sentinel data connectors documentation\n")
        f.write("- Log Analytics workspace table schemas via API\n")
        f.write("- Azure Monitor Metrics reference\n")
        f.write("- Microsoft 365 Defender tables\n")
        f.write("- Microsoft Purview audit logs tables\n")
    
    print(f"Wrote report to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Collect table information from Microsoft documentation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with defaults
  python collect_table_info.py

  # Refresh cache and run
  python collect_table_info.py --refresh-cache

  # Fetch detailed info for each table (slower)
  python collect_table_info.py --fetch-details

  # Custom output directory
  python collect_table_info.py --output ./reports
"""
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path(__file__).parent,
        help='Output directory for CSV and report (default: script directory)'
    )
    
    parser.add_argument(
        '--fetch-details',
        action='store_true',
        help='Fetch detailed info for each table from reference pages (slower)'
    )
    
    parser.add_argument(
        '--max-details',
        type=int,
        default=0,
        metavar='N',
        help='Max number of table detail pages to fetch (0=all, useful for testing)'
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
            print("Refreshing cache...")
        count = clear_cache()
        if verbose:
            print(f"Cleared {count} cached files")
    
    if verbose:
        print("Collecting Table Information from Microsoft Documentation")
        print("=" * 60)
        if _cache_enabled:
            print(f"Cache: enabled (TTL: {_cache_ttl}s, dir: {_cache_dir})")
        else:
            print("Cache: disabled")
        print()
    
    # 1. Fetch Azure Monitor tables-category
    if verbose:
        print("1. Fetching Azure Monitor tables-category...")
    try:
        content = fetch_content(AZURE_MONITOR_TABLES_CATEGORY_RAW, verbose)
        azure_monitor_tables = parse_azure_monitor_tables_category(content, verbose)
    except Exception as e:
        print(f"   Error: {e}")
        azure_monitor_tables = {}
    
    # 2. Fetch Defender XDR schema
    if verbose:
        print("\n2. Fetching Defender XDR advanced hunting schema...")
    try:
        content = fetch_content(DEFENDER_XDR_SCHEMA_RAW, verbose)
        defender_tables = parse_defender_xdr_schema(content, verbose)
    except Exception as e:
        print(f"   Error: {e}")
        defender_tables = {}
    
    # 3. Fetch feature support info
    if verbose:
        print("\n3. Fetching tables feature support...")
    try:
        content = fetch_content(TABLES_FEATURE_SUPPORT_RAW, verbose)
        feature_info = parse_tables_feature_support(content, verbose)
    except Exception as e:
        print(f"   Error: {e}")
        feature_info = {}
    
    # 4. Fetch ingestion API supported tables
    if verbose:
        print("\n4. Fetching Logs Ingestion API supported tables...")
    try:
        content = fetch_content(INGESTION_API_OVERVIEW_RAW, verbose)
        ingestion_tables = parse_ingestion_api_tables(content, verbose)
    except Exception as e:
        print(f"   Error: {e}")
        ingestion_tables = set()
    
    # Merge all information
    if verbose:
        print("\n5. Merging table information...")
    tables = merge_table_info(azure_monitor_tables, defender_tables, feature_info, ingestion_tables)
    
    if verbose:
        print(f"   Total unique tables: {len(tables)}")
    
    # Optionally fetch detailed info for each table
    if args.fetch_details:
        # Filter to only Azure Monitor tables
        azure_tables = [(name, info) for name, info in tables.items() if info.source_azure_monitor]
        total = len(azure_tables)
        
        # Apply limit if specified
        if args.max_details > 0:
            azure_tables = azure_tables[:args.max_details]
            if verbose:
                print(f"\n6. Fetching detailed info for {len(azure_tables)} of {total} Azure Monitor tables...")
        else:
            if verbose:
                print(f"\n6. Fetching detailed info for {total} Azure Monitor tables (this may take a while)...")
        
        fetched_count = 0
        for i, (table_name, info) in enumerate(azure_tables):
            try:
                details = fetch_table_details(table_name, verbose=False)
                fetched_count += 1
                
                if details['description'] and not info.description:
                    info.description = details['description']
                if details['table_type'] and not info.table_type:
                    info.table_type = details['table_type']
                if details['solutions'] and not info.solutions:
                    info.solutions = details['solutions']
                if details['resource_types'] and not info.resource_types:
                    info.resource_types = details['resource_types']
                # Merge categories from individual page
                if details['categories']:
                    if info.category:
                        # Merge if different
                        existing_cats = set(c.strip() for c in info.category.split(','))
                        new_cats = set(c.strip() for c in details['categories'].split(','))
                        all_cats = existing_cats | new_cats
                        info.category = ', '.join(sorted(all_cats))
                    else:
                        info.category = details['categories']
                if details['retention_default'] and not info.retention_default:
                    info.retention_default = details['retention_default']
                if details['retention_max'] and not info.retention_max:
                    info.retention_max = details['retention_max']
                # Update basic log and transformation from individual page
                if details['basic_log']:
                    basic_val = details['basic_log'].lower()
                    if 'yes' in basic_val:
                        info.basic_logs_eligible = 'Yes'
                    elif 'no' in basic_val:
                        info.basic_logs_eligible = 'No'
                if details['ingestion_transformation']:
                    trans_val = details['ingestion_transformation'].lower()
                    if 'yes' in trans_val:
                        info.supports_transformations = 'Yes'
                    elif 'no' in trans_val:
                        info.supports_transformations = 'No'
            except Exception as e:
                if verbose:
                    print(f"   Error fetching {table_name}: {e}")
            
            if verbose and (i + 1) % 50 == 0:
                print(f"   Processed {i + 1}/{len(azure_tables)} tables...")
        
        if verbose:
            print(f"   Successfully fetched details for {fetched_count} tables")
    
    # Write outputs
    if verbose:
        print("\nWriting outputs...")
    
    args.output.mkdir(parents=True, exist_ok=True)
    
    csv_path = args.output / 'tables_reference.csv'
    write_tables_csv(tables, csv_path)
    
    report_path = args.output / 'tables_reference_report.md'
    generate_report_md(tables, report_path)
    
    if verbose:
        print("\nDone!")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
