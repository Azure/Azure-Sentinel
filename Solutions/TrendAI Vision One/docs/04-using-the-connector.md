# Using the connector day to day

You've deployed and connected. Now what? This guide covers everything you'll actually *do* with the connector: confirming data arrives, querying it, turning on alerts, reading dashboards, filtering noise, and the region/secret housekeeping.

It assumes no KQL experience. If you've written SQL, you'll feel at home; if you haven't, you'll still be fine — every query here is copy-paste ready.

---

## A 60-second KQL primer

KQL (Kusto Query Language) is how you ask Sentinel questions. You read it **top to bottom**, and each `|` ("pipe") passes results to the next step, like an assembly line.

```kql
TrendMicro_XDR_WORKBENCH_CL     // 1. Start with this table
| where TimeGenerated > ago(1h) // 2. Keep only the last hour
| project TimeGenerated, severity_s, workbenchName_s  // 3. Show only these columns
| take 10                       // 4. Just the first 10 rows
```

Where do you type this? **Sentinel → Logs** (or **Log Analytics → Logs**). Paste, hit **Run**.

> 💡 **Why do columns end in `_s`, `_d`, `_t`, `_g`?** Log Analytics tags each column with its type: `_s` = string (text), `_d` = double (number), `_t` = datetime, `_g` = GUID, `_b` = boolean. So `severity_s` is the text severity, `priorityScore_d` is a number.

---

## Step 1 — Confirm data is arriving

Right after connecting, run the matching query. Give it **5–10 minutes** after you click Connect.

**Workbench:**
```kql
TrendMicro_XDR_WORKBENCH_CL
| where TimeGenerated > ago(1h)
| project TimeGenerated, workbenchId_s, severity_s, workbenchName_s
| take 10
```

**OAT:**
```kql
TrendMicro_XDR_OAT_CL
| where TimeGenerated > ago(1h)
| project TimeGenerated, entityType_s, detail_endpointHostName_s, detail_filterRiskLevel_s
| take 10
```

- **Rows come back?** 🎉 You're done — the connector works. Skip ahead to querying.
- **Empty, even after 10 minutes?** → [Troubleshooting](06-troubleshooting.md). The usual culprits are the wrong region or the missing `Bearer ` prefix.

You can also watch connector health visually: **Sentinel → Data connectors →** your connector **→** the *"Data received"* graph and *"Last data received"* timestamp.

---

## Step 2 — Query the data

### Workbench: high-severity alerts

```kql
TrendMicro_XDR_WORKBENCH_CL
| where severity_s in ("high", "critical")
| project TimeGenerated, workbenchId_s, workbenchName_s, severity_s, priorityScore_d
| sort by TimeGenerated desc
```

### OAT: high-risk detections

```kql
TrendMicro_XDR_OAT_CL
| where detail_filterRiskLevel_s == "high"
| project TimeGenerated, detail_endpointHostName_s, detail_processCmd_s, detail_processFileHashSha256_s
| sort by TimeGenerated desc
```

### OAT: process-tree style view

```kql
TrendMicro_XDR_OAT_CL
| where isnotempty(detail_processName_s)
| project TimeGenerated,
    Endpoint   = detail_endpointHostName_s,
    Process    = detail_processName_s,
    Parent     = detail_parentName_s,
    CommandLine= detail_processCmd_s
```

The [main README](../README.md#-data-schemas) lists the column categories for both tables (Workbench has 56 columns; OAT has 139).

---

## Step 3 — The parser functions

Both connectors install a **parser function** — a saved query you call like a table. Both are **universal**: they auto-detect the data shape and work on rows from **both** the old Function App connector and this new one, so after a migration your historical rows still parse correctly. (More in the [migration guide](05-migration.md).)

### Workbench: `TrendMicroWorkbench_Complete()`

Workbench alerts arrive with some data tucked inside nested fields (lists of indicators, entities, matched rules). Picking those apart by hand is tedious, so the parser returns the same data with **IOCs already extracted into flat columns** (`FileName_s`, `FileHashValue_s`, `IPAddress`, `DomainName_s`, `URL_s`, …):

```kql
TrendMicroWorkbench_Complete()
| where severity_s in ("high", "critical")
| where isnotempty(FileHashValue_s)
| project TimeGenerated, workbenchName_s, FileName_s, FileHashValue_s, HostHostName_s
```

> 🧠 **Why it exists:** it saves you from writing `mv-expand` / `parse_json` gymnastics every time you want a file hash. Use the raw table for simple fields; use the parser when you want IOCs.

### OAT: `TrendMicroOAT_Complete()`

OAT fields are already flat (`detail_*`), so you *can* query the raw table directly. But the parser still earns its keep: it returns **one stable, fully-typed schema** no matter how the row was ingested — old Function App data, current connector data, or older variants where the payload was kept as a whole `detail` object or `RawData` string. For every field it prefers the typed flat column and falls back to re-deriving it from the raw payload, so a query you write today keeps working across all of that history.

```kql
TrendMicroOAT_Complete()
| where detail_filterRiskLevel_s == "high"
| project TimeGenerated, detail_endpointHostName_s, detail_processCmd_s, detail_processFileHashSha256_s
```

It also adds two convenience columns pulled from the detection's filters: `mitreTacticIds_s` and `mitreTechniqueIds_s`.

> 🧠 **When to use which:** for simple, recent queries the raw `TrendMicro_XDR_OAT_CL` table is fine. Reach for `TrendMicroOAT_Complete()` when you want guaranteed column/type stability across mixed old + new data (especially right after a migration).

---

## Step 4 — Turn on the analytic rule (Workbench)

An **analytic rule** is a saved query Sentinel runs on a schedule; when it finds something, it **creates an incident** in your queue. The Workbench deployment ships one, **turned off** so it can't surprise you.

To enable it:

1. **Sentinel → Analytics**.
2. Search **"Trend Vision One"**.
3. Open **"Trend Vision One - Create Incident for Workbench Alerts"**.
4. **Edit → Enable → Save**.

What it does once on:

- Runs every **5 minutes**.
- Creates an incident per Workbench alert, mapping entities Sentinel understands — **Account, File, Process, Registry Key, Registry Value**.
- Groups alerts that share the same **WorkbenchID** so one logical incident isn't split into many.
- Maps Trend severity onto Sentinel severity and carries useful custom details (Workbench link, priority score, customer ID).

> ⚠️ **Turn it on deliberately.** Once enabled it starts generating incidents immediately. Make sure your team is ready to triage them — and if you also run the old connector's rule, see the [migration guide](05-migration.md#avoid-double-incidents) to avoid duplicate incidents.

### OAT alerting

OAT does not ship a prebuilt rule. To alert on OAT, create a scheduled analytic rule (**Analytics → Create → Scheduled query rule**) using an OAT query like the high-risk one above as the rule logic.

---

## Step 5 — The dashboard / workbook (Workbench)

A **workbook** is an interactive dashboard. Workbench installs *"TrendVisionOneWorkbenchOverview"*:

1. **Sentinel → Workbooks → My workbooks**.
2. Open **"TrendVisionOneWorkbenchOverview"**.

It shows alert trends (7- and 30-day), severity breakdown, detection-model usage, and top affected hosts. OAT does not ship a workbook; you can build one from the OAT queries above.

---

## Filtering what gets ingested

Two knobs let you ingest *less*, which lowers noise and storage cost. Both are set **at deploy time** (Portal form or CLI parameter).

### TMV1-Filter (`workbenchFilter` / `oatFilter`)

A filter expression sent to the Trend API so it only returns matching items. Examples:

| Connector | Example filter | Effect |
|-----------|----------------|--------|
| Workbench | `(severity ge 'high')` | Only high and critical alerts |
| OAT | `(riskLevel eq 'high')` | Only high-risk detections |

Leave it empty to ingest everything. To change it later, redeploy with the new value (it's a deploy-time parameter).

### Exclude third-party OAT (`excludeThirdPartyOat`, default `true`)

OAT can include detections forwarded from **non-Trend, third-party linked sources**. By default these are excluded to keep the feed focused on Trend's own detections. Set it to `false` only if you specifically want third-party detections too.

> 💰 **Why filtering matters:** Sentinel bills by **data ingested and stored**. OAT especially is high-volume. Filtering at the source is the cheapest, simplest way to control cost — far better than ingesting everything and deleting later.

---

## Regions and API endpoints

Your Trend Vision One tenant lives in one region, and the connector must call that region's API. You pick this as **Trend Vision One Region** during deployment.

| Region | Value | API endpoint |
|--------|-------|--------------|
| United States | `US` | `api.xdr.trendmicro.com` |
| United Kingdom / EU | `UK` | `api.uk.xdr.trendmicro.com` |
| Singapore / APAC | `SG` | `api.sg.xdr.trendmicro.com` |
| Canada | `CA` | `api.ca.xdr.trendmicro.com` |
| Japan | `JP` | `api.jp.xdr.trendmicro.com` |

> ❗ **Wrong region = no data and no obvious error.** The token authenticates per-region. If you picked the wrong one, the connector can't see your findings. Not sure which region you're in? Check the URL of your Trend Vision One Console, or ask your Trend admin.

---

## Rotating or replacing the API token

Tokens expire or get rotated for hygiene. When that happens, data quietly stops. To update it:

1. Create a fresh token in Trend Vision One (same **SIEM** role).
2. **Sentinel → Data connectors →** your connector **→ Open connector page**.
3. Paste the new token **with** the `Bearer ` prefix.
4. Click **Disconnect**, then **Connect** again with the new token.

Set yourself a calendar reminder before the token's expiry so the feed never goes dark.

---

## Daily-driver checklist

- **Is data current?** Check *"Last data received"* on the connector page, or run the [Step 1](#step-1-confirm-data-is-arriving) query.
- **Too noisy / too expensive?** Add or tighten a [filter](#filtering-what-gets-ingested).
- **Not enough alerts becoming incidents?** Make sure the [analytic rule is enabled](#step-4-turn-on-the-analytic-rule-workbench).
- **Feed went dark?** Token probably expired → [rotate it](#rotating-or-replacing-the-api-token), or check [troubleshooting](06-troubleshooting.md).

Next: [migrating from the old connector →](05-migration.md)
