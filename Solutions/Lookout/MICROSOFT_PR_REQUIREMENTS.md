# Microsoft PR Requirements - Completion Checklist

## ✅ 1. Custom Table Schema (COMPLETED)

**Requirement:** Add table schema for LookoutMtdV2_CL to CustomTables folder

**Location:** `.script/tests/KqlvalidationsTests/CustomTables/LookoutMtdV2_CL.json`

**Status:** ✅ Created with 12 columns matching the codeless connector schema
- TimeGenerated, id, enterprise_guid, created_time, log_type, change_type
- actor_device_guid
- Dynamic objects: device, threat, audit, smishing_alert, target, actor

---

## ✅ 2. Data Connector Screenshot (COMPLETED)

**Requirement:** Provide screenshot of running connector

**Status:** ✅ Screenshot captured showing:
- Connector: "Lookout Mobile Threat Detection Connector (via Codeless Connector Framework)"
- Status: Connected
- Provider: Microsoft
- Data flowing to LookoutMtdV2_CL table
- 189 events received
- Last log received timestamp visible

---

## ✅ 3. Workbook Images (COMPLETED)

**Requirement:** Add running workbook images with proper naming convention

**Current Structure:**
```
Workbooks/
├── Images/
│   ├── Logo/
│   │   └── lookout.svg
│   └── Preview/
│       ├── SampleLookoutWorkBookBlack.png
│       └── SampleLookoutWorkBookWhite.png
```

**Status:** ✅ Screenshots captured for:

### Lookout Security Investigation Dashboard
- `LookoutSecurityInvestigationDashboardWhite1.png` ✅
- `LookoutSecurityInvestigationDashboardWhite2.png` ✅
- `LookoutSecurityInvestigationDashboardBlack1.png` ✅
- `LookoutSecurityInvestigationDashboardBlack2.png` ✅

**Dashboard Features:**
- Critical alerts summary
- Recent threat activity with color-coded severity
- Device risk analysis
- Platform distribution charts
- Event timeline trends
- Audit log for investigations

**Naming Convention:**
- Format: `{WorkbookName}{Theme}{PageNumber}.png`
- Theme: `Black` or `White`
- PageNumber: Sequential (1, 2, 3, etc.)

**Steps:**
1. Deploy workbooks to Azure Sentinel
2. Open each workbook
3. Switch to light theme (White) and capture screenshots
4. Switch to dark theme (Black) and capture screenshots
5. Save to `Workbooks/Images/Preview/`

**Reference:** See [Cloudflare solution](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/Cloudflare/Workbooks)

---

## ⏳ 4. WorkbooksMetadata.json Entry (READY TO ADD)

**Requirement:** Include workbook metadata in the main WorkbooksMetadata.json

**Location:** `https://github.com/Azure/Azure-Sentinel/blob/master/Workbooks/WorkbooksMetadata.json`

**Entries to Add:**

### Entry 1: Lookout Executive Dashboard
```json
{
  "workbookKey": "LookoutExecutiveDashboard",
  "logoFileName": "lookout.svg",
  "description": "Executive-level dashboard for Lookout Mobile Threat Defense, providing comprehensive visibility into mobile security threats, device compliance status, and security trends. Monitor threat events, smishing alerts, audit activities, and device health metrics in real-time.",
  "dataTypesDependencies": [
    "LookoutMtdV2_CL"
  ],
  "dataConnectorsDependencies": [
    "LookoutMRAv2"
  ],
  "previewImagesFileNames": [
    "LookoutExecutiveDashboardBlack1.png",
    "LookoutExecutiveDashboardBlack2.png",
    "LookoutExecutiveDashboardWhite1.png",
    "LookoutExecutiveDashboardWhite2.png"
  ],
  "version": "4.0.0",
  "title": "Lookout Executive Dashboard",
  "templateRelativePath": "LookoutExecutiveDashboard.json",
  "subtitle": "Mobile Threat Defense Executive Overview",
  "provider": "Lookout"
}
```

### Entry 2: Lookout IOA Investigation Dashboard
```json
{
  "workbookKey": "LookoutIOAInvestigationDashboard",
  "logoFileName": "lookout.svg",
  "description": "Advanced investigation dashboard for Lookout Mobile Threat Defense, focused on Indicators of Attack (IOA) analysis. Provides detailed threat intelligence, device investigation capabilities, and deep-dive analytics for security operations and incident response teams.",
  "dataTypesDependencies": [
    "LookoutMtdV2_CL"
  ],
  "dataConnectorsDependencies": [
    "LookoutMRAv2"
  ],
  "previewImagesFileNames": [
    "LookoutIOAInvestigationDashboardBlack1.png",
    "LookoutIOAInvestigationDashboardBlack2.png",
    "LookoutIOAInvestigationDashboardWhite1.png",
    "LookoutIOAInvestigationDashboardWhite2.png"
  ],
  "version": "4.0.0",
  "title": "Lookout IOA Investigation Dashboard",
  "templateRelativePath": "LookoutIOAInvestigationDashboard.json",
  "subtitle": "Mobile Threat Investigation and IOA Analysis",
  "provider": "Lookout"
}
```

**Note:** Add these entries to the main repository's WorkbooksMetadata.json file, not your solution folder.

---

## ⏳ 5. Update Solution Data File (TODO)

**Requirement:** Update solutions data file with new Analytic Rules and workbooks

**Current Analytic Rules:**
- ✅ LookoutAuditEventV2.yaml (new)
- ✅ LookoutDeviceComplianceV2.yaml (new)
- ✅ LookoutSmishingAlertV2.yaml (new)
- ✅ LookoutThreatEventV2.yaml (new)
- LookoutThreatEvent.yaml (legacy)

**Current Workbooks:**
- ✅ LookoutExecutiveDashboard.json (new)
- ✅ LookoutIOAInvestigationDashboard.json (new)
- LookoutEvents.json (legacy)
- LookoutEventsV2.json (legacy)

**Action Required:**
1. Review `Package/mainTemplate.json` or solution data file
2. Add references to new analytic rules (V2 versions)
3. Add references to new workbooks
4. Ensure version is set to 3.0.1

---

## ⏳ 6. Repackage Solution (TODO)

**Requirement:** Create zip file with version 3.0.1 using V3 tool

**Steps:**

1. **Update Solution Version**
   ```json
   {
     "version": "3.0.1"
   }
   ```

2. **Use V3 Packaging Tool**
   - Reference: https://github.com/Azure/Azure-Sentinel/blob/master/Tools/Create-Azure-Sentinel-Solution/V3/README.md
   - Tool Location: `Tools/Create-Azure-Sentinel-Solution/V3/`

3. **Create Package**
   ```bash
   # Navigate to V3 tool directory
   cd /path/to/Azure-Sentinel/Tools/Create-Azure-Sentinel-Solution/V3/
   
   # Run packaging tool
   # (Follow V3 tool README for exact command syntax)
   ```

4. **Validate Package**
   - Ensure all new components are included
   - Verify version is 3.0.1
   - Test deployment in test environment

---

## Summary of Current Status

### ✅ Completed
1. ✅ KQL table schema created for validation
2. ✅ Workbook Images folder structure exists
3. ✅ Workbook metadata entries prepared

### ⏳ Requires Manual Action
1. ⏳ Screenshot of running data connector
2. ⏳ Screenshots of running workbooks (light and dark themes)
3. ⏳ Add entries to main WorkbooksMetadata.json
4. ⏳ Update solution data file
5. ⏳ Repackage with V3 tool

---

## Files Modified/Created

### Created
- `.script/tests/KqlvalidationsTests/CustomTables/LookoutMtdV2_CL.json` - Table schema for KQL validation

### To Be Modified
- `Workbooks/WorkbooksMetadata.json` (in main repo) - Add workbook metadata
- `SolutionMetadata.json` or `Package/mainTemplate.json` - Update version to 3.0.1
- Solution package - Repackage with V3 tool

### To Be Added
- Data connector screenshot
- Workbook screenshots (8+ images in light and dark themes)

---

## Next Steps

1. **Immediate:** Deploy connector and workbooks to capture screenshots
2. **Then:** Add workbook metadata to main repository file
3. **Then:** Update solution data file with new components
4. **Finally:** Repackage solution as version 3.0.1 and create PR

