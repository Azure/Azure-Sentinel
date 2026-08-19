# Data Lake Onboarding Guide

## Overview

This guide covers onboarding an ISV's tenant to the Microsoft Sentinel data lake from the Microsoft Defender portal.

## Prerequisites

### Required Permissions

There are **two distinct permission gates** in the onboarding process. Both must be satisfied:

#### Gate 1: Connect Sentinel Workspace to Defender Portal (USX)

Before data lake onboarding, the Sentinel workspace must be visible/connected in the Defender portal. New workspaces normally auto-connect to USX, but auto-connect can fail if permissions are insufficient.

**Required roles (ALL conditions must be met):**
- **Security Administrator** (or higher) in Microsoft Entra ID — **ALWAYS required**
- **AND** one of the following Azure roles:
  - **Owner** (scoped to subscription), OR
  - **User Access Administrator** + **Microsoft Sentinel Contributor** (scoped to subscription, resource group, or workspace)

> ⚠️ **Note:** `Sentinel Contributor` alone is sufficient for onboarding Sentinel (enabling it on a workspace), but is NOT sufficient for connecting the workspace to USX/Defender portal.
>
> ⚠️ **User Access Administrator** is an **Azure IAM role** (assigned via Subscription > Access Control). Do NOT confuse with **User Administrator** which is a different Entra ID role.
>
> Reference: [Onboard Microsoft Sentinel to Defender](https://learn.microsoft.com/en-us/unified-secops/microsoft-sentinel-onboard)

#### Gate 2: Data Lake Onboarding (Billing + Data Ingestion Authorization)

Once the workspace is connected in Defender, the data lake setup requires:

- **Azure Subscription Owner** or **Subscription Contributor** — for billing setup
  - Must be **direct** subscription owner/contributor (management-group-level inherited ownership is NOT sufficient)
- **Microsoft Entra Global Administrator** or **Security Administrator** — for data ingestion authorization from Microsoft Entra, Microsoft 365, and Azure
- **Read access to all workspaces** to enable their attachment to the data lake
- Account must be a **tenant member** (not a guest account)

> Reference: [Required roles - Data lake onboarding](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-lake-onboarding#required-roles)

### Required Access
- Azure portal: https://portal.azure.com/
- Microsoft Defender portal: https://security.microsoft.com/

## Pre-Flight: Check for Existing Data Lake

**IMPORTANT:** Before starting the onboarding steps below, always check if the ISV already has a Sentinel workspace with data lake onboarded in their tenant.

> ⚠️ **Do NOT detect onboarding by looking for the `msg-resources-<guid>` resource group, nor by listing `Microsoft.SentinelPlatformServices/sentinelplatformservices` inside a single RG.** Both signals persist after offboarding and when the linked workspace is deleted/stale. They are not authoritative.

### Authoritative Check — Combined Signal

Run the validator script. It performs a **tenant-wide Azure Resource Graph scan** (with a per-subscription `az resource list` fallback) for the Sentinel platform resource AND verifies at least one workspace has a live `Microsoft.SecurityInsights/onboardingStates/default` (API `2025-09-01`):

```powershell
./scripts/Validate-DataLake.ps1
```

Exit codes:
- **0 — Onboarded** — platform resource exists AND ≥1 Sentinel-enabled workspace is live.
- **2 — Stale** — platform resource exists BUT no live Sentinel-enabled workspace (typical after workspace deletion or offboarding).
- **1 — NotOnboarded** — no platform resource anywhere in the tenant.

### Decision Logic

| Scenario | Action |
|----------|--------|
| **Onboarded** + ISV is okay using the existing primary workspace | **Skip data lake onboarding entirely** → proceed directly to Step 2 (Data Ingestion) |
| **Onboarded** + ISV wants a NEW workspace | This triggers **Known Issue #1**. The new workspace cannot be auto-onboarded. ISV must: (1) create workspace in same region as original, (2) contact App Assure via [intake form](https://aka.ms/intakeform). App Assure works with engineering to attach. |
| **Stale** | This triggers **Known Issue #3**. Verify the original workspace's RG and subscription have not been deleted; either restore or re-onboard via the Defender portal. |
| **NotOnboarded** | Proceed with full onboarding steps below. Use `./scripts/Validate-DataLake.ps1 -Remediate` to either pick an existing Sentinel workspace or auto-create RG + LAW + Sentinel enablement, then walk the user through the Defender portal data-lake setup. |

### Automated Permission Validation

Before starting onboarding, validate the user has all required permissions:

```powershell
# Run the pre-flight permission check
# This script checks Entra roles + Azure roles and reports any gaps
./scripts/Validate-Prerequisites.ps1 -SubscriptionId <subscription-id>
```

The script validates:
1. **Gate 1 — Defender/USX connectivity roles:**
   - If user is Subscription Owner → passes
   - If NOT Owner → checks for Microsoft Sentinel Contributor + User Access Administrator (Azure IAM roles)
2. **Gate 2 — Data Lake onboarding roles:**
   - Azure: Subscription Owner OR Subscription Contributor (must be direct, not management-group inherited)
   - Entra ID: Global Administrator OR Security Administrator — via Microsoft Graph
   - Workspace: Read access to target workspace(s)
   - Account type: tenant member (not guest)

If any permission is missing, the agent should flag it and provide remediation steps before proceeding. Missing Gate 1 permissions commonly manifest as **Known Issue #4** (workspace not visible in Defender).

## Step-by-Step Process

### Step 1: Create Log Analytics Workspace

> This step is done in the **Azure portal** (https://portal.azure.com/), NOT in Defender portal.

1. Sign in to the **Azure portal** at https://portal.azure.com/
2. Search for **Microsoft Sentinel** and select it
3. Click **Create**
4. Select **Create a new workspace**
5. Under Subscription > Resource group, select **Create new** (e.g., `sentinel-rg`)
6. Configure the workspace:
   - **Workspace name:** Enter a descriptive name (e.g., `sentinel-workspace`)
   - **Region:** Select a [Data lake supported region](https://learn.microsoft.com/en-us/azure/sentinel/geographical-availability-data-residency#supported-regions) (e.g., `East US 2` or `South Central US`)
7. Click **Review + Create** → **Create** and wait for deployment

**Can be automated via az cli:**

```bash
# Create resource group
az group create --name <rg-name> --location eastus2

# Create Log Analytics workspace
az monitor log-analytics workspace create \
  --resource-group <rg-name> \
  --workspace-name <workspace-name> \
  --location eastus2

# Enable Microsoft Sentinel on workspace
az sentinel onboarding-state create \
  --resource-group <rg-name> \
  --workspace-name <workspace-name> \
  --name default \
  --customer-managed-key false
```

**Validation:**
```bash
az monitor log-analytics workspace show \
  --resource-group <rg-name> \
  --workspace-name <workspace-name> \
  --query "{name:name, id:id, customerId:customerId, location:location}"
```

**Reference:** [Create a Log Analytics workspace - Microsoft Docs](https://learn.microsoft.com/en-us/azure/sentinel/quickstart-onboard?tabs=defender-portal#create-a-log-analytics-workspace)

---

### Step 2: Sign In to Defender Portal

1. Open browser and navigate to **https://security.microsoft.com/**
2. Sign in with credentials that have the required permissions (see Prerequisites)

---

### Step 3: Initiate Data Lake Onboarding

1. Look for a **banner at the top** of the Defender portal home page indicating you can onboard to the Microsoft Sentinel data lake
2. Click the **"Get started"** button on the banner
   - **Alternative (if banner is closed):** Navigate to **System > Settings > Microsoft Sentinel > Data lake**

> ⚠️ Do NOT go to Settings first. The banner is the primary entry point.

---

### Step 4: Connect SIEM Workspace

1. If you don't have the correct roles (see Prerequisites), the Sentinel workspace won't show up here and the subscription filter might not populate
2. Select your Workspace, then click **"Connect workspace"** and set it as **Primary**

> ⚠️ The workspace must already exist (Step 1) and be in a data lake supported region.

---

### Step 5: Setup Data Lake

1. Click **"Start setup"** under **Data lake**
   - If you don't have the correct roles, a side panel will appear indicating missing permissions
2. In the setup side panel, select your target **Subscription** from the dropdown
3. Select the target **Resource group** (this enables billing for the data lake)
4. Click the **"Set up data lake"** button

> ⚠️ This is NOT the same as "Connect workspace" from Step 4. Step 4 connects the SIEM workspace; Step 5 provisions the actual data lake infrastructure.

---

### Step 6: Monitor Onboarding Progress (up to 60 minutes)

- The setup process begins and displays a progress panel
- The onboarding process can take **up to 60 minutes** to complete
- You can safely **close the setup panel** — it runs in the background
- A banner will be displayed: **"Setup in progress"**

---

### Step 7: Validate Completion

1. Once complete, a new banner appears with information cards on how to use the data lake
2. Verify **"Data lake exploration"** is available under **Microsoft Sentinel** in the Defender portal

## Programmatic Data Lake Validation

### IMPORTANT: Run this check before proceeding to Data Ingestion phase

When the user asks to move to data ingestion, ALWAYS validate data lake status first using the combined-signal validator. **Do NOT** rely on a single-RG `az resource list` for `Microsoft.SentinelPlatformServices/sentinelplatformservices` — that resource persists after offboarding and when the linked workspace is deleted/stale.

### Combined-Signal Validator (authoritative)

```powershell
./scripts/Validate-DataLake.ps1
```

What the validator does:
1. **Tenant-wide platform resource scan** via Azure Resource Graph (`resources | where type =~ 'Microsoft.SentinelPlatformServices/sentinelplatformservices'`), falling back to per-subscription `az resource list` if Resource Graph isn't available.
2. **Workspace verification** — for each Log Analytics workspace in the tenant, GETs `Microsoft.SecurityInsights/onboardingStates/default` (API `2025-09-01`). 200 → Sentinel-enabled; 404 → not enabled.
3. **Classification:**
   - **Onboarded**: platform resource exists AND ≥1 workspace is Sentinel-enabled.
   - **Stale**: platform resource exists BUT 0 Sentinel-enabled workspaces.
   - **NotOnboarded**: no platform resource anywhere.

### How to Interpret Results

| Validator output | What it means | Action |
|---|---|---|
| **Onboarded** (exit 0) | ✅ Data lake is active and at least one workspace is Sentinel-enabled | Report the primary workspace; proceed to data ingestion (or surface Issue #1 if the user wants a brand-new workspace) |
| **Stale** (exit 2) | ⚠️ Platform resource lingers, but no live Sentinel workspace | Surface **Known Issue #3**; verify RG/sub not deleted, then re-onboard via Defender portal |
| **NotOnboarded** (exit 1) | ❌ Data lake not provisioned in this tenant | Run `./scripts/Validate-DataLake.ps1 -Remediate` to either pick an existing Sentinel workspace or auto-create RG + LAW + Sentinel enablement, then guide the user through the Defender portal data-lake setup |

### Why `provisioningState: Succeeded` is NOT enough

The legacy quick check (`az resource list ... --resource-type Microsoft.SentinelPlatformServices/...`) returned `provisioningState: Succeeded` even when:
- The tenant had been offboarded from the data lake.
- The originally-linked Log Analytics workspace had been deleted.
- The resource group `msg-resources-<guid>` was still present but the data path was non-functional.

`provisioningState` is a create-time outcome; it does not reflect the live data-lake state. **Always combine the platform resource scan with a workspace-level `onboardingStates/default` check.**

### Remediation Modes

```powershell
# Detect only (no changes):
./scripts/Validate-DataLake.ps1

# Detect + guided remediation (prompts to pick an existing workspace OR auto-creates RG/LAW/Sentinel):
./scripts/Validate-DataLake.ps1 -Remediate

# Override the auto-create defaults (used only on the NotOnboarded + no-Sentinel-workspaces path):
./scripts/Validate-DataLake.ps1 -Remediate -SubscriptionId <sub-id> -ResourceGroupName <rg> -WorkspaceName <ws> -Location eastus2
```

### Data Lake Resource Details (when found)
- **Resource type:** `Microsoft.SentinelPlatformServices/sentinelplatformservices`
- **Name pattern (informational only):** Typically lives in an auto-generated RG named `msg-resources-<guid-prefix>`. ⚠️ **Do not use this RG name pattern as a detection signal** — it persists after offboarding. Use the combined-signal validator instead.
- **API version:** `2025-04-01-preview` (for the platform resource itself); `2025-09-01` for `Microsoft.SecurityInsights/onboardingStates`.
- **Identity:** SystemAssigned managed identity with Azure Reader role.
- **Location:** Fixed to the primary workspace's region at onboarding time.

### Agent Behavior: Pre-Ingestion Gate

When a user says "help me with data ingestion", "ingest data", "create custom table", or any data ingestion intent:

1. **RUN** `./scripts/Validate-DataLake.ps1` (no parameters needed for detection).
2. **IF Onboarded** → confirm primary workspace + region with the user, then proceed to data ingestion guidance.
3. **IF Stale** → surface Known Issue #3, walk through cleanup/re-onboarding, do not proceed to ingestion.
4. **IF NotOnboarded** → re-run with `-Remediate`; let the validator pick an existing workspace or auto-create one, then walk through the Defender portal data-lake setup (Steps 2–6). Do not proceed to ingestion until a re-run reports **Onboarded**.

---

## Legacy Validation (Sentinel only, NOT data lake)

```bash
# Check if Sentinel is enabled (does NOT confirm data lake)
az sentinel onboarding-state show \
  --resource-group <rg-name> \
  --workspace-name <workspace-name> \
  --name default

# Check workspace details
az monitor log-analytics workspace show \
  --resource-group <rg-name> \
  --workspace-name <workspace-name>
```

## Troubleshooting

| Issue | Resolution |
|-------|-----------|
| Workspace not visible in Defender portal | Check you have all three required permission sets |
| "Missing permissions" side panel | Ensure Security Admin in Entra + Subscription Owner (or UAA + Sentinel Contributor if not Owner) |
| Onboarding stuck | Wait full 60 minutes; check for Azure service health issues |
| Region not available | Verify region is in data lake supported regions list |

## Region Guidance

- **Recommended:** East US 2 (fastest, best support)
- **Capacity Restricted:** East US, Central US, South Central US, West US 2 (may require additional time)
- **Important:** Data lake region must match workspace region
- **For East US:** Submit AppAssure Intake form at https://aka.ms/intakeform

## Known Issues & Troubleshooting

### Issue 1: Can't onboard a new workspace after tenant is already onboarded

**Scenario:** During Sentinel platform solution development, you may delete and recreate workspaces and then try to onboard a newly created workspace to the data lake.

**Key fact:** Once the tenant is onboarded to the data lake, ANY workspaces created after that CANNOT be automatically onboarded to the data lake — regardless of whether they are in the same region or a different region. This is not self-service.

**What to do:**
1. The new workspace MUST be created in the same region as the workspace that was initially onboarded to the data lake (this is a hard pre-requisite — all data lake workspaces must be co-located in the same region)
2. ISV must reach out to the App Assure team via the [intake form](https://aka.ms/intakeform)
3. The App Assure team will work internally with the engineering team to attach the new workspace to the data lake

**Agent Behavior:** If the ISV already has a workspace with data lake active, ask if they are okay using that existing workspace for development. If yes → skip data lake onboarding entirely and proceed to data ingestion (Step 2). If they need a new workspace → explain this limitation and direct them to submit the App Assure intake form.

---

### Issue 2: Capacity limitations in specific regions

**Symptom:** Onboarding doesn't complete in specific regions due to capacity constraints.

**What to do:** Use an alternate supported region instead:
1. Delete the current Log Analytics workspace
2. Create a new workspace in a different region (e.g., East US 2)
3. Attach it to Microsoft Sentinel
4. Connect it as the Primary workspace in the Defender portal
5. Set up data lake

If your organization doesn't have a hard requirement to onboard in the affected region, use an alternate. If you must use the constrained region, ISVs can reach out to the App Assure team via the [intake form](https://aka.ms/intakeform) for assistance.

---

### Issue 3: "Something went wrong, Please try again" during setup

**Symptom:** In the Defender portal, after selecting "Set up data lake", the setup flow doesn't complete and you see: *"Something went wrong, Please try again"*.

**Common things to check:**
- Was the resource group associated with the onboarded Sentinel workspace deleted previously?
- Was the subscription used for data lake billing deleted or canceled?

**What to do:** ISVs can reach out to the App Assure team via the [intake form](https://aka.ms/intakeform) for assistance.

---

### Issue 4: Sentinel workspace not visible in Defender (or subscription filter shows "Undefined")

**Scenario:** You created a Log Analytics workspace and added Sentinel, but the Defender portal doesn't show the workspace (or UI filters don't populate correctly).

**Root Cause:** The workspace has not been connected to USX (Unified Security Operations / Defender portal). This happens when:
- Auto-connect to USX failed due to insufficient permissions at workspace creation time
- The user performing the action lacks Gate 1 permissions (see Prerequisites)

**Key insight (from Sentinel engineering):** `Sentinel Contributor` role alone is sufficient for **enabling Sentinel** on a workspace (adding the solution), but is **NOT sufficient for connecting the workspace to USX/Defender portal**. This is the most common root cause of auto-connect failures.

**What to do:**

1. Verify the user has **Gate 1 permissions** for Defender/USX onboarding:
   - **Security Administrator** (or higher) in Microsoft Entra ID — ALWAYS required
   - **AND** one of: **Subscription Owner** OR (**User Access Administrator** + **Microsoft Sentinel Contributor**)

2. **Sentinel Reader role** is sufficient to SEE the workspace listed in Defender settings, but is NOT sufficient for onboarding/connecting it.

3. If permissions are correct but workspace still doesn't appear:
   - Verify workspace is in a [data lake supported region](https://learn.microsoft.com/en-us/azure/sentinel/geographical-availability-data-residency#supported-regions)
   - Try manually connecting via: Settings > Microsoft Sentinel > Connect a workspace

4. **Important:** `User Access Administrator` is an **Azure IAM role** (assigned via Subscription > Access Control / IAM). Do NOT confuse with `User Administrator` which is a different Entra ID role.

5. Reference: [Connect Microsoft Sentinel to the Defender portal](https://learn.microsoft.com/en-us/unified-secops/microsoft-sentinel-onboard)

Use the automated permission checks (`Validate-Prerequisites.ps1`) to identify which specific role is missing.

---

## References

- [Microsoft Docs - Onboard to Sentinel data lake](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-lake-onboard-defender)
- [Supported Regions](https://learn.microsoft.com/en-us/azure/sentinel/geographical-availability-data-residency#supported-regions)
- [App Assure Intake Form](https://aka.ms/intakeform)
