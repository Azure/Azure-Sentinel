# Create Custom Lookout Dashboard

## Quick Method: Use Azure Portal

### Step 1: Create New Workbook

1. Go to **Microsoft Sentinel** → Your workspace
2. Click **Workbooks** on the left
3. Click **+ Add workbook**
4. Click **Edit** (pencil icon at top)

### Step 2: Add Widgets

Click **Add** → **Add query** for each section below:

---

## Widget 1: Event Summary (Last 7 Days)

**Query:**
```kql
let ParsedEvents = LookoutMtdV2_CL
    | extend EventType = log_type;
ParsedEvents
| where TimeGenerated > ago(7d)
| summarize Count = count() by EventType
| render piechart
```

**Settings:**
- Visualization: **Pie chart**
- Title: **Event Types - Last 7 Days**

Click **Done Editing**

---

## Widget 2: Threat Severity Over Time

**Query:**
```kql
let ParsedEvents = LookoutMtdV2_CL
    | extend 
        EventType = log_type,
        ThreatSeverity = tostring(threat.severity);
ParsedEvents
| where TimeGenerated > ago(7d)
| where EventType == "THREAT"
| summarize Count = count() by bin(TimeGenerated, 1h), ThreatSeverity
| render timechart
```

**Settings:**
- Visualization: **Time chart**
- Title: **Threat Severity Timeline**

---

## Widget 3: Top Threats

**Query:**
```kql
let ParsedEvents = LookoutMtdV2_CL
    | extend 
        EventType = log_type,
        ThreatType = tostring(threat.type),
        ThreatSeverity = tostring(threat.severity),
        DeviceEmail = tostring(threat.device.email);
ParsedEvents
| where TimeGenerated > ago(7d)
| where EventType == "THREAT"
| summarize 
    Count = count(),
    Severity = max(ThreatSeverity),
    AffectedDevices = dcount(DeviceEmail)
    by ThreatType
| sort by Count desc
```

**Settings:**
- Visualization: **Table** or **Bar chart**
- Title: **Top Threats by Type**

---

## Widget 4: Affected Devices

**Query:**
```kql
let ParsedEvents = LookoutMtdV2_CL
    | extend 
        EventType = log_type,
        DeviceEmail = tostring(threat.device.email),
        ThreatSeverity = tostring(threat.severity),
        ThreatType = tostring(threat.type);
ParsedEvents
| where TimeGenerated > ago(7d)
| where EventType == "THREAT"
| summarize 
    ThreatCount = count(),
    HighestSeverity = max(ThreatSeverity),
    ThreatTypes = make_set(ThreatType),
    LastSeen = max(TimeGenerated)
    by DeviceEmail
| sort by ThreatCount desc
```

**Settings:**
- Visualization: **Table**
- Title: **Devices with Threats**

---

## Widget 5: Audit Events Summary

**Query:**
```kql
let ParsedEvents = LookoutMtdV2_CL
    | extend 
        EventType = log_type,
        ActorType = tostring(actor.type);
ParsedEvents
| where TimeGenerated > ago(7d)
| where EventType == "AUDIT"
| summarize Count = count() by ActorType
| render columnchart
```

**Settings:**
- Visualization: **Column chart**
- Title: **Audit Events by Actor Type**

---

## Widget 6: Recent High Severity Threats (Table)

**Query:**
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
| project 
    TimeGenerated,
    Severity = ThreatSeverity,
    Type = ThreatType,
    Device = DeviceEmail,
    Details = ThreatDetails
| sort by TimeGenerated desc
| take 10
```

**Settings:**
- Visualization: **Table**
- Title: **Recent High Severity Threats**

---

## Step 3: Save the Workbook

1. Click **Done Editing** at the top
2. Click **Save** (disk icon)
3. Name it: **"Lookout Mobile Threats Dashboard"**
4. Resource Group: **lookout-sentinel-rg**
5. Location: **East US**
6. Click **Apply**

---

## Quick Copy-Paste Dashboard

Alternatively, I can create a complete workbook JSON file for you to import. Want me to do that?

---

## View Your Dashboard

After saving:
1. Go to **Workbooks** → **My workbooks**
2. Find **"Lookout Mobile Threats Dashboard"**
3. Click to open
4. Set time range at top (default: Last 7 days)

Your dashboard will auto-refresh with new data!
