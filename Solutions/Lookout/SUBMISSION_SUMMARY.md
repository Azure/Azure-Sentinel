# Microsoft PR Submission - Ready ✅

## Completion Date
November 5, 2025

## What We Completed

### ✅ 1. KQL Table Schema
- **File:** `.script/tests/KqlvalidationsTests/CustomTables/LookoutMtdV2_CL.json`
- **Status:** Complete
- **Details:** 12 columns matching codeless connector schema with dynamic objects

### ✅ 2. Data Connector Screenshot  
- **Connector:** Lookout Mobile Threat Detection Connector (via Codeless Connector Framework)
- **Status:** Connected and receiving data
- **Events:** 189 total events
- **Table:** LookoutMtdV2_CL

### ✅ 3. Workbook Screenshots
- **Location:** `Workbooks/Images/Preview/`
- **Files:**
  - LookoutSecurityInvestigationDashboardWhite1.png
  - LookoutSecurityInvestigationDashboardWhite2.png
  - LookoutSecurityInvestigationDashboardBlack1.png
  - LookoutSecurityInvestigationDashboardBlack2.png
  - LookoutExecutiveDashboardWhite1.png
  - LookoutExecutiveDashboardBlack1.png

### ✅ 4. Solution Package
- **Version:** 3.0.1
- **Files Updated:**
  - SolutionMetadata.json
  - Package/mainTemplate.json

## What Microsoft Will See

### New Components
1. **Workbook:** Lookout Security Investigation Dashboard
   - Critical alerts summary
   - Threat activity table with color-coded severity
   - Device risk analysis
   - Platform distribution
   - Timeline trends
   - Audit investigation log

2. **Parser:** LookoutEvents v4.0.0
   - Extracts 70+ normalized fields
   - Supports THREAT, DEVICE, AUDIT, SMISHING_ALERT events

3. **Analytic Rules:** 4 V2 detection rules
   - LookoutThreatEventV2
   - LookoutSmishingAlertV2
   - LookoutDeviceComplianceV2
   - LookoutAuditEventV2

### Architecture
```
Lookout API v2 → SSE Connector → DCR (field extraction) → LookoutMtdV2_CL → Parser → Workbooks/Analytics
```

## Files to Include in PR

### Must Add to Main Repo
1. `.script/tests/KqlvalidationsTests/CustomTables/LookoutMtdV2_CL.json`
2. Workbook screenshots (already in solution folder)

### Already in Solution Folder
- Analytic Rules (4 V2 rules)
- Data Connector templates
- Parser (LookoutEvents.yaml)
- Workbooks
- Package files (v3.0.1)

## Notes for Microsoft Reviewers

### Table Schema
The LookoutMtdV2_CL table uses a hybrid approach:
- **Scalar fields** for common attributes (id, log_type, enterprise_guid, etc.)
- **Dynamic objects** for nested data (device, threat, audit, smishing_alert)
- **DCR transformation** extracts additional fields at ingestion time

This design:
- ✅ Supports v2 API's rich nested structure
- ✅ Enables efficient querying via parser function
- ✅ Maintains backward compatibility
- ✅ Allows future field additions without schema changes

### Data Connector
Uses Microsoft's Codeless Connector Framework (SSE/REST API Poller):
- OAuth2 authentication with Lookout API
- Server-Sent Events (SSE) for real-time streaming
- DCR-based field extraction and transformation
- Automatic retry and error handling

### Workbooks
The Investigation Dashboard provides SOC-focused functionality:
- Real-time threat prioritization
- Device risk scoring
- Multi-platform support (iOS/Android)
- Investigation workflows
- Audit trail visibility

## Timeline
- **Deadline:** 72 hours from Nov 5 (Nov 8, 2025)
- **Status:** Ready for submission
- **Next Step:** Create PR to Azure-Sentinel repository

## Contact
- **Solution:** Lookout Mobile Threat Defense
- **Version:** 3.0.1
- **Publisher:** Lookout Inc.
- **Support:** Partner-tier

---

**Everything is ready for Microsoft review! 🎉**
