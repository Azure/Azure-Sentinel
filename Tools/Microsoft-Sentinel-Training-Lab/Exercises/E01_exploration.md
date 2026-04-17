# Exercise 1 — Exploration: Hunting Across Your Data

**Topic:** Initial data exploration with Advanced Hunting and creating your first Custom Detection Rule
**Difficulty:** Beginner

---

### Objective

Get familiar with the data ingested into your Microsoft Sentinel workspace by running **Advanced Hunting** queries across multiple data sources. Then create your own **Custom Detection Rule** based on a pattern you discover.

### Background

After deploying the Training Lab solution, your workspace contains telemetry from multiple data sources simulating a real-world attack scenario. Before building detections, a SOC analyst's first task is to **understand the data** — what tables exist, what events they contain, and what patterns are worth alerting on.

This exercise teaches two foundational skills:

1. **Data exploration** — navigating tables, understanding schemas, and writing initial KQL queries in Advanced Hunting
2. **Rule creation** — turning a hunting query into a scheduled Custom Detection Rule

---

### Steps

#### Step 1 — Discover Your Tables

Open the **Microsoft Defender portal** → **Hunting** → **Advanced Hunting**.

Run the following query to see which tables contain data and how much:

```kusto
search *
| summarize EventCount = count() by $table
| sort by EventCount desc
```

<p align="center">
<img src="../Images/OnboardingImage21.png?raw=true">
</p>

This gives you an overview of all tables with data. You should see tables like `CommonSecurityLog`, `AWSCloudTrail`, `CrowdStrikeDetections`, `CrowdStrikeAlerts`, `OktaV2_CL`, `SecurityEvent`, and more.

#### Step 2 — Explore CrowdStrike Endpoint Data

CrowdStrike is the EDR (Endpoint Detection and Response) solution in this lab. Let's explore the alerts it generated:

```kusto
CrowdStrikeAlerts
| summarize AlertCount = count() by Name, SeverityName, Tactic
| sort by AlertCount desc
```

This shows you the types of alerts CrowdStrike raised. Notice the variety of **MITRE ATT&CK tactics** — from Initial Access through Exfiltration — indicating a multi-stage attack.

Now look at the timeline of alerts per device:

```kusto
CrowdStrikeAlerts
| extend DeviceName = tostring(split(DisplayName, " on ")[-1])
| summarize
    AlertCount = count(),
    Tactics = make_set(Tactic),
    FirstAlert = min(TimeGenerated),
    LastAlert = max(TimeGenerated)
    by DeviceName
| sort by AlertCount desc
```

> **Key insight:** If a single device has alerts spanning multiple MITRE tactics (e.g., Execution, Credential Access, Lateral Movement), it is likely compromised and being used as a pivot point in a multi-stage attack.

#### Step 3 — Explore Firewall Traffic (Palo Alto)

The `CommonSecurityLog` table contains Palo Alto firewall logs. Let's get a traffic overview:

```kusto
CommonSecurityLog
| where DeviceVendor == "Palo Alto Networks"
| summarize
    TotalEvents = count(),
    DistinctSources = dcount(SourceIP),
    DistinctDestinations = dcount(DestinationIP)
    by Activity
| sort by TotalEvents desc
```

Now look for denied traffic — potential reconnaissance or blocked attacks:

```kusto
CommonSecurityLog
| where DeviceVendor == "Palo Alto Networks"
| where Activity in ("drop", "deny", "reset-both")
| summarize
    BlockedConnections = count(),
    TargetedPorts = dcount(DestinationPort)
    by SourceIP
| sort by BlockedConnections desc
| take 10
```

#### Step 4 — Explore Identity Events (Okta)

The `OktaV2_CL` table contains identity events from Okta. Let's check for suspicious activity:

```kusto
OktaV2_CL
| summarize EventCount = count() by EventOriginalType, OriginalOutcomeResult
| sort by EventCount desc
```

Look for failed logins and MFA-related events:

```kusto
OktaV2_CL
| where OriginalOutcomeResult == "FAILURE"
| summarize
    FailedAttempts = count(),
    DistinctIPs = dcount(SrcIpAddr),
    Countries = make_set(SrcGeoCountry)
    by ActorUsername
| sort by FailedAttempts desc
```

#### Step 5 — Explore Cloud Activity (AWS)

The `AWSCloudTrail` table tracks API calls in AWS. Check what happened:

```kusto
AWSCloudTrail
| summarize EventCount = count() by EventName, EventSource
| sort by EventCount desc
| take 15
```

Look for failed operations — potential attacker reconnaissance or privilege escalation attempts:

```kusto
AWSCloudTrail
| where isnotempty(ErrorCode)
| summarize
    FailedCalls = count(),
    ErrorCodes = make_set(ErrorCode)
    by UserIdentityUserName, EventName
| sort by FailedCalls desc
```

#### Step 6 — Build a Cross-Source Summary

Now combine insights from multiple sources to understand the full attack scope:

```kusto
union
    (CrowdStrikeAlerts
    | where SeverityName in ("Critical", "High")
    | project TimeGenerated, Source = "CrowdStrike", Activity = Name, Severity = SeverityName),
    (CommonSecurityLog
    | where DeviceVendor == "Palo Alto Networks"
    | where DeviceEventClassID == "THREAT"
    | project TimeGenerated, Source = "Palo Alto", Activity = Activity, Severity = LogSeverity),
    (OktaV2_CL
    | where EventOriginalType has "mfa" or EventOriginalType has "deactivate"
    | project TimeGenerated, Source = "Okta", Activity = EventOriginalType, Severity = EventSeverity),
    (AWSCloudTrail
    | where EventName in ("CreateUser", "AttachUserPolicy", "CreateAccessKey", "StopLogging")
    | project TimeGenerated, Source = "AWS", Activity = EventName, Severity = "High")
| sort by TimeGenerated asc
```

This gives you a **chronological timeline** of suspicious activity across all data sources — the foundation of any investigation.

---

### Create a Custom Detection Rule

Now that you understand the data, let's turn a hunting query into a detection rule. You'll create a rule that detects **multi-tactic activity on a single endpoint** — a strong indicator of a compromised device.

#### Step 7 — Write the Detection Query

This query finds devices with CrowdStrike alerts spanning 3 or more MITRE ATT&CK tactics within a 4-hour window:

```kusto
CrowdStrikeAlerts
| where TimeGenerated > ago(4h)
| where SeverityName in ("Critical", "High")
| extend DeviceName = tostring(split(DisplayName, " on ")[-1])
| summarize
    TacticCount = dcount(Tactic),
    Tactics = make_set(Tactic),
    AlertNames = make_set(Name, 10),
    AlertCount = count(),
    FirstSeen = min(TimeGenerated),
    LastSeen = max(TimeGenerated)
    by DeviceName, AgentId
| where TacticCount >= 3
| project
    TimeGenerated = FirstSeen,
    DeviceName,
    TacticCount,
    Tactics,
    AlertNames,
    AlertCount,
    FirstSeen,
    LastSeen,
    ReportId = tostring(hash_sha256(strcat(DeviceName, tostring(FirstSeen))))
```

Run this query in Advanced Hunting to verify it returns results.

#### Step 8 — Create the Rule

1. After running the query, select **Create detection rule**

<p align="center">
<img src="../Images/OnboardingImage22.png?raw=true">
</p>

2. Fill in the rule details:

| Field | Value |
|---|---|
| **Name** | `[E1] Multi-Tactic Compromise on Single Device` |
| **Description** | `Detects when a single endpoint has CrowdStrike alerts spanning 3 or more MITRE ATT&CK tactics, indicating a multi-stage compromise.` |
| **Severity** | High |
| **MITRE ATT&CK** | Leave default (auto-detected) |

3. On the **Impacted entities** tab, map:
   - **Device** → `DeviceName`

4. On the **Actions** tab, leave empty for now (no automated response)

5. Set the **Schedule**:
   - **Frequency** → Every 1 hour
   - **Lookback** → 4 hours

6. Select **Create** to save the rule

<p align="center">
<img src="../Images/OnboardingImage32.png?raw=true">
</p>

#### Step 9 — Verify the Rule

1. Navigate to **Hunting** → **Custom detection rules**
2. Find your new rule `[E1] Multi-Tactic Compromise on Single Device`
3. Click **Run** to execute it immediately
4. Check **Triggered alerts** to verify the rule fires

---

### Key Takeaways

- **`search *`** is the fastest way to discover what data exists in your workspace
- **`summarize` with `dcount`** reveals patterns — distinct ports, distinct IPs, distinct tactics
- **`union`** lets you correlate events across data sources into a single timeline
- **`make_set()`** collects distinct values for alert enrichment
- A good detection rule combines aggregation (`summarize`) with a threshold (`where TacticCount >= 3`)
- Always include `TimeGenerated` and `ReportId` in your detection query output — these are required by the Custom Detection framework

### Microsoft Learn References

- [Advanced hunting overview](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-overview)
- [Learn the query language (KQL)](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-query-language)
- [Custom detection rules](https://learn.microsoft.com/en-us/defender-xdr/custom-detections-overview)
- [Create a custom detection rule](https://learn.microsoft.com/en-us/defender-xdr/custom-detection-rules)
