# WhoisFreaks – Complete Deployment & Testing Guide

## 1. How this solution is packaged

This solution ships as **two separate templates** with two separate jobs:

- **`Package/mainTemplate.json`** -- the Content Hub package. Installing it from Content Hub registers the WhoisFreaks data connector UI, its metadata, and the solution entry in Sentinel. It does **not** create a Function App, storage account, DCE, DCR, or any custom tables.
- **`azuredeploy/azuredeploy.json`** -- the infrastructure template. This is what actually creates the Function App (Linux Consumption plan, system-assigned managed identity), a storage account for checkpointing, a Data Collection Endpoint, a Data Collection Rule (with one stream per feed, routed to the matching table), the 7 custom Log Analytics tables, and the two role assignments the Function's identity needs (`Storage Blob Data Contributor` on the storage account, `Monitoring Metrics Publisher` on the DCR).

Your WhoisFreaks API key and feed selection are parameters of `azuredeploy.json`, not of `mainTemplate.json` -- you supply them when you deploy the infrastructure (step 3 below), whether via the **Deploy to Azure** button in the connector's instructions or via `az deployment group create`.

## 2. Prerequisites

- Azure subscription with Microsoft Sentinel (Log Analytics workspace) already created.
- Permissions: Contributor (or equivalent) on the resource group, plus the ability to assign roles (`Storage Blob Data Contributor`, `Monitoring Metrics Publisher`) -- typically `Owner` or `User Access Administrator` + `Contributor`.
- A WhoisFreaks API key (required for live ingestion; the Function host will start and log a warning without one, but will not ingest anything).
- Azure CLI (`az`) logged in, or access to the Azure Portal.

## 3. Deploy

### 3.1 Install the Content Hub solution

Install **WhoisFreaks** from Sentinel Content Hub in the usual way (or deploy `Package/mainTemplate.json` directly with `workspace` / `workspace-location` parameters if testing outside Content Hub). This registers the connector UI only -- there is nothing to verify running yet.

### 3.2 Deploy the infrastructure

**Portal (Deploy to Azure button):** open the WhoisFreaks connector's instructions in Sentinel and click **Deploy to Azure**. You'll be prompted for the Sentinel workspace name, your WhoisFreaks API key, and which feeds to enable.

**Azure CLI:**

```bash
RG=your-resource-group          # resource group that contains the Sentinel workspace
WORKSPACE=YourSentinelWorkspaceName

az deployment group create \
  --resource-group "$RG" \
  --template-file azuredeploy/azuredeploy.json \
  --parameters \
    workspaceName="$WORKSPACE" \
    whoisfreaksApiKey="YOUR_REAL_KEY" \
    enableMalware=true \
    enablePhishing=false \
    enableSpam=false \
    enableNrdGtldWithWhois=false \
    enableNrdCctldWithWhois=false \
    enableNrdGtldWithoutWhois=false \
    enableNrdCctldWithoutWhois=false
```

A ready-to-edit copy of these parameters is in `azuredeploy/azuredeploy.parameters.json`.

`functionPackageUrl` defaults to the zip committed at `Package/FunctionApp.zip`, served from the raw GitHub URL once this solution is merged into `Azure/Azure-Sentinel`. If you're testing before merge, host the zip yourself and override the parameter:

```bash
STORAGE=wfpackagetest$RANDOM
az storage account create -n "$STORAGE" -g "$RG" -l eastus --sku Standard_LRS --kind StorageV2
az storage container create --account-name "$STORAGE" -n packages
az storage blob upload --account-name "$STORAGE" -c packages -f Package/FunctionApp.zip -n FunctionApp.zip --auth-mode login
# Generate a short-lived SAS (read-only) instead of public blob access:
EXPIRY=$(date -u -d '+2 hours' '+%Y-%m-%dT%H:%MZ' 2>/dev/null || date -u -v+2H '+%Y-%m-%dT%H:%MZ')
SAS=$(az storage blob generate-sas --account-name "$STORAGE" -c packages -n FunctionApp.zip \
  --permissions r --expiry "$EXPIRY" --auth-mode login -o tsv)
# then add: functionPackageUrl="https://$STORAGE.blob.core.windows.net/packages/FunctionApp.zip?$SAS"
```

### 3.3 Verify the deployment

- Function App exists, is running, and has the expected application settings (`WHOISFREAKS_API_KEY`, `CHECKPOINT_STORAGE_ACCOUNT`, `DCR_INGESTION_ENDPOINT`, `DCR_IMMUTABLE_ID`, `WHOISFREAKS_FEED_*_ENABLED`).
- The Data Collection Endpoint and Data Collection Rule exist, and the DCR has a stream declaration per enabled feed.
- The 7 custom tables appear under the Log Analytics workspace (may take a few minutes after first deployment).
- The Function App's managed identity has `Storage Blob Data Contributor` on the storage account and `Monitoring Metrics Publisher` on the DCR (both role assignments are created by `azuredeploy.json` automatically -- confirm under **Access control (IAM)** on each resource if you want to double-check).

## 4. Developer / local Function testing (no API key needed)

```bash
cd FunctionApp
cp local.settings.json.example local.settings.json
# edit local.settings.json -- leave WHOISFREAKS_API_KEY empty to only exercise the host,
# but CHECKPOINT_STORAGE_ACCOUNT / DCR_INGESTION_ENDPOINT / DCR_IMMUTABLE_ID are still required

python -m venv .venv
source .venv/bin/activate   # or the Windows equivalent
pip install -r requirements-dev.txt
func start
```

Run the unit tests with:

```bash
PYTHONPATH=. python -m pytest tests/ -v
```

Calling the timer or `/api/run` with an empty API key returns a **warning** JSON payload and does not crash. To exercise real ingestion locally you need a real API key, a real DCR endpoint/immutable ID, and a storage account your local identity (e.g. your `az login` session, via `DefaultAzureCredential`) can read/write.

## 5. Trigger ingestion after deploy

### Automatic
Timer fires daily at **00:00 UTC**.

### Manual
1. In Azure Portal open the Function App → **Functions** → `WhoisFreaksManualTrigger`.
2. Get the function key.
3. Call:

```
POST https://<function-app-name>.azurewebsites.net/api/run?code=<function-key>
```

Or use **Test/Run** from the Azure Portal.

## 6. Verify data in Sentinel

```kusto
union isfuzzy=true
  WhoisFreaksMalware_CL,
  WhoisFreaksPhishing_CL,
  WhoisFreaksSpam_CL,
  WhoisFreaksNRDGtldWithWhois_CL,
  WhoisFreaksNRDCctldWithWhois_CL,
  WhoisFreaksNRDGtldWithoutWhois_CL,
  WhoisFreaksNRDCctldWithoutWhois_CL
| summarize count() by Type
| sort by count_ desc
```

Or a single table:

```kusto
WhoisFreaksMalware_CL
| sort by TimeGenerated desc
| take 50
```

## 7. Change feeds after deployment (no redeploy)

1. Function App → **Configuration** → **Application settings**.
2. Edit any of:
   - `WHOISFREAKS_FEED_MALWARE_ENABLED`
   - `WHOISFREAKS_FEED_PHISHING_ENABLED`
   - `WHOISFREAKS_FEED_SPAM_ENABLED`
   - `WHOISFREAKS_FEED_NRD_GTLD_WITH_WHOIS_ENABLED`
   - `WHOISFREAKS_FEED_NRD_CCTLD_WITH_WHOIS_ENABLED`
   - `WHOISFREAKS_FEED_NRD_GTLD_WITHOUT_WHOIS_ENABLED`
   - `WHOISFREAKS_FEED_NRD_CCTLD_WITHOUT_WHOIS_ENABLED`
3. Set the value to `true` or `false`.
4. Save. Restart the app if the change isn't picked up immediately.

## 8. Troubleshooting checklist

| Symptom | Check |
|---------|-------|
| Function starts but no data | API key empty? Feeds all `false`? Check the Function's `warning`-level logs. |
| 401 / 403 from WhoisFreaks | Invalid or expired API key; feed not included in your subscription. |
| 400 from the ingestion client ("stream not declared") | The DCR doesn't declare a stream matching `FeedConfig.stream_name` -- confirm you deployed the version of `azuredeploy.json` matching this Function code, and that the table/stream names haven't been hand-edited out of sync. |
| 403 on DCR upload | Managed identity missing `Monitoring Metrics Publisher` on the DCR -- check IAM on the DCR resource. |
| Checkpoint/lock errors (`ResourceNotFoundError`, 403) | Managed identity missing `Storage Blob Data Contributor` on the storage account. |
| Package download fails (404) | `functionPackageUrl` points at the official repo, which doesn't contain the zip until this PR merges. Host it yourself (section 3.2) in the meantime. |
| Tables missing | Wait a few minutes after the DCR/table deployment; confirm the DCR destination is the correct workspace. |
| Timer never runs | Confirm the App Service plan is running; check Function App → **Monitor** → **Invocations**. |

## 9. Next steps for official Content Hub publish

1. Open a PR against https://github.com/Azure/Azure-Sentinel under `Solutions/Whoisfreaks/`.
2. Confirm `Package/FunctionApp.zip` is committed and up to date with `FunctionApp/`, or regenerate it as part of CI.
3. Run the official solution packaging/validation scripts in `Tools/Create-Azure-Sentinel-Solution/V3` and `arm-ttk` against both `Package/mainTemplate.json` and `azuredeploy/azuredeploy.json`.
4. After merge, the default `functionPackageUrl` in `azuredeploy.json` (the raw GitHub URL) will resolve without any manual hosting step.
