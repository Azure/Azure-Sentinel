# Group-IB Threat Intelligence — Microsoft Sentinel Integration: Standard Logic Apps User Guide

This guide covers the **Standard Logic Apps** deployment package in `Playbooks/Standard/`. For the **Consumption** deployment (one Logic App per playbook, ARM-template flow), see [USER_GUIDE.md](USER_GUIDE.md) instead.

## Table of Contents

- [1. Overview](#1-overview)
- [2. Standard vs. Consumption — which to choose](#2-standard-vs-consumption--which-to-choose)
- [3. Prerequisites](#3-prerequisites)
- [4. Collect required values](#4-collect-required-values)
- [5. Installation — Step by Step](#5-installation--step-by-step)
  - [5.1 Deploy infrastructure (`infrastructure-arm.json`)](#51-deploy-infrastructure-infrastructure-armjson)
  - [5.2 Assign Managed Identity roles](#52-assign-managed-identity-roles)
  - [5.3 Deploy the workflows](#53-deploy-the-workflows)
  - [5.4 Bind the two managed API connections via the Designer](#54-bind-the-two-managed-api-connections-via-the-designer)
  - [5.5 First test run and verification](#55-first-test-run-and-verification)
  - [5.6 Production configuration](#56-production-configuration)
  - [5.7 Reconcile connection access policies (redeploy only)](#57-reconcile-connection-access-policies-redeploy-only)
- [6. Operating the Standard Logic App](#6-operating-the-standard-logic-app)
- [7. Per-workflow tuning](#7-per-workflow-tuning)
- [8. Verifying the Integration, Use Cases and Analytics Rules](#8-verifying-the-integration-use-cases-and-analytics-rules)
- [9. Troubleshooting](#9-troubleshooting)
- [10. Clean reinstall — wipe and start over](#10-clean-reinstall--wipe-and-start-over)
- [A. Full workflow catalog](#a-full-workflow-catalog)

---

## 1. Overview

The Standard package packs **all 29 workflows** into a **single Standard Logic App** running on a `WorkflowStandard` (WS1) App Service plan. One App Service plan, one Storage account, one Logic App, one shared Managed Identity, two managed API connections — and 29 workflows that share them.

```
+--------------------------------------------------+
|  Standard Logic App  (single Microsoft.Web/sites)|
|  + System-assigned Managed Identity              |
|                                                  |
|   workflows/                                     |
|     GIBTIA_IndicatorProcessor_v2/  (Batch)       |
|     GIBTIA_IOC_Primary_Updated/    (Recurrence)  |
|     GIBTIA_Malware_cnc/            (Recurrence)  |
|     GIBTIA_APT_Threats/            (Recurrence)  |
|     ...                                          |
|     GIBTIA_Enrich_WHOIS/           (Webhook)     |
|     GIBTIA_Enrich_IOC/             (Webhook)     |
|     GIBTIA_Score_IP/               (Webhook)     |
+--------------------------------------------------+
            |                          |
            v                          v
  azuresentinel-1              azureloganalyticsdatacollector-1
  (MI auth)                    (MI auth)
            |                          |
            v                          v
   Microsoft Sentinel TI       Log Analytics custom tables
   (ThreatIntelIndicators)     (GIB*_CL)
```

The 29 workflows break down as:

| Category | Count | Examples |
|---|---|---|
| **Adapter** | 1 | `GIBTIA_IndicatorProcessor_v2` — Batch trigger; uploads STIX indicators to Sentinel TI |
| **Indicator collectors** | 12 | `GIBTIA_IOC_Primary_Updated`, `GIBTIA_Malware_cnc`, `GIBTIA_Attacks_phishing`, `GIBTIA_Suspicious_ip_*` (5), … — hourly recurrence, transform records into STIX 2.1 indicators, batch-send to the adapter |
| **Context collectors** | 14 | `GIBTIA_APT_Threats`, `GIBTIA_OSI_Vulnerability`, `GIBTIA_HI_*`, `GIBTIA_Compromised_BankCard`, `GIBTIA_Compromised_BreachedDB`, … — hourly recurrence, write raw records to Log Analytics custom tables |
| **Enrichment playbooks** | 3 | `GIBTIA_Enrich_WHOIS`, `GIBTIA_Enrich_IOC`, `GIBTIA_Score_IP` — triggered by Sentinel incident webhook, post enrichment as incident comments |

> **Note on `GIBTIA_Score_IP`**: this enrichment playbook ships in the Standard package and also has a Consumption ARM template equivalent (`Playbooks/GIBTIA_Score_IP/azuredeploy.json`).

See [§A. Full workflow catalog](#a-full-workflow-catalog) at the bottom of this guide for the complete list with collection slugs and destination tables.

`GIBTIA_IndicatorProcessor_v2` is the **adapter** — every indicator collector batches indicators to it, and it uploads them to Sentinel TI via the `azuresentinel` connector. The adapter must exist before any collector runs (in Standard this is automatic — they ship together).

---

## 2. Standard vs. Consumption — which to choose

| Criterion                            | Standard                                               | Consumption                                 |
| ------------------------------------ | ------------------------------------------------------ | ------------------------------------------- |
| Resources to manage                  | 1 Logic App + 1 plan + 1 storage account               | 30 Logic Apps                               |
| IAM (Managed Identity role)          | **1 assignment** on the shared MSI                     | 30 assignments (one per Logic App)          |
| Workflow count                       | 30 (includes `GIBTIA_Score_IP`, `GIBTIA_Compromised_BreachedDB`)   | 30 (`Score_IP` now shipped as `GIBTIA_Score_IP/azuredeploy.json`)                |
| Cost model                           | Fixed (App Service plan, even when idle)               | Per-action billing                          |
| Predictability under high IOC volume | More predictable — no surprise per-action spend        | Variable — bills scale with execution count |
| Deployment cadence                   | Single zip deploy / VS Code push                       | 30 separate ARM template deploys            |
| Per-playbook tuning                  | Edit `workflow.json`, redeploy the affected workflow   | Redeploy the affected ARM template          |
| Designer experience                  | All workflows in one place (left-nav of the Logic App) | Each in its own Logic App                   |
| Stateful execution history           | First-class, per workflow                              | Per Logic App                               |

Choose **Standard** when you plan to enable most of the playbooks, want a single point of administration, or need predictable monthly cost. Choose **Consumption** when you intend to enable only a few playbooks or want strict per-action billing.

---

## 3. Prerequisites

### Azure

- Active subscription with permission to create resources in the target resource group.
- Microsoft Sentinel workspace on a Log Analytics workspace.
- Permission to assign IAM roles on the Log Analytics workspace (**User Access Administrator** or **Owner**).

### Group-IB TI

- Portal credentials: username (email) + API key.

### Tools

- A modern web browser for the Azure Portal.
- One of the following to push workflows into the Logic App:
  - **VS Code** with the [**Azure Logic Apps (Standard) extension**](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurelogicapps) — recommended; designer and one-click deploy.
  - **Azure CLI** (`az` ≥ 2.50) with the `webapp` and `logicapp` modules — works headlessly.
- Optional: `jq` / `zip` if you choose the CLI path.

---

## 4. Collect required values

You will need these before starting:

| Value                 | Where to find it                                                                                                                    |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Subscription ID       | Azure Portal → **Subscriptions**                                                                                                    |
| Resource Group name   | Where your Sentinel workspace lives                                                                                                 |
| Workspace name        | Log Analytics workspace → Overview → top of page                                                                                    |
| Workspace ID (GUID)   | Log Analytics workspace → Overview → **Workspace ID**                                                                               |
| Workspace primary key | Cloud Shell → `az monitor log-analytics workspace get-shared-keys --resource-group <rg> --workspace-name <ws>` → `primarySharedKey` |
| GIB Username          | Group-IB TI portal login                                                                                                            |
| GIB API key           | Group-IB TI portal → personal settings → API token                                                                                  |
| `StartDate`           | First-run cursor, format `YYYY-MM-DD`. Used by every collector to convert into an initial `seqUpdate`.                              |

> **Note on the workspace key.** You do **not** need one. The Standard Logic App writes the seqUpdate tracking record and context records via the `azureloganalyticsdatacollector` connection using the Logic App's **Managed Identity** — which is why §3 requires the `Log Analytics Contributor` role. Earlier versions collected a `WorkspaceKey` deployment parameter; it was never referenced by any workflow and has been removed rather than left to sit in app settings in cleartext.

---

## 5. Installation — Step by Step

> **Before you start.** Check which scenario applies to you:
>
> | Scenario | Where to start | Required sections |
> |---|---|---|
> | **First-time install on a fresh RG** | §5.1 | §5.1 → §5.3 Path A → §5.5 → §5.6 |
> | **Redeploy onto a previously-used RG** | §10 (clean-reinstall recipe) | §10 → §5.1 → §5.3 Path A → §5.7 → §5.5 → §5.6 |
> | **Upgrade in place** (running Logic App, ship new `workflow.json` only) | `MAINTAINER_NOTES.md` §5 "Standard partial redeploy" — uses `az logicapp deployment source config-zip` with `-x "connections.json"` so the running app's bind survives | — |
>
> ### Recommended path: `post-deploy.sh` (the out-of-the-box flow)
>
> After §5.1 (ARM deploy), one script does everything in §5.2, §5.3, the partial §5.4 (pauses for two Designer-bind clicks), and a final restart:
>
> ```bash
> cd Playbooks/Standard
> ./post-deploy.sh <resource-group> <logic-app-name> <workspace-name>
> ```
>
> Total operator time on a familiar deploy: ~5 minutes. Full instructions in [§5.3 Path A](#path-a--post-deploysh-recommended--the-out-of-the-box-path).
>
> The fully manual flow (§5.2 by Portal clicks → §5.3 Path B or C → §5.4 by Portal clicks) is documented in each section as a fallback for environments without bash. It produces the same end state but takes ~15 minutes.
>
> ### Redeploy operators only: don't skip §5.7
>
> If you are redeploying the Standard Logic App onto a resource group that previously hosted it (i.e. the §10 path), the freshly-recreated managed API connections will inherit access policies from the previous (now-deleted) Managed Identity. The first workflow run returns **403 "Permission denied due to missing connection ACL"**. Run `reconcile-acl.sh` (§5.7) once between Path A's completion and §5.5 to fix this. First-time installs on a fresh RG don't hit it.

### 5.1 Deploy infrastructure (`infrastructure-arm.json`)

This ARM template creates three resources only:

- `Microsoft.Storage/storageAccounts` — StorageV2 for content share + AzureWebJobsStorage.
- `Microsoft.Web/serverfarms` — WS1 App Service plan (`WorkflowStandard` SKU).
- `Microsoft.Web/sites` — the Standard Logic App, `kind: "functionapp,workflowapp"`, System-assigned Managed Identity.

It does **not** create managed API connection resources. Those are created by the Designer in §5.4, which is the only way to populate the runtime URLs the workflows need. The template seeds every required app setting so that workflows resolve their `@appsetting()` references at runtime with no post-deploy configuration step.

Deploy:

1. Azure Portal → search bar → **"Deploy a custom template"** → **Build your own template in the editor**.
2. Paste the content of `Playbooks/Standard/infrastructure-arm.json` → **Save**.
3. Fill parameters:

   | Parameter                  | Value                                              | Notes                                                                                                                 |
   | -------------------------- | -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
   | `LogicAppName`             | `GIBTIA-Standard` (default)                        |                                                                                                                       |
   | `AppServicePlanName`       | `GIBTIA-Standard-Plan` (default)                   |                                                                                                                       |
   | `StorageAccountName`       | leave default — `gib<hash>` will be auto-generated |                                                                                                                       |
   | `GIBUsername`              | Group-IB portal login                              |                                                                                                                       |
   | `GIBApiKey`                | Group-IB API token                                 | securestring                                                                                                          |
   | `WorkspaceId`              | Workspace GUID                                     |                                                                                                                       |
   | `WorkspaceName`            | Workspace name                                     |                                                                                                                       |
   | `StartDate`                | `YYYY-MM-DD`                                       | First-run cursor; converted to a `seqUpdate` once on first run, ignored thereafter                                    |
   | `LimitPerPortion`          | `10` (default)                                     | **Use `10` for initial testing.** Raise afterwards — 1000 is a reasonable production value. This is a **single setting shared by all workflows**; each one clamps it to its own collection maximum, so a high value never breaks a low-limit collector. Maxima in [§7](#7-per-workflow-tuning) |
   | `IOCTypeFilter`            | `all` (default)                                    | `all` / `network` / `file` — IOC Primary indicator-type filter                                                        |
   | `UseRiskScoreAsConfidence` | `false` (default)                                  | When `true`, per-entry GIB riskScore becomes STIX confidence                                                          |
   | `FixedConfidence`          | `-1` (default)                                     | 0-100 to apply a fixed confidence; `-1` omits the field                                                               |
   | `UseAdmiraltyConfidence` | `false` (default)                                  | When `true`, STIX confidence is `(reliability + credibility) / 2` derived from `evaluation.admiraltyCode` via the Admiralty Code translation tables. Highest precedence; falls through to the two flags above when `admiraltyCode` is missing or malformed. |
   | `HasPasswordFilter`        | `1` (default)                                      | `compromised/breacheddb` only. `1` = ingest only breach records that carry a leaked password; `0` = all breach records |
   | `AccountFeedType`          | `unique` (default)                                 | `compromised/account_group` only. `unique` = only unique credentials; `combolist` = only combo-list credentials; `all` = every credential. **Default returns unique credentials only.** |
   | `ProbableCorporateAccessFilter` | `0` (default)                                 | `compromised/account_group` only. `1` = return only probable corporate-access credentials; `0` = no corporate-access filter. Independent of `AccountFeedType`. |

4. **Review + create** → **Create**. Deployment typically takes ~3–5 minutes.

### 5.2 Assign Managed Identity roles

> **If you're using §5.3 Path A (`post-deploy.sh`), skip the manual steps in this section** — the script's Phase 2 runs the equivalent `az role assignment create` commands for you. Read the role descriptions and "Why two roles?" callout below to understand what's being assigned, then move on to §5.3.

The Standard Logic App's MSI needs three permissions on the Sentinel workspace:

| Capability                                                         | Role                                             | Used by                                                                                                                                                      |
| ------------------------------------------------------------------ | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Upload indicators to Sentinel TI                                   | **Microsoft Sentinel Contributor**               | The `Upload_Indicators_V2` action in `GIBTIA_IndicatorProcessor_v2`                                                                                          |
| Query Log Analytics for `seqUpdate` checkpoint                     | (included in **Microsoft Sentinel Contributor**) | Every collector's `Query_Last_SeqUpdate` step (direct HTTP + MSI)                                                                                            |
| Write seqUpdate tracking record + context records to Log Analytics | **Log Analytics Contributor**                    | Every collector's `Save_seqUpdate_in_loop` / `Save_tracking_record` / context-table writes (via the `azureloganalyticsdatacollector` connector with MI auth) |

Steps (do both):

1. Logic App → left menu → **Identity** → confirm **System assigned** is **On**.
2. Go to your **Log Analytics workspace** → **Access control (IAM)** → **+ Add role assignment**.
3. Add **Microsoft Sentinel Contributor**:
   - Members → **Managed identity** → search for `GIBTIA-Standard` → select → **Review + assign**.
4. Repeat **+ Add role assignment** for **Log Analytics Contributor**: same member, same workspace scope.
5. Allow **5–10 minutes** for both assignments to propagate. Azure RBAC is eventually-consistent — the new roles aren't active immediately. First Upload_Indicators_V2 invocations may return **401 Unauthorized** until propagation completes; the action's retry policy (10 retries, exponential backoff up to 1 hour) typically catches up automatically.

> **Why two roles?** Microsoft Sentinel Contributor covers the Sentinel TI upload path and includes workspace _read_ permission for the seqUpdate query — but it does **not** include data-plane _write_ access to Log Analytics custom tables. Log Analytics Contributor provides that. Both roles are required for the integration to function end-to-end on Standard with MI auth.

> **⚠️ If you ever delete and re-deploy the Logic App resource, you must redo §5.2.** Each Logic App resource gets a **new** system-assigned Managed Identity with a fresh principal ID. The previous role assignments on the workspace still exist as ARM resources but reference the _old_ principal ID, which no longer corresponds to anything. Symptoms of forgetting this step: `Upload_Indicators_V2` returns **401**, `Query_Last_SeqUpdate` falls through to the `sequence_list` first-run path on every run (workflow looks like it succeeds but never advances seqUpdate). Confirm role assignments after any redeploy: `az role assignment list --assignee $(az webapp identity show -g <rg> -n <app> --query principalId -o tsv) --scope <workspace-resource-id>`.

### 5.3 Deploy the workflows

The Logic App is empty after §5.1. Three ways to get the workflows in. **Path A is the only one that works out of the box** — it bundles §5.2, this deploy step, the partial §5.4 (one Designer-bind pause), and the post-bind restart into a single 5-minute flow. Path B and Path C upload workflows only; you'll then have to do §5.2 (MSI roles), §5.4 (Designer-bind), and §5.7 (reconcile ACL on redeploys) by hand.

#### Path A — `post-deploy.sh` (recommended — the out-of-the-box path)

This script is the canonical way to take a fresh ARM deploy to a running integration. It covers §5.2 (MSI role assignment), this §5.3 (workflow upload), the partial §5.4 (Designer-bind — pauses for two clicks), and the post-bind restart. If you're redeploying, also run §5.7 after the script finishes.

##### Step 1 — get the source onto your deploy machine

You need the `Playbooks/Standard/` folder accessible from a shell that has `az` and `zip` installed. Two patterns:

**Cloud Shell (cleanest for operators without the repo locally):** build a tarball from a machine that has the repo, upload via Cloud Shell's file-upload icon.

```bash
# On a machine that has the repo:
cd /path/to/repo/Playbooks
tar --exclude='Standard/standard' \
    --exclude='Standard/.vscode' \
    --exclude='Standard/.DS_Store' \
    --exclude='Standard/.build' \
    --exclude='Standard/*.md' \
    -czf /tmp/gibtia-standard.tar.gz Standard
# Upload /tmp/gibtia-standard.tar.gz to Cloud Shell via the toolbar's Upload button, then in Cloud Shell:
cd ~
tar -xzf gibtia-standard.tar.gz
cd Standard
chmod +x post-deploy.sh reconcile-acl.sh
```

**Local terminal (developer-style):**

```bash
cd /path/to/repo/Playbooks/Standard
chmod +x post-deploy.sh reconcile-acl.sh
az login   # if not already
az account set --subscription <subscription-id>
```

##### Step 2 — run the script

```bash
./post-deploy.sh <resource-group> <logic-app-name> <workspace-name>

# Example:
./post-deploy.sh sentinel-gibtia-rg GIBTIA-Standard sentinel-gibtia-ws
```

The script proceeds through 7 phases. Watch the output as it runs:

| Phase | What it does | Operator action |
|---|---|---|
| 1 — Discover | Reads subscription, location, MSI principal ID, workspace ID | None |
| 2 — Assign MSI roles | Adds `Microsoft Sentinel Contributor` + `Log Analytics Contributor` on the workspace (= §5.2) | None |
| 3 — Initial workflow deploy | Builds a placeholder `connections.json` (so Designer can render), zips, deploys | None |
| 4 — **PAUSE** | Prompts you through two Designer-bind clicks (= §5.4) | Switch to Portal, do the two Designer binds (see §5.4 below for exact clicks), then press Enter in the shell |
| 5 — Poll for connection runtime URLs | Up to 15 minutes; typically 1–5 minutes | None (don't make Portal changes during this window) |
| 6 — Final `connections.json` + redeploy | Writes the proper `connections.json` with populated `connectionRuntimeUrl`s, redeploys | None |
| 7 — Restart | Restarts the host so it picks up the new connections | None |

When Phase 7 completes:

- **If this is a redeploy onto a previously-used RG** → run §5.7 (`reconcile-acl.sh`). The first workflow trigger will 403 otherwise.
- **If this is a first-time install** → skip §5.7. Go to §5.5 to test.

#### Path B — VS Code (Azure Logic Apps Standard extension)

Use this when you want the Designer-extension experience or can't run bash. **You will still need** to do §5.2 (MSI roles), §5.4 (Designer-bind), and §5.7 on redeploys — Path B uploads workflow files only.

1. Install the **Azure Logic Apps (Standard)** extension in VS Code.
2. **File** → **Open Folder** → select `Playbooks/Standard/`.
3. In the Azure pane, expand your subscription → resource group → find your Logic App. Expand it once so the tree fully hydrates (you should see the `Application settings` child node populate).
4. Right-click the Logic App → **Deploy to Logic App…** → confirm **"Deploy"**.
5. After the deploy finishes, return to §5.2 (if not done already) and §5.4. On redeploys also do §5.7.

If you hit `"Cannot read properties of undefined (reading 'appSettingsTreeItem')"` — reload the VS Code window (Cmd/Ctrl+Shift+P → *Developer: Reload Window*) and re-try, or fall back to Path C.

#### Path C — Manual `az` zip-deploy (no automation)

For environments where bash and `az` are available but the operator deliberately wants to skip `post-deploy.sh`. Same caveat as Path B: §5.2 / §5.4 / §5.7 still need to be done by hand.

```bash
cd Playbooks/Standard
zip -r /tmp/gibtia-standard.zip . \
  -x "*.DS_Store" \
  -x "infrastructure-arm.json" \
  -x "post-deploy.sh" \
  -x "reconcile-acl.sh" \
  -x ".build/*" \
  -x "standard/*" \
  -x ".vscode/*"

az logicapp deployment source config-zip \
  --resource-group <your-rg> \
  --name <LogicAppName> \
  --src /tmp/gibtia-standard.zip
```

After deploy, Logic App → **Workflows** → confirm all 29 workflows appear. Then go to §5.2, §5.4, optionally §5.7.

### 5.4 Bind the two managed API connections via the Designer

This is the one manual step that ARM can't automate — the Logic Apps Standard runtime generates a per-Logic-App `connectionRuntimeUrl` only when a connection is bound through the Designer or the Logic App's internal connection-management API. You only need to do it **once per connector type**, not per workflow. The shipped workflows all reference `azuresentinel` and `azureloganalyticsdatacollector` by name, so once those two connections exist in `connections.json` every workflow resolves automatically.

**Bind the `azuresentinel` connection** (used by the indicator processor and the enrichment playbooks):

1. Logic App → **Workflows** → open `GIBTIA_IndicatorProcessor_v2` → **Designer**.
2. Click the **`Upload_Indicators_V2`** action.
3. In the right pane → Connection section → click **Add new** (or **Change connection** → **Add new** depending on Portal version).
4. Authentication: **Managed identity** → **System-assigned managed identity**. Connection name: leave as `azuresentinel` (the default).
5. Click **Create**.
6. **Save the workflow** (toolbar at the top).

**Bind the `azureloganalyticsdatacollector` connection** (used by every collector + context playbook):

1. Open `GIBTIA_IOC_Primary_Updated` → **Designer**.
2. Click the **`Save_seqUpdate_in_loop`** action.
3. Connection section → **Add new**.
4. Authentication: **Managed identity** → **System-assigned managed identity**. Connection name: leave as `azureloganalyticsdatacollector`.
5. Click **Create**.
6. **Save the workflow**.

Verify the bind succeeded — Kudu → Debug console → `cd site/wwwroot` → `type connections.json`. Both connections should appear with a populated `connectionRuntimeUrl`.

### 5.5 First test run and verification

1. Open `GIBTIA_IOC_Primary_Updated` → **Overview** → **Run Trigger**.
2. Wait ~1 minute, click the run row to see step details.

Expected behaviour on the **first** run:

- `Query_Last_SeqUpdate` shows as **Failed** with a 400-range error — normal. The shared `GIBCollectionTracking_CL` table doesn't exist yet; the workflow detects the failure and falls through to the `sequence_list` first-run path.
- `Until` loop runs, `Save_seqUpdate_in_loop` succeeds, `Save_tracking_record` succeeds.
- Within 5 minutes (batch timeout), `GIBTIA_IndicatorProcessor_v2` fires automatically — check its **Run history**.

On the **second** run of the same workflow:

- `Query_Last_SeqUpdate` should now succeed (200) — the workflow resumes from the saved checkpoint instead of falling into the first-run path.

Verify in Log Analytics:

```kusto
GIBCollectionTracking_CL
| where CollectionName_s == "ioc/primary"
| order by TimeGenerated desc
| take 5
```

Expected: one row with a numeric `SeqUpdate_d`.

```kusto
ThreatIntelIndicators
| where SourceSystem contains "Group-IB"
| order by TimeGenerated desc
| take 20
```

Expected: STIX-patterned rows like `[ipv4-addr:value = '...']`, `[domain-name:value = '...']`, etc.

### 5.6 Production configuration

After the test run succeeds:

1. Logic App → **Settings → Environment variables** → raise `LimitPerPortion` to a production value (start with `1000` for IOC Primary; per-collection maxima are listed in [§7](#7-per-workflow-tuning)).
2. Enable any collectors you initially disabled (Workflows list → select → **Enable**).
3. Leave the recurrence triggers running; they fire hourly automatically.

For per-workflow overrides (e.g. a different `LimitPerPortion` per collection), see [§7](#7-per-workflow-tuning).

### 5.7 Reconcile connection access policies (redeploy only)

**Skip this section on a first-time install.** Run it only if you are redeploying the Standard Logic App onto a resource group that previously hosted it.

#### Why this step exists

`Microsoft.Web/connections` resources retain their **access-policy registration** in the Logic Apps managed-API token store even after you delete the ARM resource. When the Designer-bind step (§5.4 or its automation inside `post-deploy.sh`) recreates a connection with the same name (e.g. `azuresentinel-1`), Azure reattaches the surviving entry — which carries forward the previous Managed Identity's access policy. The current MSI doesn't match the carried-forward policy, so the runtime returns **403 "Permission denied due to missing connection ACL"** on every authenticated action (`Upload_Indicators_V2`, `Save_seqUpdate_in_loop`, context-table writes).

This trap does not fire on a first-time install (no previous token-store entry to reuse). It fires on every redeploy.

#### Run the reconciliation script

```bash
cd Playbooks/Standard
./reconcile-acl.sh <resource-group> <logic-app-name>

# Example:
./reconcile-acl.sh sentinel-gibtia-rg GIBTIA-Standard
```

The script (idempotent, ~50 lines):

1. Discovers the Logic App's current MSI, tenant, and location.
2. Finds every `Microsoft.Web/connections` resource in the RG whose name matches `azuresentinel*` or `azureloganalyticsdatacollector*`.
3. **Deletes** any access policy whose name matches `<LogicAppName>-*` AND whose principal is **not** the current MSI (i.e. orphans from previous deploys). Preserves all other policies untouched.
4. **Upserts** an access policy for the current MSI on each connection.
5. Restarts the Logic App to flush the token-exchange cache.

Wait ~60 seconds after the script reports `Restart issued.` for the host to come back, then re-trigger your test workflow (§5.5). The 403 should be gone.

> **Safe to re-run.** The script is idempotent and additive in spirit: it only deletes policies whose names match this Logic App's prefix. Customer-added or third-party policies (different naming convention) are preserved. On a clean tenant the script is effectively a no-op — nothing to prune, PUT just re-affirms the policy the Designer already created correctly.

> **Tracked as an open improvement.** See `MAINTAINER_NOTES.md §7` "Things still worth doing": there may be a way to clear the underlying token-store registration during cleanup (§10) so this script becomes unnecessary. If/when that's resolved, this section will be deprecated.

---

## 6. Operating the Standard Logic App

### Where to view runs

- Logic App → **Workflows** → click a workflow → **Run history**.
- Each workflow has its own run history; Standard does not consolidate them.

### Enabling / disabling individual workflows

- Workflows list → check the workflow → toolbar **Enable** / **Disable**.
- Disabling a workflow stops its recurrence trigger; existing runs continue to completion.

### Restarting the host

Changing app settings (e.g. `LimitPerPortion`) triggers a restart automatically. To force one: Logic App → **Overview** → **Restart**.

### Scaling

- The WS1 plan supports elastic scale-out: in `infrastructure-arm.json`, `elasticScaleEnabled: true` and `maximumElasticWorkerCount: 3`. Most installations never hit the limit.
- If you need higher throughput, upgrade the plan SKU (`WS2`, `WS3`) via the App Service Plan → **Scale up**. No workflow changes required.

### Redeploying workflows

Re-running the VS Code **Deploy to Logic App** or the `az logicapp deployment source config-zip` command **overwrites** every workflow in `wwwroot`. Customizations to individual `workflow.json` files in the running Logic App are lost — always edit in source and redeploy.

---

## 7. Per-workflow tuning

Standard supports two levels of configuration: global app settings (used by every workflow) and per-workflow `workflow.json` edits (used by one workflow).

### Global app settings (apply to every collector)

| Setting           | Type            | Default        | Effect                                    |
| ----------------- | --------------- | -------------- | ----------------------------------------- |
| `GIBUsername`     | string          | from ARM param | Group-IB API basic-auth user              |
| `GIBApiKey`       | string (secret) | from ARM param | Group-IB API basic-auth key               |
| `StartDate`       | string          | from §5.2      | First-run cursor (YYYY-MM-DD)             |
| `LimitPerPortion` | string          | from §5.2      | Page size for every collector             |
| `WorkspaceId`     | string          | from ARM param | LA workspace GUID                         |
| `WorkspaceName`   | string          | from ARM param | LA workspace name (used in MSI query URI) |
| `HasPasswordFilter` | string (`"1"`/`"0"`) | `"1"` | Used only by `GIBTIA_Compromised_BreachedDB`. `"1"` = only ingest breach records with a leaked password; `"0"` = all records |
| `AccountFeedType` | string (`"unique"`/`"combolist"`/`"all"`) | `"unique"` | Used only by `GIBTIA_Compromised_account`. `"unique"` = only unique credentials; `"combolist"` = only combo-list credentials; `"all"` = every credential. Default returns unique credentials only. |
| `ProbableCorporateAccessFilter` | string (`"1"`/`"0"`) | `"0"` | Used only by `GIBTIA_Compromised_account`. `"1"` = only probable corporate-access credentials; `"0"` = no corporate-access filter. Independent of `AccountFeedType`. |

### Changing the collection frequency

The schedule is **not** an app setting — it is deliberately absent from the table above,
which is where most people look first. It lives in each workflow's **Recurrence** trigger,
set to every 1 hour, and is changed per workflow:

1. Logic App (Standard) → **Workflows** → select the workflow.
2. **Designer** → click the **Recurrence** trigger.
3. Set **Frequency** (Minute / Hour / Day / Week) and **Interval**.
4. **Save.** It takes effect on the next scheduled run.

Alternatively, edit `"recurrence": { "frequency": ..., "interval": ... }` in that workflow's
`workflow.json` and re-deploy the zip (§5.3). That is the durable option — see the first
caveat below.

> **Note:** you cannot change this from Microsoft Sentinel. The Sentinel **Automation →
> Playbooks** blade lists the workflows and lets you attach them to automation rules, but it
> does not expose the recurrence trigger. It is a Logic Apps setting.

Three things to know before you change it:

- **A zip re-deploy silently reverts it.** The trigger is part of `workflow.json`, so
  deploying the workflows again (§5.3, or `post-deploy.sh`) overwrites a Designer change and
  restores the hourly schedule. Nothing warns you. If a non-default schedule matters, change
  it in `workflow.json` and deploy that.
- **Below one hour, some runs will be skipped — on purpose.** Each collector's `Until` paging
  loop has a `PT1H` timeout, and the trigger carries
  `runtimeConfiguration.concurrency.runs: 1`. At an hourly interval those line up exactly. If
  you set, say, 15 minutes, then whenever a run is still paging — during the initial backfill,
  or catching up after an outage — the triggers that fire in the meantime are **skipped rather
  than queued**. That cap is deliberate: two concurrent runs share one
  `GIBCollectionTracking_CL` cursor and can rewind it, causing duplicate ingestion. Gaps in
  run history under a short interval are expected, not a fault. Intervals **longer** than an
  hour have no such effect.
- **Cost behaves differently from Consumption.** The WS1 plan is fixed-price, so a shorter
  interval does not increase your bill the way it does on Consumption — but it does consume
  more of the plan's compute, which matters if you are already near its limits (§6 *Scaling*).

Changing one workflow does not change the others. If you want a different schedule across the
board, edit all 26 collector `workflow.json` files before deploying, rather than clicking
through 26 Designers.

### Per-collection limits (LimitPerPortion maxima)

The Group-IB API enforces a per-collection maximum on `limit`. Source of truth: **Integrations →
Starting Guide → API Limitations**. (Note: the individual "Collections Details – Feeds" pages carry a
boilerplate `Collection Limit | 500` row that contradicts this table for several collections — don't
use it.)

| Collection                                                                                                                                                           | Max `limit` |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `ioc/primary/updated`, `attacks/ddos/updated`, `suspicious_ip/open_proxy/updated`, `suspicious_ip/scanner/updated`, `suspicious_ip/socks_proxy/updated`              | **5000**    |
| `attacks/phishing_group/updated`, `attacks/phishing_kit/updated`, `malware/cnc/updated`                                                                              | **1000**    |
| `compromised/account_group/updated`, `compromised/bank_card_group/updated`, `compromised/masked_card/updated`, `compromised/spd/updated`                             | **500**     |
| `osi/vulnerability/updated`                                                                                                                                          | **200**     |
| `attacks/deface/updated`, `malware/config/updated`, `malware/malware/updated`, `osi/git_repository/updated`, `hi/open_threats/updated`, `hi/threat_actor/updated`, `apt/threat_actor/updated`, `compromised/breacheddb/updated`, `suspicious_ip/tor_node/updated`, `suspicious_ip/vpn/updated` | **100**     |
| `apt/threat/updated`, `hi/threat/updated`                                                                                                                            | **10**      |
| `osi/public_leak/updated`                                                                                                                                            | **5**       |

> `osi/public_leak` is the one row where the effective ceiling is **not** the API maximum. The API
> allows 100, but its records are full text dumps, so the workflow clamps at 5 to stay under the
> Logic Apps 100 MB payload limit. Size-driven, not API-driven.

> **You no longer need to act on this table.** Every workflow clamps its own request with
> `min(int(appsetting('LimitPerPortion')), <collection max>)`, so a global value above a collection's
> maximum is silently reduced for that workflow rather than breaking it. The table is here so you can
> predict the effective page size, not because you must avoid a value.
>
> **Why the clamp exists:** requesting more than a collection allows does not return a clean error.
> The response comes back far larger than a page and overflows the Logic Apps 100 MB action payload
> limit, failing `Get_next_portion` with
> `Cannot write more bytes to the buffer than the configured maximum buffer size: 104857600`.

To pin a workflow *below* its collection maximum — for example because its records are unusually
large — override in the Standard package:

1. Open `Playbooks/Standard/GIBTIA_<Name>/workflow.json` in source.
2. Find the action that calls the Group-IB `/updated` endpoint (typically `Get_next_portion` or similarly named, inside the Until loop). Its `inputs.uri` references `@appsetting('LimitPerPortion')`:
   ```
   "uri": "@{concat('https://tap.group-ib.com/api/v2/<collection>/updated?seqUpdate=', ..., '&limit=', appsetting('LimitPerPortion'))}"
   ```
3. Replace the `appsetting('LimitPerPortion')` call with the literal max for that collection (as a string), e.g. `'10'` for `apt/threat`:
   ```
   "uri": "@{concat('https://tap.group-ib.com/api/v2/apt/threat/updated?seqUpdate=', ..., '&limit=10')}"
   ```
4. Redeploy via the partial zip-deploy snippet from `MAINTAINER_NOTES.md §5` (preserves the operator's `connections.json`). Only the affected `workflow.json` is repackaged.

> **Precedent**: `GIBTIA_OSI_PublicLeak` already ships with a lowered ceiling — it clamps at `5`, not
> at its API maximum of 100, because public-leak records are full text dumps that exceed Logic Apps'
> 100 MB action payload limit at higher values. Rather than replacing the `appsetting` call with a
> literal, it lowers the clamp constant:
> `min(int(appsetting('LimitPerPortion')), 5)`. Prefer that form — the setting stays tunable *below*
> the ceiling, which is useful for testing, and the workflow keeps the same shape as every other
> collector.

### IOC Primary confidence flags

`GIBTIA_IOC_Primary_Updated` reads three confidence-control app settings (seeded by ARM, tunable via Logic App → Environment variables):

| Setting                    | Type            | Default | Effect                                                                                                                                                                                                                                                                       |
| -------------------------- | --------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `UseAdmiraltyConfidence` | Bool (`"true"`/`"false"`) | `"false"` | When `true`, STIX `confidence` is `(reliability + credibility) / 2` derived from `evaluation.admiraltyCode` (e.g. `"C3"` → 60). **Highest precedence** — falls through to `UseRiskScoreAsConfidence` / `FixedConfidence` when `admiraltyCode` is missing, wrong length, or contains a letter/digit outside the lookup table. |
| `UseRiskScoreAsConfidence` | Bool (`"true"`/`"false"`) | `"false"` | When `true`, the per-entry `riskScore` from the Group-IB `ip[]`/`domain[]`/`url[]` arrays drives STIX `confidence`.                                                                                                                                                       |
| `FixedConfidence`          | Int (-1 to 100) | `"-1"`  | When set ≥ 0 (and neither of the above supply a value), every indicator uses this fixed value. `-1` omits the field entirely.                                                                                                                                              |

Precedence: `UseAdmiraltyConfidence` (when enabled + record has parseable `admiraltyCode`) → `UseRiskScoreAsConfidence` (when enabled) → `FixedConfidence` (when ≥ 0) → field omitted.

**Admiralty Code translation tables** (hardcoded in the workflow expressions):

```
reliability: A=100, B=80, C=60, D=40, E=20, F=0   # first character of admiraltyCode
credibility: 1=100, 2=80, 3=60, 4=40, 5=20, 6=0   # second character
```

Examples: `"A1"` → 100. `"C3"` → 60. `"F6"` → 0. `"B2"` → 80. Codes outside this scheme (e.g. `"X9"`, missing field, wrong length) trigger fall-through to the next precedence option.

Change any of the three via Logic App → **Settings → Environment variables**. The Logic App restarts automatically when an app setting changes.

### Evaluation block fields surfaced on indicators

When `ioc/primary` records carry an `evaluation` block, the following fields appear on the resulting `ThreatIntelIndicators` row:

| Evaluation field | Where it lands | KQL query example |
|---|---|---|
| `TTL` (days) | `ValidUntil` = `ValidFrom + TTL days` (90 days fallback when absent) | `where ValidUntil > now() + 1d` |
| `TLP` | `object_marking_refs` (STIX V2 structured column) | (per Sentinel V2 schema docs) |
| `admiraltyCode` | `Tags` column entry `admiralty:<code>` | `where Tags has "admiralty:A1"` |
| `credibility` | `Tags` column entry `credibility:<n>` | `where Tags has "credibility:90"` |
| `reliability` | `Tags` column entry `reliability:<n>` | `where Tags has "reliability:80"` |
| `riskScore` (record field, not in evaluation block) | `Tags` column entry `risk-score:<n>` | `where Tags has "risk-score:80"` — always surfaced when present, independent of `UseRiskScoreAsConfidence` |

Records without an evaluation block produce indicators identical to the pre-2026 behavior (90-day expiry, base labels only, empty `object_marking_refs`).

`ThreatIntelIndicators` is a Microsoft-managed table, so `riskScore` (and the other evaluation tags) cannot be added as a dedicated column — they live in `Tags`. To query them as typed columns (`RiskScore`, `Credibility`, `Reliability`, `AdmiraltyCode`), create the `GIB_ThreatIntelIndicators` saved function described in [USER_GUIDE.md §5 — Surfacing risk score (and other Group-IB tags) as columns](USER_GUIDE.md#surfacing-risk-score-and-other-group-ib-tags-as-columns). It is platform-agnostic — the same function works for indicators ingested by the Standard package.

### IOCTypeFilter

`GIBTIA_IOC_Primary_Updated` also reads an `IOCTypeFilter` app setting (`all` / `network` / `file`) which restricts which indicator categories are emitted. Default: `all`.

Change via Logic App → **Settings → Environment variables** → set `IOCTypeFilter` → **Apply**. The Logic App restarts automatically; no source edit required.

---

## 8. Verifying the Integration, Use Cases and Analytics Rules

The downstream Sentinel content is identical regardless of which deployment package (Standard or Consumption) put the indicators there. Refer to the Consumption guide for the platform-agnostic sections:

- [USER_GUIDE.md §5 — Verifying the Integration](USER_GUIDE.md#5-verifying-the-integration) — health-check KQL queries.
- [USER_GUIDE.md §6 — Use Case Guide](USER_GUIDE.md#6-use-case-guide) — including the Defender portal navigation note at the top of §6 (applies to both packages), the [§6.0 Quick-start](USER_GUIDE.md#60-quick-start--get-your-first-gib-driven-incident) sequence for getting your first GIB-driven incident, [§6.1 TI Map rules](USER_GUIDE.md#61-automated-ioc-matching-ti-map-rules) for the step-by-step rule-template walkthrough, and the other use cases (APT alerting, vulnerability alerting, credential detection, phishing infrastructure correlation, etc.).
- [USER_GUIDE.md §7 — Analytics Rules](USER_GUIDE.md#7-analytics-rules--examples-and-setup) — ready-to-paste KQL detection rules for context-table use cases.
- [USER_GUIDE.md §8 — Automation with Enrichment Playbooks](USER_GUIDE.md#8-automation-with-enrichment-playbooks) — granting Sentinel permission to run playbooks (§8.2), WHOIS enrichment automation rule (§8.3), IOC Primary enrichment automation rule (§8.5).

### Standard-specific differences

When following §8.3 and §8.5 from the Consumption guide, the only meaningful Standard difference is the **playbook selector dropdown**:

- For Consumption: each enrichment playbook (`GIBTIA_Enrich_WHOIS`, `GIBTIA_Enrich_IOC`) appears as its own **top-level Logic App** resource.
- For Standard: both enrichment workflows appear **nested under the single `GIBTIA-Standard` Standard Logic App**. Expand `GIBTIA-Standard` in the picker and select the specific workflow.

Both behave identically once selected. The same Sentinel automation rule logic, the same incident-comment output, the same triggering conditions.

> **Defender-portal-specific note for Standard:** in the Defender portal's automation-rule creator, the **Run playbook** action may not yet show Standard Logic Apps' nested workflows reliably (Microsoft is still finishing this surface). If the workflow you want doesn't appear, create the automation rule via the Azure-portal Sentinel UI instead — same backend rule, the Defender portal will display and execute it correctly afterward. This is improving over time; check both portals if one isn't surfacing your workflows.

---

## 9. Troubleshooting

| Symptom                                                                                                                                                                                                                                                                    | Cause                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Resolution                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|---|---|---|
| `Query_Last_SeqUpdate` fails with **400** on the very first run                                                                                                                                                                                                            | Tracking table `GIBCollectionTracking_CL` does not exist yet                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Expected on a brand-new workspace. The workflow handles this via the `sequence_list` first-run path.                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `Query_Last_SeqUpdate` fails with **403** on every run                                                                                                                                                                                                                     | MSI missing **Microsoft Sentinel Contributor** on the workspace                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Revisit [§5.2](#52-assign-managed-identity-roles). Wait 1 minute for propagation.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `Save_seqUpdate_in_loop` / `Save_tracking_record` / context-table writes return **403**                                                                                                                                                                                    | MSI missing **Log Analytics Contributor** on the workspace                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Microsoft Sentinel Contributor does _not_ include data-plane writes to LA custom tables. Add **Log Analytics Contributor** as a second role on the same MSI — see [§5.2](#52-assign-managed-identity-roles).                                                                                                                                                                                                                                                                                                                                                                |
| `Upload_Indicators_V2` returns **403**                                                                                                                                                                                                                                     | MSI missing **Microsoft Sentinel Contributor**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Revisit [§5.2](#52-assign-managed-identity-roles).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Any action authenticating through a managed API connection fails with **403 "Permission denied due to missing connection ACL"** — `Upload_Indicators_V2`, `Save_seqUpdate_in_loop`, or context-table writes. Happens **only on a redeploy** (first-time deploys are fine). | `Microsoft.Web/connections` resources retain their access-policy registration in the Logic Apps managed-API token store across delete+recreate. When the Designer's Add new step recreates a connection with the same name (e.g. `azuresentinel-1`), Azure reattaches the surviving entry — carrying forward the previous MSI's `accessPolicies`. The token-exchange path evaluates policies in order and 403s on the first stale principal it finds (the now-deleted previous MSI) without falling through to a later matching one. | Run `./reconcile-acl.sh <rg> <app>` from `Playbooks/Standard/`. The script discovers the current MSI, deletes any orphan policies named `<LogicAppName>-*` whose principal isn't the current MSI, upserts the current MSI's policy on each Standard-package connection, and restarts the Logic App to flush the token cache. Targeted cleanup (preserves non-integration policies); idempotent (safe to re-run, safe on fresh tenants where it's effectively a no-op). Wait ~60s after the script finishes for the host to come back, then re-trigger the failing workflow. |
| HTTP 400 from Group-IB `/updated` calls                                                                                                                                                                                                                                    | `LimitPerPortion` exceeds the per-collection maximum                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | See [§7](#7-per-workflow-tuning) — override `LimitPerPortion` (app setting) or in that workflow's `workflow.json`.                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Workflow start fails with **"The workflow parameter 'X' is not found"**                                                                                                                                                                                                    | The Designer save stripped the workflow's `parameters` block — known Standard Designer bug; refs to `parameters('X')` are now orphaned                                                                                                                                                                                                                                                                                                                                                                                               | In wwwroot, edit the workflow.json and replace every `parameters('GIBUsername'                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 'GIBApiKey' | 'StartDate' | 'LimitPerPortion' | 'WorkspaceId' | 'WorkspaceName')`with`appsetting('...')`. The shipped source already does this — only manifests if you've manually edited a workflow in the Designer. |
| Workflow validation fails with **`The provided workflow name '/workflows/...' has these invalid characters '//'`**                                                                                                                                                         | The Standard runtime rejects the `/workflows/` prefix in `SendToBatch.host.workflow.id` — Microsoft tightened the validator                                                                                                                                                                                                                                                                                                                                                                                                          | Replace `"id": "/workflows/<name>"` with `"id": "<name>"` (bare name, no slashes) in every SendToBatch action. Shipped source is already correct.                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Workflow validation fails with **"The language expression property 'connectionRuntimeUrl' doesn't exist"**                                                                                                                                                                 | ARM `reference()` cannot return `connectionRuntimeUrl` from `Microsoft.Web/connections` — that property is allocated by the Logic App's runtime at connection-bind time                                                                                                                                                                                                                                                                                                                                                              | The shipped infrastructure-arm.json does not attempt this. If you see this from a customized infra template, drop any `reference(...).properties.connectionRuntimeUrl` expressions; rely on [§5.4](#54-bind-the-two-managed-api-connections-via-the-designer) Designer bind to populate the URL.                                                                                                                                                                                                                                                                            |
| Workflow start fails with **"managedApiConnections cannot be parsed"**                                                                                                                                                                                                     | `connections.json` is malformed, or has `@appsetting()` references whose target settings don't exist (resolves to null), or is missing `connectionRuntimeUrl` for a connection                                                                                                                                                                                                                                                                                                                                                       | Revisit [§5.4](#54-bind-the-two-managed-api-connections-via-the-designer) — the Designer bind must complete successfully so `connections.json` gains a populated `connectionRuntimeUrl` for both connectors.                                                                                                                                                                                                                                                                                                                                                                |
| Designer shows **"The provided subscription identifier '@{appsetting('workflows_subscription_id')}' is malformed"**                                                                                                                                                        | The Designer doesn't evaluate `@appsetting()` at design-time. Either `WORKFLOWS_SUBSCRIPTION_ID` / `_RESOURCE_GROUP_NAME` / `_LOCATION_NAME` aren't set, or the connection's `api.id` contains `@appsetting()` expressions                                                                                                                                                                                                                                                                                                           | Shipped infrastructure-arm.json seeds all three. If you see this on a deployed app, verify the three settings exist via Logic App → **Environment variables**. If they exist and the error persists, the Designer is choking on `@appsetting()` in `connections.json` — re-bind via §5.4 to overwrite that file with literal values.                                                                                                                                                                                                                                        |
| VS Code extension throws **"Cannot read properties of undefined (reading 'appSettingsTreeItem')"** during deploy                                                                                                                                                           | Stale Azure-tree cache in the Logic Apps (Standard) extension                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Reload window (Cmd/Ctrl+Shift+P → _Developer: Reload Window_). If it persists, use Path B (`az logicapp deployment source config-zip`) from [§5.3](#53-deploy-the-workflows).                                                                                                                                                                                                                                                                                                                                                                                               |
| Manual **Run Trigger** on `GIBTIA_IndicatorProcessor_v2` fails with **"Cannot read properties of undefined (reading 'headers')"**                                                                                                                                          | The adapter uses a **Batch** trigger, which can only be fired by upstream `SendToBatch` actions — not by Portal "Run Trigger"                                                                                                                                                                                                                                                                                                                                                                                                        | Expected. Don't try to start it manually. Run a collector instead; the adapter fires automatically when 100 messages queue or the 5-minute timeout elapses.                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Workflows do not appear in **Workflows** list after deployment                                                                                                                                                                                                             | Deploy uploaded to the wrong app, or the host did not restart                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Logic App → **Overview** → **Restart**. Verify with `az logicapp deployment source download` and check the zip.                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Adapter `GIBTIA_IndicatorProcessor_v2` never fires after a collector run                                                                                                                                                                                                   | The collector's `SendToBatch_*` actions failed silently (workflow status reports `Succeeded` if `Save_tracking_record` succeeds, even when batch sends failed)                                                                                                                                                                                                                                                                                                                                                                       | Open the collector run → expand the `For_each_*` loops → check each `SendToBatch_*` action status.                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `Microsoft_Sentinel_incident` webhook trigger never fires in enrichment workflows                                                                                                                                                                                          | No automation rule binds it to incidents                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Configure a Sentinel **automation rule** that calls the workflow on incident creation. The Standard Logic App's workflows appear as targets in the rule's "Run playbook" action selector.                                                                                                                                                                                                                                                                                                                                                                                   |
| Notification: **"Node.js LTS has reached EOL"** (was 18, then 20)                                                                                                                                                                                                                         | Earlier infrastructure used `WEBSITE_NODE_DEFAULT_VERSION: ~18` (EOL May 2025), then `~20` (EOL April 2026)                                                                                                                                                                                                                                                                                                                                                                                                                                     | Current `infrastructure-arm.json` uses `~22`. For existing deployments, edit the app setting in **Environment variables** to `~22`; the app restarts automatically.                                                                                                                                                                                                                                                                                                                                                         |
| Logic App billing higher than expected                                                                                                                                                                                                                                     | WS1 plan runs continuously, billed by hour regardless of executions                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Expected — Standard uses fixed plan billing. To reduce cost: scale to a smaller plan SKU (WS1 is already the smallest) or move infrequent collectors to Consumption.                                                                                                                                                                                                                                                                                                                                                                                                        |
| App setting changes do not take effect                                                                                                                                                                                                                                     | Logic App did not restart, or app settings cache is stale                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Logic App → **Overview** → **Restart**. Wait ~30 seconds.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Right after the §5.4 Designer bind, runs fail with connection/auth errors even though `connections.json` looks correct, and Stop+Start doesn't immediately fix it                                                                                                          | Logic Apps Standard's connection-claim and runtime-URL provisioning is eventually-consistent — the host process can take a few minutes to fully register newly-bound managed API connections, even after a Stop+Start. Symptoms include `ConnectionReferenceInvalid`, `headers` undefined errors on manual trigger, or 401/403 on the first auth attempt.                                                                                                                                                                            | Wait. Seriously — **5–15 minutes** is normal. Don't make any more changes during the wait, and don't try to "fix" the connection by re-binding (which can create more `-2`/`-3` suffixed orphans). Recheck after ~10 minutes; if it's still broken then, look at the connection's `overallStatus` (should be `Ready` or `Connected`) and the role assignments on the workspace.                                                                                                                                                                                             |
| `az role assignment list --assignee <msi-id>` returns `[]` even though you just successfully ran `az role assignment create` and got back a JSON object                                                                                                                    | `az role assignment list` by default only shows assignments at the **subscription scope or above** — assignments scoped to a child resource (like a Log Analytics workspace) are hidden unless you ask for them.                                                                                                                                                                                                                                                                                                                     | Add `--all` to the list command, or pass `--scope <workspace-resource-id>` explicitly. The create command's success means the assignment exists regardless of what list returns.                                                                                                                                                                                                                                                                                                                                                                                            |

For additional diagnostics, every workflow's **Run history** shows each action's rendered outputs — open the failing step to see the exact HTTP response from Group-IB or Azure.

> **Inputs on Group-IB calls are redacted by design.** Every HTTP action targeting `tap.group-ib.com` carries `runtimeConfiguration.secureData.properties: ["inputs"]`, so its inputs render as sanitized rather than showing the `Authorization: Basic …` header and the API key it encodes. This is expected, not a fault. **Outputs are not secured**, so the response body, status code and error message — the things you actually need to debug — remain fully visible. If you need to confirm the request URI, read it from the workflow definition; it is built from `@appsetting('LimitPerPortion')` and the stored `seqUpdate`.

---

## 10. Clean reinstall — wipe and start over

Use this section when you want to redeploy the Standard package onto the same resource group from scratch. The recipe deletes the Logic App, App Service Plan, Storage Account, and managed API connections. It **does not** delete the Log Analytics workspace, the Sentinel solution on it, or any of the `GIB*_CL` custom tables — so `seqUpdate` cursors and historical indicators survive, and collectors resume from where they left off on first run after redeploy.

### What gets deleted vs kept

| Deleted | Kept |
|---|---|
| `Microsoft.Web/sites` (the Logic App) | `Microsoft.OperationalInsights/workspaces` (the Log Analytics workspace) |
| `Microsoft.Web/serverfarms` (the App Service Plan) | The Sentinel solution on the workspace |
| `Microsoft.Storage/storageAccounts` (the Logic App's storage) | `GIBCollectionTracking_CL` (with seqUpdate cursors) |
| `Microsoft.Web/connections/azuresentinel-*` | `ThreatIntelIndicators` (previously-uploaded indicators expire naturally per `ExpirationDateTime`) |
| `Microsoft.Web/connections/azureloganalyticsdatacollector-*` | All `GIB*_CL` context tables |

### Stage 1 — enumerate (dry-run, no changes)

Set your deployment names and inspect what's about to be deleted:

```bash
RG=sentinel-gibtia-rg
APP=GIBTIA-Standard
WS=sentinel-gibtia-ws

PLAN=$(az appservice plan list -g "$RG" --query "[0].name" -o tsv)
STORAGE=$(az webapp config appsettings list -g "$RG" -n "$APP" \
  --query "[?name=='AzureWebJobsStorage'].value | [0]" -o tsv \
  | sed -n 's/.*AccountName=\([^;]*\).*/\1/p')
OLD_MSI=$(az webapp identity show -g "$RG" -n "$APP" --query principalId -o tsv 2>/dev/null)

echo "=== Will be DELETED ==="
echo "Logic App:   $APP"
echo "Plan:        $PLAN"
echo "Storage:     $STORAGE"
echo "Old MSI:     $OLD_MSI"
echo ""
echo "Managed API connections:"
az resource list -g "$RG" --resource-type Microsoft.Web/connections \
  --query "[?contains(name, 'azuresentinel') || contains(name, 'azureloganalyticsdatacollector')].name" \
  -o tsv | sed 's/^/  /'
echo ""
echo "=== Will be KEPT ==="
echo "Workspace:   $WS"
echo "LA tables:   GIBCollectionTracking_CL, ThreatIntelIndicators, GIB*_CL"
```

Inspect the output. If the names look correct, proceed.

### Stage 2 — delete

```bash
echo "=== 1/4 Logic App ==="
az resource delete -g "$RG" -n "$APP" --resource-type Microsoft.Web/sites

echo "=== 2/4 App Service Plan ==="
az appservice plan delete -g "$RG" -n "$PLAN" --yes

echo "=== 3/4 Storage Account ==="
az storage account delete -g "$RG" -n "$STORAGE" --yes

echo "=== 4/4 Managed API connections ==="
for CONN in $(az resource list -g "$RG" --resource-type Microsoft.Web/connections \
                --query "[?contains(name, 'azuresentinel') || contains(name, 'azureloganalyticsdatacollector')].name" -o tsv); do
  echo "  Deleting: $CONN"
  az resource delete -g "$RG" -n "$CONN" --resource-type Microsoft.Web/connections
done
```

### Stage 3 — verify

```bash
echo "=== Remaining GIBTIA-related resources (should be empty) ==="
az resource list -g "$RG" \
  --query "[?contains(name, 'GIBTIA') || contains(name, 'gibtia') || contains(name, 'azuresentinel') || contains(name, 'azureloganalyticsdata')].{name:name, type:type}" \
  -o table

echo ""
echo "=== Workspace + Sentinel should still be here ==="
az resource list -g "$RG" \
  --query "[?contains(name, '$WS')].{name:name, type:type}" -o table
```

Expected: the first command returns no rows; the second shows the workspace + `SecurityInsights(<workspace>)`.

### Optional — clean orphan role assignments

The deleted MSI's role assignments on the workspace are inert (their principal no longer resolves), but pruning them is tidy:

```bash
if [ -n "$OLD_MSI" ]; then
  WS_ID=$(az monitor log-analytics workspace show -g "$RG" --workspace-name "$WS" --query id -o tsv)
  for AID in $(az role assignment list --assignee "$OLD_MSI" --scope "$WS_ID" --all --query "[].id" -o tsv); do
    echo "  Removing orphan: $AID"
    az role assignment delete --ids "$AID"
  done
fi
```

### Now redeploy

Return to §5 and follow the scripted path. The flow is:

1. **§5.1** — Portal ARM deploy of `infrastructure-arm.json`.
2. **`./post-deploy.sh "$RG" "$APP" "$WS"`** — automates §5.2, §5.3, §5.5, and the partial §5.4. Pauses once for the Designer-bind clicks.
3. **§5.7** — run `./reconcile-acl.sh "$RG" "$APP"` to clear orphan ACLs carried forward from the previous install (skip this on a brand-new tenant).
4. **§5.5** — trigger a test workflow, verify green.
5. **§5.6** — production configuration.

Total operator time on a familiar redeploy: ~15 minutes (mostly waiting for ARM, RBAC propagation, and connection-claim provisioning).

---

## A. Full workflow catalog

The 29 workflows shipped in the Standard package, by category:

### Adapter (1)

| Workflow | Trigger | Purpose |
|---|---|---|
| `GIBTIA_IndicatorProcessor_v2` | Batch | Receives STIX 2.1 indicators from every indicator collector and uploads them to Sentinel TI via the `azuresentinel` connector. Must be present before any collector runs (always is — they ship together). |

### Indicator collectors (12)

Hourly recurrence; poll a Group-IB collection, transform records into STIX 2.1 `indicator` objects, batch-send to the adapter.

| Workflow | GIB collection | Indicator types |
|---|---|---|
| `GIBTIA_IOC_Primary_Updated` | `ioc/primary/updated` | IPv4, domain, URL, MD5/SHA-1/SHA-256 |
| `GIBTIA_Malware_cnc` | `malware/cnc/updated` | IPv4, domain, URL |
| `GIBTIA_Malware_config` | `malware/config/updated` | IPv4, domain, URL |
| `GIBTIA_Attacks_phishing` | `attacks/phishing_group/updated` | IPv4, domain, URL |
| `GIBTIA_Attacks_phishing_kit` | `attacks/phishing_kit/updated` | Email addresses |
| `GIBTIA_Attacks_ddos` | `attacks/ddos/updated` | IPv4 |
| `GIBTIA_Attacks_deface` | `attacks/deface/updated` | URL |
| `GIBTIA_Suspicious_ip_tor_node` | `suspicious_ip/tor_node/updated` | IPv4 |
| `GIBTIA_Suspicious_ip_open_proxy` | `suspicious_ip/open_proxy/updated` | IPv4 |
| `GIBTIA_Suspicious_ip_socks_proxy` | `suspicious_ip/socks_proxy/updated` | IPv4 |
| `GIBTIA_Suspicious_ip_scanner` | `suspicious_ip/scanner/updated` | IPv4 |
| `GIBTIA_Suspicious_ip_vpn` | `suspicious_ip/vpn/updated` | IPv4 |

### Context collectors (14)

Hourly recurrence; poll a Group-IB collection, write raw records to a dedicated Log Analytics custom table.

| Workflow | GIB collection | Destination table |
|---|---|---|
| `GIBTIA_APT_Threats` | `apt/threat/updated` | `GIBAPTThreat_CL` |
| `GIBTIA_APT_ThreatActor` | `apt/threat_actor/updated` | `GIBAPTThreatActor_CL` |
| `GIBTIA_HI_Threat` | `hi/threat/updated` | `GIBHIThreat_CL` |
| `GIBTIA_HI_Threat_Actor` | `hi/threat_actor/updated` | `GIBHIThreatActor_CL` |
| `GIBTIA_HI_Open_Threats` | `hi/open_threats/updated` | `GIBHIOpenThreat_CL` |
| `GIBTIA_Malware_Targeted_Malware` | `malware/malware/updated` | `GIBMalwareReport_CL` |
| `GIBTIA_Compromised_account` | `compromised/account_group/updated` | `GIBCompromisedAccount_CL` |
| `GIBTIA_Compromised_BreachedDB` | `compromised/breacheddb/updated` | `GIBCompromisedBreachedDB_CL` |
| `GIBTIA_Compromised_SPD` | `compromised/spd/updated` | `GIBCompromisedSPD_CL` |
| `GIBTIA_Compromised_BankCard` | `compromised/bank_card_group/updated` | `GIBCompromisedBankCard_CL` |
| `GIBTIA_Compromised_MaskedCard` | `compromised/masked_card/updated` | `GIBCompromisedMaskedCard_CL` |
| `GIBTIA_OSI_Vulnerability` | `osi/vulnerability/updated` | `GIBOSIVulnerability_CL` |
| `GIBTIA_OSI_PublicLeak` | `osi/public_leak/updated` | `GIBOSIPublicLeak_CL` |
| `GIBTIA_OSI_GitLeak` | `osi/git_repository/updated` | `GIBOSIGitRepository_CL` |

### Enrichment playbooks (3)

Triggered by Sentinel incident webhook (not recurrence); post enrichment as incident comments.

| Workflow | Trigger | What it does | Consumption equivalent |
|---|---|---|---|
| `GIBTIA_Enrich_WHOIS` | Sentinel incident | Per-entity WHOIS via GIB + check `ThreatIntelIndicators` for known matches | Yes |
| `GIBTIA_Enrich_IOC` | Sentinel incident | Cross-collection search via `/api/v2/search`, filtered by `granted_collections`; posts hits-per-collection summary | Yes |
| `GIBTIA_Score_IP` | Sentinel incident | Batched POST to `/api/v2/scoring`; posts each IP's GIB risk score (0–100) | Also available for Consumption: `Playbooks/GIBTIA_Score_IP/azuredeploy.json` |

All shared tracking lives in `GIBCollectionTracking_CL` filtered by `CollectionName_s`.
