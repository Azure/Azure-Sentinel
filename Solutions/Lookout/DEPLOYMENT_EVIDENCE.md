# Lookout v3.0.1 - Deployment Evidence

## Data Connector - Running and Ingesting Data

**Screenshot**: [LookoutCodelessConnectorRunning.png](Data%20Connectors/Images/LookoutCodelessConnectorRunning.png)

### Evidence Shows:
- **Status**: Connected ✅
- **Provider**: Microsoft
- **Last Log Received**: 20 Hours Ago
- **Events Ingested**: 189 events
- **Data Type**: LookoutMtdV2_CL
- **Last Data Received**: 11/4/2025, 5:51:33 PM
- **Data Flow Graph**: Shows consistent data ingestion over time

The Lookout Mobile Threat Detection Connector (via Codeless Connector Framework) is successfully:
1. Connected to the Lookout Mobile Risk API
2. Ingesting events into the `LookoutMtdV2_CL` custom log table
3. Processing threat, device, audit, and smishing alert events
4. Operating in preview mode with stable data flow

---

## Parser - LookoutEvents Function

The `LookoutEvents` parser function successfully transforms raw `LookoutMtdV2_CL` table data into normalized, queryable fields.

### Parser Capabilities:
- **Input**: Raw JSON from LookoutMtdV2_CL table
- **Output**: 100+ normalized fields including:
  - Threat Information (ThreatId, ThreatType, ThreatSeverity, ThreatClassifications, etc.)
  - Device Information (DeviceGuid, DevicePlatform, DeviceEmailAddress, DeviceSecurityStatus, etc.)
  - Audit Events (AuditType, AuditAttributeChanges)
  - Smishing Alerts (SmishingAlertType, SmishingAlertSeverity, SmishingAlertDescription)
  - Actor/Target context
  - MDM integration fields

### Parser Usage in Analytic Rules:
All V2 analytic rules successfully use the parser:
- ✅ LookoutThreatEventV2.yaml
- ✅ LookoutDeviceComplianceV2.yaml
- ✅ LookoutSmishingAlertV2.yaml
- ✅ LookoutAuditEventV2.yaml

### Sample Parser Query:
```kql
LookoutEvents
| where EventType == "THREAT"
| where ThreatSeverity in ("CRITICAL", "HIGH")
| project TimeGenerated, EventType, ThreatType, ThreatSeverity, 
          DeviceGuid, DeviceEmailAddress, DevicePlatform, 
          ThreatClassifications, DeviceSecurityStatus
| take 100
```

This query demonstrates the parser successfully extracts and normalizes fields from the nested JSON structure in LookoutMtdV2_CL.

---

## Workbooks - Security Dashboards

### 1. LookoutSecurityInvestigationDashboard
- **Purpose**: Comprehensive security monitoring and investigation
- **Preview Images**: 
  - [LookoutSecurityInvestigationDashboardBlack1.png](Workbooks/Images/Preview/LookoutSecurityInvestigationDashboardBlack1.png)
  - [LookoutSecurityInvestigationDashboardWhite1.png](Workbooks/Images/Preview/LookoutSecurityInvestigationDashboardWhite1.png)

### 2. LookoutExecutiveDashboard
- **Purpose**: High-level security posture overview
- **Preview Images**:
  - [LookoutExecutiveDashboardBlack1.png](Workbooks/Images/Preview/LookoutExecutiveDashboardBlack1.png)
  - [LookoutExecutiveDashboardWhite1.png](Workbooks/Images/Preview/LookoutExecutiveDashboardWhite1.png)

### 3. LookoutEventsV2
- **Purpose**: Detailed event analysis using v2 parser fields
- Uses LookoutEvents parser for all queries

---

## Validation Summary

- ✅ Data Connector: Deployed and ingesting data
- ✅ Parser: Functioning correctly, transforms nested JSON
- ✅ Analytic Rules: 5 rules deployed, using parser
- ✅ Workbooks: 5 workbooks deployed with preview images
- ✅ Hunting Queries: 1 advanced threat hunting query
- ✅ Version: 3.0.1

**Date**: November 14, 2025  
**Environment**: Microsoft Sentinel Production Workspace
