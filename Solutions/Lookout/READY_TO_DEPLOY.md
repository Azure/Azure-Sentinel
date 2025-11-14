# Your Ready-to-Deploy Commands

You have **2 Sentinel workspaces**. Choose which one to deploy to:

---

## Option 1: Deploy to `lookout-sentinel-ccf1` (Recommended)

This appears to be your CCF (Codeless Connector Framework) workspace.

### Copy and paste these commands in Cloud Shell:

```bash
# Set your configuration
SUBSCRIPTION_ID="a4b6a533-f801-49d5-ad81-719bc7264956"
RESOURCE_GROUP="lookout-sentinel-rg"
WORKSPACE_NAME="lookout-sentinel-ccf1"
LOCATION="eastus"

# Verify settings
echo "=== Deployment Configuration ==="
echo "Subscription: $SUBSCRIPTION_ID"
echo "Resource Group: $RESOURCE_GROUP"
echo "Workspace: $WORKSPACE_NAME"
echo "Location: $LOCATION"
echo ""
echo "Press Enter to continue or Ctrl+C to cancel..."
read

# Set subscription
az account set --subscription $SUBSCRIPTION_ID

# OPTIONAL: Test first (see what will change)
az deployment group what-if \
  --resource-group $RESOURCE_GROUP \
  --template-file mainTemplate.json \
  --parameters workspace=$WORKSPACE_NAME location=$LOCATION

# Deploy the solution
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file mainTemplate.json \
  --parameters workspace=$WORKSPACE_NAME location=$LOCATION \
  --name "lookout-v2-$(date +%Y%m%d-%H%M%S)"
```

---

## Option 2: Deploy to `LookoutdemoSentinel`

If you want to use your demo workspace instead:

```bash
# Set your configuration
SUBSCRIPTION_ID="a4b6a533-f801-49d5-ad81-719bc7264956"
RESOURCE_GROUP="lookoutsentinel"
WORKSPACE_NAME="LookoutdemoSentinel"
LOCATION="eastus"

# Verify settings
echo "=== Deployment Configuration ==="
echo "Subscription: $SUBSCRIPTION_ID"
echo "Resource Group: $RESOURCE_GROUP"
echo "Workspace: $WORKSPACE_NAME"
echo "Location: $LOCATION"
echo ""
echo "Press Enter to continue or Ctrl+C to cancel..."
read

# Set subscription
az account set --subscription $SUBSCRIPTION_ID

# Deploy the solution
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file mainTemplate.json \
  --parameters workspace=$WORKSPACE_NAME location=$LOCATION \
  --name "lookout-v2-$(date +%Y%m%d-%H%M%S)"
```

---

## Before You Run: Upload Files to Cloud Shell

You need to upload the solution files first. Choose **one** method:

### Method A: Clone from GitHub (if your code is pushed)

```bash
cd ~
git clone https://github.com/YOUR-GITHUB-USERNAME/Azure-Sentinel.git
cd Azure-Sentinel/Solutions/Lookout/Package
```

Replace `YOUR-GITHUB-USERNAME` with your actual GitHub username.

### Method B: Upload from Your Mac

1. On your Mac, create a zip file:
   ```bash
   cd /Users/fgravato/Documents/GitHub/Azure-Sentinel/Solutions/Lookout
   zip -r lookout-package.zip Package/
   ```

2. In Cloud Shell, click **Upload/Download** button (📁)
3. Upload `lookout-package.zip`
4. In Cloud Shell, run:
   ```bash
   cd ~
   unzip lookout-package.zip
   cd Package
   ls -la mainTemplate.json
   ```

You should see `mainTemplate.json` listed.

---

## Full Step-by-Step for Option 1 (lookout-sentinel-ccf1)

### Step 1: Upload Files
Choose Method A or B above to get files into Cloud Shell.

### Step 2: Navigate to Package Folder
```bash
cd ~/Package
# OR if you cloned from GitHub:
cd ~/Azure-Sentinel/Solutions/Lookout/Package
```

### Step 3: Verify File Exists
```bash
ls -la mainTemplate.json
```

You should see the file.

### Step 4: Set Variables
```bash
SUBSCRIPTION_ID="a4b6a533-f801-49d5-ad81-719bc7264956"
RESOURCE_GROUP="lookout-sentinel-rg"
WORKSPACE_NAME="lookout-sentinel-ccf1"
LOCATION="eastus"
```

### Step 5: Set Subscription
```bash
az account set --subscription $SUBSCRIPTION_ID
```

### Step 6: Deploy
```bash
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file mainTemplate.json \
  --parameters workspace=$WORKSPACE_NAME location=$LOCATION \
  --name "lookout-v2-deployment-$(date +%Y%m%d-%H%M%S)"
```

### Step 7: Wait
Deployment takes 5-10 minutes. You'll see progress output.

### Step 8: Verify
```bash
# Check deployment status
az deployment group list \
  --resource-group $RESOURCE_GROUP \
  --query "[0].{Name:name, State:properties.provisioningState}" \
  --output table
```

Look for `Succeeded` in the State column.

---

## After Deployment

### Check in Azure Portal

1. Go to **Microsoft Sentinel**
2. Click on `lookout-sentinel-ccf1` (or whichever you deployed to)
3. Click **Data connectors**
4. Search for "Lookout"
5. Should show **Lookout Mobile Threat Detection Connector**

### Verify Data Flow

In Sentinel → Logs, run:
```kql
LookoutMtdV2_CL
| where TimeGenerated > ago(1h)
| summarize count()
```

---

## Which Workspace Should You Use?

**I recommend Option 1** (`lookout-sentinel-ccf1`) because:
- It's in a dedicated resource group (`lookout-sentinel-rg`)
- The name suggests it's already set up for CCF connectors
- Cleaner organization

**Use Option 2** (`LookoutdemoSentinel`) if:
- You're just testing
- You want to keep production separate
- This is your demo environment

---

## Quick Copy-Paste (No Confirmations)

For the impatient - just run all commands at once:

```bash
# Upload files first (Method B from above), then:

cd ~/Package
SUBSCRIPTION_ID="a4b6a533-f801-49d5-ad81-719bc7264956"
RESOURCE_GROUP="lookout-sentinel-rg"
WORKSPACE_NAME="lookout-sentinel-ccf1"
LOCATION="eastus"

az account set --subscription $SUBSCRIPTION_ID

az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file mainTemplate.json \
  --parameters workspace=$WORKSPACE_NAME location=$LOCATION \
  --name "lookout-v2-deployment-$(date +%Y%m%d-%H%M%S)"
```

Done! ✅

---

**Which workspace do you want to deploy to?** Let me know if you need help with the next step!
