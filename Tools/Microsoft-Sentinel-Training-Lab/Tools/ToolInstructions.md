# Ingest Local CSVs into Microsoft Sentinel

Ingest your own CSV log data into a Log Analytics workspace using the same pipeline as the Sentinel Training Lab.

## Prerequisites

- **PowerShell 7+** or Windows PowerShell 5.1
- **Az PowerShell module** (`Install-Module Az -Scope CurrentUser`)
- **Azure CLI** (`az`) installed and authenticated
- Permissions to create **Data Collection Endpoints/Rules** and **ingest data** in the target workspace

## Quick Start

### 1. Download the script

Download [Ingest-LocalCSV.ps1](Ingest-LocalCSV.ps1) into a working folder.

### 2. Create CSV folders

In the **same folder** as the script, create one or both of these folders:

```
MyFolder/
├── Ingest-LocalCSV.ps1
├── Custom/          ← custom log tables (e.g. MyAppLogs_CL.csv)
└── BuildIn/         ← built-in tables (e.g. SecurityEvents.csv)
```

### 3. Add your CSV files

- **Custom tables** (`Custom/` folder): Name the CSV after the table you want to create (e.g., `MyAppLogs_CL.csv` → creates table `MyAppLogs_CL`). The first row must be column headers.
- **Built-in tables** (`BuildIn/` folder): Name the CSV after the built-in table (e.g., `SecurityEvents.csv`, `CommonSecurityLog.csv`). Columns must match the built-in table schema.

> **Not sure how to create realistic CSV data?** See [Generating Accurate CSV Data](#generating-accurate-csv-data) below.

### 4. Run the script

```powershell
# Ingest both custom and built-in CSVs
.\Ingest-LocalCSV.ps1 -ResourceGroupName "rg-sentinel" -WorkspaceName "law-sentinel"

# Ingest only custom tables
.\Ingest-LocalCSV.ps1 -ResourceGroupName "rg-sentinel" -WorkspaceName "law-sentinel" -SkipBuiltIn

# Ingest only built-in tables
.\Ingest-LocalCSV.ps1 -ResourceGroupName "rg-sentinel" -WorkspaceName "law-sentinel" -SkipCustom

# Specify a subscription explicitly
.\Ingest-LocalCSV.ps1 -SubscriptionId "xxxx-xxxx" -ResourceGroupName "rg-sentinel" -WorkspaceName "law-sentinel"
```

## What happens behind the scenes

1. The script discovers all `.csv` files in the `Custom/` and `BuildIn/` folders
2. Downloads `IngestCSV.ps1` (the shared ingestion engine) from the official repo
3. For **custom tables**: creates a Data Collection Endpoint + Data Collection Rule matching each CSV's schema, then ingests the data via the Logs Ingestion API
4. For **built-in tables**: creates a DCR per table and ingests using the standard schema

## Parameters

| Parameter | Required | Description |
|---|---|---|
| `SubscriptionId` | No | Azure subscription ID. Uses current context if omitted. |
| `ResourceGroupName` | Yes | Resource group with the Log Analytics workspace. |
| `WorkspaceName` | Yes | Log Analytics workspace name. |
| `IngestScriptUrl` | No | Override URL for IngestCSV.ps1 (defaults to official repo). |
| `SkipCustom` | No | Skip custom table ingestion. |
| `SkipBuiltIn` | No | Skip built-in table ingestion. |

## CSV Format Tips

- First row = column headers
- Use comma-separated values
- For custom tables, include a `TimeGenerated` column (ISO 8601 format) — if missing, the ingestion engine adds the current timestamp
- Table name is derived from the CSV filename (minus `.csv`)
- Custom table names should end with `_CL` (e.g., `MyLogs_CL.csv`)

## Folder Structure After Ingestion

```
MyFolder/
├── Ingest-LocalCSV.ps1
├── IngestCSV.ps1        ← auto-downloaded
├── Custom/
│   └── MyAppLogs_CL.csv
├── BuildIn/
│   └── SecurityEvents.csv
└── DCRTemplates/        ← auto-generated ARM templates
    └── ...
```

## Generating Accurate CSV Data

If you don't have real log data available, you can generate realistic CSV files that match the exact schema of Log Analytics tables using the Azure Monitor documentation and an LLM (such as GitHub Copilot, ChatGPT, etc.).

### Step 1: Find the table schema

Navigate to the [Azure Monitor Logs table reference](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/tables-category) and find the table you want to populate. For example:

- [SecurityEvent](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/securityevent)
- [CommonSecurityLog](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/commonsecuritylog)
- [AWSCloudTrail](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/awscloudtrail)
- [SigninLogs](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs)

### Step 2: Copy the column definitions

On the table's documentation page, you'll see a **Columns** section listing every column name, type, and description. Copy the full column table (or the page URL).

### Step 3: Ask an LLM to generate sample data

Paste the schema into GitHub Copilot, ChatGPT, or any LLM and use a prompt like:

> *"Using the schema below for the SecurityEvent table, generate a CSV file with 50 rows of realistic sample data. Include a variety of EventIDs (4624, 4625, 4648, 4672, 1102, 4657). Use realistic timestamps from the last 7 days, realistic computer names, account names, and IP addresses. The first row should be column headers."*

### Step 4: Refine the data for your scenario

To make the data useful for detection testing, consider asking the LLM to:

- **Include specific attack patterns** — e.g., brute-force login failures followed by a success, privilege escalation events, or suspicious process executions
- **Use consistent entity names** — reuse the same usernames, IPs, and hostnames across rows to create correlatable incidents
- **Embed IOCs** — include known-bad IPs, domains, or file hashes from your watchlists so your analytic rules will trigger
- **Vary timestamps realistically** — cluster events within time windows that match your analytic rule query frequency

### Step 5: Validate and save

1. Review the generated CSV — make sure headers match the schema exactly (column names are case-sensitive for built-in tables)
2. Ensure a `TimeGenerated` column exists with ISO 8601 timestamps (e.g., `2026-03-15T14:30:00Z`)
3. Save the file with a `.csv` extension matching the table name (e.g., `SecurityEvent.csv`)
4. Place it in the `Custom/` or `BuildIn/` folder next to the script

### Step 6: Generate logs that trigger analytic rules

You can take this a step further by generating CSV data that is specifically designed to trigger your analytic rules. Copy the KQL query from any analytic rule and paste it into the LLM along with the table schema:

> *"Here is a KQL analytic rule that detects brute-force login attempts:*
>
> *`SecurityEvent | where EventID == 4625 | summarize FailedAttempts = count() by TargetAccount, IpAddress, bin(TimeGenerated, 1h) | where FailedAttempts > 10`*
>
> *Generate 30 rows of SecurityEvent CSV data that will trigger this rule. Use the same TargetAccount and IpAddress for at least 15 failed login attempts (EventID 4625) within a 1-hour window, followed by a successful login (EventID 4624) from the same IP."*

The LLM will produce CSV rows that, once ingested, will cause the analytic rule to fire — giving you a realistic incident to investigate without needing a real attack.

### Tips

- **Start small** — generate 10–50 rows first, verify ingestion works, then scale up
- **Built-in tables are strict** — column names and types must match the official schema exactly. If ingestion fails, compare your CSV headers against the documentation
- **Custom tables are flexible** — you define the schema. Name your CSV with a `_CL` suffix (e.g., `MyThreatIntel_CL.csv`) and the ingestion engine will create the table automatically
- **Multiple tables at once** — you can place as many CSV files as you want in each folder. The script discovers and ingests all of them
