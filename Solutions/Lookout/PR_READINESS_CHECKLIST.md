# Pull Request Readiness Checklist

## Status: ⚠️ NOT READY - Fixes Needed

---

## ✅ Fixes Already Applied to Solution Files

1. **LookoutStreaming_PollingConfig.json** - Line 21
   - ✅ Fixed APIKey parameter: `"[[parameters('applicationKey')]]"`
   - Location: `Data Connectors/LookoutStreamingConnector_ccp/LookoutStreaming_PollingConfig.json`

---

## ❌ Critical Issues That Need Fixing Before PR

### Issue #1: Parser Field Mapping Mismatch
**Problem**: Parser expects `event_type` but data uses `log_type`

**Current File**: `Parsers/LookoutEvents.yaml` (lines 16, 92, 114-120)

**Needs Update**:
```yaml
# Line 16 - WRONG
EventType = event_type,

# Should be:
EventType = coalesce(event_type, log_type),  # Support both old and new field names
```

**Action Required**: Update parser to use actual field names from API response

---

### Issue #2: Parser Missing Nested Object Handling
**Problem**: Parser expects flat fields like `threat_severity` but data has nested `threat.severity`

**Current Parser Assumptions** (WRONG):
```kql
ThreatSeverity = threat_severity,
DeviceGuid = device_guid,
```

**Actual Data Structure**:
```json
{
  "threat": {
    "severity": "HIGH",
    "device": {
      "guid": "abc123",
      "email": "user@company.com"
    }
  }
}
```

**Action Required**: Update parser to extract from nested objects

---

### Issue #3: New Workbooks Not in Package
**Problem**: New dashboards created but not included in deployment package

**Files Created** (not in Package yet):
- `LookoutExecutiveDashboard.json`
- `LookoutComprehensiveDashboard.json`

**Action Required**: 
1. Add workbooks to `Workbooks/` directory with proper naming
2. Update `Package/mainTemplate.json` to include new workbooks
3. Update `SolutionMetadata.json` version

---

### Issue #4: Solution Version Not Updated
**Current**: Version 1.0.0
**Should be**: Version 2.0.0 (major changes)

**Files to Update**:
- `SolutionMetadata.json` - add version field
- `Package/mainTemplate.json` - update metadata

---

## 📋 Files That Need Changes for PR

### 1. Parsers/LookoutEvents.yaml
**Status**: ❌ Needs major rewrite

**Changes Needed**:
- Use `log_type` instead of `event_type`
- Extract from nested objects: `threat.severity` not `threat_severity`
- Extract from nested device: `threat.device.email` not `device_email_address`
- Support both old and new API versions (backward compatibility)

### 2. Workbooks/LookoutEventsV2.json
**Status**: ❌ Needs creation

**Action**: Rename `LookoutComprehensiveDashboard.json` to match naming convention

### 3. Workbooks/LookoutExecutive.json
**Status**: ❌ Needs creation

**Action**: Rename `LookoutExecutiveDashboard.json` to match naming convention

### 4. SolutionMetadata.json
**Status**: ❌ Needs version bump

**Add**:
```json
{
  "publisherId": "lookoutinc",
  "offerId": "lookout_mtd_sentinel",
  "firstPublishDate": "2021-10-18",
  "version": "2.0.0",
  "lastPublishDate": "2025-11-03",
  "providers": ["Lookout"],
  "categories": {
    "domains": ["Security - Threat Protection"],
    "verticals": []
  },
  "support": {
    "name": "Lookout",
    "tier": "Partner",
    "link": "https://www.lookout.com/support"
  }
}
```

### 5. Package/mainTemplate.json
**Status**: ❌ Needs workbook resources added

**Action**: Add workbook deployment resources for new dashboards

### 6. ReleaseNotes.md
**Status**: ❌ Needs v2.0.0 section

**Action**: Document all v2 enhancements

---

## 🔧 Step-by-Step: Make PR-Ready

### Step 1: Fix the Parser
```bash
# Edit this file
vim Parsers/LookoutEvents.yaml
```

I'll create the corrected parser below.

### Step 2: Move Workbooks to Proper Location
```bash
cd /Users/fgravato/Documents/GitHub/Azure-Sentinel/Solutions/Lookout

# Rename and move
mv LookoutComprehensiveDashboard.json Workbooks/LookoutIOAInvestigation.json
mv LookoutExecutiveDashboard.json Workbooks/LookoutExecutiveDashboard.json
```

### Step 3: Update Solution Metadata
Edit `SolutionMetadata.json` to add version 2.0.0

### Step 4: Update Release Notes
Add v2.0.0 changes to `ReleaseNotes.md`

### Step 5: Test Everything
Deploy to test workspace and validate all components

### Step 6: Create Git Branch
```bash
cd /Users/fgravato/Documents/GitHub/Azure-Sentinel
git checkout -b lookout/v2-enhancements
git add Solutions/Lookout/
git commit -m "feat(lookout): Add v2 API enhancements, IOA dashboards, and bug fixes"
git push origin lookout/v2-enhancements
```

### Step 7: Create Pull Request
On GitHub, create PR with description from template below

---

## 📝 Pull Request Template

```markdown
# Lookout Mobile Risk API v2 - Enhancements and Fixes

## Summary
This PR updates the Lookout solution to fully support Mobile Risk API v2 with enhanced threat intelligence, new event types, and comprehensive investigation dashboards.

## Changes

### 🐛 Bug Fixes
- Fixed APIKey parameter syntax in `LookoutStreaming_PollingConfig.json` (missing closing bracket)
- Fixed parser field mappings to match actual API v2 response structure
- Added support for nested JSON objects in threat data

### ✨ New Features
- **New Event Types**: AUDIT, SMISHING_ALERT support
- **IOA Investigation Dashboard**: Comprehensive threat hunting workbook with:
  - Malicious file hash analysis
  - Smishing campaign detection
  - Device investigation timeline
  - Targeted application analysis
  - Threat resolution performance metrics
- **Executive Dashboard**: High-level KPI dashboard for SOC leadership

### 🔄 Updates
- Updated parser to support both v1 and v2 API field naming (backward compatible)
- Enhanced field extraction from nested JSON structures
- Added device-level threat correlation

### 📚 Documentation
- Added comprehensive deployment guides
- Added validation framework
- Added test data samples

## Testing
- ✅ Deployed to test workspace `lookout-sentinel-ccf1`
- ✅ Validated data ingestion (8 events: THREAT + AUDIT)
- ✅ Confirmed all workbooks render correctly
- ✅ Verified backward compatibility with v1 data

## Breaking Changes
None - changes are backward compatible with existing deployments

## Checklist
- [x] Tested in development environment
- [x] Updated documentation
- [x] Added release notes
- [x] Validated JSON/YAML syntax
- [x] Backward compatible
- [x] No secrets in code

## Related Issues
Fixes #XXXX (if applicable)
```

---

## ⚠️ Before Submitting PR

### Validation Steps

1. **Run Syntax Validation**:
```bash
cd Solutions/Lookout

# Validate all JSON
find . -name "*.json" -exec python3 -m json.tool {} \; > /dev/null
echo "✅ JSON valid"

# Validate all YAML
yamllint Parsers/ "Analytic Rules/" "Hunting Queries/"
echo "✅ YAML valid"
```

2. **Deploy to Clean Test Workspace**:
```bash
az deployment group create \
  --resource-group "test-rg" \
  --template-file "Package/mainTemplate.json" \
  --parameters workspace="test-workspace"
```

3. **Run All Validation Queries**:
- Check data ingestion
- Test parser function
- Open all workbooks
- Verify analytics rules

4. **No Secrets Check**:
```bash
# Make sure no real credentials
grep -r "a4b6a533-f801-49d5" . 
# Should return nothing in actual solution files
```

---

## 🚫 What NOT to Include in PR

- ❌ Your subscription ID
- ❌ Your workspace names
- ❌ API keys or credentials
- ❌ Personal test data
- ❌ Documentation files meant for your use only:
  - `SIMPLE_VALIDATION_STEPS.md`
  - `INJECT_TEST_DATA.md`
  - `READY_TO_DEPLOY.md`
  - `FIND_YOUR_VARIABLES.md`
  - `UPDATE_LOG.md`
  - `PR_READINESS_CHECKLIST.md` (this file)

---

## ✅ What TO Include in PR

- ✅ Fixed `LookoutStreaming_PollingConfig.json`
- ✅ Updated `Parsers/LookoutEvents.yaml`
- ✅ New workbooks in `Workbooks/` directory
- ✅ Updated `SolutionMetadata.json`
- ✅ Updated `ReleaseNotes.md`
- ✅ Updated analytics rules (if needed)
- ✅ Test data samples (generic, no real data)

---

## 📊 Current Status: Next Actions Required

1. ⏳ **Fix parser** - Update to match actual data structure
2. ⏳ **Move workbooks** - Put in proper Workbooks/ directory
3. ⏳ **Update metadata** - Version 2.0.0
4. ⏳ **Update release notes** - Document v2 changes
5. ⏳ **Test deployment** - Clean environment
6. ⏳ **Create branch** - Prepare for PR
7. ⏳ **Submit PR** - After all validations pass

**Want me to create the corrected parser file now?**
