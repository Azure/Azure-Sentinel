# Testing Package Deployment via Azure Portal

## ✅ Setup Complete!

Your test branch `test-package-deployment` is now live on your fork with URLs pointing to `jamos-bt/Azure-Sentinel`.

## 📋 Testing Steps

### ⚠️ IMPORTANT: Which Option to Test

- **Option 1 (mainTemplate.json)**: This is the Content Hub metadata package. It only creates solution metadata in Sentinel - NO Function App, NO tables, NO actual infrastructure. This is what gets published to Content Hub, and then Content Hub uses it to install the actual connector. **You probably don't need to test this unless you're testing Content Hub publishing.**

- **Option 2 (azuredeploy_*.json)**: This is the **actual ARM template** that deploys the infrastructure (Function App, Storage, DCE, DCRs, tables, etc.). **This is what you should test** to validate your deployment.

---

### Option 1: Deploy via mainTemplate.json (Content Hub Metadata Only)

⚠️ **WARNING**: This does NOT deploy the Function App or any infrastructure. It only creates solution metadata in Sentinel's Content Hub.

**Deploy to Azure Button URL:**
```
https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fjamos-bt%2FAzure-Sentinel%2Ftest-package-deployment%2FSolutions%2FBeyondTrustPMCloud%2FPackage%2FmainTemplate.json
```

**What This Deploys:**
- ❌ NO Function App
- ❌ NO Storage Account
- ❌ NO DCE or DCRs
- ❌ NO Custom Tables
- ✅ Only Content Hub metadata (solution package, data connector UI config, workbook template)

**When to Use This:**
- Testing Content Hub publishing process
- Validating solution metadata and descriptions
- Testing the createUiDefinition.json user experience (currently incomplete - needs enhancement)

---

### Option 2: Deploy via Data Connector ARM Template (RECOMMENDED)

✅ **This is the one you want!** This deploys the actual infrastructure with all parameters.

**Deploy to Azure Button URL:**

This tests just the data connector infrastructure (without the solution wrapper).

**Deploy to Azure Button URL:**
```
https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fjamos-bt%2FAzure-Sentinel%2Ftest-package-deployment%2FSolutions%2FBeyondTrustPMCloud%2FData%2520Connectors%2Fazuredeploy_BeyondTrustPMCloud_API_FunctionApp.json
```

**Steps:**
1. Click the URL above (or paste into browser)
2. Azure Portal will open the custom deployment page with **ALL parameters**:
   - **Subscription**: Your Azure subscription
   - **Resource Group**: Choose/create resource group with your Log Analytics workspace
   - **Region**: Same as your workspace
   - **Function App Name**: Leave default or customize
   - **Workspace Name**: Your Log Analytics workspace name (e.g., `beyondtrust-pmcloud`)
   - **BeyondTrust PM Cloud Base URL**: Your tenant URL (e.g., `https://yourcompany.beyondtrustcloud.com`)
   - **BeyondTrust Client ID**: Your OAuth client ID
   - **BeyondTrust Client Secret**: Your OAuth client secret
   - **Activity Audits Polling Interval Minutes**: Default 15 minutes
   - **Client Events Polling Interval Minutes**: Default 5 minutes
   - **Log Level**: Default Information
   - **Historical Data Timeframe**: Default 1d (1 day back)
   - **Hosting Plan SKU**: Default Y1 (Consumption)
   - **Storage Account Type**: Default Standard_LRS
3. Click **Review + Create** → **Create**
4. Wait ~10 minutes for deployment

**What This Tests:**
- ✅ Complete data connector infrastructure deployment
- ✅ Function App with all Azure Functions (ActivityAudits, ClientEvents)
- ✅ Storage Account for function app state
- ✅ Application Insights for monitoring
- ✅ Data Collection Endpoint (DCE)
- ✅ Data Collection Rules (DCRs) for both tables
- ✅ Automatic table creation (BeyondTrustPM_ActivityAudits_CL, BeyondTrustPM_ClientEvents_CL)
- ✅ All app settings and environment variables configured
- ✅ Timer triggers set up with cron expressions

---

## 🔍 Validation Checklist

After deployment completes (~5-10 minutes):

### 1. Resource Verification
- [ ] Function App created: `beyondtrust-pmcloud-*`
- [ ] Storage Account created: `bt*`
- [ ] Application Insights created: `beyondtrust-pmcloud-*-insights`
- [ ] Data Collection Endpoint created: `beyondtrust-pmcloud-*-dce`
- [ ] Data Collection Rules created:
  - [ ] `beyondtrust-pmcloud-*-dcr-activityaudits`
  - [ ] `beyondtrust-pmcloud-*-dcr-clientevents`

### 2. Table Verification
Navigate to **Log Analytics workspace → Tables**:
- [ ] `BeyondTrustPM_ActivityAudits_CL` exists
- [ ] `BeyondTrustPM_ClientEvents_CL` exists
- [ ] Tables show correct schema (~40 and ~50+ columns)

Query to verify tables:
```kql
// Check Activity Audits table
BeyondTrustPM_ActivityAudits_CL
| getschema
| project ColumnName, ColumnType

// Check Client Events table
BeyondTrustPM_ClientEvents_CL
| getschema
| project ColumnName, ColumnType
```

### 3. Function App Configuration
Navigate to **Function App → Configuration**:
- [ ] `DataCollectionEndpoint` set correctly
- [ ] `ActivityAuditsDcrImmutableId` set
- [ ] `ClientEventsDcrImmutableId` set
- [ ] `ActivityAuditsStreamName` = `Custom-BeyondTrustPM_ActivityAudits_CL`
- [ ] `ClientEventsStreamName` = `Custom-BeyondTrustPM_ClientEvents_CL`
- [ ] BeyondTrust credentials configured

### 4. Function App Execution
Navigate to **Function App → Functions**:
- [ ] `ActivityAuditsTimerTrigger` exists
- [ ] `ClientEventsTimerTrigger` exists
- [ ] Click "Code + Test" → "Test/Run" to trigger manually
- [ ] Check **Monitor** tab for execution logs

### 5. Data Ingestion
Wait 15-30 minutes after first execution, then query:
```kql
// Check for Activity Audits data
BeyondTrustPM_ActivityAudits_CL
| where TimeGenerated > ago(1h)
| take 10

// Check for Client Events data
BeyondTrustPM_ClientEvents_CL
| where TimeGenerated > ago(1h)
| take 10
```

### 6. Application Insights
Navigate to **Application Insights → Logs**:
```kql
// Check for function executions
traces
| where operation_Name contains "BeyondTrust"
| project timestamp, message, severityLevel
| order by timestamp desc
| take 50

// Check for errors
exceptions
| where timestamp > ago(1h)
| project timestamp, type, outerMessage, problemId
| order by timestamp desc
```

---

## 🐛 Troubleshooting

### Function App Not Running
1. Check Application Insights for errors
2. Verify credentials in Configuration
3. Check that workspace is in same resource group
4. Restart Function App

### Tables Not Created
1. Check deployment output for errors
2. Verify workspace permissions
3. Check that deployment completed successfully
4. Look for resource creation errors in Activity Log

### No Data Ingestion
1. Verify BeyondTrust credentials are correct
2. Check Function App execution logs
3. Verify DCR immutable IDs are correct
4. Check Data Collection Endpoint is accessible
5. Review Application Insights for API errors

---

## 🧹 Cleanup After Testing

### Option A: Delete Test Resources Only
Navigate to Resource Group and delete:
- Function App
- Storage Account
- Application Insights
- Data Collection Endpoint
- Data Collection Rules
- (Keep workspace and tables if you want)

### Option B: Full Cleanup Including Tables
```bash
# Delete the workspace (includes tables)
az monitor log-analytics workspace delete \
  --workspace-name "beyondtrust-pmcloud" \
  --resource-group "SentinelCCP-Dev" \
  --yes --force
```

### Switch URLs Back to Production

After testing is complete:

```powershell
cd "C:\GitHub\Azure-Sentinel\Solutions\BeyondTrustPMCloud"
.\Switch-GitHubUrls.ps1 -Mode ToProduction

# Then switch back to master branch
cd "C:\GitHub\Azure-Sentinel"
git checkout master
git branch -D test-package-deployment

# Delete remote test branch
git push origin --delete test-package-deployment
```

---

## 📊 Expected Results

**Successful Deployment Should Show:**
- ✅ All Azure resources created
- ✅ Both custom tables created with correct schemas
- ✅ DCRs properly configured and linked
- ✅ Function App running and executing on schedule
- ✅ Data flowing from BeyondTrust → Function App → DCR → Log Analytics
- ✅ No errors in Application Insights
- ✅ Data visible in Log Analytics queries within 30 minutes

---

## 📝 About createUiDefinition.json

**What is it?**
The `createUiDefinition.json` file defines the user interface that appears in Content Hub when users install your solution from the Sentinel marketplace. It controls:
- The wizard layout and navigation
- Parameter input fields (dropdowns, text boxes, etc.)
- Validation rules
- Help text and descriptions

**Current Status:**
The current `createUiDefinition.json` is **minimal** and only includes:
- ✅ Workspace selection dropdown
- ✅ Informational text about data connector and workbook
- ❌ NO parameters for BeyondTrust configuration (Base URL, Client ID, Secret, etc.)

**Why is it minimal?**
This is a **known limitation**. The current createUiDefinition.json was designed for a two-step installation process where:
1. User installs solution from Content Hub (gets metadata only)
2. User manually runs the ARM template deployment with full parameters

**Should you test it?**
- ✅ **YES** if you're testing the Content Hub publishing/installation experience
- ❌ **NO** if you're just testing the data connector deployment (use Option 2 instead)

**Future Enhancement:**
To make Content Hub installation seamless, the createUiDefinition.json should be enhanced to include all parameters from the azuredeploy template:
- BeyondTrust PM Cloud Base URL
- Client ID and Client Secret
- Polling intervals
- Log level
- Historical data timeframe
- Hosting plan SKU
- Storage account type

This would allow users to deploy the complete solution directly from Content Hub without needing to run a separate ARM template deployment.

---

## 📝 Additional Notes

- **First Run**: The function will retrieve historical data based on `HistoricalDataTimeframe` parameter (default: 1 day)
- **Subsequent Runs**: Incremental ingestion from last processed timestamp
- **Polling Intervals**: Activity Audits every 15 min, Client Events every 5 min (default)
- **State Management**: Stored in Azure Table Storage (automatically created)
- **Cost**: Consumption plan charges per execution + Log Analytics ingestion charges

---

## 🎯 Success Criteria

You've successfully tested the package deployment if:
1. ✅ Deployment completes without errors
2. ✅ All resources are created automatically
3. ✅ Tables appear with correct schemas
4. ✅ Function App executes successfully
5. ✅ Data appears in Log Analytics within 30 minutes
6. ✅ No errors in Application Insights logs

If all criteria are met, the solution is ready for production use! 🚀
