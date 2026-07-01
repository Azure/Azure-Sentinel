# Speculus Threat Intelligence Solution for Microsoft Sentinel

Ingests STIX 2.1 IP indicators from the Speculus TAXII 2.1 server into Microsoft Sentinel using the Codeless Connector Framework (CCF) — no Azure Functions or agents required.

## What this solution deploys

| Component | Name | Purpose |
|---|---|---|
| Data connector | Speculus Threat Intelligence | RestApiPoller against the Speculus TAXII 2.1 objects endpoint |
| Custom table | `Speculus_Indicators_CL` | Flattened STIX indicators with Speculus enrichment |
| Data collection rule | `dcr-speculus-indicators` | Filters the TAXII envelope to Indicator SDOs and flattens STIX + `x_speculus_*` fields |
| Analytics rules | 3 | High-risk IP match vs. `CommonSecurityLog`, high-risk IP match vs. `SigninLogs`, feed outage detection |

## How it works

The connector polls `{taxiiBaseUrl}/collections/{collectionId}/objects/` (TAXII 2.1) with `Authorization: Bearer <API key>`, using `added_after` for incremental collection and the TAXII envelope's `next` cursor / `more` flag for pagination. Each page's `objects` array contains STIX 2.1 SDOs (an Identity, then Indicators, plus Malware/Relationship objects when an indicator has named attribution). The data collection rule keeps only `type == "indicator"` objects — attribution is preserved on the indicator itself via `x_speculus_attribution` — and flattens the STIX fields and Speculus custom properties into `Speculus_Indicators_CL`.

## Prerequisites

- A Speculus API key with access to the IOC feed. Polling the TAXII objects endpoint is metered against the same quota as the Speculus REST API.
- Microsoft Sentinel workspace with permissions to deploy data connectors (Contributor on the workspace resource group).

## Configuration

1. Install the solution from Content Hub.
2. Open the **Speculus Threat Intelligence** data connector page.
3. Enter:
   - **TAXII Base URL (including API root)** — default `https://feed.speculus.co/api1`
   - **Collection ID** — default `f3a1c2d4-5b6e-4a7f-8c9d-0e1f2a3b4c5d` (the `speculus-ioc-feed` collection)
   - **API Key** — your Speculus API key
4. Click **Connect**. Indicators appear in `Speculus_Indicators_CL` within the first polling window (60 minutes).

## Notes

- Indicators are re-ingested only when their STIX `modified` timestamp changes (signal change), not on daily `last_seen` advances — so row counts reflect new/changed intelligence, not feed size.
- The table retains 30 days of indicator history; the analytics rules match against the most recent version of each indicator seen in the last 14 days.
