"""
Generate Microsoft Learn-style connector documentation from CSV.

Creates markdown documentation organized by solution, mimicking the structure
of https://learn.microsoft.com/en-us/azure/sentinel/data-connectors-reference
"""

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import argparse
from urllib.parse import quote
import json
import re
import subprocess
import sys


# Default Solutions directory path (relative to this script)
DEFAULT_SOLUTIONS_DIR = Path(__file__).parent.parent.parent / "Solutions"

# Global set tracking internal tables (tables with category="Internal" in tables.csv)
# Internal tables are written AND read by the same solution for internal data storage
INTERNAL_TABLES: Set[str] = set()


def sanitize_anchor(text: str) -> str:
    """Convert text to URL-safe anchor."""
    return text.lower().replace(" ", "-").replace("/", "-").replace("_", "-")


def sanitize_filename(text: str) -> str:
    """Convert text to URL-safe filename, encoding special characters that break Markdown links."""
    result = text.lower().replace(" ", "-").replace("/", "-").replace("_", "-")
    # URL-encode parentheses to avoid breaking Markdown link syntax
    result = result.replace("(", "%28").replace(")", "%29")
    return result


def get_content_key(content_id: str, content_name: str, solution_name: str) -> str:
    """
    Generate a unique key for content items.
    Uses content_id if available, otherwise falls back to content_name + solution_name.
    This handles cases where content_id is empty (e.g., workbooks, playbooks).
    """
    if content_id:
        return content_id
    # Fallback: use content_name + solution_name as composite key
    return f"{content_name}::{solution_name}"


def format_tactics(tactics: str) -> str:
    """
    Format a tactics string with spaces after commas for better wrapping in tables.
    """
    if not tactics or tactics == '-':
        return '-'
    # Split by comma, strip whitespace, and rejoin with comma-space
    return ', '.join(t.strip() for t in tactics.split(',') if t.strip())


# Mapping from content type to possible folder names in the Solutions directory
CONTENT_TYPE_FOLDER_MAP = {
    'analytic_rule': ['Analytic Rules', 'Analytical Rules', 'Analytics Rules'],
    'hunting_query': ['Hunting Queries'],
    'workbook': ['Workbooks', 'Workbook'],
    'playbook': ['Playbooks', 'Playbook'],
    'parser': ['Parsers', 'Parser'],
    'watchlist': ['Watchlists'],
}


def get_content_item_github_url(item: Dict[str, str]) -> Optional[str]:
    """
    Build GitHub URL for a content item file.
    
    Args:
        item: Content item dictionary with solution_folder, content_type, content_file
    
    Returns:
        GitHub URL string or None if not enough information
    """
    solution_folder = item.get('solution_folder', '')
    content_type = item.get('content_type', '')
    content_file = item.get('content_file', '')
    
    if not solution_folder or not content_file:
        return None
    
    # Get the folder name for this content type (use first variant as default)
    folder_variants = CONTENT_TYPE_FOLDER_MAP.get(content_type, [])
    if not folder_variants:
        return None
    
    # Use the first folder variant - it's the most common
    folder_name = folder_variants[0]
    
    # Build the GitHub URL - URL encode the path components
    # Keep slashes in content_file since it may include subdirectory paths
    base_url = "https://github.com/Azure/Azure-Sentinel/blob/master/Solutions"
    encoded_solution = quote(solution_folder, safe='')
    encoded_folder = quote(folder_name, safe='')
    encoded_file = quote(content_file, safe='/')
    
    return f"{base_url}/{encoded_solution}/{encoded_folder}/{encoded_file}"


def format_table_link(table_name: str, relative_path: str = "../tables/") -> str:
    """
    Format a table name as a markdown link to its table page.
    
    Args:
        table_name: The name of the table
        relative_path: Relative path to tables directory (default: ../tables/)
    
    Returns:
        Markdown formatted link like [`TableName`](../tables/tablename.md)
    """
    table_filename = sanitize_filename(table_name) + ".md"
    return f"[`{table_name}`]({relative_path}{table_filename})"


def format_tables_with_links(tables: List[str], relative_path: str = "../tables/") -> str:
    """
    Format a list of table names as line-separated markdown links.
    
    Args:
        tables: List of table names
        relative_path: Relative path to tables directory
    
    Returns:
        Line-separated markdown links using HTML br tags, or '-' if no tables
    """
    if not tables:
        return '-'
    return '<br>'.join(format_table_link(t, relative_path) for t in sorted(tables))


def format_tables_with_usage(tables_with_usage: List[Tuple[str, str]], relative_path: str = "../tables/") -> str:
    """
    Format a list of (table_name, usage) tuples as line-separated markdown links with usage indicators.
    Separates internal tables (written to by playbooks) from regular tables.
    
    Args:
        tables_with_usage: List of (table_name, usage) tuples where usage is 'read', 'write', or 'read/write'
        relative_path: Relative path to tables directory
    
    Returns:
        Line-separated markdown links with usage indicators and internal tables listed separately, or '-' if no tables
    """
    if not tables_with_usage:
        return '-'
    
    # Separate internal and regular tables
    regular_tables = [(t, u) for t, u in tables_with_usage if t not in INTERNAL_TABLES]
    internal_tables = [(t, u) for t, u in tables_with_usage if t in INTERNAL_TABLES]
    
    def format_with_usage(table_name: str, usage: str) -> str:
        link = format_table_link(table_name, relative_path)
        if usage == 'read':
            return f"{link} *(read)*"
        elif usage == 'write':
            return f"{link} *(write)*"
        elif usage == 'read/write':
            return f"{link} *(read/write)*"
        return link
    
    result_parts = []
    
    # Regular tables first
    for table_name, usage in sorted(regular_tables, key=lambda x: x[0]):
        result_parts.append(format_with_usage(table_name, usage))
    
    # Internal tables with prefix
    if internal_tables:
        result_parts.append("*Internal use:*")
        for table_name, usage in sorted(internal_tables, key=lambda x: x[0]):
            result_parts.append(format_with_usage(table_name, usage))
    
    return '<br>'.join(result_parts) if result_parts else '-'


def format_tables_simple(tables_with_usage: List[Tuple[str, str]], relative_path: str = "../tables/") -> str:
    """
    Format a list of (table_name, usage) tuples as line-separated markdown links WITHOUT usage indicators.
    Separates internal tables (written to by playbooks) from regular tables.
    
    Args:
        tables_with_usage: List of (table_name, usage) tuples - usage is ignored
        relative_path: Relative path to tables directory
    
    Returns:
        Line-separated markdown links with internal tables listed separately, or '-' if no tables
    """
    if not tables_with_usage:
        return '-'
    
    # Separate internal and regular tables
    table_names = sorted(set(t[0] for t in tables_with_usage))
    regular_tables = [t for t in table_names if t not in INTERNAL_TABLES]
    internal_tables = [t for t in table_names if t in INTERNAL_TABLES]
    
    result_parts = []
    
    # Regular tables first
    if regular_tables:
        result_parts.extend(format_table_link(t, relative_path) for t in regular_tables)
    
    # Internal tables with prefix
    if internal_tables:
        result_parts.append("*Internal use:*")
        result_parts.extend(format_table_link(t, relative_path) for t in internal_tables)
    
    return '<br>'.join(result_parts) if result_parts else '-'


def get_release_notes(solution_name: str, solutions_dir: Path) -> Optional[str]:
    """
    Read ReleaseNotes.md from a solution directory if it exists.
    
    Args:
        solution_name: Name of the solution folder
        solutions_dir: Path to the Solutions directory
    
    Returns:
        Content of ReleaseNotes.md or None if not found
    """
    release_notes_path = solutions_dir / solution_name / "ReleaseNotes.md"
    if release_notes_path.exists():
        try:
            return release_notes_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"  Warning: Could not read {release_notes_path}: {e}")
    return None


def get_solution_readme(solution_name: str, solutions_dir: Path) -> Tuple[Optional[str], Optional[str]]:
    """
    Read README.md from a solution directory if it exists.
    
    Args:
        solution_name: Name of the solution folder
        solutions_dir: Path to the Solutions directory
    
    Returns:
        Tuple of (readme_content, github_url) or (None, None) if not found
    """
    solution_dir = solutions_dir / solution_name
    
    # Try common README filename variations (case-insensitive on Windows)
    for readme_name in ['README.md', 'readme.md', 'Readme.md']:
        readme_path = solution_dir / readme_name
        if readme_path.exists():
            try:
                content = readme_path.read_text(encoding='utf-8')
                github_url = f"https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/{solution_name}/{readme_name}"
                return content, github_url
            except Exception as e:
                print(f"  Warning: Could not read {readme_path}: {e}")
    return None, None


# Folders to exclude when searching for documentation files
EXCLUDED_FOLDERS = {
    '.python_packages', 'node_modules', '__pycache__', '.venv', 'venv', 
    'site-packages', 'dist-info', 'egg-info', '.git', '.vs', 'bin', 'obj'
}

# Files to exclude (non-documentation markdown files)
EXCLUDED_FILES = {
    'license', 'licence', 'copying', 'notice', 'authors', 'contributors',
    'history', 'news', 'todo', 'metadata'
}


def is_valid_doc_file(md_file: Path) -> bool:
    """
    Check if a markdown file is a valid documentation file.
    Excludes files in package/dependency folders and non-documentation files.
    """
    # Check if any parent folder is in the excluded list
    for parent in md_file.parents:
        if parent.name.lower() in EXCLUDED_FOLDERS or parent.name.endswith('.dist-info') or parent.name.endswith('.egg-info'):
            return False
    
    # Check if the file itself is a non-documentation file
    if md_file.stem.lower() in EXCLUDED_FILES:
        return False
    
    return True


def get_connector_readme(solution_name: str, connector_id: str, connector_files: str, 
                         solutions_dir: Path) -> Tuple[Optional[str], Optional[str]]:
    """
    Find and read documentation markdown file associated with a connector.
    
    Association rules:
    1. If connector has a dedicated subfolder with .md files (e.g., Data Connectors/ConnectorName/*.md)
    2. .md file with connector name in filename anywhere in Data Connectors folder
    3. If solution has only one connector, any .md file in Data Connectors folder (handled by caller)
    
    Args:
        solution_name: Name of the solution folder
        connector_id: The connector identifier
        connector_files: Semicolon-separated list of connector definition file URLs
        solutions_dir: Path to the Solutions directory
    
    Returns:
        Tuple of (readme_content, readme_path) or (None, None) if not found
    """
    solution_path = solutions_dir / solution_name
    if not solution_path.exists():
        return None, None
    
    # Find the Data Connectors folder (with various naming conventions)
    data_connector_folders = []
    for folder in solution_path.iterdir():
        if folder.is_dir() and ('data' in folder.name.lower() and 'connector' in folder.name.lower()):
            data_connector_folders.append(folder)
    
    if not data_connector_folders:
        return None, None
    
    # Parse connector file paths to find the connector's folder
    connector_folder_name = None
    connector_json_folder = None
    if connector_files:
        for file_url in connector_files.split(';'):
            file_url = file_url.strip()
            if not file_url:
                continue
            # Extract path after solution name
            # URL format: .../Solutions/{solution}/Data Connectors/{subfolder}/file.json
            parts = file_url.split('/')
            try:
                dc_idx = None
                for i, part in enumerate(parts):
                    if 'data' in part.lower() and 'connector' in part.lower():
                        dc_idx = i
                        break
                if dc_idx is not None and dc_idx + 1 < len(parts):
                    next_part = parts[dc_idx + 1]
                    # Check if this is a subfolder (not a JSON file)
                    if not next_part.endswith('.json'):
                        connector_folder_name = next_part
                        connector_json_folder = "/".join(parts[dc_idx:dc_idx+2])
            except (IndexError, ValueError):
                pass
    
    # Strategy 1: Look for any .md file in connector's dedicated subfolder
    for dc_folder in data_connector_folders:
        if connector_folder_name:
            connector_subfolder = dc_folder / connector_folder_name
            if connector_subfolder.exists() and connector_subfolder.is_dir():
                # Find all .md files in the subfolder (excluding package folders)
                md_files = [f for f in connector_subfolder.glob('*.md') if is_valid_doc_file(f)]
                if md_files:
                    # Prefer README.md if it exists, otherwise use the first .md file
                    readme_file = None
                    for md_file in md_files:
                        if md_file.stem.lower() == 'readme':
                            readme_file = md_file
                            break
                    if readme_file is None:
                        readme_file = md_files[0]
                    try:
                        content = readme_file.read_text(encoding='utf-8')
                        rel_path = str(readme_file.relative_to(solutions_dir))
                        return content, rel_path
                    except Exception:
                        pass
    
    # Strategy 2: Look for README with connector name in filename
    for dc_folder in data_connector_folders:
        # Look for files like ConnectorName_README.md or ConnectorName.md
        connector_id_lower = connector_id.lower()
        for md_file in dc_folder.glob('**/*.md'):
            if not is_valid_doc_file(md_file):
                continue
            file_stem_lower = md_file.stem.lower()
            if connector_id_lower in file_stem_lower or file_stem_lower in connector_id_lower:
                try:
                    content = md_file.read_text(encoding='utf-8')
                    rel_path = str(md_file.relative_to(solutions_dir))
                    return content, rel_path
                except Exception:
                    pass
    
    # Strategy 3: If only one connector in solution, use README in Data Connectors folder
    # We'll check this in the caller where we have access to all connectors for a solution
    
    return None, None


def get_single_connector_readme(solution_name: str, solutions_dir: Path) -> Tuple[Optional[str], Optional[str]]:
    """
    Get documentation .md file from Data Connectors folder when solution has only one connector.
    Prefers README.md if it exists, otherwise uses the first .md file found.
    
    Args:
        solution_name: Name of the solution folder
        solutions_dir: Path to the Solutions directory
    
    Returns:
        Tuple of (readme_content, readme_path) or (None, None) if not found
    """
    solution_path = solutions_dir / solution_name
    if not solution_path.exists():
        return None, None
    
    # Find the Data Connectors folder
    for folder in solution_path.iterdir():
        if folder.is_dir() and ('data' in folder.name.lower() and 'connector' in folder.name.lower()):
            # Look for any .md file directly in Data Connectors folder (excluding package folders)
            md_files = [f for f in folder.glob('*.md') if is_valid_doc_file(f)]
            if md_files:
                # Prefer README.md if it exists, otherwise use the first .md file
                readme_file = None
                for md_file in md_files:
                    if md_file.stem.lower() == 'readme':
                        readme_file = md_file
                        break
                if readme_file is None:
                    readme_file = md_files[0]
                try:
                    content = readme_file.read_text(encoding='utf-8')
                    rel_path = str(readme_file.relative_to(solutions_dir))
                    return content, rel_path
                except Exception:
                    pass
    
    return None, None


def format_instruction_steps(instruction_steps: str) -> str:
    """
    Parse and format instruction steps from CSV field.
    
    The instruction_steps field contains escaped JSON representing the instructionSteps array.
    This function parses the JSON and formats it as markdown.
    """
    if not instruction_steps:
        return ""
    
    try:
        # Parse the JSON string
        steps_data = json.loads(instruction_steps)
    except (json.JSONDecodeError, TypeError):
        # Fallback for old format (already formatted string with <br> tags)
        formatted = instruction_steps.replace('<br>', '\n')
        formatted = re.sub(r'\n{3,}', '\n\n', formatted)
        formatted = re.sub(r'/\*\s*Lines\s+\d+-\d+\s+omitted\s*\*/', '', formatted)
        return formatted.strip()
    
    # Format the instruction steps recursively
    return _format_instruction_steps_recursive(steps_data, indent_level=0)


def _format_data_connectors_grid(parameters: Dict[str, Any], indent: str = "") -> str:
    """Format DataConnectorsGrid instruction type with clear explanation."""
    mapping = parameters.get("mapping", [])
    menu_items = parameters.get("menuItems", [])
    
    lines = [
        f"{indent}**Connector Management Interface**\n\n",
        f"{indent}This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.\n\n"
    ]
    
    if mapping:
        lines.append(f"{indent}📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:\n")
        for col in mapping:
            col_name = col.get("columnName", "")
            if col_name:
                lines.append(f"{indent}- **{col_name}**\n")
        lines.append("\n")
    
    lines.append(f"{indent}➕ **Add New Collector**: Click the \"Add new collector\" button to configure a new data collector (see configuration form below).\n\n")
    
    if "DeleteConnector" in menu_items or "EditConnector" in menu_items:
        lines.append(f"{indent}🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.\n\n")
    
    lines.append(f"{indent}> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.\n\n")
    
    return "".join(lines)


def _format_context_pane(parameters: Dict[str, Any], indent: str = "") -> str:
    """Format ContextPane instruction type with detailed form field explanation."""
    title = parameters.get("title", "Configuration Form")
    subtitle = parameters.get("subtitle", "")
    label = parameters.get("label", "Add new collector")
    instruction_steps = parameters.get("instructionSteps", [])
    
    lines = [
        f"{indent}**{title}**\n\n",
    ]
    
    if subtitle:
        lines.append(f"{indent}*{subtitle}*\n\n")
    
    lines.append(f"{indent}When you click the \"{label}\" button in the portal, a configuration form will open. You'll need to provide:\n\n")
    
    # Process instruction steps to show what fields are required
    if instruction_steps:
        for step in instruction_steps:
            step_title = step.get("title", "")
            step_instructions = step.get("instructions", [])
            
            if step_title:
                lines.append(f"{indent}*{step_title}*\n\n")
            
            for instruction in step_instructions:
                if not isinstance(instruction, dict):
                    continue
                
                instr_type = instruction.get("type", "")
                params = instruction.get("parameters", {})
                
                if instr_type == "Textbox":
                    label_text = params.get("label", "")
                    placeholder = params.get("placeholder", "")
                    required = params.get("validations", {}).get("required", False)
                    req_marker = " (required)" if required else " (optional)"
                    
                    if label_text:
                        lines.append(f"{indent}- **{label_text}**{req_marker}")
                        if placeholder:
                            lines.append(f": {placeholder}")
                        lines.append("\n")
                
                elif instr_type == "Dropdown":
                    label_text = params.get("label", "")
                    options = params.get("options", [])
                    required = params.get("required", False)
                    req_marker = " (required)" if required else " (optional)"
                    
                    if label_text:
                        lines.append(f"{indent}- **{label_text}**{req_marker}: Select from available options\n")
                        if options:
                            for opt in options[:5]:  # Show first 5 options
                                opt_text = opt.get('text', opt.get('key', ''))
                                if opt_text:
                                    lines.append(f"{indent}  - {opt_text}\n")
                            if len(options) > 5:
                                lines.append(f"{indent}  - ... and {len(options) - 5} more options\n")
                
                elif instr_type == "Markdown":
                    content = params.get("content", "")
                    if content:
                        lines.append(f"{indent}{content}\n\n")
        
        lines.append("\n")
    
    lines.append(f"{indent}> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.\n\n")
    
    return "".join(lines)


def _format_gcp_grid(parameters: Dict[str, Any], indent: str = "") -> str:
    """Format GCPGrid instruction type."""
    lines = [
        f"{indent}**GCP Collector Management**\n\n",
        f"{indent}📊 **View GCP Collectors**: A management interface displays your configured Google Cloud Platform data collectors.\n\n",
        f"{indent}➕ **Add New Collector**: Click \"Add new collector\" to configure a new GCP data connection.\n\n",
        f"{indent}> 💡 **Portal-Only Feature**: This configuration interface is only available in the Microsoft Sentinel portal.\n\n"
    ]
    return "".join(lines)


def _format_gcp_context_pane(parameters: Dict[str, Any], indent: str = "") -> str:
    """Format GCPContextPane instruction type."""
    lines = [
        f"{indent}**GCP Connection Configuration**\n\n",
        f"{indent}When you click \"Add new collector\" in the portal, you'll be prompted to provide:\n",
        f"{indent}- **Project ID**: Your Google Cloud Platform project ID\n",
        f"{indent}- **Service Account**: GCP service account credentials with appropriate permissions\n",
        f"{indent}- **Subscription**: The Pub/Sub subscription to monitor for log data\n\n",
        f"{indent}> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.\n\n"
    ]
    return "".join(lines)


def _format_data_type_selector(instr_type: str, parameters: Dict[str, Any], indent: str = "") -> str:
    """Format data type selector instruction types (AADDataTypes, MCasDataTypes, OfficeDataTypes)."""
    data_types = parameters.get("dataTypes", [])
    
    type_names = {
        "AADDataTypes": "Microsoft Entra ID",
        "MCasDataTypes": "Microsoft Defender for Cloud Apps",
        "OfficeDataTypes": "Microsoft 365"
    }
    
    type_name = type_names.get(instr_type, "Data")
    
    lines = [
        f"{indent}**Select {type_name} Data Types**\n\n",
        f"{indent}In the Microsoft Sentinel portal, select which data types to enable:\n\n"
    ]
    
    if data_types:
        for dt in data_types:
            if isinstance(dt, dict):
                dt_name = dt.get("name", "")
                dt_title = dt.get("title", dt_name)
                if dt_title:
                    lines.append(f"{indent}- ☐ **{dt_title}**\n")
                    
                    # Add info box if available
                    info_html = dt.get("infoBoxHtmlTemplate", "")
                    if info_html and len(info_html) < 200:
                        # Strip HTML tags for simple display
                        info_text = re.sub(r'<[^>]+>', '', info_html).strip()
                        if info_text:
                            lines.append(f"{indent}  *{info_text}*\n")
        lines.append("\n")
    
    lines.append(f"{indent}Each data type may have specific licensing requirements. Review the information provided for each type in the portal before enabling.\n\n")
    lines.append(f"{indent}> 💡 **Portal-Only Feature**: Data type selection is only available in the Microsoft Sentinel portal.\n\n")
    
    return "".join(lines)


def _format_instruction_steps_recursive(instruction_steps: Any, indent_level: int = 0) -> str:
    """
    Recursively format instructionSteps array to markdown.
    
    Args:
        instruction_steps: List of instruction step objects
        indent_level: Current nesting level for indentation (0 = top level)
    
    Returns:
        Formatted markdown string
    """
    if not isinstance(instruction_steps, list):
        return ""
    
    lines = []
    step_num = 0
    indent = "  " * indent_level  # 2 spaces per level
    
    for step in instruction_steps:
        if not isinstance(step, dict):
            continue
        
        title = step.get("title", "") or ""
        description = step.get("description", "") or ""
        title = title.strip() if isinstance(title, str) else ""
        description = description.strip() if isinstance(description, str) else ""
        instructions = step.get("instructions", [])
        inner_steps = step.get("innerSteps", [])
        
        # Skip empty steps unless they have instructions or innerSteps
        if not title and not description and not instructions and not inner_steps:
            continue
        
        # Check if title already starts with a number (to avoid duplicate numbering)
        title_has_number = bool(title and re.match(r'^\d+\.', title))
        
        # Only increment step number if there's substantial content and title doesn't already have a number
        if (title or (description and not description.startswith(">"))) and not title_has_number:
            step_num += 1
        
        # Format the step with indentation
        if title and description:
            if indent_level == 0:
                if title_has_number:
                    lines.append(f"**{title}**\n\n{description}\n")
                else:
                    lines.append(f"**{step_num}. {title}**\n\n{description}\n")
            else:
                lines.append(f"{indent}**{title}**\n\n{indent}{description}\n")
        elif title:
            if indent_level == 0:
                if title_has_number:
                    lines.append(f"**{title}**\n")
                else:
                    lines.append(f"**{step_num}. {title}**\n")
            else:
                lines.append(f"{indent}**{title}**\n")
        elif description:
            # For notes without titles (usually start with >)
            lines.append(f"{indent}{description}\n")
        
        # Process instructions array if present (UI elements like CopyableLabel)
        if isinstance(instructions, list):
            for instruction in instructions:
                if not isinstance(instruction, dict):
                    continue
                
                instr_type = instruction.get("type", "")
                parameters = instruction.get("parameters", {})
                
                # Handle different instruction types
                if instr_type == "CopyableLabel" and isinstance(parameters, dict):
                    label = parameters.get("label", "")
                    # Check for both fillWith (array) and value (string) patterns
                    fill_with = parameters.get("fillWith", [])
                    value = parameters.get("value", "")
                    if label:
                        if value:
                            # Use direct value if present
                            fill_value = value
                            lines.append(f"{indent}- **{label}**: `{fill_value}`\n")
                        elif fill_with:
                            # Use first element from fillWith array
                            fill_value = fill_with[0] if isinstance(fill_with, list) and fill_with else ""
                            lines.append(f"{indent}- **{label}**: `{fill_value}`\n")
                            lines.append(f"{indent}  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*\n")
                        else:
                            lines.append(f"{indent}- **{label}**\n")
                
                elif instr_type == "InfoMessage" and isinstance(parameters, dict):
                    # InfoMessage: inline information message
                    # Parameters: text, visible, inline
                    text = parameters.get("text", "")
                    inline = parameters.get("inline", True)
                    visible = parameters.get("visible", True)
                    if text and visible:
                        lines.append(f"\n{indent}ℹ️ {text}\n")
                
                elif instr_type == "Markdown" and isinstance(parameters, dict):
                    # Markdown: displays formatted markdown text
                    # Parameters: content
                    content = parameters.get("content", "")
                    if content:
                        lines.append(f"{indent}{content}\n")
                
                elif instr_type == "MarkdownControlEnvBased" and isinstance(parameters, dict):
                    # Environment-based markdown (prod/gov scripts)
                    prod_script = parameters.get("prodScript", "")
                    gov_script = parameters.get("govScript", "")
                    if prod_script:
                        lines.append(f"{indent}{prod_script}\n")
                    if gov_script and gov_script != prod_script:
                        lines.append(f"{indent}\n**Government Cloud:**\n{indent}{gov_script}\n")
                
                elif instr_type == "Textbox" and isinstance(parameters, dict):
                    # Textbox: input field for text, password, number, or email
                    # Parameters: label, placeholder, type, name, validations
                    label = parameters.get("label", "")
                    placeholder = parameters.get("placeholder", "")
                    text_type = parameters.get("type", "text")
                    if label:
                        if text_type == "password":
                            lines.append(f"{indent}- **{label}**: (password field)\n")
                        elif placeholder:
                            lines.append(f"{indent}- **{label}**: {placeholder}\n")
                        else:
                            lines.append(f"{indent}- **{label}**\n")
                
                elif instr_type == "OAuthForm" and isinstance(parameters, dict):
                    # OAuthForm: OAuth connection form
                    # Parameters: clientIdLabel, clientSecretLabel, connectButtonLabel, disconnectButtonLabel
                    client_id_label = parameters.get("clientIdLabel", "Client ID")
                    client_secret_label = parameters.get("clientSecretLabel", "Client Secret")
                    connect_label = parameters.get("connectButtonLabel", "Connect")
                    lines.append(f"{indent}- **OAuth Configuration**:\n")
                    lines.append(f"{indent}  - {client_id_label}\n")
                    lines.append(f"{indent}  - {client_secret_label}\n")
                    lines.append(f"{indent}  - Click '{connect_label}' to authenticate\n")
                
                elif instr_type == "Dropdown" and isinstance(parameters, dict):
                    # Dropdown: dropdown selection list
                    # Parameters: label, name, options, placeholder, isMultiSelect, required, defaultAllSelected
                    label = parameters.get("label", "")
                    options = parameters.get("options", [])
                    is_multi = parameters.get("isMultiSelect", False)
                    if label:
                        select_type = "multi-select" if is_multi else "select"
                        lines.append(f"{indent}- **{label}** ({select_type})\n")
                        if options and isinstance(options, list):
                            for opt in options[:5]:  # Show first 5 options
                                if isinstance(opt, dict):
                                    opt_text = opt.get("text", opt.get("key", ""))
                                    if opt_text:
                                        lines.append(f"{indent}  - {opt_text}\n")
                            if len(options) > 5:
                                lines.append(f"{indent}  - ... and {len(options) - 5} more options\n")
                
                elif instr_type == "InstallAgent" and isinstance(parameters, dict):
                    # InstallAgent: displays link to Azure portal sections for installation
                    # Parameters: linkType, policyDefinitionGuid, assignMode, dataCollectionRuleType
                    link_type = parameters.get("linkType", "")
                    if link_type:
                        # Map technical linkType names to user-friendly descriptions
                        link_descriptions = {
                            "InstallAgentOnWindowsVirtualMachine": "Install agent on Windows Virtual Machine",
                            "InstallAgentOnWindowsNonAzure": "Install agent on Windows (Non-Azure)",
                            "InstallAgentOnLinuxVirtualMachine": "Install agent on Linux Virtual Machine",
                            "InstallAgentOnLinuxNonAzure": "Install agent on Linux (Non-Azure)",
                            "OpenSyslogSettings": "Open Syslog settings",
                            "OpenCustomLogsSettings": "Open custom logs settings",
                            "OpenWaf": "Configure Web Application Firewall",
                            "OpenAzureFirewall": "Configure Azure Firewall",
                            "OpenMicrosoftAzureMonitoring": "Open Azure Monitoring",
                            "OpenFrontDoors": "Configure Azure Front Door",
                            "OpenCdnProfile": "Configure CDN Profile",
                            "AutomaticDeploymentCEF": "Automatic CEF deployment",
                            "OpenAzureInformationProtection": "Configure Azure Information Protection",
                            "OpenAzureActivityLog": "Configure Azure Activity Log",
                            "OpenIotPricingModel": "Configure IoT pricing",
                            "OpenPolicyAssignment": "Configure policy assignment",
                            "OpenAllAssignmentsBlade": "View all assignments",
                            "OpenCreateDataCollectionRule": "Create data collection rule"
                        }
                        description = link_descriptions.get(link_type, f"Install/configure: {link_type}")
                        lines.append(f"{indent}- **{description}**\n")
                
                elif instr_type == "ConnectionToggleButton" and isinstance(parameters, dict):
                    # ConnectionToggleButton: toggle button to connect/disconnect
                    # Parameters: connectLabel, disconnectLabel, name, disabled, isPrimary
                    connect_label = parameters.get("connectLabel", "Connect")
                    disconnect_label = parameters.get("disconnectLabel", "Disconnect")
                    lines.append(f"{indent}- Click '{connect_label}' to establish connection\n")
                
                elif instr_type == "InstructionStepsGroup" and isinstance(parameters, dict):
                    # InstructionStepsGroup: collapsible group of instructions
                    # Parameters: title, description, instructionSteps, canCollapseAllSections, expanded
                    group_title = parameters.get("title", "")
                    group_description = parameters.get("description", "")
                    group_steps = parameters.get("instructionSteps", [])
                    can_collapse = parameters.get("canCollapseAllSections", False)
                    
                    if group_title:
                        collapse_indicator = " (expandable)" if can_collapse else ""
                        lines.append(f"{indent}**{group_title}{collapse_indicator}**\n\n")
                    if group_description:
                        lines.append(f"{indent}{group_description}\n\n")
                    if group_steps:
                        nested_content = _format_instruction_steps_recursive(group_steps, indent_level + 1)
                        if nested_content:
                            lines.append(nested_content + "\n")
                
                elif instr_type == "ConfigureLogSettings" and isinstance(parameters, dict):
                    link_type = parameters.get("linkType", "")
                    lines.append(f"{indent}- Configure log settings: {link_type}\n")
                
                elif instr_type == "MSG" and isinstance(parameters, dict):
                    # Microsoft Security Graph items
                    msg_description = parameters.get("description", "")
                    items = parameters.get("items", [])
                    if msg_description:
                        lines.append(f"{indent}{msg_description}\n")
                    if items:
                        for item in items:
                            if isinstance(item, dict):
                                label = item.get("label", "")
                                if label:
                                    lines.append(f"{indent}  - {label}\n")
                
                elif instr_type in ["SecurityEvents", "WindowsSecurityEvents", "WindowsForwardedEvents", 
                                   "WindowsFirewallAma", "SysLogAma", "CefAma", "CiscoAsaAma"]:
                    # Data connector configuration types
                    lines.append(f"{indent}- Configure {instr_type} data connector\n")
                
                elif instr_type == "OmsDatasource" and isinstance(parameters, dict):
                    datasource = parameters.get("datasourceName", "")
                    if datasource:
                        lines.append(f"{indent}- Configure data source: {datasource}\n")
                
                elif instr_type == "OmsSolutions" and isinstance(parameters, dict):
                    solution = parameters.get("solutionName", "")
                    if solution:
                        lines.append(f"{indent}- Install solution: {solution}\n")
                
                elif instr_type == "SentinelResourceProvider" and isinstance(parameters, dict):
                    connector_kind = parameters.get("connectorKind", "")
                    title = parameters.get("title", connector_kind)
                    if title:
                        lines.append(f"{indent}- Connect {title}\n")
                
                elif instr_type == "DeployPushConnectorButton_test" and isinstance(parameters, dict):
                    label = parameters.get("label", "Deploy connector")
                    app_name = parameters.get("applicationDisplayName", "")
                    if label:
                        lines.append(f"{indent}- {label}\n")
                    if app_name:
                        lines.append(f"{indent}  Application: {app_name}\n")
                
                # UI-centric instruction types
                elif instr_type == "DataConnectorsGrid" and isinstance(parameters, dict):
                    # DataConnectorsGrid: displays a grid of data connectors
                    # Parameters: mapping, menuItems
                    lines.append(_format_data_connectors_grid(parameters, indent))
                
                elif instr_type == "ContextPane" and isinstance(parameters, dict):
                    # ContextPane: displays a contextual information pane
                    # Parameters: title, subtitle, contextPaneType, instructionSteps, label, isPrimary
                    lines.append(_format_context_pane(parameters, indent))
                
                elif instr_type == "GCPGrid":
                    # GCP-specific grid display
                    lines.append(_format_gcp_grid(parameters if isinstance(parameters, dict) else {}, indent))
                
                elif instr_type == "GCPContextPane":
                    # GCP-specific context pane
                    lines.append(_format_gcp_context_pane(parameters if isinstance(parameters, dict) else {}, indent))
                
                elif instr_type in ["AADDataTypes", "MCasDataTypes", "OfficeDataTypes"] and isinstance(parameters, dict):
                    # Data type selector for Microsoft services
                    lines.append(_format_data_type_selector(instr_type, parameters, indent))
                
                # For any other types, show basic info if available
                elif instr_type:
                    # For types we haven't explicitly handled, try to extract useful information
                    if isinstance(parameters, dict):
                        # Try to find useful text fields in order of preference
                        useful_text = None
                        for key in ['text', 'content', 'description', 'label', 'title', 'message']:
                            if key in parameters and isinstance(parameters[key], str) and parameters[key].strip():
                                useful_text = parameters[key].strip()
                                break
                        
                        if useful_text:
                            # Found useful text, display it
                            lines.append(f"{indent}{useful_text}\n")
                        else:
                            # No useful text found, provide a generic note
                            lines.append(f"{indent}> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `{instr_type}`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.\n")
        
        # Recursively process innerSteps if present (nested sub-steps)
        if isinstance(inner_steps, list) and inner_steps:
            inner_content = _format_instruction_steps_recursive(inner_steps, indent_level + 1)
            if inner_content:
                lines.append(inner_content)
        
        lines.append("\n")
    
    return "".join(lines).strip()


def format_permissions(permissions_json: str) -> str:
    """
    Parse and format permissions from JSON-encoded CSV field.
    
    Renders permissions based on the official Microsoft Sentinel data connector UI definitions:
    https://learn.microsoft.com/en-us/azure/sentinel/data-connector-ui-definitions-reference#permissions
    
    Args:
        permissions_json: JSON-encoded permissions object from CSV
        
    Returns:
        Formatted markdown string with permissions
    """
    if not permissions_json:
        return ""
    
    try:
        permissions = json.loads(permissions_json)
    except json.JSONDecodeError:
        # If it's not JSON, return as-is (backward compatibility)
        return permissions_json.replace('<br>', '\n').strip()
    
    if not isinstance(permissions, dict):
        return ""
    
    lines = []
    
    # Resource Provider permissions
    resource_providers = permissions.get("resourceProvider", [])
    if isinstance(resource_providers, list) and resource_providers:
        lines.append("**Resource Provider Permissions:**\n")
        for rp in resource_providers:
            if not isinstance(rp, dict):
                continue
            
            provider = rp.get("provider", "")
            provider_display = rp.get("providerDisplayName", "")
            scope = rp.get("scope", "Workspace")
            perms_text = rp.get("permissionsDisplayText", "")
            required_perms = rp.get("requiredPermissions", {})
            
            # Build permission description
            display_name = provider_display or provider
            if not display_name:
                continue
                
            perm_parts = []
            if isinstance(required_perms, dict):
                if required_perms.get("read"):
                    perm_parts.append("read")
                if required_perms.get("write"):
                    perm_parts.append("write")
                if required_perms.get("delete"):
                    perm_parts.append("delete")
                if required_perms.get("action"):
                    perm_parts.append("action")
            
            # Use permissionsDisplayText if available, otherwise build from requiredPermissions
            if perms_text:
                lines.append(f"- **{display_name}** ({scope}): {perms_text}\n")
            elif perm_parts:
                perms_desc = " and ".join(perm_parts) + " permission" + ("s" if len(perm_parts) > 1 else "")
                lines.append(f"- **{display_name}** ({scope}): {perms_desc} required.\n")
            else:
                lines.append(f"- **{display_name}** ({scope})\n")
    
    # Custom permissions
    customs = permissions.get("customs", [])
    if isinstance(customs, list) and customs:
        if lines:
            lines.append("\n")
        lines.append("**Custom Permissions:**\n")
        for custom in customs:
            if not isinstance(custom, dict):
                continue
            name = custom.get("name", "")
            description = custom.get("description", "")
            
            if name:
                if description:
                    lines.append(f"- **{name}**: {description}\n")
                else:
                    lines.append(f"- **{name}**\n")
    
    # Licenses
    licenses = permissions.get("licenses", [])
    if isinstance(licenses, list) and licenses:
        if lines:
            lines.append("\n")
        lines.append("**Licenses:**\n")
        # Map license codes to friendly names
        license_names = {
            "OfficeIRM": "Office Information Rights Management",
            "OfficeATP": "Office Advanced Threat Protection",
            "Office365": "Office 365",
            "AadP1P2": "Azure AD Premium P1/P2",
            "Mcas": "Microsoft Defender for Cloud Apps",
            "Aatp": "Microsoft Defender for Identity",
            "Mdatp": "Microsoft Defender for Endpoint",
            "Mtp": "Microsoft Threat Protection",
            "IoT": "Azure IoT"
        }
        for license in licenses:
            if isinstance(license, str):
                license_name = license_names.get(license, license)
                lines.append(f"- {license_name}\n")
    
    # Tenant permissions
    tenant = permissions.get("tenant", [])
    if isinstance(tenant, list) and tenant:
        if lines:
            lines.append("\n")
        lines.append("**Tenant Permissions:**\n")
        tenant_roles = ", ".join(tenant)
        lines.append(f"Requires {tenant_roles} on the workspace's tenant\n")
    
    return "".join(lines).strip()


def generate_index_page(solutions: Dict[str, List[Dict[str, str]]], output_dir: Path,
                       content_items_by_solution: Dict[str, List[Dict[str, str]]] = None) -> None:
    """Generate the main index page with table of all solutions.
    
    Args:
        solutions: Dictionary mapping solution name to list of connector entries
        output_dir: Output directory for documentation
        content_items_by_solution: Dictionary mapping solution name to list of content items
    """
    if content_items_by_solution is None:
        content_items_by_solution = {}
    
    index_path = output_dir / "solutions-index.md"
    
    with index_path.open("w", encoding="utf-8") as f:
        f.write("# Microsoft Sentinel Solutions Index\n\n")
        f.write("This reference documentation provides detailed information about data connectors ")
        f.write("available in Microsoft Sentinel Solutions.\n\n")
        
        # Add coverage note
        f.write("> **Note:** This index covers connectors managed through Solutions in the Azure-Sentinel ")
        f.write("GitHub repository. A small number of connectors (such as Microsoft Dataverse, ")
        f.write("Microsoft Power Automate, Microsoft Power Platform Admin, and SAP connectors) ")
        f.write("are not managed via Solutions and are therefore not included here.\n\n")
        
        # Add navigation to other indexes
        f.write("**Browse by:**\n\n")
        f.write("- [Solutions](solutions-index.md) (this page)\n")
        f.write("- [Connectors](connectors-index.md)\n")
        f.write("- [Tables](tables-index.md)\n\n")
        f.write("---\n\n")
        
        f.write("## Overview\n\n")
        
        # Count solutions with connectors (solutions that have at least one row with non-empty connector_id)
        solutions_with_connectors = 0
        for connectors in solutions.values():
            # A solution has a connector if at least one of its rows has a non-empty connector_id
            has_connector = False
            for conn in connectors:
                connector_id = conn.get('connector_id', '')
                # Handle both empty strings and 'nan' string values
                if connector_id and str(connector_id).strip() and str(connector_id).strip().lower() != 'nan':
                    has_connector = True
                    break
            if has_connector:
                solutions_with_connectors += 1
        
        f.write(f"This documentation covers **{len(solutions)} solutions**, ")
        if solutions_with_connectors == len(solutions):
            f.write(f"all of which include data connectors, ")
        else:
            f.write(f"of which **{solutions_with_connectors}** include data connectors, ")
        
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
        f.write(f"| Solutions with Connectors | {solutions_with_connectors} ({100*solutions_with_connectors//len(solutions)}%) |\n")
        f.write(f"| Unique Connectors | {len(all_connector_ids)} |\n")
        f.write(f"| Unique Tables | {len(all_tables)} |\n\n")
        
        # Content Items Statistics
        if content_items_by_solution:
            # Count content items by type
            content_by_type: Dict[str, int] = defaultdict(int)
            solutions_with_content = 0
            total_content_items = 0
            
            for solution_name_iter, items in content_items_by_solution.items():
                if items:
                    solutions_with_content += 1
                    for item in items:
                        content_type = item.get('content_type', 'unknown')
                        content_by_type[content_type] += 1
                        total_content_items += 1
            
            content_type_names = {
                'analytic_rule': 'Analytic Rules',
                'hunting_query': 'Hunting Queries',
                'workbook': 'Workbooks',
                'playbook': 'Playbooks',
                'parser': 'Parsers',
                'watchlist': 'Watchlists',
            }
            
            f.write("### Content Items Statistics\n\n")
            f.write("| Content Type | Count |\n")
            f.write("|:-------------|:------|\n")
            
            # Sort by count descending
            for content_type, count in sorted(content_by_type.items(), key=lambda x: -x[1]):
                type_name = content_type_names.get(content_type, content_type.replace('_', ' ').title())
                f.write(f"| {type_name} | {count} |\n")
            
            f.write(f"| **Total** | **{total_content_items}** |\n\n")
            f.write(f"*Content items found in {solutions_with_content} of {len(solutions)} solutions ({100*solutions_with_content//len(solutions)}%)*\n\n")
        
        # Build collection method summary
        # Collect all unique connectors with their metadata
        # Track all solutions per connector (some connectors appear in multiple solutions)
        connectors_map: Dict[str, Dict[str, any]] = {}
        connector_solutions: Dict[str, Set[str]] = defaultdict(set)  # connector_id -> set of solution names
        
        for solution_name_iter, connectors in solutions.items():
            for conn in connectors:
                connector_id = conn.get('connector_id', '')
                if not connector_id:
                    continue
                
                # Track all solutions this connector belongs to
                connector_solutions[connector_id].add(solution_name_iter)
                
                if connector_id in connectors_map:
                    continue
                
                connector_title = conn.get('connector_title', connector_id)
                connectors_map[connector_id] = {
                    'title': connector_title,
                    'collection_method': conn.get('collection_method', ''),
                }
        
        # Separate deprecated and active connectors
        deprecated_connectors = {}
        active_connectors_map = {}
        
        for connector_id, info in connectors_map.items():
            title = info['title']
            if '[DEPRECATED]' in title.upper() or title.startswith('[Deprecated]'):
                deprecated_connectors[connector_id] = info
            else:
                active_connectors_map[connector_id] = info
        
        # Build solutions_all_connectors using the complete mapping
        solutions_all_connectors: Dict[str, List[str]] = defaultdict(list)
        for connector_id, solution_names in connector_solutions.items():
            for solution_name_iter in solution_names:
                solutions_all_connectors[solution_name_iter].append(connector_id)
        
        # Identify deprecated solutions
        deprecated_solutions: Set[str] = set()
        for solution_name_iter, connector_ids in solutions_all_connectors.items():
            if '[DEPRECATED]' in solution_name_iter.upper() or solution_name_iter.startswith('[Deprecated]'):
                deprecated_solutions.add(solution_name_iter)
            elif all(cid in deprecated_connectors for cid in connector_ids):
                deprecated_solutions.add(solution_name_iter)
        
        # Build collection method stats - count all solutions each connector belongs to
        collection_method_stats: Dict[str, Dict[str, any]] = defaultdict(lambda: {
            'total_connectors': 0,
            'active_connectors': 0,
            'total_solutions': set(),
            'active_solutions': set(),
        })
        
        for connector_id, info in connectors_map.items():
            method = info.get('collection_method', 'Unknown') or 'Unknown'
            is_deprecated_connector = connector_id in deprecated_connectors
            
            collection_method_stats[method]['total_connectors'] += 1
            
            if not is_deprecated_connector:
                collection_method_stats[method]['active_connectors'] += 1
            
            # Add ALL solutions this connector belongs to
            for solution_name_iter in connector_solutions[connector_id]:
                collection_method_stats[method]['total_solutions'].add(solution_name_iter)
                if solution_name_iter not in deprecated_solutions:
                    collection_method_stats[method]['active_solutions'].add(solution_name_iter)
        
        # Write collection method summary table
        f.write("### Collection Methods\n\n")
        f.write("| Collection Method | Total Connectors | Active Connectors* | Total Solutions | Active Solutions* |\n")
        f.write("|:-----------------|:----------------:|:-----------------:|:---------------:|:----------------:|\n")
        
        sorted_methods = sorted(
            collection_method_stats.items(),
            key=lambda x: x[1]['total_connectors'],
            reverse=True
        )
        
        total_all_connectors = 0
        total_active_connectors = 0
        all_solutions_set: Set[str] = set()
        all_active_solutions_set: Set[str] = set()
        
        for method, stats in sorted_methods:
            total_connectors_count = stats['total_connectors']
            active_connectors_count = stats['active_connectors']
            total_solutions_count = len(stats['total_solutions'])
            active_solutions_count = len(stats['active_solutions'])
            
            total_all_connectors += total_connectors_count
            total_active_connectors += active_connectors_count
            all_solutions_set.update(stats['total_solutions'])
            all_active_solutions_set.update(stats['active_solutions'])
            
            f.write(f"| {method} | {total_connectors_count} | {active_connectors_count} | {total_solutions_count} | {active_solutions_count} |\n")
        
        f.write(f"| **Total** | **{total_all_connectors}** | **{total_active_connectors}** | **{len(all_solutions_set)}** | **{len(all_active_solutions_set)}** |\n")
        f.write("\n")
        f.write("*\\*Active excludes connectors and solutions marked as deprecated.*\n\n")
        
        # Organization section
        f.write("## How This Documentation is Organized\n\n")
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
                
                solution_link = f"[{solution_name}](solutions/{sanitize_filename(solution_name)}.md)"
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
                'collection_method': conn.get('collection_method', ''),
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
        
        # Add coverage note
        f.write("> **Note:** This index covers connectors managed through Solutions in the Azure-Sentinel ")
        f.write("GitHub repository. A small number of connectors (such as Microsoft Dataverse, ")
        f.write("Microsoft Power Automate, Microsoft Power Platform Admin, and SAP connectors) ")
        f.write("are not managed via Solutions and are therefore not included here.\n\n")
        
        # Add navigation
        f.write("**Browse by:**\n\n")
        f.write("- [Solutions](solutions-index.md)\n")
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
                collection_method = info.get('collection_method', '')
                
                f.write(f"### [{title}](connectors/{sanitize_filename(connector_id)}.md)\n\n")
                f.write(f"**Publisher:** {publisher}\n\n")
                f.write(f"**Solution:** [{solution_name}](solutions/{sanitize_filename(solution_name)}.md)\n\n")
                
                if collection_method:
                    f.write(f"**Collection Method:** {collection_method}\n\n")
                
                if tables:
                    f.write(f"**Tables ({len(tables)}):** ")
                    f.write(", ".join(f"`{table}`" for table in tables))
                    f.write("\n\n")
                
                description = info['description']
                if description:
                    # Replace <br> with newline but preserve markdown links
                    description = description.replace('<br>', '\n')
                    f.write(f"{description}\n\n")
                
                f.write(f"[→ View full connector details](connectors/{sanitize_filename(connector_id)}.md)\n\n")
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
                collection_method = info.get('collection_method', '')
                
                f.write(f"### [{title}](connectors/{sanitize_filename(connector_id)}.md)\n\n")
                f.write(f"**Publisher:** {publisher}\n\n")
                f.write(f"**Solution:** [{solution_name}](solutions/{sanitize_filename(solution_name)}.md)\n\n")
                
                if collection_method:
                    f.write(f"**Collection Method:** {collection_method}\n\n")
                
                if tables:
                    f.write(f"**Tables ({len(tables)}):** ")
                    f.write(", ".join(f"`{table}`" for table in tables))
                    f.write("\n\n")
                
                description = info['description']
                if description:
                    # Replace <br> with newline but preserve markdown links
                    description = description.replace('<br>', '\n')
                    f.write(f"{description}\n\n")
                
                f.write(f"[→ View full connector details](connectors/{sanitize_filename(connector_id)}.md)\n\n")
                f.write("---\n\n")
    
    print(f"Generated connectors index: {index_path}")


def generate_tables_index(solutions: Dict[str, List[Dict[str, str]]], output_dir: Path, tables_reference: Dict[str, Dict[str, str]],
                          content_table_info: Dict[str, Dict[str, Dict[str, Set[str]]]] = None) -> Dict[str, Dict[str, any]]:
    """Generate tables index page organized alphabetically.
    
    Args:
        solutions: Dictionary of solution names to connector rows
        output_dir: Output directory for documentation
        tables_reference: Dictionary of table metadata from reference CSV
        content_table_info: Dictionary of solution -> table -> {types, usage} from content items
    """
    if content_table_info is None:
        content_table_info = {}
    
    index_path = output_dir / "tables-index.md"
    
    # Collect all unique tables with their usage
    tables_map: Dict[str, Dict[str, any]] = defaultdict(lambda: {
        'solutions': set(),
        'connectors': set(),
        'content_types': set(),
        'is_unique': False,
    })
    
    # Add tables from connectors
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
    
    # Add tables from content items (analytics rules, hunting queries, etc.)
    for solution_name, tables_info in content_table_info.items():
        for table_name, info in tables_info.items():
            if table_name:  # Skip empty table names
                tables_map[table_name]['solutions'].add(solution_name)
                tables_map[table_name]['content_types'].update(info.get('types', set()))
    
    # Add tables from tables_reference that aren't already in the map
    # These are reference tables that may not be actively used by solutions
    for table_name in tables_reference.keys():
        if table_name and table_name not in tables_map:
            tables_map[table_name]  # Initialize with defaults from defaultdict
    
    with index_path.open("w", encoding="utf-8") as f:
        f.write("# Microsoft Sentinel Tables Index\n\n")
        f.write("Browse all tables used by Microsoft Sentinel solutions and data connectors.\n\n")
        
        # Add navigation
        f.write("**Browse by:**\n\n")
        f.write("- [Solutions](solutions-index.md)\n")
        f.write("- [Connectors](connectors-index.md)\n")
        f.write("- [Tables](tables-index.md) (this page)\n\n")
        f.write("---\n\n")
        
        f.write(f"## Overview\n\n")
        # Count tables with connectors vs content-only
        tables_with_connectors = sum(1 for info in tables_map.values() if info['connectors'])
        content_only_tables = len(tables_map) - tables_with_connectors
        f.write(f"This page lists **{len(tables_map)} unique tables** ({tables_with_connectors} ingested by connectors, {content_only_tables} referenced by content only).\n\n")
        
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
        
        # Generate sections by letter - with line breaks between items for readability
        for letter in letters:
            f.write(f"## {letter}\n\n")
            f.write("| Table | Solutions | Connectors |\n")
            f.write("|-------|-----------|------------|\n")
            
            for table in sorted(by_letter[letter]):
                info = tables_map[table]
                num_solutions = len(info['solutions'])
                num_connectors = len(info['connectors'])
                
                # All tables get individual pages now
                table_cell = f"[`{table}`](tables/{sanitize_filename(table)}.md)"
                
                # Solutions cell - use line breaks (HTML <br>) for multiple solutions
                if num_solutions == 1:
                    solution_name = list(info['solutions'])[0]
                    solutions_cell = f"[{solution_name}](solutions/{sanitize_filename(solution_name)}.md)"
                elif num_solutions <= 3:
                    solution_links = []
                    for solution_name in sorted(info['solutions']):
                        solution_links.append(f"[{solution_name}](solutions/{sanitize_filename(solution_name)}.md)")
                    solutions_cell = "<br>".join(solution_links)
                else:
                    solution_links = []
                    for solution_name in sorted(info['solutions'])[:3]:
                        solution_links.append(f"[{solution_name}](solutions/{sanitize_filename(solution_name)}.md)")
                    more_link = f"[+{num_solutions - 3} more](tables/{sanitize_filename(table)}.md)"
                    solutions_cell = "<br>".join(solution_links) + "<br>" + more_link
                
                # Connectors cell - use line breaks for multiple connectors
                if num_connectors == 1:
                    connector_id, connector_title = list(info['connectors'])[0]
                    connectors_cell = f"[{connector_title}](connectors/{sanitize_filename(connector_id)}.md)"
                elif num_connectors <= 5:
                    connector_links = []
                    for connector_id, connector_title in sorted(info['connectors']):
                        connector_links.append(f"[{connector_title}](connectors/{sanitize_filename(connector_id)}.md)")
                    connectors_cell = "<br>".join(connector_links)
                else:
                    connector_links = []
                    for connector_id, connector_title in sorted(info['connectors'])[:5]:
                        connector_links.append(f"[{connector_title}](connectors/{sanitize_filename(connector_id)}.md)")
                    more_link = f"[+{num_connectors - 5} more](tables/{sanitize_filename(table)}.md)"
                    connectors_cell = "<br>".join(connector_links) + "<br>" + more_link
                
                f.write(f"| {table_cell} | {solutions_cell} | {connectors_cell} |\n")
            
            f.write("\n")
    
    print(f"Generated tables index: {index_path}")
    
    # Return tables_map for use in generating table pages
    return tables_map


def generate_table_pages(tables_map: Dict[str, Dict[str, any]], output_dir: Path, tables_reference: Dict[str, Dict[str, str]],
                         content_tables_by_table: Dict[str, List[Dict[str, str]]] = None) -> None:
    """Generate individual table documentation pages for ALL tables.
    
    Args:
        tables_map: Dictionary of table names to their solution/connector info
        output_dir: Output directory for documentation
        tables_reference: Dictionary of table metadata from reference CSV
        content_tables_by_table: Dictionary of table name to list of content items using that table
    """
    if content_tables_by_table is None:
        content_tables_by_table = {}
    
    table_dir = output_dir / "tables"
    table_dir.mkdir(parents=True, exist_ok=True)
    
    pages_created = 0
    
    for table, info in sorted(tables_map.items()):
        num_solutions = len(info['solutions'])
        num_connectors = len(info['connectors'])
        
        # Generate page for ALL tables now (removed condition that required multiple solutions/connectors)
        
        table_path = table_dir / f"{sanitize_anchor(table)}.md"
        
        # Get reference data from tables_reference CSV
        table_ref = tables_reference.get(table, {})
        
        with table_path.open("w", encoding="utf-8") as f:
            f.write(f"# {table}\n\n")
            
            # Check if this is an internal use table
            # Only custom tables (_CL suffix) that are in INTERNAL_TABLES should show the note
            # Standard Sentinel tables (SecurityAlert, etc.) may be categorized as "Internal" in Azure Monitor
            # but they are not solution-specific internal use tables
            if table in INTERNAL_TABLES and table.endswith('_CL'):
                # Find solutions that use this table from content_tables_by_table
                solutions_using = sorted(set(row.get('solution_name', '') for row in content_tables_by_table.get(table, []) if row.get('solution_name', '')))
                if len(solutions_using) == 1:
                    solution_link = f"[{solutions_using[0]}](../solutions/{sanitize_filename(solutions_using[0])}.md)"
                    f.write(f"> **Internal Use Table:** This table is created and used internally by the {solution_link} solution. It is written to by playbooks for solution-specific data storage.\n\n")
                elif solutions_using:
                    solution_links = [f"[{s}](../solutions/{sanitize_filename(s)}.md)" for s in solutions_using]
                    f.write(f"> **Internal Use Table:** This table is created and used internally by the following solutions: {', '.join(solution_links)}. It is written to by playbooks for solution-specific data storage.\n\n")
                else:
                    f.write(f"> **Internal Use Table:** This table is created and used internally by solutions for playbook data storage.\n\n")
            
            # Description from reference CSV
            description = table_ref.get('description', '')
            if description:
                f.write(f"{description}\n\n")
            
            # Metadata table - exclude Table Name (redundant with title)
            # Collect attributes to check if table would be empty
            attributes = []
            
            category = table_ref.get('category', '')
            if category:
                attributes.append(('Category', category))
            
            # Table characteristics from reference CSV
            basic_logs = table_ref.get('basic_logs_eligible', '')
            if basic_logs:
                basic_logs_display = "✓ Yes" if basic_logs.lower() == 'yes' else "✗ No" if basic_logs.lower() == 'no' else basic_logs
                attributes.append(('Basic Logs Eligible', basic_logs_display))
            
            supports_transforms = table_ref.get('supports_transformations', '')
            if supports_transforms:
                transforms_display = "✓ Yes" if supports_transforms.lower() == 'yes' else "✗ No" if supports_transforms.lower() == 'no' else supports_transforms
                attributes.append(('Supports Transformations', transforms_display))
            
            ingestion_api = table_ref.get('ingestion_api_supported', '')
            if ingestion_api:
                ingestion_display = "✓ Yes" if ingestion_api.lower() == 'yes' else "✗ No" if ingestion_api.lower() == 'no' else ingestion_api
                attributes.append(('Ingestion API Supported', ingestion_display))
            
            search_job = table_ref.get('search_job_support', '')
            if search_job:
                search_display = "✓ Yes" if search_job.lower() == 'yes' else "✗ No" if search_job.lower() == 'no' else search_job
                attributes.append(('Search Job Support', search_display))
            
            plan = table_ref.get('plan', '')
            if plan:
                attributes.append(('Plan', plan))
            
            # Documentation links
            azure_monitor_link = table_ref.get('azure_monitor_doc_link', '')
            defender_xdr_link = table_ref.get('defender_xdr_doc_link', '')
            
            # Generate fallback Azure Monitor link if table is in Azure Monitor reference but no link stored
            if not azure_monitor_link and table_ref.get('source_azure_monitor', '').lower() == 'yes':
                azure_monitor_link = f"https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/{table.lower()}"
            
            if azure_monitor_link:
                attributes.append(('Azure Monitor Docs', f"[View Documentation]({azure_monitor_link})"))
            
            if defender_xdr_link:
                attributes.append(('Defender XDR Docs', f"[View Documentation]({defender_xdr_link})"))
            
            # Only write attribute table if there are attributes
            if attributes:
                f.write("| Attribute | Value |\n")
                f.write("|:----------|:------|\n")
                for attr_name, attr_value in attributes:
                    f.write(f"| **{attr_name}** | {attr_value} |\n")
                f.write("\n")
            
            # Solutions using this table - bullet list
            if info['solutions']:
                f.write(f"## Solutions ({len(info['solutions'])})\n\n")
                f.write("This table is used by the following solutions:\n\n")
                for name in sorted(info['solutions']):
                    f.write(f"- [{name}](../solutions/{sanitize_filename(name)}.md)\n")
                f.write("\n")
            
            # Connectors ingesting this table - bullet list
            if info['connectors']:
                f.write(f"## Connectors ({len(info['connectors'])})\n\n")
                f.write("This table is ingested by the following connectors:\n\n")
                for cid, title in sorted(info['connectors']):
                    f.write(f"- [{title}](../connectors/{sanitize_filename(cid)}.md)\n")
                f.write("\n")
            
            f.write("---\n\n")
            
            # Content Items section (analytics rules, hunting queries, etc. that use this table)
            table_content_items = content_tables_by_table.get(table, [])
            if table_content_items:
                # Group by content type
                content_by_type: Dict[str, List[Dict[str, str]]] = defaultdict(list)
                for item in table_content_items:
                    content_type = item.get('content_type', 'unknown')
                    content_by_type[content_type].append(item)
                
                content_type_names = {
                    'analytic_rule': 'Analytic Rules',
                    'hunting_query': 'Hunting Queries',
                    'workbook': 'Workbooks',
                    'playbook': 'Playbooks',
                    'parser': 'Parsers',
                    'watchlist': 'Watchlists',
                }
                
                f.write(f"## Content Items Using This Table ({len(table_content_items)})\n\n")
                
                for content_type in ['analytic_rule', 'hunting_query', 'workbook', 'parser']:
                    items = content_by_type.get(content_type, [])
                    if not items:
                        continue
                    
                    type_name = content_type_names.get(content_type, content_type.replace('_', ' ').title())
                    f.write(f"### {type_name} ({len(items)})\n\n")
                    
                    # Group by solution for better organization
                    items_by_solution: Dict[str, List[Dict[str, str]]] = defaultdict(list)
                    for item in items:
                        solution = item.get('solution_name', 'Unknown')
                        items_by_solution[solution].append(item)
                    
                    for solution_name, sol_items in sorted(items_by_solution.items()):
                        # Create solution link
                        solution_filename = sanitize_filename(solution_name) + ".md"
                        f.write(f"**In solution [{solution_name}](../solutions/{solution_filename}):**\n")
                        for item in sorted(sol_items, key=lambda x: x.get('content_name', '')):
                            name = item.get('content_name', 'N/A')
                            # Add link to GitHub file
                            github_url = get_content_item_github_url(item)
                            name_display = f"[{name}]({github_url})" if github_url else name
                            f.write(f"- {name_display}\n")
                        f.write("\n")
            
            # Additional reference information
            resource_types = table_ref.get('resource_types', '')
            if resource_types and resource_types != '-':
                f.write("## Resource Types\n\n")
                f.write("This table collects data from the following Azure resource types:\n\n")
                for rt in resource_types.split(','):
                    rt = rt.strip()
                    if rt:
                        f.write(f"- `{rt}`\n")
                f.write("\n")
            
            # Retention information
            retention_default = table_ref.get('retention_default', '')
            retention_max = table_ref.get('retention_max', '')
            if retention_default or retention_max:
                f.write("## Retention\n\n")
                if retention_default:
                    f.write(f"- **Default Retention:** {retention_default}\n")
                if retention_max:
                    f.write(f"- **Maximum Retention:** {retention_max}\n")
                f.write("\n")
            
            # Navigation
            f.write("---\n\n")
            f.write("**Browse:**\n\n")
            f.write("- [← Back to Tables Index](../tables-index.md)\n")
            f.write("- [Solutions Index](../solutions-index.md)\n")
            f.write("- [Connectors Index](../connectors-index.md)\n")
        
        pages_created += 1
    
    print(f"Generated {pages_created} individual table pages")


def generate_connector_pages(solutions: Dict[str, List[Dict[str, str]]], output_dir: Path, 
                            tables_reference: Dict[str, Dict[str, str]],
                            solutions_dir: Path = None) -> None:
    """Generate individual connector documentation pages.
    
    Args:
        solutions: Dictionary of solution name to list of connector entries
        output_dir: Output directory for documentation
        tables_reference: Dictionary of table metadata
        solutions_dir: Path to Solutions directory for reading additional markdown files
    """
    
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
            
            # Connector metadata table
            f.write("| Attribute | Value |\n")
            f.write("|:----------|:------|\n")
            f.write(f"| **Connector ID** | `{connector_id}` |\n")
            
            publisher = first_entry.get('connector_publisher', '')
            if publisher:
                f.write(f"| **Publisher** | {publisher} |\n")
            
            # Solutions
            solutions_list = ", ".join([f"[{solution_name}](../solutions/{sanitize_filename(solution_name)}.md)" for solution_name in sorted(data['solutions'])])
            f.write(f"| **Used in Solutions** | {solutions_list} |\n")
            
            # Collection Method
            collection_method = first_entry.get('collection_method', '')
            if collection_method:
                f.write(f"| **Collection Method** | {collection_method} |\n")
            
            # Connector files
            connector_files = first_entry.get('connector_files', '')
            if connector_files:
                files = [f.strip() for f in connector_files.split(';') if f.strip()]
                if files:
                    files_list = ", ".join([f"[{file_url.split('/')[-1]}]({file_url})" for file_url in files])
                    f.write(f"| **Connector Definition Files** | {files_list} |\n")
            
            f.write("\n")
            
            # Description
            description = first_entry.get('connector_description', '')
            if description:
                description = description.replace('<br>', '\n\n')
                f.write(f"{description}\n\n")
            
            # Tables Ingested Section - Enhanced with transformation and ingestion API info
            tables = sorted([t for t in data['tables'] if t])
            if tables:
                f.write("## Tables Ingested\n\n")
                f.write("This connector ingests data into the following tables:\n\n")
                f.write("| Table | Supports Transformations | Ingestion API Supported |\n")
                f.write("|-------|:------------------------:|:-----------------------:|\n")
                
                for table in tables:
                    table_ref = tables_reference.get(table, {})
                    supports_transforms = table_ref.get('supports_transformations', '')
                    ingestion_api = table_ref.get('ingestion_api_supported', '')
                    
                    # Format as checkmarks/dashes
                    transforms_cell = "✓" if supports_transforms.lower() == 'yes' else "✗" if supports_transforms.lower() == 'no' else "—"
                    ingestion_cell = "✓" if ingestion_api.lower() == 'yes' else "✗" if ingestion_api.lower() == 'no' else "—"
                    
                    table_link = f"[`{table}`](../tables/{sanitize_filename(table)}.md)"
                    f.write(f"| {table_link} | {transforms_cell} | {ingestion_cell} |\n")
                
                f.write("\n")
                
                # Add note about ingestion API support
                has_ingestion_api_tables = any(
                    tables_reference.get(t, {}).get('ingestion_api_supported', '').lower() == 'yes' 
                    for t in tables
                )
                if has_ingestion_api_tables:
                    f.write("> 💡 **Tip:** Tables with Ingestion API support allow data ingestion via the [Azure Monitor Data Collector API](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview), which also enables custom transformations during ingestion.\n\n")
            
            # Permissions section
            permissions = first_entry.get('connector_permissions', '')
            if permissions:
                f.write("## Permissions\n\n")
                formatted_permissions = format_permissions(permissions)
                f.write(f"{formatted_permissions}\n\n")
            
            # Setup Instructions section
            instruction_steps = first_entry.get('connector_instruction_steps', '')
            if instruction_steps:
                f.write("## Setup Instructions\n\n")
                f.write("> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.\n\n")
                formatted_instructions = format_instruction_steps(instruction_steps)
                f.write(f"{formatted_instructions}\n\n")
            
            # Additional Documentation section (from README.md files)
            if solutions_dir:
                readme_content = None
                readme_path = None
                
                # Get solution name for this connector
                solution_name = list(data['solutions'])[0] if data['solutions'] else None
                
                if solution_name:
                    # Count connectors in this solution to determine if we can use general README
                    solution_connector_count = sum(
                        1 for cid in by_connector.keys() 
                        if solution_name in by_connector[cid]['solutions']
                    )
                    
                    # Try to find connector-specific README
                    readme_content, readme_path = get_connector_readme(
                        solution_name, connector_id, connector_files, solutions_dir
                    )
                    
                    # If no specific README found and only one connector, try general README
                    if readme_content is None and solution_connector_count == 1:
                        readme_content, readme_path = get_single_connector_readme(solution_name, solutions_dir)
                
                if readme_content:
                    f.write("## Additional Documentation\n\n")
                    f.write(f"> 📄 *Source: [{readme_path}](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/{readme_path})*\n\n")
                    f.write(readme_content.strip())
                    f.write("\n\n")
            
            # Back navigation
            f.write("[← Back to Connectors Index](../connectors-index.md)\n")
        
        print(f"Generated connector page: {connector_path}")


def generate_solution_page(solution_name: str, connectors: List[Dict[str, str]], output_dir: Path,
                          solutions_dir: Path = None, content_items: List[Dict[str, str]] = None,
                          content_tables_mapping: Dict[str, List[str]] = None,
                          solution_table_content_types: Dict[str, Dict[str, Set[str]]] = None) -> None:
    """Generate individual solution documentation page.
    
    Args:
        solution_name: Name of the solution
        connectors: List of connector entries for this solution
        output_dir: Output directory for documentation
        solutions_dir: Path to Solutions directory for reading additional markdown files
        content_items: List of content items (analytics rules, hunting queries, etc.) for this solution
        content_tables_mapping: Dictionary mapping content_id to list of tables used
        solution_table_content_types: Dictionary mapping table_name to content types and usage for this solution
    """
    if content_items is None:
        content_items = []
    if content_tables_mapping is None:
        content_tables_mapping = {}
    if solution_table_content_types is None:
        solution_table_content_types = {}
    
    solution_dir = output_dir / "solutions"
    solution_dir.mkdir(parents=True, exist_ok=True)
    
    solution_path = solution_dir / f"{sanitize_anchor(solution_name)}.md"
    
    # Get solution-level metadata from first connector entry
    metadata = connectors[0]
    
    # Check if this solution has any connectors (connector_id will be empty for all entries if not)
    has_connectors = any(bool(conn.get('connector_id', '').strip()) for conn in connectors)
    
    # Get release notes if available
    release_notes = None
    if solutions_dir:
        release_notes = get_release_notes(solution_name, solutions_dir)
    
    with solution_path.open("w", encoding="utf-8") as f:
        f.write(f"# {solution_name}\n\n")
        
        # Solution metadata section
        f.write("## Solution Information\n\n")
        f.write("| Attribute | Value |\n")
        f.write("|:------------------------|:------|\n")
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
        
        # Load README content for later use (added at the end like connector docs)
        readme_content = None
        readme_github_url = None
        if solutions_dir:
            readme_content, readme_github_url = get_solution_readme(solution_name, solutions_dir)
        
        # Only include connectors section if solution has connectors
        if not has_connectors:
            f.write("## Data Connectors\n\n")
            f.write("**This solution does not include data connectors.**\n\n")
            f.write("This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.\n\n")
            
            # For solutions without connectors, show content item tables if any
            content_item_tables = set(solution_table_content_types.keys())
            if content_item_tables:
                # Separate internal tables from regular tables
                regular_tables = sorted([t for t in content_item_tables if t not in INTERNAL_TABLES])
                internal_tables = sorted([t for t in content_item_tables if t in INTERNAL_TABLES])
                
                f.write("## Tables Reference\n\n")
                
                # Content type display names
                content_type_short_names = {
                    'analytic_rule': 'Analytics',
                    'hunting_query': 'Hunting',
                    'workbook': 'Workbooks',
                    'playbook': 'Playbooks',
                    'parser': 'Parsers',
                    'watchlist': 'Watchlists',
                }
                
                def write_tables_table(tables: List[str], header: str = None) -> None:
                    """Write a table of tables with their content types."""
                    if header:
                        f.write(f"{header}\n\n")
                    f.write("| Table | Used By Content |\n")
                    f.write("|-------|----------------|\n")
                    for table in tables:
                        table_info = solution_table_content_types.get(table, {'types': set(), 'usage': set()})
                        content_types = table_info.get('types', set())
                        table_usage = table_info.get('usage', set())
                        content_parts = []
                        for ct in sorted(content_types):
                            ct_name = content_type_short_names.get(ct, ct.replace('_', ' ').title())
                            content_parts.append(ct_name)
                        has_write = 'write' in table_usage or 'read/write' in table_usage
                        if has_write:
                            content_parts = [f"{part} (writes)" if part == 'Playbooks' else part for part in content_parts]
                        content_list = ", ".join(content_parts) if content_parts else "-"
                        f.write(f"| {format_table_link(table)} | {content_list} |\n")
                    f.write("\n")
                
                if regular_tables:
                    f.write(f"This solution queries **{len(regular_tables)} table(s)** from its content items:\n\n")
                    write_tables_table(regular_tables)
                
                if internal_tables:
                    f.write(f"### Internal Tables\n\n")
                    f.write(f"The following **{len(internal_tables)} table(s)** are used internally by this solution's playbooks:\n\n")
                    write_tables_table(internal_tables)
                
                if not regular_tables and not internal_tables:
                    f.write("No tables found.\n\n")
        else:
            # Group by connector (filter out empty connector_ids from the row added for solutions without connectors)
            by_connector: Dict[str, List[Dict[str, str]]] = defaultdict(list)
            for conn in connectors:
                connector_id = conn.get('connector_id', '')
                if connector_id.strip():  # Only include non-empty connector_ids
                    by_connector[connector_id].append(conn)
            
            # Connectors section - simple list with links to connector pages
            f.write("## Data Connectors\n\n")
            f.write(f"This solution provides **{len(by_connector)} data connector(s)**:\n\n")
            
            for connector_id in sorted(by_connector.keys()):
                conn_entries = by_connector[connector_id]
                first_conn = conn_entries[0]
                connector_title = first_conn.get('connector_title', connector_id)
                connector_link = f"[{connector_title}](../connectors/{sanitize_filename(connector_id)}.md)"
                f.write(f"- {connector_link}\n")
            
            f.write("\n")
        
            # Tables summary section - combine connector tables and content item tables
            connector_tables = set(conn['Table'] for conn in connectors if conn.get('Table', '').strip())
            content_item_tables = set(solution_table_content_types.keys())
            all_tables = sorted(connector_tables | content_item_tables)
            
            if all_tables:
                # Separate internal tables from regular tables
                regular_tables = sorted([t for t in all_tables if t not in INTERNAL_TABLES])
                internal_tables = sorted([t for t in all_tables if t in INTERNAL_TABLES])
                
                f.write("## Tables Reference\n\n")
                
                # Content type display names
                content_type_short_names = {
                    'analytic_rule': 'Analytics',
                    'hunting_query': 'Hunting',
                    'workbook': 'Workbooks',
                    'playbook': 'Playbooks',
                    'parser': 'Parsers',
                    'watchlist': 'Watchlists',
                }
                
                def write_connector_tables_table(tables: List[str], header: str = None) -> None:
                    """Write a table of tables with connectors and content types."""
                    if header:
                        f.write(f"{header}\n\n")
                    f.write("| Table | Used By Connectors | Used By Content |\n")
                    f.write("|-------|-------------------|----------------|\n")
                    for table in tables:
                        # Get connector info
                        table_connectors = []
                        for conn in connectors:
                            if conn.get('Table') == table:
                                connector_id = conn.get('connector_id', '')
                                connector_title = conn.get('connector_title', connector_id)
                                table_connectors.append((connector_id, connector_title))
                        unique_connectors = sorted(set(table_connectors), key=lambda x: x[1])
                        connector_links = [f"[{title}](../connectors/{sanitize_anchor(cid)}.md)" for cid, title in unique_connectors]
                        connector_list = ", ".join(connector_links) if connector_links else "-"
                        # Get content types
                        table_info = solution_table_content_types.get(table, {'types': set(), 'usage': set()})
                        content_types = table_info.get('types', set())
                        table_usage = table_info.get('usage', set())
                        content_parts = []
                        for ct in sorted(content_types):
                            ct_name = content_type_short_names.get(ct, ct.replace('_', ' ').title())
                            content_parts.append(ct_name)
                        has_write = 'write' in table_usage or 'read/write' in table_usage
                        if has_write:
                            content_parts = [f"{part} (writes)" if part == 'Playbooks' else part for part in content_parts]
                        content_list = ", ".join(content_parts) if content_parts else "-"
                        f.write(f"| {format_table_link(table)} | {connector_list} | {content_list} |\n")
                    f.write("\n")
                
                if regular_tables:
                    f.write(f"This solution uses **{len(regular_tables)} table(s)**:\n\n")
                    write_connector_tables_table(regular_tables)
                
                if internal_tables:
                    f.write(f"### Internal Tables\n\n")
                    f.write(f"The following **{len(internal_tables)} table(s)** are used internally by this solution's playbooks:\n\n")
                    write_connector_tables_table(internal_tables)
        
        # Content Items section
        if content_items:
            # Group content items by type
            content_by_type: Dict[str, List[Dict[str, str]]] = defaultdict(list)
            for item in content_items:
                content_type = item.get('content_type', 'unknown')
                content_by_type[content_type].append(item)
            
            # Display friendly names for content types
            content_type_names = {
                'analytic_rule': 'Analytic Rules',
                'hunting_query': 'Hunting Queries',
                'workbook': 'Workbooks',
                'playbook': 'Playbooks',
                'parser': 'Parsers',
                'watchlist': 'Watchlists',
            }
            
            f.write("## Content Items\n\n")
            f.write(f"This solution includes **{len(content_items)} content item(s)**:\n\n")
            
            # Summary table by type
            f.write("| Content Type | Count |\n")
            f.write("|:-------------|:------|\n")
            for content_type, items in sorted(content_by_type.items(), key=lambda x: -len(x[1])):
                type_name = content_type_names.get(content_type, content_type.replace('_', ' ').title())
                f.write(f"| {type_name} | {len(items)} |\n")
            f.write("\n")
            
            # Detailed sections for each content type
            for content_type in ['analytic_rule', 'hunting_query', 'workbook', 'playbook', 'parser', 'watchlist']:
                items = content_by_type.get(content_type, [])
                if not items:
                    continue
                
                type_name = content_type_names.get(content_type, content_type.replace('_', ' ').title())
                
                # Separate active items from retired/deprecated/missing
                active_items = []
                retired_items = []
                for item in items:
                    query_status = item.get('content_query_status', 'has_query')
                    if query_status in ('retired', 'deprecated', 'moved_or_replaced', 'missing_query'):
                        retired_items.append((item, query_status))
                    else:
                        active_items.append(item)
                
                f.write(f"### {type_name}\n\n")
                
                # Display active items
                if content_type == 'analytic_rule':
                    if active_items:
                        f.write("| Name | Severity | Tactics | Tables Used |\n")
                        f.write("|:-----|:---------|:--------|:------------|\n")
                        for item in sorted(active_items, key=lambda x: x.get('content_name', '')):
                            name = item.get('content_name', 'N/A')
                            severity = item.get('content_severity', '') or '-'
                            tactics = format_tactics(item.get('content_tactics', ''))
                            content_key = get_content_key(item.get('content_id', ''), name, solution_name)
                            tables_with_usage = content_tables_mapping.get(content_key, [])
                            tables_str = format_tables_simple(tables_with_usage)
                            # Add link to GitHub file
                            github_url = get_content_item_github_url(item)
                            name_display = f"[{name}]({github_url})" if github_url else name
                            f.write(f"| {name_display} | {severity} | {tactics} | {tables_str} |\n")
                        f.write("\n")
                    
                    # Display retired/deprecated items separately
                    if retired_items:
                        f.write("#### Retired/Deprecated Rules\n\n")
                        f.write("| Name | Status | Description |\n")
                        f.write("|:-----|:-------|:------------|\n")
                        for item, status in sorted(retired_items, key=lambda x: x[0].get('content_name', '')):
                            name = item.get('content_name', 'N/A')
                            status_display = status.replace('_', ' ').title()
                            desc = item.get('content_description', '')[:150] + '...' if len(item.get('content_description', '')) > 150 else item.get('content_description', '') or '-'
                            github_url = get_content_item_github_url(item)
                            name_display = f"[{name}]({github_url})" if github_url else name
                            f.write(f"| {name_display} | {status_display} | {desc} |\n")
                        f.write("\n")
                        
                elif content_type == 'hunting_query':
                    if active_items:
                        f.write("| Name | Tactics | Tables Used |\n")
                        f.write("|:-----|:--------|:------------|\n")
                        for item in sorted(active_items, key=lambda x: x.get('content_name', '')):
                            name = item.get('content_name', 'N/A')
                            tactics = format_tactics(item.get('content_tactics', ''))
                            content_key = get_content_key(item.get('content_id', ''), name, solution_name)
                            tables_with_usage = content_tables_mapping.get(content_key, [])
                            tables_str = format_tables_simple(tables_with_usage)
                            # Add link to GitHub file
                            github_url = get_content_item_github_url(item)
                            name_display = f"[{name}]({github_url})" if github_url else name
                            f.write(f"| {name_display} | {tactics} | {tables_str} |\n")
                        f.write("\n")
                    
                    # Display retired/deprecated items separately
                    if retired_items:
                        f.write("#### Retired/Deprecated Queries\n\n")
                        f.write("| Name | Status | Description |\n")
                        f.write("|:-----|:-------|:------------|\n")
                        for item, status in sorted(retired_items, key=lambda x: x[0].get('content_name', '')):
                            name = item.get('content_name', 'N/A')
                            status_display = status.replace('_', ' ').title()
                            desc = item.get('content_description', '')[:150] + '...' if len(item.get('content_description', '')) > 150 else item.get('content_description', '') or '-'
                            github_url = get_content_item_github_url(item)
                            name_display = f"[{name}]({github_url})" if github_url else name
                            f.write(f"| {name_display} | {status_display} | {desc} |\n")
                        f.write("\n")
                else:
                    # Include tables for other content types
                    # Workbooks don't have useful descriptions, so omit the Description column
                    if content_type == 'workbook':
                        f.write("| Name | Tables Used |\n")
                        f.write("|:-----|:------------|\n")
                        for item in sorted(items, key=lambda x: x.get('content_name', '')):
                            name = item.get('content_name', 'N/A')
                            content_key = get_content_key(item.get('content_id', ''), name, solution_name)
                            tables_with_usage = content_tables_mapping.get(content_key, [])
                            tables_str = format_tables_simple(tables_with_usage)
                            github_url = get_content_item_github_url(item)
                            name_display = f"[{name}]({github_url})" if github_url else name
                            f.write(f"| {name_display} | {tables_str} |\n")
                        f.write("\n")
                    else:
                        f.write("| Name | Description | Tables Used |\n")
                        f.write("|:-----|:------------|:------------|\n")
                        for item in sorted(items, key=lambda x: x.get('content_name', '')):
                            name = item.get('content_name', 'N/A')
                            desc = item.get('content_description', '')[:100] + '...' if len(item.get('content_description', '')) > 100 else item.get('content_description', '') or '-'
                            content_key = get_content_key(item.get('content_id', ''), name, solution_name)
                            tables_with_usage = content_tables_mapping.get(content_key, [])
                            tables_str = format_tables_with_usage(tables_with_usage)
                            github_url = get_content_item_github_url(item)
                            name_display = f"[{name}]({github_url})" if github_url else name
                            f.write(f"| {name_display} | {desc} | {tables_str} |\n")
                        f.write("\n")
        
        # Additional Documentation section (from README.md files) - similar to connector docs
        if readme_content:
            f.write("## Additional Documentation\n\n")
            # Clean up README content - remove the title if it matches solution name
            lines = readme_content.strip().split('\n')
            # Skip first line if it's a title that matches the solution name
            if lines and lines[0].strip().startswith('#'):
                first_title = lines[0].strip().lstrip('#').strip()
                if first_title.lower() == solution_name.lower() or 'solution' in first_title.lower():
                    lines = lines[1:]
            
            # Include the README content (limit to reasonable size)
            readme_text = '\n'.join(lines).strip()
            if len(readme_text) > 3000:
                readme_text = readme_text[:3000].rsplit('\n', 1)[0] + '\n\n*[Content truncated...]*'
            
            f.write(f"> 📄 *Source: [{solution_name}/README.md]({readme_github_url})*\n\n")
            f.write(readme_text)
            f.write("\n\n")
        
        # Release Notes section (if available)
        if release_notes:
            f.write("## Release Notes\n\n")
            # The release notes are usually already in markdown table format
            f.write(release_notes.strip())
            f.write("\n\n")
        
        # Navigation
        f.write("---\n\n")
        f.write("**Browse:**\n\n")
        f.write("- [← Back to Solutions Index](../solutions-index.md)\n")
        f.write("- [Connectors Index](../connectors-index.md)\n")
        f.write("- [Tables Index](../tables-index.md)\n")
    
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
        "--connectors-csv",
        type=Path,
        default=Path(__file__).parent / "connectors.csv",
        help="Path to connectors CSV file with collection methods (default: connectors.csv)",
    )
    parser.add_argument(
        "--tables-csv",
        type=Path,
        default=Path(__file__).parent / "tables_reference.csv",
        help="Path to tables reference CSV file from Azure Monitor docs (default: tables_reference.csv)",
    )
    parser.add_argument(
        "--tables-overrides-csv",
        type=Path,
        default=Path(__file__).parent / "tables.csv",
        help="Path to tables CSV with solution-specific overrides like internal category (default: tables.csv)",
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
    parser.add_argument(
        "--solutions-dir",
        type=Path,
        default=DEFAULT_SOLUTIONS_DIR,
        help="Path to Solutions directory for reading ReleaseNotes.md and connector README files",
    )
    parser.add_argument(
        "--content-items-csv",
        type=Path,
        default=Path(__file__).parent / "content_items.csv",
        help="Path to content items CSV file (default: content_items.csv)",
    )
    parser.add_argument(
        "--content-tables-csv",
        type=Path,
        default=Path(__file__).parent / "content_tables_mapping.csv",
        help="Path to content-to-tables mapping CSV file (default: content_tables_mapping.csv)",
    )
    parser.add_argument(
        "--skip-input-generation",
        action="store_true",
        help="Skip running input CSV generation scripts",
    )
    
    args = parser.parse_args()
    
    # Run input CSV generation scripts if not skipped
    script_dir = Path(__file__).parent
    if not args.skip_input_generation:
        print("Running input CSV generation scripts...")
        
        # Run compare_connector_catalogs.py
        compare_script = script_dir / "compare_connector_catalogs.py"
        if compare_script.exists():
            print(f"  Running {compare_script.name}...")
            result = subprocess.run(
                [sys.executable, str(compare_script)],
                cwd=str(script_dir),
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"    Warning: {compare_script.name} failed: {result.stderr}")
            else:
                print(f"    Done.")
        
        # Run collect_table_info.py (uses local cache by default, no web fetching)
        collect_script = script_dir / "collect_table_info.py"
        if collect_script.exists():
            print(f"  Running {collect_script.name} (using local cache)...")
            result = subprocess.run(
                [sys.executable, str(collect_script)],
                cwd=str(script_dir),
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"    Warning: {collect_script.name} failed: {result.stderr}")
            else:
                print(f"    Done.")
    
    if not args.input.exists():
        raise SystemExit(f"Input file not found: {args.input}")
    
    # Load tables reference CSV (Azure Monitor docs) into a dictionary keyed by table name
    tables_reference: Dict[str, Dict[str, str]] = {}
    if args.tables_csv.exists():
        print(f"Reading {args.tables_csv}...")
        with args.tables_csv.open("r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                table_name = row.get('table_name', '')
                if table_name:
                    tables_reference[table_name] = row
        print(f"Loaded {len(tables_reference)} tables from reference CSV")
    else:
        print(f"Warning: Tables reference CSV not found: {args.tables_csv}")
    
    # Load tables overrides CSV (mapper output) to get internal table categories
    if args.tables_overrides_csv.exists():
        print(f"Reading {args.tables_overrides_csv} for overrides...")
        with args.tables_overrides_csv.open("r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                table_name = row.get('table_name', '')
                if table_name:
                    # Track internal tables (category="Internal")
                    if row.get('category', '').lower() == 'internal':
                        INTERNAL_TABLES.add(table_name)
                    # Merge overrides into tables_reference (create entry if not exists)
                    if table_name not in tables_reference:
                        tables_reference[table_name] = row
                    else:
                        # Override category if set to Internal
                        if row.get('category', '').lower() == 'internal':
                            tables_reference[table_name]['category'] = 'Internal'
        print(f"Loaded overrides ({len(INTERNAL_TABLES)} internal tables)")
    else:
        print(f"Warning: Tables overrides CSV not found: {args.tables_overrides_csv}")
    
    # Load connectors CSV for collection method info
    connectors_reference: Dict[str, Dict[str, str]] = {}
    if args.connectors_csv.exists():
        print(f"Reading {args.connectors_csv}...")
        with args.connectors_csv.open("r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                connector_id = row.get('connector_id', '')
                if connector_id:
                    connectors_reference[connector_id] = row
        print(f"Loaded {len(connectors_reference)} connectors from connectors CSV")
    else:
        print(f"Warning: Connectors CSV not found: {args.connectors_csv}")
    
    # Load content items CSV
    content_items_by_solution: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    if args.content_items_csv.exists():
        print(f"Reading {args.content_items_csv}...")
        with args.content_items_csv.open("r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                solution_name = row.get('solution_name', '')
                if solution_name:
                    content_items_by_solution[solution_name].append(row)
        total_content = sum(len(items) for items in content_items_by_solution.values())
        print(f"Loaded {total_content} content items from {len(content_items_by_solution)} solutions")
    else:
        print(f"Warning: Content items CSV not found: {args.content_items_csv}")
    
    # Load content-to-tables mapping CSV
    content_tables_by_table: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    if args.content_tables_csv.exists():
        print(f"Reading {args.content_tables_csv}...")
        with args.content_tables_csv.open("r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                table_name = row.get('table_name', '')
                if table_name:
                    content_tables_by_table[table_name].append(row)
        total_mappings = sum(len(items) for items in content_tables_by_table.values())
        print(f"Loaded {total_mappings} content-table mappings for {len(content_tables_by_table)} tables")
    else:
        print(f"Warning: Content-tables mapping CSV not found: {args.content_tables_csv}")
    
    # Build content_id to tables mapping for solution pages
    # Uses get_content_key() to handle items without content_id (workbooks, playbooks)
    # Maps content_key -> list of (table_name, usage) tuples
    content_tables_mapping: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    # Also build solution -> table -> {content_types, table_usage} mapping
    solution_table_content_types: Dict[str, Dict[str, Dict[str, Set[str]]]] = defaultdict(lambda: defaultdict(lambda: {'types': set(), 'usage': set()}))
    if args.content_tables_csv.exists():
        with args.content_tables_csv.open("r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                content_id = row.get('content_id', '')
                content_name = row.get('content_name', '')
                solution_name = row.get('solution_name', '')
                table_name = row.get('table_name', '')
                content_type = row.get('content_type', '')
                table_usage = row.get('table_usage', 'read')
                content_key = get_content_key(content_id, content_name, solution_name)
                if content_key and table_name:
                    # Check if table already in list (to avoid duplicates)
                    existing_tables = [t for t, u in content_tables_mapping[content_key]]
                    if table_name not in existing_tables:
                        content_tables_mapping[content_key].append((table_name, table_usage))
                # Track which content types use each table in each solution
                if solution_name and table_name:
                    solution_table_content_types[solution_name][table_name]['types'].add(content_type)
                    solution_table_content_types[solution_name][table_name]['usage'].add(table_usage)
        
        print(f"Built content-to-tables mapping for {len(content_tables_mapping)} content items")
    
    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read CSV
    print(f"Reading {args.input}...")
    with args.input.open("r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
    
    # Enrich rows with collection method from connectors CSV
    for row in rows:
        connector_id = row.get('connector_id', '')
        if connector_id and connector_id in connectors_reference:
            row['collection_method'] = connectors_reference[connector_id].get('collection_method', '')
            row['collection_method_reason'] = connectors_reference[connector_id].get('collection_method_reason', '')
    
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
    
    # Check if solutions directory exists for additional markdown content
    solutions_dir = args.solutions_dir if args.solutions_dir.exists() else None
    if solutions_dir:
        print(f"Reading additional markdown from: {solutions_dir}")
    else:
        print(f"Warning: Solutions directory not found: {args.solutions_dir} - skipping ReleaseNotes and README enrichment")
    
    # Generate index pages
    generate_index_page(by_solution, args.output_dir, content_items_by_solution)
    generate_connectors_index(by_solution, args.output_dir)
    tables_map = generate_tables_index(by_solution, args.output_dir, tables_reference, solution_table_content_types)
    
    # Generate individual connector pages
    generate_connector_pages(by_solution, args.output_dir, tables_reference, solutions_dir)
    
    # Generate individual solution pages
    for solution_name, connectors in sorted(by_solution.items()):
        solution_content = content_items_by_solution.get(solution_name, [])
        solution_table_types = solution_table_content_types.get(solution_name, {})
        generate_solution_page(solution_name, connectors, args.output_dir, solutions_dir, solution_content, content_tables_mapping, solution_table_types)
    
    # Generate individual table pages with content item references
    generate_table_pages(tables_map, args.output_dir, tables_reference, content_tables_by_table)
    
    # Count unique connectors and tables
    all_connector_ids = set()
    for connectors in by_solution.values():
        for conn in connectors:
            connector_id = conn.get('connector_id', '')
            if connector_id:
                all_connector_ids.add(connector_id)
    
    # Count table pages created - now counts all tables with pages
    table_pages_count = len(tables_map)
    
    print(f"\nDocumentation generated successfully in: {args.output_dir}")
    print(f"  - Solutions index: {args.output_dir / 'solutions-index.md'}")
    print(f"  - Connectors index: {args.output_dir / 'connectors-index.md'}")
    print(f"  - Tables index: {args.output_dir / 'tables-index.md'}")
    print(f"  - Solutions: {args.output_dir / 'solutions'}/ ({len(by_solution)} files)")
    print(f"  - Connectors: {args.output_dir / 'connectors'}/ ({len(all_connector_ids)} files)")
    print(f"  - Tables: {args.output_dir / 'tables'}/ ({table_pages_count} files)")


if __name__ == "__main__":
    main()
