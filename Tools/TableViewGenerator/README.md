# Table View Generator

A Python tool that generates Bicep templates to deploy KQL functions emulating table schemas using the `datatable` operator. This is useful for testing ASIM parsers, detection rules, and hunting queries against table schemas without requiring actual data.

## Features

- **Multiple input methods:**
  - Direct table names as parameters
  - Files containing comma or line-separated table names
  - JSON schema files (same format as KqlvalidationsTests\CustomTables)

- **Automatic schema lookup:** (in priority order)
  1. Local CustomTables folder - JSON schema files from `Azure-Sentinel/.script/tests/KqlvalidationsTests/CustomTables/` (800+ schemas)
  2. Azure Monitor log reference documentation (online)
  3. Microsoft Defender XDR advanced hunting schema (online)

- **Output formats:**
  - Bicep template (recommended)
  - ARM JSON template (alternative)
  - KQL-only output (for testing)

- **Caching:**
  - Caches online documentation lookups for 1 week
  - Speeds up repeated runs

- **Self-contained scripts:**
  - No external dependencies beyond Python standard library
  - Can be copied and run from any location

## Installation

Requires Python 3.9 or later.

The scripts use only Python standard library modules - no pip install required.

To use the scripts from a different location:
1. Copy `generate_table_views_templates.py` and/or `deploy_table_views.py` to your desired location
2. Use `--custom-tables-path` to specify where to find local schema files

## Usage

### Basic Usage - Table Names

```bash
# Generate view for a single table
python generate_table_views_templates.py --tables SigninLogs

# Generate views for multiple tables
python generate_table_views_templates.py --tables SigninLogs SecurityEvent DeviceEvents
```

### Using a Table List File

Create a file with table names (comma, semicolon, or newline separated):

```text
SigninLogs
SecurityEvent
DeviceEvents
AuditLogs
```

Then run:

```bash
python generate_table_views_templates.py --table-file tables.txt --output myViews.bicep
```

### Using JSON Schema Files

```bash
# Use existing schema files from CustomTables folder
python generate_table_views_templates.py --schema-files path/to/CustomTables/SigninLogs.json

# Use multiple schema files
python generate_table_views_templates.py --schema-files schema1.json schema2.json
```

### Output Formats

```bash
# Generate Bicep template (default)
python generate_table_views_templates.py --tables SigninLogs --format bicep

# Generate ARM JSON template
python generate_table_views_templates.py --tables SigninLogs --format arm

# Generate KQL-only output (for testing)
python generate_table_views_templates.py --tables SigninLogs --format kql
```

### Running from a Different Location

When running the scripts from outside the Azure-Sentinel repository, use `--custom-tables-path` to point to local schema files:

```bash
# Run from anywhere, pointing to the CustomTables folder
python /path/to/generate_table_views_templates.py \
  --tables SigninLogs SecurityEvent \
  --custom-tables-path /path/to/Azure-Sentinel/.script/tests/KqlvalidationsTests/CustomTables

# Or rely on online lookup only (no local schemas)
python generate_table_views_templates.py --tables SigninLogs SecurityEvent
```

### Cache Options

```bash
# Clear cache and fetch fresh content
python generate_table_views_templates.py --tables SigninLogs --refresh-cache

# Skip cache for this run only
python generate_table_views_templates.py --tables SigninLogs --skip-cache

# Set custom cache TTL (in seconds)
python generate_table_views_templates.py --tables SigninLogs --cache-ttl 86400
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `--tables`, `-t` | string[] | One or more table names to generate views for |
| `--table-file`, `-f` | string | Path to file containing table names |
| `--schema-files`, `-s` | string[] | Paths to JSON schema files |
| `--output`, `-o` | string | Output file path (default: `tableViews.bicep`) |
| `--format` | string | Output format: `bicep`, `arm`, or `kql` |
| `--custom-tables-path`, `-c` | string | Path to CustomTables folder |
| `--skip-online` | flag | Skip searching online documentation |
| `--prefix` | string | Prefix for saved search names (default: empty) |
| `--suffix` | string | Suffix for saved search names (default: empty) |
| `--refresh-cache` | flag | Clear cache before fetching |
| `--skip-cache` | flag | Don't use cache for this run |
| `--cache-ttl` | int | Cache time-to-live in seconds (default: 604800 = 1 week) |

## Deploying the Generated Template

### Using Azure CLI

```bash
az deployment group create \
  --resource-group <resource-group-name> \
  --template-file tableViews.bicep \
  --parameters WorkspaceResourceId=<workspace-resource-id>
```

### Using Azure PowerShell

```powershell
New-AzResourceGroupDeployment `
  -ResourceGroupName <resource-group-name> `
  -TemplateFile tableViews.bicep `
  -WorkspaceResourceId <workspace-resource-id>
```

## Deploy Script (Recommended)

The `deploy_table_views.py` script combines generation and deployment into a single command. It also **automatically checks for existing tables** in the workspace to prevent conflicts between function aliases and real tables.

### Why Use the Deploy Script?

- **Conflict detection:** Automatically skips tables that already exist in your workspace
- **Auto-redeploy:** Automatically deletes and redeploys existing functions (can be disabled with `--no-redeploy`)
- **Single command:** Generate and deploy in one step
- **Dry-run support:** Preview what would be deployed without making changes

### Basic Usage

```bash
# Deploy views for specific tables
python deploy_table_views.py \
  --workspace-id <workspace-guid> \
  --resource-id <full-workspace-resource-id> \
  --tables AWSCloudTrail AWSGuardDuty SecurityEvent

# With subscription (if not in default)
python deploy_table_views.py \
  --workspace-id 60d381d4-e3ea-4553-ad97-047d10b0025b \
  --resource-id "/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.OperationalInsights/workspaces/<ws-name>" \
  --subscription "My Subscription" \
  --tables AWSCloudTrail AWSGuardDuty
```

### Dry Run Mode

Preview what would be deployed without making changes:

```bash
python deploy_table_views.py \
  --workspace-id <workspace-guid> \
  --resource-id <full-workspace-resource-id> \
  --tables Table1 Table2 Table3 \
  --dry-run
```

### Deploy Script Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `--workspace-id`, `-w` | string | **Required.** Log Analytics workspace ID (GUID) |
| `--resource-id`, `-r` | string | **Required.** Full resource ID of the workspace |
| `--tables`, `-t` | string[] | Table names to deploy (mutually exclusive with other inputs) |
| `--table-file`, `-f` | string | File containing table names |
| `--schema-files`, `-s` | string[] | JSON schema files |
| `--subscription` | string | Azure subscription name or ID |
| `--resource-group`, `-g` | string | Resource group (auto-extracted from resource-id) |
| `--output`, `-o` | string | Save generated Bicep to file (optional) |
| `--dry-run` | flag | Preview deployment without executing |
| `--force` | flag | Deploy even if tables exist (may cause conflicts) |
| `--no-redeploy` | flag | Skip redeploying existing functions (default: redeploy) |
| `--skip-checks` | flag | Skip existing table/function checks (faster) |
| `--skip-online` | flag | Skip online schema lookup |
| `--custom-tables-path`, `-c` | string | Path to CustomTables folder |
| `--suffix` | string | Suffix for saved search names (default: empty) |
| `--refresh-cache` | flag | Clear schema cache before fetching |

### Example Output

```
==========================================
   Deploy Table Views to Log Analytics
==========================================

Workspace ID: 60d381d4-e3ea-4553-ad97-047d10b0025b
Resource Group: my-resource-group
Workspace Name: my-workspace

Checking for existing tables in workspace...
  Found 764 existing tables
Checking for existing functions...
  Found 279 existing functions

Requested tables: AWSCloudTrail, AWSGuardDuty, MyCustomTable

Skipping (already exist):
  - AWSCloudTrail (table exists)
  - AWSGuardDuty (table exists)

Tables to deploy: MyCustomTable

Fetching schemas...
  MyCustomTable: 25 columns

Generating Bicep template...
Deploying to Azure...
Deployment successful!
```

### Finding Your Workspace Details

To get your workspace ID and resource ID:

```bash
# List workspaces and get details
az monitor log-analytics workspace list --output table

# Get full resource ID for a specific workspace
az monitor log-analytics workspace show \
  --resource-group <rg-name> \
  --workspace-name <ws-name> \
  --query id --output tsv
```

## Schema File Format

The tool uses the same JSON format as the `CustomTables` folder:

```json
{
  "Name": "MyCustomTable",
  "Properties": [
    {
      "Name": "TimeGenerated",
      "Type": "datetime"
    },
    {
      "Name": "Computer",
      "Type": "string"
    },
    {
      "Name": "EventID",
      "Type": "int"
    },
    {
      "Name": "Properties",
      "Type": "dynamic"
    }
  ]
}
```

### Supported KQL Types

- `string`
- `datetime`
- `dynamic`
- `bool`
- `int`
- `long`
- `real`
- `guid`
- `timespan`
- `decimal`

## How It Works

1. **Schema Resolution:** For each table name, the tool:
   - First checks the local `CustomTables` folder for a matching JSON file
   - If not found and online search is enabled, queries Azure Monitor documentation
   - If still not found, queries Defender XDR documentation

2. **KQL Generation:** Creates a `datatable` expression matching the table schema:

   ```kql
   datatable(TimeGenerated:datetime, TenantId:string, SourceSystem:string, ...)[]
   ```

3. **Bicep Template:** Wraps each function in a Log Analytics saved search resource:

   ```bicep
   resource savedSearch0 'Microsoft.OperationalInsights/workspaces/savedSearches@2020-08-01' = {
     name: '${workspaceName}/SigninLogs_view'
     properties: {
       displayName: 'SigninLogs'
       category: 'TableViews'
       query: 'datatable(...)[]'
       functionAlias: 'SigninLogs'
     }
   }
   ```

## Examples

### Generate Views for ASIM Testing

```bash
# Generate views for common ASIM source tables
python generate_table_views_templates.py --tables \
    SecurityEvent \
    Syslog \
    CommonSecurityLog \
    AuditLogs \
    SigninLogs \
    DeviceProcessEvents \
    DeviceNetworkEvents \
    --output asim-test-views.bicep
```

### Generate All Defender XDR Tables

```bash
python generate_table_views_templates.py --tables \
    DeviceEvents \
    DeviceFileEvents \
    DeviceProcessEvents \
    DeviceNetworkEvents \
    DeviceLogonEvents \
    DeviceRegistryEvents \
    DeviceImageLoadEvents \
    AlertInfo \
    AlertEvidence \
    EmailEvents \
    IdentityLogonEvents \
    --output defender-views.bicep
```

## Troubleshooting

### Schema Not Found

If a table schema is not found:
1. Check if the table name is spelled correctly
2. Check if a JSON file exists in the CustomTables folder
3. Try without `--skip-online` to query online documentation
4. Use `--custom-tables-path` if running from a different location

### Online Lookup Fails

The online lookup uses web scraping and may fail if:
- Microsoft changes their documentation format
- Network connectivity issues
- Rate limiting

Solution: Use local JSON schema files instead, or try `--refresh-cache`.

### Bicep Deployment Errors

If deployment fails:
1. Ensure the workspace resource ID is correct
2. Check you have permissions to create saved searches
3. Verify function names don't conflict with existing functions

### Running from Different Location

If you're running the script from outside the Azure-Sentinel repository:
1. Use `--custom-tables-path` to point to your CustomTables folder
2. Or rely on online lookup for schemas (works without local files)
3. The `.cache` folder will be created next to the script

## Files

| File | Description |
|------|-------------|
| `generate_table_views_templates.py` | Main script to generate Bicep/ARM/KQL templates |
| `deploy_table_views.py` | Deploy script with conflict detection |
| `README.md` | This documentation |

## Contributing

To add new table schemas:
1. Create a JSON file in the `CustomTables` folder
2. Follow the schema format shown above
3. Submit a pull request

## Related Tools

- [TableCreator](../TableCreator/) - Creates actual Log Analytics tables from schemas
- [CustomTables](../../.script/tests/KqlvalidationsTests/CustomTables/) - Repository of table schemas

## Version History

- **1.4.0** - Consolidated single-file scripts
  - Renamed `generate_table_views.py` to `generate_table_views_templates.py`
  - Removed Helpers folder - all code is now inline
  - Scripts can be copied and run from any location
  - Added `--custom-tables-path` documentation for remote usage

- **1.3.0** - Deploy script added
  - New `deploy_table_views.py` for combined generation and deployment
  - Automatic detection of existing tables and functions
  - Prevents conflicts between function aliases and real tables
  - Dry-run mode for previewing deployments
  - Uses fast Tables API for workspace queries

- **1.2.0** - Python-only version
  - Removed PowerShell version
  - Added caching for online lookups
  - Simplified datatable output (empty brackets, no sample data)
  - Function alias uses table name directly

- **1.1.0** - Python version added
  - Full feature parity with PowerShell version
  - Additional ARM JSON and KQL-only output formats
  - Cross-platform support (Windows, macOS, Linux)

- **1.0.0** - Initial release
  - Table name, file, and JSON schema input support
  - Azure Monitor and Defender XDR online lookup
  - Bicep template generation
