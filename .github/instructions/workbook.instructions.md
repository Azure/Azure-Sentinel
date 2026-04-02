---
applyTo: "Workbooks/*.json,Solutions/**/Workbooks/*.json"
---

# Workbook Instructions

## Overview

Workbooks are interactive Azure Monitor visualization templates that provide comprehensive dashboards for monitoring, analyzing, and visualizing security data in Microsoft Sentinel. These instructions provide guidelines for creating, validating, and deploying workbooks with consistent quality standards.

## Workbook JSON Structure

### Required Top-Level Fields

Every workbook JSON file must include these essential fields:

```json
{
  "version": "Notebook/1.0",
  "items": [ /* workbook content items */ ],
  "fallbackResourceIds": [],
  "fromTemplateId": "sentinel-WorkbookName",
  "$schema": "https://github.com/Microsoft/Application-Insights-Workbooks/blob/master/schema/workbook.json"
}
```

#### version
- **Required**: Yes (all workbooks)
- **Value**: Must be exactly `"Notebook/1.0"`
- **Purpose**: Specifies the workbook format version
- **Rules**: Cannot be changed or omitted

#### items
- **Required**: Yes (all workbooks)
- **Type**: Array of item objects
- **Rules**:
  - Can contain any valid workbook items (type 1-12+)
  - Minimum 1 item required (typically at least a header and visualization)
  - Each item represents a section, visualization, parameter, or content block
  - Order matters - items render in array sequence
- **Valid Item Types**:
  - Type 1: Text/Markdown content
  - Type 3: KQL queries and visualizations
  - Type 9: Parameter controls
  - Type 12: Notebook groups (containers)

#### fallbackResourceIds
- **Required**: No (optional field)
- **Type**: Array (must be empty)
- **Format**: 
  - Must be empty array: `[]`
- **Purpose**: Reserved field for future extensibility
- **Rules**:
  - Should ALWAYS be an empty array `[]`
  - Must NOT contain any workspace resource IDs or identifying information
  - Users will explicitly select their workspace when opening the workbook
  - Do not include any Azure resource information in this field

#### fromTemplateId
- **Required**: Yes (all workbooks)
- **Format**: `sentinel-<workbook-name>` where workbook name can be:
  - Pure kebab-case: `sentinel-security-operations-efficiency`
  - Vendor name + workbook type: `sentinel-CriblWorkbook`, `sentinel-BarracudaCloudFirewall`
- **Naming Convention**: `sentinel-` prefix followed by workbook name
- **Examples**:
  - `sentinel-security-operations-efficiency` (all lowercase kebab-case)
  - `sentinel-CriblWorkbook` (vendor + workbook type)
  - `sentinel-BarracudaCloudFirewall` (vendor + workbook type)
  - `sentinel-auth0-activity-analysis` (all lowercase kebab-case)
- **Rules**:
  - Must start with `sentinel-`
  - After `sentinel-`, use either: all lowercase with hyphens (kebab-case) OR vendor name with workbook descriptor
  - Match workbook display name appropriately
  - Should correspond to workbook filename (without .json)

#### $schema
- **Required**: Yes (all workbooks)
- **Value**: Must be exactly:
  ```
  https://github.com/Microsoft/Application-Insights-Workbooks/blob/master/schema/workbook.json
  ```
- **Purpose**: Points to the JSON schema validation reference
- **Rules**: Cannot be changed or omitted

### Complete Minimal Workbook Example

```json
{
  "version": "Notebook/1.0",
  "items": [
    {
      "type": 1,
      "content": {
        "json": "# Workbook Title\nWelcome to your workbook"
      },
      "name": "text - header"
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "SecurityIncident\n| summarize Count=count() by Severity\n| render barchart",
        "size": 1,
        "queryType": 0,
        "resourceType": "microsoft.operationalinsights/workspaces"
      },
      "name": "query - incidents by severity"
    }
  ],
  "fallbackResourceIds": [],
  "fromTemplateId": "sentinel-MyWorkbook",
  "$schema": "https://github.com/Microsoft/Application-Insights-Workbooks/blob/master/schema/workbook.json"
}
```

## Best Practices

### Workbook Organization
1. **Header Section**: Main headline identifying workbook
2. **Parameters Section**: All parameter controls grouped early
3. **Summary/KPI Section**: Key metrics and high-level overview
4. **Content Sections**: Visualizations organized by business area
5. **Details Section**: Detailed tables and drill-down data
6. **Help Section**: Documentation and usage guidance (conditionally visible)

### Naming Conventions
- **Item Names**: Clear, descriptive (e.g., "Security Incidents Overview")
- **Parameter IDs**: PascalCase (e.g., `DefaultWorkspace`, `TimeRange`, `SeverityFilter`)
- **Custom Width**: `"100"` (full), `"67"` (two-thirds), `"50"` (half), `"33"` (third)

## Parameters and Queries

### Required Parameters

**Time Range (Type 4):**
```json
{
  "type": 4,
  "name": "TimeRange",
  "isRequired": true,
  "value": {"durationMs": 2592000000},
  "typeSettings": {
    "selectableValues": [
      {"durationMs": 14400000},
      {"durationMs": 604800000},
      {"durationMs": 2592000000}
    ],
    "allowCustom": true
  }
}
```

### Optional Parameters (Type 2 Multi-Select, Type 10 Toggle)
Use dropdowns for filtering and toggles for conditional display of help sections.

### KQL Query Guidelines
- Filter early in queries to reduce processing
- Use `summarize arg_max()` for latest records
- Add time range filtering: `where TimeGenerated >= {TimeRange:start}`
- Support "Select All" pattern: `where Status in ({Status}) or "*" in ({Status})`
- Parse JSON safely: `extend Metadata = todynamic(AdditionalData)`
- Handle nulls: `case(isempty(Owner), "Unassigned", Owner)`

### Chart Types
| Type | Use Case | Data Format |
|------|----------|-------------|
| **linechart** | Trends over time | Time series |
| **barchart** | Ranking, comparisons | Category, value |
| **unstackedbar** | Multiple series | Category, series, value |
| **piechart** | Part-to-whole | Category, value |
| **tiles** | KPIs, metrics | Value |
| **table** | Detailed records | Multiple columns |

## Metadata and Submission

All workbooks require a `WorkbooksMetadata.json` entry following this structure:

```json
{
  "workbookKey": "UniqueIdentifier",
  "title": "Workbook Title",
  "description": "Complete description of purpose and insights",
  "version": "1.0.0",
  "provider": "Microsoft",
  "templateRelativePath": "WorkbookName.json",
  "logoFileName": "Workbooks/Images/Logo/VendorLogo.svg",
  "previewImagesFileNames": [
    "Workbooks/Images/Preview/VendorNameWhite.png",
    "Workbooks/Images/Preview/VendorNameBlack.png"
  ],
  "dataTypeDependencies": ["CommonSecurityLog"],
  "dataConnectorsDependencies": ["DataConnectorId"],
  "firstPublishDate": "2024-01-01",
  "lastPublishDate": "2024-01-01",
  "source": {"kind": "Community"},
  "TemplateSpec": true
}
```

**Key Field Requirements:**
- **workbookKey**: Unique, camelCase (e.g., `barracudaCloudFirewall`)
- **title**: Clear name (50-100 chars), no parentheses
- **description**: Explains purpose, data, and insights (50+ chars)
- **version**: Semantic versioning (X.Y.Z format, e.g., `1.0.0`). This is the metadata/template version and is independent from the workbook JSON top-level `version` field (which is fixed as `"Notebook/1.0"`). Increment this version when you make changes to the workbook content.
- **templateRelativePath**: Just the workbook filename (e.g., `AWSSecurityHubComplianceWorkbook.json`), NOT the full path. The metadata system resolves paths based on metadata location automatically:
  - If metadata is in `WorkbooksMetadata.json` (root): resolver looks in `Workbooks/`
  - If metadata is in `Solutions/SolutionName/metadata-template.json`: resolver looks in `Solutions/SolutionName/Workbooks/`
- **lastPublishDate**: Update to current date (ISO 8601: YYYY-MM-DD) when making changes
- **dataTypeDependencies**: `["CommonSecurityLog"]`, `["Syslog"]`, `["SecurityIncident"]`, or exact `["CustomLog_CL"]` names
- **dataConnectorsDependencies**: Matches data connector ID exactly
- **Standalone workbooks**: Include `"source": {"kind": "Community"}`

**Version Updates (CRITICAL):**
- Change to workbook JSON → increment metadata version
- Bug fix/optimization → PATCH (1.0.0 → 1.0.1)
- New feature/enhancement → MINOR (1.0.0 → 1.1.0)
- Breaking changes → MAJOR (1.0.0 → 2.0.0)

**Images:**
- Logo: SVG in `Workbooks/Images/Logo/` (required for ISV)
- Previews: PNG in `Workbooks/Images/Preview/` (white and black backgrounds)
- Filenames must match metadata exactly

**Folder Structure:**
- **Standalone**: `Workbooks/`
- **Solution**: `Solutions/VendorName/Workbooks/` 

## Validation Issues and Common Errors

| Issue | Cause | Solution |
|-------|-------|----------|
| Invalid workbook JSON | Missing required top-level fields | Include version, items, fromTemplateId, $schema; ensure fallbackResourceIds is empty array |
| fromTemplateId incorrect | Wrong format or naming | Use format: `sentinel-workbookname` (kebab-case) |
| Version mismatch | Confusion about metadata version vs. workbook JSON version | Metadata `version` uses SemVer (1.0.0); workbook JSON `version` is fixed as `"Notebook/1.0"`. These are independent fields. |
| Metadata version not incremented | Changes made to workbook but version unchanged | Increment version in metadata (PATCH, MINOR, or MAJOR depending on change) |
| lastPublishDate not updated | Workbook updated but date not refreshed | Update `lastPublishDate` to current date (ISO 8601: YYYY-MM-DD) |
| Workbook not in gallery | Metadata not included in PR | Include WorkbooksMetadata.json file |
| Query execution errors | Syntax errors in KQL | Validate all queries; check parameter references |
| Logo not displaying | Wrong file format or path | Use SVG format; verify logoFileName path |
| Preview images missing | Files not in correct location | Place PNG files in Workbooks/Images/Preview/ |
| Parameters not filtering | Missing parameter references in queries | Add `{ParameterName}` to query where clauses |
| Charts not rendering | Visualization configuration issue | Verify query returns expected data structure |
| Metadata validation fails | Field format or required field missing | Check all required fields; validate JSON format |

## JSON Schema Validation

### Full Schema Example with Validation
```json
{
  "version": "Notebook/1.0",
  "items": [
    {
      "type": 1,
      "content": {
        "json": "## Workbook Title"
      },
      "name": "text - header"
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "SecurityIncident | summarize count()",
        "size": 1,
        "queryType": 0,
        "resourceType": "microsoft.operationalinsights/workspaces"
      },
      "name": "query - incidents"
    }
  ],
  "fallbackResourceIds": [],
  "fromTemplateId": "sentinel-MyWorkbook",
  "$schema": "https://github.com/Microsoft/Application-Insights-Workbooks/blob/master/schema/workbook.json"
}
```

### Validation Rules Summary

| Field | Required | Type | Valid Values | Notes |
|-------|----------|------|--------------|-------|
| `version` | Yes | String | `"Notebook/1.0"` | Must be exactly this value |
| `items` | Yes | Array | Any valid items | Minimum 1 item required |
| `fallbackResourceIds` | No (Optional) | Array | `[]` (empty only) | Must always be empty array, no workspace information |
| `fromTemplateId` | Yes | String | `sentinel-*` (kebab-case or vendor-style) | Must start with `sentinel-`, followed by either all lowercase kebab-case or vendor name with workbook descriptor |
| `$schema` | Yes | String | GitHub schema URL | Exact URL required |

## PR Description Template

When submitting workbook PR, include:

```markdown
## Workbook Addition: [Workbook Name]

### Description
Brief description of the workbook purpose and value.

### Data Dependencies
- Data Types: CommonSecurityLog, Syslog (as applicable)
- Data Connectors: [List connector names]

### Content
- Number of visualizations: [#]
- Parameters included: [List key parameters]
- Key metrics: [List main KPIs/metrics]

### Files Included
- [ ] WorkbookName.json
- [ ] WorkbooksMetadata.json
- [ ] Logo file (Workbooks/Images/Logo/)
- [ ] Preview images (Workbooks/Images/Preview/)

### JSON Validation
- [ ] version: "Notebook/1.0" present
- [ ] items: Array with valid items
- [ ] fallbackResourceIds: Empty array `[]` (no workspace information included)
- [ ] fromTemplateId: sentinel-workbookname format
- [ ] $schema: GitHub schema URL included

### Metadata Validation
- [ ] lastPublishDate updated to current date (ISO 8601: YYYY-MM-DD)
- [ ] Version incremented if workbook changed (PATCH/MINOR/MAJOR per change type)
- [ ] All metadata fields updated to reflect workbook changes
```
