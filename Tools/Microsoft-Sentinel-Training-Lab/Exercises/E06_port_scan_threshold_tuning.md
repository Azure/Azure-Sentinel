# Exercise 6 — Port Scan Detection & Threshold Tuning

**Rule:** `Lab Stage E2 - Port Scan Detection (Palo Alto)`  
**Difficulty:** Beginner  
**Prerequisites:** None

---

## Objective

Tune a port scan detection rule to reduce false positives while still catching real reconnaissance. You will establish a baseline, choose a threshold based on observed data, and update the detection query with enrichment fields that help analysts during triage.

## Background

Port scanning is one of the most common reconnaissance techniques (MITRE T1046). Attackers probe destination hosts across many ports to discover open services. In the Lab scenario, the attacker scans the internal network after establishing a C2 channel, looking for lateral movement targets.

Palo Alto firewalls log denied connections with the action `drop`, `deny`, or `reset-both`. When traffic has an `incomplete` application protocol, it indicates the session never completed — a strong indicator of scanning rather than legitimate traffic.

## Steps

### Step 1 — Establish a Baseline

Before choosing a threshold, understand the normal port diversity in your environment. Run this query in Advanced Hunting:

```kusto
CommonSecurityLog
| where TimeGenerated > ago(24h)
| where DeviceVendor == "Palo Alto Networks"
| where Activity in ("drop", "deny", "reset-both")
| where ApplicationProtocol == "incomplete"
| summarize DistinctPorts = dcount(DestinationPort) by SourceIP, DestinationIP
| summarize
    avg_ports = avg(DistinctPorts),
    p50 = percentile(DistinctPorts, 50),
    p90 = percentile(DistinctPorts, 90),
    p95 = percentile(DistinctPorts, 95),
    p99 = percentile(DistinctPorts, 99),
    max_ports = max(DistinctPorts)
```

**What to look for:**

| Percentile | Meaning |
|---|---|
| **p50** | Median behaviour — this is "normal" |
| **p90 / p95** | Higher-end but still relatively common |
| **p99** | Boundary where activity becomes rare |
| **max_ports** | Most extreme observed case |

**How to pick a threshold:**

| If p99 is... | Start with threshold... |
|---|---|
| 10 or lower | `> 15` |
| 11–20 | `> 20` |
| Above 20 | p99 + 20%, rounded up |

> **Goal:** Reduce noise while still surfacing suspicious scanning behaviour.

### Step 2 — Update the Rule with the Tuned Query

Open the rule in Defender → **Hunting** → **Custom detection rules** → find `Lab Stage E2 - Port Scan Detection (Palo Alto)` → **Edit**.

Replace the query with the following complete detection query. Change the threshold on the `where DistinctPorts >` line to match the value you chose in Step 1:

```kusto
CommonSecurityLog
| where TimeGenerated > ago(4h)
| where DeviceVendor == "Palo Alto Networks"
| where Activity in ("drop", "deny", "reset-both")
| where ApplicationProtocol == "incomplete"
| summarize
    FirstSeen = min(TimeGenerated),
    LastSeen = max(TimeGenerated),
    DistinctPorts = dcount(DestinationPort),
    PortList = make_set(DestinationPort, 25),
    EventCount = count()
    by SourceIP, DestinationIP, SourceHostName, SourceUserName
| extend ScanDurationMinutes = datetime_diff('minute', LastSeen, FirstSeen)
| extend PortsPerMinute = iff(
    ScanDurationMinutes > 0,
    todouble(DistinctPorts) / todouble(ScanDurationMinutes),
    todouble(DistinctPorts)
)
| where DistinctPorts > 20
| project
    FirstSeen,
    LastSeen,
    SourceIP,
    DestinationIP,
    DistinctPorts,
    EventCount,
    ScanDurationMinutes,
    PortsPerMinute,
    PortList,
    SourceHostName,
    SourceUserName
| extend
    TimeGenerated = FirstSeen,
    AccountUpn = SourceUserName,
    DeviceName = SourceHostName,
    RemoteIP = DestinationIP,
    ReportId = tostring(hash_sha256(strcat(SourceIP, DestinationIP, tostring(DistinctPorts))))
```

> **Note:** Replace `> 20` with the threshold you chose based on your baseline analysis.

**What each enrichment field provides:**

| Field | Purpose |
|---|---|
| `DistinctPorts` | How many unique ports were targeted |
| `PortList` | Which specific ports — helps identify the scan type |
| `EventCount` | Total volume of denied connections |
| `ScanDurationMinutes` | How long the scan lasted — distinguishes bursts from slow scans |
| `PortsPerMinute` | Scan speed — fast (>10/min) is more likely adversarial |

### Step 3 — Validate the Results

After saving the updated rule:

1. Run the query manually in Advanced Hunting to confirm it returns expected results
2. Verify the threshold is appropriate — check that alert volume is manageable
3. Confirm the enrichment fields (`PortList`, `PortsPerMinute`) appear in the output
4. Wait for the rule to trigger (or click **Run** to execute immediately)

**Validation checklist:**

- [ ] Query returns realistic scan candidates
- [ ] Alert volume is acceptable (not flooding the incident queue)
- [ ] `PortList` and `DistinctPorts` help the analyst understand the activity quickly
- [ ] `PortsPerMinute` adds useful triage context
- [ ] No obvious false positives from legitimate multi-port services

## Key Takeaways

- `dcount()` is the go-to aggregation function for detecting anomalous diversity
- Threshold tuning requires understanding baseline behaviour — always measure first
- `make_set()` provides valuable context in the alert by showing which ports were scanned
- Time window and schedule frequency must be aligned (lookback ≥ 4× frequency)

## Microsoft Learn References

- [summarize operator](https://learn.microsoft.com/en-us/kusto/query/summarize-operator)
- [dcount aggregation function](https://learn.microsoft.com/en-us/kusto/query/dcount-aggfunction)
- [Advanced hunting query best practices](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-best-practices)
- [MITRE T1046 — Network Service Discovery](https://attack.mitre.org/techniques/T1046/)

---

## Next Steps

Continue to **[Exercise 7 — Okta MFA Factor Manipulation](./E07_okta_mfa_manipulation.md)**
