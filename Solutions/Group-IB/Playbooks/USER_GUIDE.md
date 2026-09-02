# Group-IB Threat Intelligence — Microsoft Sentinel Integration: User Guide

This guide covers the **Consumption** deployment package — one Logic App per playbook, deployed via individual ARM templates. For the **Standard** deployment package (all playbooks in a single WS1 Logic App), see [USER_GUIDE_STANDARD.md](USER_GUIDE_STANDARD.md).

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Before You Begin — Collect Required Values](#3-before-you-begin--collect-required-values)
4. [Installation — Step-by-Step](#4-installation--step-by-step)
   - 4.1 [Deploy the Indicator Processor (adapter)](#41-deploy-the-indicator-processor-adapter)
   - 4.2 [Assign the Managed Identity role — Indicator Processor](#42-assign-the-managed-identity-role--indicator-processor)
   - 4.3 [Deploy the IOC Primary Collector](#43-deploy-the-ioc-primary-collector)
   - 4.4 [Authorize API connections — IOC Primary Collector](#44-authorize-api-connections--ioc-primary-collector)
   - 4.5 [Run first test and verify](#45-run-first-test-and-verify)
   - 4.6 [Deploy additional indicator collectors](#46-deploy-additional-indicator-collectors)
   - 4.7 [Deploy context intelligence playbooks](#47-deploy-context-intelligence-playbooks)
   - 4.8 [Deploy enrichment playbooks](#48-deploy-enrichment-playbooks)
   - 4.9 [Assign roles for enrichment playbooks](#49-assign-roles-for-enrichment-playbooks)
   - 4.10 [Production configuration](#410-production-configuration)
5. [Verifying the Integration](#5-verifying-the-integration)
6. [Use Case Guide](#6-use-case-guide)
7. [Analytics Rules — Examples and Setup](#7-analytics-rules--examples-and-setup)
8. [Automation with Enrichment Playbooks](#8-automation-with-enrichment-playbooks)
9. [Troubleshooting](#9-troubleshooting)
10. [Maintenance and Operations](#10-maintenance-and-operations)

---

## 1. Overview

This integration delivers Group-IB threat intelligence into Microsoft Sentinel through two mechanisms:

**Threat Indicators** flow into the Sentinel Threat Intelligence blade (`ThreatIntelIndicators` table) as STIX 2.1 objects. Sentinel automatically cross-references these indicators against your security log data (firewall, DNS, proxy, endpoint, identity) and creates alerts when matches are found.

**Context Intelligence** lands in dedicated Log Analytics custom tables (`GIBAPTThreat_CL`, `GIBOSIVulnerability_CL`, etc.). These tables contain full intelligence records — threat actor profiles, campaign reports, malware family analysis, CVE enrichment, leaked credential metadata — and can power analytics rules, workbooks, and enrichment playbooks.

You choose which feeds to enable based on your Group-IB TI subscription and security priorities. Each feed is an independent Logic App that can be enabled or disabled at any time.

---

## 2. Prerequisites

### Azure requirements

- An active Azure subscription.
- A **resource group** containing a deployed **Microsoft Sentinel** workspace (Sentinel is the add-on to Log Analytics — both must be active).
- Permission to deploy ARM templates (Contributor or Owner on the resource group).
- Permission to assign IAM roles on the Log Analytics workspace (User Access Administrator or Owner).

### Group-IB TI requirements

- An active Group-IB TI portal account at `tap.group-ib.com`.
- Your **Group-IB login email** (used as the API username).
- A **Group-IB personal API key** — generate it in the Group-IB portal: top-right menu → **Profile** → **API keys** → **Generate**.
- Access to the specific Group-IB TI collections you wish to ingest. Not all collections are available to all subscription tiers. Contact your Group-IB account manager if a collection returns 403.

### Tool requirements

- Access to the **Azure Portal** at `portal.azure.com`.
- Basic familiarity with Azure resource groups and Log Analytics. No PowerShell or CLI expertise is required — the entire installation is done through the Azure Portal UI.

---

## 3. Before You Begin — Collect Required Values

Gather the following values before starting the deployment. You will need them multiple times during setup.

| Value                     | Where to find it                                                                                                                                                         | Example                 |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------- |
| **Subscription ID**       | Azure Portal → top search bar → "Subscriptions" → click your subscription → copy the Subscription ID field                                                               | `a1b2c3d4-...`          |
| **Resource Group name**   | The resource group where your Sentinel workspace lives                                                                                                                   | `rg-sentinel-prod`      |
| **Workspace name**        | Log Analytics workspace → Overview page → the resource name at the top                                                                                                   | `la-sentinel-workspace` |
| **Workspace ID (GUID)**   | Log Analytics workspace → Overview → "Workspace ID" field                                                                                                                | `b5c6d7e8-...`          |
| **Workspace primary key** | See instructions below                                                                                                                                                   | (long base64 string)    |
| **Group-IB login email**  | Your Group-IB TI portal login                                                                                                                                            | `analyst@company.com`   |
| **Group-IB API key**      | Group-IB portal → Profile → API keys                                                                                                                                     | (alphanumeric string)   |
| **StartDate**             | Choose a date in `YYYY-MM-DD` format to begin the initial data pull. Use a recent date (e.g. 30 days ago) for testing, or a further-back date for a historical backfill. | `2025-01-01`            |

### Getting the workspace primary key

The primary key is used only by the Log Analytics Data Collector connection (to write tracking records). It is not used for the MSI-authenticated queries.

**Method 1 — Azure Cloud Shell (recommended):**

1. In the Azure Portal, click the **Cloud Shell** icon (`>_`) in the top navigation bar.
2. If prompted, select **Bash** and create a storage account if this is your first time.
3. Run the following command (replace the placeholders with your values):

```bash
az monitor log-analytics workspace get-shared-keys \
  --resource-group YOUR_RESOURCE_GROUP_NAME \
  --workspace-name YOUR_WORKSPACE_NAME
```

4. Copy the `primarySharedKey` value from the output.

**Method 2 — Azure Portal (older UI):**

Log Analytics workspace → left menu → **Agents** → expand **Log Analytics agent instructions** → the Primary key is listed there.

---

## 4. Installation — Step-by-Step

### 4.1 Deploy the Indicator Processor (adapter)

The `GIBTIA_IndicatorProcessor_v2` playbook is the central receiving point for all indicator data. **It must be deployed before any indicator collector.** It uses a batch trigger — when a collector sends 100 indicators or after a 5-minute timeout (whichever comes first), this playbook wakes up and submits the batch to Sentinel's Threat Intelligence API.

**Steps:**

1. In the Azure Portal, type **"Deploy a custom template"** in the search bar and select the result.

2. Click **"Build your own template in the editor"**.

3. Open the file `Playbooks/azuredeploy-GIBTIA_IndicatorProcessor_v2.json` from this repository. Select all the content and copy it.

4. In the Azure Portal editor, delete any existing content and paste the copied JSON. Click **Save**.

5. Fill in the deployment parameters:

   | Parameter          | Value                                                                                         |
   | ------------------ | --------------------------------------------------------------------------------------------- |
   | **Subscription**   | Your Azure subscription                                                                       |
   | **Resource group** | The resource group where Sentinel lives                                                       |
   | `PlaybookName`     | Leave as default: `GIBTIA_IndicatorProcessor_v2`                                              |
   | `UserName`         | Your Azure AD email address (informational — used as the display name for the API connection) |
   | `WorkspaceId`      | Your Log Analytics workspace ID (GUID)                                                        |

6. Click **Review + create**, then **Create**. Wait for the deployment to complete (typically 30–60 seconds).

7. After deployment, navigate to the newly created Logic App resource (`GIBTIA_IndicatorProcessor_v2`).

8. In the left menu, under **Settings**, click **Identity**. Verify that **System assigned** status shows **On**. If it shows Off, toggle it On and click Save. This must be enabled before the role assignment in the next step.

> **Note on the API connection:** The `azuresentinel` connection deployed with this playbook uses Managed Identity authentication. If you navigate to the API connection resource and click "Edit API connection", you will see a message that the connection can only be used with a managed identity — this is correct and expected. Do not attempt to authorize it manually.

---

### 4.2 Assign the Managed Identity role — Indicator Processor

The Logic App needs permission to upload indicators to Sentinel. This is done via an IAM role assignment.

1. Go to your **Log Analytics workspace** resource (or navigate to it via Microsoft Sentinel → Settings → Workspace settings).

2. In the left menu, click **Access control (IAM)**.

3. Click **+ Add** → **Add role assignment**.

4. In the **Role** tab, search for and select **Microsoft Sentinel Contributor**. Click **Next**.

5. In the **Members** tab:
   - **Assign access to**: select **Managed identity**
   - Click **+ Select members**
   - In the **Managed identity** dropdown, select **Logic app**
   - Search for `GIBTIA_IndicatorProcessor_v2`
   - Select it and click **Select**

6. Click **Review + assign**, then **Review + assign** again to confirm.

> **Important:** Role assignments propagate in Azure in up to 2–5 minutes. If you test immediately and see authorization errors, wait a few minutes and try again.

---

### 4.3 Deploy the IOC Primary Collector

The `GIBTIA_IOC_Primary_Updated` playbook polls the `ioc/primary/updated` Group-IB TI feed — the most comprehensive indicator feed, covering IPs, domains, URLs, and file hashes with threat/malware attribution.

**Steps:**

1. Azure Portal → **"Deploy a custom template"** → **"Build your own template in the editor"**.

2. Paste the content of `Playbooks/azuredeploy-GIBTIA_IOC_Primary_Updated.json`. Click **Save**.

3. Fill in parameters:

   | Parameter                        | Value                            | Notes                                                                      |
   | -------------------------------- | -------------------------------- | -------------------------------------------------------------------------- |
   | `PlaybookName`                   | `GIBTIA_IOC_Primary_Updated`     | Leave as default                                                           |
   | `UserName`                       | Your Azure AD email              | Informational only                                                         |
   | `GIBUsername`                    | Your Group-IB portal login email | e.g. `analyst@company.com`                                                 |
   | `GIBApiKey`                      | Your Group-IB personal API key   | Stored as securestring in the Logic App                                    |
   | `StartDate`                      | `YYYY-MM-DD`                     | Starting date for initial data pull                                        |
   | `LimitPerPortion`                | `10`                             | **Use 10 for initial testing.** Each template's `maxValue` is its collection's API maximum, and the request is additionally clamped at runtime, so you cannot set a breaking value. See §4.6. |
   | `IOCTypeFilter`                  | `all`                            | Or `network` (IP/domain/URL only) or `file` (hashes only)                 |
   | `UseRiskScoreAsConfidence`       | `false`                          | Set to `true` to use each IOC's Group-IB risk score as the STIX confidence value. Each indicator type (IP, domain, URL, hash) carries its own risk score. |
   | `FixedConfidence`                | `-1`                             | Set to a value between 0–100 to apply a fixed confidence to all indicators. Used when neither `UseAdmiraltyConfidence` nor `UseRiskScoreAsConfidence` supplies a value. Leave at `-1` to omit confidence entirely. |
   | `UseAdmiraltyConfidence`       | `false`                          | Set to `true` to derive STIX confidence by parsing `evaluation.admiraltyCode` (e.g. `"C3"`) via the Admiralty Code translation tables (`reliability: A=100, B=80, C=60, D=40, E=20, F=0`; `credibility: 1=100, 2=80, 3=60, 4=40, 5=20, 6=0`) and emitting `(reliability + credibility) / 2`. **Highest precedence** — falls through to `UseRiskScoreAsConfidence` / `FixedConfidence` when `admiraltyCode` is missing, wrong length, or contains a letter/digit outside the lookup table. The other evaluation fields (`admiraltyCode`, `credibility`, `reliability`, `TLP`, `TTL`) are always surfaced when present: `admiraltyCode`/`credibility`/`reliability` appear in the `Tags` column as `admiralty:C3`/`credibility:60`/`reliability:60`, the per-entry/item-level `riskScore` appears as `risk-score:<n>` regardless of confidence mode, `TLP` becomes `object_marking_refs`, and `TTL` (in days) drives `ValidUntil` instead of the 90-day fallback. |
   | `IndicatorProcessorPlaybookName` | `GIBTIA_IndicatorProcessor_v2`   | Must match the adapter name exactly                                        |
   | `WorkspaceId`                    | Your workspace GUID              | For MSI query calls                                                        |
   | `WorkspaceName`                  | Your workspace name              | For constructing the ARM query URL                                         |

4. Click **Review + create** → **Create**.

---

### 4.4 Authorize API connections — IOC Primary Collector

After deployment, two API connections must be configured. Find them in the same resource group.

\*\*`azureloganalyticsdatacollector-GIBTIA_IOC_Primary_Updated`\*\*

This connection writes the seqUpdate tracking record after each run.

1. Navigate to the resource group → find `azureloganalyticsdatacollector-GIBTIA_IOC_Primary_Updated` → click it.
2. In the left menu, click **Edit API connection**.
3. Enter your **Workspace ID** and **Workspace Key** in the respective fields.
4. Click **Save**.

> The collector also queries Log Analytics for its last `seqUpdate` on each run, but that call is signed directly with the Logic App's Managed Identity — there is no `azuremonitorlogs` API connection to authorize. The MSI needs a workspace role instead; see the next subsection.

#### Assign the Managed Identity role — IOC Primary Collector

The collector reads its last `seqUpdate` from Log Analytics by signing an HTTPS query with the Logic App's Managed Identity. Without a read role on the workspace this step returns **403** on every run, and the playbook silently falls back to the first-run path (re-pulling from `StartDate` and never advancing).

1. `GIBTIA_IOC_Primary_Updated` Logic App → left menu → **Identity** → verify **System assigned** is **On**.
2. Go to your **Log Analytics workspace** → **Access control (IAM)** → **+ Add role assignment**.
3. Role: **Log Analytics Reader** *(or **Microsoft Sentinel Contributor** if you prefer a single role on this Logic App — Contributor includes the read permission)*.
4. Members → **Managed identity** → search for `GIBTIA_IOC_Primary_Updated` → select it.
5. Click **Review + assign**.

Allow ~1 minute for the role assignment to propagate before triggering a run.

#### Enable the playbooks

1. Navigate to `GIBTIA_IndicatorProcessor_v2` → **Overview** → click **Enable**.
2. Navigate to `GIBTIA_IOC_Primary_Updated` → **Overview** → click **Enable**.

Both Logic Apps deploy in **Disabled** state. They will not run until explicitly enabled.

---

### 4.5 Run first test and verify

Before changing `LimitPerPortion` to production values, verify the pipeline works end to end.

**Trigger a manual run:**

1. Go to `GIBTIA_IOC_Primary_Updated` → **Overview**.
2. Click **Run Trigger** → **Recurrence**.
3. Wait 1–2 minutes.

**Check the collector run:**

4. Still on the Logic App overview, click **Run history** in the left menu.
5. Click the most recent run to open it.
6. Expand each step to verify:
   - `Query_Last_SeqUpdate`: will likely show as **Failed** with a 400-range error on the very first run — this is normal and expected. The shared `GIBCollectionTracking_CL` table does not exist yet, and the playbook is designed to handle this by falling through to the first-run path.
   - `Condition_First_Run` → `HTTP_Get_SequenceList`: should show **Succeeded** with a 200 response.
   - `Until` loop steps: should show **Succeeded**.
   - `Save_tracking_record`: should show **Succeeded**.

**Check that indicators reached the adapter:**

7. Navigate to `GIBTIA_IndicatorProcessor_v2` → **Run history**.
8. A run should appear. The adapter fires when 100 messages are batched (or after a 5-minute timeout). With `LimitPerPortion = 10`, you may only see the timeout-triggered run after 5 minutes.

**Verify indicators in Log Analytics:**

9. Go to your Sentinel workspace → left menu → **Logs**.
10. Run:

```kusto
ThreatIntelIndicators
| where SourceSystem contains "Group-IB"
| order by TimeGenerated desc
| take 20
```

You should see rows with STIX patterns like `[ipv4-addr:value = '...']`, `[domain-name:value = '...']`, etc.

**Verify the seqUpdate was saved:**

```kusto
GIBCollectionTracking_CL
| where CollectionName_s == "ioc/primary"
| order by TimeGenerated desc
| take 5
```

Expected: one row with `CollectionName_s == "ioc/primary"` and a numeric `SeqUpdate_d` value.

**Verify in the Sentinel Threat Intelligence blade:**

11. In Sentinel → left menu under **Threat management** → **Threat intelligence**.
12. You should see the newly ingested indicators. Note: the blade can lag behind the table by several minutes.

---

### 4.6 Deploy additional indicator collectors

Each additional indicator collector follows the same deployment pattern. Deploy them one at a time, or in parallel — they are independent of each other and only depend on the adapter (`GIBTIA_IndicatorProcessor_v2`) being available.

**Per-collector steps:**

1. Azure Portal → **"Deploy a custom template"** → **"Build your own template in the editor"**.
2. Paste the playbook JSON → Save.
3. Fill parameters: `GIBUsername`, `GIBApiKey`, `StartDate`, `WorkspaceId`, `WorkspaceName`. Leave `LimitPerPortion` at 10 for initial testing. Set `IndicatorProcessorPlaybookName` to `GIBTIA_IndicatorProcessor_v2`.
4. Review + create → Create.
5. Authorize `azureloganalyticsdatacollector-<PlaybookName>` connection (enter Workspace ID + Key).
6. **Assign the Managed Identity role.** Same procedure as the "Assign the Managed Identity role — IOC Primary Collector" subsection in §4.4, but selecting **this** collector's Logic App as the member. Role: **Log Analytics Reader**. Required so the collector can query its last `seqUpdate` — without it the playbook re-pulls from `StartDate` on every run.
7. Logic App → Overview → **Enable**.

**Available additional indicator collectors:**

| File | Collection | Indicator types | Max `LimitPerPortion` |
|---|---|---|---|
| `azuredeploy-GIBTIA_Malware_cnc.json` | `malware/cnc` | IP, domain, URL | **1000** |
| `azuredeploy-GIBTIA_Malware_config.json` | `malware/config` | IP, domain, URL | **100** |
| `azuredeploy-GIBTIA_Attacks_phishing.json` | `attacks/phishing_group` | IP, domain, URL | **1000** |
| `azuredeploy-GIBTIA_Attacks_phishing_kit.json` | `attacks/phishing_kit` | Email | **1000** |
| `azuredeploy-GIBTIA_Attacks_ddos.json` | `attacks/ddos` | IP | **5000** |
| `azuredeploy-GIBTIA_Attacks_deface.json` | `attacks/deface` | URL | **100** |
| `azuredeploy-GIBTIA_Compromised_BankCard.json` | `compromised/bank_card_group` | (context — no indicators) | **500** |
| `azuredeploy-GIBTIA_Compromised_MaskedCard.json` | `compromised/masked_card` | (context — no indicators) | **500** |
| `azuredeploy-GIBTIA_Suspicious_ip_tor_node.json` | `suspicious_ip/tor_node` | IP | **100** |
| `azuredeploy-GIBTIA_Suspicious_ip_open_proxy.json` | `suspicious_ip/open_proxy` | IP | **5000** |
| `azuredeploy-GIBTIA_Suspicious_ip_socks_proxy.json` | `suspicious_ip/socks_proxy` | IP | **5000** |
| `azuredeploy-GIBTIA_Suspicious_ip_scanner.json` | `suspicious_ip/scanner` | IP | **5000** |
| `azuredeploy-GIBTIA_Suspicious_ip_vpn.json` | `suspicious_ip/vpn` | IP | **100** |

---

### 4.7 Deploy context intelligence playbooks

Context playbooks write full intelligence records to Log Analytics custom tables. They do not interact with the adapter or the Threat Intelligence blade.

**Per-playbook steps:**

1. Azure Portal → **"Deploy a custom template"** → **"Build your own template in the editor"**.
2. Paste the playbook JSON → Save.
3. Fill parameters:

   | Parameter         | Value                                        |
   | ----------------- | -------------------------------------------- |
   | `PlaybookName`    | Leave as default                             |
   | `UserName`        | Your Azure AD email                          |
   | `GIBUsername`     | Group-IB portal login                        |
   | `GIBApiKey`       | Group-IB API key                             |
   | `StartDate`       | `YYYY-MM-DD`                                 |
   | `LimitPerPortion` | `10` for testing, max per collection (see table above) |
   | `WorkspaceId`     | Workspace GUID                               |
   | `WorkspaceName`   | Workspace name                               |

4. Review + create → Create.
5. Authorize `azureloganalyticsdatacollector-<PlaybookName>` connection (enter Workspace ID + Key).
6. **Assign the Managed Identity role.** Same procedure as the "Assign the Managed Identity role — IOC Primary Collector" subsection in §4.4, but selecting this context collector's Logic App as the member. Role: **Log Analytics Reader**. Required so the collector can query its last `seqUpdate` — without it the playbook re-pulls from `StartDate` on every run.
7. Logic App → Overview → **Enable**.

**Available context playbooks:**

| File | Collection | Custom table | Max `LimitPerPortion` |
|---|---|---|---|
| `azuredeploy-GIBTIA_APT_Threats.json` | `apt/threat` | `GIBAPTThreat_CL` | **10** |
| `azuredeploy-GIBTIA_APT_ThreatActor.json` | `apt/threat_actor` | `GIBAPTThreatActor_CL` | **100** |
| `azuredeploy-GIBTIA_HI_Threat.json` | `hi/threat` | `GIBHIThreat_CL` | **10** |
| `azuredeploy-GIBTIA_HI_Threat_Actor.json` | `hi/threat_actor` | `GIBHIThreatActor_CL` | **100** |
| `azuredeploy-GIBTIA_HI_Open_Threats.json` | `hi/open_threats` | `GIBHIOpenThreat_CL` | **100** |
| `azuredeploy-GIBTIA_Malware_Targeted_Malware.json` | `malware/malware` | `GIBMalwareReport_CL` | **100** |
| `azuredeploy-GIBTIA_Compromised_account.json` | `compromised/account_group` | `GIBCompromisedAccount_CL` | **500** |
| `azuredeploy-GIBTIA_Compromised_BreachedDB.json` | `compromised/breacheddb` | `GIBCompromisedBreachedDB_CL` | **100** |
| `azuredeploy-GIBTIA_Compromised_SPD.json` | `compromised/spd` | `GIBCompromisedSPD_CL` | **500** |
| `azuredeploy-GIBTIA_OSI_Vulnerability.json` | `osi/vulnerability` | `GIBOSIVulnerability_CL` | **200** |
| `azuredeploy-GIBTIA_OSI_PublicLeak.json` | `osi/public_leak` | `GIBOSIPublicLeak_CL` | **5** (size-driven, not the API's 100 — records are full text dumps) |
| `azuredeploy-GIBTIA_OSI_GitLeak.json` | `osi/git_repository` | `GIBOSIGitRepository_CL` | **100** |

---

### 4.8 Deploy enrichment playbooks

Two enrichment playbooks are available, each serving a different role:

- **`GIBTIA_Enrich_WHOIS`** — Light enrichment intended for any incident from any source (EDR, firewall, identity, etc.). Queries Group-IB WHOIS for each IP and domain entity, and checks `ThreatIntelIndicators` for already-ingested Group-IB indicators. No live `ioc/primary` API call.
- **`GIBTIA_Enrich_IOC`** — Cross-collection enrichment for any incident. For each IP, domain, URL, or file-hash entity it calls `/api/v2/user/granted_collections` once, then `/api/v2/search` per entity to find matches across all Group-IB collections the API key is entitled to, fetches the first 3 records of each granted+matching collection, and posts the **full JSON record** of each (one per line) as an incident comment. Output is split into multiple comments ("part N of M") when it would exceed Sentinel's 30,000-character comment limit. Makes no Log Analytics calls.

Both playbooks are triggered by Sentinel incident webhook events and write their findings as incident comments.

**Deploying `GIBTIA_Enrich_WHOIS`:**

1. Azure Portal → **"Deploy a custom template"** → **"Build your own template in the editor"**.
2. Paste `Playbooks/azuredeploy-GIBTIA_Enrich_WHOIS.json` → Save.
3. Fill parameters:

   | Parameter       | Value                        |
   | --------------- | ---------------------------- |
   | `PlaybookName`  | `GIBTIA_Enrich_WHOIS`        |
   | `UserName`      | Your Azure AD email          |
   | `GIBUsername`   | Group-IB portal login        |
   | `GIBApiKey`     | Group-IB API key             |
   | `WorkspaceName` | Log Analytics workspace name |

4. Review + create → Create.
5. Authorize the `azuresentinel-GIBTIA_Enrich_WHOIS` API connection:
   - Navigate to the connection resource → **Edit API connection** → **Authorize** → sign in with your Azure AD account → **Save**.
6. Enable the Logic App.

**Deploying `GIBTIA_Enrich_IOC`:**

1. Azure Portal → **"Deploy a custom template"** → **"Build your own template in the editor"**.
2. Paste `Playbooks/azuredeploy-GIBTIA_Enrich_IOC.json` → Save.
3. Fill parameters:

   | Parameter       | Value                             |
   | --------------- | --------------------------------- |
   | `PlaybookName`  | `GIBTIA_Enrich_IOC`       |
   | `UserName`      | Your Azure AD email               |
   | `GIBUsername`   | Group-IB portal login             |
   | `GIBApiKey`     | Group-IB API key                  |

4. Review + create → Create.
5. Authorize the `azuresentinel-GIBTIA_Enrich_IOC` API connection:
   - Navigate to the connection resource → **Edit API connection** → **Authorize** → sign in with your Azure AD account → **Save**.
6. Enable the Logic App.

**Deploying `GIBTIA_Score_IP`:** *(optional — IP risk-scoring enrichment)*

1. Azure Portal → **"Deploy a custom template"** → **"Build your own template in the editor"**.
2. Paste `Playbooks/azuredeploy-GIBTIA_Score_IP.json` → Save.
3. Fill parameters (`PlaybookName` = `GIBTIA_Score_IP`, `UserName` = your Azure AD email, `GIBUsername` / `GIBApiKey` = Group-IB credentials). No `WorkspaceName` — this playbook makes no Log Analytics calls.
4. Review + create → Create.
5. Authorize the `azuresentinel-GIBTIA_Score_IP` API connection (as above).
6. Enable the Logic App.

This playbook collects the IP entities from an incident, batches them into a single `POST /api/v2/scoring` call, and posts each IP's Group-IB risk score (0–100) back as an incident comment.

---

### 4.9 Assign roles for enrichment playbooks

**`GIBTIA_Enrich_WHOIS` only** uses Managed Identity to query the `ThreatIntelIndicators` table in Log Analytics, so it needs **Log Analytics Reader** on the workspace. (`GIBTIA_Enrich_IOC` and `GIBTIA_Score_IP` make no Log Analytics calls — they query Group-IB directly — so they do **not** need this role.)

1. Log Analytics workspace → **Access control (IAM)** → **+ Add role assignment**.
2. Role: **Log Analytics Reader**.
3. Members: Managed identity → select **Logic app** → search for `GIBTIA_Enrich_WHOIS` → select.
4. Review + assign.

**All enrichment playbooks** use Managed Identity to post comments to Sentinel incidents via the `azuresentinel` connector. Each needs **Microsoft Sentinel Contributor** on the workspace:

1. Log Analytics workspace → **Access control (IAM)** → **+ Add role assignment**.
2. Role: **Microsoft Sentinel Contributor**.
3. Members: Managed identity → select **Logic app** → search for `GIBTIA_Enrich_WHOIS` → select.
4. Review + assign.
5. Repeat for `GIBTIA_Enrich_IOC` and (if deployed) `GIBTIA_Score_IP`.

---

### 4.10 Production configuration

Once testing is verified, update the collectors to production throughput settings:

1. For each enabled collector Logic App:
   - Logic App → left menu → **Parameters** (or redeploy the ARM template with updated values)
   - Set `LimitPerPortion` to `100` for most collections (safe default). For high-volume collections (`attacks/ddos`, `suspicious_ip/open_proxy`, `suspicious_ip/socks_proxy`, `suspicious_ip/scanner`) you may raise it up to the collection's documented maximum. See the per-collection limits tables in §4.6 and §4.7.
   - For `GIBTIA_IOC_Primary_Updated`, ensure `IOCTypeFilter` is set to `all` unless you specifically want to limit indicator types

2. Verify the hourly recurrence is running. Each collector runs every hour automatically once enabled.

3. To confirm incremental operation is working after the second scheduled run:

```kusto
GIBCollectionTracking_CL
| order by TimeGenerated desc
| take 20
```

The `SeqUpdate_d` value for each collection should be higher on each successive run.

#### Changing the collection frequency

The schedule is **not** a deployment parameter — it lives in each playbook's **Recurrence**
trigger, set to every 1 hour. Change it per playbook in the Azure Portal:

1. Open the collector's Logic App → left menu → **Logic app designer** (or **Code view**).
2. Click the **Recurrence** trigger.
3. Set **Frequency** (Minute / Hour / Day / Week) and **Interval**.
4. **Save.** It takes effect on the next scheduled run — no redeploy needed.

This is per playbook. There are 26 collectors, and changing one does not change the others.

> **Note:** you cannot change this from Microsoft Sentinel. The Sentinel **Automation →
> Playbooks** blade lists the Logic Apps and lets you attach them to automation rules, but it
> does not expose the recurrence trigger. It is a Logic Apps setting.

Three things to know before you change it:

- **A redeploy silently reverts it.** The trigger lives inside the ARM template
  (`resources[].properties.definition`), so redeploying `azuredeploy-GIBTIA_<Name>.json`
  overwrites your change and restores the hourly schedule. Nothing warns you. If a
  non-default schedule matters to you, edit the `frequency` / `interval` values in the
  template and deploy that, rather than clicking in the portal.
- **Below one hour, some runs will be skipped — on purpose.** Each collector's paging loop
  has a one-hour timeout, and the trigger is capped at one concurrent run. At an hourly
  interval those line up exactly. If you set, say, 15 minutes, then whenever a run is still
  paging — during the initial backfill, or catching up after an outage — the triggers that
  fire in the meantime are **skipped rather than queued**. That cap is deliberate: two
  concurrent runs share one `GIBCollectionTracking_CL` cursor and can rewind it, causing
  duplicate ingestion. Gaps in run history under a short interval are expected, not a fault.
  Intervals **longer** than an hour have no such effect.
- **Frequency is directly billable on the Consumption plan.** Every run costs actions even
  when the API returns an empty page, so a 15-minute interval is roughly 4× the action count
  for the same amount of data.

Finally, do not confuse this with the **analytics rule** schedule in
[§7](#7-analytics-rules--examples-and-setup). That controls how often Sentinel matches your
logs against the indicators; the recurrence above controls how often we pull new data from
Group-IB. They are independent clocks.

---

## 5. Verifying the Integration

### Overall health check queries

**Check all active collections and their last seqUpdate:**

```kusto
GIBCollectionTracking_CL
| summarize LastRun = max(TimeGenerated), LastSeqUpdate = max(SeqUpdate_d) by CollectionName_s
| order by LastRun desc
```

**Check IOC primary tracking specifically:**

```kusto
GIBCollectionTracking_CL
| where CollectionName_s == "ioc/primary"
| summarize LastRun = max(TimeGenerated), LastSeqUpdate = max(SeqUpdate_d) by CollectionName_s
```

**Count indicators ingested by type over the last 24 hours:**

```kusto
ThreatIntelIndicators
| where TimeGenerated > ago(24h)
| where SourceSystem contains "Group-IB"
| extend IndicatorType = case(
    Pattern has "ipv4-addr", "IPv4",
    Pattern has "domain-name", "Domain",
    Pattern has "url", "URL",
    Pattern has "file:hashes", "File Hash",
    "Other"
  )
| summarize Count = count() by IndicatorType
| order by Count desc
```

**Check indicator collector playbook for errors:**

```kusto
AzureDiagnostics
| where ResourceType == "WORKFLOWS"
| where resource_workflowName_s has "GIBTIA"
| where status_s == "Failed"
| project TimeGenerated, resource_workflowName_s, status_s, error_message_s
| order by TimeGenerated desc
| take 20
```

### Surfacing risk score (and other Group-IB tags) as columns

`ThreatIntelIndicators` is a Microsoft-managed table — its schema is fixed, so custom columns such as `RiskScore` **cannot** be added to it directly. Group-IB risk score is instead written into the `Tags` collection as `risk-score:<n>` (always present when the source record has a `riskScore`, independent of the `UseRiskScoreAsConfidence` setting). The same applies to `admiralty:<code>`, `credibility:<n>`, and `reliability:<n>`.

To work with these as if they were real columns, create a **saved function** that parses them out of `Tags`. Querying the function then behaves exactly like querying a table that has typed `RiskScore` / `Credibility` / `Reliability` columns — sortable, filterable, and chartable.

1. In the Defender / Sentinel portal open **Logs**.
2. Paste the query below and run it to confirm it parses correctly.
3. Click **Save → Save as function**. Set **Function name** to `GIB_ThreatIntelIndicators` and a **Legacy category** of e.g. `Group-IB`, then **Save**.

```kusto
ThreatIntelIndicators
| extend RiskScore   = toint(extract(@"risk-score:(\d+)", 1, tostring(Tags)))
| extend Credibility = toint(extract(@"credibility:(\d+)", 1, tostring(Tags)))
| extend Reliability = toint(extract(@"reliability:(\d+)", 1, tostring(Tags)))
| extend AdmiraltyCode = extract(@"admiralty:([A-F][1-6])", 1, tostring(Tags))
```

`extract` returns an empty value when the tag is absent, so indicators without a risk score simply get a null `RiskScore` rather than failing. Once saved, use it anywhere you'd use the raw table:

```kusto
GIB_ThreatIntelIndicators
| where SourceSystem contains "Group-IB"
| where RiskScore >= 80
| project TimeGenerated, ObservableValue, RiskScore, Credibility, Reliability, AdmiraltyCode, Confidence, Tags
| order by RiskScore desc
```

The function applies retroactively to already-ingested indicators — no re-ingestion needed. It is read-only and additive; it does not alter the underlying table or the indicator pipeline.

> **Note:** The `Tags` are only populated once the `labels`-array fix is deployed. Before that fix, the upload API rejected the `labels` property (HTTP 200 with a per-record `errors[]` body), so `Tags` — and therefore `RiskScore` — would be empty. If `RiskScore` comes back blank for everything, confirm you are running the current `GIBTIA_IOC_Primary_Updated` and that recent indicators show non-empty `Tags`.

---

## 6. Use Case Guide

> **Portal navigation note — Defender portal migration.** Microsoft is consolidating Sentinel into the **Microsoft Defender portal** (`security.microsoft.com`). The Azure portal Sentinel blade still works but is the legacy experience and is being deprecated. Both portals hit the same backend (same incidents, same analytics rules, same automation rules); only the URL and menu paths differ. Where this guide says "Sentinel → *Section*", you'll find the same content in either:
>
> | Azure portal (`portal.azure.com`) | Defender portal (`security.microsoft.com`) |
> |---|---|
> | Microsoft Sentinel → workspace → **Analytics** | **Microsoft Sentinel → Configuration → Analytics** |
> | Microsoft Sentinel → workspace → **Automation** | **Microsoft Sentinel → Configuration → Automation** |
> | Microsoft Sentinel → workspace → **Threat intelligence** | **Threat intelligence → Intel management** |
> | Microsoft Sentinel → workspace → **Incidents** | **Investigation & response → Incidents & alerts → Incidents** |
> | Microsoft Sentinel → workspace → **Hunting** | **Threat hunting → Hunting** |
> | Microsoft Sentinel → workspace → **Settings → Settings tab** | **Microsoft Sentinel → Configuration → Settings** |
>
> Use whichever you prefer. New customers should generally use the Defender portal; existing customers can migrate at their own pace.

### 6.0 Quick start — get your first GIB-driven incident

If you've completed §4 and §5 and want the fastest path from "indicators are flowing" to "Sentinel alerts on a real match," follow this sequence:

1. **Enable a TI Map rule template** (§6.1 below — pick one that matches a data connector you already have, e.g. Azure AD Sign-In logs).
2. **Wait one rule-run cycle** (default: 1 hour). The TI Map rule joins recent log entries against `ThreatIntelIndicators`; if anything matches, a Sentinel incident is created with the matched indicator and the matching log entity attached.
3. **Set up the WHOIS enrichment automation rule** (§8.3) so every new incident automatically gets a GIB context comment.

After step 3, every incident that the TI Map rule creates will arrive in your analyst queue already annotated with WHOIS data and any cross-reference to existing GIB indicators. That's the full integration loop from feed → indicator → match → incident → enrichment, with zero manual analyst action between them.

### 6.1 Automated IOC Matching (TI Map rules)

**Scenario:** Your organization wants alerts when an IP address, domain, or URL from Group-IB's threat intelligence feeds appears in your network or security logs.

**How it works:** When indicators are in `ThreatIntelIndicators`, Sentinel's built-in **TI Map** analytics rules (available in the Analytics rule templates gallery) automatically cross-reference them against your data connectors (Defender for Endpoint, Azure Firewall, DNS logs, etc.).

**Step-by-step setup of one TI Map rule** (repeat for each one you want active):

1. Sentinel → **Analytics** → **Rule templates** tab (Defender portal: *Configuration → Analytics → Rule templates*).
2. Filter by **Data source: Threat Intelligence**, OR type `TI map` in the search box.
3. Pick a template that matches a data connector you actually have. Common starting picks:
   - `TI map IP entity to AzureActivity` — needs Azure Activity logs
   - `TI map IP entity to Sigin` — needs Azure AD Sign-In Logs
   - `TI map Domain entity to DnsEvents` — needs DNS data connector
   - `TI map File Hash entity to SecurityEvent` — needs Windows Security Events
   - `TI map URL entity to PaloAlto` (or Cisco / Fortinet / etc.) — needs the corresponding firewall connector
4. Click the template → **Create rule** → walk through the wizard:
   - **General** tab: leave the default name or rename for clarity; set severity (default Medium is fine).
   - **Set rule logic**: leave the default KQL (already wired up to query `ThreatIntelIndicators` joined against the log source). Entity mapping is pre-configured.
   - **Incident settings**: leave **Create incidents from alerts** on. Optionally enable **Alert grouping** if you expect high volume.
   - **Automated response**: skip for now — you'll attach the enrichment playbook via a *separate* automation rule in §8.3, which is more flexible than per-rule attachment.
   - **Review and create**.
5. The rule is now Active. It runs every 1 hour by default. After the first run, check Sentinel → **Incidents** for any matches.

> **No data connectors yet?** TI Map rules need real log data to match against. If your subscription is brand-new with no log sources, enable at least **Azure Activity** (free, instant) so you have *some* log stream to match against. For meaningful detection coverage you'll want sign-in logs (AAD), DNS, firewall, EDR, etc.

**Setup:**

1. In Sentinel → **Analytics** → **Rule templates** tab.
2. Search for "TI map" — you will find rules like:
   - `TI map IP entity to AzureActivity`
   - `TI map Domain entity to DNS Events`
   - `TI map URL entity to PaloAlto`
   - `TI map File Hash to Security Events`
3. Click a rule → **Create rule** → follow the wizard.
4. These rules run on a schedule (typically every hour) and create incidents when your logs contain entities matching active indicators.

**Priority feeds for this use case:** `ioc/primary`, `malware/cnc`, `attacks/phishing`.

---

### 6.2 APT and Targeted Threat Alerting

**Scenario:** Your organization operates in the Financial Services or Energy sector and wants to know immediately when a new APT campaign targeting your industry is reported.

**How it works:** The `GIBTIA_APT_Threats` playbook writes reports to `GIBAPTThreat_CL`. An analytics rule queries this table and fires when new reports mention your sector.

**Feeds required:** `GIBTIA_APT_Threats.json`, `GIBTIA_APT_ThreatActor.json`

See [Section 7.1](#71-apt-threat-report-alerting-by-sector) for the analytics rule.

---

### 6.3 Exploited Vulnerability Alerting

**Scenario:** Your security team needs to be notified in Sentinel when a new CVE is confirmed as being actively exploited, particularly CVEs with high CVSS scores.

**How it works:** The `GIBTIA_OSI_Vulnerability` playbook writes enriched CVE records to `GIBOSIVulnerability_CL` including `hasExploit_b` (boolean) and CVSS score. An analytics rule creates high-priority incidents when new exploited CVEs arrive.

**Feeds required:** `GIBTIA_OSI_Vulnerability.json`

See [Section 7.2](#72-newly-exploited-cve-alert) for the analytics rule.

---

### 6.4 Compromised Credential Detection

**Scenario:** Your SOC needs to detect when employee credentials (from your corporate domain) appear in credential leak databases.

**How it works:** The `GIBTIA_Compromised_account` playbook writes leak event metadata to `GIBCompromisedAccount_CL`, and `GIBTIA_Compromised_BreachedDB` writes breached-database records to `GIBCompromisedBreachedDB_CL`. Both **mask the leaked password** before ingestion (first 3 characters + `****`), so an analyst can identify and notify affected end users of the specific password without the plaintext ever landing in Sentinel. An analytics rule can alert on records mentioning your domain in the credential metadata.

**Feeds required:** `GIBTIA_Compromised_account.json`, `GIBTIA_Compromised_BreachedDB.json`

> **`HasPasswordFilter` (breacheddb only):** the `GIBTIA_Compromised_BreachedDB` template exposes a `HasPasswordFilter` parameter (`1` = default, only records that carry a leaked password; `0` = all breach records). Leave it at `1` for the credential-notification use case. Note: breacheddb records also carry other identity data (email, and an `addInfo` object with name/phone/address/etc.) which is ingested **unmasked** — only the password is masked.

> **`AccountFeedType` / `ProbableCorporateAccessFilter` (account_group only):** the `GIBTIA_Compromised_account` template exposes `AccountFeedType` (`unique` = default, only unique credentials; `combolist` = only combo-list credentials; `all` = every credential) and `ProbableCorporateAccessFilter` (`0` = default; `1` = return only probable corporate-access credentials). The default `unique` returns de-duplicated credentials — set `all` to ingest everything, or combine `ProbableCorporateAccessFilter=1` with any feed type to narrow to corporate access.

See [Section 7.3](#73-corporate-domain-in-leaked-credential-data) for the analytics rule.

---

### 6.5 Git Repository Secret Leak Detection

**Scenario:** Your application security team wants to know when source code or credentials from your organization are detected in public GitHub repositories.

**How it works:** `GIBTIA_OSI_GitLeak` writes records to `GIBOSIGitRepository_CL`. These records include repository URLs and matched content summaries. An analytics rule can alert on any new records (or filter by keyword).

**Feeds required:** `GIBTIA_OSI_GitLeak.json`

See [Section 7.4](#74-new-git-repository-leak-detection) for the analytics rule.

---

### 6.6 Incident Enrichment

Two enrichment playbooks are available, designed to complement each other:

#### WHOIS enrichment — all incidents

**Scenario:** Any incident created in Sentinel — from EDR, firewall, identity protection, or any other source — automatically gets Group-IB WHOIS registration data and a TI indicator check added as a comment.

**How it works:** The `GIBTIA_Enrich_WHOIS` playbook is attached via a broad automation rule that fires on all new incidents. For each IP and domain entity it queries the Group-IB WHOIS API and the local `ThreatIntelIndicators` table (already-ingested Group-IB indicators). No live call is made to the `ioc/primary` feed — this is a fast, lightweight enrichment.

**Playbook:** `GIBTIA_Enrich_WHOIS.json`

#### Cross-collection IOC enrichment

**Scenario:** An incident contains IP, domain, URL, or file-hash entities and analysts want to know where those IOCs appear across the entire Group-IB dataset — which collections (malware C2, phishing, etc.) reference them, and the full record details — without leaving Sentinel.

**How it works:** The `GIBTIA_Enrich_IOC` playbook discovers the collections the API key is entitled to (`/api/v2/user/granted_collections`), then for each entity runs a global `/api/v2/search`, intersects the hits with the granted collections, and fetches the first 3 records of each matching collection. It posts the **full JSON record** of each fetched sample (one per line, grouped by collection) as an incident comment, splitting into multiple comments ("part N of M") when output exceeds Sentinel's 30,000-character limit. It makes no Log Analytics calls.

**Playbook:** `GIBTIA_Enrich_IOC.json`

See [Section 8](#8-automation-with-enrichment-playbooks) for full setup of both rules.

---

### 6.7 Phishing Infrastructure Correlation

**Scenario:** A user reports a suspicious email. The SOC wants to check if the sending IP, URLs in the email, or domains are in Group-IB's phishing intelligence.

**How it works (manual):** Run ad-hoc KQL:

```kusto
// Check if a known IP appears in Group-IB TI
ThreatIntelIndicators
| where Pattern has "ipv4-addr:value"
    and Pattern has "203.0.113.45"    // replace with the IP in question
| where ValidUntil > now()
| project TimeGenerated, Pattern, Labels, Confidence
```

```kusto
// Check if a domain appears in phishing feeds
ThreatIntelIndicators
| where Pattern has "domain-name:value"
    and Pattern has "suspicious-domain.example"
| where ValidUntil > now()
| project TimeGenerated, Pattern, Labels, Confidence, ValidUntil
```

**How it works (automated):** Combine with the `GIBTIA_Enrich_WHOIS` automation rule so every phishing-related incident automatically gets Group-IB context attached.

---

### 6.8 Malware C2 Blocking Support

**Scenario:** Your firewall or proxy team wants an export of active malware C2 indicators to feed into blocking lists.

**How it works:** Query `ThreatIntelIndicators` filtered by the `malware/cnc` label:

```kusto
ThreatIntelIndicators
| where Labels has "malware/cnc"
| where ValidUntil > now()
| extend IndicatorValue = extract(@"= '(.+?)'", 1, Pattern)
| project IndicatorValue, Pattern, Confidence, ValidUntil
| order by Confidence desc
```

This can be exported to CSV or integrated with Azure Firewall Policy, Defender for Endpoint indicators, or a SOAR platform.

---

### 6.9 TOR / Proxy Access Detection

**Scenario:** You want to alert when authenticated users in your environment are accessing corporate resources via Tor exit nodes or known anonymization proxies.

**How it works:** TI Map rules correlate `suspicious_ip/tor_node` and `suspicious_ip/open_proxy` indicators against Azure AD Sign-In logs and network logs automatically. For a focused custom rule, see [Section 7.5](#75-sign-in-from-tor-exit-node).

**Feeds required:** `GIBTIA_Suspicious_ip_tor_node.json`, `GIBTIA_Suspicious_ip_open_proxy.json`

---

## 7. Analytics Rules — Examples and Setup

> §7 covers **custom KQL analytics rules** for use cases that the built-in TI Map templates don't address — context-table queries (APT reports, vulnerabilities, leaked credentials) and bespoke join logic. For the simpler "match indicators against logs" pattern, the built-in TI Map rules in [§6.1](#61-automated-ioc-matching-ti-map-rules) are easier and require no KQL.

### How to create a Scheduled Analytics Rule in Sentinel

Navigation: Sentinel → **Analytics** (Azure portal) *or* **Microsoft Sentinel → Configuration → Analytics** (Defender portal).

1. Click **+ Create** → **Scheduled query rule**.
2. Fill in the **General** tab: name, description, severity, tactics (MITRE ATT&CK).
3. In the **Set rule logic** tab: paste the KQL query. Configure the **Query scheduling** (typically "Run every 1 hour", "Lookup data from the last 1 hour").
4. Configure **Entity mapping** to help Sentinel extract entities (IP, domain, file hash, account) from query results — this enables enrichment playbooks and investigation graph.
5. In the **Automated response** tab: optionally attach enrichment playbooks (or — more flexibly — leave empty and attach via a Sentinel automation rule per [§8.3](#83-setting-up-the-whois-enrichment-automation-rule)).
6. Click **Review + create** → **Save**.

---

### 7.1 APT Threat Report Alerting by Sector

Fires when a new APT threat report arrives mentioning sectors your organization cares about. Adjust the `sectors_s` values to match your industry.

```kusto
GIBAPTThreat_CL
| where TimeGenerated > ago(1h)
| where sectors_s has_any ("Finance", "Banking", "Financial Services",
                            "Energy", "Oil and Gas",
                            "Government", "Defense",
                            "Healthcare", "Pharmaceutical")
| project
    TimeGenerated,
    ReportTitle = title_s,
    Sectors = sectors_s,
    ThreatActor = threat_actor_s,
    Description = description_s,
    SeqUpdate = SeqUpdate_d
```

**Recommended settings:**

- Severity: **Medium**
- Run every: 1 hour
- Lookup data from: last 1 hour
- Tactics: `InitialAccess`, `Reconnaissance`

**Entity mapping:** None required (this creates a contextual alert, not an IOC match).

---

### 7.2 Newly Exploited CVE Alert

Fires when Group-IB records a CVE as having a known exploit and a CVSS score of 7 or higher. This typically means exploitation in the wild has been observed.

```kusto
GIBOSIVulnerability_CL
| where TimeGenerated > ago(1h)
| where hasExploit_b == true
| where mergedCvss_d >= 7.0
| project
    TimeGenerated,
    CVE = cveId_s,
    CVSS = mergedCvss_d,
    Title = title_s,
    AffectedSoftware = affectedSoftware_s,
    PublishedDate = publishedDate_s,
    HasPoC = hasPoc_b,
    DarkwebMentions = darkwebMentions_d
| order by CVSS desc, DarkwebMentions desc
```

**Recommended settings:**

- Severity: **High** (CVSS ≥ 9.0) — adjust using a `where` clause or create two rules with different thresholds
- Run every: 1 hour
- Lookup data from: last 1 hour
- Tactics: `Exploitation`

**Variant — Critical CVEs with darkweb activity:**

```kusto
GIBOSIVulnerability_CL
| where TimeGenerated > ago(1h)
| where hasExploit_b == true
| where mergedCvss_d >= 9.0
| where DarkwebMentions_d > 0
| project TimeGenerated, cveId_s, mergedCvss_d, title_s, affectedSoftware_s, darkwebMentions_d
```

---

### 7.3 Corporate Domain in Leaked Credential Data

Fires when new leaked credential records appear that reference your organization's email domain. Replace `@yourcompany.com` with your actual domain(s).

```kusto
GIBCompromisedAccount_CL
| where TimeGenerated > ago(1h)
| where login_s endswith "@yourcompany.com"
       or login_s endswith "@subsidiary.com"
| project
    TimeGenerated,
    Login = login_s,
    Domain = domain_s,
    Source = source_s,
    DateDetected = dateDetected_s,
    CNCDomain = cnc_domain_s,
    CNCIP = cnc_ip_s
```

**Recommended settings:**

- Severity: **High**
- Run every: 1 hour
- Lookup data from: last 1 hour
- Tactics: `CredentialAccess`, `InitialAccess`

**Entity mapping:**

- Account → `Login` field
- IP → `CNCIP` field

> **Note:** Passwords are **masked** by the collector before ingestion — the first 3 characters are preserved and the remainder replaced with `****` (e.g. `Password123` → `Pas****`; strings of 3 characters or fewer become `****`). This lets an analyst recognize *which* password was compromised for end-user notification without storing the plaintext in Sentinel. Masking is applied to `compromised/account_group` (scalar `password`) and `compromised/breacheddb` (each entry in the `password` array). The masked value lands in the `password_s` column.

---

### 7.4 New Git Repository Leak Detection

Fires when Group-IB detects sensitive content (tokens, credentials, internal hostnames) in a public code repository linked to your organization.

```kusto
GIBOSIGitRepository_CL
| where TimeGenerated > ago(1h)
| project
    TimeGenerated,
    RepositoryURL = repository_url_s,
    Author = author_s,
    FileName = file_name_s,
    Description = description_s,
    DatePublished = datePublished_s,
    ThreatLevel = threatLevel_s
```

**Recommended settings:**

- Severity: **High**
- Run every: 1 hour
- Lookup data from: last 1 hour
- Tactics: `Exfiltration`, `CredentialAccess`

**Tip:** If `GIBOSIGitRepository_CL` returns too many records (Group-IB monitors many organizations' keywords), filter by a specific keyword or domain:

```kusto
GIBOSIGitRepository_CL
| where TimeGenerated > ago(1h)
| where description_s has "yourcompany" or author_s has "yourcompany"
```

---

### 7.5 Sign-In from Tor Exit Node

Correlates Azure AD sign-in logs against Group-IB's Tor exit node indicator feed. Fires when any successful or failed sign-in originates from a known Tor node.

```kusto
let TorNodes = ThreatIntelIndicators
    | where Labels has "suspicious_ip/tor_node"
    | where ValidUntil > now()
    | extend TorIP = extract(@"= '(.+?)'", 1, Pattern)
    | where isnotempty(TorIP)
    | summarize by TorIP;
SigninLogs
| where TimeGenerated > ago(1h)
| where IPAddress in (TorNodes)
| project
    TimeGenerated,
    UserPrincipalName,
    IPAddress,
    AppDisplayName,
    ResultType,
    ResultDescription,
    Location,
    ConditionalAccessStatus
```

**Recommended settings:**

- Severity: **Medium** (High if `ResultType == 0`, i.e. successful sign-in)
- Run every: 1 hour
- Lookup data from: last 1 hour
- Tactics: `DefenseEvasion`, `InitialAccess`

**Entity mapping:**

- Account → `UserPrincipalName`
- IP → `IPAddress`

---

### 7.6 Network Connection to Active Malware C2

Detects outbound connections to known malware command-and-control infrastructure. Requires network logs in Sentinel (Azure Firewall, Palo Alto, Cisco ASA, or similar).

```kusto
let MalwareC2_IPs = ThreatIntelIndicators
    | where Labels has "malware/cnc"
    | where ValidUntil > now()
    | extend C2IP = extract(@"= '(.+?)'", 1, Pattern)
    | where Pattern has "ipv4-addr"
    | where isnotempty(C2IP)
    | summarize by C2IP;
let MalwareC2_Domains = ThreatIntelIndicators
    | where Labels has "malware/cnc"
    | where ValidUntil > now()
    | extend C2Domain = extract(@"= '(.+?)'", 1, Pattern)
    | where Pattern has "domain-name"
    | where isnotempty(C2Domain)
    | summarize by C2Domain;
// Example using Azure Firewall logs — adapt to your firewall schema
AZFWNetworkRule
| where TimeGenerated > ago(1h)
| where Action == "Allow"
| where DestinationIp in (MalwareC2_IPs)
       or DestinationFqdn in (MalwareC2_Domains)
| project
    TimeGenerated,
    SourceIp,
    DestinationIp,
    DestinationFqdn,
    DestinationPort,
    Protocol
```

**Recommended settings:**

- Severity: **High**
- Run every: 1 hour
- Lookup data from: last 1 hour
- Tactics: `CommandAndControl`

**Entity mapping:**

- IP → `SourceIp` (the infected host)
- IP → `DestinationIp`

---

### 7.7 File Hash Match — Endpoint Security Logs

Correlates file hashes observed on endpoints against Group-IB TI file indicators (from `ioc/primary` and `malware/targeted_malware`).

```kusto
let GIBFileHashes = ThreatIntelIndicators
    | where Labels has_any ("ioc/primary", "malware/targeted_malware")
    | where ValidUntil > now()
    | where Pattern has "file:hashes"
    | extend HashValue = extract(@"= '(.+?)'", 1, Pattern)
    | extend HashType = case(
        Pattern has "SHA-256", "SHA256",
        Pattern has "SHA-1", "SHA1",
        Pattern has "MD5", "MD5",
        "Unknown"
      )
    | where isnotempty(HashValue)
    | project HashValue, HashType, Labels, Confidence;
DeviceFileEvents
| where TimeGenerated > ago(1h)
| where ActionType == "FileCreated" or ActionType == "FileModified"
| extend NormHash = coalesce(SHA256, SHA1, MD5)
| where isnotempty(NormHash)
| join kind=inner (GIBFileHashes) on $left.NormHash == $right.HashValue
| project
    TimeGenerated,
    DeviceName,
    FileName,
    FolderPath,
    NormHash,
    HashType,
    GIBLabels = Labels,
    GIBConfidence = Confidence,
    InitiatingProcessAccountName
```

**Recommended settings:**

- Severity: **High**
- Run every: 1 hour
- Lookup data from: last 1 hour
- Tactics: `Execution`, `Persistence`

**Entity mapping:**

- Host → `DeviceName`
- FileHash → `NormHash`
- Account → `InitiatingProcessAccountName`

---

### 7.8 Phishing URL in Proxy or Browser Logs

Detects when users navigate to URLs matching Group-IB's phishing intelligence.

```kusto
let PhishingURLs = ThreatIntelIndicators
    | where Labels has "attacks/phishing_group"
    | where ValidUntil > now()
    | extend PhishURL = extract(@"= '(.+?)'", 1, Pattern)
    | where Pattern has "url:value"
    | where isnotempty(PhishURL)
    | summarize by PhishURL;
// Using Squid proxy logs as example — adapt to your schema
W3CIISLog
| where TimeGenerated > ago(1h)
| extend FullURL = strcat(csHost, csUriStem)
| where FullURL in (PhishingURLs)
| project TimeGenerated, cIP, csHost, csUriStem, csMethod, scStatus, csUserName
```

---

## 8. Automation with Enrichment Playbooks

Enrichment playbooks integrate with Sentinel's **Automation rules** to run automatically when incidents are created or updated. This section walks through the full setup.

### 8.1 Understanding automation rules vs. playbooks

In Sentinel, **automation rules** are lightweight condition/action configurations that can:

- Change an incident's severity, status, or owner
- Assign a tag
- **Run a playbook**

Automation rules are evaluated whenever an incident is created or updated. By attaching an enrichment playbook to an automation rule, you ensure every qualifying incident automatically gets Group-IB context added as a comment — without any analyst intervention.

### 8.2 Granting Sentinel permission to run playbooks

Before Sentinel can trigger a Logic App playbook, you must grant it permission.

Navigation:
- **Azure portal**: Sentinel → workspace → **Settings → Settings** tab → scroll to **Playbook permissions**.
- **Defender portal**: **Microsoft Sentinel → Configuration → Settings** → **Settings** tab → **Playbook permissions**.

Steps:

1. Click **Configure permissions**.
2. Find and check the resource group containing your enrichment playbooks (for the Standard package, this is the RG containing the `GIBTIA-Standard` Logic App).
3. Click **Apply**.

Alternatively, on the Logic App resource itself:

- Logic App → **Access control (IAM)** → **+ Add role assignment**
- Role: **Microsoft Sentinel Automation Contributor**
- Assign to: `Azure Security Insights` service principal (this is Sentinel's managed identity)

### 8.3 Setting up the WHOIS enrichment automation rule

This rule automatically runs `GIBTIA_Enrich_WHOIS` on every new incident — regardless of source. It is intentionally broad because the WHOIS enrichment is lightweight and provides value for any incident that contains IP or domain entities.

Navigation: Sentinel → **Automation** (Azure portal) *or* **Microsoft Sentinel → Configuration → Automation** (Defender portal).

1. **+ Create** → **Automation rule**.

2. Configure the rule:

   **Name:** `Group-IB TI — WHOIS Enrichment on New Incidents`

   **Trigger:** `When incident is created`

   **Conditions:**
   - Incident provider: `Microsoft Sentinel`

   > You may optionally add a severity condition (e.g., `High`, `Medium`) to skip enrichment on Informational incidents and reduce API calls, but this is not required.

3. **Actions:**
   - Click **+ Add action** → **Run playbook**
   - Select `GIBTIA_Enrich_WHOIS` from the dropdown

4. **Order:** `10`

5. Click **Apply**.

**Result:** Every new incident will have a WHOIS enrichment comment added within minutes. If the incident's IP or domain entities are already in `ThreatIntelIndicators`, their labels and confidence score will also appear. Comment format:

```
Group-IB TI — WHOIS & Indicator Enrichment

IP: 203.0.113.45
Group-IB TI: ["malicious-activity"] | confidence: 85
WHOIS: AS12345 | ISP: Example Hosting Ltd | Country: RU | Range: 203.0.113.0 – 203.0.113.255

Domain: malicious-example.com
Group-IB TI: Not in GIB ThreatIntelIndicators
WHOIS: registered 2024-11-01 | updated 2024-11-15 | zone: .com
```

### 8.4 Setting up manual enrichment via incident actions

Enrichment playbooks can also be run manually by analysts directly from an incident:

1. In Sentinel → **Incidents** → click an incident to open the details panel.
2. Click **View full details** → **Incident actions** (top right) → **Run playbook**.
3. Select `GIBTIA_Enrich_WHOIS` or `GIBTIA_Enrich_IOC` from the list.
4. Click **Run**.

This is useful for one-off enrichment or when the automation rule didn't trigger (e.g., for older incidents).

### 8.5 Setting up the cross-collection IOC enrichment rule

The `GIBTIA_Enrich_IOC` playbook searches each incident's IP / domain / URL / file-hash entities across all Group-IB collections the API key is entitled to, and posts the full records found in each matching collection as incident comment(s). It works for incidents from any source — it does not require the incident to come from a TI Map match — so you can scope it broadly or narrowly as you prefer.

Set it up as a second automation rule, running after the WHOIS rule:

1. Sentinel → **Automation** → **+ Create** → **Automation rule**.
2. Name: `Group-IB TI — IOC Primary Context Enrichment`
3. Trigger: `When incident is created`
4. Conditions: match this rule to the analytics rules that generate Group-IB TI indicator incidents in your environment. For example:
   - **Analytics rule name** `Contains` → `TI map` — matches the built-in Microsoft TI Map rules
   - Or use any other condition that identifies incidents sourced from Group-IB indicator matches in your setup

   > You can also attach this playbook manually from an incident's **Incident actions → Run playbook** menu on a case-by-case basis, without creating an automation rule at all.

5. Actions: **Run playbook** → `GIBTIA_Enrich_IOC`
6. Order: `20` (runs after the WHOIS rule)
7. Click **Apply**.

### 8.6 Chaining enrichment with triage automation

For a more complete automated workflow, combine Group-IB enrichment with Sentinel's other automation capabilities:

**Example — full automated triage chain:**

| Order | Automation rule | Action |
|---|---|---|
| 1 | Auto-assign new incidents | Owner: SOC Team / specific analyst |
| 10 | Group-IB WHOIS enrichment (all incidents) | Run `GIBTIA_Enrich_WHOIS` |
| 20 | Group-IB IOC full enrichment (TI Map incidents only) | Run `GIBTIA_Enrich_IOC` |
| 30 | Auto-close known false positives | Status: Closed, if specific rule name |
| 40 | Escalate confirmed C2 matches | Severity: High, add tag "C2 Traffic" |

Rules are evaluated in order for each incident event. If an earlier rule changes the incident status or severity, later rules can use those updated values as conditions.

### 8.7 Monitoring enrichment playbook runs

To verify enrichment playbooks are running correctly:

**Check playbook run history:**

Logic App → **Run history** — look for runs triggered by `Microsoft_Sentinel_incident` (the webhook trigger).

**Query playbook execution from Log Analytics:**

```kusto
AzureDiagnostics
| where ResourceType == "WORKFLOWS"
| where resource_workflowName_s in ("GIBTIA_Enrich_WHOIS", "GIBTIA_Enrich_IOC")
| where TimeGenerated > ago(24h)
| summarize Total = count(), Failed = countif(status_s == "Failed"), Succeeded = countif(status_s == "Succeeded")
    by resource_workflowName_s
```

**Check incidents with enrichment comments:**

```kusto
SecurityIncident
| where TimeGenerated > ago(24h)
| where Comments has "Group-IB TI"
| project TimeGenerated, IncidentName, Severity, Status, Comments
| order by TimeGenerated desc
```

### 8.8 Single-entity (on-demand) enrichment playbooks

The three enrichers above are **incident-triggered**: they enrich *every* matching entity in an incident. If an analyst wants to enrich just **one** IP (or domain / URL / file-hash), deploy the **single-entity** variants — these use the Sentinel **entity trigger** and are run by hand from the entity, not from the incident.

| Playbook | Base | Entity type it runs on |
|---|---|---|
| `GIBTIA_Score_IP_Single` | Score_IP | IP |
| `GIBTIA_Enrich_IOC_Single_IP` | Enrich_IOC | IP |
| `GIBTIA_Enrich_IOC_Single_Domain` | Enrich_IOC | Domain (DNS) |
| `GIBTIA_Enrich_IOC_Single_URL` | Enrich_IOC | URL |
| `GIBTIA_Enrich_IOC_Single_FileHash` | Enrich_IOC | File hash |
| `GIBTIA_Enrich_WHOIS_Single_IP` | Enrich_WHOIS | IP |
| `GIBTIA_Enrich_WHOIS_Single_Domain` | Enrich_WHOIS | Domain (DNS) |

Templates: `Playbooks/azuredeploy-GIBTIA_<name>.json`. **Deploy, authorize the `azuresentinel-<PlaybookName>` connection, assign roles, and enable them exactly like the bulk enrichers** ([§4.8](#48-deploy-enrichment-playbooks), [§4.9](#49-assign-roles-for-enrichment-playbooks)): **Microsoft Sentinel Contributor** on all seven, plus **Log Analytics Reader** on the two `Enrich_WHOIS_Single_*` (they query `ThreatIntelIndicators`; the two use the `WorkspaceName` parameter). Score_IP and IOC single variants need no Log Analytics role.

**How an analyst runs one:**

1. Open an incident → **Investigation graph** (or the entity side panel).
2. Right-click the entity (e.g. an IP) → **Run playbook**.
3. Pick the matching single-entity playbook (only playbooks whose entity type matches the selected entity appear).
4. The playbook enriches **just that one entity** and adds a comment to the incident.

**Important limitations:**

- **These cannot be attached to automation rules** — the entity trigger is manual-only (a Microsoft limitation). Use the bulk incident-triggered enrichers for automation.
- **The comment lands only when the entity is run from within an incident.** The entity trigger passes the incident's ARM id (`IncidentArmID`) only in incident context; if you launch a single-entity playbook from the standalone **Entity behavior** page (no incident), the enrichment still runs and its result is visible in the Logic App **Run history**, but there is no incident to comment on (the playbook skips the comment step).
- The `Enrich_IOC_Single_*` variants still split long output into multiple "part N of M" comments, so a single IOC that matches many collections won't hit Sentinel's 30,000-character comment limit.

---

## 9. Troubleshooting

### Query_Last_SeqUpdate fails on first run

**Symptom:** `Query_Last_SeqUpdate` step shows as Failed with a 400 or 404 error on the very first run.

**Cause:** The shared tracking table `GIBCollectionTracking_CL` does not exist yet — Log Analytics returns an error when you query a table that has never been written to.

**Resolution:** This is expected behavior. The playbook detects this failure and automatically follows the first-run path (calling `sequence_list` to get an initial seqUpdate). No action required.

---

### Upload_Indicators_V2 fails with 403 Forbidden

**Symptom:** The `GIBTIA_IndicatorProcessor_v2` adapter run shows a 403 error on the `Upload_Indicators_V2` step.

**Cause:** The Logic App's Managed Identity does not have `Microsoft Sentinel Contributor` on the workspace, or the role assignment has not propagated yet.

**Resolution:**

1. Go to the Logic App → **Identity** → copy the **Object (principal) ID**.
2. Go to the workspace → **Access control (IAM)** → **Role assignments** tab.
3. Verify that an entry exists for the object ID with role **Microsoft Sentinel Contributor**.
4. If not present, add the role assignment as per Step 4.2.
5. Wait 5 minutes for propagation and re-run.

**Note:** If you redeploy the Logic App (even the same template), Azure creates a **new** Managed Identity with a new object ID. The old role assignment no longer applies. Always check the Identity tab after redeployment and re-assign if needed.

---

### Single-entity enrichment fails with 403 AuthorizationFailed on the comment step

**Symptom:** An entity-triggered single-enrichment playbook (e.g. `GIBTIA_Enrich_IOC_Single_IP`, `GIBTIA_Score_IP_Single`, `GIBTIA_Enrich_WHOIS_Single_IP`) run shows a 403 on the `Add_comment_to_incident` step:

```
"code":"AuthorizationFailed","message":"The client '…' with object id '…' does not have authorization
to perform action 'Microsoft.SecurityInsights/incidents/comments/write' over scope '…/incidents/…/comments/…'"
```

**Cause:** The playbook's Managed Identity lacks **Microsoft Sentinel Contributor** on the workspace. Each single-entity playbook (see [§8.8](#88-single-entity-on-demand-enrichment-playbooks)) is a **separate Logic App with its own Managed Identity**, so each needs its **own** role assignment — assigning the role to the bulk enrichers does not cover them. A freshly deployed single-entity playbook simply hasn't been granted the role yet, or the assignment hasn't propagated (Sentinel RBAC takes 5–15 minutes). That the write reached the correct incident scope means the entity trigger passed the incident id correctly — only authorization is missing.

**Resolution:**

1. Logic App → **Identity** → copy the **Object (principal) ID** (it matches the `object id` in the error).
2. Workspace → **Access control (IAM)** → **+ Add role assignment** → **Microsoft Sentinel Contributor** → **Managed identity** → select this Logic App → **Review + assign**. (Or use the CLI below.)
3. Wait 5–15 minutes for propagation, then re-run the playbook on an entity from within an incident.

```bash
az role assignment create \
  --assignee-object-id <logic-app-MSI-object-id> \
  --assignee-principal-type ServicePrincipal \
  --role "Microsoft Sentinel Contributor" \
  --scope "/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.OperationalInsights/workspaces/<workspace>"
```

**Notes:**
- **Repeat this for every single-entity playbook you deploy** — each has its own Managed Identity. The two `GIBTIA_Enrich_WHOIS_Single_*` playbooks additionally need **Log Analytics Reader** (they query `ThreatIntelIndicators`), same as [§4.9](#49-assign-roles-for-enrichment-playbooks).
- `Microsoft Sentinel Responder` also grants `incidents/comments/write`, but use **Sentinel Contributor** for consistency with the rest of this guide.
- Redeploying the Logic App creates a **new** Managed Identity with a new object ID — re-assign the role afterward.

---

### Upload_Indicators_V2 fails with 404 Not Found

**Symptom:** 404 error on the upload step.

**Cause:** The `WorkspaceId` parameter passed to the adapter is incorrect.

**Resolution:** Verify the workspace GUID in Log Analytics → Overview → Workspace ID. Redeploy the adapter with the correct value.

---

### Adapter fails with "data.id is not of the form specified in the STIX standard"

**Symptom:** Adapter run fails with a STIX validation error.

**Cause:** Stale batch messages from a previous failed collector run with an older or broken payload format are queued for the adapter.

**Resolution:** Redeploy the adapter Logic App (this resets the batch trigger and clears queued messages). Then redeploy the collector. Re-run the collector manually.

---

### `azuremonitorlogs` connection shows authorization errors

**Symptom:** Context playbook fails with `Unauthorized` or `InvalidAuthenticationTokenTenant` on the `Query_Last_SeqUpdate` step.

**Cause:** These playbooks now use HTTP + Managed Identity (not the `azuremonitorlogs` OAuth connector) for the seqUpdate query. If you see this error, you may be running an older version of the playbook.

**Resolution:** Redeploy the playbook using the current ARM template from this repository. The current versions do not use `azuremonitorlogs` for seqUpdate queries.

---

### azureloganalyticsdatacollector connection shows as error

**Symptom:** The API connection resource shows a red error state, and the playbook fails on the `Save_tracking_record` step.

**Cause:** The Workspace ID and/or Workspace Key entered in the connection are incorrect, or the key has been rotated.

**Resolution:**

1. Log Analytics workspace → **Agents** page → copy the current Primary Key.
2. Navigate to the API connection resource → **Edit API connection** → re-enter the Workspace ID and Key → **Save**.

---

### No indicators appear in Threat Intelligence blade

**Symptom:** The adapter runs succeed, but no indicators appear in Sentinel → Threat Intelligence.

**Resolution steps:**

1. Query `ThreatIntelIndicators` directly in Log Analytics — the blade can lag by up to 15 minutes.
2. Check that the indicators' `ValidUntil` is in the future (expired indicators are not shown).
3. Verify the adapter's `WorkspaceId` parameter matches the workspace where Sentinel is deployed.
4. Check the adapter run details — look at the `Upload_Indicators_V2` step response body for any error messages from the Sentinel API.

---

### Until loop iterates on the same seqUpdate

**Symptom:** The collector's Until loop keeps iterating but `seqUpdate` never changes; the loop hits the 100-iteration limit.

**Cause:** The `Parse_Feed_Response` step is failing silently, or the API response has an unexpected structure.

**Resolution:** Open the failing run → expand the `Until` loop → check the `Parse_Feed_Response` step. If it is in the `Failed` path, examine the raw response from `Get_next_portion`. The response may contain an error message or an unexpected field structure. Check your Group-IB API credentials and collection access permissions.

---

## 10. Maintenance and Operations

### Rotating the Group-IB API key

Group-IB API keys may be rotated for security reasons. When you rotate the key in the Group-IB portal:

1. Update each Logic App that uses the key:
   - Logic App → left menu → **Parameters** → find `GIBApiKey` → update the value.
   - Or redeploy the ARM template with the new key value.
2. The key is stored as a securestring parameter inside each Logic App. It is not visible in the portal after saving.

### Rotating the Log Analytics workspace key

If you rotate the workspace primary key:

1. Get the new key: Cloud Shell → `az monitor log-analytics workspace get-shared-keys ...`
2. Update each `azureloganalyticsdatacollector-*` API connection:
   - Navigate to the connection → **Edit API connection** → enter new key → **Save**.

### Adjusting LimitPerPortion

The recommended steady-state value is **100** for most collections. This is safe across all feeds and keeps Logic App action costs low. For collections with a higher published limit you can increase the value up to the documented maximum — but never exceed it or the API will return an error.

| Collection type | Recommended | Maximum |
|---|---|---|
| `apt/threat`, `hi/threat` | 10 | **10** |
| `osi/vulnerability` | 100 | **200** |
| `compromised/account_group`, `compromised/spd`, `compromised/bank_card_group`, `compromised/masked_card` | 100 | **500** |
| `compromised/breacheddb` | 100 | **100** |
| `malware/cnc`, `attacks/phishing_group`, `attacks/phishing_kit` | 100 | **1000** |
| `attacks/ddos`, `suspicious_ip/open_proxy`, `suspicious_ip/socks_proxy`, `suspicious_ip/scanner` | 100 | **5000** |
| All others | 100 | **100** |

If you are seeing playbook runs approach the 1-hour timeout, reduce `LimitPerPortion` rather than raising it — the bottleneck is usually downstream processing (foreach loop, SendToBatch), not the API call itself.

If you want to backfill historical data faster (e.g., you set `StartDate` far in the past):

- Temporarily raise `LimitPerPortion` to the collection's maximum.
- Run manually multiple times until the seqUpdate catches up to today.
- Reduce back to `100` for steady-state operation.

### Monitoring Logic App execution costs

Logic Apps in Azure are billed per action execution. Each playbook run consumes actions (each HTTP call, foreach iteration, and condition check counts). For cost monitoring:

1. Azure Portal → **Cost Management** → **Cost analysis** → filter by resource type `Microsoft.Logic/workflows`.
2. Filter by resource name prefix `GIBTIA` to see integration-specific costs.

For high-volume collections such as `suspicious_ip/open_proxy` or `attacks/ddos`, raising `LimitPerPortion` above 100 will increase action executions proportionally. The default of `100` provides a predictable cost baseline across all collections.

### Disabling a feed temporarily

To pause a specific feed without losing its progress:

1. Logic App → **Overview** → click **Disable**.
2. The seqUpdate last saved to `GIBCollectionTracking_CL` is preserved.
3. When you re-enable, the playbook resumes from the last saved seqUpdate with no data gaps.

### Viewing indicator coverage in Sentinel

To see a summary of active Group-IB TI coverage across your Sentinel workspace:

```kusto
ThreatIntelIndicators
| where ValidUntil > now()
| where SourceSystem contains "Group-IB"
| extend Collection = tostring(parse_json(tostring(Labels))[1])
| extend IndicatorType = case(
    Pattern has "ipv4-addr", "IPv4",
    Pattern has "domain-name", "Domain",
    Pattern has "url:value", "URL",
    Pattern has "file:hashes.'SHA-256'", "SHA-256",
    Pattern has "file:hashes.'SHA-1'", "SHA-1",
    Pattern has "file:hashes.'MD5'", "MD5",
    "Other"
  )
| summarize ActiveIndicators = count() by Collection, IndicatorType
| order by ActiveIndicators desc
```

This gives you a breakdown of how many active (non-expired) indicators are currently loaded per collection and type.
