# Exercise 8 — Watchlist Integration

**Rule:** `[E4] [AWS] Console Login Without MFA` _(the `[E4]` prefix is the deployed rule tag)_
**Deployed in:** `Artifacts/DetectionRules/rules.json`
**MITRE ATT&CK:** T1078.004 (Valid Accounts: Cloud Accounts)
**Difficulty:** Intermediate

---

## Objective

Create a Microsoft Sentinel **watchlist** and integrate it into a Custom Detection rule using the `_GetWatchlist()` KQL function. This exercise demonstrates how to enrich detection logic with contextual business data.

## Background

The rule `[E4] [AWS] Console Login Without MFA` detects AWS console logins where MFA was not used. On its own, the rule generates alerts for **all** non-MFA logins. By adding a watchlist, you can prioritise alerts for logins that affect **business-critical AWS services** — making the detection far more actionable.

### What is a Watchlist?

A watchlist is a named lookup table uploaded to Microsoft Sentinel as a CSV file. Once uploaded, it becomes queryable via the `_GetWatchlist('alias')` function in any KQL query, including Custom Detection rules.

> **Reference:** [Watchlists in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/watchlists)

### Common Watchlist Use Cases

| Use Case | Example |
|---|---|
| High-value assets | VIP users, critical servers, privileged accounts |
| Allowed/blocked lists | Trusted IPs, known-safe hashes |
| Business context enrichment | Service criticality, department ownership |
| Terminated employees | Former staff accounts that shouldn't be active |

## Steps

### Step 1 — Create the Watchlist CSV

Create a CSV file named `BusinessCriticalAWS.csv` with the following content:

```csv
EventSource,ServiceName,Criticality
iam.amazonaws.com,IAM,Critical
s3.amazonaws.com,S3,High
ec2.amazonaws.com,EC2,High
lambda.amazonaws.com,Lambda,Medium
kms.amazonaws.com,KMS,Critical
sts.amazonaws.com,STS,Critical
organizations.amazonaws.com,Organizations,Critical
cloudtrail.amazonaws.com,CloudTrail,High
```

This maps AWS API event sources to their service names and business criticality levels.

### Step 2 — Upload the Watchlist to Sentinel

1. Navigate to **Microsoft Sentinel** → **Configuration** → **Watchlist**
2. Click **+ New**
3. Fill in the details:

| Field | Value |
|---|---|
| Name | `BusinessCriticalAWS` |
| Alias | `BusinessCriticalAWS` |
| Description | Business-critical AWS services for detection enrichment |
| Source type | Local file |
| File | Upload `BusinessCriticalAWS.csv` |
| SearchKey | `EventSource` |

4. Click **Create**
5. Wait 1–2 minutes for the watchlist to become available in queries

### Step 3 — Verify the Watchlist in Advanced Hunting

Run this query to confirm the watchlist is accessible:

```kusto
_GetWatchlist('BusinessCriticalAWS')
| project EventSource, ServiceName, Criticality
```

You should see all rows from your CSV.

### Step 4 — Modify the Detection Query

Open `[E4] [AWS] Console Login Without MFA` and modify the query to join with the watchlist. Replace the existing query with:

```kusto
let critical_services = _GetWatchlist('BusinessCriticalAWS')
    | project EventSource, ServiceName, Criticality;
AWSCloudTrail
| where TimeGenerated > ago(4h)
| where EventName == "ConsoleLogin"
| where SessionMfaAuthenticated != "true"
| lookup kind=leftouter critical_services on EventSource
| extend
    ServiceName = coalesce(ServiceName, "Unknown"),
    Criticality = coalesce(Criticality, "Low")
| project
    TimeGenerated,
    UserIdentityUserName,
    SourceIpAddress,
    AWSRegion,
    EventName,
    EventSource,
    ServiceName,
    Criticality,
    MfaAuthenticated = SessionMfaAuthenticated
| extend
    AccountUpn = UserIdentityUserName,
    RemoteIP = SourceIpAddress,
    ReportId = tostring(hash_sha256(strcat(
        UserIdentityUserName, SourceIpAddress, tostring(TimeGenerated))))
```

### Key Changes Explained

| Change | Purpose |
|---|---|
| `_GetWatchlist('BusinessCriticalAWS')` | Loads the watchlist into a variable |
| `lookup kind=leftouter` | Joins the watchlist — events without a match still appear |
| `coalesce(Criticality, "Low")` | Default criticality for unmatched services |
| `ServiceName`, `Criticality` in output | Enriches alerts with business context |

### Alternative: Inline Watchlist with `in` Operator

For simpler use cases, filter instead of enriching:

```kusto
AWSCloudTrail
| where TimeGenerated > ago(4h)
| where EventName == "ConsoleLogin"
| where SessionMfaAuthenticated != "true"
| where EventSource in (
    (_GetWatchlist('BusinessCriticalAWS')
    | where Criticality == "Critical"
    | project SearchKey)
)
```

This only alerts when non-MFA logins access **Critical** services.

### Step 5 — Update the Alert Title

To include the business context in the alert, update the title to:

```
Console login without MFA by {{UserIdentityUserName}} — {{Criticality}} service
```

### Step 6 — Enable and Verify

1. Save the modified query
2. Enable the rule
3. Check that alerts now include `ServiceName` and `Criticality` enrichment

## Solution

The complete modified query is in Step 4 above. Key elements:

1. Watchlist loaded via `_GetWatchlist('BusinessCriticalAWS')`
2. Joined via `lookup kind=leftouter` on `EventSource`
3. Output enriched with `ServiceName` and `Criticality`

## Key Takeaways

- Watchlists add **business context** that pure log data doesn't have
- Use `lookup kind=leftouter` to enrich without filtering — all events still appear
- Use `in` with a watchlist subquery to filter to only critical assets
- The `SearchKey` defined during watchlist creation optimises lookups
- Watchlists refresh every 12 days in Sentinel — plan updates accordingly
- Watchlists are limited to 3.8 MB for local uploads (500 MB via Azure Storage)

## Microsoft Learn References

- [Create watchlists in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/watchlists-create)
- [Build queries with watchlists](https://learn.microsoft.com/en-us/azure/sentinel/watchlists-queries)
- [_GetWatchlist function](https://learn.microsoft.com/en-us/azure/sentinel/watchlists-queries#build-queries-with-watchlists)
- [MITRE T1078.004 — Valid Accounts: Cloud Accounts](https://attack.mitre.org/techniques/T1078/004/)
