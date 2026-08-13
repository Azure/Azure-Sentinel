# Managing Fivetran log volume and ingestion cost

Optional guidance for operators whose Fivetran External Logs feed is larger than
they want to pay for on the Analytics table plan. Nothing here is required. The
default deployment described in `README.md` is a single `Fivetran_CL` table on the
Analytics plan, which is the simplest and most capable option.

## Why the feed is large

Fivetran's External Log Service emits one row per connector sync event. The great
majority of those rows are routine `INFO` progress messages. They have real
investigative value after an incident, but they do not drive any detection in this
solution. The two analytics rules and the hunting query key off `SEVERE`,
`WARNING` and authentication failure text, not off `INFO`.

That creates the classic mismatch: the highest volume data has the lowest
detection value, and on the Analytics plan every row costs the same per GB.

## Establish your own baseline first

Do not act on assumptions about the split. The shipped **Fivetran workbook** has
an "Ingestion volume and cost" section that answers this directly, including a
"Split-plan opportunity" panel showing how much of your billed volume could move
to the Auxiliary tier. Or run it yourself:

```kusto
Fivetran_CL
| where TimeGenerated > ago(30d)
| summarize GB = round(sum(_BilledSize) / 1024.0 / 1024.0 / 1024.0, 2), Events = count() by Level
| extend PercentOfVolume = round(100.0 * GB / toscalar(
    Fivetran_CL
    | where TimeGenerated > ago(30d)
    | summarize sum(_BilledSize) / 1024.0 / 1024.0 / 1024.0), 1)
| sort by GB desc
```

If `INFO` is not a large share of your billed volume, stop here. The split below
adds operational complexity and is only worth it when the volume is genuinely
concentrated in the low value tier.

## Option 1, drop what you will never read

The cheapest data is the data you never ingest. Data removed by a DCR
transformation is not written to the destination table, and Log Analytics billing
is based on the data sent to the workspace.

Add a `where` clause to the existing `transformKql` in `Fivetran_DCR.json`, for
example to discard successful routine syncs while keeping everything else:

```kusto
source
| where not(Level == 'INFO' and Message has 'sync completed successfully')
| extend TimeGenerated = CreatedAt
```

Be conservative. Filtering is irreversible for the dropped rows, and over-eager
filters are a real detection-evasion risk. Prefer Option 2 if you are unsure.

Reference: https://learn.microsoft.com/en-us/azure/azure-monitor/data-collection/data-collection-transformations-samples

Note: Microsoft's documentation states that ingestion is billed on data sent to
the workspace and shows `where` filtering as a cost-reduction technique, but does
not contain an explicit sentence confirming that filtered-out rows incur no
charge. Treat the saving as expected rather than contractually documented, and
verify against your own bill.

## Option 2, split by severity across two table plans

Keep everything, but stop paying the Analytics rate for the noisy tier.

| Data | Plan | Table |
| --- | --- | --- |
| `WARNING` and `SEVERE` | Analytics | `Fivetran_CL` |
| Everything else | Auxiliary | `FivetranVerbose_CL` |

Deploy `FivetranVerbose_Table.json`, then deploy
`Fivetran_DCR_SplitPlan.json` in place of `Fivetran_DCR.json`. Fivetran's
configuration does not change; it still posts to one stream and one DCR.

What you gain: the Auxiliary plan has a minimal ingestion charge and remains
interactively queryable for its full total retention period, rather than the fixed
30 days of the Basic plan.

What you give up, and these are not small:

- **Auxiliary tables do not support alerts at all.** Basic supports only Simple
  Log Alerts. Full scheduled analytics rules require the Analytics plan.
- Queries against Basic and Auxiliary tables are **limited to a single table**.
  `join`, `find`, `search` and `externaldata` are unsupported. `union` and
  `lookup` are permitted only against a small number of Analytics tables.
  `summarize` and scalar functions do work.
- Queries are **billed per GB scanned** on Basic and Auxiliary, where Analytics
  interactive queries are not. A careless full-retention scan can cost more than
  the ingestion you saved.
- Auxiliary requires `TimeGenerated` in ISO 8601 with six decimal places.
- Table plan changes are limited to **one switch per table per week**.

References:
https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-table-plans
https://learn.microsoft.com/en-us/azure/azure-monitor/logs/basic-logs-query
https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-platform-logs

### Required change if you adopt Option 2

The shipped `FivetranIngestionGap` analytics rule already handles the split. Its
query is tier-agnostic:

```kusto
union isfuzzy=true
    (Fivetran_CL | ... | summarize LastLogReceived = max(TimeGenerated)),
    (FivetranVerboseSummary_CL | ... | summarize LastLogReceived = max(TimeGenerated))
```

`isfuzzy=true` means the rule works unchanged in a default single-table
deployment, where `FivetranVerboseSummary_CL` does not exist, and also in a
split deployment. You do not need to edit the rule.

What you **do** need to create is the summary table it looks for. Without it, a
healthy account emitting only `INFO` writes nothing to `Fivetran_CL` and the gap
rule will fire a false positive after two hours.

Create a summary rule that aggregates the Auxiliary tier into an Analytics table
named `FivetranVerboseSummary_CL`:

```kusto
FivetranVerbose_CL
| summarize EventCount = count(), FirstEvent = min(TimeGenerated), LastEvent = max(TimeGenerated), BilledBytes = sum(_BilledSize) by Level
```

Run it at a 60 minute bin size with an Analytics plan destination table. Summary
rules read from Analytics, Basic or Auxiliary sources and always write to an
Analytics destination, which is what makes alerting possible again. With an
Auxiliary source you pay the query scan cost plus Analytics ingestion for the
small aggregated result.

The summary rule is not shipped as a deployable ARM resource in this solution,
because the exact ARM resource type and apiVersion for summary rules could not be
confirmed from Microsoft's published documentation at time of writing. Create it
in the portal or via the documented API.

Reference: https://learn.microsoft.com/en-us/azure/azure-monitor/logs/summary-rules

## Option 3, shorten retention rather than reduce ingestion

Ingestion is usually the dominant cost, but retention is not free. The Analytics
plan includes 31 days in the ingestion price; this solution's table ships with
`totalRetentionInDays` of 365. If you do not have a compliance requirement for a
year of Fivetran connector chatter, lowering it is a one-line change in
`Fivetran_Table.json` with no effect on detections.

## Option 4, use the Platform Connector path instead

If the reason you want the External Logs feed is historical audit evidence rather
than real-time detection, you are paying Sentinel ingestion rates for something
the Fivetran Platform Connector delivers into your own lake. See
`Platform-Connector-Ingest/`. Per-GB Sentinel ingestion is avoided entirely for
data that stays in the lake.

## What not to do

- Do not switch `Fivetran_CL` itself to Basic or Auxiliary. The analytics rules,
  hunting query and entity mappings depend on it being an Analytics table.
- Do not filter on `Message` text patterns without reviewing them against a real
  sample. Fivetran message wording is not a documented contract and can change.
- Do not assume a saving. Measure with the baseline query above, apply one change,
  then measure again.
