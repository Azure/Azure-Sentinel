# Group-IB Threat Intelligence — Microsoft Sentinel Integration

This integration connects the [Group-IB Threat Intelligence](https://www.group-ib.com/products/threat-intelligence/) platform to Microsoft Sentinel using Azure Logic Apps (playbooks). It continuously fetches threat intelligence data from Group-IB TI feeds and delivers it to Sentinel in two complementary forms:

- **Threat indicators** (IPs, domains, URLs, file hashes) pushed to the Sentinel Threat Intelligence blade as STIX 2.1 objects, where they match against your log data in real time.
- **Context records** (threat actor profiles, APT reports, malware intelligence, vulnerability data, leaked credential metadata, and more) written to dedicated Log Analytics custom tables for analytics rules and enrichment queries.

---

## Deployment Options

The integration ships in two functionally-equivalent packages — pick one based on how you want to operate the integration in Azure:

| Package         | What it is                                                                                                                                                                                   | Best for                                                                                                 | Operator guide                                   |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| **Consumption** | 30 separate Logic Apps, each deployed from its own `azuredeploy-*.json` ARM template at the root of `Playbooks/`. Per-action billing, individual scaling and management per playbook.        | Lighter setups, partial-coverage installs, predictable per-action cost.                                  | [USER_GUIDE.md](USER_GUIDE.md)                   |
| **Standard**    | One Standard Logic App (`Microsoft.Web/sites` + WS1 plan) hosting all 30 playbooks as nested workflows. Single shared Managed Identity, fixed plan billing. Source in `Playbooks/Standard/`. | Production installs running most/all playbooks, predictable monthly cost, single point of admin and IAM. | [USER_GUIDE_STANDARD.md](USER_GUIDE_STANDARD.md) |

Both packages produce identical downstream Sentinel content (same indicators in `ThreatIntelIndicators`, same `GIB*_CL` context tables). Only the wrapper around the workflow definitions differs.

### Standard package: optional `post-deploy.sh` script

For the Standard package, the helper script at `Playbooks/Standard/post-deploy.sh` automates everything after the initial ARM deployment except the one manual Designer-bind step that Azure's tooling currently requires for managed API connections to provision their runtime URLs.

```bash
# 1. In the Azure Portal, "Deploy a custom template" → paste Playbooks/Standard/infrastructure-arm.json → fill params → deploy.

# 2. Then, from the repo root in Cloud Shell or any environment with `az` + `zip`:
cd Playbooks/Standard
./post-deploy.sh <resource-group> <logic-app-name> <workspace-name>
```

The script (~310 lines, bash):

1. Discovers your deployment from the deployed Logic App.
2. Assigns the two required MSI roles (`Microsoft Sentinel Contributor` + `Log Analytics Contributor`) on the workspace.
3. Generates a placeholder `connections.json` so the Designer can render workflows, and zip-deploys the workflows.
4. Pauses and instructs you through the **one** manual Designer-bind step (~2 minutes of Portal clicks).
5. Polls Azure for the two new connection resources to gain populated `connectionRuntimeUrl` values (typically 1-5 minutes).
6. Writes the final `connections.json` and redeploys.
7. Restarts the Logic App.

After the script completes, allow 5-15 minutes for RBAC propagation and connection-claim provisioning, then trigger any workflow to verify end-to-end. See [USER_GUIDE_STANDARD.md §5.3](USER_GUIDE_STANDARD.md#53-deploy-the-workflows) for the manual step-by-step alternative.

---

## Playbook Catalog

### Required Infrastructure

| Playbook file                                   | Purpose                                                                                                                                                                                       | Deploy order |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| `azuredeploy-GIBTIA_IndicatorProcessor_v2.json` | Receives batched STIX 2.1 indicators from all collector playbooks and uploads them to Sentinel Threat Intelligence via Managed Identity. **Must be deployed before any indicator collector.** | 1st          |

---

### Indicator Collector Playbooks

These playbooks poll Group-IB TI feeds on an hourly recurrence, transform records into STIX 2.1 indicator objects, and send them to `GIBTIA_IndicatorProcessor_v2` for submission to the Sentinel Threat Intelligence blade.

| Playbook file                                       | Group-IB collection         | Indicator types                        | Notes                                                                                                                                                                                                                                                     |
| --------------------------------------------------- | --------------------------- | -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `azuredeploy-GIBTIA_IOC_Primary_Updated.json`       | `ioc/primary`               | IPv4, domain, URL, MD5, SHA-1, SHA-256 | Broadest IOC feed — curated cross-source indicators with threat/malware attribution. Supports `IOCTypeFilter` parameter (`all`/`network`/`file`). Optional `UseRiskScoreAsConfidence` and `FixedConfidence` parameters control the STIX confidence field. |
| `azuredeploy-GIBTIA_Malware_cnc.json`               | `malware/cnc`               | IPv4, domain, URL                      | Command-and-control infrastructure for tracked malware families.                                                                                                                                                                                          |
| `azuredeploy-GIBTIA_Malware_config.json`            | `malware/config`            | IPv4, domain, URL                      | Extracted C2 addresses from parsed malware configurations.                                                                                                                                                                                                |
| `azuredeploy-GIBTIA_Attacks_phishing.json`          | `attacks/phishing_group`    | IPv4, domain, URL                      | Phishing kit hosting infrastructure.                                                                                                                                                                                                                      |
| `azuredeploy-GIBTIA_Attacks_phishing_kit.json`      | `attacks/phishing_kit`      | Email addresses                        | Operator email addresses extracted from phishing kit archives.                                                                                                                                                                                            |
| `azuredeploy-GIBTIA_Attacks_ddos.json`              | `attacks/ddos`              | IPv4                                   | DDoS botnet C2 nodes and target IPs.                                                                                                                                                                                                                      |
| `azuredeploy-GIBTIA_Attacks_deface.json`            | `attacks/deface`            | URL                                    | Defaced page URLs — confirm if your domains are affected.                                                                                                                                                                                                 |
| `azuredeploy-GIBTIA_Suspicious_ip_tor_node.json`    | `suspicious_ip/tor_node`    | IPv4                                   | Known Tor exit nodes.                                                                                                                                                                                                                                     |
| `azuredeploy-GIBTIA_Suspicious_ip_open_proxy.json`  | `suspicious_ip/open_proxy`  | IPv4                                   | Publicly listed open proxy servers.                                                                                                                                                                                                                       |
| `azuredeploy-GIBTIA_Suspicious_ip_socks_proxy.json` | `suspicious_ip/socks_proxy` | IPv4                                   | Infected hosts running SOCKS proxy malware.                                                                                                                                                                                                               |
| `azuredeploy-GIBTIA_Suspicious_ip_scanner.json`     | `suspicious_ip/scanner`     | IPv4                                   | IPs actively scanning for vulnerabilities.                                                                                                                                                                                                                |
| `azuredeploy-GIBTIA_Suspicious_ip_vpn.json`         | `suspicious_ip/vpn`         | IPv4                                   | Commercial VPN exit nodes used for anonymisation.                                                                                                                                                                                                         |

---

### Context Intelligence Playbooks

These playbooks poll Group-IB TI intelligence collections on an hourly recurrence and write full structured records to dedicated Log Analytics custom tables. They do **not** write to the Threat Intelligence blade. Records contain rich context — threat actor profiles, malware analysis reports, CVE data, leak events — intended for analytics rules and analyst enrichment.

| Playbook file                                      | Group-IB collection           | Log Analytics table           | Content                                                                                                                                                                                                                                                                                                                                                          |
| -------------------------------------------------- | ----------------------------- | ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `azuredeploy-GIBTIA_APT_Threats.json`              | `apt/threat`                  | `GIBAPTThreat_CL`             | APT campaign reports with associated IOCs, sectors, and TTPs.                                                                                                                                                                                                                                                                                                    |
| `azuredeploy-GIBTIA_APT_ThreatActor.json`          | `apt/threat_actor`            | `GIBAPTThreatActor_CL`        | Nation-state and state-sponsored threat actor profiles (aliases, capabilities, targeted regions/sectors).                                                                                                                                                                                                                                                        |
| `azuredeploy-GIBTIA_HI_Threat.json`                | `hi/threat`                   | `GIBHIThreat_CL`              | Hacker Intel campaign and threat reports (non-APT cybercrime groups).                                                                                                                                                                                                                                                                                            |
| `azuredeploy-GIBTIA_HI_Threat_Actor.json`          | `hi/threat_actor`             | `GIBHIThreatActor_CL`         | Individual hacker and cybercrime group profiles.                                                                                                                                                                                                                                                                                                                 |
| `azuredeploy-GIBTIA_HI_Open_Threats.json`          | `hi/open_threats`             | `GIBHIOpenThreat_CL`          | Threat context for actively tracked open threats.                                                                                                                                                                                                                                                                                                                |
| `azuredeploy-GIBTIA_Malware_Targeted_Malware.json` | `malware/malware`             | `GIBMalwareReport_CL`         | Malware family intelligence: classification, capabilities, C2 infrastructure, associated threat actors.                                                                                                                                                                                                                                                          |
| `azuredeploy-GIBTIA_Compromised_account.json`      | `compromised/account_group`   | `GIBCompromisedAccount_CL`    | Leaked credential metadata (stealer logs, credential databases). Passwords are **masked** before ingestion — first 3 characters preserved, remainder replaced with `****` (e.g. `Password123` → `Pas****`). Defaults to **unique credentials** (`AccountFeedType=unique`); switch to `combolist` or `all`, and optionally set `ProbableCorporateAccessFilter=1`. |
| `azuredeploy-GIBTIA_Compromised_BreachedDB.json`   | `compromised/breacheddb`      | `GIBCompromisedBreachedDB_CL` | Breached-database records (leak name, authors, download links, per-subject `addInfo`). Passwords are **masked** as above (each entry in the password array). Defaults to only records that carry a password (`HasPasswordFilter=1`). Other identity fields (email, addInfo) are ingested unmasked.                                                               |
| `azuredeploy-GIBTIA_Compromised_SPD.json`          | `compromised/spd`             | `GIBCompromisedSPD_CL`        | Suspicious payment data — financial fraud indicators. (Replacing Mules collection)                                                                                                                                                                                                                                                                               |
| `azuredeploy-GIBTIA_Compromised_BankCard.json`     | `compromised/bank_card_group` | `GIBCompromisedBankCard_CL`   | Compromised bank-card records from underground markets, forums, and messaging platforms. Card number, expiry, owner, bank, source — grouped by card. **CVV is stripped before ingestion** (see note below).                                                                                                                                                      |
| `azuredeploy-GIBTIA_Compromised_MaskedCard.json`   | `compromised/masked_card`     | `GIBCompromisedMaskedCard_CL` | Partially-masked compromised bank-card records from the same sources. Use when full card data isn't available or needed for the use case. **CVV is stripped before ingestion** (see note below).                                                                                                                                                                 |
| `azuredeploy-GIBTIA_OSI_Vulnerability.json`        | `osi/vulnerability`           | `GIBOSIVulnerability_CL`      | CVE records enriched with CVSS score, exploitation status, darkweb mentions, and PoC availability.                                                                                                                                                                                                                                                               |
| `azuredeploy-GIBTIA_OSI_PublicLeak.json`           | `osi/public_leak`             | `GIBOSIPublicLeak_CL`         | Leaked data posted on Pastebin-style sites and file-sharing resources.                                                                                                                                                                                                                                                                                           |
| `azuredeploy-GIBTIA_OSI_GitLeak.json`              | `osi/git_repository`          | `GIBOSIGitRepository_CL`      | Sensitive data found in public code repositories (tokens, credentials, internal paths).                                                                                                                                                                                                                                                                          |

---

### Enrichment Playbooks

These playbooks are triggered by Sentinel incidents and add structured context as incident comments. They are not recurrence-based — they run in response to analyst activity or automation rules.

| Playbook file                          | Trigger                           | What it does                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| -------------------------------------- | --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `azuredeploy-GIBTIA_Enrich_WHOIS.json` | Sentinel incident created/updated | **Light enrichment** for any incident from any source. For each IP and domain entity: queries Group-IB WHOIS API for registration data and checks `ThreatIntelIndicators` for already-ingested Group-IB indicators. Intended to run on all new incidents automatically.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `azuredeploy-GIBTIA_Enrich_IOC.json`   | Sentinel incident created/updated | **Cross-collection IOC enrichment.** For each IP, domain, URL, or file-hash entity in the incident: (1) calls `/api/v2/user/granted_collections` once to discover which Group-IB collections this API key can read; (2) calls `/api/v2/search?q=<value>` per entity to find matches across all collections; (3) intersects the match list with the granted-collection set; (4) for each granted+matching collection, fetches the first 3 records via the collection-specific link. Posts a comment showing which collections have hits, how many, and the **full JSON record** of each fetched sample (one per line). Output is split across multiple incident comments when it would exceed Sentinel's 30,000-character comment limit ("part N of M"). The granted-collections gate ensures the playbook only fetches data the operator's account is actually entitled to. |
| `azuredeploy-GIBTIA_Score_IP.json`     | Sentinel incident created/updated | **Risk scoring** for IP entities. Batches all IPs from the incident into a single `POST /api/v2/scoring` call, and posts each IP's GIB risk score (0–100) back as an incident comment. Score is derived from multi-source TI tags weighted by recency, frequency, persistence, and severity.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |

---

## Authentication Model

All playbooks authenticate to Azure services using **Managed Identity** — no OAuth tokens, no client secrets, no manual re-authorization. Each Logic App resource is deployed with `"identity": {"type": "SystemAssigned"}`.

| Service                                  | Auth method                                        | Required role                  |
| ---------------------------------------- | -------------------------------------------------- | ------------------------------ |
| Log Analytics query (seqUpdate read)     | Managed Identity → ARM endpoint                    | Log Analytics Reader           |
| Log Analytics Data Collector API (write) | Workspace ID + Primary Key (in parameters)         | N/A — key-based                |
| Sentinel Threat Intelligence upload      | Managed Identity → azuresentinel connector         | Microsoft Sentinel Contributor |
| Group-IB TI API                          | HTTP Basic Auth (username + API key in parameters) | N/A — Group-IB-side credential |

---

## Incremental Polling Design

All collector playbooks use Group-IB's `seqUpdate` mechanism for reliable incremental polling:

1. On startup, the playbook reads the last saved `seqUpdate` from the `GIBCollectionTracking_CL` table, filtered by `CollectionName_s` (the same shared table is used for every collector, including `ioc/primary`).
2. On first run (table doesn't exist or is empty), the playbook calls Group-IB's `sequence_list` endpoint to convert the user-provided `StartDate` into a `seqUpdate` value.
3. The playbook enters an Until loop, fetching pages of up to `LimitPerPortion` records at a time.
4. After all pages are exhausted (API returns `count: 0`), the final `seqUpdate` is saved back to Log Analytics.
5. The next hourly run continues exactly from where the previous run stopped — no data gaps, no re-processing.

### Changing the polling frequency

The hourly schedule is set in each playbook's **Recurrence** trigger, not as a deployment
parameter or app setting. Change it per playbook in the Azure Portal — Logic app designer →
**Recurrence** → Frequency / Interval → Save (Standard: **Workflows** → pick the workflow →
Designer). It cannot be changed from Microsoft Sentinel; the Automation → Playbooks blade
does not expose the trigger.

Three caveats apply — a redeploy silently reverts a portal change, intervals shorter than an
hour cause deliberately skipped runs (the paging loop's timeout is one hour and the trigger
is capped at one concurrent run), and on Consumption the frequency is directly billable. Full
detail: [`USER_GUIDE.md` §4.10](USER_GUIDE.md) for Consumption,
[`USER_GUIDE_STANDARD.md` §7](USER_GUIDE_STANDARD.md) for Standard.

---

## STIX 2.1 Indicator Format

All indicators submitted to Sentinel Threat Intelligence are STIX 2.1 compliant, as required by the Sentinel Upload Indicators API. Each indicator object contains:

| Field                                 | Value                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`                                | `"indicator"`                                                                                                                                                                                                                                                                                                                                      |
| `spec_version`                        | `"2.1"`                                                                                                                                                                                                                                                                                                                                            |
| `id`                                  | `"indicator--"` + generated GUID                                                                                                                                                                                                                                                                                                                   |
| `created` / `modified` / `valid_from` | `dateFirstSeen` from Group-IB record                                                                                                                                                                                                                                                                                                               |
| `valid_until`                         | `dateFirstSeen + evaluation.TTL days` when present; falls back to `dateFirstSeen + 90 days` otherwise (IOC Primary only; other collectors use the 90-day default unconditionally)                                                                                                                                                                  |
| `pattern`                             | STIX pattern, e.g. `[ipv4-addr:value = '1.2.3.4']`                                                                                                                                                                                                                                                                                                 |
| `pattern_type`                        | `"stix"`                                                                                                                                                                                                                                                                                                                                           |
| `confidence`                          | 0–100. IOC Primary: `(admiralty_reliability + admiralty_credibility) / 2` derived from `evaluation.admiraltyCode` (when `UseAdmiraltyConfidence=true` and code is parseable), else per-entry `riskScore` (when `UseRiskScoreAsConfidence=true`), else `FixedConfidence` (when not `-1`), else field omitted. Other collectors: hardcoded fallback. |
| `indicator_types`                     | `["malicious-activity"]`                                                                                                                                                                                                                                                                                                                           |
| `labels`                              | `["Group-IB TI", "<collection-name>"]` plus, when present on the record (IOC Primary only): `"admiralty:<code>"`, `"credibility:<n>"`, `"reliability:<n>"`, `"risk-score:<n>"`. `risk-score` is always surfaced when present regardless of confidence mode.                                                                                        |
| `object_marking_refs`                 | STIX 2.1 TLP marking-definition ID derived from `evaluation.TLP` (RED/AMBER/GREEN/WHITE\|CLEAR). Empty array when no TLP. IOC Primary only.                                                                                                                                                                                                        |

---

## Custom Log Tables Reference

| Table                         | Tracking table             | Collection name (in tracking)                                |
| ----------------------------- | -------------------------- | ------------------------------------------------------------ |
| `ThreatIntelIndicators`       | `GIBCollectionTracking_CL` | `ioc/primary`, `malware/cnc`, `attacks/phishing_group`, etc. |
| `GIBAPTThreat_CL`             | `GIBCollectionTracking_CL` | `apt/threat`                                                 |
| `GIBAPTThreatActor_CL`        | `GIBCollectionTracking_CL` | `apt/threat_actor`                                           |
| `GIBHIThreat_CL`              | `GIBCollectionTracking_CL` | `hi/threat`                                                  |
| `GIBHIThreatActor_CL`         | `GIBCollectionTracking_CL` | `hi/threat_actor`                                            |
| `GIBHIOpenThreat_CL`          | `GIBCollectionTracking_CL` | `hi/open_threats`                                            |
| `GIBMalwareReport_CL`         | `GIBCollectionTracking_CL` | `malware/malware`                                            |
| `GIBCompromisedAccount_CL`    | `GIBCollectionTracking_CL` | `compromised/account_group`                                  |
| `GIBCompromisedBreachedDB_CL` | `GIBCollectionTracking_CL` | `compromised/breacheddb`                                     |
| `GIBCompromisedSPD_CL`        | `GIBCollectionTracking_CL` | `compromised/spd`                                            |
| `GIBCompromisedBankCard_CL`   | `GIBCollectionTracking_CL` | `compromised/bank_card_group`                                |
| `GIBCompromisedMaskedCard_CL` | `GIBCollectionTracking_CL` | `compromised/masked_card`                                    |
| `GIBOSIVulnerability_CL`      | `GIBCollectionTracking_CL` | `osi/vulnerability`                                          |
| `GIBOSIPublicLeak_CL`         | `GIBCollectionTracking_CL` | `osi/public_leak`                                            |
| `GIBOSIGitRepository_CL`      | `GIBCollectionTracking_CL` | `osi/git_repository`                                         |

---

## Requirements

| Requirement              | Details                                                                                                           |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| Azure subscription       | Active subscription with resource group containing a Sentinel workspace                                           |
| Microsoft Sentinel       | Enabled on a Log Analytics workspace                                                                              |
| Group-IB TI subscription | Active Group-IB TI portal access with API key; access to specific collections depends on your subscription tier   |
| Logic App region         | Must be in a region supported by the `azuresentinel` managed API and `azureloganalyticsdatacollector` managed API |
| Permissions              | Ability to create Logic App resources, assign IAM roles on the workspace, and deploy ARM templates                |
