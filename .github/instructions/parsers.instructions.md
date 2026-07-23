---
applyTo: "**/Solutions/**/Parsers/*.yaml, **/Solutions/**/Parsers/*.yml"
---

# Parser File Validation Instructions

## Overview
This document provides validation guidelines for parser files in Azure Sentinel Solutions. Parsers are KQL (Kusto Query Language) functions stored in YAML format within solution folders.

> **Important**: Parser files are located in `Solutions/<SolutionName>/Parsers/` directory and follow a standardized YAML format.

---

## Parser File Structure

All parser files must be YAML files (`.yaml` extension) with the following mandatory structure:

```yaml
id: <UUID>
Function:
  Title: <string>
  Version: '<version>'
  LastUpdated: '<date>'
Category: Microsoft Sentinel Parser
FunctionName: <string>
FunctionAlias: <string>
FunctionQuery: |
  <KQL Query>
```

---

## Validation Rules

### 1. File Naming
- **Rule**: Parser file names must have `.yaml` extension
- **Example**: `AIShield.yaml`, `AkamaiSIEMEvent.yaml`
- **Validation**: `[ERROR]` if file extension is not `.yaml`

### 2. File Location
- **Rule**: Parser files must be located in `Solutions/<SolutionName>/Parsers/` directory
- **Example**: `Solutions/AIShield AI Security Monitoring/Parsers/AIShield.yaml`
- **Validation**: `[ERROR]` if file is located outside the `Parsers` folder within a solution

### 3. Required Fields

#### 3.1 ID Field
- **Rule**: Must contain a valid UUID (v4 format)
- **Format**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **Example**: `574a5c4d-051c-41c8-83a9-f06962e14d85`
- **Validation**: 
  - `[ERROR]` if `id` field is missing
  - `[ERROR]` if `id` is not a valid UUID format
  - `[WARNING]` if UUID is replicated across multiple files

#### 3.2 Function Section
All fields under `Function:` are mandatory:

| Field | Type | Rules | Example |
|-------|------|-------|---------|
| `Title` | string | Required, descriptive text | `Parser for AIShield` |
| `Version` | string | SemVer format (quoted) | `'1.0.1'` |
| `LastUpdated` | string | ISO 8601 date format (quoted) | `'2023-12-21'` |

- **Validation**: 
  - `[ERROR]` if any of these fields are missing
  - `[ERROR]` if `Version` is not in SemVer format (e.g., not `'X.Y.Z'`)
  - `[WARNING]` if `LastUpdated` is older than 1 year from current date
  - `[WARNING]` if `LastUpdated` is in the future

#### 3.3 Category Field
- **Rule**: Must be exactly `Microsoft Sentinel Parser` (case-sensitive)
- **Validation**: `[ERROR]` if category value differs from the required string

#### 3.4 FunctionName
- **Rule**: Must be a valid KQL function name (alphanumeric, no special characters except `_`)
- **Pattern**: `^[a-zA-Z_][a-zA-Z0-9_]*$`
- **Validation**: 
  - `[ERROR]` if FunctionName contains invalid characters
  - `[WARNING]` if FunctionName is duplicated in the same solution

#### 3.5 FunctionAlias
- **Rule**: Should typically match `FunctionName` for consistency
- **Validation**: 
  - `[WARNING]` if `FunctionAlias` does not match `FunctionName`

#### 3.6 FunctionQuery
- **Rule**: Must contain valid KQL code
- **Requirements**:
  - After optional `let` bindings, the query must reference a table (e.g., `CommonSecurityLog`, `AIShield_CL`)
  - Cannot be empty
  - Should use `|` for piping operators
  - Multi-line queries should use the `|` separator with proper indentation
- **Validation**:
  - `[ERROR]` if `FunctionQuery` is empty or missing
  - `[ERROR]` if `FunctionQuery` contains syntax errors (missing pipes, unclosed quotes)
  - `[ERROR]` if query doesn't reference a valid table
  - `[WARNING]` if query is overly complex (>50 lines without comments)
  - `[WARNING]` if query uses deprecated KQL functions

---

## Multi-Table Parser Examples

### Example 1: Simple Parser (Single Table)
```yaml
id: 9db78fa7-e565-45ee-8478-e562630b084a
Function:
  Title: Parser for AkamaiSIEMEvent
  Version: '1.0.0'
  LastUpdated: '2023-08-23'
Category: Microsoft Sentinel Parser
FunctionName: AkamaiSIEMEvent
FunctionAlias: AkamaiSIEMEvent
FunctionQuery: |
  CommonSecurityLog 
  | where DeviceVendor == 'Akamai'
  | where DeviceProduct == 'akamai_siem'
  | extend EventVendor = 'Akamai'
  | project TimeGenerated, EventVendor, EventProduct
```

### Example 2: Parser with Custom Transformations
```yaml
id: 574a5c4d-051c-41c8-83a9-f06962e14d85
Function:
  Title: Parser for AIShield
  Version: '1.0.1'
  LastUpdated: '2023-12-21'
Category: Microsoft Sentinel Parser
FunctionName: AIShield
FunctionAlias: AIShield
FunctionQuery: |
  AIShield_CL
  | extend EventVendor = 'Bosch'
  | extend EventProduct = 'AIShield'
  | extend Severity = iff(probability_d > 0.50, "High", "Low")
  | project-rename AttackName = attack_name_s
  | project TimeGenerated, EventVendor, Severity
```

### Example 3: Parser with Lookup Tables (Datatable)
```yaml
id: 8121523a-4ceb-4fe9-abd9-da65a319f459
Function:
  Title: Parser for afad_parser
  Version: '1.0.0'
  LastUpdated: '2023-08-23'
Category: Microsoft Sentinel Parser
FunctionName: afad_parser
FunctionAlias: afad_parser
FunctionQuery: |
  let CodeTable = datatable(Code: string, Meaning: string) [
    "C-ADM-ACC-USAGE", "Recent use of administrator account",
    "C-PASSWORD-DONT-EXPIRE", "Never expiring passwords"
  ];
  afad_events_CL
  | lookup CodeTable on $left.alert_code_s == $right.Code
  | project TimeGenerated, alert_code_s, Meaning
```

---

## Validation Error/Warning Summary

### Error Messages (Must Fix)
| Error Code | Description | Fix |
|-----------|-------------|-----|
| FILE_EXT_001 | File extension is not `.yaml` | Rename file to `.yaml` |
| FILE_LOC_001 | Parser not in `Parsers` folder | Move file to `Solutions/<Solution>/Parsers/` |
| ID_MISSING_001 | Missing `id` field | Add valid UUID |
| ID_INVALID_001 | Invalid UUID format | Use valid UUID v4 format |
| FUNC_MISSING_001 | Missing `Function` section | Add `Function:` with required fields |
| FUNC_FIELD_MISSING_001 | Missing required field in Function | Add `Title`, `Version`, `LastUpdated` |
| VERSION_FORMAT_001 | Invalid version format | Use SemVer format (e.g., `'1.0.0'`) |
| CATEGORY_001 | Invalid category value | Use `Microsoft Sentinel Parser` exactly |
| FUNCNAME_INVALID_001 | FunctionName has invalid characters | Use alphanumeric and `_` only |
| QUERY_EMPTY_001 | FunctionQuery is empty | Add valid KQL query |
| QUERY_SYNTAX_001 | KQL syntax errors detected | Fix query syntax (pipes, quotes, operators) |

### Warning Messages (Recommended Fixes)
| Warning Code | Description | Recommendation |
|-------------|-------------|-----------------|
| LAST_UPDATE_001 | LastUpdated is > 1 year old | Update date to current version |
| LAST_UPDATE_002 | LastUpdated is in the future | Correct date to today or before |
| ALIAS_MISMATCH_001 | FunctionAlias differs from FunctionName | Keep consistent for clarity |
| DUP_FUNCNAME_001 | Duplicate FunctionName in solution | Use unique names |
| DUP_UUID_001 | UUID used in multiple files | Generate unique UUID for each file |

---

## Validation Checklist

Use this checklist when creating or updating parser files:

- [ ] File is in `Solutions/<SolutionName>/Parsers/` directory
- [ ] File has `.yaml` extension
- [ ] Contains valid UUID in `id` field
- [ ] `Function.Title` is descriptive and non-empty
- [ ] `Function.Version` follows SemVer format (e.g., `'1.0.0'`)
- [ ] `Function.LastUpdated` is in ISO 8601 format and current
- [ ] `Category` is exactly `Microsoft Sentinel Parser`
- [ ] `FunctionName` uses valid KQL naming (alphanumeric + underscore)
- [ ] `FunctionAlias` matches `FunctionName` (recommended)
- [ ] `FunctionQuery` contains valid KQL code and is non-empty
- [ ] Query references a table after optional `let` bindings
- [ ] Query uses proper pipe operators and formatting
- [ ] No duplicate UUIDs across solutions
- [ ] No duplicate function names within same solution
- [ ] YAML syntax is valid (proper indentation, no syntax errors)

---

## Common Issues & Fixes

### Issue 1: Invalid YAML Syntax
**Problem**: File doesn't parse as valid YAML (missing colon after key)
```yaml
id: 574a5c4d-051c-41c8-83a9-f06962e14d85
Function  Title: Parser Name
```
**Fix**: Ensure proper YAML syntax with colons after keys:
```yaml
id: 574a5c4d-051c-41c8-83a9-f06962e14d85
Function:
  Title: Parser Name
```

### Issue 2: Incorrect Version Format
**Problem**: Version not in SemVer format
```yaml
Version: 1.0  # Missing patch version
```
**Fix**: Add patch version:
```yaml
Version: '1.0.0'
```

### Issue 3: Missing Quotes on Version/Date
**Problem**: Version treated as number instead of string
```yaml
Version: 1.0.1
LastUpdated: 2023-12-21
```
**Fix**: Add quotes to ensure string type:
```yaml
Version: '1.0.1'
LastUpdated: '2023-12-21'
```

### Issue 4: Empty Query
**Problem**: FunctionQuery has no content
```yaml
FunctionQuery: |
```
**Fix**: Add valid KQL query:
```yaml
FunctionQuery: |
  TableName
  | where TimeGenerated > ago(7d)
```

---

## Best Practices

1. **Consistency**: Keep function naming consistent with solution naming convention
2. **Documentation**: Use descriptive titles that explain parser purpose
3. **Version Management**: Update version number for any changes to the query
4. **Date Maintenance**: Keep `LastUpdated` current to indicate active maintenance
5. **Query Readability**: Format KQL queries with proper indentation and line breaks
6. **Testing**: Validate KQL syntax in Log Analytics before committing
7. **Uniqueness**: Ensure each parser has a unique UUID and function name

---
