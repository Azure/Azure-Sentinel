# How to Find Your Azure Variables

## Easy Way - Use Cloud Shell to Find Everything!

Open Cloud Shell (click `>_` at top of Azure Portal), then run these commands:

---

## 1. Get Your Subscription ID

```bash
az account show --query id -o tsv
```

**Copy the output** - it looks like: `12345678-1234-1234-1234-123456789abc`

Or see all your subscriptions:
```bash
az account list --query "[].{Name:name, SubscriptionId:id}" -o table
```

---

## 2. Get Your Resource Group Name

```bash
az group list --query "[].name" -o table
```

**Look for the resource group** where your Sentinel workspace is located.

Usually named something like:
- `rg-sentinel`
- `sentinel-rg`
- `SecurityOperations`

---

## 3. Get Your Workspace Name

```bash
az monitor log-analytics workspace list --query "[].{Name:name, ResourceGroup:resourceGroup, Location:location}" -o table
```

**Copy the Name** of your Sentinel workspace.

---

## 4. Get Your Location

```bash
az group show --name YOUR-RESOURCE-GROUP --query location -o tsv
```

Replace `YOUR-RESOURCE-GROUP` with the name from step 2.

Common locations:
- `eastus`
- `westus2`
- `centralus`
- `westeurope`
- `uksouth`

---

## Alternative: Find in Azure Portal (Visual Guide)

### Finding Subscription ID

1. In Azure Portal, click the **🔍 Search bar** at the top
2. Type **"Subscriptions"**
3. Click **Subscriptions**
4. You'll see a list - copy the **Subscription ID** column
5. It looks like: `12345678-1234-1234-1234-123456789abc`

---

### Finding Resource Group

1. In Azure Portal search bar, type **"Microsoft Sentinel"**
2. Click **Microsoft Sentinel**
3. You'll see your workspace(s) listed
4. Look at the **Resource Group** column
5. Copy that name (e.g., `sentinel-production-rg`)

---

### Finding Workspace Name

1. Same page as above (Microsoft Sentinel)
2. Look at the **Name** column
3. Copy the workspace name (e.g., `law-sentinel-prod`)

---

### Finding Location

1. In search bar, type **"Resource groups"**
2. Click **Resource groups**
3. Find your resource group from the list
4. Click on it
5. Look at **Location** in the Overview (e.g., `East US`)
6. Convert to Azure format:
   - `East US` → `eastus`
   - `West US 2` → `westus2`
   - `Central US` → `centralus`
   - `West Europe` → `westeurope`
   - `UK South` → `uksouth`

---

## Quick Test - All in One Command

Run this in Cloud Shell to see everything at once:

```bash
echo "=== YOUR AZURE CONFIGURATION ==="
echo ""
echo "SUBSCRIPTION_ID:"
az account show --query id -o tsv
echo ""
echo "RESOURCE_GROUPS:"
az group list --query "[].name" -o table
echo ""
echo "SENTINEL WORKSPACES:"
az monitor log-analytics workspace list --query "[].{Name:name, ResourceGroup:resourceGroup, Location:location}" -o table
```

Copy the values from the output!

---

## Example: What It Should Look Like

After you find your values, they should look like this:

```bash
SUBSCRIPTION_ID="a1b2c3d4-e5f6-7890-abcd-ef1234567890"
RESOURCE_GROUP="rg-sentinel-production"
WORKSPACE_NAME="law-sentinel-workspace"
LOCATION="eastus"
```

---

## Still Can't Find Them?

### Option 1: Ask Someone
- Your Azure administrator
- The person who created the Sentinel workspace
- Your IT/Security team

### Option 2: Create a Test Environment

If you have permissions, create a test workspace:

```bash
# In Cloud Shell
az group create --name "rg-sentinel-test" --location "eastus"

az monitor log-analytics workspace create \
  --resource-group "rg-sentinel-test" \
  --workspace-name "law-sentinel-test" \
  --location "eastus"
```

Then use:
- RESOURCE_GROUP: `rg-sentinel-test`
- WORKSPACE_NAME: `law-sentinel-test`
- LOCATION: `eastus`

---

## Copy-Paste Template

Once you have the values, fill this in:

```bash
# Paste your values here (remove the placeholder text)
SUBSCRIPTION_ID="PASTE-YOUR-SUBSCRIPTION-ID-HERE"
RESOURCE_GROUP="PASTE-YOUR-RESOURCE-GROUP-HERE"
WORKSPACE_NAME="PASTE-YOUR-WORKSPACE-NAME-HERE"
LOCATION="PASTE-LOCATION-HERE"

# Verify they're set correctly
echo "Subscription: $SUBSCRIPTION_ID"
echo "Resource Group: $RESOURCE_GROUP"
echo "Workspace: $WORKSPACE_NAME"
echo "Location: $LOCATION"
```

**Check the output** - make sure nothing says "PASTE-YOUR..." anymore!

---

## Next Step

Once you have all 4 values, go back to [CLOUDSHELL_DEPLOYMENT.md](CLOUDSHELL_DEPLOYMENT.md) and continue from **Step 3**.
