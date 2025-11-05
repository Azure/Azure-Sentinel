# Connector Update Validation Checklist

## ✅ Critical Fix Applied
- **FIXED**: API Key parameter token in `LookoutStreaming_PollingConfig.json` (line 21)
  - Was: `"[[parameters('applicationKey')]"`
  - Now: `"[[parameters('applicationKey')]]"`

---

## How the Update Works

Your existing connector will be **updated in place** because:

1. **Same Resource Names** = In-Place Update (not new resources)
   - Data Connector Definition: `LookoutStreaming_Definition`
   - Polling Config: `LookoutMtd_PollingConfig`
   - Table: `LookoutMtdV2_CL`
   - DCR: `LookoutMtdDCR`

2. **V2 API Configuration** is correct:
   - ✅ Endpoint: `https://api.lookout.com/mra/stream/v2/events`
   - ✅ Header: `X-Event-Version: v2`
   - ✅ Event types: `THREAT,DEVICE,SMISHING_ALERT,AUDIT`

3. **Backward Compatible**:
   - All existing queries will continue to work
   - Legacy field names still mapped in parser

---

## Pre-Deployment Validation

### Step 1: Validate JSON Syntax
Run this in your terminal:

```bash
cd "/Users/fgravato/Documents/GitHub/Azure-Sentinel/Solutions/Lookout"

# Validate all connector JSON files
python3 -m json.tool "Data Connectors/LookoutStreamingConnector_ccp/LookoutStreaming_DataConnectorDefinition.json" > /dev/null && echo "✅ Definition OK"
python3 -m json.tool "Data Connectors/LookoutStreamingConnector_ccp/LookoutStreaming_PollingConfig.json" > /dev/null && echo "✅ Polling Config OK"
python3 -m json.tool "Data Connectors/LookoutStreamingConnector_ccp/LookoutStreaming_DCR.json" > /dev/null && echo "✅ DCR OK"
python3 -m json.tool "Data Connectors/LookoutStreamingConnector_ccp/LookoutStreaming_Table.json" > /dev/null && echo "✅ Table OK"
```

### Step 2: Test ARM Template (What-If)
Before deploying, see what will change:

```bash
az deployment group what-if \
  --resource-group "YOUR-RESOURCE-GROUP" \
  --template-file "Package/mainTemplate.json" \
  --parameters workspace="YOUR-WORKSPACE-NAME"
```

**Expected Output**: Should show "Modify" (not "Create") for existing resources.

---

## Deployment Steps

### Option 1: Via Azure Portal (Safest)

1. **Content Hub Method**:
   - Go to Sentinel → Content Hub
   - Search "Lookout"
   - Click **Update** (if available)
   - Or click **Install** (will update existing)

2. **Monitor the Update**:
   - Go to Data Connectors
   - Find "Lookout Mobile Threat Detection Connector"
   - Should still show "Connected" status
   - Click to verify configuration preserved

### Option 2: Via ARM Template

```bash
# Deploy the update
az deployment group create \
  --resource-group "YOUR-RESOURCE-GROUP" \
  --template-file "Package/mainTemplate.json" \
  --parameters \
    workspace="YOUR-WORKSPACE-NAME" \
    location="YOUR-REGION"
```

---

## Post-Deployment Validation

### Step 1: Verify Connector Status
1. Go to Sentinel → **Data Connectors**
2. Search "Lookout"
3. **Should show**:
   - Status: Connected ✅
   - Same configuration (API key preserved)
   - No duplicate connectors

### Step 2: Check Data Ingestion
In Sentinel **Logs**, run:

```kql
// Check if data is still flowing
LookoutMtdV2_CL
| where TimeGenerated > ago(1h)
| summarize 
    EventCount = count(),
    LatestEvent = max(TimeGenerated)
```

**Expected**: Events with timestamp within last hour.

### Step 3: Validate V2 Fields
Check that new v2 fields are populated:

```kql
// Check THREAT events
LookoutMtdV2_CL
| where event_type == "THREAT"
| where TimeGenerated > ago(24h)
| project 
    TimeGenerated,
    threat_id,
    threat_type,
    threat_severity,
    threat_classifications,
    threat_assessments,
    device_platform,
    device_os_version
| take 10
```

```kql
// Check SMISHING_ALERT events (new v2)
LookoutMtdV2_CL
| where event_type == "SMISHING_ALERT"
| where TimeGenerated > ago(24h)
| project 
    TimeGenerated,
    smishing_alert_id,
    smishing_alert_type,
    smishing_alert_severity,
    device_email_address
| take 10
```

```kql
// Check AUDIT events (new v2)
LookoutMtdV2_CL
| where event_type == "AUDIT"
| where TimeGenerated > ago(24h)
| project 
    TimeGenerated,
    audit_type,
    actor_type,
    actor_guid,
    target_type
| take 10
```

### Step 4: Test Parser Function
```kql
// Verify parser works with v2 data
LookoutEvents
| where TimeGenerated > ago(1h)
| summarize count() by EventType, ThreatSeverity
```

### Step 5: Verify Analytics Rules
```kql
// Check if rules are triggering
SecurityAlert
| where TimeGenerated > ago(24h)
| where AlertName contains "Lookout"
| summarize count() by AlertName, AlertSeverity
```

### Step 6: Test Workbook
1. Go to Sentinel → **Workbooks**
2. Open "Lookout Events V2"
3. Verify all charts load with data
4. Check for any errors or blank panels

---

## Rollback Plan (If Needed)

If something goes wrong:

1. **Connector still works but no new data**:
   - Go to Data Connectors → Lookout
   - Click **Disconnect**
   - Wait 2 minutes
   - Click **Connect** and re-enter API key

2. **Analytics rules not triggering**:
   - Go to Analytics → Rules
   - Find Lookout rules
   - Toggle **Disabled** then **Enabled**

3. **Full rollback**:
   ```bash
   # Redeploy previous version
   git checkout <previous-commit>
   az deployment group create \
     --resource-group "YOUR-RESOURCE-GROUP" \
     --template-file "Package/mainTemplate.json" \
     --parameters workspace="YOUR-WORKSPACE-NAME"
   ```

---

## Expected Behavior Summary

| Component | Before Update | After Update |
|-----------|--------------|--------------|
| **Connector Name** | Lookout Mobile Threat Detection Connector | Same (no change) |
| **Connection Status** | Connected | Still Connected |
| **Table Name** | LookoutMtdV2_CL | Same |
| **Event Types** | THREAT, DEVICE | THREAT, DEVICE, SMISHING_ALERT, AUDIT |
| **API Version** | v2 | v2 (enhanced fields) |
| **Existing Queries** | Work | Still work (backward compatible) |
| **New Fields** | N/A | Available in new events |

---

## Common Issues & Fixes

### Issue: "No data after update"
**Fix**: 
1. Check Data Connector status - should be "Connected"
2. Wait 5-10 minutes for buffering
3. Verify API credentials still valid
4. Check DCE (Data Collection Endpoint) logs

### Issue: "Duplicate connectors showing"
**Fix**: This shouldn't happen if names match. If it does:
1. Delete the duplicate (keep the Connected one)
2. Verify template uses exact same resource names

### Issue: "Analytics rules failing"
**Fix**:
1. Check if parser function exists: `LookoutEvents | take 1`
2. Re-deploy parser from `Parsers/LookoutEvents.yaml`
3. Refresh analytics rules (disable/enable)

### Issue: "Missing v2 fields"
**Fix**:
1. Verify connector is pointing to v2 endpoint
2. Check `X-Event-Version: v2` header in PollingConfig
3. Restart data connector

---

## Success Criteria

✅ **Your update is successful when**:
- [ ] Connector shows "Connected" status
- [ ] Data ingesting within 10 minutes of update
- [ ] All 4 event types visible: THREAT, DEVICE, SMISHING_ALERT, AUDIT
- [ ] V2 fields populated in query results
- [ ] Parser function works without errors
- [ ] Analytics rules enabled and creating alerts
- [ ] Workbook displays data correctly
- [ ] No duplicate connectors created
- [ ] Existing dashboards still work

---

**Next Steps**:
1. Run pre-deployment validation
2. Deploy update
3. Wait 15 minutes
4. Run post-deployment validation
5. Monitor for 24 hours
