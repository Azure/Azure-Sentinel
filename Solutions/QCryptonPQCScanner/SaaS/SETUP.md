# QCrypton PQC Scanner — SaaS Transactable Offer Setup

## Prerequisites

1. **Azure AD App Registration** — for calling the SaaS Fulfillment API
2. **Partner Center account** — with publisher ID `qcryptoninc1788706847984`
3. **Azure subscription** — for deploying the fulfillment infrastructure

---

## Step 1: Create Azure AD App Registration

1. Go to **Azure Portal > Azure Active Directory > App registrations > New registration**
2. Name: `QCrypton-Marketplace-Fulfillment`
3. Supported account types: **Single tenant**
4. Register, then note the **Client ID** and **Tenant ID**
5. Go to **Certificates & secrets > New client secret** — save the secret value
6. Go to **API permissions > Add permission > APIs my organization uses**
7. Search for `Microsoft Marketplace` (app ID: `62d94f6c-d599-489b-a797-3e10e42fbe22`)
8. Add delegated permission: `Marketplace.ReadWrite.All`

---

## Step 2: Deploy Fulfillment Infrastructure

```bash
az deployment group create \
  --resource-group qcrypton-saas-test-rg \
  --template-file SaaS/deploy/azuredeploy.json \
  --parameters \
    appNamePrefix=qcrypton-saas \
    azureTenantId=<your-tenant-id> \
    azureClientId=<your-client-id> \
    azureClientSecret=<your-client-secret>
```

Note the outputs:
- `landingPageUrl` — configure this in Partner Center
- `webhookUrl` — configure this in Partner Center

---

## Step 3: Deploy the Azure Functions

```bash
cd SaaS/functions

# Create a virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Deploy to Azure
func azure functionapp publish qcrypton-saas-func
```

---

## Step 4: Configure Partner Center

### 4a. Technical Configuration

1. Go to **Partner Center > Marketplace offers > QCrypton PQC Scanner - SaaS**
2. Navigate to **Technical configuration**
3. Set:
   - **Landing page URL**: `https://qcrypton-saas-func.azurewebsites.net/api/landing`
   - **Connection webhook URL**: `https://qcrypton-saas-func.azurewebsites.net/api/webhook`
   - **Azure Active Directory tenant ID**: `<your-tenant-id>`
   - **Azure Active Directory application ID**: `<your-client-id>`

### 4b. Plan Setup

1. Go to **Plan overview > Create new plan**
2. Create three plans matching `SaaS/plans.json`:

   | Plan ID | Display Name | Price | Billing |
   |---------|-------------|-------|---------|
   | `basic` | Basic | $299/mo | Monthly |
   | `professional` | Professional | $999/mo | Monthly |
   | `enterprise` | Enterprise | $9,999/yr | Annual |

3. For each plan:
   - Set **Markets**: United States (expand later)
   - Set **Pricing model**: Flat rate
   - Set **Billing term**: Monthly or Annual
   - Set **Price**: As listed above

### 4c. Offer Listing

1. Go to **Offer listing**
2. Update description to reference the three pricing tiers
3. Add screenshots of the Sentinel workbook and data connector

### 4d. Publish

1. **Review and publish** the updated offer
2. Microsoft will validate the technical configuration (landing page + webhook reachable)
3. Once approved, the offer becomes **transactable**

---

## Step 5: Test the Integration

### Test with Microsoft's Mock APIs

Before going live, test the full flow:

1. **Landing page test**: Visit `https://<func-app>/api/landing?token=test-token`
2. **Webhook test**: Send a test POST to `https://<func-app>/api/webhook`:

```bash
curl -X POST https://qcrypton-saas-func.azurewebsites.net/api/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "action": "Unsubscribe",
    "subscriptionId": "test-sub-id",
    "id": "test-operation-id",
    "planId": "basic",
    "quantity": 1,
    "publisherId": "qcryptoninc1788706847984"
  }'
```

3. Use the **Marketplace mock API** in Partner Center to simulate purchases

---

## Architecture

```
Customer buys in Azure Marketplace
        |
        v
Microsoft redirects to Landing Page (Azure Function)
        |
        v
Landing Page resolves token via SaaS Fulfillment API v2
        |
        v
Customer clicks "Activate"
        |
        v
API Key provisioned in Key Vault
Subscription activated with Microsoft
        |
        v
Customer configures Sentinel Data Connector with API key
        |
        v
Sentinel polls api.qcrypton.com/v1/pqc/findings
        |
        v
PQC findings flow into PQReadiness_CL table
```

## Subscription Lifecycle

```
Purchase → Landing Page → Activate → Active
                                       |
                          +------------+------------+
                          |            |            |
                      ChangePlan   Suspend    Unsubscribe
                          |            |            |
                      Update Key   Disable Key  Revoke Key
                       Quotas          |
                                   Reinstate
                                       |
                                   Re-enable Key
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `fulfillment/marketplace_client.py` | SaaS Fulfillment API v2 client |
| `functions/webhook_handler/` | Marketplace lifecycle event handler |
| `functions/landing_page/` | Customer activation landing page |
| `functions/shared/api_key_manager.py` | API key provisioning tied to subscriptions |
| `deploy/azuredeploy.json` | ARM template for infrastructure |
| `plans.json` | Pricing plan definitions |
