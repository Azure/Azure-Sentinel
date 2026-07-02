# Speculus Threat Intelligence Solution for Microsoft Sentinel

Ingests STIX 2.1 IP indicators from the Speculus TAXII 2.1 server into Microsoft Sentinel using the Codeless Connector Framework (CCF) — no Azure Functions or agents required.

## What this solution deploys

| Component | Name | Purpose |
|---|---|---|
| Data connector | Speculus Threat Intelligence | RestApiPoller against the Speculus TAXII 2.1 objects endpoint |
| Custom table | `Speculus_Indicators_CL` | Flattened STIX indicators with Speculus enrichment |
| Data collection rule | `dcr-speculus-indicators` | Filters the TAXII envelope to Indicator SDOs and flattens STIX + `x_speculus_*` fields |
| Analytics rules | 3 | High-risk IP match vs. `CommonSecurityLog`, high-risk IP match vs. `SigninLogs`, feed outage detection |
| Playbook | `pb-speculus-incident-enrichment` | On-demand: looks up every IP entity on a triggered incident against the Speculus REST API and posts full enrichment as an incident comment |

## How it works

The connector polls `{taxiiBaseUrl}/collections/{collectionId}/objects/` (TAXII 2.1) with `Authorization: Bearer <API key>`, using `added_after` for incremental collection and the TAXII envelope's `next` cursor / `more` flag for pagination. Each page's `objects` array contains STIX 2.1 SDOs (an Identity, then Indicators, plus Malware/Relationship objects when an indicator has named attribution). The data collection rule keeps only `type == "indicator"` objects — attribution is preserved on the indicator itself via `x_speculus_attribution` — and flattens the STIX fields and Speculus custom properties into `Speculus_Indicators_CL`.

## Prerequisites

- A Speculus API key with access to the IOC feed.
- Microsoft Sentinel workspace with permissions to deploy data connectors (Contributor on the workspace resource group).

## Configuration

1. Install the solution from Content Hub.
2. Open the **Speculus Threat Intelligence** data connector page.
3. Enter:
   - **TAXII Base URL (including API root)** — default `https://feed.speculus.co/api1`
   - **Collection ID** — default `f3a1c2d4-5b6e-4a7f-8c9d-0e1f2a3b4c5d` (the `speculus-ioc-feed` collection)
   - **API Key** — your Speculus API key
4. Click **Connect**. Indicators appear in `Speculus_Indicators_CL` within the first polling window (60 minutes).

## Incident enrichment playbook

`pb-speculus-incident-enrichment` runs per-incident rather than on a schedule: it reads the IP entities attached to a Sentinel incident, calls `GET {baseUrl}/v1/objects/{ip}` on the Speculus REST API for each one, and posts the full enrichment (risk score, activity, attribution, labels, scanner/Tor/blacklist flags, ISP/ASN, geo, and the verdict description) as an incident comment.

1. Deploy the playbook from the solution (it deploys **disabled**).
2. Open the playbook's API connections and authorize the `azuresentinel` connection (one-time, interactive).
3. Enable the Logic App.
4. Attach it to an automation rule (recommended: trigger on incident creation), or run it manually from an incident's **Run playbook** action.

This endpoint is quota-metered against the same Speculus API key used elsewhere — unlike the TAXII data connector above, which is not. Per-incident lookup volume is low for most SOCs, so a `developer`-tier key is typically sufficient, but size your key to your incident volume if you also use the same key for other REST API calls.

## Notes

- Indicators are re-ingested only when their STIX `modified` timestamp changes (signal change), not on daily `last_seen` advances — so row counts reflect new/changed intelligence, not feed size.
- The table retains 30 days of indicator history; the analytics rules match against the most recent version of each indicator seen in the last 14 days.
- The TAXII data connector (bulk feed) is not quota-metered; the REST single-IP endpoint the playbook uses is. This is intentional — see the Operations decisions log for why.
