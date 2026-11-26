# Cognyte Luminar Threat Intelligence Connector - Microsoft Sentinel

## Table of Contents

1. [Overview](#overview)
2. [What is ingested](#what-is-ingested)
3. [Luminar API account](#luminar-api-account)
4. [Register a Microsoft Entra application for the upload API](#entra-app)
5. [Deployment](#deployment)
6. [Configuration reference](#configuration-reference)
7. [Detection & investigation](#detection--investigation)
8. [Local development and tests](#local-development-and-tests)

## Overview

Cognyte is a global leader in security analytics software that empowers governments and enterprises with Actionable Intelligence for a safer world. Luminar is an asset-based cybersecurity intelligence platform that enables enterprise organizations to build and maintain a proactive threat intelligence operation.

This connector is an Azure Function that pulls STIX 2.1 objects from the Luminar TAXII 2.1 server and uploads them to Microsoft Sentinel threat intelligence through the [STIX objects upload API](https://learn.microsoft.com/azure/sentinel/stix-objects-api). Objects land in the `ThreatIntelIndicators` and `ThreatIntelObjects` tables.

```
Luminar TAXII 2.1  --(luminar_manager.py)-->  batches
  --(stix_transform.py)-->  indicator / threat-actor / identity / relationship
  --(sentinel_client.py)-->  api.ti.sentinel.azure.com  -->  ThreatIntelIndicators, ThreatIntelObjects
```

## What is ingested

| Luminar collection | Uploaded | Not uploaded (unsupported by the upload API) |
|---|---|---|
| `iocs` | indicators (URL, IPv4, with Luminar confidence, labels and 7-day validity), relationships to identities / threat actors | `software` and the relationships pointing at it |
| `cyberfeeds` | indicators (SHA-256, MD5, SHA-1, IPv4, domain), threat actors, identities, relationships between them | `malware`, `report`, `vulnerability`, `campaign`, `software`, `location` |
| `leakedrecords` | nothing | the collection contains only `incident`, `user-account`, `malware` and `relationship` objects, none of which the upload API accepts |

The upload API accepts five STIX types: `indicator`, `attack-pattern`, `identity`, `threat-actor`, `relationship`. Every object is uploaded with:

- Luminar's own STIX `id`, so re-ingestion updates rather than duplicates.
- Luminar's `extensions` block (score, ASN, country, resolving domains, ...) untouched; it is stored in the `Data` column.
- A `luminar:<collection>` label, a TLP marking (`TLPLevel`), and an `external_references` entry carrying the Luminar id.
- Indicators without `valid_until` (all of `cyberfeeds`) get `valid_from + DefaultIndicatorValidityDays`; indicators without `confidence` get `DefaultConfidence`.
- Indicators that are already expired at upload time are skipped (`SkipExpiredIndicators`), together with relationships that point at them.
- `cyberfeeds` indicators are enriched from the Luminar reports that reference them: report titles are appended to `description`, and `malware:<name>` / `actor:<name>` / `campaign:<name>` labels are added for objects referenced by the same report.

## Luminar API account

You need a Luminar API **Account ID**, **Client ID** and **Client Secret**. For registration contact luminar@cognyte.com.

<a name="entra-app"></a>
## Register a Microsoft Entra application for the upload API

The upload API authenticates with a Microsoft Entra application that holds the **Microsoft Sentinel Contributor** role on the workspace. No Microsoft Graph permission is needed.

1. Go to **Microsoft Entra ID > App registrations > New registration**, give it a name and register it.
2. On the **Overview** tab copy the **Application (client) ID** and **Directory (tenant) ID**.
3. Under **Certificates & secrets > New client secret** create a secret and copy its value immediately.
4. Open the Log Analytics workspace that backs Microsoft Sentinel, go to **Access control (IAM) > Add > Add role assignment**, pick **Microsoft Sentinel Contributor**, then **Members > User, group, or service principal** and select the application by name.
5. Copy the **Workspace ID** from the workspace **Overview** page.

Reference: [Connect your TIP with the upload API](https://learn.microsoft.com/azure/sentinel/connect-threat-intelligence-upload-api).

## Deployment

1. In Microsoft Sentinel open **Content hub**, search for **Cognyte Luminar** and install it.
2. Open the data connector page and use one of the **Deploy to Azure** buttons (Flex Consumption or Premium plan).
3. Fill in the parameters listed in the next section and deploy.

Upgrading from 3.0.x: redeploy with the new parameters (`WorkspaceID` is mandatory) and assign the Sentinel Contributor role to the existing app. The old single checkpoint stored in the function's file share is migrated automatically to per-collection checkpoints.

## Configuration reference

| App setting | Required | Default | Description |
|---|---|---|---|
| `TenantID`, `ApplicationID`, `ClientSecret` | yes | | Entra application with Microsoft Sentinel Contributor on the workspace |
| `WorkspaceID` | yes | | Log Analytics workspace ID |
| `LuminarAPIClientID`, `LuminarAPIClientSecret`, `LuminarAPIAccountID` | yes | | Luminar API credentials |
| `LuminarBaseURL` | yes | `https://www.cyberluminar.com` | Luminar API base URL |
| `LuminarInitialFetchDate` | yes | | `YYYY-MM-DD` (or full ISO timestamp); used only when a collection has no checkpoint |
| `LuminarCollections` | no | `iocs,cyberfeeds` | Comma-separated collections to ingest |
| `DefaultIndicatorValidityDays` | no | `90` | Expiry for indicators published without `valid_until` |
| `DefaultConfidence` | no | `50` | Confidence for indicators published without one; `none` leaves it unset |
| `TLPLevel` | no | `green` | `white`, `green`, `amber` or `red` |
| `EnrichFromReports` | no | `true` | Enrich `cyberfeeds` indicators from Luminar reports |
| `SkipExpiredIndicators` | no | `true` | Do not upload indicators whose `valid_until` (Luminar's, or the defaulted one) is already in the past, nor relationships that point at them |
| `SourceSystem` | no | `Cognyte Luminar` | Value of `SourceSystem` in the TI tables |
| `LuminarPageLimit` / `LuminarPagesPerBatch` | no | `9999` / `1` | TAXII page size (9999 is the server maximum) and pages per upload batch |
| `MaxRunMinutes` | no | `25` | Stop cleanly after this long; the next run resumes from the checkpoint. Keep it well under the platform's execution limit. |
| `ResumeOverlapSeconds` | no | `1` | Re-read this much history when resuming from a checkpoint |
| `Polling` | yes | from `TimeInterval` | Timer CRON expression |

Checkpoints are the `X-TAXII-Date-Added-Last` header of the last batch uploaded for each collection, saved after the upload succeeds. A run that stops part-way resumes from the last uploaded batch.

## Detection & investigation

Luminar indicators are available to the built-in threat intelligence analytics rules. Sample queries:

```kusto
// Latest version of every Luminar indicator
ThreatIntelIndicators
| where SourceSystem == 'Cognyte Luminar'
| summarize arg_max(TimeGenerated, *) by Id
| where IsDeleted == false
| project ObservableKey, ObservableValue, Confidence, ValidUntil, Tags, Data
```

```kusto
// Sign-ins from IPs that Luminar flagged
let ips = ThreatIntelIndicators
| where SourceSystem == 'Cognyte Luminar' and ObservableKey == 'ipv4-addr:value'
| summarize arg_max(TimeGenerated, *) by Id
| where IsDeleted == false and ValidUntil > now()
| project IPAddress = ObservableValue, Confidence, Tags;
SigninLogs | join kind=inner ips on IPAddress
```

```kusto
// Threat actors and the organisations they target
let actors = ThreatIntelObjects | where SourceSystem == 'Cognyte Luminar' and StixType == 'threat-actor'
  | extend ActorId = tostring(Data.id), Actor = tostring(Data.name);
let rels = ThreatIntelObjects | where SourceSystem == 'Cognyte Luminar' and StixType == 'relationship'
  | extend Src = tostring(Data.source_ref), Tgt = tostring(Data.target_ref), Rel = tostring(Data.relationship_type);
let idents = ThreatIntelObjects | where SourceSystem == 'Cognyte Luminar' and StixType == 'identity'
  | extend IdentityId = tostring(Data.id), Target = tostring(Data.name);
actors | join kind=inner rels on $left.ActorId == $right.Src
| join kind=inner idents on $left.Tgt == $right.IdentityId
| project Actor, Rel, Target
```

## Local development and tests

```bash
cd "Data Connectors"
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt pytest
python -m pytest tests
```

Module layout:

| File | Role |
|---|---|
| `main.py` | timer entry point and per-collection orchestration |
| `luminar_manager.py` | shared Luminar TAXII client (auth, paging, stale-cursor recovery, reference hydration) |
| `stix_transform.py` | pure transform from Luminar objects to upload-ready STIX |
| `sentinel_client.py` | Entra token, upload API, batching, rate limiting, per-record error parsing |
| `state_manager.py` | per-collection checkpoints in the function's Azure File Share |
| `config.py` | app-settings parsing and validation |
