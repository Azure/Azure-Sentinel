# 💡 tableCreator.ps1 (v2.5)

**Author:** Marko Lauren

![screenshot](https://github.com/user-attachments/assets/6732b1fb-b83a-4dcf-911b-6143e1098ec5)

## Purpose

`tableCreator.ps1` is a PowerShell script designed to streamline the process of duplicating the schema of an existing Microsoft Sentinel table and creating a new table with the same schema. Alternatively, you can bring your own schema via a JSON file (BYOS - bring-your-own-schema). The script supports Analytics, Data Lake, Auxiliary and Basic table types. This tool is ideal for scenarios such as streaming the logs to table with different/cheaper plan or splitting log to multiple tables.

## Key Features

- **Data Lake Table Creation:** Easily create new tables with the same schema as existing tables.
- **Schema Duplication:** Automatically capture and reuse the schema from any existing Sentinel table.
- **Bring-Your-Own-Schema (BYOS):** Create tables using a custom JSON schema file instead of copying from existing tables.
- **Flexible Table Types:** Supports Analytics, Data Lake, Auxiliary and Basic types.
- **Retention Settings:** Define both interactive and total retention periods for new tables.
- **Dynamic Column Handling:** Optionally convert dynamic columns to string for compatibility with Data Lake and Auxiliary tables.
- **Interactive & Command-Line Modes:** Use prompts for missing parameters or provide all options via command line.
- **Resource Targeting:** Specify your Sentinel workspace via parameter or prompt.
- **Tenant Selection:** Use `-TenantId` for authentication outside Azure Cloud Shell.

## Usage

### 1. Define Your Sentinel Resource ID

To obtain full resource ID, go to log analytics workspace and either choose "JSON view" in overview or go to "Properties".<br>
You can provide the resource ID in two ways:

- **Command-Line:**  
  ```
  .\tableCreator.ps1 -FullResourceId "/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/providers/Microsoft.OperationalInsights/workspaces/<WORKSPACE_NAME>"
  ```
- **Script Modification:**  
  Edit the script and set:
  ```powershell
  $resourceId = "/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/providers/Microsoft.OperationalInsights/workspaces/<WORKSPACE_NAME>"
  ```

If not provided, the script will prompt you for the resource ID.

### 2. Run the Script

You can run the script interactively or with full command-line parameters.

#### Interactive Mode

Run:
```
.\tableCreator.ps1
```
You will be prompted for the source table name, new table name, table type, and retention settings.

#### Command-Line Mode

Specify all required parameters:
```
.\tableCreator.ps1 -FullResourceId <RESOURCE_ID> -tableName <SourceTable> -newTableName <NewTable> -type <datalake|dl|analytics|basic|aux|auxiliary> -retention <Days> -totalRetention <Days> [-ConvertToString] [-TenantId <TenantId>]
```

**Examples:**
```
.\tableCreator.ps1 -tableName MyTable -newTableName MyAnalyticsTable_CL -type analytics -retention 180 -totalRetention 365
.\tableCreator.ps1 -tableName MyTable -newTableName MyDLTable_CL -type datalake -totalRetention 365
.\tableCreator.ps1 -tableName MyTable -newTableName MyAuxTable_CL -type aux -totalRetention 365 -ConvertToString
```

#### Bring Your Own Schema (BYOS) Mode

Create tables using a custom JSON schema file:
```
.\tableCreator.ps1 -SchemaFile <path-to-schema.json> -newTableName <NewTable> -type <datalake|dl|analytics|basic|aux|auxiliary> -retention <Days> -totalRetention <Days>
```

**Example:**
```
.\tableCreator.ps1 -SchemaFile mySchema.json -newTableName MyCustomTable_CL -type datalake -totalRetention 365
```

The schema file should be a JSON array containing objects with `name` and `type` properties:
```json
[
  {"name": "TimeGenerated", "type": "datetime"},
  {"name": "Action", "type": "string"},
  {"name": "Status", "type": "int"}
]
```

### Parameters

- `-FullResourceId` : Full Azure Resource ID of the Sentinel workspace.
- `-tableName` : Name of the existing table to copy schema from (not required when using `-SchemaFile`).
- `-newTableName` : Name for the new table.
- `-type` : Table type (`analytics`, `datalake`/`dl`, `auxiliary`/`aux`, `basic`).
- `-retention` : Interactive/analytics retention in days.
- `-totalRetention` : Total retention in days.
- `-ConvertToString` : (Optional) Convert dynamic columns to string (recommended for Data Lake and Auxiliary tables).
- `-SchemaFile` : (Optional) Path to JSON schema file for Bring Your Own Schema (BYOS) functionality.
- `-TenantId` : (Optional) Azure tenant ID for authentication.

## Notes

- The script uses KQL `getschema` to retrieve table schemas. Columns of type `guid` are reported as `string` due to unknown reason. If the table you're creating a copy has guid type column(s) it causes a mismatch with column types when creating DCR. Workaround is to modify DCR with transformKql:
"transformKql": "source | extend SomeGuid = tostring(SomeGuid), AnotherGuid = tostring(AnotherGuid)"
Another workaround is to debug the script and interpret those columns on the fly. This is already done for SecurityEvent and SigninLogs table.

---
