# Deploying the connector

This guide installs a connector from zero. It's written so you can follow it without ever having deployed anything in Azure before. Veterans: the [Azure CLI section](#deploying-with-the-azure-cli) is probably what you want.

> ✅ **Before you start**, make sure you've got everything on the [permissions checklist](02-permissions.md#permissions-checklist). The two things people forget: a **Trend Vision One API token** and knowing your **region**.

---

## Decide two things first

### 1. Which connector(s)?

Workbench, OAT, or both? If you're unsure, [this section](01-concepts.md#workbench-vs-oat-which-one-do-i-want) helps you choose. You can always add the other one later.

### 2. Connect now, or connect later?

The deployment form has an **optional API token field**. This is a genuine fork in the road:

| Choice | What happens | Pick this if… |
|--------|--------------|---------------|
| **Enter the token at deploy time** | Everything deploys **and** the poller starts pulling data immediately. One-and-done. | You have the token ready and want data flowing right away. |
| **Leave the token blank** | Everything deploys *except* the live poller. You connect afterward from the Sentinel portal. | The person deploying isn't the person who holds the token, or you want to separate "infra" from "secrets." |

Both are fully supported. This guide covers both.

---

## Option 1 — Deploy with the "Deploy to Azure" button (recommended)

This is the point-and-click path.

### Step 1 — Click the button

In the main [README](../README.md#-quick-deploy), click **Deploy to Azure** next to the connector you want. Your browser opens the Azure Portal with the deployment form pre-loaded.

> If you see a sign-in prompt, log in with the Azure account that has the [permissions](02-permissions.md) from the checklist.

### Step 2 — Fill in the form

You'll see a custom form. Here's every field and what to put:

| Field | What to enter | Notes |
|-------|---------------|-------|
| **Subscription** | The Azure subscription that holds your Sentinel workspace | If you only have one, it's pre-selected |
| **Resource group** | Pick an existing one, or create a new one like `rg-sentinel-trend` | A dedicated group keeps things tidy and easy to clean up |
| **Region / Location** | The **Azure** region of your workspace | This is the *Azure* region, not the Trend region — keep them the same as your workspace |
| **Workspace** | Choose your Sentinel workspace from the dropdown | The dropdown lists workspaces in the selected resource group |
| **Trend Vision One Region** | The region your **Trend** tenant lives in: US, UK, SG, CA, or JP | Must match your tenant — wrong region = no data. See [regions](04-using-the-connector.md#regions-and-api-endpoints) |
| **Trend Vision One API Token** | *(optional)* Paste the **raw** token — **no** `Bearer ` prefix | Leave blank to connect later. See the [prefix gotcha](02-permissions.md#the-bearer--prefix-gotcha) |
| **Optional TMV1-Filter** *(Workbench)* | *(optional)* A filter expression, e.g. `(severity ge 'high')` | Limits which alerts are pulled. Leave blank for everything. See [filters](04-using-the-connector.md#filtering-what-gets-ingested) |
| **OAT Filter** *(OAT)* | *(optional)* e.g. `(riskLevel eq 'high')` | Same idea, for OAT |
| **Exclude third-party OAT** *(OAT)* | Defaults to **on (true)** | Drops detections that came from non-Trend linked sources. Leave on unless you specifically want them |

### Step 3 — Review and create

1. Click **Review + create**.
2. Azure validates the form. If it complains, fix the highlighted field and try again.
3. Click **Create**.
4. Wait. Deployment takes about **3–5 minutes**. You'll see a "Deployment in progress" screen, then "Your deployment is complete."

### Step 4 — If you left the token blank, connect now

*(Skip this if you entered the token at deploy time — you're already connected.)*

1. Go to **Microsoft Sentinel → Data connectors**.
2. Search for **"Trend Vision One - Workbench Alerts"** or **"Trend Vision One - OAT"**.
3. Click it, then **Open connector page**.
4. In the **API Token** box, paste your token **with** the `Bearer ` prefix:
   `Bearer eyJhbGciOi...`
5. Click **Connect**.

> 🔁 **Two different token formats!** Deploy-time field = **no** prefix. Connector page = **with** `Bearer ` prefix. This catches everyone once.

### Step 5 — Confirm it worked

Jump to [Using the connector → Verify data is flowing](04-using-the-connector.md#step-1-confirm-data-is-arriving). Data appears within **5–10 minutes** of connecting.

---

## Option 2 — Deploying with the Azure CLI

For automation, repeatable deployments, or if you just prefer a terminal.

### Prerequisites

```bash
# Install the Azure CLI if you don't have it
#   macOS:  brew install azure-cli
#   Other:  https://learn.microsoft.com/cli/azure/install-azure-cli

az login
az account set --subscription "<your-subscription-name-or-id>"
```

### Deploy Workbench

```bash
az deployment group create \
  --resource-group <your-rg> \
  --template-uri https://raw.githubusercontent.com/trendmicro/trendai-sentinel-ccf-data-connector/main/templates/workbench/mainTemplate.json \
  --parameters \
      workspace=<workspace-name> \
      trendaiRegion=US
```

### Deploy OAT

```bash
az deployment group create \
  --resource-group <your-rg> \
  --template-uri https://raw.githubusercontent.com/trendmicro/trendai-sentinel-ccf-data-connector/main/templates/oat/mainTemplate.json \
  --parameters \
      workspace=<workspace-name> \
      trendaiRegion=US
```

### Connecting at deploy time via CLI (optional)

Add the API token to start the poller immediately. **Use the raw token, no `Bearer ` prefix.** Never hard-code a secret — read it from an environment variable or Key Vault:

```bash
az deployment group create \
  --resource-group <your-rg> \
  --template-uri https://raw.githubusercontent.com/trendmicro/trendai-sentinel-ccf-data-connector/main/templates/workbench/mainTemplate.json \
  --parameters \
      workspace=<workspace-name> \
      trendaiRegion=US \
      apikey="$TREND_API_TOKEN" \
      workbenchFilter="(severity ge 'high')"
```

### All available parameters

| Parameter | Applies to | Default | Meaning |
|-----------|------------|---------|---------|
| `workspace` | both | *(required)* | Log Analytics / Sentinel workspace name |
| `workspace-location` | both | resource group's location | Azure region of the workspace |
| `trendaiRegion` | both | `US` | Trend region: `US`, `UK`, `SG`, `CA`, `JP` |
| `apikey` | both | *(empty)* | Raw Trend API token. Empty = deploy without the poller |
| `workbenchFilter` | Workbench | *(empty)* | TMV1-Filter expression for Workbench alerts |
| `oatFilter` | OAT | *(empty)* | TMV1-Filter expression for OAT detections |
| `excludeThirdPartyOat` | OAT | `true` | Drop detections from third-party linked sources |

---

## What got created (so you can find it later)

After a successful Workbench deploy, your resource group contains:

- A custom table: `TrendMicro_XDR_WORKBENCH_CL`
- A Data Collection Endpoint and a Data Collection Rule
- The connector definition (visible under Sentinel → Data connectors)
- A parser function: `TrendMicroWorkbench_Complete()`
- An analytic rule (named *"Trend Vision One - Create Incident for Workbench Alerts"*), **disabled** by default
- A workbook: *"TrendVisionOneWorkbenchOverview"*

OAT deploys the table (`TrendMicro_XDR_OAT_CL`), DCE, DCR, connector definition, and a parser function: `TrendMicroOAT_Complete()`. (OAT does not ship its own analytic rule or workbook — see [usage](04-using-the-connector.md).)

The Azure Portal also prints a **"Deployment complete"** message in the outputs with these same next steps.

---

## Deploying both connectors

Just run the process twice — once per connector. They share nothing that conflicts, and you can deploy them into the same resource group and workspace.

---

## Government cloud (Azure US Gov)

The README includes separate **Deploy to Azure US Gov** buttons that target `portal.azure.us`. Use those instead of the commercial buttons if your Sentinel runs in Azure Government. Everything else in this guide is identical.

---

## Next steps

- ✅ [Verify data is flowing and learn to query it](04-using-the-connector.md)
- ❌ No data after 10 minutes? → [Troubleshooting](06-troubleshooting.md)
