# Simple Validation Steps - No Technical Experience Required

## What You Need
- Access to Azure Portal (portal.azure.com)
- A Microsoft Sentinel workspace already set up
- Lookout API credentials (you should have these from Lookout)

---

## Step 1: Open Azure Portal
1. Go to https://portal.azure.com
2. Sign in with your credentials
3. In the search bar at the top, type **"Microsoft Sentinel"**
4. Click on **Microsoft Sentinel** from the results

---

## Step 2: Select Your Workspace
1. You'll see a list of Sentinel workspaces
2. Click on the one you want to use for testing
3. You're now in your Sentinel workspace

---

## Step 3: Install the Lookout Solution (Easiest Method)

### Option A: From Content Hub (Recommended)
1. On the left menu, click **Content hub**
2. In the search box, type **"Lookout"**
3. Click on the **Lookout** solution card
4. Click the **Install** button
5. Wait for installation to complete (5-10 minutes)

### Option B: If Content Hub doesn't work
Skip to Step 4 and we'll do it manually.

---

## Step 4: Check If Data Is Coming In

1. On the left menu, click **Logs**
2. Close any popup windows
3. Copy and paste this query into the query box:

```kql
LookoutMtdV2_CL
| where TimeGenerated > ago(24h)
| take 10
```

4. Click **Run**
5. **If you see data**: Great! Continue to Step 5
6. **If you see no data**: The connector isn't set up yet - we need to configure it first

---

## Step 5: Verify the Parser Works

1. In the same **Logs** window, clear the previous query
2. Copy and paste this query:

```kql
LookoutEvents
| where TimeGenerated > ago(24h)
| take 5
```

3. Click **Run**
4. You should see events with fields like `EventType`, `ThreatType`, `DeviceGuid`

---

## Step 6: Check Analytics Rules

1. On the left menu, click **Analytics**
2. Click on **Rules** tab at the top
3. In the search box, type **"Lookout"**
4. You should see these rules:
   - ✅ Lookout - High Severity Mobile Threats Detected
   - ✅ Lookout - Device Compliance and Security Status Changes
   - ✅ Lookout - Critical Smishing and Phishing Alerts
   - ✅ Lookout - Critical Audit and Policy Changes

5. Make sure they're **Enabled** (green toggle switch)

---

## Step 7: Check the Workbook

1. On the left menu, click **Workbooks**
2. Click on **My workbooks** or **Templates** tab
3. Look for **"Lookout Events V2"** or **"Lookout Events"**
4. Click on it to open
5. You should see charts and graphs with your Lookout data

---

## Step 8: Simple Validation Test

Run this all-in-one validation query in **Logs**:

```kql
// Quick validation of Lookout v2 components
print "=== VALIDATION RESULTS ==="
| extend TestName = "Starting validation..."

// Test 1: Check raw data
union
(LookoutMtdV2_CL
| where TimeGenerated > ago(24h)
| summarize RawEventCount = count()
| extend TestName = "1. Raw Data Ingestion"),

// Test 2: Check parser
(LookoutEvents
| where TimeGenerated > ago(24h)
| summarize ParsedEventCount = count(), EventTypes = make_set(EventType)
| extend TestName = "2. Parser Function"),

// Test 3: Check for recent alerts
(SecurityAlert
| where TimeGenerated > ago(24h)
| where AlertName contains "Lookout"
| summarize AlertCount = count()
| extend TestName = "3. Analytics Rules")

| project TestName
```

---

## Expected Results

✅ **Success looks like:**
- Test 1: Shows a number greater than 0
- Test 2: Shows event counts and event types
- Test 3: Shows alerts (may be 0 if no threats detected)

❌ **Problems:**
- All tests show 0 or nothing: Data connector not working
- Test 1 works, Test 2 fails: Parser issue
- Tests 1 & 2 work, Test 3 fails: Analytics rules not enabled

---

## If You Get Stuck

**No data at all?**
- Your Lookout data connector needs to be configured
- You need to set it up with your Lookout API credentials first

**Need help with setup?**
Let me know and I'll create an even simpler guide for the data connector setup.

---

## Quick Reference: Where Things Are

| What | Where to Find It |
|------|-----------------|
| Run queries | Sentinel → Logs |
| Check rules | Sentinel → Analytics → Rules |
| View dashboards | Sentinel → Workbooks |
| Install solution | Sentinel → Content hub |
| Check alerts | Sentinel → Incidents |

---

**Start with Step 1 and let me know where you get stuck!**
