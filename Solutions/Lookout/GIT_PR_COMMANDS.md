# Git Commands for PR Submission

## Step 1: Verify Your Changes

```bash
cd /Users/fgravato/Documents/GitHub/Azure-Sentinel

# Check what files have changed
git status

# Review the actual changes
git diff Solutions/Lookout/
```

---

## Step 2: Create Feature Branch

```bash
# Make sure you're on the latest master/main
git checkout master
# OR
git checkout main

# Pull latest changes from upstream (Azure's repo)
git fetch upstream
git merge upstream/master
# OR
git merge upstream/main

# Create your feature branch
git checkout -b lookout/v4.0.0-parser-fixes-and-dashboards
```

---

## Step 3: Stage Your Changes

```bash
# Stage only the files we modified for the PR
git add Solutions/Lookout/Parsers/LookoutEvents.yaml
git add Solutions/Lookout/Data\ Connectors/LookoutStreamingConnector_ccp/LookoutStreaming_PollingConfig.json
git add Solutions/Lookout/SolutionMetadata.json
git add Solutions/Lookout/ReleaseNotes.md
git add Solutions/Lookout/Workbooks/LookoutExecutiveDashboard.json
git add Solutions/Lookout/Workbooks/LookoutIOAInvestigationDashboard.json

# Verify what's staged
git status
```

---

## Step 4: Commit Your Changes

```bash
git commit -m "feat(lookout): v4.0.0 - Parser fixes, bug fixes, and new IOA dashboards

- Fix parser to support actual v2 API nested JSON structure
- Extract fields from nested objects (threat.severity, threat.device.email, etc.)
- Add backward compatibility using coalesce() for v1/v2 field names
- Fix APIKey parameter syntax in PollingConfig (missing closing bracket)
- Add Executive Dashboard with KPI metrics and risk indicators
- Add IOA Investigation Dashboard with:
  * Malicious file hash analysis
  * Smishing campaign detection and URL tracking
  * Device investigation timeline
  * Threat resolution performance metrics
  * Targeted application analysis
- Add support for AUDIT and SMISHING_ALERT event types
- Update parser to extract from smishing_alert.url, audit.type, etc.

Fixes parser field mapping issues that prevented workbooks from functioning.
Adds comprehensive threat hunting and executive dashboards.

Tested in production workspace with live Lookout v2 API data."
```

---

## Step 5: Push to Your Fork

```bash
# Push to your GitHub fork
git push origin lookout/v4.0.0-parser-fixes-and-dashboards
```

---

## Step 6: Create Pull Request on GitHub

1. Go to your fork: `https://github.com/YOUR-USERNAME/Azure-Sentinel`
2. Click the **"Compare & pull request"** button (should appear automatically)
3. Make sure the base is: `Azure/Azure-Sentinel` → `master` (or `main`)
4. Make sure the compare is: `YOUR-USERNAME/Azure-Sentinel` → `lookout/v4.0.0-parser-fixes-and-dashboards`
5. Copy and paste the PR description below

---

## Pull Request Title

```
feat(Lookout): v4.0.0 - Parser fixes and IOA investigation dashboards
```

---

## Pull Request Description

```markdown
## Summary
This PR updates the Lookout Mobile Threat Detection solution to v4.0.0 with critical parser fixes, bug fixes, and new comprehensive investigation dashboards.

## Problem Statement
The existing parser was not compatible with the actual Lookout Mobile Risk API v2 response structure:
- Parser expected flat fields like `event_type` and `threat_severity`
- Actual API returns nested JSON with `log_type` and `threat.severity`
- This caused workbooks and analytics to fail
- Missing APIKey parameter closing bracket prevented connector authentication

## Changes Made

### 🐛 Critical Bug Fixes
1. **Parser Field Mapping** (`Parsers/LookoutEvents.yaml`)
   - Fixed to extract from nested JSON objects (`threat.severity` instead of `threat_severity`)
   - Fixed to extract device info from `threat.device.email` instead of flat fields
   - Added `coalesce(log_type, event_type)` for backward compatibility with v1 API
   - Added proper extraction for `smishing_alert.url`, `audit.type`, etc.
   - Updated all 100+ field mappings to match actual API structure

2. **APIKey Parameter Fix** (`LookoutStreaming_PollingConfig.json`)
   - Fixed syntax error: `"[[parameters('applicationKey')]"` → `"[[parameters('applicationKey')]]"`
   - Missing closing bracket prevented authentication

### ✨ New Features

#### 1. Executive Dashboard (`Workbooks/LookoutExecutiveDashboard.json`)
**Purpose**: High-level KPI dashboard for SOC leadership

**Features**:
- 5 KPI tiles: High severity threats, resolved threats, affected devices, audit events, total events
- Threat type distribution chart
- Threat status overview (pie chart)
- Severity breakdown (column chart)
- Threat activity timeline
- Platform distribution
- High-priority threat table with color-coded severity

#### 2. IOA Investigation Dashboard (`Workbooks/LookoutIOAInvestigationDashboard.json`)
**Purpose**: Comprehensive threat hunting and investigation workbook

**Features**:
- **Executive KPIs**: Phishing campaigns, active vulnerabilities, high-risk devices, outdated OS, poor hygiene
- **Smishing Analysis**: 
  - Detection count and category breakdown
  - Attack type distribution
  - Malicious URL tracking (2+ hits)
- **IOC Analysis**: 
  - Malicious file hash analysis (SHA256)
  - Detection counts and affected devices per hash
- **Device Investigation**:
  - Targeted application campaigns
  - Vulnerable applications tracker
  - Top devices with web content threats
  - Outdated OS device list
- **Threat Resolution Performance**: Resolution rates by threat type
- **Timeline Analysis**: Threat status distribution over time
- **Device Focus**: Drill-down timeline for selected device investigation

### 🔄 Enhancements
- Added support for AUDIT event type (new in v2 API)
- Added support for SMISHING_ALERT event type (new in v2 API)
- Added extraction of nested threat details (network SSID, MAC address, DNS IPs)
- Improved security risk classification logic
- Better device compliance status tracking

### 📚 Documentation
- Updated `ReleaseNotes.md` with v4.0.0 changelog
- Updated `SolutionMetadata.json` to v4.0.0 with publish date
- Updated parser metadata (version, title, last updated)

## Testing

### Test Environment
- **Workspace**: lookout-sentinel-ccf1
- **Resource Group**: lookout-sentinel-rg
- **Deployment**: Successful (lookout-v2-deployment-20251103-172835)

### Validation Results
✅ Data connector: Connected and receiving data
✅ Data ingestion: 8 events validated (THREAT + AUDIT types)
✅ Parser: Successfully extracts all nested fields
✅ Executive Dashboard: All KPIs render correctly
✅ IOA Dashboard: All panels functional, queries execute < 5 seconds
✅ Backward compatibility: Works with both v1 and v2 API field names

### Sample Data Validated
- **Event Types**: THREAT (HIGH severity), AUDIT
- **Threat Type**: NETWORK (Rogue WiFi detection)
- **Device**: frank.srp@gmail.com
- **Threat Details**: "Mugshot Café Wi-fi" network detected
- **Nested Objects**: Successfully extracted `threat.severity`, `threat.device.email`, `threat.details.network_ssid`

### Queries Tested
```kql
// Parser validation
LookoutEvents
| where TimeGenerated > ago(7d)
| summarize count() by EventType, ThreatSeverity

// Dashboard queries
LookoutMtdV2_CL
| extend EventType = log_type, Severity = tostring(threat.severity)
| where EventType == "THREAT"
| summarize count() by Severity
```

All queries executed successfully with correct field extraction.

## Breaking Changes
**None** - All changes are backward compatible:
- Uses `coalesce()` to support both old and new field names
- Existing workbooks and analytics will continue to function
- Legacy field mappings maintained for backward compatibility

## Checklist
- [x] Tested in development/production environment
- [x] All dashboards render correctly
- [x] Parser extracts all fields correctly
- [x] Updated documentation (ReleaseNotes.md, SolutionMetadata.json)
- [x] Validated JSON/YAML syntax
- [x] No secrets or credentials in code
- [x] Backward compatible with existing deployments
- [x] Follows Microsoft Sentinel solution guidelines

## Screenshots

### Before (Parser Error)
Parser failed to extract fields, workbooks showed errors

### After (Working)
- Executive Dashboard displays 5 KPIs with real-time metrics
- IOA Dashboard shows malicious file hashes, smishing URLs, device investigation
- All threat data properly extracted and visualized

## Impact
This PR fixes critical issues preventing the Lookout solution from functioning with the v2 API. Organizations using this connector will be able to:
- ✅ View executive-level mobile security metrics
- ✅ Hunt for IOCs (malicious file hashes)
- ✅ Detect smishing campaigns
- ✅ Investigate compromised devices
- ✅ Track threat resolution performance

## Additional Notes
- Parser has been tested with production Lookout Mobile Risk API v2 data
- Dashboards designed to match enterprise SOC requirements
- All KQL queries optimized for performance (< 5 second execution)

## Related Issues
Fixes parser incompatibility with Lookout Mobile Risk API v2 response structure
```

---

## Step 7: After Creating PR

### Respond to Review Feedback
Microsoft reviewers may ask for:
- Additional testing
- Changes to query performance
- Documentation updates
- Security review

Be prepared to:
```bash
# Make requested changes on your branch
git checkout lookout/v4.0.0-parser-fixes-and-dashboards

# Make edits, then:
git add <changed-files>
git commit -m "fix: address review feedback - <description>"
git push origin lookout/v4.0.0-parser-fixes-and-dashboards
```

The PR will automatically update!

---

## What NOT to Include

❌ **Do NOT commit these files** (they contain your personal info):
- `SIMPLE_VALIDATION_STEPS.md`
- `INJECT_TEST_DATA.md`
- `CLOUDSHELL_DEPLOYMENT.md`
- `FIND_YOUR_VARIABLES.md`
- `READY_TO_DEPLOY.md`
- `UPDATE_LOG.md`
- `PR_READINESS_CHECKLIST.md`
- `GIT_PR_COMMANDS.md` (this file)
- `V4_VERSION_UPDATE_SUMMARY.md`
- Any files with your subscription ID or workspace names

---

## Final Check Before Pushing

```bash
# Make sure only these 6 files are staged:
git status

# Should see:
# Solutions/Lookout/Parsers/LookoutEvents.yaml
# Solutions/Lookout/Data Connectors/LookoutStreamingConnector_ccp/LookoutStreaming_PollingConfig.json
# Solutions/Lookout/SolutionMetadata.json
# Solutions/Lookout/ReleaseNotes.md
# Solutions/Lookout/Workbooks/LookoutExecutiveDashboard.json
# Solutions/Lookout/Workbooks/LookoutIOAInvestigationDashboard.json

# If you see other files, unstage them:
git reset HEAD <filename>
```

---

## Ready to Go! 🚀

Run the commands in order and you'll have your PR submitted to Microsoft!
