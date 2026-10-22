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

Use time-binned counts to spot empty windows, then export the result as the gap CSV. Sample
query:

```kusto
let lookback = 7d;
let bin_size = 15m;
ABAPAuditLog
| where TimeGenerated > ago(lookback)
| summarize Events = count() by bin(TimeGenerated, bin_size)
| make-series Events = sum(Events) default = 0 on TimeGenerated from ago(lookback) to now() step bin_size
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
