# CCF Pull Connector — Nested API Accelerator: Agent Deployment Instructions

> These are instructions for a GitHub Copilot agent. When a user pastes the trigger prompt,
> load this file and follow the steps below exactly.

---

## Step 0 — Collect Deployment Values

**Start here every time.** Before taking any deployment action, work through the values below.

**Default behaviour when a value is missing**: this is a lab accelerator, so resource names do not need to be meaningful as long as they are unique in the environment. **If the user doesn't provide a value, generate one yourself** (e.g. append a random 4-digit suffix like `contoso-nested-ws-4821`). Do not ask for values the user hasn't volunteered. Generate sensible defaults, show them in the confirmation table, and proceed.

The only value you must confirm with the user is the **Subscription ID** (if more than one exists).

Collect all values and print the confirmation table before executing any `az` command.

---

### 1. Azure Subscription ID

Run to see available subscriptions and let the user choose:

```powershell
az account list --query "[].{name:name, id:id, isDefault:isDefault}" -o table
```

If only one subscription exists (or one is marked `isDefault: True`), confirm it with the user rather than assuming.

---

### 2. Sentinel Workspace Name + Resource Group

If not provided, ask: *"Do you have an existing Sentinel workspace, or should I create a new one?"*

**Existing workspace** — list and let the user pick:

```powershell
az monitor log-analytics workspace list `
  --query "[].{name:name, resourceGroup:resourceGroup, location:location}" -o table
```

Derive `workspace-resource-group` and `location` from the chosen row — do not ask again.

**New workspace** — suggest these names and ask the user to confirm or change them:
- Workspace name: `contoso-nested-ws`
- Resource group: `contoso-nested-rg`
- Location: see value 3 below

Once confirmed, run:

```powershell
# Create resource group (skip if reusing an existing one)
az group create `
  --name <workspace-rg> `
  --location <region> `
  --output table

# Create the Log Analytics workspace
az monitor log-analytics workspace create `
  --workspace-name <workspace-name> `
  --resource-group <workspace-rg> `
  --location <region> `
  --output table

# Enable Microsoft Sentinel on the workspace
# Note: use Invoke-WebRequest with a bearer token — az rest can hang in VS Code terminals
$WS_ID = (az monitor log-analytics workspace show `
  --name <workspace-name> `
  --resource-group <workspace-rg> `
  --query id -o tsv).Trim()

$token = (az account get-access-token --query accessToken -o tsv).Trim()
$sentinelUrl = "https://management.azure.com$WS_ID/providers/Microsoft.SecurityInsights/onboardingStates/default?api-version=2024-03-01"
$sentinelResp = Invoke-WebRequest -Uri $sentinelUrl -Method PUT `
  -Headers @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" } `
  -Body "{}"
Write-Host "Sentinel enabled: HTTP $($sentinelResp.StatusCode)"
```

**Verify**: confirm workspace exists and Sentinel is enabled:

```powershell
az monitor log-analytics workspace show `
  --name <workspace-name> `
  --resource-group <workspace-rg> `
  --query "{name:name, location:location, resourceGroup:resourceGroup, provisioningState:provisioningState}" `
  --output table
```

---

### 3. Azure Region / Location

- If reusing an **existing** workspace, inherit its `location` automatically — do **not** ask.
- If creating a **new** workspace, suggest `eastus` and ask the user to confirm.
- This value is passed as `workspace-location` in Step 3. It must match the workspace region exactly.

---

### 4. Mock API Resource Group

- Suggest `contoso-mock-api-rg` (separate from the Sentinel workspace RG).
- Ask the user to confirm or provide a different name.
- The Mock API can share the workspace RG or use a dedicated one — both work.

---

### 5. Mock API Function App Name Prefix

- Suggest `ContosoMockApi` as the prefix.
- A random 8-character suffix is appended automatically by the ARM template to ensure global uniqueness.
- Ask the user to confirm or change the prefix.

---

### Value Summary Checkpoint

Once all values are collected, print a confirmation table before taking any action:

```
Subscription ID:        xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Workspace name:         my-sentinel-ws
Workspace RG:           sentinel-rg
Region / location:      eastus
Mock API RG:            contoso-mock-api-rg
Function App prefix:    ContosoMockApi
```

Ask: **"Does this look correct? Type `yes` to begin deployment."**

---

## Deployment Rules — Follow Without Exception

1. **Never** use the VS Code `deploy_connector` extension tool. For the Function App code deploy, use the Kudu async REST API (Step 2). For the Sentinel solution, use the ARM management REST API (Step 4). Do not use `az functionapp deployment source config-zip` or `az deployment group create` for these steps — both hang in VS Code terminals when they run silently for more than ~2 minutes.

2. **Always** pass `workspace-location` explicitly in the Step 4 deployment body.
   Omitting it causes DCR and connector definition resource placement to fail.

3. To enable Sentinel on a new workspace use `Invoke-WebRequest` with a bearer token from `az account get-access-token`. Do not use `az rest` — it hangs in VS Code integrated terminals.

4. Step 5 (clicking **Connect** in the portal) is the **only manual action**. Every other step is CLI. The ARM deployment in Step 4 registers the connector definition but does NOT start polling. Only the Connect button starts data collection.

5. The Function App name is `<prefix><8-char-suffix>` (lowercase, no hyphens). Always read
   the `functionAppName` output from the Step 1 deployment to get the actual name before
   proceeding to Step 2.

6. After **every** CLI step, automatically verify success before proceeding. Run a follow-up
   `az` command confirming `provisioningState=Succeeded` or the expected resource state.
   Report the result inline, then immediately continue. Only pause and ask when a step has
   genuinely failed and you cannot self-recover.

7. This is a dev/demo accelerator. The Function App API key and Mock API URL **should be displayed clearly in chat** at Step 5 so the user can copy them directly into the portal without switching to the terminal.

---

## Step 1 — Deploy the Mock API Infrastructure

```powershell
# Create resource group
az group create `
  --name <mock-api-rg> `
  --location <region> `
  --output table

# Deploy Function App infrastructure
cd <workspace-root>   # e.g. C:\GitHub\Azure-Sentinel
az deployment group create `
  --resource-group <mock-api-rg> `
  --template-file "Tools/CCF-Pull-Connector-Nested-Accelerator/MockApi/azuredeploy_MockApi.json" `
  --parameters FunctionAppName=<prefix> Location=<region> `
  --output table
```

**Capture outputs** and store for use in later steps:

```powershell
$outputs = (az deployment group show `
  --resource-group <mock-api-rg> `
  --name azuredeploy_MockApi `
  --query properties.outputs -o json | ConvertFrom-Json)

$functionAppName = $outputs.functionAppName.value
$mockApiBaseUrl  = $outputs.mockApiBaseUrl.value

Write-Host "Function App: $functionAppName"
Write-Host "Base URL:     $mockApiBaseUrl"
```

**Verify**: confirm the ARM deployment succeeded:

```powershell
az deployment group show `
  --resource-group <mock-api-rg> `
  --name azuredeploy_MockApi `
  --query "{state:properties.provisioningState}" `
  --output table
```

> **Note**: Skip `az functionapp show` — it hangs in VS Code terminals. The ARM deployment succeeding is sufficient confirmation the Function App was provisioned.

---

## Step 2 — Deploy the Mock API Code

Zip the `MockApi/` folder and deploy via the Kudu async REST API. This avoids `az functionapp deployment source config-zip`, which hangs in VS Code terminals during the remote pip install.

```powershell
# Run from workspace root
$zipPath = Join-Path $PWD "contosoapi.zip"
Compress-Archive `
  -Path "Tools/CCF-Pull-Connector-Nested-Accelerator/MockApi/*" `
  -DestinationPath $zipPath `
  -Force

# Get Kudu publishing credentials
$creds = az functionapp deployment list-publishing-credentials `
  --name $functionAppName `
  --resource-group <mock-api-rg> `
  --query "{username:publishingUserName, password:publishingPassword}" -o json | ConvertFrom-Json
$base64Auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$($creds.username):$($creds.password)"))

# Submit async zip deploy via Kudu REST API
$deployResp = Invoke-WebRequest `
  -Uri "https://$functionAppName.scm.azurewebsites.net/api/zipdeploy?isAsync=true" `
  -Method POST `
  -InFile $zipPath `
  -Headers @{ Authorization = "Basic $base64Auth"; "Content-Type" = "application/zip" }
Write-Host "Deploy submitted: HTTP $($deployResp.StatusCode)"

# Poll until complete (status 4 = Success, status 3 = Failed)
do {
  Start-Sleep -Seconds 10
  $buildStatus = Invoke-RestMethod `
    -Uri "https://$functionAppName.scm.azurewebsites.net/api/deployments/latest" `
    -Headers @{ Authorization = "Basic $base64Auth" }
  Write-Host "[$([datetime]::Now.ToString('HH:mm:ss'))] status=$($buildStatus.status) complete=$($buildStatus.complete)"
} while ($buildStatus.status -lt 3)
Write-Host "Code deploy complete: status=$($buildStatus.status)"
```

Expected: status=4, complete=True. Status 3 means the remote build failed — check the Function App's Log stream in the Azure Portal.

> Full endpoint verification (with API key) runs in Step 3 after the key is retrieved.

---

## Step 3 — Retrieve the Function App API Key

Retrieve the default function key. Display it clearly in chat so the user can copy it directly into the portal in Step 5.

```powershell
$apiKey = (az functionapp keys list `
  --name $functionAppName `
  --resource-group <mock-api-rg> `
  --query functionKeys.default -o tsv).Trim()

Write-Host "API key: $apiKey"
```

Display the key clearly in chat so the user can copy it directly into the portal in Step 5.

**Verify** the endpoints respond correctly:

```powershell
# List endpoint — expect 5 incidents
$listResponse = Invoke-RestMethod "$mockApiBaseUrl/incidents" -Headers @{"x-functions-key" = $apiKey}
Write-Host "Incidents returned: $($listResponse.incidents.Count)"

# Detail endpoint — expect INC-001 details
$detailResponse = Invoke-RestMethod "$mockApiBaseUrl/incidents/INC-001/details" -Headers @{"x-functions-key" = $apiKey}
Write-Host "INC-001 title: $($detailResponse.title)"
```

---

## Step 4 — Deploy the Sentinel Solution

Deploy the main template which creates the DCE, `ContosoIncidents_CL` table, DCR, and connector definition.

Use the ARM management REST API directly — this avoids `az deployment group create`, which hangs in VS Code terminals when the template takes more than ~2 minutes to complete silently.

```powershell
# Get a fresh access token
$token = (az account get-access-token --query accessToken -o tsv).Trim()

# Read the template from disk
$template = Get-Content `
  "Tools/CCF-Pull-Connector-Nested-Accelerator/ContosoIncidents/Package/mainTemplate.json" `
  -Raw | ConvertFrom-Json

# Build the deployment request body
$deployBody = @{
  properties = @{
    mode     = "Incremental"
    template = $template
    parameters = @{
      workspace            = @{ value = "<workspace-name>" }
      "workspace-location" = @{ value = "<region>" }
    }
  }
} | ConvertTo-Json -Depth 50

# Submit the deployment
$subId = (az account show --query id -o tsv).Trim()
$deployUrl = "https://management.azure.com/subscriptions/$subId/resourceGroups/<workspace-rg>/providers/Microsoft.Resources/deployments/mainTemplate?api-version=2021-04-01"
$submitResp = Invoke-WebRequest -Uri $deployUrl -Method PUT `
  -Headers @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" } `
  -Body $deployBody
Write-Host "Deployment submitted: HTTP $($submitResp.StatusCode)"

# Poll until the deployment reaches a terminal state
do {
  Start-Sleep -Seconds 15
  $token = (az account get-access-token --query accessToken -o tsv).Trim()
  $deployState = (Invoke-RestMethod -Uri $deployUrl `
    -Headers @{ Authorization = "Bearer $token" }).properties.provisioningState
  Write-Host "[$([datetime]::Now.ToString('HH:mm:ss'))] $deployState"
} while ($deployState -notin @("Succeeded","Failed","Canceled"))
Write-Host "Deployment final state: $deployState"
```

Expected final state: `Succeeded`. If `Failed`, check the deployment operations in the Azure Portal (Resource Group → Deployments → mainTemplate → Operation details).

Once confirmed, print the full deployment summary so the user has a single reference for all resources:

```powershell
$subId = (az account show --query id -o tsv).Trim()

Write-Host ""
Write-Host "========== Deployment Summary =========="
Write-Host ""
Write-Host ("Subscription ID      : " + $subId)
Write-Host ("Region               : <region>")
Write-Host ""
Write-Host "--- Sentinel Workspace ---"
Write-Host ("Workspace Name       : <workspace-name>")
Write-Host ("Workspace RG         : <workspace-rg>")
Write-Host ""
Write-Host "--- Mock API ---"
Write-Host ("Function App Name    : " + $functionAppName)
Write-Host ("Resource Group       : <mock-api-rg>")
Write-Host ("Mock API Base URL    : " + $mockApiBaseUrl)
Write-Host ("API Key              : (run: Write-Host `$apiKey to copy)")
Write-Host ""
Write-Host "========================================"
```

---

## Step 5 — Enable the Connector (Portal)

The ARM deployment from Step 4 registers the connector definition — it does **not** start data collection. The user must click **Connect** in the portal once, providing the Mock API URL and API key. This is the only manual action in the entire deployment.

Print the connection values the user needs to paste into the portal **directly in chat** — display both values clearly:

| Field | Value |
|-------|-------|
| Mock API Base URL | *(print actual value of `$mockApiBaseUrl`)* |
| Function App API Key | *(print actual value of `$apiKey`)* |

Guide the user to:

1. Navigate to **Microsoft Sentinel** → **Data Connectors**
2. Find **Contoso Incidents (CCF Nested API Accelerator)** — if not visible, click **Refresh** or wait 2–3 minutes for the ARM deployment to propagate
3. Click **Open connector page**
4. Under **STEP 2 — Connect to the Contoso Mock API**, enter:

   | Field | Value |
   |-------|-------|
   | Mock API Base URL | `<mockApiBaseUrl>` (from Step 1 output) |
   | Function App API Key | *(run `Write-Host $apiKey` in terminal and paste the value)* |

5. Click **connect**

Once clicked, the CCF engine begins polling immediately. No further manual steps are required.

---

## Step 6 — Verify Data in Log Analytics

Allow **5–10 minutes** for the first poll cycle after clicking Connect, then confirm data arrived.

Guide the user to **Microsoft Sentinel → Logs** to run:

```kql
ContosoIncidents_CL
| sort by TimeGenerated desc
| take 10
```

Expected result: **5 rows** with columns `IncidentId`, `Title`, `Severity`, `Status`, `AffectedUser`, `SourceIp` all populated.

- `TimeGenerated` = ingestion time (`now()`) for all records — the DCR transform sets this unconditionally.
- Connector status in the Data Connectors blade should show **Connected**.

If no rows appear after 15 minutes:
1. Confirm the connector status is **Connected** (not **Disconnected**) in the portal
2. Re-check the API key is correct by testing the endpoint manually
3. Check the DCR: `az monitor data-collection rule show --name ContosoIncidents-DCR --resource-group <workspace-rg>`

---

## Cleanup (Optional)

To remove all deployed resources, ask the user to confirm before running destructive commands:

```powershell
# Remove Mock API Function App and its resource group
az group delete --name <mock-api-rg> --yes --no-wait

# Remove Sentinel resources (if workspace RG is dedicated to this accelerator)
az group delete --name <workspace-rg> --yes --no-wait
```

> If the workspace RG contains other resources, delete individual resources via the portal rather than the entire RG.