# Exercise 11 — Data Lake KQL Jobs

**Topic:** Create and schedule KQL jobs in the Microsoft Sentinel data lake  
**Difficulty:** Intermediate  
**Prerequisites:** Data lake enabled on your workspace (see [Onboarding](./Onboarding.md))

---

## Objective

Learn how to create a **KQL job** that queries data in the Microsoft Sentinel data lake and promotes the results to the analytics tier. You will create a scheduled job that aggregates Palo Alto firewall traffic from `CommonSecurityLog` into a summary table, making the aggregated data available for detections and hunting in Defender XDR.

## Background

### What are KQL Jobs?

KQL jobs are one-time or scheduled queries that run against data stored in the **data lake tier**. They are designed for:

- **Long-running investigations** — query months or years of historical data
- **Data aggregation** — compress high-volume raw logs into meaningful summaries
- **Threat intelligence matching** — retrospective IOC scans across historical data
- **Anomaly detection** — pattern analysis across extended time ranges

The key concept is **data promotion**: KQL jobs take data from the low-cost data lake tier and write the results to the analytics tier, where it becomes available for Advanced Hunting queries and custom detection rules.

> **Cost consideration:** Storage in the analytics tier costs more than the data lake tier. Use KQL queries to `project` only the columns you need and `where` filters to reduce the volume of promoted data.

### How It Fits Into This Lab

The Lab already uses this pattern. The detection rule `[S8] [Palo Alto] Data Lake Promoted Threat` queries the `PaloAlto_ThreatSummary_KQL_CL` table — a table created by a KQL job that aggregates firewall data. In this exercise, you will create that KQL job yourself.

| Component | Role |
|---|---|
| **Source data** | `CommonSecurityLog` (Palo Alto firewall logs in the data lake) |
| **KQL job** | Aggregates traffic into source-destination pair summaries |
| **Output table** | `PaloAlto_ThreatSummary_KQL_CL` (analytics tier) |
| **Detection rule** | `[S8]` queries the output table for threats |

### Data Lake Ingestion Latency

The data lake tier stores data in cold storage. There is a typical latency of **up to 15 minutes** before newly ingested data is available for querying. When scheduling KQL jobs, you must account for this latency by including a delay parameter in your queries:

```kusto
let delay = 15m;
let endTime = now() - delay;
let startTime = endTime - 1h;
CommonSecurityLog
| where TimeGenerated between (startTime .. endTime)
```

This ensures your job only queries data that is fully ingested and available.

---

## Steps

### Step 1 — Navigate to KQL Jobs in the Portal

There are two ways to access KQL jobs:

**Option A — From the Jobs management page:**

1. Open the **Microsoft Defender portal** (https://security.microsoft.com)
2. In the left navigation, expand **Microsoft Sentinel**
3. Select **Data lake exploration** → **Jobs**
4. You will see the jobs management page listing any existing KQL jobs

<p align="center">
<img src="../Images/OnboardingImage10.png?raw=true">
</p>

**Option B — From the KQL query editor:**

1. Open the **Microsoft Defender portal**
2. Navigate to **Microsoft Sentinel** → **Data lake exploration** → **KQL queries**
3. Write your query in the editor
4. Select the **Create job** button in the upper right corner of the query editor

<p align="center">
<img src="../Images/OnboardingImage11.png?raw=true">
</p>

---

### Step 2 — Create a New KQL Job

1. From the **Jobs** page, select **Create job**

2. Enter the following job details:

   | Field | Value |
   |---|---|
   | **Job name** | `PaloAlto_ThreatSummary` |
   | **Job description** | `Aggregates Palo Alto firewall threat and traffic data from the data lake into source-destination pair summaries for detection and hunting.` |
   | **Destination workspace** | Select your Lab workspace |
   | **Destination table** | Select **Create a new table** and enter `PaloAlto_ThreatSummary` (the suffix `_KQL_CL` is appended automatically) |

3. Select **Next**

<p align="center">
<img src="../Images/OnboardingImage9.png?raw=true">
</p>


---

### Step 3 — Write the Aggregation Query

In the **Prepare the query** panel, paste the following KQL query:

```kusto
let delay = 15m;
let endTime = now() - delay;
let startTime = endTime - 4h;
CommonSecurityLog
| where TimeGenerated between (startTime .. endTime)
| where DeviceVendor == "Palo Alto Networks"
| where DeviceEventClassID in ("TRAFFIC", "THREAT")
| extend ThreatCategory = iff(DeviceEventClassID == "THREAT", Activity, "")
| summarize
    TotalSessions        = count(),
    TotalBytesSent       = sum(SentBytes),
    TotalBytesReceived   = sum(ReceivedBytes),
    DistinctPorts        = dcount(DestinationPort),
    ThreatCategories     = make_set_if(ThreatCategory, isnotempty(ThreatCategory)),
    TopActions           = make_set(DeviceAction, 5),
    FirstSeen            = min(TimeGenerated),
    LastSeen             = max(TimeGenerated),
    SourceUserName       = take_any(SourceUserName),
    SourceHostName       = take_any(SourceHostName)
    by SourceIP, DestinationIP
| extend TimeGenerated = FirstSeen
| project
    TimeGenerated,
    SourceIP,
    DestinationIP,
    TotalSessions,
    TotalBytesSent,
    TotalBytesReceived,
    DistinctPorts,
    ThreatCategories,
    TopActions,
    FirstSeen,
    LastSeen,
    SourceUserName,
    SourceHostName
```

**Understanding the query:**

| Clause | Purpose |
|---|---|
| `let delay = 15m` | Accounts for data lake ingestion latency |
| `where DeviceVendor == "Palo Alto Networks"` | Filters to Palo Alto firewall logs only |
| `where DeviceEventClassID in ("TRAFFIC", "THREAT")` | Includes both traffic and threat event types |
| `extend ThreatCategory = iff(...)` | Extracts the threat type (e.g., `spyware`) from the `Activity` column on THREAT rows |
| `summarize ... by SourceIP, DestinationIP` | Aggregates raw events into source-destination pair summaries |
| `make_set_if(ThreatCategory, ...)` | Collects distinct threat categories per source-destination pair (only from THREAT events) |
| `dcount(DestinationPort)` | Counts unique destination ports (useful for scan detection) |
| `extend TimeGenerated = FirstSeen` | Sets `TimeGenerated` so the promoted data has a valid timestamp |

4. Select the **workspace(s)** to run the query against from the **Selected workspaces** dropdown — choose the workspace that contains your `CommonSecurityLog` data.

5. Select **Next**

<p align="center">
<img src="../Images/OnboardingImage12.png?raw=true">
</p>


> **Important:** The `TimeGenerated` column is overwritten by the ingestion process if it is older than two days. If you need to preserve the original event time, write it to a separate column (which we do here with `FirstSeen` and `LastSeen`).

---

### Step 4 — Schedule the Job

On the **Schedule the query job** page:

1. Select **Scheduled job**
2. Configure the schedule:

   | Setting | Value |
   |---|---|
   | **Repeat frequency** | Hourly |
   | **Repeat every** | 4 hours |
   | **From** | Set to a date/time at least 30 minutes from now |
   | **To** | Select **Set job to run indefinitely** (or pick an end date for testing) |

3. Select **Next**

<p align="center">
<img src="../Images/OnboardingImage13.png?raw=true">
</p>


> **Why 4 hours?** The query uses a 4-hour lookback window (`startTime = endTime - 4h`). Running the job every 4 hours ensures continuous coverage without gaps. The 15-minute delay parameter prevents querying data that hasn't been fully ingested yet.

---

### Step 5 — Review and Submit

1. Review the job summary:
   - **Job name:** `PaloAlto_ThreatSummary`
   - **Destination table:** `PaloAlto_ThreatSummary_KQL_CL`
   - **Schedule:** Every 4 hours
   - **Query:** Aggregation of Palo Alto firewall data

2. Select **Submit** to create the job

3. The job is scheduled. You can view its status by selecting the link on the confirmation page, or by navigating back to **Microsoft Sentinel** → **Data lake exploration** → **Jobs**

<p align="center">
<img src="../Images/OnboardingImage14.png?raw=true">
</p>

---

### Step 6 — Verify the Output Table

After the job runs (wait for the first scheduled execution or create a one-time job to test immediately):

1. Navigate to **Microsoft Defender portal** → **Hunting** → **Advanced Hunting**
2. Run the following query to verify data was promoted:

```kusto
PaloAlto_ThreatSummary_KQL_CL
| take 10
| project
    TimeGenerated,
    SourceIP,
    DestinationIP,
    TotalSessions,
    TotalBytesSent,
    DistinctPorts,
    ThreatCategories,
    FirstSeen,
    LastSeen
```

3. Confirm that rows appear with aggregated traffic summaries

> **Tip:** If no data appears, wait for the next scheduled run or check the job status on the **Jobs** page. Look for errors related to schema mismatches or permission issues.

---

### Step 7 — Connect to Detection Rule S8

Now that your KQL job is populating the `PaloAlto_ThreatSummary_KQL_CL` table, the existing detection rule `[S8] [Palo Alto] Data Lake Promoted Threat` will start generating alerts when it finds suspicious aggregated traffic.

Review the S8 detection rule query to understand how it consumes the promoted data:

```kusto
PaloAlto_ThreatSummary_KQL_CL
| where TimeGenerated > ago(4h)
| where TotalSessions > 5
    or set_has_element(todynamic(ThreatCategories), "spyware")
    or set_has_element(todynamic(ThreatCategories), "wildfire-virus")
    or tolong(TotalBytesSent) > 50000000
```

Questions to consider:
- What would happen if the KQL job fails — would S8 still detect threats?
- How would you modify the aggregation query to include additional context (e.g., `ApplicationProtocol`)?
- What is the maximum detection delay for this pattern (latency of ingestion + job schedule + detection rule schedule)?

---

## Using Job Templates

Instead of writing queries from scratch, you can use **built-in job templates** provided by Microsoft:

1. From the **Jobs** page or **KQL query editor**, select **Create job** → **Create from template**
2. Browse the available templates:

   | Template | Category |
   |---|---|
   | Palo Alto potential network beaconing | Hunting |
   | Daily network traffic trend per destination IP | Baseline |
   | Daily network traffic trend per source IP with data transfer stats | Hunting |
   | Network log IOC matching | Hunting |
   | Anomalous sign-in locations increase | Hunting |
   | Windows suspicious login outside normal hours | Anomaly detection |

3. Select a template, review the description and query, then select **Create job from template**
4. The job creation wizard opens with pre-populated settings — just select your destination workspace and adjust the schedule

<p align="center">
<img src="../Images/OnboardingImage15.png?raw=true">
</p>


---

## Considerations and Limitations

| Constraint | Limit |
|---|---|
| Concurrent job execution per tenant | 3 |
| Job query execution timeout | 1 hour |
| Enabled jobs per tenant | 100 |
| Output tables per job | 1 |
| Query scope | Multiple workspaces |
| Query time range | Up to 12 years |
| Job start time | At least 30 minutes after creation |

**KQL restrictions** in data lake jobs:
- `adx()`, `arg()`, `externaldata()`, and `ingestion_time()` are **not supported**
- User-defined functions are **not supported**
- `TimeGenerated` is overwritten if older than 2 days — use a separate column to preserve original timestamps

**Reserved columns** — the following columns are overwritten during ingestion and should not be used in your output schema:
`TenantId`, `_TimeReceived`, `Type`, `SourceSystem`, `_ResourceId`, `_SubscriptionId`, `_ItemId`, `_BilledSize`, `_IsBillable`, `_WorkspaceId`

---

## Key Takeaways

- KQL jobs **promote data** from the low-cost data lake tier to the analytics tier for hunting and detection
- Always include a **delay parameter** (`now() - 15m`) to account for data lake ingestion latency
- Schedule frequency should **match the query lookback window** to ensure continuous coverage
- Promoted data can be consumed by **custom detection rules** (like S8) and **Advanced Hunting** queries
- Use **job templates** for common scenarios to accelerate setup
- Only promote the data you need — use `project` and `where` filters to minimize analytics tier costs

## Microsoft Learn References

- [Create KQL jobs in the Microsoft Sentinel data lake](https://learn.microsoft.com/en-us/azure/sentinel/datalake/kql-jobs)
- [Manage jobs in the Microsoft Sentinel data lake](https://learn.microsoft.com/en-us/azure/sentinel/datalake/kql-manage-jobs)
- [KQL queries in the Microsoft Sentinel data lake](https://learn.microsoft.com/en-us/azure/sentinel/datalake/kql-queries)
- [Microsoft Sentinel data lake overview](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-lake-overview)
- [Handle ingestion delay in scheduled analytics rules](https://learn.microsoft.com/en-us/azure/sentinel/ingestion-delay)
