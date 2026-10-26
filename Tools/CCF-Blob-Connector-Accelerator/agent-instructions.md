# CCF Blob Connector Accelerator — Agent Deployment Instructions

> These are instructions for a GitHub Copilot agent. When a user pastes the trigger prompt,
> load this file and follow the steps below exactly.

---

## Step 0 — Collect Deployment Values

**Start here every time.** Before taking any deployment action, work through the six values below.

**Default behaviour when a value is missing**: do not guess or skip — ask the user one of:
- *"Do you have an existing [resource], or should I create a new one for you?"*
- *"Should I generate a name for this, or do you have one in mind?"*

Collect **all six values** and print the confirmation table before executing any `az` command.

---

### 1. Azure Subscription ID

- Run to see available subscriptions and let the user choose:
  ```powershell
  az account list --query "[].{name:name, id:id, isDefault:isDefault}" -o table
  ```
- If only one subscription exists (or one is marked `isDefault: True`), confirm it with the user rather than assuming.

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
- Workspace name: `contosofort-ws`
- Resource group: `contosofort-rg`
- Location: see value 3 below

---

### 3. Azure Region / Location

- If reusing an **existing** workspace, inherit its `location` automatically — do **not** ask.
- If creating a **new** workspace, suggest `eastus` and ask the user to confirm.
- This value is passed as `workspace-location` in Step 3 — it is **required** and must match the workspace region exactly.

---

### 4. Storage Account Name *(globally unique across all of Azure)*

> ⚠️ Azure storage account names are **globally unique** — not just within a region or subscription. A name taken anywhere in Azure is unavailable to you.

If not provided, ask: *"Should I generate a unique storage account name for you?"*

**User provides a name** — validate format (3–24 lowercase alphanumeric, no hyphens) and check global availability:
```powershell
az storage account check-name --name <provided-name> `
  --query "{available:nameAvailable, reason:reason}" -o table
```
If unavailable, explain why and either ask for a different name or offer to generate one.

**Generate automatically** — run this loop, then confirm the result with the user before using it:
```powershell
do {
    $suffix    = -join ((97..122) | Get-Random -Count 8 | ForEach-Object { [char]$_ })
    $name      = "ccfblob$suffix"
    $available = (az storage account check-name --name $name --query nameAvailable -o tsv).Trim()
} while ($available -ne "true")
Write-Host "Generated storage account name: $name"
```

---

### 5. Storage Account Resource Group

If not provided, ask: *"Should I create a new resource group for the storage account, or reuse an existing one?"*

- **New RG** — suggest `contosofort-blob-rg` and ask the user to confirm or change it.
- **Reuse Sentinel RG** — acceptable; storage and workspace can share a resource group.
- The storage RG must be in the same subscription as the Sentinel workspace.

---

### 6. Blob Container Name

- Default: `contosofort-logs` — use this unless the user specifies otherwise.
- No global-uniqueness constraint; any lowercase alphanumeric + hyphens string is valid.

---

### Value Summary Checkpoint

Once all values are collected, print a confirmation table before taking any action:

```
Subscription ID:       xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Workspace name:        my-sentinel-ws
Workspace RG:          sentinel-rg
Region / location:     eastus
Storage account name:  ccfblobabc12345  (generated / provided)
Storage RG:            ccfblob-rg       (new / existing)
Blob container name:   contosofort-logs
```

Ask: **"Does this look correct? Type `yes` to begin deployment."**

---

## Deployment Rules — Follow Without Exception

1. **Never** use the VS Code `deploy_connector` extension tool — always deploy using
   `az deployment group create` targeting
   `Tools/CCF-Blob-Connector-Accelerator/ContosoFort/Package/mainTemplate.json`
   (path relative to workspace root). Confirm the user's workspace root before running.

2. **Always** pass `workspace-location=<region>` explicitly in the Step 3 CLI command.
   Omitting it causes `workspace-location` to default to an empty string, which gets baked
   into the stored connection template. The ARM deployment will succeed but every Connect
   attempt will fail with `LocationRequired`.

3. To enable Sentinel on a new workspace use `az rest`, **not** `az security insights create`
   (that command does not exist):
   ```bash
   az rest --method PUT \
     --url "https://management.azure.com{workspace_resource_id}/providers/Microsoft.SecurityInsights/onboardingStates/default?api-version=2024-03-01" \
     --body '{}'
   ```

4. Step 4 (clicking Connect) is a **manual portal action**. There is no CLI equivalent.
   Guide the user to the exact portal URL and provide field values to paste in.

5. The storage account **must** be ADLS Gen2 with `--enable-hierarchical-namespace true`.
   Standard StorageV2 without HNS silently fails — no error on upload, no data ingested.

6. For blob uploads with `--auth-mode login`, the signed-in user needs
   **Storage Blob Data Contributor** on the storage account (separate from the Sentinel
   Service Principal roles).

7. After **every** CLI step, automatically verify success before proceeding. Run a follow-up
   `az` command confirming the expected resource/state exists (e.g. `provisioningState=Succeeded`,
   role assignment present, deployment state=Succeeded). Report the result inline, then
   immediately continue. Only pause and ask when a step has genuinely failed and you
   cannot self-recover.

---

## Step 1 — Deploy the Storage Account

```bash
# Create resource group (skip if reusing existing)
az group create \
  --name <storage-rg> \
  --location <region> \
  --output table

# Deploy ADLS Gen2 storage account (HNS required)
az storage account create \
  --name <storage-account-name> \
  --resource-group <storage-rg> \
  --location <region> \
  --sku Standard_LRS \
  --kind StorageV2 \
  --enable-hierarchical-namespace true \
  --min-tls-version TLS1_2 \
  --allow-blob-public-access false \
  --output table

# Create the blob container (use filesystem API for HNS accounts)
az storage fs create \
  --name <blob-container-name> \
  --account-name <storage-account-name> \
  --auth-mode login \
  --output table
```

**Verify**: confirm `isHnsEnabled=True` and `provisioningState=Succeeded`:
```bash
az storage account show \
  --name <storage-account-name> \
  --resource-group <storage-rg> \
  --query "{name:name, hns:isHnsEnabled, location:location, state:provisioningState}" \
  --output table
```

---

## Step 2 — Grant RBAC to the Sentinel Service Principal

> This is handled automatically when the user clicks Connect in Step 4 **if** they have
> Owner/UAA on the storage subscription. Only run manually if auto-assignment fails
> (`BLB40011: Access to queue denied`).

```powershell
$SP_ID    = (az ad sp show --id "4f05ce56-95b6-4612-9d98-a45c8cc33f9f" --query id -o tsv).Trim()
$SA_SCOPE = (az storage account show --name <storage-account-name> --resource-group <storage-rg> --query id -o tsv).Trim()

az role assignment create --assignee $SP_ID --role "Storage Blob Data Reader"       --scope $SA_SCOPE
az role assignment create --assignee $SP_ID --role "Storage Queue Data Contributor"  --scope $SA_SCOPE
```

**Verify**: list role assignments and confirm both roles are present.

> ⏱️ RBAC propagation takes 1–5 minutes — allow time before Step 4.

---

## Step 3 — Deploy the Sentinel Solution

> Run from the workspace root (`C:\GitHub\Azure-Sentinel` or wherever this repo is cloned).
> The `--template-file` path is relative to the current directory.

```powershell
cd <workspace-root>   # e.g. C:\GitHub\Azure-Sentinel
az deployment group create `
  --resource-group <workspace-rg> `
  --template-file "Tools/CCF-Blob-Connector-Accelerator/ContosoFort/Package/mainTemplate.json" `
  --parameters workspace=<workspace-name> workspace-location=<region> `
  --output table
```

**Verify**: confirm `provisioningState=Succeeded` in the deployment output.

---

## Step 4 — Connect the Connector (Manual Portal Action)

Guide the user to:

1. **Microsoft Sentinel** → **Content Hub** → **Data Connectors**
2. Find **ContosoFort (Using Blob Container) (via Codeless Connector Framework)**
3. Click **Open connector page** → fill in:

   | Field | Value |
   |-------|-------|
   | Blob container URL | `https://<storage-account-name>.blob.core.windows.net/<blob-container-name>` |
   | Storage account resource group | `<storage-rg>` |
   | Storage account location | `<region>` |
   | Storage account subscription ID | `<subscription-id>` |
   | Event Grid topic name | *(leave blank on first connect)* |

4. Click **Connect**

If `BLB40011: Access to queue denied` appears, complete Step 2 manually, wait 5 minutes, and click Connect again.

---

## Step 5 — Upload Sample Data

```powershell
# Grant the signed-in user upload permission if needed
$MY_ID    = (az ad signed-in-user show --query id -o tsv).Trim()
$SA_SCOPE = (az storage account show --name <storage-account-name> --resource-group <storage-rg> --query id -o tsv).Trim()
az role assignment create --assignee $MY_ID --role "Storage Blob Data Contributor" --scope $SA_SCOPE

# Upload the sample data file (run from workspace root)
az storage blob upload `
  --account-name <storage-account-name> `
  --container-name <blob-container-name> `
  --name "ContosoFortSampleData.json" `
  --file "Tools/CCF-Blob-Connector-Accelerator/ContosoFort/Sample Data/ContosoFortSampleData.json" `
  --auth-mode login
```

**Verify**: check a queue message was generated (Event Grid working):
```bash
az storage message peek \
  --queue-name sentinel-connector-notification \
  --account-name <storage-account-name> \
  --auth-mode login \
  --num-messages 5
```

---

## Step 6 — Verify Data in Log Analytics

Allow ~5 minutes, then confirm data arrived:
```kql
ContosoFortV1_CL
| order by TimeGenerated desc
| take 10
```

Guide the user to **Microsoft Sentinel → Logs** to run this query.
