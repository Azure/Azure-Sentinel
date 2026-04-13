# Exercise 6 — Port Scan Detection & Threshold Tuning

**Rule:** `[E2] [Palo Alto] Port Scan Detection` _(the `[E2]` prefix is the deployed rule tag)_
**Deployed in:** `Artifacts/DetectionRules/rules.json`
**MITRE ATT&CK:** T1046 (Network Service Discovery)
**Difficulty:** Beginner

---

## Objective

Learn how to detect network reconnaissance by aggregating firewall deny logs and applying threshold-based alerting. Understand how to tune detection thresholds to balance alert fidelity vs coverage.

## Background

Port scanning is one of the most common reconnaissance techniques (MITRE T1046). Attackers probe destination hosts across many ports to discover open services. In the Lab scenario, the attacker scans the internal network after establishing a C2 channel, looking for lateral movement targets.

Palo Alto firewalls log denied connections with the action `drop`, `deny`, or `reset-both`. When traffic has an `incomplete` application protocol, it indicates the session never completed — a strong indicator of scanning rather than legitimate traffic.

## Techniques Covered

### KQL Aggregation — `summarize` and `dcount`

```kusto
CommonSecurityLog
| where Activity in ("drop", "deny", "reset-both")
| where ApplicationProtocol == "incomplete"
| summarize
    DistinctPorts = dcount(DestinationPort),
    PortList = make_set(DestinationPort, 25),
    EventCount = count()
    by SourceIP, DestinationIP
| where DistinctPorts > 20
```

| Function | Purpose |
|---|---|
| `dcount()` | Counts distinct values — ideal for detecting diversity (many ports = scan) |
| `make_set()` | Collects distinct values into an array — useful for alert enrichment |
| `count()` | Total events — measures volume |
| `by` clause | Groups results per source-destination pair |

### Threshold Tuning

The current threshold is **20 distinct ports**. Consider:

| Threshold | Trade-off |
|---|---|
| `> 5` | High sensitivity — catches slow scans but may alert on legitimate services |
| `> 20` | Balanced — catches horizontal scans, filters legitimate multi-port services |
| `> 50` | Low sensitivity — only catches aggressive wide scans |

> **Best practice:** Start with a higher threshold to reduce noise, then lower it as you understand your environment's baseline.

### Time Window Impact

The `ago(4h)` lookback matches the 1-hour schedule frequency (4x lookback is default). A slower scan across 24h would be missed. For slow scans, consider:

```kusto
// Wider window for slow scans
| where TimeGenerated > ago(24h)
// With a 24h schedule frequency to match
```

## Steps

### Step 1 — Analyse the Baseline

Run this query in Advanced Hunting to understand normal port diversity:

```kusto
CommonSecurityLog
| where TimeGenerated > ago(24h)
| where DeviceVendor == "Palo Alto Networks"
| where Activity in ("drop", "deny", "reset-both")
| summarize DistinctPorts = dcount(DestinationPort) by SourceIP, DestinationIP
| summarize
    avg_ports = avg(DistinctPorts),
    p50 = percentile(DistinctPorts, 50),
    p90 = percentile(DistinctPorts, 90),
    p99 = percentile(DistinctPorts, 99),
    max_ports = max(DistinctPorts)
```

This tells you the normal distribution of port diversity — set your threshold above the p99 to avoid false positives.

### Step 2 — Modify the Threshold

1. Open the rule in Defender → **Hunting** → **Custom detection rules**
2. Click **Modify query**
3. Change the threshold from `20` to your chosen value
4. Run the query to preview results

### Step 3 — Add Time-Based Enrichment

Extend the query to calculate scan **speed** (ports per minute):

```kusto
| extend ScanDurationMinutes = datetime_diff('minute', LastSeen, FirstSeen)
| extend PortsPerMinute = iff(ScanDurationMinutes > 0,
    toreal(DistinctPorts) / toreal(ScanDurationMinutes), toreal(DistinctPorts))
```

A fast scan (>10 ports/minute) is more likely adversarial than a slow one.

### Step 4 — Enable and Verify

1. Save the modified query
2. Enable the rule
3. Verify alerts appear with the `DistinctPorts` and `PortList` enrichment

## Solution

The deployed rule already works with a threshold of 20. The extension challenge is adding `PortsPerMinute` to the output:

```kusto
| extend ScanDurationMinutes = datetime_diff('minute', LastSeen, FirstSeen)
| extend PortsPerMinute = iff(ScanDurationMinutes > 0,
    toreal(DistinctPorts) / toreal(ScanDurationMinutes), toreal(DistinctPorts))
```

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
