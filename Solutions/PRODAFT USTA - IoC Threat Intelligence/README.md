# PRODAFT USTA - IoC Threat Intelligence — Microsoft Sentinel Solution

Ingests **indicators of compromise** — malicious URLs, malware hashes, and phishing sites —
from the PRODAFT USTA Security Intelligence API into Microsoft Sentinel **Threat
Intelligence** as STIX 2.1 indicators. Unlike the other PRODAFT USTA solutions (which land
data in custom `_CL` tables via a codeless connector), this solution pushes indicators to
Sentinel's **Upload STIX Objects API**, so they appear in the **Threat Intelligence blade**
and the built-in `ThreatIntelIndicators` table. Each feed uploads under its own
`SourceSystem` — `PRODAFT USTA - Malicious URLs`, `PRODAFT USTA - Malware Hashes` and
`PRODAFT USTA - Phishing Sites` — so `SourceSystem startswith "PRODAFT USTA"` selects every
USTA indicator while each feed stays individually filterable in the Threat Intelligence blade.

## Contents

| Content | Items |
|---|---|
| Data connector | `PRODAFTUstaIoC_UploadIndicatorsAPI` — a documentation/health card; ingestion is performed by the playbooks below |
| Import playbooks | `PRODAFTUstaIoC-ImportMaliciousUrls`, `PRODAFTUstaIoC-ImportMalwareHashes`, `PRODAFTUstaIoC-ImportPhishingSites` — hourly, one per feed |
| Backfill playbooks | `PRODAFTUstaIoC-BackfillMaliciousUrls`, `PRODAFTUstaIoC-BackfillMalwareHashes`, `PRODAFTUstaIoC-BackfillPhishingSites` — on-demand historical load, one per feed (default 90 days) |
| Analytic rules | TI map URL → Syslog; TI map Domain → DnsEvents; TI map File Hash → CommonSecurityLog |
| Workbook | `PRODAFTUstaIoCOverview` |

## How it works

Each import playbook is a Logic App that, every hour:

1. Reads its own ingestion watermark — `max(Created)` for this feed's `SourceSystem` in
   `ThreatIntelIndicators`, minus a 5-minute overlap — and fetches everything created since,
   following the API's `next` link until the page set is exhausted. `LookBackHours` (default 2)
   is only the fallback for the first run, when no watermark exists yet. Because the watermark
   advances only after a **successful** upload, a failed run retries the same window rather
   than skipping indicators.
2. Maps each record to a **STIX 2.1 indicator** — `is_domain` chooses a `domain-name` vs
   `url` pattern; malware hashes become a `file:hashes` pattern (MD5/SHA-1/SHA-256); vendor
   `tags` become STIX `labels`; indicators are marked `TLP:AMBER`. When the record carries
   `ip_addresses`, each address is appended to the **same** indicator's pattern as its own
   observation expression — `ipv4-addr:value` or `ipv6-addr:value`, picked per address — so the
   URL/hash and its resolved IPs travel as one indicator sharing one validity window.
3. Uploads batches (≤100) to Sentinel via the **Upload STIX Objects** action using the Logic
   App's **system-assigned managed identity**.

STIX ids are **deterministic** (the USTA record id for URLs/hashes; a stable UUID derived
from the integer id for phishing sites), so overlapping re-uploads **update**
rather than duplicate indicators. Malicious URLs and malware hashes carry `valid_from` and
`valid_until` in the feed and those values are used as-is. Phishing sites have no expiry in
the feed, so a validity window (`ValidityDays`, default 365) is synthesized from each site's
`created` date.

## Deployment

### Prerequisites

* Install the Microsoft **Threat Intelligence** solution from the Content hub first — it
  provides the Threat Intelligence blade, the `ThreatIntelIndicators` table, and 50+
  source-agnostic TI-map rules (which will also match PRODAFT USTA indicators).
* A PRODAFT USTA long-lived API key and the **name** of your Microsoft Sentinel (Log
  Analytics) workspace.

### From the portal (Content Hub)

1. Install **PRODAFT USTA - IoC Threat Intelligence** from **Microsoft Sentinel → Content hub**.
2. From **Manage → Playbook templates**, deploy the three import playbooks, supplying the
   USTA base URL, API key, and workspace name.
3. For **each** import playbook, grant its system-assigned managed identity **two** roles on the
   workspace. Open **Log Analytics workspace → Access control (IAM) → Add role assignment** — on the
   *workspace*, **not** on the Logic App; opening IAM from the playbook's own blade scopes the
   assignment to `.../Microsoft.Logic/workflows/<playbook>`, which looks right in the portal but
   grants no workspace access. Assign:
   **Microsoft Sentinel Contributor** for the Upload STIX Objects call, and **Log Analytics Reader**
   for the watermark query. Sentinel Contributor alone is not enough for the query — it grants
   `Microsoft.OperationalInsights/workspaces/*/read`, which does not cover the bare
   `Microsoft.OperationalInsights/workspaces/read` action the Azure Monitor Logs connection
   performs, so the run fails with `AuthorizationFailed`. The **backfill** playbooks upload only
   and need just Microsoft Sentinel Contributor.
4. To load history, deploy the matching **backfill** playbook for each feed and run its trigger
   once. It pages `BackfillDays` (default **90**) of history into the same `SourceSystem`, so the
   data unifies with the hourly imports. See each playbook's readme —
   [BackfillMaliciousUrls](Playbooks/PRODAFTUstaIoC-BackfillMaliciousUrls/readme.md),
   [BackfillMalwareHashes](Playbooks/PRODAFTUstaIoC-BackfillMalwareHashes/readme.md),
   [BackfillPhishingSites](Playbooks/PRODAFTUstaIoC-BackfillPhishingSites/readme.md).
   Backfills are safe to run while the import playbooks are active: STIX ids are deterministic, so
   re-uploads update rather than duplicate, and loading older records never moves an import
   playbook's watermark backwards.

### Via scripts (this repository)

Generate the deployable package with the repo's packaging tool (creates
`Package/mainTemplate.json` + `Package/createUiDefinition.json`):

```bash
# from the repository root — pass the ABSOLUTE path to this solution's Data folder
pwsh Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1 \
  -SolutionDataFolderPath "$(pwd)/Solutions/PRODAFT USTA - IoC Threat Intelligence/Data" \
  -VersionMode catalog
```

```bash
az deployment group create \
     --resource-group "<resource-group>" \
     --template-file "Solutions/PRODAFT USTA - IoC Threat Intelligence/Package/mainTemplate.json" \
     --parameters workspace="<workspace>" workspace-location="<location>"
```

Installing the solution **stores** the playbook templates in the workspace; it does not create
any Logic App. Instantiate each playbook afterwards from **Manage → Playbook templates** (or by
deploying its own `azuredeploy.json`), then complete the role assignments (step 3 above).

## Notes

* **No plaintext secrets in ARM:** the USTA API key is passed as a secured parameter; the
  fetch and upload actions run with secure inputs/outputs so the key and data are hidden
  from the Logic App run history.
* **Detections:** the three shipped rules are PRODAFT-scoped (`SourceSystem startswith "PRODAFT USTA"`)
  and query the modern `ThreatIntelIndicators` table. They require the relevant log-source
  connectors (Syslog, DNS, CEF) to be enabled to produce matches.
* **Resolved IP addresses** from each feed's `ip_addresses` field are included in the
  indicator pattern (up to the first **10** per record; additional addresses are dropped).
  Sentinel splits a multi-observation pattern into one `ObservableKey`/`ObservableValue` row
  per observable, so these IPs are matchable on their own — including by the source-agnostic
  IP TI-map rules shipped with the Microsoft **Threat Intelligence** solution.
* **Shared hosting caveat:** many phishing hosts sit behind CDNs, so a resolved address is
  often a shared edge IP rather than attacker infrastructure. Matching on such an address can
  raise false positives on legitimate traffic. If that matters in your environment, keep the
  PRODAFT-scoped rules in this solution (they match on URL, domain and file hash, not IP) and
  leave the generic IP TI-map rules disabled for this source.
