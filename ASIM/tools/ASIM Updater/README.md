# ASIM Schema Updater Tools

This directory contains tools to maintain ASIM (Advanced Security Information Model) schema consistency across the Azure-Sentinel repository.

## Tools

### update_empty_parsers.py

Updates empty parser YAML files (`vim*Empty.yaml`) to match the field definitions in `ASIM/dev/ASimTester/ASimTester.csv`.

**Key Features:**
- **Surgical edits**: Instead of regenerating entire datatables, makes minimal changes (add, remove, modify) for easier code review
- **Preserves formatting**: Maintains the existing code style and comments
- **Schema-aware**: Handles schema inheritance (Common fields apply to all schemas)
- **Dry-run support**: Preview changes before applying them

**Usage:**

```bash
# Preview changes (dry-run)
python update_empty_parsers.py --dry-run

# Apply changes to all empty parsers
python update_empty_parsers.py

# Update a specific parser
python update_empty_parsers.py --parser "/path/to/vimAuditEventEmpty.yaml"

# Verbose output
python update_empty_parsers.py --verbose
```

**Options:**
- `--repo-root`: Root directory of the Azure-Sentinel repository (auto-detected if not specified)
- `--csv-path`: Path to ASimTester.csv (auto-detected if not specified)
- `--dry-run`: Show what would be changed without making changes
- `--parser`: Update only the specified parser file
- `--verbose`, `-v`: Show detailed output including files with no changes

## GitHub Workflow

The tools are automatically run via GitHub Actions:
- **Scheduled**: Weekly on Sundays at midnight UTC
- **On push**: When relevant files are changed (CSV schema or empty parsers)

See `.github/workflows/asim-schema-updater.yml` for the workflow configuration.

## Schema Source

The canonical schema definitions are in `ASIM/dev/ASimTester/ASimTester.csv`, which contains:
- `ColumnName`: Field name
- `ColumnType`: Data type (string, int, datetime, etc.)
- `Class`: Field class (Mandatory, Recommended, Optional, Conditional, Alias)
- `Schema`: Schema name (AuditEvent, NetworkSession, Dns, etc.)
- `LogicalType`: Logical type hint
- `ListOfValues`: Allowed values for enumerated fields
- `Aliased`: Field this is an alias for (if Class is Alias)

## Empty Parsers

Empty parsers are located at:
```
Parsers/ASim*/Parsers/vim*Empty.yaml
```

They define the schema structure using an empty KQL datatable and are used for:
- Schema validation
- Union operations in parsers
- Documentation generation
