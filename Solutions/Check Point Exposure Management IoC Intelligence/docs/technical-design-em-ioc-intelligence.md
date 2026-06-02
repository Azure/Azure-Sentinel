# Integration | Check Point Exposure Management IoC Intelligence for Microsoft Sentinel

## General Description

The **Check Point Exposure Management IoC Intelligence** Solution streams the high-fidelity Premium Indicators-of-Compromise feed from the Cyberint Infinity External Risk Management (Argos) platform into Microsoft Sentinel and provides an out-of-the-box (OOTB) playbook to enrich Sentinel incident entities against the same Premium intelligence.

Compared to the existing **Check Point Cyberint IOC** Solution (which ingests the daily public IOC feed), the Premium variant exposes a richer schema and uses incremental polling against the new `ioc-intel/feed-api` and `ioc-intel/enrichment-api` services.

| Property | Cyberint IOC (existing) | Exposure Management IoC Intelligence (this Solution) |
|---|---|---|
| Solution id | `checkpoint.azure-sentinel-checkpoint-cyberint-ioc` | `checkpoint.azure-sentinel-checkpoint-em-ioc-intelligence` |
| Feed endpoint | `POST /ioc/api/v1/feed/daily/get` | `POST /ioc-intel/feed-api/v1/feed/jsonl` |
| Enrichment endpoint | `GET /api/v1/file/{type}/{value}` (via Alerts solution) | `POST /ioc-intel/enrichment-api/v1/enrichment` |
| Response format | JSON array | JSON Lines (NDJSON) |
| Polling cadence | 1× / 24h | 1× / 60 min |
| Cursor field | `date` (yyyy-MM-dd) | `added_to_feed_after` (ISO-8601) |
| Custom table | `iocsent_CL` (7 columns) | `emiocintel_CL` (16 + `TimeGenerated`) |
| Feed payload | flat scalar fields | scalar + arrays + nested type-specific enrichment |
| Includes OOTB playbook | No | Yes (`Check_Point_EM_IOCIntelligenceEnrichment`) |

The two Solutions install side-by-side; they declare different Solution IDs, connector IDs and table names.

## Use Cases

### Use Case #1 — IoC Intelligence ingestion into Microsoft Sentinel

- A Codeless Connector Platform (CCP) data connector polls the Premium feed every 60 minutes filtered by `added_to_feed_after = lastQueryWindowStart`.
- Each indicator is written as a row in `emiocintel_CL`.
- A Data Collection Rule (DCR) transform sets `TimeGenerated = todatetime(added_to_feed)` so KQL ranges (`ago(...)`, `between(...)`) return data ordered by feed-publish time, not ingestion time.

### Use Case #2 — Incident IOC enrichment

- An Automation Rule (or manual run from the incident pane) invokes the `Check_Point_EM_IOCIntelligenceEnrichment` Logic App.
- The playbook extracts IP, FileHash, DNS and URL entities from the Sentinel incident.
- For each entity, it calls `POST /ioc-intel/enrichment-api/v1/enrichment` with the appropriate `type` (auto-detecting `md5` / `sha1` / `sha256` from hash length) and the entity value.
- The aggregated enrichment summary (malicious / confidence / severity / activity / kill-chain stage / malware family / threat actors / CVEs) is appended to the incident as a comment.

## Architecture Overview

```
                            ┌────────────────────────────────────┐
                            │  Cyberint Argos / Infinity ERM     │
                            │                                    │
                            │  /ioc-intel/feed-api/v1/feed/jsonl │  ◄── batch (Premium feed)
                            │  /ioc-intel/enrichment-api/v1/...  │  ◄── point lookup (per IOC)
                            └────────────────┬───────────────────┘
                                             │   POST  + Cookie: access_token=...
                          ┌──────────────────┴────────────────────┐
                          │                                       │
              ┌───────────▼────────────┐         ┌────────────────▼─────────────────┐
              │   Sentinel CCP Poller  │         │   Logic App (OOTB Playbook)      │
              │   RestApiPoller every  │         │   Check_Point_EM_PremiumIOC...   │
              │   60 min, jsonlines    │         │   Trigger: incident creation     │
              └───────────┬────────────┘         └─────────────────┬────────────────┘
                          │ Custom-emiocintel_CL stream         │ Sentinel REST API
              ┌───────────▼────────────┐                            │ (incident comment)
              │  Data Collection Rule  │                            │
              │  + KQL transform       │                            │
              │  TimeGenerated <-      │                            │
              │  todatetime(added_to.. │                            │
              └───────────┬────────────┘                            │
                          │                                         │
              ┌───────────▼────────────┐                ┌───────────▼────────────┐
              │   Log Analytics:       │                │   Microsoft Sentinel   │
              │   emiocintel_CL    │                │   Incident             │
              └────────────────────────┘                └────────────────────────┘
```

### Components

| # | Component | Type | Trigger | Purpose |
|---|---|---|---|---|
| 1 | IoC Intelligence Data Connector | CCP `RestApiPoller` | Recurrence (60 min) | Pulls new indicators since the last poll window |
| 2 | IoC Intelligence DCR | Data Collection Rule | Per row | Streams ingested events into `emiocintel_CL`, projecting `TimeGenerated` from `added_to_feed` |
| 3 | IoC Intelligence Table | Custom Log Analytics table | n/a | Persistent store for the feed |
| 4 | `Check_Point_EM_IOCIntelligenceEnrichment` | Logic App Playbook | Sentinel incident creation (Automation Rule) or manual | Enriches IP/FileHash/DNS/URL incident entities |

All four are packaged as Sentinel content templates inside `Package/mainTemplate.json` and registered under the Solution `contentPackage` so they appear in **Content Hub → Manage → Check Point Exposure Management IoC Intelligence**.

## Data Model

### Custom table: `emiocintel_CL`

| Column | Type | Source field | Notes |
|---|---|---|---|
| `indicator_type` | string | `indicator_type` | Enum: `ipv4`, `domain`, `url`, `sha256`, `sha1`, `md5` |
| `indicator_value` | string | `indicator_value` | The raw IOC (IP, FQDN, URL, hash) |
| `activity` | string | `activity` | `ActivityClassification` enum (e.g. `Phishing`, `CnC Server`, `Malware`) |
| `confidence` | int | `confidence` | 0–100 |
| `severity` | int | `severity` | 1–5 |
| `malicious` | string | `malicious` | `yes` / `no` / `inconclusive` |
| `kill_chain_stage` | string | `kill_chain_stage` | MITRE-style enum (e.g. `command-and-control`, `initial-access`) |
| `first_seen` | datetime | `first_seen` | First Cyberint observation |
| `last_seen` | datetime | `last_seen` | Most recent observation |
| `added_to_feed` | datetime | `added_to_feed` | Source of `TimeGenerated` |
| `valid_until` | datetime | `valid_until` | TTL after which the IOC should be considered stale |
| `is_blocking` | boolean | `is_blocking` | Cyberint recommendation to block |
| `is_unique` | boolean | `is_unique` | Indicator is unique to this customer |
| `malware_types` | dynamic | `malware_types` | Array, e.g. `["Trojan", "Ransomware"]` |
| `has_cve` | boolean | `has_cve` | Indicator has associated CVEs |
| `has_campaign` | boolean | `has_campaign` | Indicator linked to a tracked campaign |
| `TimeGenerated` | datetime | (derived) | `todatetime(added_to_feed)` via DCR transform |

### DCR transform

```kql
source
| extend TimeGenerated = todatetime(added_to_feed)
```

The original `added_to_feed` is preserved as a column in addition to becoming the row's `TimeGenerated`.

### Sample KQL

```kql
// Last 24h of high-confidence, blocking malicious indicators
emiocintel_CL
| where TimeGenerated > ago(24h)
| where malicious == "yes" and is_blocking == true
| where confidence >= 80 and severity >= 4
| project TimeGenerated, indicator_type, indicator_value,
          activity, kill_chain_stage, confidence, severity, malware_types
| order by TimeGenerated desc
```

```kql
// Indicators tagged with Ransomware, by activity classification
emiocintel_CL
| where TimeGenerated > ago(7d)
| where malware_types has "Ransomware"
| summarize indicators = dcount(indicator_value) by activity
| order by indicators desc
```

```kql
// Match Sentinel-observed entities (e.g. SecurityEvent IPs) against the Premium feed
let bad = emiocintel_CL
    | where TimeGenerated > ago(30d) and malicious == "yes"
    | summarize arg_max(TimeGenerated, *) by indicator_value
    | where indicator_type == "ipv4"
    | project IpAddress = indicator_value, confidence, severity, activity;
SecurityEvent
| where TimeGenerated > ago(1d)
| where isnotempty(IpAddress)
| join kind=inner bad on IpAddress
```

## Data Connector

### Authentication

Cyberint API access tokens are sent as a cookie:

```
Cookie: access_token=<API_TOKEN>
```

The connector form collects:

| Field | Description |
|---|---|
| **Argos URL** | Cyberint API base, e.g. `https://your-company.cyberint.io` |
| **API Token** | Long-lived API access token (stored as a SecureString) |
| **Customer Name** | Company (client) name associated with the Cyberint instance — sent as `X-Integration-Customer-Name` for telemetry |

### Polling configuration

| Setting | Value | Rationale |
|---|---|---|
| `httpMethod` | `POST` | Premium feed expects a JSON body |
| `apiEndpoint` | `<argosurl>/ioc-intel/feed-api/v1/feed/jsonl` | JSON Lines variant (one IOC per line) |
| `queryWindowInMin` | `60` | Hourly polling balances freshness against rate-limits |
| `queryTimeFormat` | `yyyy-MM-ddTHH:mm:ssZ` | ISO-8601 to match the API contract for `added_to_feed_after` |
| `rateLimitQPS` | `10` | Premium API rate limit |
| `timeoutInSeconds` | `120` | Larger payloads than the daily feed |
| `retryCount` | `3` | Retry transient errors |
| `response.format` | `jsonlines` | CCP framework parses each line as a separate event |
| `response.eventsJsonPaths` | `["$"]` | Each parsed line is a complete event |
| `response.successStatusCodes` | `[200]` | Only treat 200 as success |

### Request body template

```json
{
  "filters": {
    "added_to_feed_after": "{_QueryWindowStartTime}"
  },
  "pagination": {
    "limit": 100000,
    "offset": 0
  },
  "sort": {
    "field": "added_to_feed",
    "direction": "asc"
  }
}
```

`{_QueryWindowStartTime}` is substituted by the CCP runtime with the start of the current poll window (formatted per `queryTimeFormat`). Sorting ascending guarantees that any indicator written after the cursor moment is captured on the next run.

### Telemetry headers

| Header | Value | Purpose |
|---|---|---|
| `X-Sender-Id` | `0` | Reserved for Cyberint internal telemetry |
| `X-Integration-Type` | `Azure Sentinel CPEM IoC Intelligence` | Identifies the calling integration |
| `X-Integration-Instance-Name` | `Default` | Instance label (free-form) |
| `X-Integration-Instance-Id` | `0` | Instance identifier (free-form) |
| `X-Integration-Customer-Name` | (from form) | Customer label, supplied at connector setup |
| `X-Integration-Version` | `1.0` | Solution schema version |
| `User-Agent` | `Scuba` | Conventional Cyberint integration UA |

## Playbook: `Check_Point_EM_IOCIntelligenceEnrichment`

### Trigger

`Microsoft Sentinel incident` (`/incident-creation`) — works either via an Automation Rule on incident creation or as a manual run from the incident pane.

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `PlaybookName` | String | Logic App name; defaults to `Check_Point_EM_IOCIntelligenceEnrichment` |
| `API_Base_URL` | String | Cyberint API base URL, e.g. `https://your-company.cyberint.io` |
| `API_Access_Token` | SecureString | Cyberint API access token |

### Workflow

```
Trigger: incident-creation
   ├─ Entities - Get IPs        \
   ├─ Entities - Get FileHashes  ┐
   ├─ Entities - Get DNS         ├─ run in parallel
   └─ Entities - Get URLs       /
        └─ Initialize EnrichmentComment (string, "")
             └─ For each IP
                  ├─ POST /v1/enrichment  body: { type: "ipv4",   value: <IP> }
                  └─ Append to EnrichmentComment
                       └─ For each FileHash
                            ├─ Detect type by length (32→md5, 40→sha1, 64→sha256)
                            ├─ POST /v1/enrichment  body: { type: <detected>, value: <hash> }
                            └─ Append to EnrichmentComment
                                 └─ For each Domain (DNS resolution)
                                      ├─ POST /v1/enrichment  body: { type: "domain", value: <fqdn> }
                                      └─ Append to EnrichmentComment
                                           └─ For each URL
                                                ├─ POST /v1/enrichment  body: { type: "url", value: <url> }
                                                └─ Append to EnrichmentComment
                                                     └─ Add comment to incident
```

The for-each blocks are sequential (each chained via `runAfter`) so the comment is appended in a deterministic order.

### Per-entity enrichment call

```http
POST {API_Base_URL}/ioc-intel/enrichment-api/v1/enrichment
Accept:        application/json
Content-Type:  application/json
Cookie:        access_token={API_Access_Token}
X-Integration-Type:    Azure Sentinel CPEM IoC Intelligence
X-Integration-Version: 1.0

{
  "type":  "ipv4|domain|url|sha256|sha1|md5",
  "value": "<entity value>"
}
```

### Response fields surfaced into the incident comment

| Comment label | JSON path | Notes |
|---|---|---|
| `Malicious` | `malicious` | `yes` / `no` / `inconclusive` |
| `Confidence` | `confidence` | 0–100 |
| `Severity` | `severity` | 0–5 |
| `Activity` | `activity` | Activity classification |
| `Kill Chain` | `kill_chain_stage` | (IP / URL only) |
| `Malware Family` | `malware_family` | |
| `Threat Actors` | `threat_actors[]` | Joined with `,` (FileHash, Domain) |
| `CVEs` | `cves[]` | Joined with `,` (FileHash) |
| `First Seen` | `first_seen` | (IP) |

The full Premium response also includes `last_seen`, `valid_until`, `malware_types`, `origin_countries`, `targeted_countries`, `targeted_sectors`, `targeted_brands`, `campaigns`, `ttps`, `tags`, plus a type-specific `enrichment` block (geo+ASN for IPs, whois for domains/URLs, filenames+download_urls for hashes). These are returned by the API and can be surfaced in additional comment fields if required.

### Sample incident comment

```
CPEM IoC Intelligence Enrichment Results:
IP: 198.51.100.42 — Malicious: yes | Confidence: 92 | Severity: 4 | Activity: CnC Server
   | Kill Chain: command-and-control | Malware Family: Cobalt Strike | First Seen: 2026-04-19T08:14:00Z
Hash (sha256): 6a7b02c43837dcb8e40d271edb88d13d2e723c721a74931857aaef4853317789 — Malicious: yes
   | Confidence: 99 | Severity: 5 | Activity: Malware | Malware Family: LockBit
   | Threat Actors: Lockbit Group, ITG23 | CVEs: CVE-2024-1234, CVE-2024-5678
Domain: malicious-example.com — Malicious: yes | Confidence: 85 | Severity: 3
   | Activity: Phishing | Malware Family: – | Threat Actors: APT-Phantom
URL: http://www.evil-example.com/payload — Malicious: yes | Confidence: 95 | Severity: 5
   | Activity: Malware | Kill Chain: execution | Malware Family: Emotet
```

### Required permissions

The Logic App's System-Assigned Managed Identity needs the **Microsoft Sentinel Responder** role on the resource group hosting the Sentinel workspace, to write incident comments.

## Solution Package

```
Solutions/Check Point Exposure Management IoC Intelligence/
├── Data/
│   └── Solution_CPEMIOCIntelligence.json
├── Data Connectors/
│   └── CPEMIOCIntelligenceLogs_ccp/
│       ├── CPEMIOCIntelligenceLogs_connectorDefinition.json
│       ├── CPEMIOCIntelligenceLogs_PollingConfig.json
│       ├── CPEMIOCIntelligenceLogs_DCR.json
│       └── CPEMIOCIntelligenceLogs_Table.json
├── Playbooks/
│   └── CPEM_IOCIntelligenceEnrichment/
│       └── azuredeploy.json                 (standalone deployment)
├── Package/
│   ├── mainTemplate.json                    (Solution ARM — embeds connector + playbook)
│   ├── createUiDefinition.json
│   └── testParameters.json
├── docs/
│   └── technical-design-em-ioc-intelligence.md      (this document)
├── ReleaseNotes.md
└── SolutionMetadata.json
```

`Package/mainTemplate.json` is the artifact deployed by **Content Hub** when a customer installs the Solution. It packages four resources behind a single content package:

| Resource | Kind | Reason for being in the Solution |
|---|---|---|
| `dataConnectorDefinitions/CheckPointEMIOCIntelligence` | Customizable | Renders the connector form in Sentinel UI |
| `metadata/DataConnector-CheckPointEMIOCIntelligence` | Metadata | Registers the connector in Content Hub |
| Connector content template (`...-dc-...`) | DataConnector | Holds the DCR + table schema |
| Resources content template (`...-dc-...`) | ResourcesDataConnector | Holds the `RestApiPoller` instance template |
| Playbook content template (`...-pl-...`) | Playbook | Holds the IoC Intelligence Enrichment Logic App template |
| `contentPackages/...-em-ioc-intelligence` | Solution | Top-level Solution registration with dependency graph |

## Deployment

### Prerequisites

- A Microsoft Sentinel workspace (Log Analytics).
- A Cyberint API access token with read access to the IoC Intelligence feed and enrichment APIs.
- For the playbook: the Logic App's Managed Identity must hold **Microsoft Sentinel Responder** on the resource group.

### Option A — Content Hub (production)

1. Open Microsoft Sentinel → **Content management** → **Content Hub**.
2. Search for **Check Point Exposure Management IoC Intelligence**.
3. Click **Install**.
4. Open **Manage** → **Data connectors** → **Check Point Exposure Management IoC Intelligence Connector** → fill in **Argos URL**, **API Token**, **Customer Name** → **Connect**.
5. Open **Manage** → **Playbook templates** → **Check Point EM IoC Intelligence Enrichment** → **Create playbook** → supply `API_Base_URL` and `API_Access_Token`.
6. Create an **Automation rule** to attach the playbook to incident creation.

### Option B — Direct ARM deploy (dev / lab)

```bash
az deployment group create \
  --resource-group <rg> \
  --template-file "Solutions/Check Point Exposure Management IoC Intelligence/Package/mainTemplate.json" \
  --parameters workspace=<workspace> workspace-location=<region>
```

The Solution package is identical to what Content Hub deploys.

### Option C — Standalone Logic App deploy (just the playbook)

```bash
az deployment group create \
  --resource-group <rg> \
  --template-file "Solutions/Check Point Exposure Management IoC Intelligence/Playbooks/CPEM_IOCIntelligenceEnrichment/azuredeploy.json" \
  --parameters API_Base_URL=https://your-company.cyberint.io API_Access_Token=<token>
```

Useful when iterating on the playbook without re-deploying the whole Solution.

## Verification

```kql
// 1. Connector is producing rows
emiocintel_CL
| summarize count(), max(TimeGenerated) by bin(TimeGenerated, 1h)
| order by TimeGenerated desc
```

```kql
// 2. Schema is healthy (no row should have null indicator_type / indicator_value)
emiocintel_CL
| where isempty(indicator_type) or isempty(indicator_value)
| count
```

```kql
// 3. Distribution by IOC type — sanity check
emiocintel_CL
| where TimeGenerated > ago(24h)
| summarize count() by indicator_type
```

To verify the playbook end-to-end:
1. Create a test Sentinel incident with at least one IP, file hash, domain or URL entity (or trigger the playbook manually on an existing incident).
2. Watch the Logic App run history — the four `Entities - Get *` actions should succeed, then per-entity `Enrich_*` HTTP actions should return `200`.
3. Confirm the new comment appears on the incident with the structured enrichment line.

## Operational Notes

- **Retention**: `emiocintel_CL` follows the Log Analytics workspace's table retention. For long-term IOC retention consider configuring a longer per-table retention policy.
- **Cost**: Premium feed is incremental (`added_to_feed_after` cursor), so ingestion cost is proportional to the number of *new* indicators per hour, not the entire catalogue size.
- **Co-existence**: IoC Intelligence can be installed alongside the original **Check Point Cyberint IOC** Solution. They write to different tables (`emiocintel_CL` vs `iocsent_CL`) and register different Solution IDs.
- **Rate limits**: The connector defaults to 10 QPS. The enrichment playbook makes one HTTP call per incident entity sequentially; Logic Apps' built-in throttling is sufficient for typical incident volumes.
- **Failure semantics**: If the feed endpoint is unavailable, the CCP poller retries up to 3 times per window and surfaces the error in the connector health blade. The enrichment playbook does not block the incident if the API is unreachable — the comment is still posted, with empty enrichment fields.

## API Reference

### Feed: `POST /ioc-intel/feed-api/v1/feed/jsonl`

Request body (`FeedRequest`):

| Field | Type | Description |
|---|---|---|
| `filters.indicator_type` | array<enum> | `ipv4`, `domain`, `url`, `sha256`, `sha1`, `md5` — optional |
| `filters.activity` | array<enum> | `ActivityClassification` — optional |
| `filters.confidence_min` / `confidence_max` | int 0-100 | optional |
| `filters.severity_min` / `severity_max` | int 1-5 | optional |
| `filters.malicious` | enum | `yes` / `no` / `inconclusive` — optional |
| `filters.first_seen_after` / `_before` | datetime | optional |
| `filters.last_seen_after` / `_before` | datetime | optional |
| `filters.added_to_feed_after` / `_before` | datetime | **used by this Solution** for incremental polling |
| `filters.is_blocking` / `is_unique` | bool | optional |
| `filters.malware_family` | array<string> | optional |
| `filters.origin_country` / `targeted_country` / `targeted_sector` | array<string> | optional |
| `filters.has_campaign` / `has_cve` | bool | optional |
| `pagination.limit` | int (max 100000) | default 10000 |
| `pagination.offset` | int | optional |
| `sort.field` | enum | `confidence` / `severity` / `first_seen` / `last_seen` / `added_to_feed` |
| `sort.direction` | enum | `asc` / `desc` |

Response: a JSON Lines stream of indicators (one IOC per line) — see *Data Model* above for the schema.

### Enrichment: `POST /ioc-intel/enrichment-api/v1/enrichment`

Request body (`EnrichmentRequest`):

```json
{
  "type":  "ipv4 | domain | url | sha256 | sha1 | md5",
  "value": "<indicator>"
}
```

Response (`EnrichedIOC`) — fields beyond what the feed returns:

| Field | Type | Notes |
|---|---|---|
| `malware_family` | string | |
| `origin_countries` | array<string> | |
| `targeted_countries` | array<string> | |
| `targeted_sectors` | array<string> | |
| `targeted_brands` | array<string> | |
| `threat_actors` | array<string> | |
| `campaigns` | array<string> | |
| `cves` | array<string> | |
| `ttps` | array<{mitre_id,title}> | MITRE ATT&CK techniques |
| `tags` | array<string> | |
| `enrichment` | object | Type-specific: `Ipv4Enrichment` (geo + ASN), `DomainEnrichment` (ips + whois), `URLEnrichment` (ips + hostname + domain + whois), `FileHashEnrichment` (filenames + download_urls) |

## Versioning

| Solution version | Date | Notes |
|---|---|---|
| 1.0.0 | 2026-04-26 | Initial release. CCP data connector + `Check_Point_EM_IOCIntelligenceEnrichment` playbook. |

## References

- Exposure Management IoC Intelligence Feed API: `em-ioc-intelligence-feed-api.json` (OpenAPI 3.1)
- Exposure Management IoC Intelligence Enrichment API: `em-ioc-intelligence-enrichment-api.json` (OpenAPI 3.1)
- Microsoft Sentinel CCP framework: <https://learn.microsoft.com/azure/sentinel/data-connector-references-customizable>
- XSOAR reference integration (Cyberint Premium Feed): `Packs/Cyberint/Integrations/FeedCyberintPremium/`
- Companion Solution: **Check Point Cyberint IOC** (legacy daily feed)
- Companion Solution: **Check Point Cyberint Alerts** (alert ingestion + bi-directional sync + IOC/Credential/Phishing/Vulnerability OOTB playbooks)
