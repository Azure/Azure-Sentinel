#!/usr/bin/env python3
"""
ASIM Empty Parser Updater

This script updates empty parser YAML files to match the schema definition in ASimTester.csv.
Instead of regenerating the entire datatable, it makes surgical edits:
- Adds missing fields
- Removes fields that shouldn't be in the schema
- Modifies fields with incorrect types

This approach enables easier review of changes in git diffs.
"""

import csv
import re
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass


@dataclass
class FieldDefinition:
    """Represents a field definition from the CSV schema."""
    name: str
    column_type: str
    field_class: str  # Mandatory, Recommended, Optional, Conditional, Alias
    schema: str
    logical_type: str
    list_of_values: str
    aliased: str


@dataclass
class ParserField:
    """Represents a field found in a parser's datatable."""
    name: str
    column_type: str
    line_number: int
    original_line: str
    indent: str
    has_trailing_comma: bool
    comment: str


def load_schema_from_csv(csv_path: str) -> Dict[str, Dict[str, FieldDefinition]]:
    """
    Load field definitions from ASimTester.csv.
    Returns a dict: schema_name -> {field_name -> FieldDefinition}
    """
    schemas: Dict[str, Dict[str, FieldDefinition]] = {}
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
        reader = csv.DictReader(f)
        for row in reader:
            schema = row.get('Schema', '').strip()
            if not schema or schema == 'Schema':  # Skip header if present
                continue
            
            # Get column name, handling potential BOM in header
            column_name = row.get('ColumnName', '') or row.get('\ufeffColumnName', '')
            column_name = column_name.strip()
            
            if not column_name:
                continue
                
            field = FieldDefinition(
                name=column_name,
                column_type=row.get('ColumnType', '').strip(),
                field_class=row.get('Class', '').strip(),
                schema=schema,
                logical_type=row.get('LogicalType', '').strip(),
                list_of_values=row.get('ListOfValues', '').strip(),
                aliased=row.get('Aliased', '').strip()
            )
            
            if schema not in schemas:
                schemas[schema] = {}
            
            # Don't overwrite if already exists (first definition wins)
            if field.name not in schemas[schema]:
                schemas[schema][field.name] = field
    
    return schemas


def get_common_fields(schemas: Dict[str, Dict[str, FieldDefinition]]) -> Dict[str, FieldDefinition]:
    """Get fields from the Common schema that apply to all schemas."""
    return schemas.get('Common', {})


def get_schema_fields(schemas: Dict[str, Dict[str, FieldDefinition]], 
                      schema_name: str) -> Dict[str, FieldDefinition]:
    """
    Get all fields for a schema, including Common fields.
    Schema-specific fields override Common fields.
    """
    common_fields = get_common_fields(schemas).copy()
    schema_fields = schemas.get(schema_name, {})
    
    # Schema-specific fields override common fields
    common_fields.update(schema_fields)
    return common_fields


def parse_datatable_field(line: str, line_number: int) -> Optional[ParserField]:
    """
    Parse a single line from a datatable definition.
    Returns ParserField if the line contains a field definition, None otherwise.
    """
    # Match patterns like:
    #   FieldName:type
    #   , FieldName:type
    #   FieldName:type,
    #   , FieldName: type // comment
    
    # Remove leading/trailing whitespace for analysis but preserve original
    stripped = line.strip()
    
    # Skip empty lines, comments-only lines, parentheses, brackets
    if not stripped or stripped.startswith('//') or stripped in ['(', ')', '[]', '];', ')[];', ')[]', ');']:
        return None
    
    # Extract indent
    indent_match = re.match(r'^(\s*)', line)
    indent = indent_match.group(1) if indent_match else ''
    
    # Pattern to match field definitions
    # Handles: ", FieldName:type" or "FieldName:type," or ", FieldName: type // comment"
    pattern = r'^[,\s]*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([a-z]+)'
    match = re.search(pattern, stripped, re.IGNORECASE)
    
    if not match:
        return None
    
    field_name = match.group(1)
    field_type = match.group(2).lower()
    
    # Check for trailing comma
    has_trailing_comma = stripped.rstrip().endswith(',') or ',' in stripped.split('//')[0].split(field_type)[-1]
    
    # Extract comment if present
    comment = ''
    comment_match = re.search(r'//\s*(.*)$', stripped)
    if comment_match:
        comment = comment_match.group(1).strip()
    
    return ParserField(
        name=field_name,
        column_type=field_type,
        line_number=line_number,
        original_line=line,
        indent=indent,
        has_trailing_comma=has_trailing_comma,
        comment=comment
    )


def find_datatable_bounds(lines: List[str]) -> Tuple[int, int, str]:
    """
    Find the start and end line indices of the datatable definition.
    Returns (start_index, end_index, datatable_variable_name)
    """
    start_idx = -1
    end_idx = -1
    var_name = ''
    paren_depth = 0
    in_datatable = False
    
    for i, line in enumerate(lines):
        # Look for datatable declaration
        if 'datatable' in line.lower() and '(' in line:
            # Extract variable name if present (e.g., "let EmptyEvents=datatable(")
            var_match = re.search(r'let\s+(\w+)\s*=\s*datatable', line, re.IGNORECASE)
            if var_match:
                var_name = var_match.group(1)
            start_idx = i
            in_datatable = True
            paren_depth = line.count('(') - line.count(')')
            continue
        
        if in_datatable:
            paren_depth += line.count('(') - line.count(')')
            
            # Check for end of datatable (closing with )[] or similar)
            if paren_depth <= 0 or ')]' in line or ')[]' in line or ');' in line:
                end_idx = i
                break
    
    return start_idx, end_idx, var_name


def extract_parser_fields(lines: List[str], start_idx: int, end_idx: int) -> List[ParserField]:
    """Extract all field definitions from the datatable."""
    fields = []
    
    for i in range(start_idx, end_idx + 1):
        field = parse_datatable_field(lines[i], i)
        if field:
            fields.append(field)
    
    return fields


def detect_field_style(fields: List[ParserField]) -> Tuple[str, bool, bool]:
    """
    Detect the formatting style used in the parser.
    Returns (indent, comma_before, space_after_colon)
    """
    if not fields:
        return '    ', False, True
    
    # Check if comma comes before or after
    comma_before = False
    space_after_colon = True
    indent = '    '  # Default
    
    for field in fields[:10]:
        stripped = field.original_line.strip()
        if stripped.startswith(','):
            comma_before = True
            # For comma-before style, use the indent of a field with comma
            indent = field.indent
            break
    
    # If not comma-before, use the first field's indent
    if not comma_before:
        indent = fields[0].indent if fields else '    '
    
    # Check for space after colon
    for field in fields[:5]:
        stripped = field.original_line.strip()
        if ': ' in stripped:
            space_after_colon = True
            break
        elif ':' in stripped and ': ' not in stripped:
            space_after_colon = False
            break
    
    return indent, comma_before, space_after_colon


def normalize_type(csv_type: str) -> str:
    """Normalize CSV type to KQL type."""
    type_mapping = {
        'string': 'string',
        'int': 'int',
        'long': 'long',
        'datetime': 'datetime',
        'bool': 'bool',
        'boolean': 'bool',
        'real': 'real',
        'double': 'real',
        'dynamic': 'dynamic',
        'guid': 'string',  # GUIDs are stored as strings in KQL
        'sting': 'string',  # Fix typo in CSV
    }
    return type_mapping.get(csv_type.lower(), csv_type.lower())


def generate_field_line(field_name: str, field_type: str, indent: str, 
                        comma_before: bool, space_after_colon: bool = True,
                        is_last: bool = False, comment: str = '') -> str:
    """Generate a properly formatted field line."""
    normalized_type = normalize_type(field_type)
    colon = ': ' if space_after_colon else ':'
    
    if comma_before:
        prefix = ', '
        line = f"{indent}{prefix}{field_name}{colon}{normalized_type}"
    else:
        suffix = ',' if not is_last else ''
        line = f"{indent}{field_name}{colon}{normalized_type}{suffix}"
    
    if comment:
        line += f" // {comment}"
    
    return line


def compute_changes(parser_fields: List[ParserField], 
                   schema_fields: Dict[str, FieldDefinition],
                   schema_name: str) -> Tuple[List[str], List[ParserField], List[Tuple[ParserField, str]]]:
    """
    Compute the changes needed to update the parser.
    
    Returns:
        - fields_to_add: List of field names to add
        - fields_to_remove: List of ParserField objects to remove
        - fields_to_modify: List of (ParserField, new_type) tuples
    """
    parser_field_names = {f.name for f in parser_fields}
    schema_field_names = set(schema_fields.keys())
    
    # Fields to add (in schema but not in parser)
    # Exclude Alias fields - they typically don't need to be in empty parsers
    fields_to_add = []
    for name in schema_field_names - parser_field_names:
        field_def = schema_fields[name]
        if field_def.field_class != 'Alias':
            fields_to_add.append(name)
    
    # Fields to remove (in parser but not in schema and not common special fields)
    # Be conservative - only remove if clearly not in schema
    special_fields = {'TimeGenerated', '_ResourceId', 'Type', 'TenantId'}
    fields_to_remove = []
    for field in parser_fields:
        if field.name not in schema_field_names and field.name not in special_fields:
            # Double-check it's not an alias
            fields_to_remove.append(field)
    
    # Fields to modify (type mismatch)
    fields_to_modify = []
    for field in parser_fields:
        if field.name in schema_fields:
            expected_type = normalize_type(schema_fields[field.name].column_type)
            actual_type = normalize_type(field.column_type)
            if expected_type != actual_type:
                fields_to_modify.append((field, expected_type))
    
    return fields_to_add, fields_to_remove, fields_to_modify


def apply_changes(lines: List[str], 
                  parser_fields: List[ParserField],
                  schema_fields: Dict[str, FieldDefinition],
                  fields_to_add: List[str],
                  fields_to_remove: List[ParserField],
                  fields_to_modify: List[Tuple[ParserField, str]],
                  start_idx: int, 
                  end_idx: int) -> List[str]:
    """
    Apply the computed changes to the file lines.
    Returns the modified lines.
    """
    # Create a copy of lines to modify
    new_lines = lines.copy()
    
    # Track line offset due to additions/deletions
    offset = 0
    
    # Detect style
    indent, comma_before, space_after_colon = detect_field_style(parser_fields)
    
    # 1. Mark lines for removal
    lines_to_delete = set()
    for field in fields_to_remove:
        lines_to_delete.add(field.line_number)
    
    # 2. Apply type modifications in place
    for field, new_type in fields_to_modify:
        if field.line_number not in lines_to_delete:
            old_line = new_lines[field.line_number]
            # Replace the type in the line while preserving formatting
            pattern = rf'({re.escape(field.name)}\s*:\s*){field.column_type}'
            new_line = re.sub(pattern, rf'\g<1>{new_type}', old_line, flags=re.IGNORECASE)
            new_lines[field.line_number] = new_line
    
    # 3. Delete lines marked for removal (in reverse order to preserve indices)
    for line_num in sorted(lines_to_delete, reverse=True):
        del new_lines[line_num]
        offset -= 1
    
    # 4. Add new fields before the closing of the datatable
    if fields_to_add:
        # Find insertion point (before the closing )[] )
        adjusted_end = end_idx + offset
        
        # Find the last actual field line
        insert_idx = adjusted_end
        for i in range(adjusted_end, start_idx, -1):
            if parse_datatable_field(new_lines[i], i):
                insert_idx = i + 1
                break
        
        # Sort fields to add for consistent ordering
        fields_to_add.sort()
        
        # Generate new lines
        new_field_lines = []
        for field_name in fields_to_add:
            field_def = schema_fields[field_name]
            line = generate_field_line(
                field_name, 
                field_def.column_type, 
                indent, 
                comma_before,
                space_after_colon
            )
            new_field_lines.append(line + '\n')
        
        # Insert new lines
        for i, new_line in enumerate(new_field_lines):
            new_lines.insert(insert_idx + i, new_line)
    
    return new_lines


def get_schema_name_from_yaml(yaml_path: str) -> Optional[str]:
    """Extract the schema name from the YAML file."""
    with open(yaml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for Schema: in Normalization section
    match = re.search(r'Schema:\s*(\w+)', content)
    if match:
        return match.group(1)
    
    # Try to infer from filename
    filename = os.path.basename(yaml_path)
    # vimAuditEventEmpty.yaml -> AuditEvent
    # vimDnsEmpty.yaml -> Dns
    match = re.search(r'vim(\w+?)Empty\.yaml', filename, re.IGNORECASE)
    if match:
        name = match.group(1)
        # Handle special cases
        if name.lower() == 'process':
            return 'ProcessEvent'
        return name
    
    return None


def update_parser_file(yaml_path: str, 
                       schemas: Dict[str, Dict[str, FieldDefinition]],
                       dry_run: bool = False) -> Dict:
    """
    Update a single parser file.
    
    Returns a dict with:
        - schema: schema name
        - added: list of added fields
        - removed: list of removed fields
        - modified: list of (field, old_type, new_type)
        - error: error message if any
    """
    result = {
        'file': yaml_path,
        'schema': None,
        'added': [],
        'removed': [],
        'modified': [],
        'error': None
    }
    
    try:
        # Read the file
        with open(yaml_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines(keepends=True)
        
        # Ensure lines have newline endings
        lines = [line if line.endswith('\n') else line + '\n' for line in lines]
        
        # Get schema name
        schema_name = get_schema_name_from_yaml(yaml_path)
        if not schema_name:
            result['error'] = 'Could not determine schema name'
            return result
        
        result['schema'] = schema_name
        
        # Get expected fields for this schema
        schema_fields = get_schema_fields(schemas, schema_name)
        if not schema_fields:
            result['error'] = f'No fields found for schema {schema_name}'
            return result
        
        # Find datatable bounds
        start_idx, end_idx, _ = find_datatable_bounds(lines)
        if start_idx < 0 or end_idx < 0:
            result['error'] = 'Could not find datatable definition'
            return result
        
        # Extract current fields
        parser_fields = extract_parser_fields(lines, start_idx, end_idx)
        
        # Compute changes
        fields_to_add, fields_to_remove, fields_to_modify = compute_changes(
            parser_fields, schema_fields, schema_name
        )
        
        result['added'] = fields_to_add
        result['removed'] = [f.name for f in fields_to_remove]
        result['modified'] = [(f.name, f.column_type, new_type) for f, new_type in fields_to_modify]
        
        # Apply changes if not dry run and there are changes
        if not dry_run and (fields_to_add or fields_to_remove or fields_to_modify):
            new_lines = apply_changes(
                lines, parser_fields, schema_fields,
                fields_to_add, fields_to_remove, fields_to_modify,
                start_idx, end_idx
            )
            
            with open(yaml_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        
    except Exception as e:
        result['error'] = str(e)
    
    return result


def find_empty_parsers(repo_root: str) -> List[str]:
    """Find all empty parser YAML files in the repository."""
    parsers_dir = os.path.join(repo_root, 'Parsers')
    empty_parsers = []
    
    for root, dirs, files in os.walk(parsers_dir):
        for file in files:
            # Match pattern: vim*Empty.yaml in ASim* directories
            if file.endswith('Empty.yaml') and file.startswith('vim'):
                dir_name = os.path.basename(os.path.dirname(os.path.dirname(root + '/')))
                if dir_name.startswith('ASim'):
                    empty_parsers.append(os.path.join(root, file))
    
    return sorted(empty_parsers)


def main():
    parser = argparse.ArgumentParser(
        description='Update ASIM empty parser files based on schema definition'
    )
    parser.add_argument(
        '--repo-root',
        default=None,
        help='Root directory of the Azure-Sentinel repository'
    )
    parser.add_argument(
        '--csv-path',
        default=None,
        help='Path to ASimTester.csv'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes'
    )
    parser.add_argument(
        '--parser',
        default=None,
        help='Update only the specified parser file'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Show detailed output'
    )
    
    args = parser.parse_args()
    
    # Determine repository root
    if args.repo_root:
        repo_root = args.repo_root
    else:
        # Try to find it relative to this script
        # Script is at: ASIM/tools/ASIM Updater/update_empty_parsers.py
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    
    # Determine CSV path
    if args.csv_path:
        csv_path = args.csv_path
    else:
        csv_path = os.path.join(repo_root, 'ASIM', 'dev', 'ASimTester', 'ASimTester.csv')
    
    if not os.path.exists(csv_path):
        print(f'Error: CSV file not found: {csv_path}', file=sys.stderr)
        sys.exit(1)
    
    # Load schema definitions
    print(f'Loading schema definitions from {csv_path}...')
    schemas = load_schema_from_csv(csv_path)
    print(f'Loaded {len(schemas)} schemas')
    
    # Find parsers to update
    if args.parser:
        parsers = [args.parser]
    else:
        parsers = find_empty_parsers(repo_root)
    
    print(f'Found {len(parsers)} empty parser(s) to check')
    
    # Process each parser
    total_changes = 0
    for parser_path in parsers:
        result = update_parser_file(parser_path, schemas, dry_run=args.dry_run)
        
        has_changes = result['added'] or result['removed'] or result['modified']
        
        if result['error']:
            print(f"\n[ERROR] {os.path.basename(parser_path)}: {result['error']}")
        elif has_changes:
            total_changes += 1
            action = 'Would update' if args.dry_run else 'Updated'
            print(f"\n[UPDATE] {action}: {os.path.basename(parser_path)} (Schema: {result['schema']})")
            
            if result['added']:
                print(f"   + Add {len(result['added'])} field(s): {', '.join(result['added'][:5])}" + 
                      ('...' if len(result['added']) > 5 else ''))
            if result['removed']:
                print(f"   - Remove {len(result['removed'])} field(s): {', '.join(result['removed'][:5])}" +
                      ('...' if len(result['removed']) > 5 else ''))
            if result['modified']:
                print(f"   ~ Modify {len(result['modified'])} field(s):")
                for name, old_type, new_type in result['modified'][:5]:
                    print(f"     {name}: {old_type} -> {new_type}")
                if len(result['modified']) > 5:
                    print('     ...')
        elif args.verbose:
            print(f"[OK] {os.path.basename(parser_path)}: No changes needed")
    
    print(f'\n{"Would update" if args.dry_run else "Updated"} {total_changes} file(s)')
    
    # Exit with appropriate code for CI/CD
    sys.exit(0 if total_changes == 0 or not args.dry_run else 1)


if __name__ == '__main__':
    main()
