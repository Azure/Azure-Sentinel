# SAP Agentless Connector – Time-Slice Backfill

`Invoke-SapAgentlessBackfill.ps1` is a PowerShell REST client that loads chosen **historic time
slices** for the agentless SAP data connector (SAP Integration Suite / `SAPCC`).

Use it to:

- **Load history at first setup.** The Microsoft Sentinel connector starts collecting at
  *now* and does not load the past.
- **Fill gaps after intermittent failures**, such as RFC errors, timeouts, an expired
  credential or a paused connection.
- **Recover after log pipeline downtime** in SAP Integration Suite, SAP Cloud Connector,
  SAP ERP or the DCE/DCR.

> [!IMPORTANT]
> This tool is provided as-is, as a sample. Test it in a non-production landscape first.
> Read [Sizing and load protection](#sizing-and-load-protection) before you run any large load.

## Analyze ingestion without running a backfill

Looking for **SAP ingestion peaks, truncation or high-volume accounts**? Jump to
[SAP ingestion analysis and exclusion candidates](#sap-ingestion-analysis-and-exclusion-candidates)
for seven copyable KQL queries and guidance on reviewing potential exclusions.
This standalone section does not require running the backfill script.

## How it works

```
 Invoke-SapAgentlessBackfill.ps1                 Microsoft Sentinel
 (REST client, one slice at a time)              ┌──────────────────────────────┐
        │  GET ?startTimeUTC=..&endTimeUTC=..    │ DCE ─▶ SAPCC DCR ─▶ ABAP*    │
        │  Bearer token + RfcDestinationName     │                     tables   │
        ▼                                        └──────────────▲───────────────┘
 SAP Integration Suite                                          │ push
 /http/microsoft/sentinel/sap-log-trigger  ─────────────────────┘
        │ RFC (per destination)
        ▼
 SAP Cloud Connector ─▶ SAP ERP / S/4HANA (Audit log, change docs, users, roles)
```

The Sentinel connector (a CCF `RestApiPoller`) calls the same iFlow endpoint every polling
interval with a `startTimeUTC`/`endTimeUTC` window. The iFlow reads that window from SAP and
**pushes the records to the DCE/DCR itself**. The HTTP response only carries counts per
source. The connector ingests only the `SentinelHealth` heartbeat from that response.

The script makes the same call for windows you choose in the past. The SAP data lands in the
regular tables (`ABAPAuditLog`, `ABAPChangeDocsLog`, `ABAPUserDetails`,
`ABAPAuthorizationDetails`). No extra Sentinel configuration is needed. Calls made by the
script do **not** create `SentinelHealth` heartbeat records.

## Prerequisites

- PowerShell 7+ (recommended) or Windows PowerShell 5.1.
- The Microsoft Sentinel solution for SAP iFlow, deployed on the SAP Integration Suite tenant.
- The service key of the **Process Integration Runtime** instance that the connector uses:
  - `url` → `-CpiEndpoint`
  - `tokenurl` → `-TokenUrl`
  - `clientid` → `-ClientId`
  - `clientsecret` → `-ClientSecret`

  See [`IntegrationSuite/provision-sap-cpi-runtime.ps1`](../IntegrationSuite/README.md).
- The RFC/BTP destination name of the SAP system (`-RfcDestinationName`). This is the same
  value that is configured on the Sentinel connection.

The client secret is a `SecureString` and you are prompted for it if it is omitted. Do not
store secrets in scripts or in source control.

## Usage

### Quick start with `Trigger-Run.ps1`

`Trigger-Run.ps1` is a launcher, so you don't have to retype connection details for every run.

1. Fill in its `SETTINGS` block once: CPI endpoint, token URL, client id, destination, default
   range and tuning. Alternatively, set the `SAP_BACKFILL_CPI_ENDPOINT`,
   `SAP_BACKFILL_TOKEN_URL`, `SAP_BACKFILL_CLIENT_ID` and `SAP_BACKFILL_RFC_DESTINATION`
   environment variables. They take precedence over the `SETTINGS` block and keep tenant
   details out of the file.
2. Provide the secret through `SAP_BACKFILL_CLIENT_SECRET`, or enter it at the prompt.
3. Run it:

```powershell
.\Trigger-Run.ps1 -DryRun                                                   # preview the default range
.\Trigger-Run.ps1                                                           # run the default range
.\Trigger-Run.ps1 -StartTimeUtc '2026-10-20T00:00' -EndTimeUtc '2026-10-20T06:00'
.\Trigger-Run.ps1 -LastHours 6 -SliceMinutes 2                              # now-6h .. now
.\Trigger-Run.ps1 -GapCsvPath .\gaps.csv
```

Results are written to `runs\SapBackfill_<destination>_<timestamp>.csv`. The `runs` folder is
git-ignored. Do not commit a `Trigger-Run.ps1` that contains real tenant details.

The sections below call `Invoke-SapAgentlessBackfill.ps1` directly with all parameters.

### 1. Plan with a dry run

Always start with `-DryRun`. It only prints the slices that would be requested. It does not
authenticate or send any requests.

```powershell
.\Invoke-SapAgentlessBackfill.ps1 -StartTimeUtc '2026-10-20T00:00:00' -EndTimeUtc '2026-10-21T00:00:00' `
    -SliceMinutes 5 -DryRun
```

### 2. Load an explicit range

```powershell
$params = @{
    CpiEndpoint        = 'https://<tenant>.it-cpi023-rt.cfapps.eu20-001.hana.ondemand.com'
    TokenUrl           = 'https://<subdomain>.authentication.eu20.hana.ondemand.com/oauth/token'
    ClientId           = '<client id>'
    RfcDestinationName = '<destination name>'
}
.\Invoke-SapAgentlessBackfill.ps1 @params -StartTimeUtc '2026-10-20T00:00:00' -EndTimeUtc '2026-10-20T06:00:00' `
    -SliceMinutes 5 -PauseSeconds 10 -MaxRuntimeMinutes 120
```

### 3. Load a list of gap windows from a CSV

`gaps.csv`:

```csv
StartTimeUTC,EndTimeUTC
2026-10-18T02:10:00,2026-10-18T02:45:00
2026-10-19T13:00:00,2026-10-19T14:30:00
```

```powershell
.\Invoke-SapAgentlessBackfill.ps1 @params -GapCsvPath .\gaps.csv
```

### 4. Re-run failed slices

Each slice is appended to the results CSV (`-LogFile`, default
`SapBackfill_<timestamp>.csv`) with these columns: `Status` (`OK`/`Error`/`Timeout`),
`ElapsedTime`, the per-source counts, `MPLLogID`, `RunId` and `Error`. The results CSV can be
passed straight back as a gap CSV:

```powershell
Import-Csv .\SapBackfill_20261022_101500.csv | Where-Object Status -eq 'Error' |
    Export-Csv .\retry.csv -NoTypeInformation
.\Invoke-SapAgentlessBackfill.ps1 @params -GapCsvPath .\retry.csv
```

### 5. Resume after a timeout or after reaching max runtime

- **Timeout:** if a request reaches `-TimeoutSeconds` (default 180 s, the same as the
  connector), the script **exits with code 1**. A long-running request is a sign that the
  backend is struggling, and continuing would only add load.
- **Max runtime:** when `-MaxRuntimeMinutes` is reached, the script stops cleanly.

In both cases the script prints the parameters needed to resume, for example:

```
Resume from the interrupted slice with:
  -StartTimeUtc '2026-10-20T03:15:00' -EndTimeUtc '2026-10-20T06:00:00'
```

Before you resume after a timeout, reduce `-SliceMinutes` and/or increase `-PauseSeconds`.
Use the `MPLLogID` from the CSV to check the message in the CPI message monitor.

### Parameters

| Parameter | Default | Description |
|---|---|---|
| `-StartTimeUtc` / `-EndTimeUtc` | – | Range to load (UTC, ISO 8601; the end is exclusive). Cannot be combined with `-GapCsvPath`. |
| `-GapCsvPath` | – | CSV with `StartTimeUTC,EndTimeUTC` (or `StartTime,EndTime`). |
| `-SliceMinutes` | `1` | Window size per request. |
| `-PauseSeconds` | `5` | Pause between two requests. |
| `-TimeoutSeconds` | `180` | Timeout per request. The script exits when it is reached. |
| `-MaxRuntimeMinutes` | `0` (unlimited) | Stops cleanly and prints a resume hint. |
| `-SafetyLagMinutes` | `5` | Windows newer than now minus this lag are skipped or clamped. The live connector covers them. |
| `-LargeRunSliceThreshold` | `1440` | The script refuses runs with more slices than this unless `-Force` is set. |
| `-TimeFormat` | `yyyy-MM-ddTHH:mm:ss` | Format of the time query parameters. |
| `-ApiPath` | `/http/microsoft/sentinel/sap-log-trigger` | iFlow path. |
| `-LogFile` | `.\SapBackfill_<timestamp>.csv` | Results CSV. |
| `-DryRun` | – | Lists the slices only. |

## Finding gaps

Use time-binned counts to spot empty windows, then export the result as the gap CSV. The query
uses aligned buckets and only includes completed windows, so it avoids treating a partially
elapsed current bucket as a gap:

```kusto
let lookback = 7d;
let bin_size = 15m;
let end_utc = bin(now(), bin_size);
let start_utc = bin(end_utc - lookback, bin_size);
ABAPAuditLog
| where TimeGenerated >= start_utc and TimeGenerated < end_utc
| make-series Events = count() default = 0 on TimeGenerated
    from start_utc to end_utc step bin_size
| mv-expand TimeGenerated to typeof(datetime), Events to typeof(long)
| where Events == 0
| project StartTimeUTC = TimeGenerated, EndTimeUTC = TimeGenerated + bin_size
```

Some systems have quiet periods (nights, weekends) that are legitimately empty. Cross-check
with the connector heartbeat in `SentinelHealth` and the CPI message monitor before you
reload a window.

## Sizing and load protection

> [!WARNING]
> **A massive initial or catch-up load that runs alongside existing live connections must be
> sized carefully.** Every slice triggers a full iFlow run with RFC calls into SAP. If
> uncontrolled, a backfill can saturate:
>
> - **SAP Integration Suite (CPI):** worker node CPU and memory, message processing log (MPL)
>   volume and retention, tenant quotas and the HTTP connection limit. This can delay or fail
>   the *live* connector polls that share the same tenant.
> - **SAP Cloud Connector:** concurrent connections, worker threads and bandwidth, shared with
>   every other scenario that uses this Cloud Connector.
> - **SAP ERP / S/4HANA:** dialog and RFC work processes, reads of the Security Audit Log files
>   (SM20/RSAU), scans of large change document tables (CDHDR/CDPOS), and user and role
>   lookups. This can affect business users.

Recommendations:

1. **Estimate the volume first.** Run the ABAP report from
   [`LogExtractorStatistics`](../LogExtractorStatistics/README.md) for the period you want to
   load. Large volumes (millions of audit or change-document records) need extra care.
2. **Start small and observe.** Run a short range with the defaults (1-minute slices, 5 s
   pause) and watch the `ElapsedTime` column. Increase `-SliceMinutes` only while elapsed
   times stay well below the timeout. If elapsed times grow, reduce the slice size and/or
   increase the pause.
3. **Run off-peak.** Schedule large loads outside business hours and outside SAP batch
   windows. Use `-MaxRuntimeMinutes` to stay inside an agreed maintenance window, then resume
   in the next one.
4. **One backfill per SAP system.** Never run several instances of the script against the same
   RFC destination or the same Cloud Connector at once. The script is intentionally
   sequential.
5. **Mind the live connector.** Live polls continue during the backfill. Leave enough headroom
   on CPI and SAP so that live polls do not time out. Watch the `SentinelHealth` heartbeat
   while the backfill runs.
6. **Coordinate with the SAP Basis and integration teams.** Monitor work processes (SM50/SM66),
   Cloud Connector monitoring, and the CPI message monitor (filter by the `MPLLogID` / `RunId`
   values in the results CSV).
7. **Mind the retention.** You can only backfill data that SAP still holds. The Security Audit
   Log and change documents might have been archived or deleted by SAP retention jobs.
8. **Cost.** Backfilled data is billed like any other ingestion into the Log Analytics
   workspace.

## Duplicates

The iFlow does not deduplicate across calls. Loading a window that has already been ingested
creates **duplicate records**. To avoid this:

- For an initial load, set `-EndTimeUtc` to the start of the connector's first successful poll
  (see `SentinelHealth`).
- For gaps, load only windows that were confirmed missing.
- `-SafetyLagMinutes` prevents the script from loading windows that the live connector is
  currently handling.

If duplicates were ingested, deduplicate in queries, for example with
`summarize arg_max(TimeGenerated, *) by <unique key columns>`.

## SAP ingestion analysis and exclusion candidates

These queries analyze **already ingested SAP Security Audit Log data** independently of
the backfill procedure. Use them in the Microsoft Sentinel Logs view to investigate
truncation, understand volume patterns, and identify high-volume accounts for review.
They do not change collection or configure exclusions.

All timestamps are UTC. The date-range examples use a start-inclusive, end-exclusive
interval: replace `StartUtc` and `EndUtc` with your dates. For example, October 19 through
October 25 uses `StartUtc = datetime(2026-10-19)` and `EndUtc = datetime(2026-10-26)`.
In a shared workspace, apply the same SAP system and client filters to every query,
using the identifying columns in your data.

`TimeGenerated` groups events by their recorded event time; `ingestion_time()` groups
them by approximate arrival time in the workspace. Historic loads can therefore show
an arrival peak today but an event-time peak in the past. For ingestion-time queries,
set the Logs time picker wide enough to include the underlying historic events so
an implicit `TimeGenerated` filter does not hide them. Null ingestion timestamps cannot
be assigned to an arrival-time bucket.

`_BilledSize` is the record size in bytes. The examples label binary units as GB
(bytes / 1024^3) and TB (GB / 1024), matching the calculations below. These totals and
projections are volume indicators, **not invoice estimates**: pricing, billable status,
commitment tiers, retention and other charges are not accounted for.

### Truncation events

Find truncation markers and extract the counts from their messages:

```kusto
let StartUtc = datetime(2026-10-19);
let EndUtc = datetime(2026-10-26);
ABAPAuditLog
| where TimeGenerated >= StartUtc and TimeGenerated < EndUtc
| where Instance == "TRUNCATED"
| extend TruncatedCount = tolong(extract(@"truncated:\s*(\d+)", 1, MessageText)),
         ProcessedCount = tolong(extract(@"processed\s+(\d+)", 1, MessageText))
| extend TruncationAmount = TruncatedCount - ProcessedCount
| project TimeGenerated, MessageText, TruncatedCount, ProcessedCount, TruncationAmount
| order by TimeGenerated desc
```

The extraction assumes messages contain `truncated: <number>` and `processed <number>`.
Check the actual message format and count meanings for your deployed iFlow version
before interpreting the difference as unprocessed events. Unmatched counts stay null,
not zero; a negative difference also warrants checking the format and semantics.
Ingested rows cannot establish the full volume of events that were dropped or never
collected. Correlate markers with SAP and Integration Suite diagnostics.

### Daily ingestion volume by event time

Count events and their record-size volume for each event day:

```kusto
let StartUtc = datetime(2026-10-19);
let EndUtc = datetime(2026-10-26);
ABAPAuditLog
| where TimeGenerated >= StartUtc and TimeGenerated < EndUtc
| summarize EventCount = count(), IngestedBytes = sum(_BilledSize)
    by Day = bin(TimeGenerated, 1d)
| project Day, EventCount, IngestedGB = round(IngestedBytes / 1024.0 / 1024.0 / 1024.0, 2)
| order by Day asc
```

This shows when the ingested events occurred, not when their bytes arrived. Missing
days are absent from this result; partial days should not be compared with full days.

### Average ingested GB per day

Use complete UTC days and approximate ingestion time to measure arrival volume.
Zero-volume days are included in the average:

```kusto
let StartUtc = datetime(2026-10-19);
let EndUtc = datetime(2026-10-26);
let DailyVolume =
    ABAPAuditLog
    | extend IngestedAt = ingestion_time()
    | where IngestedAt >= StartUtc and IngestedAt < EndUtc
    | summarize IngestedBytes = sum(_BilledSize) by Day = startofday(IngestedAt);
range Day from StartUtc to (EndUtc - 1d) step 1d
| join kind=leftouter DailyVolume on Day
| extend IngestedGB = coalesce(IngestedBytes, 0.0) / 1024.0 / 1024.0 / 1024.0
| summarize AvgDailyGB = avg(IngestedGB)
| project AvgDailyGB = round(AvgDailyGB, 2),
          EstimatedMonthlyGB = round(AvgDailyGB * 30, 2),
          EstimatedMonthlyTB = round(AvgDailyGB * 30 / 1024, 2)
```

Set both dates to midnight, with `EndUtc` later than `StartUtc` and no later than
the start of today. The monthly values project 30 days from the **unrounded** average;
they assume the selected period is representative. Catch-up loads, outages and missing
retained data can skew the estimate.

### Peak periods per hour

Visualize event-time activity over the last seven days to locate bursts:

```kusto
ABAPAuditLog
| where TimeGenerated > ago(7d)
| summarize EventCount = count() by Hour = bin(TimeGenerated, 1h)
| order by Hour asc
| render timechart
```

For actual arrival peaks, instead group on `bin(ingestion_time(), 1h)` and filter
on ingestion time, with the Logs time picker adjusted as described above.
Neither chart measures SAP ERP, Cloud Connector or Integration Suite resource capacity.

### Highest-volume user accounts

Identify the top five accounts by record-size volume. Ranking uses unrounded bytes:

```kusto
let StartUtc = datetime(2026-10-19);
let EndUtc = datetime(2026-10-26);
ABAPAuditLog
| where TimeGenerated >= StartUtc and TimeGenerated < EndUtc
| summarize EventCount = count(), IngestedBytes = sum(_BilledSize) by User
| top 5 by IngestedBytes desc
| project User, EventCount, IngestedGB = round(IngestedBytes / 1024.0 / 1024.0 / 1024.0, 2)
```

Investigate the event types, SAP systems and business processes behind these accounts.
High volume alone does not mean an account is safe to exclude, especially for technical,
privileged or security-sensitive users. Empty usernames may also appear and need
investigation rather than blanket exclusion.

### User and volume analysis

Estimate the share of already ingested volume attributable to an explicit account list:

```kusto
let StartUtc = datetime(2026-10-19);
let EndUtc = datetime(2026-10-26);
let CandidateUsers = dynamic(["USER"]);
ABAPAuditLog
| where TimeGenerated >= StartUtc and TimeGenerated < EndUtc
| summarize AllBytes = sum(_BilledSize),
            WithoutUsersBytes = sumif(_BilledSize, User !in (CandidateUsers))
    by Day = startofday(TimeGenerated)
| extend UserImpactBytes = AllBytes - WithoutUsersBytes
| project Day = format_datetime(Day, "yyyy-MM-dd"),
          AllEventsGB = round(AllBytes / 1024.0 / 1024.0 / 1024.0, 2),
          WithoutUsersGB = round(WithoutUsersBytes / 1024.0 / 1024.0 / 1024.0, 2),
          UserImpactGB = round(UserImpactBytes / 1024.0 / 1024.0 / 1024.0, 2),
          UserImpactPercent = iff(AllBytes > 0, round(100.0 * UserImpactBytes / AllBytes, 2), real(null))
| order by Day asc
```

Replace `USER` with the candidate accounts. Matching is exact and case-sensitive
(`in`/`!in`), not token-based `has_any`, so similar usernames are not inadvertently grouped.
Differences and percentages are computed before rounding. The result is a what-if
analysis only; it does not exclude anything or guarantee future savings.

Before configuring exclusions, review detection and investigation coverage, audit and
compliance requirements, and obtain approval from the SAP and security owners.
Confirm where filtering occurs: filtering after ingestion does not reduce source
extraction load, and a workspace-side filter does not remove upstream RFC/CPI work.
Any source-side exclusion also needs assessment of its impact on SAP audit requirements.

### Threshold ingestion chart

Compare observed event counts per minute with an editable reference line:

```kusto
let ReferenceEventsPerMinute = 150000;
ABAPAuditLog
| where TimeGenerated > ago(7d)
| summarize Count = count() by Minute = bin(TimeGenerated, 1m)
| extend Threshold = ReferenceEventsPerMinute
| order by Minute asc
| render timechart with (ycolumns = Count, Threshold)
```

**150,000 events/minute is an illustrative reference, not a documented supported limit**
for the SAP connector, Integration Suite, Cloud Connector or SAP ERP, and it does not
predict truncation. Adjust it to an agreed operational baseline. This chart uses
event time and only shows minutes with ingested events; it cannot reveal the true peak
of data lost through truncation or pipeline failures.
