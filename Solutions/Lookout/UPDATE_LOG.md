# Lookout Sentinel Solution - Complete Update Log

**Date**: November 3, 2025
**Workspace**: lookout-sentinel-ccf1
**Resource Group**: lookout-sentinel-rg
**Subscription**: a4b6a533-f801-49d5-ad81-719bc7264956

---

## ✅ What Was Completed

### 1. Deployment
- ✅ Deployed Lookout v2 solution via ARM template to Azure Sentinel
- ✅ Updated Lookout CCF data connector (fixed APIKey parameter bug)
- ✅ Data connector status: **Connected**
- ✅ Data flowing: 8 events (6 AUDIT, 2 THREAT - HIGH severity)
- ✅ Deployment name: `lookout-v2-deployment-20251103-172835`

### 2. Data Validation
- ✅ Raw data table: `LookoutMtdV2_CL`
- ✅ Event types confirmed: THREAT, AUDIT (v2 feature working!)
- ✅ Detected threat: Rogue WiFi "Mugshot Café Wi-fi" on frank.srp@gmail.com
- ✅ Last data received: 11/3/2025, 12:50:10 PM

### 3. Parser Fixed
- ✅ Identified data structure mismatch (uses `log_type` not `event_type`)
- ✅ Created working inline parser for queries
- ✅ Issue: Duplicate `LookoutEvents` function exists (needs cleanup)

### 4. Workbooks Created
- ✅ **Lookout CCF** - Basic workbook (deployed, has errors due to function conflict)
- ✅ **LookoutExecutiveDashboard.json** - Executive metrics dashboard
- ✅ **LookoutComprehensiveDashboard.json** - Full IOA/investigation dashboard

---

## 📁 Files Created (All in /Users/fgravato/Documents/GitHub/Azure-Sentinel/Solutions/Lookout/)

1. **SIMPLE_VALIDATION_STEPS.md** - Beginner validation guide
2. **INJECT_TEST_DATA.md** - How to inject test data
3. **CONNECTOR_UPDATE_VALIDATION.md** - Connector update validation checklist
4. **CLOUDSHELL_DEPLOYMENT.md** - Azure Cloud Shell deployment guide
5. **FIND_YOUR_VARIABLES.md** - How to find Azure variables
6. **READY_TO_DEPLOY.md** - Ready-to-run deployment commands
7. **FIXED_PARSER.kql** - Fixed parser for actual data structure
8. **CUSTOM_DASHBOARD.md** - Custom dashboard creation guide
9. **LookoutExecutiveDashboard.json** - Executive dashboard (Splunk-style)
10. **LookoutComprehensiveDashboard.json** - Comprehensive IOA dashboard
11. **UPDATE_LOG.md** - This file

---

## 🔧 Critical Fixes Made

### Fix #1: APIKey Parameter Bug
**File**: `Data Connectors/LookoutStreamingConnector_ccp/LookoutStreaming_PollingConfig.json`
**Line**: 21
**Changed**:
```json
"APIKey": "[[parameters('applicationKey')]",  // WRONG
```
**To**:
```json
"APIKey": "[[parameters('applicationKey')]]", // FIXED
```

### Fix #2: Parser Data Structure
**Issue**: Deployed parser expects `event_type` but data uses `log_type`

**Working Parser** (use this in queries):
```kql
let ParsedLookoutEvents = 
    LookoutMtdV2_CL
    | extend 
        EventType = log_type,
        EventId = id,
        ThreatType = tostring(threat.type),
        ThreatSeverity = tostring(threat.severity),
        ThreatStatus = tostring(threat.status),
        DeviceEmailAddress = tostring(threat.device.email),
        DeviceGuid = tostring(threat.device.guid),
        ThreatNetworkSSID = tostring(threat.details.network_ssid),
        ActorType = tostring(actor.type),
        TargetType = tostring(target.type);
ParsedLookoutEvents
```

---

## 📊 Working Queries (Copy-Paste Ready)

### Query 1: Event Summary
```kql
let ParsedEvents = LookoutMtdV2_CL
    | extend EventType = log_type;
ParsedEvents
| where TimeGenerated > ago(7d)
| summarize count() by EventType, tostring(threat.severity)
```

### Query 2: High Severity Threats
```kql
let ParsedEvents = LookoutMtdV2_CL
    | extend 
        EventType = log_type,
        ThreatType = tostring(threat.type),
        ThreatSeverity = tostring(threat.severity),
        DeviceEmail = tostring(threat.device.email),
        ThreatDetails = tostring(threat.details.network_ssid);
ParsedEvents
| where TimeGenerated > ago(7d)
| where EventType == "THREAT"
| where ThreatSeverity in ("HIGH", "CRITICAL")
| project TimeGenerated, ThreatType, ThreatSeverity, DeviceEmail, ThreatDetails
| sort by TimeGenerated desc
```

### Query 3: Audit Events (NEW v2 Feature)
```kql
let ParsedEvents = LookoutMtdV2_CL
    | extend 
        EventType = log_type,
        ActorType = tostring(actor.type),
        TargetType = tostring(target.type);
ParsedEvents
| where TimeGenerated > ago(7d)
| where EventType == "AUDIT"
| summarize count() by ActorType
```

### Query 4: Device Investigation
```kql
let ParsedEvents = LookoutMtdV2_CL
    | extend 
        EventType = log_type,
        DeviceEmail = tostring(threat.device.email),
        ThreatType = tostring(threat.type),
        ThreatSeverity = tostring(threat.severity);
ParsedEvents
| where TimeGenerated > ago(7d)
| where DeviceEmail == "frank.srp@gmail.com"
| project TimeGenerated, EventType, ThreatType, ThreatSeverity
| sort by TimeGenerated desc
```

---

## 🚀 How to Redeploy Everything (If Deleted)

### Step 1: Redeploy Solution
```bash
# In Azure Cloud Shell
cd ~/Lookout/Package

SUBSCRIPTION_ID="a4b6a533-f801-49d5-ad81-719bc7264956"
RESOURCE_GROUP="lookout-sentinel-rg"
WORKSPACE_NAME="lookout-sentinel-ccf1"
LOCATION="eastus"

az account set --subscription $SUBSCRIPTION_ID

az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file mainTemplate.json \
  --parameters workspace=$WORKSPACE_NAME location=$LOCATION \
  --name "lookout-v2-redeploy-$(date +%Y%m%d-%H%M%S)"
```

### Step 2: Import Executive Dashboard
1. Go to Sentinel → Workbooks → + Add workbook
2. Click Edit → Advanced Editor
3. Delete all JSON
4. Copy content from `LookoutExecutiveDashboard.json`
5. Paste and click Apply
6. Save as "Lookout Executive Dashboard"

### Step 3: Import Comprehensive Dashboard
1. Repeat Step 2 with `LookoutComprehensiveDashboard.json`
2. Save as "Lookout IOA Investigation Dashboard"

---

## 🎯 Current State Summary

### Components Deployed
- ✅ Data Connector: Lookout Mobile Threat Detection Connector (CCF)
- ✅ Data Connector Definition: `LookoutStreaming_Definition`
- ✅ Polling Config: `LookoutMtd_PollingConfig`
- ✅ Parser: `Lookout Data Parser` (has issues, use inline version)
- ✅ Analytics Rules: 4 rules deployed
- ✅ Workbook: "Lookout CCF" (needs fixing)
- ✅ Content Package: `lookoutinc.lookout_mtd_sentinel`

### Data Statistics (as of 11/3/2025)
- **Total Events**: 8
- **THREAT Events**: 2 (HIGH severity)
  - Type: NETWORK (Rogue WiFi)
  - Device: frank.srp@gmail.com
  - Network: "Mugshot Café Wi-fi"
- **AUDIT Events**: 6 (NEW v2 feature!)
- **Last Data**: 11/3/2025 12:50:10 PM

### Known Issues
1. **Duplicate LookoutEvents function** - causes errors in workbooks
   - **Workaround**: Use inline parser in queries (see "Working Queries" above)
   - **Fix**: Need to delete one of the duplicate functions

2. **Workbook "Lookout CCF" has errors** - due to function conflict
   - **Workaround**: Use the new comprehensive dashboards instead

---

## 📋 Validation Checklist (Run This After Redeployment)

### 1. Data Connector
```bash
# Check in Portal
Sentinel → Data connectors → Search "Lookout"
# Should show: Connected, Last received < 30 min ago
```

### 2. Data Ingestion
```kql
LookoutMtdV2_CL
| where TimeGenerated > ago(1h)
| summarize count()
```
**Expected**: Number > 0

### 3. Event Types
```kql
LookoutMtdV2_CL
| where TimeGenerated > ago(24h)
| extend EventType = log_type
| summarize count() by EventType
```
**Expected**: THREAT, AUDIT (and possibly DEVICE, SMISHING_ALERT)

### 4. Workbooks
```bash
Sentinel → Workbooks → My workbooks
```
**Expected**: See your imported dashboards

### 5. Analytics Rules
```bash
Sentinel → Analytics → Rules
# Search: "Lookout"
```
**Expected**: 4 enabled rules

---

## 🔐 Security Note

**NEVER commit these files with real credentials:**
- API Keys
- Subscription IDs (already in this file - keep secure!)
- Workspace IDs
- Connection strings

This document contains your subscription ID and resource group name. Keep it secure!

---

## 📞 Support Information

### If Someone Deleted Your Workbook Again

1. **Check Audit Logs**:
   ```bash
   # In Azure Cloud Shell
   az monitor activity-log list \
     --resource-group lookout-sentinel-rg \
     --start-time 2025-11-03T00:00:00Z \
     --query "[?contains(operationName.value, 'workbooks')].{Time:eventTimestamp, User:caller, Operation:operationName.value, Status:status.value}" \
     --output table
   ```

2. **Redeploy from this directory**:
   - All dashboard JSON files are saved locally
   - Follow "How to Redeploy Everything" section above

3. **Lock the workbook**:
   - After redeploying, add a resource lock
   - Azure Portal → Resource Groups → lookout-sentinel-rg → Locks
   - Add "Read-only" or "Delete" lock

---

## 🎓 What You Learned

1. ✅ How to deploy Sentinel solutions via ARM template
2. ✅ How to use Azure Cloud Shell for deployments
3. ✅ How to validate data connectors
4. ✅ How to write KQL queries for mobile threat data
5. ✅ How to create Azure Workbooks
6. ✅ How to troubleshoot parser and function issues
7. ✅ How Lookout v2 API works (THREAT, AUDIT, SMISHING_ALERT events)

---

## 📝 Next Steps (Optional Improvements)

1. **Fix duplicate parser function** - delete one via API or Portal
2. **Add more analytics rules** - for SMISHING_ALERT events
3. **Configure alerting** - route high-severity threats to email/Teams
4. **Add data retention** - configure Log Analytics retention policy
5. **Enable workbook auto-refresh** - set refresh interval
6. **Add resource locks** - prevent accidental deletion

---

**End of Update Log**

*All changes documented and files preserved. You can now redeploy everything if needed!*
