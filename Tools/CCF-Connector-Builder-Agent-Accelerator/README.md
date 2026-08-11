# Sentinel CCF Pull Connector Builder – Lab Guide

## What Is This?

This accelerator lets you deploy a working REST API and build a Microsoft Sentinel CCP (Codeless Connector Platform) pull connector against it — with no code required.

It works by deploying a pre-built Network Log API as an Azure Function App (one-click via ARM template), then using a GitHub Copilot agent to read the API documentation and automatically generate the four CCP connector files: connector definition, DCR, table schema, and polling config. The result is a fully functional Sentinel data connector that ingests data from the API into a custom Log Analytics table.

This is designed as both a learning accelerator and a reusable pattern — replace the Network Log API with any REST API to build a real connector using the same workflow.

---

## GitHub Copilot Quick Deploy

### Before You Start

| Requirement | Details |
|---|---|
| **VS Code** | With the [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot-chat) extension installed and signed in |
| **Azure CLI** | Installed and logged in (`az login`). [Install guide](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) |
| **Azure subscription** | With **Contributor** role on the resource group where the Function App will be deployed |
| **Microsoft Sentinel workspace** | Already deployed. [Quickstart](https://learn.microsoft.com/en-us/azure/sentinel/quickstart-onboard) |
| **This repo cloned locally** | Agent reads `agent-instructions.md` and deploys the Function App and connector from disk |

> Full prerequisites (provider registration, permission breakdown, etc.) are in the [Prerequisites](#prerequisites) section below.

---

Paste the following into **GitHub Copilot Chat** in VS Code (Agent mode):

```
Load and follow the deployment instructions at
Sentinel-CCF-Pull-Connector-Builder-Agent-Accelerator/agent-instructions.md. Let's deploy the Network Log API and build a CCF pull connector.
```

The agent will collect all required values interactively — offering to look up or generate
any values you haven't specified — then deploy the Function App, run the CCF Connector Builder
Agent, and verify each step automatically.

> Full agent instructions: [`agent-instructions.md`](./agent-instructions.md)

---

This repository contains a **mock Network Log API** (Azure Function App) and a complete lab
environment for building and testing [Microsoft Sentinel Codeless Connector Framework (CCF)](https://learn.microsoft.com/en-us/azure/sentinel/create-codeless-connector)
pull connectors — using the **API Poller** kind.

The lab walks through three phases:
1. Deploy a live API serving realistic network log data (firewall events, brute-force blocks, C2 detections)
2. Use the **Sentinel CCF Connector Builder Agent** to auto-generate the full connector package from the API documentation
3. Deploy and validate the connector end-to-end in a live Sentinel workspace

---

## What is a CCF Pull Connector?

The [Codeless Connector Framework (CCF)](https://learn.microsoft.com/en-us/azure/sentinel/create-codeless-connector) lets ISV partners integrate log sources into Microsoft Sentinel without deploying infrastructure. The **API Poller** kind uses a polling pattern:

1. Sentinel periodically calls your **HTTP API endpoint** using configured auth and pagination
2. Each response page is parsed using the configured **events JSON path**
3. Records are sent to a **Data Collection Rule (DCR)** for transformation
4. The DCR writes rows to your custom **Log Analytics table**
5. On subsequent polls, the **`since` query parameter** is used for incremental / delta pulls

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Network Log API (Azure Function App)                    │
│  GET /api/GetNetworkLogs?page=N&since=<ISO8601>          │
│  Auth: X-API-Key header                                  │
└───────────────────────────┬──────────────────────────────┘
                            │  HTTP 200 JSON (paginated)
                            ▼
┌──────────────────────────────────────────────────────────┐
│  Microsoft Sentinel CCF API Poller                       │
│  (polls on schedule, follows nextLink pagination,        │
│   passes since= for incremental pulls)                   │
└───────────────────────────┬──────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────┐
│  Data Collection Rule (DCR)                              │
│  KQL transform → project, type-cast, TimeGenerated       │
└───────────────────────────┬──────────────────────────────┘
                            │
                            ▼
              NetworkLogAPINetworkLogs_CL
          (Log Analytics custom table)
```

---

## Repository Structure

```
├── AzureFunctionNetworkLogAPI/
│   ├── function_app.py               # Python Azure Function – two HTTP endpoints
│   ├── host.json                     # Azure Functions host configuration
│   ├── requirements.txt              # Python dependencies
│   └── NetworkLogAPI.zip             # Pre-built deployment package
├── sentinel-connectors/
│   └── NetworkLogAPI_CCF/            # Generated CCF connector package
│       ├── NetworkLogAPI_PollingConfig.json      # API poller config (auth, pagination, DCR)
│       ├── NetworkLogAPI_Table.json              # Custom Log Analytics table schema
│       ├── NetworkLogAPI_DCR.json                # Data Collection Rule
│       └── NetworkLogAPI_ConnectorDefinition.json  # Connector UI definition
├── azuredeploy_NetworkLogAPI.json    # ARM template – deploys the Function App
├── agent-instructions.md             # GitHub Copilot agent deployment instructions
├── NetworkLogAPI_API_Documentation.md  # Full API reference (input for CCF agent)
└── README.md                         # This file – lab guide
```

---

## Prerequisites

### Azure Permissions

> You need **Contributor** role on the resource group where the Function App will be deployed.

| Action | Step | Required Role |
|---|---|---|
| Create resource group | Step 3 | Contributor on subscription or existing RG |
| Deploy Function App ARM template | Step 5 | Contributor on the target resource group |
| Deploy CCF connector to Sentinel | Step 8 | Microsoft Sentinel Contributor on Sentinel workspace RG |
| Query Log Analytics | Step 9 | Log Analytics Reader (or above) |

**Recommended:** Contributor on the subscription where the Function App will be deployed, plus Microsoft Sentinel Contributor on the Sentinel workspace resource group.

### Tooling

| Requirement | Notes |
|---|---|
| **VS Code** | With [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot-chat) and [AI Toolkit](https://marketplace.visualstudio.com/items?itemName=ms-windows-ai-studio.windows-ai-studio) extensions |
| **Azure CLI** | [Install guide](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) — verify with `az --version`, log in with `az login` |
| **Git** | For cloning this repository |

### Azure Resources

- **Azure subscription** — with Contributor access (see above)
- **Microsoft Sentinel workspace** — already deployed. [Quickstart: Onboard Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/quickstart-onboard)

If you need to create a new workspace via CLI:

```bash
az monitor log-analytics workspace create \
  --workspace-name <workspace-name> \
  --resource-group <resource-group> \
  --location centralus \
  --output table
```

### Provider Registration

Ensure the following providers are registered in your subscription:

```bash
az provider register --namespace Microsoft.Web --wait
az provider register --namespace Microsoft.Insights --wait
az provider register --namespace Microsoft.SecurityInsights --wait
```

---

## Step 1 – Clone the Repository

```bash
git clone https://github.com/robertmoriarty12/Sentinel-CCF-Pull-Connector-Builder-Agent-Accelerator.git
cd Sentinel-CCF-Pull-Connector-Builder-Agent-Accelerator
```

---

## Step 2 – Log in to Azure

```bash
az login
```

If MFA or a specific tenant is required, use the device code flow:

```bash
az login --tenant <your-tenant-id> --use-device-code
```

Set your target subscription and verify:

```bash
az account set --subscription "<your-subscription-name-or-id>"
az account show --query "{name:name, id:id}" -o table
```

---

## Step 3 – Create a Resource Group

```bash
az group create --name connectorBuilderAgent --location centralus
```

> **Region tip:** Deploy to **Central US** (`centralus`). If you encounter `SubscriptionIsOverQuotaForSku` errors in East US, Central US reliably has Consumption plan capacity. The Function App ARM template uses an implicit hosting plan (no explicit `serverfarms` resource) to avoid SKU-level quota checks — see [ARM template pattern note](#why-no-explicit-hosting-plan) below.

---

## Step 4 – Get Your Log Analytics Workspace Resource ID

You will need this when deploying the ARM template for Application Insights.

```bash
az monitor log-analytics workspace show \
  --name <your-workspace-name> \
  --resource-group <workspace-resource-group> \
  --query id -o tsv
```

Copy the output — it looks like:
```
/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.OperationalInsights/workspaces/<name>
```

---

## Step 5 – Deploy the Function App

- **`<your-api-key>`** – A secret string (≥ 8 characters). Callers supply this in the `X-API-Key` header. Save it — you will need it for CCF connector configuration.
- **`<workspace-resource-id>`** – The value from Step 4.

### Option A — Deploy via Azure Portal (ARM template)

1. Open the [Azure Portal](https://portal.azure.com) and search for **"Deploy a custom template"**
2. Click **Build your own template in the editor**, paste the contents of `azuredeploy_NetworkLogAPI.json`, and click **Save**
3. Fill in the parameters:

   | Parameter | Description | Example |
   |---|---|---|
   | **Resource Group** | Use `connectorBuilderAgent` (create new or existing) | `connectorBuilderAgent` |
   | **Api Key** | Your API key (≥ 8 chars) | `mySecretKey123` |
   | **App Insights Workspace Resource ID** | Full resource ID from Step 4 | `/subscriptions/.../workspaces/<name>` |
   | **Function App Location** | Azure region | `eastus` |

4. Click **Review + create** → **Create**

After deployment, note the **Outputs** tab for `FunctionAppName` and `GetNetworkLogsEndpoint`.

### Option B — Deploy via Azure CLI

```bash
az deployment group create \
  --name "NetworkLogAPI-Deploy" \
  --resource-group connectorBuilderAgent \
  --template-file azuredeploy_NetworkLogAPI.json \
  --parameters \
      ApiKey="<your-api-key>" \
      AppInsightsWorkspaceResourceID="<workspace-resource-id>" \
      FunctionAppLocation="eastus"
```

> ⚠️ Always pass `FunctionAppLocation` explicitly. If the resource group exists in a different region than where you want the Function App, this parameter overrides the RG location.

Deployment takes approximately 2–3 minutes. Capture the outputs:

```bash
az deployment group show \
  --name "NetworkLogAPI-Deploy" \
  --resource-group connectorBuilderAgent \
  --query "properties.outputs" -o json
```

| Output Key | Description |
|---|---|
| `FunctionAppName` | Deployed Function App name (with unique suffix) |
| `FunctionAppUrl` | Base URL |
| `GetNetworkLogsEndpoint` | Full URL for the data endpoint |
| `RefreshDataEndpoint` | Full URL for the refresh endpoint |

---

## Step 6 – Verify the API

The ARM template automatically configures CORS to allow `https://portal.azure.com`, so you can test the function directly from the Azure Portal (Function App → Functions → select a function → **Test/Run**) and view live logs in the browser via **Log stream**.

Test the endpoint from the CLI using the Function App name and API key from Step 5:

```bash
curl -s -H "X-API-Key: <your-api-key>" \
  "https://<FunctionAppName>.azurewebsites.net/api/GetNetworkLogs?page=1&pageSize=5"
```

You should receive a JSON response with 5 network log records and pagination metadata:

```json
{
  "status": "success",
  "metadata": {
    "totalCount": 50,
    "page": 1,
    "pageSize": 5,
    "totalPages": 10,
    "hasNextPage": true,
    "nextLink": "https://<FunctionAppName>.azurewebsites.net/api/GetNetworkLogs?page=2&pageSize=5"
  },
  "data": [ ... ]
}
```

A `401 Unauthorized` response means the `X-API-Key` value does not match what was set during deployment.

---

## Step 7 – Review the API Documentation

Open [NetworkLogAPI_API_Documentation.md](./NetworkLogAPI_API_Documentation.md).

This document is structured for CCF connector development and covers:

- **Authentication** – `X-API-Key` header
- **Pagination** – offset/page-based with `nextLink`
- **Incremental Pull** – `since` query parameter for delta ingestion
- **Data Schema** – all 20 fields with types and enum values
- **CCF API Poller Configuration** – ready-to-use settings and sample connector JSON

---

## Step 8 – Build the CCF Connector with the Sentinel Connector Builder Agent

This lab uses the **Sentinel CCF Connector Builder Agent** — an AI agent in VS Code (via AI Toolkit) that reads your API documentation and automatically generates the full CCF connector package.

### What the agent generates

Pointing the agent at `NetworkLogAPI_API_Documentation.md` produces four files in `sentinel-connectors/NetworkLogAPI_CCF/`:

| File | Purpose |
|---|---|
| `NetworkLogAPI_PollingConfig.json` | API poller config — auth, endpoint, pagination, incremental pull, DCR stream |
| `NetworkLogAPI_Table.json` | Custom Log Analytics table schema (`NetworkLogAPINetworkLogs_CL`) |
| `NetworkLogAPI_DCR.json` | Data Collection Rule — stream declarations, KQL transform, workspace destination |
| `NetworkLogAPI_ConnectorDefinition.json` | Connector UI — title, description, graph queries, sample queries, instruction steps |

These files are already committed to this repo under `sentinel-connectors/NetworkLogAPI_CCF/` as a reference output.

### How to run the agent

Paste the following into **GitHub Copilot Chat** in VS Code (Agent mode):

```
@sentinel /create-connector build me a connector based on the api documentation published here Sentinel-CCF-Pull-Connector-Builder-Agent-Accelerator\NetworkLogAPI_API_Documentation.md
```

If the agent asks for additional details, provide:
- **Base URL:** `https://<FunctionAppName>.azurewebsites.net` (from Step 5 outputs)
- **API key header:** `X-API-Key`

The agent will walk through each step — polling config, table schema, DCR, and connector definition — generating and validating each file automatically.

Review the generated files in `sentinel-connectors/NetworkLogAPI_CCF/` before deploying.

### Deploy the connector to a Sentinel workspace

Once the connector files are generated, you can deploy directly from VS Code — no CLI required:

1. In the VS Code Explorer, navigate to any file in `sentinel-connectors/NetworkLogAPI_CCF/`.
2. Right-click the file and select **Deploy Connector** (provided by the Sentinel Connector Builder Agent).
3. Follow the prompts to select your Azure subscription and target Sentinel workspace.
4. The agent will deploy all four connector files (polling config, table, DCR, and connector definition) to the workspace in the correct order.

> Once deployed, the connector will appear in Microsoft Sentinel under **Content Hub / Data Connectors**.

### Test the connector connection

Before deploying to Sentinel, you can validate that the connector can successfully reach your API directly from VS Code:

1. In the VS Code Explorer, right-click any file in `sentinel-connectors/NetworkLogAPI_CCF/`.
2. Select **Test Connector** from the context menu.
3. The agent reads your `NetworkLogAPI_PollingConfig.json` and establishes a live connection to the API using the auth, endpoint, pagination, and incremental pull settings defined by the connector builder agent.
4. A test result will confirm whether the API responded successfully, returned data at the expected JSON path (`$.data`), and that pagination (`$.metadata.nextLink`) resolved correctly.

> This is useful for catching config issues — wrong base URL, incorrect API key header name, or a mismatched events path — before the connector is deployed to a workspace.

### Key connector settings (for reference)

| CCF Setting | Value |
|---|---|
| Auth Type | `APIKey` |
| API Key Header | `X-API-Key` |
| Endpoint | `https://<FunctionAppName>.azurewebsites.net/api/GetNetworkLogs` |
| Pagination Type | `NextPageUrl` |
| Next Page URL Path | `$.metadata.nextLink` |
| Has Next Page Path | `$.metadata.hasNextPage` |
| Events Array Path | `$.data` |
| Timestamp Field | `timestamp` |
| Incremental Param | `since` |
| Custom Table | `NetworkLogAPINetworkLogs_CL` |

---

## Step 9 – Enable the Connector in Microsoft Sentinel

After deploying the connector package (Step 8), activate it from within the Sentinel workspace:

1. In the [Azure Portal](https://portal.azure.com), navigate to your **Microsoft Sentinel** workspace.
2. Go to **Content Hub** → **Data Connectors** and find **NetworkLogAPI**.
3. Click **Open connector page**.
4. In the connector configuration panel, fill in the two required fields:
   - **Base URL** – the Function App base URL from Step 5, e.g. `https://<FunctionAppName>.azurewebsites.net`
   - **API Key** – the `ApiKey` value you set during deployment
5. Click **Connect**.
6. Use the **Test Connectivity** button to confirm a successful connection — a green status indicates the connector reached your API and validated the response correctly.

Once connected, data will begin appearing in the `NetworkLogAPINetworkLogs_CL` table in Log Analytics. Allow **5–20 minutes** for the first records to land.

You can verify ingestion with this query in Log Analytics:

```kusto
NetworkLogAPINetworkLogs_CL
| sort by TimeGenerated desc
| take 10
```

---

## Step 10 – Refresh Data (Optional)

Regenerate all 50 records with fresh timestamps to simulate a new batch of events:

```bash
curl -s -X POST -H "X-API-Key: <your-api-key>" \
  "https://<FunctionAppName>.azurewebsites.net/api/RefreshData"
```

---

## Updating the Function App Code

If you modify `function_app.py`, rebuild the zip, push it to GitHub, then restart the app:

```bash
# Rebuild the zip (run from repo root)
cd AzureFunctionNetworkLogAPI
zip -r NetworkLogAPI.zip function_app.py host.json requirements.txt
cd ..

# Commit and push
git add AzureFunctionNetworkLogAPI/NetworkLogAPI.zip
git commit -m "Update function app package"
git push

# Restart the Function App to load the new package
az webapp restart --name <FunctionAppName> --resource-group connectorBuilderAgent
```

---

## Troubleshooting

> 📖 For Function App diagnostics, use **Function App → Log stream** or the **Code + Test** panel in the Azure Portal.

| Symptom | Likely Cause | Fix |
|---|---|---|
| `SubscriptionIsOverQuotaForSku` on deployment | Region capacity issue for Consumption plan | Deploy to `centralus` instead of `eastus` |
| `401 Unauthorized` from API | Wrong or missing `X-API-Key` header | Verify the key matches `ApiKey` set during ARM deployment |
| `401 Unauthorized` from Azure Portal Test/Run | Portal uses a different key scope | Use **Selected key: `_master`** (host key) in the Test/Run panel |
| Empty `data` array in API response | `since` filter excludes all records | Records have rolling timestamps ~48 h behind current time — omit `since` for initial test |
| Connector not visible in Sentinel Content Hub | Files not yet deployed, or wrong workspace | Re-run the connector deploy step targeting the correct workspace |
| No data after 20+ minutes | CCF poller hasn't run yet, or config mismatch | Verify `eventsJsonPaths`, `nextLinkPath`, and `hasNextPagePath` in `PollingConfig.json` match the API response structure |
| DLQ messages / ingestion errors | Schema mismatch between DCR and table | Ensure all fields in `NetworkLogAPI_DCR.json` `streamDeclarations` match `NetworkLogAPI_Table.json` columns |
| `403` when deploying connector from VS Code | Insufficient Sentinel permissions | Assign **Microsoft Sentinel Contributor** on the Sentinel workspace resource group |

---

## Why No Explicit Hosting Plan?

The Function App ARM template (`azuredeploy_NetworkLogAPI.json`) intentionally omits the `Microsoft.Web/serverfarms` resource. Explicitly declaring a Linux Consumption (Y1/Dynamic) plan causes ARM to validate the SKU against regional capacity, which fails in high-demand regions like East US with a quota error — even when capacity is actually available. By omitting the serverfarm, Azure assigns the Function App to Consumption tier implicitly without triggering the SKU-level quota check. This matches the pattern used by Microsoft Sentinel solutions in the official repository.

---

## Cleaning Up

```bash
az group delete --name connectorBuilderAgent --yes --no-wait
```

---

## API Key Security Note

The API key is stored as an encrypted Azure App Setting (`NETWORK_LOG_API_KEY`). It is never logged or returned in any response. Treat it like a password.
