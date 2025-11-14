# Deploy Lookout Solution Using Azure Cloud Shell

## Super Simple - Just Copy & Paste Commands!

---

## Step 1: Open Azure Cloud Shell

1. Go to https://portal.azure.com
2. At the top right, click the **Cloud Shell icon** (looks like `>_`)
3. If prompted, choose **Bash** or **PowerShell** (either works)
4. Wait for it to load (creates storage first time, takes ~1 minute)

---

## Step 2: Upload the Solution Files

### Option A: Upload from GitHub (Easiest)

In Cloud Shell, copy and paste these commands:

```bash
# Download the solution files
cd ~
git clone https://github.com/YOUR-GITHUB-USERNAME/Azure-Sentinel.git
cd Azure-Sentinel/Solutions/Lookout
```

**Replace `YOUR-GITHUB-USERNAME`** with your actual GitHub username.

### Option B: Upload Files Manually

1. In Cloud Shell, click the **Upload/Download files** button (📁 icon)
2. Click **Upload**
3. Navigate to `/Users/fgravato/Documents/GitHub/Azure-Sentinel/Solutions/Lookout/Package`
4. Upload `mainTemplate.json`
5. Wait for upload to complete

Then run:
```bash
cd ~/Package
ls -la mainTemplate.json
```

You should see the file listed.

---

## Step 3: Set Your Configuration

Copy and paste these commands **ONE AT A TIME** (replace the values):

```bash
# Your Azure subscription ID
SUBSCRIPTION_ID="12345678-1234-1234-1234-123456789abc"

# Your resource group name (where Sentinel is)
RESOURCE_GROUP="your-sentinel-resource-group"

# Your Sentinel workspace name
WORKSPACE_NAME="your-sentinel-workspace"

# Your Azure region (e.g., eastus, westus2, etc.)
LOCATION="eastus"
```

To find these values:
- **SUBSCRIPTION_ID**: Run `az account show --query id -o tsv`
- **RESOURCE_GROUP**: Run `az group list --query "[].name" -o table`
- **WORKSPACE_NAME**: Run `az monitor log-analytics workspace list --query "[].name" -o table`
- **LOCATION**: Same as your resource group location

---

## Step 4: Set the Right Subscription

```bash
az account set --subscription $SUBSCRIPTION_ID
az account show
```

**Check**: You should see your subscription name displayed.

---

## Step 5: Test Before Deploying (Optional but Recommended)

This shows what will change WITHOUT actually changing anything:

```bash
az deployment group what-if \
  --resource-group $RESOURCE_GROUP \
  --template-file mainTemplate.json \
  --parameters \
    workspace=$WORKSPACE_NAME \
    location=$LOCATION
```

**Look for**:
- Resources with `~` (Modify) = Good! Updating existing
- Resources with `+` (Create) = Creating new components
- Resources with `-` (Delete) = Bad! Don't proceed if you see this

---

## Step 6: Deploy the Solution

```bash
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file mainTemplate.json \
  --parameters \
    workspace=$WORKSPACE_NAME \
    location=$LOCATION \
  --name "lookout-v2-deployment-$(date +%Y%m%d-%H%M%S)"
```

**This will take 5-10 minutes.** You'll see output showing progress.

---

## Step 7: Check Deployment Status

```bash
# List recent deployments
az deployment group list \
  --resource-group $RESOURCE_GROUP \
  --query "[].{Name:name, State:properties.provisioningState, Timestamp:properties.timestamp}" \
  --output table
```

**Success looks like**: `ProvisioningState: Succeeded`

---

## Step 8: Verify in Azure Portal

1. Go to **Microsoft Sentinel** → Your workspace
2. Click **Data connectors** on the left
3. Search for "Lookout"
4. You should see: **Lookout Mobile Threat Detection Connector**
5. Status should show **Connected** (or ready to configure)

---

## Step 9: Check Components Deployed

Run this in Cloud Shell to see what was created:

```bash
# List all Lookout-related resources
az resource list \
  --resource-group $RESOURCE_GROUP \
  --query "[?contains(name, 'Lookout')].{Name:name, Type:type, Location:location}" \
  --output table
```

You should see:
- Data Connector Definition
- Data Connector (polling config)
- Data Collection Rule (DCR)
- Data Collection Endpoint (DCE)

---

## Step 10: Validate Data Flow

1. In Azure Portal, go to Sentinel → **Logs**
2. Run this query:

```kql
LookoutMtdV2_CL
| where TimeGenerated > ago(1h)
| summarize count()
```

**If you see data**: Great! Everything works!

**If no data**: The connector is deployed but not configured yet (need to add Lookout API credentials).

---

## Alternative: Upload Your Local Files to Cloud Shell

If you want to deploy YOUR modified files:

### Step 1: Prepare Files Locally

On your Mac, create a zip of the solution:

```bash
cd /Users/fgravato/Documents/GitHub/Azure-Sentinel/Solutions
zip -r Lookout.zip Lookout/
```

### Step 2: Upload to Cloud Shell

1. Open Cloud Shell in Azure Portal
2. Click the **Upload/Download** button (📁)
3. Upload `Lookout.zip`
4. In Cloud Shell, run:

```bash
unzip Lookout.zip
cd Lookout
```

### Step 3: Deploy from Package

```bash
cd Package

# Set your variables (same as before)
SUBSCRIPTION_ID="your-subscription-id"
RESOURCE_GROUP="your-resource-group"
WORKSPACE_NAME="your-workspace-name"
LOCATION="eastus"

# Deploy
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file mainTemplate.json \
  --parameters \
    workspace=$WORKSPACE_NAME \
    location=$LOCATION
```

---

## Troubleshooting

### Error: "template file not found"
```bash
# Check where you are
pwd

# List files
ls -la

# Navigate to Package folder
cd ~/Azure-Sentinel/Solutions/Lookout/Package
```

### Error: "subscription not found"
```bash
# List all subscriptions
az account list --output table

# Set the right one
az account set --subscription "YOUR-SUBSCRIPTION-NAME"
```

### Error: "resource group not found"
```bash
# List resource groups
az group list --query "[].name" -o table

# Verify it exists
az group show --name $RESOURCE_GROUP
```

### Error: "deployment failed"
```bash
# Get detailed error
az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name lookout-v2-deployment-TIMESTAMP \
  --query "properties.error"
```

---

## After Deployment: Configure the Connector

1. Go to Sentinel → **Data connectors**
2. Find "Lookout Mobile Threat Detection Connector"
3. Click **Open connector page**
4. Enter your **Lookout API Key**
5. Click **Connect**
6. Wait 5-10 minutes for data to start flowing

---

## Quick Reference Commands

```bash
# Check deployment status
az deployment group list -g $RESOURCE_GROUP --query "[0].properties.provisioningState"

# View deployment outputs
az deployment group show -g $RESOURCE_GROUP -n DEPLOYMENT_NAME --query properties.outputs

# Delete deployment (if you need to start over)
az deployment group delete -g $RESOURCE_GROUP -n DEPLOYMENT_NAME

# Clean up resources (CAREFUL - this deletes things!)
az resource delete --ids $(az resource list -g $RESOURCE_GROUP --query "[?contains(name, 'Lookout')].id" -o tsv)
```

---

## Summary: The 3-Command Deployment

If you just want to deploy quickly (skip all validation):

```bash
# 1. Set variables
SUBSCRIPTION_ID="your-sub-id"
RESOURCE_GROUP="your-rg"
WORKSPACE_NAME="your-workspace"
LOCATION="eastus"

# 2. Set subscription
az account set --subscription $SUBSCRIPTION_ID

# 3. Deploy
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file mainTemplate.json \
  --parameters workspace=$WORKSPACE_NAME location=$LOCATION
```

Done! ✅

---

**Need help?** Let me know which step is giving you trouble!
