# Cyble Threat Intelligence Parser

Parser for threat intelligence ingested into Microsoft Sentinel from the Cyble TAXII connector.

## What it does

Cyble's TAXII feed carries per-source ratings inside `external_references`, packed into the
`description` field as a single string:

```json
"external_references": [
  {
    "source_name": "AbuseIPDB",
    "description": "risk_score=56; confidence_rating=Medium"
  }
]
```

The Sentinel TAXII connector maps standard STIX properties to columns on `ThreatIntelIndicators`
and stores the full object in the `Data` column, but `external_references` has no column of its
own. That leaves the risk score and confidence rating locked inside a string, so they cannot be
filtered or aggregated without hand-written extraction in every query.

This parser returns `ThreatIntelIndicators` unchanged and adds the parsed values to `Data` as
top-level fields alongside `external_references`:

| Field | Example | Description |
| --- | --- | --- |
| `ext_source_name` | `abuseipdb` | Source that enriched the indicator. Comma separated when several sources are present. |
| `<source_name>.risk_score` | `abuseipdb.risk_score` = `56` | Risk score reported by that source. |
| `<source_name>.confidence_rating` | `abuseipdb.confidence_rating` = `Medium` | Confidence rating reported by that source. |

Source names are lowercased so the generated key names stay stable across the casing the feed
uses (`AbuseIPDB`, `censys`, `Shodan`). Indicators enriched by more than one source get one key
pair per source, so the values never overwrite one another.

## Prerequisites

- A Microsoft Sentinel workspace with the Cyble TAXII data connector configured and ingesting
  into the `ThreatIntelIndicators` table.
- Permission to save functions in the workspace (Log Analytics Contributor or equivalent).

## Installation

1. Open [`ThreatIntelParser.yaml`](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/Cyble/ThreatIntelParser.yaml)
   from the Azure-Sentinel repository and copy the KQL under the `FunctionQuery` block.
2. In the Azure portal, go to your Microsoft Sentinel workspace and open **Logs**.
3. Paste the parser into a new query.
4. Set `SourceSystemName` to the `SourceSystem` value of your TAXII connector. Leaving it as an
   empty string parses indicators from every source system.

   ```kql
   let SourceSystemName = "CybleGTI";
   ```

   To find the value used in your workspace:

   ```kql
   ThreatIntelIndicators
   | distinct SourceSystem
   ```

5. Select **Save** > **Save as function**.
6. Enter the following, then save:

   - **Function name:** `CybleThreatIntel`
   - **Legacy category:** `CybleThreatIntel`

The parser is now available as a function and can be called by name from any query in the
workspace.

## Usage

Call it exactly as you would the underlying table:

```kql
CybleThreatIntel
```

Only add a `where` clause if you deliberately want to narrow the result. For example, to look at
scored indicators alone:

```kql
CybleThreatIntel
| where toint(Data.['abuseipdb.risk_score']) > 0
```

## Notes

- Indicators rewritten by Sentinel's `LogARepublisher` process carry no `external_references`,
  because the republish rebuilds `Data` from the platform schema and drops properties that have
  no column. Those rows are returned unchanged rather than dropped, so the parser is a safe
  drop-in replacement for querying the table directly. Filter on
  `LastUpdateMethod == "TAXIIConnector"` if you only want records that can carry ratings.
- `Data` is returned as `dynamic` rather than the `string` it is natively, which is what makes it
  render as an expandable object in the Logs view. Append `| extend Data = tostring(Data)` if
  something downstream expects a string.
- A blank `confidence_rating` with `risk_score=0` means the source did not enrich that indicator.
  It is not a parsing failure.
