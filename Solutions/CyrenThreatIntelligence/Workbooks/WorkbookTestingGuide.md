# Cyren Threat Intelligence Workbook Testing Guide

## Overview

This document provides testing and validation documentation for the **Cyren Threat Intelligence Dashboard** workbook included in the Cyren Threat Intelligence solution for Microsoft Sentinel.

## Workbook Information

| Property | Value |
|----------|-------|
| **Name** | Cyren Threat Intelligence Dashboard |
| **Version** | 1.0.0 |
| **Provider** | Data443 Risk Mitigation, Inc. |
| **Template ID** | sentinel-CyrenThreatIntelligence |
| **Data Source** | Cyren_Indicators_CL |
| **Connector Dependency** | CyrenThreatIntel |

## Prerequisites

Before testing the workbook, ensure the following:

1. **Microsoft Sentinel workspace** is deployed and accessible
2. **Cyren Threat Intelligence CCF connector** is installed and connected
3. **Data is flowing** to the `Cyren_Indicators_CL` custom table
4. User has **Workbook Reader** or **Workbook Contributor** permissions

## Workbook Components

The workbook contains the following visualization components:

### 1. Data Pipeline Health Tile
- **Query**: Summarizes total records, IP reputation indicators, and malware URL indicators from the last hour
- **Visualization**: Tile with status indicator (🟢 Healthy / 🟡 Warning / 🔴 Critical)
- **Purpose**: Real-time monitoring of data ingestion pipeline health

### 2. IP Reputation Indicators Chart
- **Query**: Time-series aggregation of IP reputation indicators
- **Visualization**: Time chart showing indicator counts over selected time range
- **Purpose**: Trend analysis of IP-based threat intelligence

### 3. Malware URL Indicators Chart
- **Query**: Time-series aggregation of malware URL indicators
- **Visualization**: Time chart showing URL indicator counts over selected time range
- **Purpose**: Trend analysis of URL-based threat intelligence

### 4. High-Risk IP Indicators Table
- **Query**: Filters IP indicators with risk score >= 80
- **Visualization**: Table with risk-based color formatting
- **Purpose**: Prioritized view of highest-risk IP indicators

### 5. High-Risk Malware URLs Table
- **Query**: Filters URL indicators with risk score >= 80
- **Visualization**: Table with risk-based color formatting
- **Purpose**: Prioritized view of highest-risk malware URLs

### 6. Top Threat Categories Pie Chart
- **Query**: Aggregation of indicators by category
- **Visualization**: Pie chart showing category distribution
- **Purpose**: Overview of threat category distribution

## Testing Procedures

### Test 1: Workbook Template Validation

**Objective**: Verify the workbook JSON template is valid and follows Microsoft Sentinel schema.

**Steps**:
1. Open `CyrenThreatIntelligenceDashboard.json`
2. Validate JSON syntax using a JSON linter
3. Verify `fromTemplateId` is set to `sentinel-CyrenThreatIntelligence`
4. Verify `$schema` points to valid Application Insights Workbooks schema

**Expected Result**: JSON is valid, template ID is correct, schema reference is present.

**Status**: ✅ PASS

### Test 2: Query Syntax Validation

**Objective**: Verify all KQL queries in the workbook are syntactically correct.

**Steps**:
1. Extract each query from the workbook JSON
2. Run each query in Log Analytics with sample data
3. Verify no syntax errors are returned

**Test Queries**:

```kusto
// Health Check Query
Cyren_Indicators_CL 
| where TimeGenerated >= ago(1h) 
| summarize 
    Total=count(), 
    IPRep=countif(source_s contains 'IP'), 
    MalwareURLs=countif(source_s contains 'Malware'), 
    Latest=max(TimeGenerated),
    HoursAgo=datetime_diff('hour', now(), max(TimeGenerated))
| extend Status = case(
    HoursAgo > 7, "🔴 Critical - No data > 7 hours",
    HoursAgo > 6, "🟡 Warning - Data delayed",
    "🟢 Healthy - Data flowing"
)
| project Status, Total, IPRep, MalwareURLs, Latest, HoursAgo
```

```kusto
// IP Indicators Time Series
Cyren_Indicators_CL
| where TimeGenerated >= ago(24h)
| where isnotempty(ip_s)
| extend Risk = toint(risk_d)
| summarize 
    Count = count(),
    AvgRisk = avg(Risk),
    MaxRisk = max(Risk),
    Categories = make_set(category_s)
  by bin(TimeGenerated, 1h)
| order by TimeGenerated asc
```

```kusto
// High-Risk IPs Query
Cyren_Indicators_CL
| where TimeGenerated >= ago(24h)
| where isnotempty(ip_s)
| extend Risk = toint(risk_d)
| where Risk >= 80
| summarize 
    DetectionCount = count(),
    MaxRisk = max(Risk),
    Categories = make_set(category_s),
    FirstSeen = min(TimeGenerated),
    LastSeen = max(TimeGenerated)
  by IP = ip_s
| order by MaxRisk desc
| take 100
```

**Expected Result**: All queries execute without syntax errors.

**Status**: ✅ PASS

### Test 3: Time Range Parameter

**Objective**: Verify the time range parameter filters data correctly.

**Steps**:
1. Open workbook in Microsoft Sentinel
2. Select different time ranges (1 hour, 6 hours, 24 hours, 7 days, 30 days)
3. Verify visualizations update to reflect the selected time range

**Expected Result**: All visualizations respect the time range parameter selection.

**Status**: ✅ PASS

### Test 4: Preview Images Validation

**Objective**: Verify preview images are present and in correct PNG format.

**Steps**:
1. Locate preview images in `Workbooks/Images/Preview/`
2. Verify both Black and White theme images exist
3. Verify images are actual PNG format (not JPEG with .png extension)

**Validation Command**:
```bash
file Workbooks/Images/Preview/CyrenThreatIntelligenceDashboard*.png
```

**Expected Output**:
```
CyrenThreatIntelligenceDashboardBlack.png: PNG image data
CyrenThreatIntelligenceDashboardWhite.png: PNG image data
```

**Status**: ✅ PASS

### Test 5: WorkbooksMetadata.json Entry

**Objective**: Verify the workbook is properly registered in WorkbooksMetadata.json.

**Steps**:
1. Open `Workbooks/WorkbooksMetadata.json`
2. Search for `CyrenThreatIntelligenceDashboard` entry
3. Verify all required properties are present

**Required Properties**:
- `workbookKey`: CyrenThreatIntelligenceDashboard
- `logoFileName`: cyren_logo.svg
- `description`: Present and descriptive
- `dataTypesDependencies`: ["Cyren_Indicators_CL"]
- `dataConnectorsDependencies`: ["CyrenThreatIntel"]
- `previewImagesFileNames`: Both Black and White images
- `version`: 1.0.0
- `title`: Cyren Threat Intelligence Dashboard
- `templateRelativePath`: CyrenThreatIntelligenceDashboard.json
- `provider`: Data443 Risk Mitigation, Inc.

**Status**: ✅ PASS

### Test 6: Visualization Rendering

**Objective**: Verify all visualizations render correctly with sample data.

**Steps**:
1. Deploy workbook to test Microsoft Sentinel workspace
2. Ensure Cyren CCF connector is providing data
3. Open workbook and verify each component renders

**Expected Results**:
- Health tile displays with correct status
- Time charts display trend data
- Tables display high-risk indicators
- Pie chart displays category distribution

**Status**: ✅ PASS (verified with production data)

## Data Schema Reference

The workbook queries the `Cyren_Indicators_CL` table with the following schema:

| Column | Type | Description |
|--------|------|-------------|
| TimeGenerated | datetime | Record ingestion time |
| ip_s | string | IP address indicator |
| url_s | string | URL indicator |
| domain_s | string | Domain name |
| category_s | string | Threat category |
| risk_d | int | Risk score (0-100) |
| source_s | string | Feed source identifier |
| firstSeen_t | datetime | First observation time |
| lastSeen_t | datetime | Last observation time |

## Troubleshooting

### No Data Displayed

1. Verify the Cyren CCF connector is connected and healthy
2. Check that data is flowing to `Cyren_Indicators_CL` table
3. Verify the selected time range contains data
4. Check user permissions for Log Analytics queries

### Health Tile Shows Critical

1. Check connector status in Data Connectors blade
2. Verify API credentials are valid
3. Check network connectivity to Cyren API endpoints

### Queries Return Errors

1. Verify the `Cyren_Indicators_CL` table exists
2. Check column names match expected schema
3. Verify workspace has query permissions

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-09 | Initial release |

## Support

For issues with this workbook, contact:
- **Provider**: Data443 Risk Mitigation, Inc.
- **Email**: support@data443.com
- **Website**: https://www.data443.com
- **Support Portal**: https://data443.com/support

## References

- [Microsoft Sentinel Workbooks Documentation](https://learn.microsoft.com/en-us/azure/sentinel/monitor-your-data)
- [Azure Monitor Workbooks](https://learn.microsoft.com/en-us/azure/azure-monitor/visualize/workbooks-overview)
- [Sentinel Solution Quality Guidelines](https://learn.microsoft.com/en-us/azure/sentinel/sentinel-solution-quality-guidance)
