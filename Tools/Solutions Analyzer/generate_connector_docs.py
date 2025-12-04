"""
Generate Microsoft Learn-style connector documentation from CSV.

Creates markdown documentation organized by solution, mimicking the structure
of https://learn.microsoft.com/en-us/azure/sentinel/data-connectors-reference
"""

import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set
import argparse
from urllib.parse import quote


def sanitize_anchor(text: str) -> str:
    """Convert text to URL-safe anchor."""
    return text.lower().replace(" ", "-").replace("/", "-").replace("_", "-")


def generate_index_page(solutions: Dict[str, List[Dict[str, str]]], output_dir: Path) -> None:
    """Generate the main index page with table of all solutions."""
    
    index_path = output_dir / "solutions-index.md"
    
    with index_path.open("w", encoding="utf-8") as f:
        f.write("# Microsoft Sentinel Solutions Index\n\n")
        f.write("This reference documentation provides detailed information about data connectors ")
        f.write("available in Microsoft Sentinel Solutions.\n\n")
        
        # Add navigation to other indexes
        f.write("**Browse by:**\n\n")
        f.write("- [Solutions](solutions-index.md) (this page)\n")
        f.write("- [Connectors](connectors-index.md)\n")
        f.write("- [Tables](tables-index.md)\n\n")
        f.write("---\n\n")
        
        f.write("## Overview\n\n")
        f.write(f"This documentation covers **{len(solutions)} solutions** with data connectors, ")
        
        # Count unique connectors across all solutions
        all_connector_ids = set()
        for connectors in solutions.values():
            for conn in connectors:
                connector_id = conn.get('connector_id', '')
                if connector_id:
                    all_connector_ids.add(connector_id)
        
        # Count unique tables across all solutions
        all_tables = set()
        for connectors in solutions.values():
            for conn in connectors:
                table = conn.get('Table', '')
                if table:
                    all_tables.add(table)
        
        f.write(f"providing access to **{len(all_connector_ids)} unique connectors** ")
        f.write(f"and **{len(all_tables)} unique tables**.\n\n")
        
        # Statistics section
        f.write("### Quick Statistics\n\n")
        f.write("| Metric | Count |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Total Solutions | {len(solutions)} |\n")
        f.write(f"| Unique Connectors | {len(all_connector_ids)} |\\n")
        f.write(f"| Unique Tables | {len(all_tables)} |\\n\\n")
        
        # Organization section
        f.write("## How This Documentation is Organized\\n\\n")
        f.write("Each solution has its own page containing:\n\n")
        f.write("- **Solution Overview**: Publisher, support information, and categories\n")
        f.write("- **Connectors**: List of all connectors in the solution\n")
        f.write("- **Tables**: Data tables ingested by the connectors\n")
        f.write("- **GitHub Links**: Direct links to connector definition files\n\n")
        
        # Generate alphabetical index
        f.write("## Solutions Index\n\n")
        f.write("Browse solutions alphabetically:\n\n")
        
        # Create alphabetical sections
        by_letter: Dict[str, List[str]] = defaultdict(list)
        for solution_name in sorted(solutions.keys()):
            first_letter = solution_name[0].upper()
            if first_letter.isalpha():
                by_letter[first_letter].append(solution_name)
            else:
                by_letter['#'].append(solution_name)
        
        # Letter navigation
        f.write("**Jump to:** ")
        letters = sorted(by_letter.keys())
        f.write(" | ".join(f"[{letter}](#{letter.lower()})" for letter in letters))
        f.write("\n\n")
        
        # Generate sections by letter
        for letter in letters:
            f.write(f"### {letter}\n\n")
            f.write("| Solution | First Published | Publisher |\n")
            f.write("|----------|----------------|----------|\n")
            
            for solution_name in sorted(by_letter[letter]):
                connectors = solutions[solution_name]
                
                support_tier = connectors[0].get('solution_support_tier', 'N/A')
                support_name = connectors[0].get('solution_support_name', 'N/A')
                first_published = connectors[0].get('solution_first_publish_date', 'N/A')
                
                solution_link = f"[{solution_name}](solutions/{sanitize_anchor(solution_name)}.md)"
                f.write(f"| {solution_link} | {first_published} | {support_name} |\n")
            
            f.write("\n")
    
    print(f"Generated index: {index_path}")


def generate_connectors_index(solutions: Dict[str, List[Dict[str, str]]], output_dir: Path) -> None:
    """Generate connectors index page organized alphabetically."""
    
    index_path = output_dir / "connectors-index.md"
    
    # Collect all unique connectors with their metadata
    connectors_map: Dict[str, Dict[str, any]] = {}
    
    for solution_name, connectors in solutions.items():
        for conn in connectors:
            connector_id = conn.get('connector_id', '')
            if not connector_id or connector_id in connectors_map:
                continue
            
            connector_title = conn.get('connector_title', connector_id)
            connectors_map[connector_id] = {
                'title': connector_title,
                'publisher': conn.get('connector_publisher', 'N/A'),
                'solution_name': solution_name,
                'solution_folder': conn.get('solution_folder', ''),
                'tables': set(),
                'description': conn.get('connector_description', ''),
            }
        
        # Collect all tables for each connector
        for conn in connectors:
            connector_id = conn.get('connector_id', '')
            if connector_id in connectors_map:
                table = conn.get('Table', '')
                if table:
                    connectors_map[connector_id]['tables'].add(table)
    
    with index_path.open("w", encoding="utf-8") as f:
        f.write("# Microsoft Sentinel Connectors Index\n\n")
        f.write("Browse all data connectors available in Microsoft Sentinel Solutions.\n\n")
        
        # Add navigation
        f.write("**Browse by:**\n\n")
        f.write("- [Solutions](connector-reference-index.md)\n")
        f.write("- [Connectors](connectors-index.md) (this page)\n")
        f.write("- [Tables](tables-index.md)\n\n")
        f.write("---\n\n")
        
        f.write(f"## Overview\n\n")
        f.write(f"This page lists **{len(connectors_map)} unique connectors** across all solutions.\n\n")
        
        # Separate deprecated and active connectors
        deprecated_connectors = {}
        active_connectors = {}
        
        for connector_id, info in connectors_map.items():
            title = info['title']
            if '[DEPRECATED]' in title.upper() or title.startswith('[Deprecated]'):
                deprecated_connectors[connector_id] = info
            else:
                active_connectors[connector_id] = info
        
        # Create alphabetical index for active connectors
        by_letter: Dict[str, List[str]] = defaultdict(list)
        for connector_id, info in active_connectors.items():
            title = info['title']
            first_letter = title[0].upper()
            if first_letter.isalpha():
                by_letter[first_letter].append(connector_id)
            else:
                by_letter['#'].append(connector_id)
        
        # Letter navigation
        f.write("**Jump to:** ")
        letters = sorted(by_letter.keys())
        f.write(" | ".join(f"[{letter}](#{letter.lower()})" for letter in letters))
        f.write("\n\n")
        
        # Generate sections by letter
        for letter in letters:
            f.write(f"## {letter}\n\n")
            
            for connector_id in sorted(by_letter[letter], key=lambda cid: connectors_map[cid]['title']):
                info = connectors_map[connector_id]
                title = info['title']
                publisher = info['publisher']
                solution_name = info['solution_name']
                tables = sorted(info['tables'])
                
                f.write(f"### [{title}](connectors/{sanitize_anchor(connector_id)}.md)\n\n")
                f.write(f"**Publisher:** {publisher}\n\n")
                f.write(f"**Solution:** [{solution_name}](solutions/{sanitize_anchor(solution_name)}.md)\n\n")
                
                if tables:
                    f.write(f"**Tables ({len(tables)}):** ")
                    f.write(", ".join(f"`{table}`" for table in tables))
                    f.write("\n\n")
                
                description = info['description']
                if description:
                    # Replace <br> with newline but preserve markdown links
                    description = description.replace('<br>', '\n')
                    f.write(f"{description}\n\n")
                
                f.write(f"[→ View full connector details](connectors/{sanitize_anchor(connector_id)}.md)\n\n")
                f.write("---\n\n")
        
        # Add deprecated connectors section at the end
        if deprecated_connectors:
            f.write("## Deprecated Connectors\n\n")
            f.write(f"The following **{len(deprecated_connectors)} connector(s)** are deprecated:\n\n")
            
            for connector_id in sorted(deprecated_connectors.keys(), key=lambda cid: deprecated_connectors[cid]['title']):
                info = deprecated_connectors[connector_id]
                title = info['title']
                publisher = info['publisher']
                solution_name = info['solution_name']
                tables = sorted(info['tables'])
                
                f.write(f"### [{title}](connectors/{sanitize_anchor(connector_id)}.md)\n\n")
                f.write(f"**Publisher:** {publisher}\n\n")
                f.write(f"**Solution:** [{solution_name}](solutions/{sanitize_anchor(solution_name)}.md)\n\n")
                
                if tables:
                    f.write(f"**Tables ({len(tables)}):** ")
                    f.write(", ".join(f"`{table}`" for table in tables))
                    f.write("\n\n")
                
                description = info['description']
                if description:
                    # Replace <br> with newline but preserve markdown links
                    description = description.replace('<br>', '\n')
                    f.write(f"{description}\n\n")
                
                f.write(f"[→ View full connector details](connectors/{sanitize_anchor(connector_id)}.md)\n\n")
                f.write("---\n\n")
    
    print(f"Generated connectors index: {index_path}")


def generate_tables_index(solutions: Dict[str, List[Dict[str, str]]], output_dir: Path) -> None:
    """Generate tables index page organized alphabetically."""
    
    index_path = output_dir / "tables-index.md"
    
    # Collect all unique tables with their usage
    tables_map: Dict[str, Dict[str, any]] = defaultdict(lambda: {
        'solutions': set(),
        'connectors': set(),
        'is_unique': False,
    })
    
    for solution_name, connectors in solutions.items():
        for conn in connectors:
            table = conn.get('Table', '')
            if not table:
                continue
            
            connector_id = conn.get('connector_id', '')
            # Skip entries with empty connector_id (solutions without connectors)
            if not connector_id.strip():
                continue
            connector_title = conn.get('connector_title', connector_id)
            tables_map[table]['solutions'].add(solution_name)
            tables_map[table]['connectors'].add((connector_id, connector_title))
            
            # Check if unique
            if conn.get('is_unique', 'false') == 'true':
                tables_map[table]['is_unique'] = True
    
    with index_path.open("w", encoding="utf-8") as f:
        f.write("# Microsoft Sentinel Tables Index\n\n")
        f.write("Browse all tables ingested by Microsoft Sentinel data connectors.\n\n")
        
        # Add navigation
        f.write("**Browse by:**\n\n")
        f.write("- [Solutions](solutions-index.md)\n")
        f.write("- [Connectors](connectors-index.md)\n")
        f.write("- [Tables](tables-index.md) (this page)\n\n")
        f.write("---\n\n")
        
        f.write(f"## Overview\n\n")
        f.write(f"This page lists **{len(tables_map)} unique tables** ingested by connectors.\n\n")
        
        # Create alphabetical index
        by_letter: Dict[str, List[str]] = defaultdict(list)
        for table in tables_map.keys():
            first_letter = table[0].upper()
            if first_letter.isalpha():
                by_letter[first_letter].append(table)
            else:
                by_letter['#'].append(table)
        
        # Letter navigation
        f.write("**Jump to:** ")
        letters = sorted(by_letter.keys())
        f.write(" | ".join(f"[{letter}](#{letter.lower()})" for letter in letters))
        f.write("\n\n")
        
        # Generate sections by letter
        for letter in letters:
            f.write(f"## {letter}\n\n")
            f.write("| Table | Solutions | Connectors |\n")
            f.write("|-------|-----------|------------|\n")
            
            for table in sorted(by_letter[letter]):
                info = tables_map[table]
                num_solutions = len(info['solutions'])
                
                # Create links to first few solutions
                solution_links = []
                for solution_name in sorted(info['solutions'])[:3]:
                    solution_links.append(f"[{solution_name}](solutions/{sanitize_anchor(solution_name)}.md)")
                
                solutions_cell = ", ".join(solution_links)
                if num_solutions > 3:
                    solutions_cell += f" +{num_solutions - 3} more"
                
                # Create links to connectors
                connector_links = []
                for connector_id, connector_title in sorted(info['connectors'])[:5]:
                    connector_links.append(f"[{connector_title}](connectors/{sanitize_anchor(connector_id)}.md)")
                
                connectors_cell = ", ".join(connector_links)
                if len(info['connectors']) > 5:
                    connectors_cell += f" +{len(info['connectors']) - 5} more"
                
                f.write(f"| `{table}` | {solutions_cell} | {connectors_cell} |\n")
            
            f.write("\n")
    
    print(f"Generated tables index: {index_path}")


def generate_connector_pages(solutions: Dict[str, List[Dict[str, str]]], output_dir: Path) -> None:
    """Generate individual connector documentation pages."""
    
    connector_dir = output_dir / "connectors"
    connector_dir.mkdir(parents=True, exist_ok=True)
    
    # Group all data by connector_id
    by_connector: Dict[str, Dict[str, any]] = defaultdict(lambda: {
        'entries': [],
        'solutions': set(),
        'tables': set()
    })
    
    for solution_name, connectors in solutions.items():
        for conn in connectors:
            connector_id = conn.get('connector_id', '')
            # Skip entries with empty connector_id (solutions without connectors)
            if not connector_id.strip():
                continue
            by_connector[connector_id]['entries'].append(conn)
            by_connector[connector_id]['solutions'].add(solution_name)
            by_connector[connector_id]['tables'].add(conn.get('Table', ''))
    
    # Generate a page for each connector
    for connector_id, data in sorted(by_connector.items()):
        connector_path = connector_dir / f"{sanitize_anchor(connector_id)}.md"
        entries = data['entries']
        first_entry = entries[0]
        
        connector_title = first_entry.get('connector_title', connector_id)
        
        with connector_path.open("w", encoding="utf-8") as f:
            f.write(f"# {connector_title}\n\n")
            
            # Connector metadata table (no column headers)
            f.write("| | |\n")
            f.write("|----------|-------|\n")
            f.write(f"| **Connector ID** | `{connector_id}` |\n")
            
            publisher = first_entry.get('connector_publisher', '')
            if publisher:
                f.write(f"| **Publisher** | {publisher} |\n")
            
            # Tables
            tables_list = ", ".join([f"[`{table}`](../tables-index.md#{table.lower()})" for table in sorted(data['tables']) if table])
            f.write(f"| **Tables Ingested** | {tables_list} |\n")
            
            # Solutions
            solutions_list = ", ".join([f"[{solution_name}](../solutions/{sanitize_anchor(solution_name)}.md)" for solution_name in sorted(data['solutions'])])
            f.write(f"| **Used in Solutions** | {solutions_list} |\n")
            
            # Connector files
            connector_files = first_entry.get('connector_files', '')
            if connector_files:
                files = [f.strip() for f in connector_files.split(';') if f.strip()]
                if files:
                    files_list = ", ".join([f"[{file_url.split('/')[-1]}]({file_url})" for file_url in files])
                    f.write(f"| **Connector Definition Files** | {files_list} |\n")
            
            f.write("\n")
            
            # Description at the bottom
            description = first_entry.get('connector_description', '')
            if description:
                description = description.replace('<br>', '\n\n')
                f.write(f"{description}\n\n")
            
            # Back navigation
            f.write("[← Back to Connectors Index](../connectors-index.md)\n")
        
        print(f"Generated connector page: {connector_path}")


def generate_solution_page(solution_name: str, connectors: List[Dict[str, str]], output_dir: Path) -> None:
    """Generate individual solution documentation page."""
    
    solution_dir = output_dir / "solutions"
    solution_dir.mkdir(parents=True, exist_ok=True)
    
    solution_path = solution_dir / f"{sanitize_anchor(solution_name)}.md"
    
    # Get solution-level metadata from first connector entry
    metadata = connectors[0]
    
    # Check if this solution has any connectors (connector_id will be empty for all entries if not)
    has_connectors = any(bool(conn.get('connector_id', '').strip()) for conn in connectors)
    
    with solution_path.open("w", encoding="utf-8") as f:
        f.write(f"# {solution_name}\n\n")
        
        # Solution metadata section
        f.write("## Solution Information\n\n")
        f.write("| | |\n")
        f.write("|------------------------|-------|\n")
        f.write(f"| **Publisher** | {metadata.get('solution_support_name', 'N/A')} |\n")
        f.write(f"| **Support Tier** | {metadata.get('solution_support_tier', 'N/A')} |\n")
        
        support_link = metadata.get('solution_support_link', '')
        if support_link:
            f.write(f"| **Support Link** | [{support_link}]({support_link}) |\n")
        
        categories = metadata.get('solution_categories', '')
        if categories:
            f.write(f"| **Categories** | {categories} |\n")
        
        version = metadata.get('solution_version', '')
        if version:
            f.write(f"| **Version** | {version} |\n")
        
        author = metadata.get('solution_author_name', '')
        if author:
            f.write(f"| **Author** | {author} |\n")
        
        first_publish = metadata.get('solution_first_publish_date', '')
        if first_publish:
            f.write(f"| **First Published** | {first_publish} |\n")
        
        last_publish = metadata.get('solution_last_publish_date', '')
        if last_publish:
            f.write(f"| **Last Updated** | {last_publish} |\n")
        
        solution_folder = metadata.get('solution_folder', '')
        if solution_folder:
            f.write(f"| **Solution Folder** | [{solution_folder}]({solution_folder}) |\n")
        
        f.write("\n")
        
        # Only include connectors section if solution has connectors
        if not has_connectors:
            f.write("## Data Connectors\n\n")
            f.write("**This solution does not include data connectors.**\n\n")
            f.write("This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.\n\n")
        else:
            # Group by connector (filter out empty connector_ids from the row added for solutions without connectors)
            by_connector: Dict[str, List[Dict[str, str]]] = defaultdict(list)
            for conn in connectors:
                connector_id = conn.get('connector_id', '')
                if connector_id.strip():  # Only include non-empty connector_ids
                    by_connector[connector_id].append(conn)
            
            # Connectors section
            f.write("## Data Connectors\n\n")
            f.write(f"This solution provides **{len(by_connector)} data connector(s)**.\n\n")
            
            for connector_id in sorted(by_connector.keys()):
                conn_entries = by_connector[connector_id]
                first_conn = conn_entries[0]
                
                connector_title = first_conn.get('connector_title', connector_id)
                connector_link = f"[{connector_title}](../connectors/{sanitize_anchor(connector_id)}.md)"
                f.write(f"### {connector_link}\n\n")
                
                # Connector metadata
                publisher = first_conn.get('connector_publisher', '')
                if publisher:
                    f.write(f"**Publisher:** {publisher}\n\n")
                
            description = first_conn.get('connector_description', '')
            if description:
                # Replace <br> with newlines but preserve markdown formatting
                description = description.replace('<br>', '\n\n')
                f.write(f"{description}\n\n")
            
            # Combined table for Tables Ingested and Connector Definition Files
            tables = sorted(set(conn['Table'] for conn in conn_entries))
            connector_files = first_conn.get('connector_files', '')
            files = [f.strip() for f in connector_files.split(';') if f.strip()] if connector_files else []
            
            f.write("| | |\n")
            f.write("|--------------------------|---|\n")
            
            # Tables Ingested
            if len(tables) == 1:
                f.write(f"| **Tables Ingested** | `{tables[0]}` |\n")
            else:
                for i, table in enumerate(tables):
                    if i == 0:
                        f.write(f"| **Tables Ingested** | `{table}` |\n")
                    else:
                        f.write(f"| | `{table}` |\n")
            
            # Connector Definition Files
            if files:
                for i, file_url in enumerate(files):
                    file_name = file_url.split('/')[-1]
                    if i == 0:
                        f.write(f"| **Connector Definition Files** | [{file_name}]({file_url}) |\n")
                    else:
                        f.write(f"| | [{file_name}]({file_url}) |\n")
            
            f.write("\n")
            
            # Link to connector page
            f.write(f"[→ View full connector details](../connectors/{sanitize_anchor(connector_id)}.md)\n\n")
        
            # Tables summary section (only for solutions with connectors)
            all_tables = sorted(set(conn['Table'] for conn in connectors if conn.get('Table', '').strip()))
            if all_tables:
                f.write("## Tables Reference\n\n")
                f.write(f"This solution ingests data into **{len(all_tables)} table(s)**:\n\n")
                
                f.write("| Table | Used By Connectors |\n")
                f.write("|-------|-------------------|\n")
                
                for table in all_tables:
                    # Get connector info (id and title) for this table
                    table_connectors = []
                    for conn in connectors:
                        if conn.get('Table') == table:
                            connector_id = conn.get('connector_id', '')
                            connector_title = conn.get('connector_title', connector_id)
                            table_connectors.append((connector_id, connector_title))
                    
                    # Remove duplicates and sort by title
                    unique_connectors = sorted(set(table_connectors), key=lambda x: x[1])
                    
                    # Create links to connector pages
                    connector_links = [f"[{title}](../connectors/{sanitize_anchor(cid)}.md)" for cid, title in unique_connectors]
                    connector_list = ", ".join(connector_links)
                    
                    f.write(f"| `{table}` | {connector_list} |\n")
                
                f.write("\n")
        
        # Back navigation
        f.write("[← Back to Solutions Index](../solutions-index.md)\n")
    
    print(f"Generated solution page: {solution_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Microsoft Learn-style connector documentation from CSV"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).parent / "solutions_connectors_tables_mapping.csv",
        help="Path to input CSV file (default: solutions_connectors_tables_mapping.csv)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "connector-docs",
        help="Output directory for generated documentation (default: connector-docs/)",
    )
    parser.add_argument(
        "--solutions",
        nargs="*",
        help="Generate docs only for specific solutions (default: all solutions)",
    )
    
    args = parser.parse_args()
    
    if not args.input.exists():
        raise SystemExit(f"Input file not found: {args.input}")
    
    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read CSV
    print(f"Reading {args.input}...")
    with args.input.open("r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
    
    print(f"Loaded {len(rows)} rows")
    
    # Group by solution
    by_solution: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in rows:
        solution_name = row.get('solution_name', 'Unknown')
        by_solution[solution_name].append(row)
    
    # Filter solutions if specified
    if args.solutions:
        by_solution = {
            name: connectors
            for name, connectors in by_solution.items()
            if name in args.solutions
        }
        print(f"Filtered to {len(by_solution)} solution(s)")
    
    print(f"Generating documentation for {len(by_solution)} solution(s)...")
    
    # Generate index pages
    generate_index_page(by_solution, args.output_dir)
    generate_connectors_index(by_solution, args.output_dir)
    generate_tables_index(by_solution, args.output_dir)
    
    # Generate individual connector pages
    generate_connector_pages(by_solution, args.output_dir)
    
    # Generate individual solution pages
    for solution_name, connectors in sorted(by_solution.items()):
        generate_solution_page(solution_name, connectors, args.output_dir)
    
    # Count unique connectors
    all_connector_ids = set()
    for connectors in by_solution.values():
        for conn in connectors:
            connector_id = conn.get('connector_id', '')
            if connector_id:
                all_connector_ids.add(connector_id)
    
    print(f"\nDocumentation generated successfully in: {args.output_dir}")
    print(f"  - Solutions index: {args.output_dir / 'solutions-index.md'}")
    print(f"  - Connectors index: {args.output_dir / 'connectors-index.md'}")
    print(f"  - Tables index: {args.output_dir / 'tables-index.md'}")
    print(f"  - Solutions: {args.output_dir / 'solutions'}/ ({len(by_solution)} files)")
    print(f"  - Connectors: {args.output_dir / 'connectors'}/ ({len(all_connector_ids)} files)")


if __name__ == "__main__":
    main()
