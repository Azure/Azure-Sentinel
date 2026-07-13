# Sentinel CCF Pull Connector Builder — Agent Deployment Instructions

> For GitHub Copilot. Load this file when a user pastes the trigger prompt and follow the steps below exactly.

---

## Step 0 — Collect Deployment Values

**Start here every time.** Before taking any deployment action, work through the four values below.

**Default behaviour when a value is missing**: present the user with clear options inline in Copilot Chat — including a "generate / look up for me" option wherever applicable. Collect **all four values** and print the confirmation table before executing any `az` command.

---

### 1. Azure Subscription

- Run to see available subscriptions and let the user choose:
  ```powershell
  az account list --query "[].{name:name, id:id, isDefault:isDefault}" -o table
  ```
- If only one subscription exists (or one is marked `isDefault: True`), confirm it with the user rather than assuming.

---

### 2. Sentinel Workspace + Resource Group

If not provided, ask: *"Do you have an existing Sentinel workspace, or should I create a new one?"*

**Existing workspace** — list and let the user pick:
```powershell
az monitor log-analytics workspace list `
  --query "[].{name:name, resourceGroup:resourceGroup, location:location}" -o table
```
Derive `workspace-rg` and `location` from the chosen row — do not ask again.

**New workspace** — generate unique names using a random suffix and ask the user to confirm or change them:
```powershell
$suffix = -join ((97..122) | Get-Random -Count 6 | ForEach-Object { [char]$_ })
Write-Host "Suggested workspace: ccfpull-ws-$suffix"
Write-Host "Suggested RG:        ccfpull-rg-$suffix"
Write-Host "Suggested FA RG:     ccfpull-fa-$suffix"
```
Use `$suffix` for **all** generated resource names in this session — workspace, workspace RG, and Function App RG.
- See **Region** below for location.

---

### 3. Region / Location

Always ask explicitly: *"Which Azure region should I deploy to? (e.g. `eastus`, `centralus`, `westeurope`)"*

- **Existing workspace** — show the workspace's current location as the default, but still ask: *"Your workspace is in `<location>` — use the same region for the Function App?"*
- **New workspace + RG** — if the suggested RG already exists (name collision), generate a new suffix and re-suggest. Check first:
  ```powershell
  az group show --name ccfpull-rg-$suffix --query location -o tsv 2>$null
  ```
  If it exists, generate a new suffix. If it does not exist, confirm the name with the user before creating.
- This value is passed as both the workspace `--location` (if creating) and `FunctionAppLocation` in Step 2.

---

### 4. API Key

If not provided, ask: *"Should I generate an API key for you?"*

**User provides a key** — use as-is (minimum 8 characters).

**Generate automatically** — run this and confirm the result with the user before using it:
```powershell
$apiKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object { [char]$_ })
Write-Host "Generated API key: $apiKey"
```

> ⚠️ The user must save this key — it is not retrievable after deployment.

---

### Value Summary Checkpoint

Once all values are collected, print a confirmation table before taking any action:

```
Subscription:        <name>  (<id>)
Workspace:           ccfpull-ws-<suffix>  (ccfpull-rg-<suffix>, <region>)
Function App RG:     ccfpull-fa-<suffix>  (new / existing)
Region:              <region>
API key:             <key>
```

Ask: **"Does this look correct? Type `yes` to begin deployment."**

---

## Deployment Rules

1. **Check before create** — never assume a resource group doesn't exist. Check both RGs:
   ```powershell
   az group show --name ccfpull-fa-$suffix --query "{name:name,location:location}" -o table 2>$null
   az group show --name ccfpull-rg-$suffix --query "{name:name,location:location}" -o table 2>$null
   ```
   If a generated name collides, generate a new suffix and re-check. If the Function App RG exists in a different region than selected, ask the user whether to reuse it or create a new one.

2. **Verify after every step** — run the verify command and report result before moving on. Only pause if a step has genuinely failed and you cannot self-recover.

3. **Full resource ID** — `AppInsightsWorkspaceResourceID` must be the full ID, not just the workspace name:
   `/subscriptions/<id>/resourceGroups/<rg>/providers/Microsoft.OperationalInsights/workspaces/<name>`

4. **Template path** — use the path relative to the workspace root where this repo is cloned. Confirm the root before running.

5. **Enable Sentinel** — use `az rest`, not `az security insights create` (that command does not exist).

---

## Step 1 — Set Subscription + Create Resources

```powershell
az account set --subscription "<subscription-id>"
az account show --query "{name:name, id:id}" -o table
```

**Create resource group** (check first — see Deployment Rule 1):
```powershell
az group create --name ccfpull-fa-$suffix --location <region> --output table
```

**Create Sentinel workspace** (only if creating new):
```powershell
az monitor log-analytics workspace create `
  --workspace-name <workspace-name> `
  --resource-group <workspace-rg> `
  --location <region> `
  --output table
```

**Enable Sentinel on the workspace:**
```powershell
$wsId = az monitor log-analytics workspace show `
  --name <workspace-name> --resource-group <workspace-rg> --query id -o tsv

az rest --method PUT `
  --url "https://management.azure.com${wsId}/providers/Microsoft.SecurityInsights/onboardingStates/default?api-version=2024-03-01" `
  --body '{}'
```

**Verify:**
```powershell
az monitor log-analytics workspace show `
  --name <workspace-name> --resource-group <workspace-rg> `
  --query "{name:name, provisioningState:provisioningState, location:location}" -o table
```

---

## Step 2 — Deploy the Function App

```powershell
$wsId = az monitor log-analytics workspace show `
  --name <workspace-name> --resource-group <workspace-rg> --query id -o tsv

az deployment group create `
  --name "NetworkLogAPI-Deploy" `
  --resource-group ccfpull-fa-$suffix `
  --template-file "<repo-root>/Sentinel-CCF-Pull-Connector-Builder-Agent-Accelerator/azuredeploy_NetworkLogAPI.json" `
  --parameters `
      ApiKey="<api-key>" `
      AppInsightsWorkspaceResourceID="$wsId" `
      FunctionAppLocation="<region>" `
  --output table
```

**Capture outputs immediately after deployment succeeds:**
```powershell
$outputs = az deployment group show `
  --name "NetworkLogAPI-Deploy" `
  --resource-group ccfpull-fa-$suffix `
  --query "properties.outputs" -o json | ConvertFrom-Json

$functionAppName = $outputs.functionAppName.value
$endpoint        = $outputs.getNetworkLogsEndpoint.value
Write-Host "Function App: $functionAppName"
Write-Host "Endpoint:     $endpoint"
```

**Verify:**
```powershell
az functionapp show `
  --name $functionAppName --resource-group ccfpull-fa-$suffix `
  --query "{name:name, state:state, location:location}" -o table
```

---

## Step 3 — Verify the API

```powershell
Invoke-RestMethod `
  -Uri "https://$functionAppName.azurewebsites.net/api/GetNetworkLogs?page=1&pageSize=5" `
  -Headers @{ "X-API-Key" = "<api-key>" } | ConvertTo-Json -Depth 4
```

**Expected:** `status: "success"`, `metadata.totalCount: 50`, 5 records in `data`.

- `401` — API key mismatch; verify `ApiKey` parameter used in Step 2.
- `404` / connection refused — Function App still cold-starting; wait 60 s and retry.

---

## Step 4 — Run the CCF Connector Builder Agent

Tell the user to paste the following into **GitHub Copilot Chat** (Agent mode) in VS Code:

```
@sentinel /create-connector build me a connector based on the api documentation published here Sentinel-CCF-Pull-Connector-Builder-Agent-Accelerator\NetworkLogAPI_API_Documentation.md
```

If the agent asks for the base URL or API key, provide:
- **Base URL:** `https://<functionAppName>.azurewebsites.net`
- **API key header:** `X-API-Key`

The agent generates four files under `sentinel-connectors/NetworkLogAPI_CCF/`:

| File | Purpose |
|---|---|
| `NetworkLogAPI_PollingConfig.json` | Auth, endpoint, pagination, incremental pull, DCR stream |
| `NetworkLogAPI_Table.json` | `NetworkLogAPINetworkLogs_CL` table schema |
| `NetworkLogAPI_DCR.json` | Stream declarations, KQL transform, workspace destination |
| `NetworkLogAPI_ConnectorDefinition.json` | Connector UI — title, description, KQL queries |

---

## Step 5 — Deploy Connector + Activate in Sentinel

**Deploy from VS Code:**
1. Right-click any file in `sentinel-connectors/NetworkLogAPI_CCF/`
2. Select **Deploy Connector** → choose subscription and Sentinel workspace

**Verify — connector visible in Sentinel:**
Guide user to **Microsoft Sentinel → Content Hub → Data Connectors** → search **NetworkLogAPI**.

**Activate:**
1. Click **Open connector page**
2. Fill in:

   | Field | Value |
   |---|---|
   | Base URL | `https://<functionAppName>.azurewebsites.net` |
   | API Key | `<api-key>` |

3. Click **Connect** → then **Test Connectivity** — confirm green status

---

## Step 6 — Verify Data Ingestion

Allow 5–20 minutes, then confirm data in **Sentinel → Logs**:

```kql
NetworkLogAPINetworkLogs_CL
| sort by TimeGenerated desc
| take 10
```

**Expected:** Records with `sourceIp`, `destinationIp`, `action`, `severity`, `threatIndicator`.

If no data after 20 minutes, verify in `PollingConfig.json`:
- `eventsJsonPaths` = `$.data`
- `nextLinkPath` = `$.metadata.nextLink`
- `hasNextPagePath` = `$.metadata.hasNextPage`

---

## Completion Summary

Print when all steps are done:

```
Function App:    https://<functionAppName>.azurewebsites.net
Endpoint:        https://<functionAppName>.azurewebsites.net/api/GetNetworkLogs
Function App RG: ccfpull-fa-<suffix>  (<region>)
Workspace:       ccfpull-ws-<suffix>  (ccfpull-rg-<suffix>)
Table:           NetworkLogAPINetworkLogs_CL
Status:          Connected
```

---

## Cleanup (when requested)

```powershell
az group delete --name ccfpull-fa-$suffix --yes --no-wait
az group delete --name ccfpull-rg-$suffix --yes --no-wait
```
