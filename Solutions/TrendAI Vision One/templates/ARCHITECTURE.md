# Sentinel Connector Architecture

This document describes the modular architecture used for both **Workbench** and **OAT** connectors.

## Overview

Both connectors follow Microsoft's recommended **Codeless Connector Platform (CCP)** pattern with modular components, enabling:

- ✅ Single-click deployment via "Deploy to Azure" button
- ✅ Independent component testing and updates
- ✅ Proper dependency management
- ✅ Custom Azure Portal deployment UI

## Directory Structure

```
templates/
├── workbench/                          # Workbench Alerts Connector
│   ├── mainTemplate.json               # Orchestrator
│   ├── createUiDefinition.json         # Custom Portal UI
│   └── components/
│       ├── sentinel-solution.json      # Enables Sentinel
│       ├── table.json                  # 56 columns
│       ├── dce.json                    # Data Collection Endpoint
│       ├── dcr.json                    # Data Collection Rule + transform
│       ├── connector-definition.json   # Portal UI definition
│       └── parser-function.json        # KQL parser for IOC extraction
│
├── oat/                                # OAT Connector
│   ├── mainTemplate.json               # Orchestrator
│   ├── createUiDefinition.json         # Custom Portal UI
│   └── components/
│       ├── sentinel-solution.json      # Enables Sentinel
│       ├── table.json                  # 139 columns
│       ├── dce.json                    # Data Collection Endpoint
│       ├── dcr.json                    # Data Collection Rule + transform
│       ├── connector-definition.json   # Portal UI definition
│       └── parser-function.json        # Universal parser (old + new OAT data)
│
└── legacy/                             # Archived old templates
```

## Component Architecture

### 1. mainTemplate.json (Orchestrator)

**Purpose**: Entry point for "Deploy to Azure" button that orchestrates all component deployments.

**How it works**:
- Uses nested deployments to call each component template
- Components hosted on GitHub (linked templates)
- Manages dependency chain automatically
- Passes outputs between components

**Key sections**:
```json
{
  "variables": {
    "baseUrl": "https://raw.githubusercontent.com/trendmicro/..."
  },
  "resources": [
    {
      "type": "Microsoft.Resources/deployments",
      "properties": {
        "templateLink": {
          "uri": "[concat(variables('baseUrl'), '/sentinel-solution.json')]"
        }
      }
    }
  ]
}
```

### 2. createUiDefinition.json (Portal UI)

**Purpose**: Custom deployment experience in Azure Portal.

**Features**:
- Workspace dropdown (auto-populated from subscription)
- Region selector for Trend Vision One
- Validation and tooltips
- Post-deployment instructions

**User experience**:
1. User clicks "Deploy to Azure"
2. Portal loads this UI definition
3. User fills simple form (workspace + region)
4. Deployment starts automatically

### 3. Components

#### A. sentinel-solution.json

Deploys Microsoft Sentinel solution to enable Sentinel on workspace.

**Resource**: `Microsoft.OperationsManagement/solutions`

**Outputs**: `solutionId`

#### B. table.json

Creates custom log table with schema.

**Resource**: `Microsoft.OperationalInsights/workspaces/tables`

**Schemas**:
- **Workbench**: 56 columns (core fields + IOCs + dynamic columns)
- **OAT**: 139 columns (all detail_* fields flattened)

**Outputs**: `tableName`, `tableId`

#### C. dce.json

Creates Data Collection Endpoint for log ingestion.

**Resource**: `Microsoft.Insights/dataCollectionEndpoints`

**Outputs**: `dceId`, `dceName`, `dceEndpoint`

#### D. dcr.json

Creates Data Collection Rule with transformation.

**Resource**: `Microsoft.Insights/dataCollectionRules`

**Key features**:
- Stream declaration (input schema from API)
- TransformKql (maps API response → table schema)
- Routes data to Log Analytics workspace

**Workbench transform example**:
```kql
source 
| extend TimeGenerated = todatetime(createdDateTime)
| extend workbenchId_s = tostring(id)
| extend severity_s = tostring(severity)
| extend indicators = indicators
| extend entities = impactScope.entities
```

**OAT transform** (very large):
- Flattens entire `detail` dynamic object
- 130+ field mappings
- Converts Unix timestamps to datetime

**Outputs**: `dcrId`, `dcrImmutableId`, `streamName`

#### E. connector-definition.json

Creates connector UI in Sentinel portal.

**Resource**: `Microsoft.OperationalInsights/workspaces/providers/dataConnectorDefinitions`

**Kind**: `Customizable`

**Includes**:
- UI configuration (title, description, instructions)
- Sample queries
- Connectivity criteria
- Graph queries

**Note**: Connection details (API endpoint, auth, paging) are configured manually in the Portal after deployment.

**Outputs**: `connectorId`

#### F. parser-function.json (Workbench and OAT)

Deploys a KQL saved function. Both connectors ship one, and both are **universal** —
they auto-detect the data shape and return one stable schema across old (legacy V1
Azure Function) and new (CCF) data.

**Resource**: `Microsoft.OperationalInsights/workspaces/savedSearches`

**Workbench function**: `TrendMicroWorkbench_Complete()` — extracts IOCs from the dynamic
columns (indicators, entities, matchedRules), falling back to the stringified `*_s`
columns for old data.

```kql
TrendMicroWorkbench_Complete()
| where severity_s == "critical"
| where isnotempty(FileHashValue_s)
```

**OAT function**: `TrendMicroOAT_Complete()` — returns the full flat `detail_*` schema,
preferring the typed flat column and falling back to re-deriving each field from the
detail payload (`detail` dynamic, `detail_s` string, or `RawData`). Adds convenience
columns `mitreTacticIds_s` / `mitreTechniqueIds_s`.

```kql
TrendMicroOAT_Complete()
| where detail_filterRiskLevel_s == "high"
| project TimeGenerated, detail_endpointHostName_s, detail_processCmd_s
```

**Outputs**: `functionName`

## Deployment Flow

```
User clicks "Deploy to Azure" button
        ↓
Azure Portal loads:
  - mainTemplate.json
  - createUiDefinition.json
        ↓
User fills form:
  - Selects workspace (dropdown)
  - Selects Trend region (dropdown)
        ↓
Deployment begins:
  1. sentinel-solution       ✓
  2. table                   ✓ (depends on #1)
  3. dce                     ✓ (parallel with #2)
  4. dcr                     ✓ (depends on #2, #3)
  5. connector-definition    ✓ (depends on #1, #4)
  6. parser-function         ✓ (depends on #2; Workbench + OAT)
        ↓
Deployment complete (3-5 min)
        ↓
User manually connects in Portal:
  - Sentinel → Data connectors
  - Enter API token
  - Click Connect
```

## Dependency Chain

### Workbench

```
sentinel-solution
    ↓
table ───────┐
    ↓        │
    ↓    dce │
    ↓     ↓  │
    └──→ dcr │
         ↓   │
connector-definition
         ↓
    parser-function
```

### OAT

```
sentinel-solution
    ↓
table ───────┐
    ↓        │
    ↓    dce │
    ↓     ↓  │
    └──→ dcr │
         ↓   │
connector-definition
         ↓
    parser-function
```

## Comparison: Workbench vs OAT

| Aspect | Workbench | OAT |
|--------|-----------|-----|
| Components | 6 | 6 |
| Table Columns | 56 | 139 |
| Input Stream Fields | 19 | 9 |
| Transform Complexity | Moderate | Very High |
| Dynamic Columns | Yes (indicators, entities, matchedRules) | No (all flattened) |
| Parser Function | Yes (IOC extraction, universal old+new) | Yes (universal old+new normalizer) |
| API Endpoint | /v3.0/workbench/alerts | /v3.0/oat/detections |
| Data Volume | Medium | High |

## Benefits of Modular Architecture

### 1. Maintainability

Update individual components without touching others:
- Need to change DCR transform? Edit `dcr.json` only
- Need to add table columns? Edit `table.json` only
- Changes auto-deploy on next "Deploy to Azure" click

### 2. Testability

Test each component independently:
```bash
az deployment group create \
  --template-file templates/workbench/components/table.json \
  --parameters workspace=test-ws workspace-location=eastus
```

### 3. Reusability

Components can be reused in other solutions:
- Copy `dce.json` + `dcr.json` for any custom log ingestion
- Reuse `sentinel-solution.json` for any Sentinel deployment
- Pattern works for any Trend Vision One API

### 4. Microsoft Best Practices

Follows official patterns:
- [SentinelOne CCP Example](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/SentinelOne/Data%20Connectors/SentinelOne_ccp)
- [Deploy to Azure Button Guide](https://learn.microsoft.com/azure/azure-resource-manager/templates/deploy-to-azure-button)
- [CCP Documentation](https://learn.microsoft.com/azure/sentinel/create-codeless-connector)

## Technical Deep Dives

### Transform KQL Examples

**Workbench - Extract IOCs from indicators array**:
```kql
source
| extend TimeGenerated = todatetime(createdDateTime)
| extend indicators_dynamic = indicators
| extend indicators_s = tostring(indicators)
| extend indicators = indicators_dynamic
```

**OAT - Flatten detail object**:
```kql
source 
| extend d = detail
| extend detail_processCmd_s = tostring(d.processCmd)
| extend detail_processFileHashSha256_s = tostring(d.processFileHashSha256)
| extend detail_processPid_d = toreal(d.processPid)
| extend detail_firstSeen_t = todatetime(datetime(1970-01-01) + tolong(d.firstSeen) * 1ms)
... (130+ more fields)
```

### Linked Template Pattern

mainTemplate.json references components via GitHub URLs:
```json
{
  "templateLink": {
    "uri": "https://raw.githubusercontent.com/trendmicro/.../table.json",
    "contentVersion": "1.0.0.0"
  }
}
```

**Benefits**:
- Components update automatically when repo updates
- No need to merge everything into one massive file
- Version control per component

### createUiDefinition Schema

```json
{
  "basics": [
    {
      "name": "workspaceSelector",
      "type": "Microsoft.Solutions.ResourceSelector",
      "resourceType": "Microsoft.OperationalInsights/workspaces"
    }
  ],
  "steps": [
    {
      "name": "trendConfig",
      "elements": [
        {
          "name": "trendaiRegion",
          "type": "Microsoft.Common.DropDown",
          "allowedValues": ["US", "UK", "SG", "CA", "JP"]
        }
      ]
    }
  ]
}
```

## Migration from Legacy

If you deployed old templates (templates/legacy/), you can:

### Option 1: Keep Existing
- Old deployments continue to work
- No action required

### Option 2: Fresh Deployment
- Deploy modular templates to new workspace
- Migrate data if needed
- Decommission old deployment

### Option 3: In-Place Upgrade
1. Delete old connector definition
2. Deploy modular components
3. Reconnect with API token

**Recommendation**: Option 2 (fresh deployment to new workspace) is safest for production.

## Resources

- [Microsoft Sentinel Documentation](https://learn.microsoft.com/azure/sentinel)
- [ARM Template Reference](https://learn.microsoft.com/azure/templates)
- [Data Collection Rules](https://learn.microsoft.com/azure/azure-monitor/essentials/data-collection-rule-overview)
- [Trend Vision One API](https://automation.trendmicro.com/xdr/api-v3)

---

**Architecture Version**: 2.0  
**Last Updated**: May 2026
