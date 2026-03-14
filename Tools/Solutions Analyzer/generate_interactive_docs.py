"""
Generate interactive HTML documentation with DataTables.js for filtering and sorting.

Reads the same CSV inputs as generate_connector_docs.py and produces a set of
HTML pages with sortable/filterable/searchable tables using DataTables.js.

This module can be invoked standalone or called from generate_connector_docs.py
via the --html flag.

Output structure:
    index.html          - Main page with tab navigation to all views
    css/style.css       - Custom styles
    js/app.js           - Tab switching and DataTables initialization
"""

import csv
import hashlib
import html as html_module
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import quote
import argparse
import sys


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATATABLES_CSS = "https://cdn.datatables.net/1.13.8/css/dataTables.bootstrap5.min.css"
DATATABLES_JS = "https://cdn.datatables.net/1.13.8/js/jquery.dataTables.min.js"
DATATABLES_BS5_JS = "https://cdn.datatables.net/1.13.8/js/dataTables.bootstrap5.min.js"
JQUERY_JS = "https://code.jquery.com/jquery-3.7.1.min.js"
BOOTSTRAP_CSS = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap5.min.css"
BOOTSTRAP_JS = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"

# Status icons (plain text for HTML)
UNPUBLISHED_ICON = "⚠️"
DEPRECATED_ICON = "🚫"
DISCOVERED_ICON = "🔍"
CLV1_ICON = "🔶"
SCHEMA_ICON = "📖"

# Content source icons
SOURCE_SOLUTION_ICON = "📦"
SOURCE_STANDALONE_ICON = "📄"
SOURCE_GITHUB_ICON = "🔗"

# Base path prefix for links from index.html to markdown docs.
# Set at generation time via generate_interactive(docs_base_path=...).
# When index.html is in the same directory as the docs, this is "".
# When index.html is at a different level (e.g. repo root), this is
# e.g. "Solutions Docs/" so that links become "Solutions Docs/solutions/foo.md".
_docs_base_path: str = ""

# File extension for entity page links from index.html.
# Defaults to ".md".  Set to ".html" when HTML entity pages are generated
# so that all links from the interactive index point to the rendered HTML
# versions instead of raw markdown files.
_link_extension: str = ".md"

# Display-friendly names for content types (matches generate_connector_docs.py)
CONTENT_TYPE_DISPLAY = {
    'analytic_rule': 'Analytic Rule',
    'hunting_query': 'Hunting Query',
    'workbook': 'Workbook',
    'playbook': 'Playbook',
    'parser': 'Parser',
    'watchlist': 'Watchlist',
    'summary_rule': 'Summary Rule',
}


def format_content_type(raw_type: str) -> str:
    """Convert raw content_type to display-friendly name."""
    return CONTENT_TYPE_DISPLAY.get(raw_type, raw_type.replace('_', ' ').title())


# ---------------------------------------------------------------------------
# Data Loading (mirrors generate_connector_docs.py loading)
# ---------------------------------------------------------------------------

def load_csv(path: Path) -> List[Dict[str, str]]:
    """Load a CSV file into a list of dicts."""
    rows = []
    if not path.exists():
        print(f"  Warning: {path} not found, skipping.")
        return rows
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def load_solutions_data(solutions_csv: Path) -> Dict[str, Dict[str, str]]:
    """Load solutions.csv into a dict keyed by solution_name."""
    result = {}
    for row in load_csv(solutions_csv):
        name = row.get('solution_name', '')
        if name:
            result[name] = row
    return result


def load_connectors_data(connectors_csv: Path) -> Dict[str, Dict[str, str]]:
    """Load connectors.csv into a dict keyed by connector_id."""
    result = {}
    for row in load_csv(connectors_csv):
        cid = row.get('connector_id', '')
        if cid:
            result[cid] = row
    return result


def load_mapping_data(mapping_csv: Path) -> Dict[str, List[Dict[str, str]]]:
    """Load solutions_connectors_tables_mapping.csv grouped by solution_name."""
    by_solution: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in load_csv(mapping_csv):
        sol = row.get('solution_name', '')
        if sol:
            by_solution[sol].append(row)
    return dict(by_solution)


def load_content_items(content_csv: Path) -> Dict[str, List[Dict[str, str]]]:
    """Load content_items.csv grouped by solution_name.
    
    Items without a solution_name are grouped under 'GitHub Only' (matching doc generator).
    """
    by_solution: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in load_csv(content_csv):
        sol = row.get('solution_name', '')
        if sol:
            by_solution[sol].append(row)
        elif row.get('content_source', '') == 'GitHub Only':
            row['solution_name'] = 'GitHub Only'
            by_solution['GitHub Only'].append(row)
    return dict(by_solution)


def load_tables_reference(tables_csv: Path) -> Dict[str, Dict[str, str]]:
    """Load tables_reference.csv keyed by table_name."""
    result = {}
    for row in load_csv(tables_csv):
        name = row.get('table_name', '')
        if name:
            result[name] = row
    return result


def load_tables_overrides(tables_overrides_csv: Path, tables_ref: Dict[str, Dict[str, str]]) -> None:
    """Load tables.csv (mapper output) and merge overrides into tables_ref in-place.
    
    Tables not in tables_ref are added; existing entries get category/is_clv1 overrides.
    """
    for row in load_csv(tables_overrides_csv):
        name = row.get('table_name', '')
        if not name:
            continue
        if name not in tables_ref:
            tables_ref[name] = row
        else:
            if row.get('category', '').lower() == 'internal':
                tables_ref[name]['category'] = 'Internal'
            if row.get('is_clv1', ''):
                tables_ref[name]['is_clv1'] = row['is_clv1']


def load_content_tables(content_tables_csv: Path) -> Dict[str, Dict[str, Set[str]]]:
    """Load content_tables_mapping.csv grouped by table_name.
    
    Returns dict: table_name -> { 'solutions': set, 'content_types': set }
    """
    result: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: {'solutions': set(), 'content_types': set()})
    for row in load_csv(content_tables_csv):
        table = row.get('table_name', '')
        if not table:
            continue
        sol = row.get('solution_name', '')
        ctype = row.get('content_type', '')
        if sol:
            result[table]['solutions'].add(sol)
        if ctype:
            result[table]['content_types'].add(ctype)
    return dict(result)


def load_table_schemas(table_schemas_csv: Path) -> Set[str]:
    """Load table_schemas.csv and return set of table names that have schemas."""
    names = set()
    for row in load_csv(table_schemas_csv):
        name = row.get('table_name', '')
        if name:
            names.add(name)
    return names


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def esc(text: str) -> str:
    """HTML-escape a string."""
    return html_module.escape(str(text)) if text else ""


def sanitize_filename(text: str) -> str:
    """Convert text to safe filename, matching generate_connector_docs.py logic."""
    result = text.lower().replace(" ", "-").replace("/", "-").replace("_", "-")
    result = result.replace(":", "-").replace("*", "-").replace("?", "-")
    result = result.replace('"', "-").replace("<", "-").replace(">", "-").replace("|", "-")
    result = result.replace("(", "-").replace(")", "-").replace("%", "-")
    while "--" in result:
        result = result.replace("--", "-")
    result = result.strip("-")
    return result


def _md_link(name: str, folder: str) -> str:
    """Return an HTML <a> link to a doc page."""
    filename = sanitize_filename(name)
    return f'<a href="{_docs_base_path}{folder}/{filename}{_link_extension}">{esc(name)}</a>'


def get_content_item_filename(content_id: str, content_name: str, solution_name: str,
                              content_file: str = '', content_type: str = '') -> str:
    """Generate a unique filename for a content item page.
    
    Mirrors generate_connector_docs.py get_content_item_filename exactly.
    """
    sanitized_solution = sanitize_filename(solution_name)
    sanitized_name = sanitize_filename(content_name)
    MAX_FILENAME_LENGTH = 150

    hash_input = f"{solution_name}|{content_name}|{content_id}|{content_file}|{content_type}".encode('utf-8')
    uniqueness_hash = hashlib.md5(hash_input).hexdigest()[:8]

    if content_id:
        sanitized_id = sanitize_filename(content_id)
        filename = f"{sanitized_solution}-{sanitized_name}-{sanitized_id}-{uniqueness_hash}"
    else:
        filename = f"{sanitized_solution}-{sanitized_name}-{uniqueness_hash}"

    if len(filename) > MAX_FILENAME_LENGTH:
        if content_id:
            sanitized_id = sanitize_filename(content_id)
            id_part = f"-{sanitized_id}-{uniqueness_hash}"
            available = MAX_FILENAME_LENGTH - len(id_part)
            if available > 20:
                filename = filename[:available] + id_part
            else:
                full_hash = hashlib.md5(filename.encode('utf-8')).hexdigest()[:16]
                filename = filename[:MAX_FILENAME_LENGTH - 17] + f"-{full_hash}"
        else:
            hash_part = f"-{uniqueness_hash}"
            available = MAX_FILENAME_LENGTH - len(hash_part)
            filename = filename[:available] + hash_part

    return filename


def _content_link(item: Dict[str, Any]) -> str:
    """Return an HTML <a> link to a content item's doc page."""
    content_name = item.get('name', '')
    # Items with resolved placeholder names have no matching doc page
    if item.get('no_link'):
        return esc(content_name)
    content_type = item.get('raw_type', '')
    solution_name = item.get('solution', '')
    content_id = item.get('content_id', '')
    content_file = item.get('content_file', '')

    # Parsers have dedicated pages in parsers/ directory
    if content_type == 'parser':
        filename = sanitize_filename(content_name)
        return f'<a href="{_docs_base_path}parsers/{filename}{_link_extension}">{esc(content_name)}</a>'

    filename = get_content_item_filename(content_id, content_name, solution_name, content_file, content_type)
    return f'<a href="{_docs_base_path}content/{filename}{_link_extension}">{esc(content_name)}</a>'


# ---------------------------------------------------------------------------
# Data assembly for tables
# ---------------------------------------------------------------------------

def build_solutions_table_data(
    by_solution: Dict[str, List[Dict[str, str]]],
    solutions_ref: Dict[str, Dict[str, str]],
    content_items: Dict[str, List[Dict[str, str]]],
) -> List[Dict[str, Any]]:
    """Build the data rows for the solutions table."""
    rows = []
    for sol_name in sorted(by_solution.keys(), key=str.casefold):
        connectors = by_solution[sol_name]
        sol_meta = solutions_ref.get(sol_name, {})
        first = connectors[0] if connectors else {}

        # Count real connectors (not discovered)
        real_connectors = set()
        for c in connectors:
            cid = c.get('connector_id', '')
            if cid and cid.strip() and str(cid).lower() != 'nan':
                if c.get('not_in_solution_json', 'false') != 'true':
                    real_connectors.add(cid)

        # Count tables
        tables = set()
        for c in connectors:
            t = c.get('Table', '')
            if t:
                tables.add(t)

        content_count = len(content_items.get(sol_name, []))
        content_in_solution = sum(1 for i in content_items.get(sol_name, []) if i.get('not_in_solution_json', 'false') != 'true')
        content_discovered = content_count - content_in_solution
        is_published = first.get('is_published', 'true') != 'false'
        is_deprecated = first.get('solution_is_deprecated', 'false') == 'true'
        support_tier = first.get('solution_support_tier', '')
        publisher = first.get('solution_support_name', sol_meta.get('support_name', ''))
        first_published = first.get('solution_first_publish_date', sol_meta.get('first_publish_date', ''))
        logo_url = first.get('solution_logo_url', '') or sol_meta.get('solution_logo_url', '')

        status = "Deprecated" if is_deprecated else ("Unpublished" if not is_published else "Active")

        rows.append({
            'name': sol_name,
            'logo_url': logo_url,
            'status': status,
            'publisher': publisher,
            'support_tier': support_tier,
            'first_published': first_published,
            'popularity': sol_meta.get('mp_popularity', ''),
            'connectors': len(real_connectors),
            'tables': len(tables),
            'content_items': content_count,
            'content_in_solution': content_in_solution,
            'content_discovered': content_discovered,
        })
    return rows


def build_connectors_table_data(
    by_solution: Dict[str, List[Dict[str, str]]],
    connectors_ref: Dict[str, Dict[str, str]],
    solutions_ref: Dict[str, Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """Build the data rows for the connectors table.
    
    Includes all connectors in solutions (including discovered ones).
    Uses connectors_ref (connectors.csv) for is_deprecated, not_in_solution_json,
    collection_method, and ingestion_api since the mapping CSV lacks these fields.
    """
    solutions_ref = solutions_ref or {}
    connectors_map: Dict[str, Dict[str, Any]] = {}

    for sol_name, connectors in by_solution.items():
        for c in connectors:
            cid = c.get('connector_id', '')
            if not cid:
                continue

            # Look up connector reference data for extended fields
            ref = connectors_ref.get(cid, {})

            is_discovered = ref.get('not_in_solution_json', 'false') == 'true'

            if cid in connectors_map:
                # Still collect tables for existing connectors
                t = c.get('Table', '')
                if t:
                    connectors_map[cid]['tables'].add(t)
                continue

            is_deprecated = ref.get('is_deprecated', 'false') == 'true'
            is_published = c.get('is_published', 'true') != 'false' and ref.get('is_published', 'true') != 'false'

            connectors_map[cid] = {
                'id': cid,
                'title': c.get('connector_title', cid),
                'solution': sol_name,
                'publisher': c.get('connector_publisher', ''),
                'collection_method': ref.get('collection_method', ''),
                'ingestion_api': ref.get('ingestion_api', ''),
                'is_deprecated': is_deprecated,
                'is_published': is_published,
                'logo_url': c.get('solution_logo_url', '') or solutions_ref.get(sol_name, {}).get('solution_logo_url', ''),
                'tables': set(),
                'support_tier': c.get('solution_support_tier', ''),
                'is_clv1': ref.get('is_clv1', '').lower() == 'true',
                'is_discovered': is_discovered,
            }
            t = c.get('Table', '')
            if t:
                connectors_map[cid]['tables'].add(t)

    rows = []
    for cid in sorted(connectors_map.keys(), key=lambda x: connectors_map[x]['title'].lower()):
        info = connectors_map[cid]
        status = "Deprecated" if info['is_deprecated'] else ("Unpublished" if not info['is_published'] else "Active")

        rows.append({
            'id': cid,
            'title': info['title'],
            'solution': info['solution'],
            'publisher': info['publisher'],
            'collection_method': info['collection_method'] or '?',
            'ingestion_api': info['ingestion_api'] or '',
            'status': status,
            'tables': len(info['tables']),
            'is_clv1': info['is_clv1'],
            'is_discovered': info['is_discovered'],
            'logo_url': info['logo_url'],
            'support_tier': info['support_tier'],
        })
    return rows


def _is_valid_table(t: str) -> bool:
    """Check if a table name is valid for the interactive index."""
    if not t or t.startswith('_') or len(t) < 3:
        return False
    if not any(c.isalnum() for c in t):
        return False
    if not t[0].isalpha() and t[0] != '_':
        return False
    return True


def build_tables_table_data(
    by_solution: Dict[str, List[Dict[str, str]]],
    tables_ref: Dict[str, Dict[str, str]],
    content_tables: Dict[str, Dict[str, Set[str]]],
    tables_with_schemas: Set[str],
) -> List[Dict[str, Any]]:
    """Build the data rows for the tables table.
    
    Merges tables from connectors, content-to-table mapping, tables_reference
    (already includes overrides), and table schemas — mirroring the doc generator.
    """
    tables_map: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        'solutions': set(), 'connectors': set(), 'content_types': set()
    })

    # From connectors
    for sol_name, connectors in by_solution.items():
        for c in connectors:
            t = c.get('Table', '')
            cid = c.get('connector_id', '')
            if not _is_valid_table(t):
                continue
            if cid:
                tables_map[t]['connectors'].add(cid)
            if sol_name:
                tables_map[t]['solutions'].add(sol_name)

    # From content_tables_mapping
    for table_name, info in content_tables.items():
        if _is_valid_table(table_name):
            tables_map[table_name]['solutions'].update(info.get('solutions', set()))
            tables_map[table_name]['content_types'].update(info.get('content_types', set()))

    # From tables_reference (already merged with overrides)
    for t in tables_ref:
        if _is_valid_table(t):
            tables_map[t]  # ensure entry exists

    # From table schemas
    for t in tables_with_schemas:
        if _is_valid_table(t):
            tables_map[t]  # ensure entry exists

    rows = []
    for tname in sorted(tables_map.keys(), key=str.casefold):
        info = tables_map[tname]
        ref = tables_ref.get(tname, {})

        # Discovery source (priority: Connector > Content > Docs > Schema > Reference)
        if info['connectors']:
            discovery = "Connector"
        elif info['content_types']:
            discovery = "Content"
        elif any(ref.get(k, '').lower() == 'yes' for k in
                 ['source_azure_monitor', 'source_defender_xdr', 'source_sentinel_tables', 'source_feature_support']):
            discovery = "Docs"
        elif tname in tables_with_schemas:
            discovery = "Schema"
        else:
            discovery = "Reference"

        is_clv1 = ref.get('is_clv1', '').lower() == 'true'
        category = ref.get('category', '')
        source_am = ref.get('source_azure_monitor', '').lower() == 'yes'
        source_xdr = ref.get('source_defender_xdr', '').lower() == 'yes'

        rows.append({
            'name': tname,
            'discovery': discovery,
            'solutions': len(info['solutions']),
            'connectors': len(info['connectors']),
            'category': category,
            'is_clv1': is_clv1,
            'has_schema': tname in tables_with_schemas,
            'azure_monitor': source_am,
            'defender_xdr': source_xdr,
        })
    return rows


def build_content_table_data(
    content_items: Dict[str, List[Dict[str, str]]],
) -> List[Dict[str, Any]]:
    """Build the data rows for the content items table."""
    rows = []
    for sol_name, items in sorted(content_items.items(), key=lambda x: x[0].lower()):
        for item in items:
            content_type = item.get('content_type', '')
            content_name = item.get('content_name', '')
            if not content_name:
                continue
            # Replace ARM template placeholder names (e.g. <PlaybookName>, PlaybookName)
            # with the folder name from the content file path
            placeholder_resolved = False
            if (content_name.startswith('<') and content_name.endswith('>')) or content_name.lower() == 'playbookname':
                content_file = item.get('content_file', '')
                if '/' in content_file:
                    content_name = content_file.split('/')[0]
                    placeholder_resolved = True
                else:
                    continue  # skip entries with no usable name
            raw_desc = item.get('content_description', '') or item.get('description', '') or ''
            # Strip wrapping single quotes (common in solution JSON descriptions)
            if raw_desc.startswith("'") and raw_desc.endswith("'") and len(raw_desc) > 1:
                raw_desc = raw_desc[1:-1]
            elif raw_desc.startswith("'"):
                raw_desc = raw_desc[1:]
            desc = raw_desc[:200] + ('...' if len(raw_desc) > 200 else '')
            content_source = item.get('content_source', '')
            is_discovered = item.get('not_in_solution_json', 'false') == 'true'
            rows.append({
                'name': content_name,
                'type': format_content_type(content_type),
                'raw_type': content_type,
                'solution': sol_name,
                'description': desc,
                'content_id': item.get('content_id', ''),
                'content_file': item.get('content_file', ''),
                'no_link': placeholder_resolved,
                'content_source': content_source,
                'is_discovered': is_discovered,
            })
    return rows


def load_parsers(parsers_csv: Path) -> List[Dict[str, str]]:
    """Load parsers.csv and apply TXT duplicate filtering.
    
    If both a .txt and .yaml version exist for the same (parser_name, location_key),
    the TXT version is removed.
    """
    rows = load_csv(parsers_csv)
    # Find YAML twins
    yaml_keys = set()
    for r in rows:
        if r.get('file_type', '') == 'yaml':
            loc_key = r.get('solution_name', '') or r.get('location', '')
            yaml_keys.add((r.get('parser_name', ''), loc_key))
    # Filter out TXT duplicates
    filtered = []
    for r in rows:
        if r.get('file_type', '') == 'txt':
            loc_key = r.get('solution_name', '') or r.get('location', '')
            if (r.get('parser_name', ''), loc_key) in yaml_keys:
                continue
        filtered.append(r)
    return filtered


def build_parsers_table_data(parsers: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Build rows for the Parsers tab."""
    rows = []
    for p in sorted(parsers, key=lambda x: x.get('parser_name', '').lower()):
        name = p.get('parser_name', '')
        if not name:
            continue
        location = p.get('location', '')
        solution = p.get('solution_name', '')
        discovered = p.get('discovered', 'false') == 'true'
        tables_raw = p.get('tables', '')
        table_list = [t.strip() for t in tables_raw.split(',') if t.strip()] if tables_raw else []
        tables_display = ', '.join(table_list[:2])
        if len(table_list) > 2:
            tables_display += ', ...'
        if not tables_display:
            tables_display = '?'

        if location == 'legacy':
            source = 'Legacy'
        else:
            source = 'Solution'

        rows.append({
            'name': name,
            'source': source,
            'solution': solution,
            'tables': tables_display,
            'is_discovered': discovered,
        })
    return rows


def build_asim_table_data(asim_parsers: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Build rows for the ASIM Parsers tab.
    
    Only includes union and source parsers (excludes empty placeholders).
    """
    rows = []
    for p in sorted(asim_parsers, key=lambda x: (x.get('schema', '').lower(), x.get('parser_type', ''), x.get('parser_name', '').lower())):
        ptype = p.get('parser_type', '')
        if ptype == 'empty':
            continue  # skip empty/placeholder parsers
        name = p.get('parser_name', '')
        if not name:
            continue
        schema = p.get('schema', '')
        product = p.get('product_name', '')
        version = p.get('parser_version', '')
        solutions = p.get('associated_solutions', '')

        if ptype == 'union':
            display_type = 'Unifying'
        else:
            display_type = 'Source'

        rows.append({
            'name': name,
            'schema': schema,
            'type': display_type,
            'product': product,
            'version': version,
            'solutions': solutions,
        })
    return rows


# ---------------------------------------------------------------------------
# HTML Generation
# ---------------------------------------------------------------------------

def generate_html_page(
    output_dir: Path,
    solutions_data: List[Dict],
    connectors_data: List[Dict],
    tables_data: List[Dict],
    content_data: List[Dict],
    parsers_data: List[Dict] = None,
    asim_data: List[Dict] = None,
) -> None:
    """Generate the main interactive HTML page with all tabs.

    The module-level ``_docs_base_path`` must be set before calling this
    function so that all entity links point to the correct docs location.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write CSS
    css_dir = output_dir / "css"
    css_dir.mkdir(exist_ok=True)
    _write_css(css_dir / "style.css")

    # Write JS
    js_dir = output_dir / "js"
    js_dir.mkdir(exist_ok=True)
    _write_js(js_dir / "app.js")

    # Write main HTML
    _write_index_html(
        output_dir / "index.html",
        solutions_data,
        connectors_data,
        tables_data,
        content_data,
        parsers_data or [],
        asim_data or [],
    )

    # Create .nojekyll to prevent GitHub Pages from running Jekyll.
    # Jekyll's Liquid engine misinterprets {{ in generated docs (e.g. Azure
    # deployment template URIs) and the build is extremely slow.
    nojekyll_path = output_dir / ".nojekyll"
    if not nojekyll_path.exists():
        nojekyll_path.touch()

    print(f"  Interactive docs generated: {output_dir / 'index.html'}")


def _write_css(path: Path) -> None:
    """Write the custom CSS file."""
    path.write_text("""\
/* Solutions Analyzer Interactive Docs */

:root {
    --ms-blue: #0078d4;
    --ms-dark: #1b1a19;
    --ms-gray: #605e5c;
    --ms-light: #f3f2f1;
    --ms-border: #e1dfdd;
}

body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: #faf9f8;
    color: var(--ms-dark);
    margin: 0;
    padding: 0;
}

.navbar {
    background: var(--ms-blue) !important;
}

.navbar-brand {
    font-weight: 600;
    font-size: 1.1rem;
}
.navbar-nav-links {
    display: flex;
    gap: 16px;
    align-items: center;
}
.nav-doc-link {
    color: rgba(255,255,255,0.85);
    text-decoration: none;
    font-size: 0.85rem;
}
.nav-doc-link:hover {
    color: #fff;
}

.container-fluid {
    max-width: 1600px;
}

/* Tabs */
.nav-tabs .nav-link {
    color: var(--ms-gray);
    font-weight: 500;
    border: none;
    padding: 0.75rem 1.25rem;
}

.nav-tabs .nav-link.active {
    color: var(--ms-blue);
    border-bottom: 3px solid var(--ms-blue);
    background: transparent;
}

.nav-tabs .nav-link:hover:not(.active) {
    color: var(--ms-dark);
    border-bottom: 3px solid var(--ms-border);
}

/* Badge counts in tabs */
.tab-badge {
    font-size: 0.75rem;
    padding: 0.2em 0.5em;
    vertical-align: middle;
    margin-left: 4px;
}

/* Summary cards */
.summary-card {
    background: white;
    border: 1px solid var(--ms-border);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    text-align: center;
}

.summary-card .number {
    font-size: 2rem;
    font-weight: 700;
    color: var(--ms-blue);
    line-height: 1.2;
}

.summary-card .label {
    font-size: 0.85rem;
    color: var(--ms-gray);
}

/* DataTable overrides */
.dataTables_wrapper {
    padding-top: 0.5rem;
}

table.dataTable {
    font-size: 0.875rem;
}

table.dataTable thead th {
    background: var(--ms-light);
    border-bottom: 2px solid var(--ms-border);
    font-weight: 600;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    white-space: nowrap;
}

table.dataTable thead tr.filters th {
    background: white;
    border-bottom: 1px solid var(--ms-border);
    padding: 4px 6px;
    font-weight: normal;
    text-transform: none;
}

table.dataTable tbody td {
    vertical-align: middle;
    padding: 0.5rem 0.75rem;
}

table.dataTable tbody tr:hover {
    background: #e8f4fd !important;
}

table.dataTable tbody td {
    cursor: pointer;
}

/* Logo images in tables */
.sol-logo {
    width: 28px;
    height: 28px;
    object-fit: contain;
    border-radius: 4px;
}
.sol-logo-fallback {
    display: inline-block;
    width: 28px;
    text-align: center;
    font-size: 20px;
    line-height: 28px;
    opacity: 0.5;
}

/* Links in table cells */
table.dataTable a {
    color: var(--ms-blue);
    text-decoration: none;
}
table.dataTable a:hover {
    text-decoration: underline;
}

/* Status badges */
.badge-active { background: #107c10; }
.badge-deprecated { background: #a80000; }
.badge-unpublished { background: #ca5010; }
.badge-discovered { background: #8764b8; }

/* Legend */
.table-legend {
    margin-top: 0.5rem;
    padding: 0.4rem 0.8rem;
    font-size: 0.78rem;
    color: var(--ms-gray);
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
}
.table-legend .legend-item {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
}

/* Footer */
.footer {
    margin-top: 2rem;
    padding: 1rem 0;
    color: var(--ms-gray);
    font-size: 0.8rem;
    text-align: center;
    border-top: 1px solid var(--ms-border);
}

/* Column filters - individual search */
.column-filter {
    width: 100%;
    padding: 2px 6px;
    font-size: 0.78rem;
    border: 1px solid var(--ms-border);
    border-radius: 3px;
    margin-top: 4px;
}

.column-filter:focus {
    outline: none;
    border-color: var(--ms-blue);
}

/* Top info (record count next to length menu) */
.col-sm-6 .dataTables_info {
    display: inline-block;
    margin-left: 1.2em;
    font-size: 0.85rem;
    color: #666;
    padding-top: 0;
}

/* Clear all filters bar */
.clear-filters-bar {
    display: none;
    padding: 5px 12px;
    margin-bottom: 4px;
    border-radius: 4px;
    background: #fff4ce;
    border: 1px solid #f0d060;
    font-size: 0.82rem;
    color: #6b5900;
    align-items: center;
    justify-content: space-between;
}
.clear-filters-bar.visible {
    display: flex;
}
.clear-filters-bar .clear-label {
    font-weight: 500;
}
.clear-filters-bar .btn-clear-all {
    font-size: 0.78rem;
    padding: 2px 12px;
    border: 1px solid #d4a800;
    border-radius: 4px;
    background: #fff;
    color: #6b5900;
    cursor: pointer;
    font-weight: 500;
}
.clear-filters-bar .btn-clear-all:hover {
    background: #ffeea0;
    border-color: #b08f00;
}

/* Loading overlay */
.loading-overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(255,255,255,0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    font-size: 1.2rem;
    color: var(--ms-blue);
}
""", encoding='utf-8')


def _write_js(path: Path) -> None:
    """Write the application JavaScript."""
    path.write_text("""\
/* Solutions Analyzer Interactive Docs */

$(document).ready(function() {
    // Common DataTable config
    var dtDefaults = {
        pageLength: 50,
        lengthMenu: [[25, 50, 100, -1], [25, 50, 100, "All"]],
        order: [],
        autoWidth: false,
        deferRender: true,
        stateSave: false,
        orderCellsTop: true,
        dom: '<"row"<"col-sm-6"li><"col-sm-6"f>>rtip',
        language: {
            search: "Quick filter:",
            lengthMenu: "Show _MENU_ rows",
            info: "Showing _START_-_END_ of _TOTAL_",
            emptyTable: "No matching records",
        }
    };

    // Initialize DataTables with per-column filters in header
    function initTable(tableId, extraOpts) {
        var opts = $.extend(true, {}, dtDefaults, extraOpts || {});
        opts.initComplete = function() {
            var api = this.api();
            // Add per-column search inputs in the second header row
            $('#' + tableId + ' thead tr.filters th').each(function(i) {
                var column = api.column(i);
                if ($(this).data('filter') !== false) {
                    var input = $('<input type="text" class="column-filter" placeholder="Filter...">')
                        .appendTo($(this).empty())
                        .on('keyup change clear', function() {
                            if (column.search() !== this.value) {
                                column.search(this.value).draw();
                            }
                            updateClearBtn(tableId, api);
                        });
                }
            });

            // Add "Clear All Filters" bar above the table
            var clearBar = $(
                '<div class="clear-filters-bar">' +
                '<span class="clear-label">Filters are active</span>' +
                '<button class="btn-clear-all" title="Clear all filters">✕ Clear All Filters</button>' +
                '</div>'
            );
            clearBar.find('.btn-clear-all').on('click', function() {
                api.search('');
                api.columns().every(function() { this.search(''); });
                $('#' + tableId + ' thead tr.filters input.column-filter').val('');
                $(api.table().container()).find('.dataTables_filter input').val('');
                api.draw();
                clearBar.removeClass('visible');
            });
            $(api.table().container()).prepend(clearBar);

            // Also track global search changes
            $(api.table().container()).find('.dataTables_filter input').on('keyup change clear', function() {
                updateClearBtn(tableId, api);
            });

            // Show button if any filters are active on load (from saved state)
            updateClearBtn(tableId, api);

            // Hide loading overlay
            $('#loading').fadeOut(200);
        };
        return $('#' + tableId).DataTable(opts);
    }

    // Show/hide the Clear All Filters bar based on whether any filters are active
    function updateClearBtn(tableId, api) {
        var hasFilter = !!api.search();
        if (!hasFilter) {
            api.columns().every(function() { if (this.search()) hasFilter = true; });
        }
        $(api.table().container()).find('.clear-filters-bar').toggleClass('visible', hasFilter);
    }

    // Solutions table
    if ($('#solutions-table').length) {
        initTable('solutions-table', {
            order: [[1, 'asc']],
            columnDefs: [
                { targets: 0, orderable: false, searchable: false, width: '40px' },
                { targets: [7,8,9], className: 'text-center' },
                { targets: 6, className: 'text-center' },
            ]
        });
    }

    // Connectors table
    if ($('#connectors-table').length) {
        initTable('connectors-table', {
            order: [[1, 'asc']],
            columnDefs: [
                { targets: 0, orderable: false, searchable: false, width: '40px' },
                { targets: [7], className: 'text-center' },
            ]
        });
    }

    // Tables table
    if ($('#tables-table').length) {
        initTable('tables-table', {
            order: [[0, 'asc']],
            columnDefs: [
                { targets: [3,4], className: 'text-center' },
            ]
        });
    }

    // Content table
    if ($('#content-table').length) {
        initTable('content-table', {
            order: [[0, 'asc']],
        });
    }

    // Parsers table
    if ($('#parsers-table').length) {
        initTable('parsers-table', {
            order: [[0, 'asc']],
        });
    }

    // ASIM table
    if ($('#asim-table').length) {
        initTable('asim-table', {
            order: [[1, 'asc'], [2, 'asc'], [0, 'asc']],
        });
    }

    // Tab switching - use Bootstrap's tab events
    $('button[data-bs-toggle="tab"]').on('shown.bs.tab', function(e) {
        // Adjust DataTable columns on tab show (fixes width issues)
        $.fn.dataTable.tables({ visible: true, api: true }).columns.adjust();
        // Update URL hash to reflect active tab
        var id = $(e.target).attr('id');  // e.g. 'connectors-tab'
        if (id) history.replaceState(null, '', '#' + id.replace('-tab', ''));
    });

    // Activate tab from URL hash
    function activateTabFromHash() {
        var hash = window.location.hash.replace('#', '');
        if (hash) {
            var tabBtn = document.getElementById(hash + '-tab');
            if (tabBtn) {
                bootstrap.Tab.getOrCreateInstance(tabBtn).show();
            }
        }
    }
    // On initial page load
    activateTabFromHash();
    // On hash change (same-page navigation)
    $(window).on('hashchange', activateTabFromHash);
    // On bfcache restoration (back/forward navigation)
    window.addEventListener('pageshow', function(e) {
        if (e.persisted) activateTabFromHash();
    });

    // Click-to-filter: clicking a cell value filters that column
    // Skip if the click target is a link (let it navigate normally)
    $(document).on('click', 'table.dataTable tbody td', function(e) {
        if ($(e.target).closest('a').length) return;
        var table = $(this).closest('table').DataTable();
        var colIdx = table.cell(this).index().column;
        // Get the text content (strip HTML tags)
        var text = $(this).text().trim();
        if (!text || text === '?' || text === '0') return;
        // Don't filter on numeric-only cells or logo columns
        var th = $($(this).closest('table').find('thead tr.filters th')[colIdx]);
        if (th.data('filter') === false) return;
        // Set the column filter
        var input = th.find('input.column-filter');
        if (input.length) {
            input.val(text).trigger('change');
        }
    });
});
""", encoding='utf-8')


def _status_badge(status: str) -> str:
    """Return an HTML badge for a status string."""
    cls = {
        'Active': 'badge-active',
        'Deprecated': 'badge-deprecated',
        'Unpublished': 'badge-unpublished',
        'Discovered': 'badge-discovered',
    }.get(status, 'bg-secondary')
    return f'<span class="badge {cls}">{esc(status)}</span>'


def _logo_img(url: str, fallback: str = '') -> str:
    """Return an img tag for a logo URL, or a fallback emoji/icon string."""
    if not url:
        return f'<span class="sol-logo-fallback">{fallback}</span>' if fallback else ''
    return f'<img src="{esc(url)}" alt="" class="sol-logo" loading="lazy">'


def _popularity_label(value: str) -> str:
    """Format marketplace popularity score for HTML display."""
    if not value:
        return ''
    try:
        score = float(value)
    except ValueError:
        return ''
    pct = int(score * 100)
    if score >= 0.8:
        return f'<span title="Popularity: {pct}%">🟢 High</span>'
    elif score >= 0.5:
        return f'<span title="Popularity: {pct}%">🔵 Medium</span>'
    elif score >= 0.1:
        return f'<span title="Popularity: {pct}%">🟡 Low</span>'
    else:
        return f'<span title="Popularity: {pct}%">⚪ Very Low</span>'


def _write_index_html(
    path: Path,
    solutions_data: List[Dict],
    connectors_data: List[Dict],
    tables_data: List[Dict],
    content_data: List[Dict],
    parsers_data: List[Dict] = None,
    asim_data: List[Dict] = None,
) -> None:
    """Write the main index.html file."""
    parsers_data = parsers_data or []
    asim_data = asim_data or []
    # Summary counts
    active_solutions = sum(1 for s in solutions_data if s['status'] == 'Active')
    active_connectors = sum(1 for c in connectors_data if c['status'] == 'Active')
    total_tables = len(tables_data)
    total_content = len(content_data)

    html_parts = []
    html_parts.append(f"""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Microsoft Sentinel Solutions Analyzer</title>
    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- DataTables Bootstrap 5 -->
    <link href="{DATATABLES_CSS}" rel="stylesheet">
    <!-- Custom -->
    <link href="css/style.css" rel="stylesheet">
</head>
<body>

<div id="loading" class="loading-overlay">Loading data&hellip;</div>

<nav class="navbar navbar-dark">
    <div class="container-fluid">
        <span class="navbar-brand">Microsoft Sentinel &mdash; Solutions Analyzer</span>
        <div class="navbar-nav-links">
            <a href="{_docs_base_path}README{_link_extension}" class="nav-doc-link" title="Documentation home">📖 Docs</a>
            <a href="{_docs_base_path}statistics{_link_extension}" class="nav-doc-link" title="Statistics and metrics">📊 Statistics</a>
            <a href="asim-browser.html" class="nav-doc-link" title="ASIM Schema Browser">🔎 ASIM Browser</a>
        </div>
    </div>
</nav>

<div class="container-fluid py-3">

<!-- Summary cards -->
<div class="row g-3 mb-3">
    <div class="col"><div class="summary-card"><div class="number">{active_solutions}</div><div class="label">Active Solutions</div></div></div>
    <div class="col"><div class="summary-card"><div class="number">{active_connectors}</div><div class="label">Active Connectors</div></div></div>
    <div class="col"><div class="summary-card"><div class="number">{total_tables}</div><div class="label">Tables</div></div></div>
    <div class="col"><div class="summary-card"><div class="number">{total_content}</div><div class="label">Content Items</div></div></div>
    <div class="col"><div class="summary-card"><div class="number">{len(parsers_data)}</div><div class="label">Parsers</div></div></div>
    <div class="col"><div class="summary-card"><div class="number">{len(asim_data)}</div><div class="label">ASIM Parsers</div></div></div>
</div>

<!-- Tabs -->
<ul class="nav nav-tabs" id="mainTabs" role="tablist">
    <li class="nav-item" role="presentation">
        <button class="nav-link active" id="solutions-tab" data-bs-toggle="tab" data-bs-target="#solutions-pane" type="button" role="tab">
            Solutions <span class="badge tab-badge bg-primary">{len(solutions_data)}</span>
        </button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="connectors-tab" data-bs-toggle="tab" data-bs-target="#connectors-pane" type="button" role="tab">
            Connectors <span class="badge tab-badge bg-primary">{len(connectors_data)}</span>
        </button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="tables-tab" data-bs-toggle="tab" data-bs-target="#tables-pane" type="button" role="tab">
            Tables <span class="badge tab-badge bg-primary">{len(tables_data)}</span>
        </button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="content-tab" data-bs-toggle="tab" data-bs-target="#content-pane" type="button" role="tab">
            Content <span class="badge tab-badge bg-primary">{len(content_data)}</span>
        </button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="parsers-tab" data-bs-toggle="tab" data-bs-target="#parsers-pane" type="button" role="tab">
            Parsers <span class="badge tab-badge bg-primary">{len(parsers_data)}</span>
        </button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="asim-tab" data-bs-toggle="tab" data-bs-target="#asim-pane" type="button" role="tab">
            ASIM <span class="badge tab-badge bg-primary">{len(asim_data)}</span>
        </button>
    </li>
</ul>

<div class="tab-content mt-2" id="mainTabContent">
""")

    # ---- Solutions Tab ----
    html_parts.append("""\
<div class="tab-pane fade show active" id="solutions-pane" role="tabpanel">
<table id="solutions-table" class="table table-striped table-hover" style="width:100%">
<thead>
<tr>
    <th></th><th>Solution</th><th>Status</th><th>Publisher</th><th>Support</th>
    <th>First Published</th><th>Popularity</th><th>Connectors</th><th>Tables</th><th>Content</th>
</tr>
<tr class="filters">
    <th data-filter="false"></th><th></th><th></th><th></th><th></th>
    <th></th><th></th><th data-filter="false"></th><th data-filter="false"></th><th data-filter="false"></th>
</tr>
</thead>
<tbody>
""")
    for s in solutions_data:
        logo = _logo_img(s['logo_url'], '📦')
        badge = _status_badge(s['status'])
        name_link = _md_link(s['name'], 'solutions')
        pop_label = _popularity_label(s.get('popularity', ''))
        content_display = str(s['content_items'])
        if s['content_discovered'] > 0:
            content_display = f"{s['content_in_solution']} (+{s['content_discovered']} \U0001f50d)"
        html_parts.append(
            f"<tr><td>{logo}</td><td>{name_link}</td><td>{badge}</td>"
            f"<td>{esc(s['publisher'])}</td><td>{esc(s['support_tier'])}</td>"
            f"<td>{esc(s['first_published'])}</td><td>{pop_label}</td>"
            f"<td>{s['connectors']}</td><td>{s['tables']}</td><td>{content_display}</td></tr>\n"
        )
    html_parts.append("</tbody></table>\n")
    html_parts.append("""\
<div class="table-legend">
    <span class="legend-item"><span class="badge badge-active">Active</span> Published solution</span>
    <span class="legend-item"><span class="badge badge-deprecated">Deprecated</span> Deprecated solution</span>
    <span class="legend-item"><span class="badge badge-unpublished">Unpublished</span> Not on content hub</span>
</div>
""")
    html_parts.append("</div>\n")

    # ---- Connectors Tab ----
    html_parts.append("""\
<div class="tab-pane fade" id="connectors-pane" role="tabpanel">
<table id="connectors-table" class="table table-striped table-hover" style="width:100%">
<thead>
<tr>
    <th></th><th>Connector</th><th>Status</th><th>Publisher</th>
    <th>Collection Method</th><th>Ingestion API</th><th>Solution</th><th>Tables</th>
</tr>
<tr class="filters">
    <th data-filter="false"></th><th></th><th></th><th></th>
    <th></th><th></th><th></th><th data-filter="false"></th>
</tr>
</thead>
<tbody>
""")
    for c in connectors_data:
        logo = _logo_img(c['logo_url'], '🔌')
        badge = _status_badge(c['status'])
        clv1 = f" {CLV1_ICON}" if c.get('is_clv1') else ""
        discovered = f" {DISCOVERED_ICON}" if c.get('is_discovered') else ""
        title_link = _md_link(c['id'], 'connectors').replace(f'>{esc(c["id"])}<', f'>{esc(c["title"])}{clv1}{discovered}<')
        method = c['collection_method']
        if method and method != '?':
            method_file = sanitize_filename(method)
            method_html = f'<a href="{_docs_base_path}methods/{method_file}{_link_extension}">{esc(method)}</a>'
        else:
            method_html = esc(method)
        sol_link = _md_link(c['solution'], 'solutions')
        tables_display = str(c['tables']) if c['tables'] else '?'
        html_parts.append(
            f"<tr><td>{logo}</td><td>{title_link}</td><td>{badge}</td>"
            f"<td>{esc(c['publisher'])}</td><td>{method_html}</td>"
            f"<td>{esc(c['ingestion_api'])}</td>"
            f"<td>{sol_link}</td><td>{tables_display}</td></tr>\n"
        )
    html_parts.append("</tbody></table>\n")
    html_parts.append(f"""\
<div class="table-legend">
    <span class="legend-item"><span class="badge badge-active">Active</span> Published connector</span>
    <span class="legend-item"><span class="badge badge-deprecated">Deprecated</span> Deprecated connector</span>
    <span class="legend-item"><span class="badge badge-unpublished">Unpublished</span> Not on content hub</span>
    <span class="legend-item">{CLV1_ICON} Custom Logs v1 (classic, may not be accurate)</span>
    <span class="legend-item">{DISCOVERED_ICON} Not listed in solution JSON</span>
</div>
""")
    html_parts.append("</div>\n")

    # ---- Tables Tab ----
    html_parts.append("""\
<div class="tab-pane fade" id="tables-pane" role="tabpanel">
<table id="tables-table" class="table table-striped table-hover" style="width:100%">
<thead>
<tr>
    <th>Table</th><th>Discovered Via</th><th>Category</th>
    <th>Solutions</th><th>Connectors</th><th>Azure Monitor</th><th>Defender XDR</th>
</tr>
<tr class="filters">
    <th></th><th></th><th></th>
    <th data-filter="false"></th><th data-filter="false"></th><th></th><th></th>
</tr>
</thead>
<tbody>
""")
    for t in tables_data:
        icons = ""
        if t.get('is_clv1'):
            icons += f" {CLV1_ICON}"
        if t.get('has_schema'):
            icons += f" {SCHEMA_ICON}"
        name_link = _md_link(t['name'], 'tables')
        if icons:
            name_link = name_link.replace('</a>', f'{icons}</a>')
        am = "Yes" if t['azure_monitor'] else "No"
        xdr = "Yes" if t['defender_xdr'] else "No"
        html_parts.append(
            f"<tr><td>{name_link}</td><td>{esc(t['discovery'])}</td><td>{esc(t['category'])}</td>"
            f"<td>{t['solutions']}</td><td>{t['connectors']}</td>"
            f"<td>{am}</td><td>{xdr}</td></tr>\n"
        )
    html_parts.append("</tbody></table>\n")
    html_parts.append(f"""\
<div class="table-legend">
    <span class="legend-item">{CLV1_ICON} Custom Logs v1 (classic, may not be accurate)</span>
    <span class="legend-item">{SCHEMA_ICON} Table schema available</span>
</div>
""")
    html_parts.append("</div>\n")

    # ---- Content Tab ----
    html_parts.append("""\
<div class="tab-pane fade" id="content-pane" role="tabpanel">
<table id="content-table" class="table table-striped table-hover" style="width:100%">
<thead>
<tr>
    <th>Name</th><th>Type</th><th>Source</th><th>Solution</th><th>Description</th>
</tr>
<tr class="filters">
    <th></th><th></th><th></th><th></th><th></th>
</tr>
</thead>
<tbody>
""")
    for item in content_data:
        name_link = _content_link(item)
        discovered = f" {DISCOVERED_ICON}" if item.get('is_discovered') else ""
        if discovered:
            name_link += discovered
        # Source with icon
        src = item.get('content_source', '')
        if src == 'Solution':
            source_html = f'{SOURCE_SOLUTION_ICON} Solution'
        elif src == 'Standalone':
            source_html = f'{SOURCE_STANDALONE_ICON} Standalone'
        elif src == 'GitHub Only':
            source_html = f'{SOURCE_GITHUB_ICON} GitHub'
        else:
            source_html = esc(src)
        sol_name = item['solution']
        if sol_name and sol_name != 'GitHub Only' and item.get('content_source') != 'Standalone':
            sol_link = _md_link(sol_name, 'solutions')
        else:
            sol_link = esc(sol_name)
        html_parts.append(
            f"<tr><td>{name_link}</td><td>{esc(item['type'])}</td>"
            f"<td>{source_html}</td><td>{sol_link}</td><td>{esc(item['description'])}</td></tr>\n"
        )
    html_parts.append("</tbody></table>\n")
    html_parts.append(f"""\
<div class="table-legend">
    <span class="legend-item">{SOURCE_SOLUTION_ICON} In solution package</span>
    <span class="legend-item">{SOURCE_STANDALONE_ICON} Standalone (not in solution JSON)</span>
    <span class="legend-item">{SOURCE_GITHUB_ICON} GitHub only (no content hub package)</span>
    <span class="legend-item">{DISCOVERED_ICON} Not listed in solution JSON</span>
</div>
""")
    html_parts.append("</div>\n")

    # ---- Parsers Tab ----
    html_parts.append("""\
<div class="tab-pane fade" id="parsers-pane" role="tabpanel">
<table id="parsers-table" class="table table-striped table-hover" style="width:100%">
<thead>
<tr>
    <th>Parser</th><th>Source</th><th>Solution</th><th>Tables</th>
</tr>
<tr class="filters">
    <th></th><th></th><th></th><th></th>
</tr>
</thead>
<tbody>
""")
    for p in parsers_data:
        discovered = f" {DISCOVERED_ICON}" if p.get('is_discovered') else ""
        name_link = f'<a href="{_docs_base_path}parsers/{sanitize_filename(p["name"])}{_link_extension}">{esc(p["name"])}</a>{discovered}'
        if p['source'] == 'Legacy':
            source_html = '📂 Legacy'
        else:
            source_html = f'{SOURCE_SOLUTION_ICON} Solution'
        sol = p.get('solution', '')
        sol_html = _md_link(sol, 'solutions') if sol else ''
        html_parts.append(
            f"<tr><td>{name_link}</td><td>{source_html}</td>"
            f"<td>{sol_html}</td><td>{esc(p['tables'])}</td></tr>\n"
        )
    html_parts.append("</tbody></table>\n")
    html_parts.append(f"""\
<div class="table-legend">
    <span class="legend-item">{SOURCE_SOLUTION_ICON} In solution package</span>
    <span class="legend-item">📂 Legacy parser (Parsers folder)</span>
    <span class="legend-item">{DISCOVERED_ICON} Discovered (not in solution JSON)</span>
</div>
""")
    html_parts.append("</div>\n")

    # ---- ASIM Tab ----
    html_parts.append("""\
<div class="tab-pane fade" id="asim-pane" role="tabpanel">
<table id="asim-table" class="table table-striped table-hover" style="width:100%">
<thead>
<tr>
    <th>Parser</th><th>Schema</th><th>Type</th><th>Product</th><th>Version</th><th>Solutions</th>
</tr>
<tr class="filters">
    <th></th><th></th><th></th><th></th><th></th><th></th>
</tr>
</thead>
<tbody>
""")
    for a in asim_data:
        name_link = f'<a href="{_docs_base_path}asim/{sanitize_filename(a["name"])}{_link_extension}">{esc(a["name"])}</a>'
        # Build solution links (comma-separated)
        sol_parts = []
        if a.get('solutions'):
            for sol in [s.strip() for s in a['solutions'].split(',') if s.strip()]:
                sol_parts.append(_md_link(sol, 'solutions'))
        sols_html = ', '.join(sol_parts) if sol_parts else ''
        html_parts.append(
            f"<tr><td>{name_link}</td><td>{esc(a['schema'])}</td>"
            f"<td>{esc(a['type'])}</td><td>{esc(a['product'])}</td>"
            f"<td>{esc(a['version'])}</td><td>{sols_html}</td></tr>\n"
        )
    html_parts.append("</tbody></table>\n")
    html_parts.append("""\
<div class="table-legend">
    <span class="legend-item"><b>Unifying</b> Aggregates multiple source parsers</span>
    <span class="legend-item"><b>Source</b> Parses a specific product log</span>
</div>
""")
    html_parts.append("</div>\n")

    # Close tabs
    html_parts.append("""\
</div><!-- tab-content -->

<div class="footer">
    Generated by Microsoft Sentinel Solutions Analyzer
</div>

</div><!-- container -->

<!-- Scripts -->
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://cdn.datatables.net/1.13.8/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/1.13.8/js/dataTables.bootstrap5.min.js"></script>
<script src="js/app.js"></script>
</body>
</html>
""")

    path.write_text("".join(html_parts), encoding='utf-8')


# ---------------------------------------------------------------------------
# HTML entity page generation  (MD → HTML conversion)
# ---------------------------------------------------------------------------

def _write_page_css(path: Path) -> None:
    """Write CSS for the rendered HTML entity pages."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("""\
/* Solutions Analyzer – entity page styles */
:root {
    --ms-blue: #0078d4;
    --ms-dark: #1b1a19;
    --ms-gray: #605e5c;
    --ms-light: #f3f2f1;
    --ms-border: #e1dfdd;
}
* { box-sizing: border-box; }
body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    margin: 0; padding: 0;
    color: #333; background: #faf9f8;
}

/* Navbar (matches interactive index) */
.navbar {
    background: var(--ms-blue);
    padding: 8px 20px;
    display: flex; align-items: center; justify-content: space-between;
}
.navbar-brand {
    color: #fff; font-weight: 600; font-size: 1.05rem;
}
.navbar-nav-links { display: flex; gap: 16px; align-items: center; }
.navbar-nav-links a {
    color: rgba(255,255,255,0.85); text-decoration: none; font-size: 0.85rem;
}
.navbar-nav-links a:hover { color: #fff; }

/* Content area */
.doc-content {
    max-width: 1100px; margin: 24px auto; padding: 28px 36px;
    background: #fff; border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    line-height: 1.65;
}

/* Typography */
h1 { color: var(--ms-blue); border-bottom: 2px solid var(--ms-border); padding-bottom: 8px; margin-top: 0; }
h2 { color: #333; margin-top: 1.6em; border-bottom: 1px solid var(--ms-border); padding-bottom: 6px; }
h3 { color: #444; margin-top: 1.3em; }
h4 { color: var(--ms-gray); margin-top: 1.1em; }

a { color: var(--ms-blue); text-decoration: none; }
a:hover { text-decoration: underline; }

/* Tables */
table { border-collapse: collapse; width: 100%; margin: 14px 0; font-size: 0.9rem; }
th, td { border: 1px solid var(--ms-border); padding: 8px 12px; text-align: left; }
th { background: var(--ms-light); font-weight: 600; }
tr:hover { background: #f5f5f5; }

/* Code */
code {
    background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.88em;
    font-family: 'Cascadia Code', 'Consolas', monospace;
}
pre { background: #f5f5f5; padding: 14px 18px; border-radius: 6px; overflow-x: auto; }
pre code { background: none; padding: 0; }

/* Horizontal rules */
hr { border: none; border-top: 1px solid var(--ms-border); margin: 1.5em 0; }

/* Lists */
ul, ol { padding-left: 1.5em; }
li { margin: 4px 0; }

/* Images */
img { max-width: 100%; height: auto; }

/* Responsive */
@media (max-width: 768px) {
    .doc-content { margin: 10px; padding: 18px; }
    table { font-size: 0.82rem; }
    th, td { padding: 5px 8px; }
}

/* DataTable overrides for schema tables */
table.dataTable thead th {
    background: var(--ms-light);
    font-weight: 600;
    white-space: nowrap;
}
table.dataTable thead tr.filters th {
    background: #fff;
    padding: 4px 6px;
}
table.dataTable thead tr.filters input {
    width: 100%;
    padding: 2px 6px;
    font-size: 0.82rem;
    border: 1px solid var(--ms-border);
    border-radius: 3px;
}
table.dataTable thead tr.filters input:focus {
    outline: none;
    border-color: var(--ms-blue);
}
table.dataTable tbody tr:hover {
    background: #e8f4fd !important;
}
.dataTables_filter { margin-bottom: 6px; }
""", encoding='utf-8')


_PAGE_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} &mdash; Solutions Analyzer</title>
<link rel="stylesheet" href="{css_path}">
{head_extra}
</head>
<body>
<nav class="navbar">
    <a href="{index_url}" class="navbar-brand" style="text-decoration:none;color:inherit">Microsoft Sentinel &mdash; Solutions Analyzer</a>
    <div class="navbar-nav-links">
        <a href="{asim_browser_url}" class="nav-doc-link" title="ASIM Schema Browser">🔎 ASIM Browser</a>
    </div>
</nav>
<div class="doc-content">
{body}
</div>
{body_extra}
</body>
</html>
"""

# DataTables resources injected into table doc pages that have a schema section.
_DATATABLE_HEAD_EXTRA = """\
<link href="https://cdn.datatables.net/1.13.8/css/dataTables.bootstrap5.min.css" rel="stylesheet">
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.datatables.net/1.13.8/js/jquery.dataTables.min.js"></script>"""

_DATATABLE_BODY_EXTRA = """\
<script>
$(function() {
    var t = $('#schema-table');
    if (!t.length) return;
    // Add filter row to thead
    var hdr = t.find('thead');
    var cols = hdr.find('tr:first th').length;
    var fr = $('<tr class="filters"></tr>');
    for (var i = 0; i < cols; i++) fr.append('<th><input type="text" placeholder="Filter…"></th>');
    hdr.append(fr);
    // Init DataTable
    var dt = t.DataTable({
        paging: false,
        info: true,
        orderCellsTop: true,
        dom: 'frti',
    });
    // Per-column filter
    hdr.find('tr.filters input').each(function(i) {
        $(this).on('keyup change', function() {
            dt.column(i).search(this.value).draw();
        });
    });
});
</script>"""


def _generate_html_pages(docs_dir: Path, html_output_dir: Path,
                         index_url: str) -> None:
    """Convert every .md file under *docs_dir* to a styled .html page.

    * Uses Python-Markdown with ``tables`` and ``fenced_code`` extensions.
    * Rewrites relative ``.md`` links to ``.html`` so internal navigation
      works entirely within the HTML entity pages.
    * Writes a ``page.css`` stylesheet to ``{html_output_dir}/css/``.
    """
    import time as _time
    try:
        import markdown as _markdown_lib
    except ImportError:
        print("  WARNING: 'markdown' package not installed — skipping HTML page generation.")
        print("           Install with: pip install markdown")
        return

    # Write shared CSS for entity pages
    _write_page_css(html_output_dir / "css" / "page.css")

    # Map subdirectory names to the corresponding tab hash fragment on
    # index.html so that the navbar "Interactive" link opens the right tab.
    _dir_to_tab = {
        'solutions': 'solutions',
        'connectors': 'connectors',
        'tables': 'tables',
        'content': 'content',
        'parsers': 'parsers',
        'asim': 'asim',
        'methods': 'connectors',   # methods are shown via the Connectors tab
    }

    # Map index page filenames to tab hash fragments (for browse-bar rewriting)
    _index_to_tab = {
        'solutions-index.html': '#solutions',
        'connectors-index.html': '#connectors',
        'methods-index.html': '#connectors',
        'tables-index.html': '#tables',
        'content-index.html': '#content',
        'parsers-index.html': '#parsers',
        'asim-index.html': '#asim',
        'asim-products-index.html': '#asim',
    }

    # Pre-compile regex patterns used in the per-file loop
    _re_h1 = re.compile(r'^#\s+(.+)$', re.MULTILINE)
    _re_strip_md_fmt = re.compile(r'[*_`\[\]()]')
    _re_md_links = re.compile(r'href="(?!https?://|mailto:)([^"]*?)\.md"')
    _re_index_links = re.compile(
        r'href="(?:[^"]*/)?((?:solutions|connectors|methods|tables|content|parsers|asim(?:-products)?)-index\.html)"'
    )
    _re_home_link = re.compile(r'href="[^"]*README\.html"')
    _re_interactive_link = re.compile(r'\s*·\s*<a\s+href="[^"]*"[^>]*>🔍</a>')
    _re_schema_table = re.compile(
        r'(<h2>Schema\b[^<]*</h2>\s*(?:<p>.*?</p>\s*)?)<table>',
        re.DOTALL,
    )

    # Reuse a single Markdown converter instance (reset between files)
    # Note: 'toc' extension intentionally omitted — we don't generate a
    # [TOC] block and it adds significant per-file overhead.
    md_extensions = ['tables', 'fenced_code', 'sane_lists']
    md_converter = _markdown_lib.Markdown(extensions=md_extensions)

    # Collect files first to know total count for progress reporting
    md_files = sorted(docs_dir.rglob('*.md'))
    total = len(md_files)
    count = 0
    t_start = _time.perf_counter()

    print(f"  Converting {total} markdown files to HTML...", flush=True)

    for md_file in md_files:
        file_t0 = _time.perf_counter()
        md_content = md_file.read_text(encoding='utf-8')

        # Extract title from first H1
        title_match = _re_h1.search(md_content)
        if title_match:
            title = _re_strip_md_fmt.sub('', title_match.group(1)).strip()
        else:
            title = md_file.stem

        # Determine the parent directory (used for tab linking and schema detection)
        parent_name = md_file.parent.name

        # Convert markdown → HTML body (reuse converter, reset state)
        md_converter.reset()
        html_body = md_converter.convert(md_content)

        # Rewrite relative .md links → .html  (leave http(s) and mailto alone)
        html_body = _re_md_links.sub(r'href="\1.html"', html_body)

        # Compute base index URL (without tab hash) for browse-bar rewriting.
        # Always use relative paths — HTML entity pages coexist with index.html
        # in the same served directory structure, so relative links work both
        # locally (file://) and on GitHub Pages.
        base_index_url = os.path.relpath(
            html_output_dir / 'index.html',
            md_file.parent,
        ).replace('\\', '/')

        # Rewrite browse-bar links: static index pages → index.html#tab
        def _rewrite_index_link(m: re.Match, _base=base_index_url) -> str:
            """Replace static index page links with index.html#tab links."""
            filename = m.group(1)
            if filename in _index_to_tab:
                return f'href="{_base}{_index_to_tab[filename]}"'
            return m.group(0)

        html_body = _re_index_links.sub(_rewrite_index_link, html_body)

        # Rewrite 🏠 home link: README.html → index.html (no tab hash)
        html_body = _re_home_link.sub(f'href="{base_index_url}"', html_body)

        # Remove the 🔍 Interactive link from the browse bar (if still present)
        html_body = _re_interactive_link.sub('', html_body)

        # For table docs with a Schema section, tag the schema <table> with
        # an id so DataTables.js can enhance it with sort + filter.
        has_schema_table = False
        if parent_name == 'tables':
            html_body, n = _re_schema_table.subn(
                r'\1<table id="schema-table">',
                html_body,
                count=1,
            )
            has_schema_table = n > 0

        head_extra = _DATATABLE_HEAD_EXTRA if has_schema_table else ''
        body_extra = _DATATABLE_BODY_EXTRA if has_schema_table else ''

        # Compute relative path to CSS
        css_path = os.path.relpath(
            html_output_dir / 'css' / 'page.css',
            md_file.parent,
        ).replace('\\', '/')

        # Determine the tab fragment from the parent directory name
        tab_fragment = _dir_to_tab.get(parent_name, '')
        tab_hash = f'#{tab_fragment}' if tab_fragment else ''

        # Compute index URL — always relative (same rationale as base_index_url)
        page_index_url = os.path.relpath(
            html_output_dir / 'index.html',
            md_file.parent,
        ).replace('\\', '/') + tab_hash

        # Compute ASIM browser URL — relative from this page to asim-browser.html
        page_asim_url = os.path.relpath(
            html_output_dir / 'asim-browser.html',
            md_file.parent,
        ).replace('\\', '/')

        # Assemble final page
        html_page = _PAGE_HTML_TEMPLATE.format(
            title=esc(title),
            css_path=css_path,
            index_url=esc(page_index_url),
            asim_browser_url=esc(page_asim_url),
            body=html_body,
            head_extra=head_extra,
            body_extra=body_extra,
        )

        html_file = md_file.with_suffix('.html')
        html_file.write_text(html_page, encoding='utf-8')
        count += 1

        # Warn about slow individual files (>5s)
        file_dt = _time.perf_counter() - file_t0
        if file_dt > 5:
            print(f"    SLOW ({file_dt:.1f}s): {md_file.relative_to(docs_dir)}", flush=True)

        # Progress reporting every 200 converted files
        if count % 200 == 0:
            elapsed = _time.perf_counter() - t_start
            rate = count / elapsed if elapsed > 0 else 0
            remaining = (total - count) / rate if rate > 0 else 0
            print(f"    {count:,}/{total:,} pages ({elapsed:.1f}s elapsed, ~{remaining:.0f}s remaining)", flush=True)

    elapsed = _time.perf_counter() - t_start
    print(f"  Generated {count:,} HTML entity pages in {elapsed:.1f}s")


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def generate_interactive(
    mapping_csv: Path,
    connectors_csv: Path,
    solutions_csv: Path,
    content_items_csv: Path,
    tables_csv: Path,
    output_dir: Path,
    content_tables_csv: Path = None,
    tables_overrides_csv: Path = None,
    table_schemas_csv: Path = None,
    parsers_csv: Path = None,
    asim_parsers_csv: Path = None,
    html_output_dir: Path = None,
    html_docs_path: str = '',
    html_index_url: str = '',
) -> None:
    """Main entry point: load data and generate interactive HTML docs.

    Args:
        html_output_dir: Where to write index.html, css/, js/.
            Defaults to *output_dir* (same directory as the markdown docs).
            When provided, also generates HTML entity pages alongside the
            markdown docs (unless *html_docs_path* is an absolute URL).
        html_docs_path: Relative or absolute URL path prefix from index.html
            to the markdown docs directory.  For example ``"Solutions Docs/"``
            when index.html lives at the repo root and docs live in
            ``Solutions Docs/``.  Must end with ``/`` if non-empty.
            An absolute URL (starting with ``http://`` or ``https://``) is
            also supported — in that case HTML entity pages are NOT generated
            and all links point to the external URL.
        html_index_url: Absolute URL to index.html (e.g. GitHub Pages URL).
            Used in HTML entity page navbars and in static markdown page
            navbars.  Falls back to a relative path if empty.
    """
    global _docs_base_path, _link_extension

    # Determine whether to generate HTML entity pages.
    # When html_output_dir is explicit and docs_path is relative (not an
    # external URL), we render .html copies of every markdown page and
    # make the interactive index link to the .html versions.
    _wants_html_pages = (
        html_output_dir is not None
        and not html_docs_path.startswith(('http://', 'https://'))
    )
    _link_extension = '.html' if _wants_html_pages else '.md'

    # Normalise docs base path
    if html_docs_path:
        # Ensure trailing slash for relative paths
        if not html_docs_path.startswith(('http://', 'https://')) and not html_docs_path.endswith('/'):
            html_docs_path += '/'
        _docs_base_path = html_docs_path
    else:
        _docs_base_path = ''

    if html_output_dir is None:
        html_output_dir = output_dir

    print("Generating interactive HTML documentation...")

    # Default paths relative to this script
    script_dir = Path(__file__).parent
    if content_tables_csv is None:
        content_tables_csv = script_dir / "content_tables_mapping.csv"
    if tables_overrides_csv is None:
        tables_overrides_csv = script_dir / "tables.csv"
    if table_schemas_csv is None:
        table_schemas_csv = script_dir / "table_schemas.csv"
    if parsers_csv is None:
        parsers_csv = script_dir / "parsers.csv"
    if asim_parsers_csv is None:
        asim_parsers_csv = script_dir / "asim_parsers.csv"

    print("  Loading data...")
    by_solution = load_mapping_data(mapping_csv)
    connectors_ref = load_connectors_data(connectors_csv)
    solutions_ref = load_solutions_data(solutions_csv)
    content_items = load_content_items(content_items_csv)
    tables_ref = load_tables_reference(tables_csv)

    # Merge tables overrides (tables.csv) into tables_ref
    load_tables_overrides(tables_overrides_csv, tables_ref)

    # Load content-to-tables mapping and table schemas
    content_tables = load_content_tables(content_tables_csv)
    tables_with_schemas = load_table_schemas(table_schemas_csv)

    print("  Building data tables...")
    solutions_data = build_solutions_table_data(by_solution, solutions_ref, content_items)
    connectors_data = build_connectors_table_data(by_solution, connectors_ref, solutions_ref)
    tables_data = build_tables_table_data(by_solution, tables_ref, content_tables, tables_with_schemas)
    content_data = build_content_table_data(content_items)

    # Load parsers
    parsers_raw = load_parsers(parsers_csv)
    parsers_data = build_parsers_table_data(parsers_raw)

    # Load ASIM parsers
    asim_raw = load_csv(asim_parsers_csv)
    asim_data = build_asim_table_data(asim_raw)

    print(f"  Solutions: {len(solutions_data)}, Connectors: {len(connectors_data)}, "
          f"Tables: {len(tables_data)}, Content: {len(content_data)}, "
          f"Parsers: {len(parsers_data)}, ASIM: {len(asim_data)}")

    generate_html_page(html_output_dir, solutions_data, connectors_data, tables_data,
                       content_data, parsers_data, asim_data)

    # Generate HTML entity pages alongside the markdown docs
    if _wants_html_pages:
        index_url = html_index_url or 'index.html'
        _generate_html_pages(output_dir, html_output_dir, index_url)


def main() -> None:
    """CLI entry point for standalone usage."""
    parser = argparse.ArgumentParser(
        description="Generate interactive HTML documentation with DataTables.js"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).parent / "solutions_connectors_tables_mapping.csv",
        help="Path to solutions-connectors-tables mapping CSV",
    )
    parser.add_argument(
        "--connectors-csv",
        type=Path,
        default=Path(__file__).parent / "connectors.csv",
        help="Path to connectors CSV",
    )
    parser.add_argument(
        "--solutions-csv",
        type=Path,
        default=Path(__file__).parent / "solutions.csv",
        help="Path to solutions CSV",
    )
    parser.add_argument(
        "--content-items-csv",
        type=Path,
        default=Path(__file__).parent / "content_items.csv",
        help="Path to content items CSV",
    )
    parser.add_argument(
        "--tables-csv",
        type=Path,
        default=Path(__file__).parent / "tables_reference.csv",
        help="Path to tables reference CSV",
    )
    parser.add_argument(
        "--content-tables-csv",
        type=Path,
        default=Path(__file__).parent / "content_tables_mapping.csv",
        help="Path to content-to-tables mapping CSV",
    )
    parser.add_argument(
        "--tables-overrides-csv",
        type=Path,
        default=Path(__file__).parent / "tables.csv",
        help="Path to tables overrides CSV (mapper output)",
    )
    parser.add_argument(
        "--table-schemas-csv",
        type=Path,
        default=Path(__file__).parent / "table_schemas.csv",
        help="Path to table schemas CSV",
    )
    parser.add_argument(
        "--parsers-csv",
        type=Path,
        default=Path(__file__).parent / "parsers.csv",
        help="Path to parsers CSV",
    )
    parser.add_argument(
        "--asim-parsers-csv",
        type=Path,
        default=Path(__file__).parent / "asim_parsers.csv",
        help="Path to ASIM parsers CSV",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "interactive-docs",
        help="Output directory for markdown docs (also used for HTML if --html-output-dir not set)",
    )
    parser.add_argument(
        "--html-output-dir",
        type=Path,
        default=None,
        help="Output directory for index.html, css/, js/ (default: same as --output-dir)",
    )
    parser.add_argument(
        "--html-docs-path",
        type=str,
        default='',
        help="Relative or absolute URL path from index.html to the docs directory "
             "(e.g. 'Solutions Docs/' when index.html is at repo root). Must end with '/'. "
             "When relative and --html-output-dir is set, HTML entity pages are generated.",
    )
    parser.add_argument(
        "--html-index-url",
        type=str,
        default='',
        help="Absolute URL to index.html (e.g. GitHub Pages URL). Used in HTML entity "
             "page navbars.  Falls back to a relative path if not provided.",
    )

    args = parser.parse_args()

    generate_interactive(
        mapping_csv=args.input,
        connectors_csv=args.connectors_csv,
        solutions_csv=args.solutions_csv,
        content_items_csv=args.content_items_csv,
        tables_csv=args.tables_csv,
        output_dir=args.output_dir,
        content_tables_csv=args.content_tables_csv,
        tables_overrides_csv=args.tables_overrides_csv,
        table_schemas_csv=args.table_schemas_csv,
        parsers_csv=args.parsers_csv,
        asim_parsers_csv=args.asim_parsers_csv,
        html_output_dir=args.html_output_dir,
        html_docs_path=args.html_docs_path,
        html_index_url=args.html_index_url,
    )


if __name__ == "__main__":
    main()
