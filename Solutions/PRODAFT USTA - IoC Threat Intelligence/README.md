# PRODAFT USTA - IoC Threat Intelligence — Microsoft Sentinel Solution

Ingests **indicators of compromise** — malicious URLs, malware hashes, and phishing sites —
from the PRODAFT USTA Security Intelligence API into Microsoft Sentinel **Threat
Intelligence** as STIX 2.1 indicators. Unlike the other PRODAFT USTA solutions (which land
data in custom `_CL` tables via a codeless connector), this solution pushes indicators to
Sentinel's **Upload STIX Objects API**, so they appear in the **Threat Intelligence blade**
and the built-in `ThreatIntelIndicators` table with `SourceSystem == "PRODAFT USTA"`

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

1. Reads a sliding window (`LookBackHours`, default 2) of new records from its USTA IoC feed,
   following the API's `next` link until the page set is exhausted.
2. Maps each record to a **STIX 2.1 indicator** — `is_domain` chooses a `domain-name` vs
   `url` pattern; malware hashes become a `file:hashes` pattern (MD5/SHA-1/SHA-256); vendor
   `tags` become STIX `labels`; indicators are marked `TLP:AMBER`.
3. Uploads batches (≤100) to Sentinel via the **Upload STIX Objects** action using the Logic
   App's **system-assigned managed identity**.

STIX ids are **deterministic** (the USTA record id for URLs/hashes; a stable UUID derived
from the integer id for phishing sites), so re-uploads over the sliding window **update**
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
3. For **each** import playbook, grant its system-assigned managed identity the
   **Microsoft Sentinel Contributor** role on the workspace
   (Log Analytics workspace → Access control (IAM) → Add role assignment). This is required
   for the Upload STIX Objects call.
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

Then deploy `Package/mainTemplate.json` into a Sentinel-enabled workspace and complete the
managed-identity role assignment (step 3 above).

## Notes

* **No plaintext secrets in ARM:** the USTA API key is passed as a secured parameter; the
  fetch and upload actions run with secure inputs/outputs so the key and data are hidden
  from the Logic App run history.
* **Detections:** the three shipped rules are PRODAFT-scoped (`SourceSystem == "PRODAFT USTA"`)
  and query the modern `ThreatIntelIndicators` table. They require the relevant log-source
  connectors (Syslog, DNS, CommonSecurityLog) to be enabled to produce matches.
* **Resolved IP addresses** returned by the feeds are not promoted to separate `ipv4-addr`
  indicators by default (to avoid shared-hosting false positives).
