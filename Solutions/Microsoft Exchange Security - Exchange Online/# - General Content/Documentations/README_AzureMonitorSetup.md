# Azure Monitor Log Ingestion API Setup for Exchange Security Insights

This guide covers the full setup of Azure Monitor components required by the ESI Collector to ingest Exchange security data into Microsoft Sentinel using the Log Ingestion API.

> [!IMPORTANT]
> The Log Ingestion API replaces the legacy Log Analytics HTTP Data Collector API (deprecated in 2025). All new deployments should use the Azure Monitor Ingestion API.

## Architecture Overview

The ingestion pipeline consists of these Azure components:

```text
ESI Collector Script
        │
        ▼
  Entra ID App Registration  ──(certificate auth)──►  Azure AD Token
        │
        ▼
  Data Collection Endpoint (DCE)
        │
        ▼
  Data Collection Rule (DCR)  ──(transform + route)──►  Log Analytics Custom Tables
        │
        ▼
  Microsoft Sentinel Workspace
```

| Component | Purpose |
|-----------|---------|
| Entra ID Application | Authenticates the collector to the ingestion endpoint |
| Self-signed Certificate | Credential for the application (preferred over secrets) |
| Data Collection Endpoint (DCE) | HTTPS endpoint receiving log payloads |
| Data Collection Rule (DCR) | Defines schema, transforms, and routing to tables |
| Custom Log Analytics Tables | Store the collected Exchange configuration data |

## Prerequisites

Before you begin, verify these requirements:

- An Azure subscription with Contributor access on the target resource group
- A Log Analytics workspace (where Microsoft Sentinel is enabled)
- PowerShell 7.0+ with the following modules installed:
  - `Az.Accounts`
  - `Az.Monitor`
  - `Az.Resources`
  - `Microsoft.Graph` (if creating the Entra ID Application via script)
- Azure CLI (alternative for deployment and permission management)
- OpenSSL or PowerShell `New-SelfSignedCertificate` for certificate generation

## Step 1: Create a Self-Signed Certificate

The ESI Collector authenticates to Azure using a certificate-based credential. You can use an existing PKI certificate or generate a self-signed one.

### Option A: PowerShell (Windows)

```powershell
# Create a self-signed certificate valid for 2 years
$cert = New-SelfSignedCertificate `
    -Subject "CN=ESI-Collector-Auth" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -KeyExportPolicy Exportable `
    -KeySpec Signature `
    -KeyLength 2048 `
    -HashAlgorithm SHA256 `
    -NotAfter (Get-Date).AddYears(2)

# Display the thumbprint (you need it for configuration)
Write-Host "Certificate Thumbprint: $($cert.Thumbprint)"

# Export the public key (.cer) for uploading to Entra ID Application
Export-Certificate -Cert $cert -FilePath ".\ESI-Collector-Auth.cer" -Type CERT

# (Optional) Export the PFX for Azure Automation import
$pwd = ConvertTo-SecureString -String "YourStrongPassword" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath ".\ESI-Collector-Auth.pfx" -Password $pwd
```

### Option B: OpenSSL (Linux / macOS)

```bash
# Generate private key and self-signed certificate (2 years)
openssl req -x509 -newkey rsa:2048 \
    -keyout esi-collector-key.pem \
    -out esi-collector-cert.pem \
    -sha256 -days 730 \
    -subj "/CN=ESI-Collector-Auth" \
    -nodes

# Convert to PFX for Azure Automation
openssl pkcs12 -export \
    -out esi-collector.pfx \
    -inkey esi-collector-key.pem \
    -in esi-collector-cert.pem

# Get the thumbprint
openssl x509 -in esi-collector-cert.pem -noout -fingerprint -sha1 \
    | sed 's/://g' | cut -d= -f2
```

> [!NOTE]
> Record the certificate thumbprint. You need it when configuring the collector and when running from a server. For Azure Automation, import the PFX into the Automation Account certificate store.

## Step 2: Register an Entra ID Application

The application identity enables the collector to obtain tokens for the Azure Monitor ingestion endpoint.

### Option A: Azure Portal

1. Navigate to **Microsoft Entra ID** > **App registrations** > **New registration**
2. Set the display name to `ESI-Collector-LogIngestion` (or your preferred name)
3. Leave the redirect URI empty (no interactive sign-in needed)
4. Click **Register**
5. Note the **Application (client) ID** and **Directory (tenant) ID** from the Overview page
6. Navigate to **Certificates & secrets** > **Certificates** > **Upload certificate**
7. Upload the `.cer` file generated in Step 1
8. Create a **Service Principal** (automatic when registering via portal)

### Option B: PowerShell with Microsoft Graph

```powershell
# Connect to Microsoft Graph
Connect-MgGraph -Scopes "Application.ReadWrite.All"

# Create the application
$app = New-MgApplication -DisplayName "ESI-Collector-LogIngestion"

# Create the service principal
$sp = New-MgServicePrincipal -AppId $app.AppId

# Upload the certificate
$certContent = [System.IO.File]::ReadAllBytes(".\ESI-Collector-Auth.cer")
$base64Cert = [System.Convert]::ToBase64String($certContent)

$keyCredential = @{
    Type        = "AsymmetricX509Cert"
    Usage       = "Verify"
    Key         = [System.Convert]::FromBase64String($base64Cert)
    DisplayName = "ESI-Collector-Auth"
}

Update-MgApplication -ApplicationId $app.Id -KeyCredentials @($keyCredential)

# Display information needed for configuration
Write-Host "Application (Client) ID: $($app.AppId)"
Write-Host "Object ID: $($app.Id)"
Write-Host "Service Principal Object ID: $($sp.Id)"
```

### Option C: Azure CLI

```bash
# Create the application with the certificate
az ad app create --display-name "ESI-Collector-LogIngestion"

# Get the App ID
APP_ID=$(az ad app list --display-name "ESI-Collector-LogIngestion" --query "[0].appId" -o tsv)

# Create a service principal
az ad sp create --id $APP_ID

# Upload the certificate
az ad app credential reset --id $APP_ID --cert @esi-collector-cert.pem --append

echo "Application (Client) ID: $APP_ID"
```

> [!TIP]
> No API permissions are required on the Entra ID Application itself. Access control is handled through Azure RBAC on the Data Collection Rule.

## Step 3: Deploy the Data Collection Endpoint, Rules, and Tables

The ARM template in the `Deployments` folder creates all required Azure Monitor resources:

- 1 Data Collection Endpoint (DCE)
- Up to 3 Custom Log Analytics tables (each controlled by a master switch):
  - `ESIAPIExchangeOnPremConfig_CL` (Exchange On-Premises configuration)
  - `ESIAPIExchangeOnlineConfig_CL` (Exchange Online configuration)
  - `ExchangeOnlineMessageTracking_CL` (message tracking)
- Up to 3 Data Collection Rules (one per table):
  - `DCR-ESI-OnPremisesConfig`
  - `DCR-ESI-OnlineConfig`
  - `DCR-ESI-MessageTracking`

> [!TIP]
> Master parameters `deployTables`, `deployDataCollection`, `deployOnPremConfigTable`, `deployOnlineConfigTable`, and `deployMessageTrackingTable` let you deploy any subset. See [README_LogIngestionAPI.md](README_LogIngestionAPI.md) for the full parameter reference.

### Option A: Using Azure CLI

```bash
# Login and set subscription
az login
az account set --subscription "YOUR_SUBSCRIPTION_ID"

# Create a resource group (if needed)
az group create --name "rg-sentinel-esi" --location "eastus"

# Deploy the template
az deployment group create \
    --resource-group "rg-sentinel-esi" \
    --template-file azuredeploy_ESI_LogIngestionAPI.json \
    --parameters azuredeploy_ESI_LogIngestionAPI.parameters.json
```

### Option B: Using PowerShell

```powershell
# Login and set subscription
Connect-AzAccount
Set-AzContext -SubscriptionId "YOUR_SUBSCRIPTION_ID"

# Create a resource group (if needed)
New-AzResourceGroup -Name "rg-sentinel-esi" -Location "eastus"

# Deploy the template
New-AzResourceGroupDeployment `
    -ResourceGroupName "rg-sentinel-esi" `
    -TemplateFile "azuredeploy_ESI_LogIngestionAPI.json" `
    -TemplateParameterFile "azuredeploy_ESI_LogIngestionAPI.parameters.json"
```

### Option C: Using Azure Portal

1. Navigate to **Deploy a custom template** in the Azure Portal
2. Click **Build your own template in the editor**
3. Paste the content of `azuredeploy_ESI_LogIngestionAPI.json`
4. Fill in the parameters:

   | Parameter | Description | Example |
   |-----------|-------------|---------|
   | `workspaceName` | Name of your existing Log Analytics workspace | `law-sentinel-prod` |
   | `location` | Azure region matching your workspace | `eastus` |
   | `dataCollectionEndpointName` | Name for the DCE | `DCE-ESI-LogIngestion` |
   | `dataCollectionRuleOnPremisesConfigName` | Name for the On-Premises Config DCR | `DCR-ESI-OnPremisesConfig` |
   | `dataCollectionRuleOnlineConfigName` | Name for the Online Config DCR | `DCR-ESI-OnlineConfig` |
   | `dataCollectionRuleMessageTrackingName` | Name for the Message Tracking DCR | `DCR-ESI-MessageTracking` |
   | `retentionInDays` | Data retention period (30-730) | `90` |
   | `deployTables` | Deploy the custom Log Analytics tables | `true` |
   | `deployDataCollection` | Deploy the DCE and DCRs | `true` |
   | `deployOnPremConfigTable` | Deploy the On-Premises config resources | `true` |
   | `deployOnlineConfigTable` | Deploy the Exchange Online config resources | `true` |
   | `deployMessageTrackingTable` | Deploy message tracking resources | `true` |

5. Click **Review + create**

### Collect Deployment Outputs

After deployment, retrieve these values from the outputs:

```powershell
$deployment = Get-AzResourceGroupDeployment `
    -ResourceGroupName "rg-sentinel-esi" `
    -Name "YOUR_DEPLOYMENT_NAME"

# Values needed for configuration
$deployment.Outputs.dataCollectionEndpointUri.Value                             # DCE URI
$deployment.Outputs.dataCollectionRuleOnPremisesConfigImmutableId.Value         # DCR Immutable ID (On-Premises Config)
$deployment.Outputs.dataCollectionRuleOnlineConfigImmutableId.Value             # DCR Immutable ID (Online Config)
$deployment.Outputs.dataCollectionRuleMessageTrackingImmutableId.Value          # DCR Immutable ID (Message Tracking)
```

Or via Azure CLI:

```bash
az deployment group show \
    --resource-group "rg-sentinel-esi" \
    --name "YOUR_DEPLOYMENT_NAME" \
    --query properties.outputs
```

> [!IMPORTANT]
> Record the **DCE URI** and **DCR Immutable IDs** from the deployment outputs. You need these values for both the permission assignment and the collector configuration.

## Step 4: Assign Permissions on the Data Collection Rule

The Entra ID Application (service principal) requires the **Monitoring Metrics Publisher** role on each Data Collection Rule it sends data to.

### Option A: Azure CLI

```bash
# Get the service principal Object ID
SP_OBJECT_ID=$(az ad sp list --filter "appId eq 'YOUR_APP_ID'" --query "[0].id" -o tsv)

# Assign on On-Premises Config DCR (if deployed)
az role assignment create \
    --role "Monitoring Metrics Publisher" \
    --assignee-object-id "$SP_OBJECT_ID" \
    --assignee-principal-type ServicePrincipal \
    --scope "/subscriptions/YOUR_SUB_ID/resourceGroups/rg-sentinel-esi/providers/Microsoft.Insights/dataCollectionRules/DCR-ESI-OnPremisesConfig"

# Assign on Online Config DCR (if deployed)
az role assignment create \
    --role "Monitoring Metrics Publisher" \
    --assignee-object-id "$SP_OBJECT_ID" \
    --assignee-principal-type ServicePrincipal \
    --scope "/subscriptions/YOUR_SUB_ID/resourceGroups/rg-sentinel-esi/providers/Microsoft.Insights/dataCollectionRules/DCR-ESI-OnlineConfig"

# Assign on Message Tracking DCR (if deployed)
az role assignment create \
    --role "Monitoring Metrics Publisher" \
    --assignee-object-id "$SP_OBJECT_ID" \
    --assignee-principal-type ServicePrincipal \
    --scope "/subscriptions/YOUR_SUB_ID/resourceGroups/rg-sentinel-esi/providers/Microsoft.Insights/dataCollectionRules/DCR-ESI-MessageTracking"
```

### Option B: PowerShell

```powershell
# Get the service principal Object ID
$sp = Get-AzADServicePrincipal -ApplicationId "YOUR_APP_ID"

# Assign on On-Premises Config DCR (if deployed)
New-AzRoleAssignment `
    -ObjectId $sp.Id `
    -RoleDefinitionName "Monitoring Metrics Publisher" `
    -Scope "/subscriptions/YOUR_SUB_ID/resourceGroups/rg-sentinel-esi/providers/Microsoft.Insights/dataCollectionRules/DCR-ESI-OnPremisesConfig"

# Assign on Online Config DCR (if deployed)
New-AzRoleAssignment `
    -ObjectId $sp.Id `
    -RoleDefinitionName "Monitoring Metrics Publisher" `
    -Scope "/subscriptions/YOUR_SUB_ID/resourceGroups/rg-sentinel-esi/providers/Microsoft.Insights/dataCollectionRules/DCR-ESI-OnlineConfig"

# Assign on Message Tracking DCR (if deployed)
New-AzRoleAssignment `
    -ObjectId $sp.Id `
    -RoleDefinitionName "Monitoring Metrics Publisher" `
    -Scope "/subscriptions/YOUR_SUB_ID/resourceGroups/rg-sentinel-esi/providers/Microsoft.Insights/dataCollectionRules/DCR-ESI-MessageTracking"
```

### Option C: Azure Portal

1. Navigate to **Monitor** > **Data Collection Rules**
2. Select your DCR (e.g., `DCR-ESI-OnlineConfig`)
3. Go to **Access control (IAM)** > **Add role assignment**
4. Select role **Monitoring Metrics Publisher**
5. Under Members, select **User, group, or service principal**
6. Search for your application name (`ESI-Collector-LogIngestion`)
7. Click **Review + assign**
8. Repeat for the On-Premises Config DCR and the Message Tracking DCR if deployed

> [!WARNING]
> Without the **Monitoring Metrics Publisher** role on the DCR, the collector receives `403 Forbidden` errors when ingesting data. Verify the assignment before testing.

## Step 5: Configure the ESI Collector

Update the `CollectExchSecConfiguration.json` file with the values collected during setup.

### Log Collection Section

```json
{
    "LogCollection": {
        "ActivateLogUpdloadToSentinel": "true",
        "SentinelLogIngestionAPIActivated": "true",
        "DataCollectionEndpointURI": "https://YOUR-DCE-NAME.region.ingest.monitor.azure.com",
        "DCRImmutableId": "dcr-00000000000000000000000000000000",
        "UseManagedIdentity": "false",
        "TargetLogTenantID": "YOUR-TENANT-ID",
        "TargetLogAppID": "YOUR-APPLICATION-CLIENT-ID",
        "TargetLogCertificateThumbprint": "YOUR-CERTIFICATE-THUMBPRINT",
        "LogTypeName": "ESIExchangeConfig",
        "CSVOutputFile": "ExchSecIns.csv",
        "ExportDomainsInformation": "True"
    }
}
```

| Field | Value Source |
|-------|-------------|
| `DataCollectionEndpointURI` | Deployment output: `dataCollectionEndpointUri` |
| `DCRImmutableId` | Deployment output matching the target table: `dataCollectionRuleOnPremisesConfigImmutableId`, `dataCollectionRuleOnlineConfigImmutableId`, or `dataCollectionRuleMessageTrackingImmutableId` |
| `TargetLogTenantID` | Entra ID > Overview > Tenant ID |
| `TargetLogAppID` | Entra ID > App registrations > Application (client) ID |
| `TargetLogCertificateThumbprint` | Certificate thumbprint from Step 1 |

> [!NOTE]
> `DCRImmutableId` must correspond to the DCR routing to the table you want to target (on-premises, online, or message tracking). Set the ESI collector `LogTypeName` accordingly (`ESIExchangeConfig`, `ESIExchangeOnlineConfig`, or `ExchangeOnlineMessageTracking`).

### Azure Automation Execution (Managed Identity)

When running from Azure Automation with a managed identity, set `UseManagedIdentity` to `"true"` and assign the **Monitoring Metrics Publisher** role to the Automation Account's system-assigned managed identity on each DCR.

```json
{
    "LogCollection": {
        "SentinelLogIngestionAPIActivated": "true",
        "UseManagedIdentity": "true",
        "DataCollectionEndpointURI": "https://YOUR-DCE-NAME.region.ingest.monitor.azure.com",
        "DCRImmutableId": "dcr-00000000000000000000000000000000"
    }
}
```

```powershell
# Assign Monitoring Metrics Publisher to the Automation Account's managed identity
$automationMI = (Get-AzAutomationAccount -ResourceGroupName "rg-automation" -Name "aa-esi-collector").Identity.PrincipalId

# Repeat this assignment for every DCR you send to (OnPremises, Online, MessageTracking).
New-AzRoleAssignment `
    -ObjectId $automationMI `
    -RoleDefinitionName "Monitoring Metrics Publisher" `
    -Scope "/subscriptions/YOUR_SUB_ID/resourceGroups/rg-sentinel-esi/providers/Microsoft.Insights/dataCollectionRules/DCR-ESI-OnlineConfig"
```

## Step 6: Validate the Setup

### Test Authentication

```powershell
# Connect using the certificate
Connect-AzAccount `
    -CertificateThumbprint "YOUR_CERTIFICATE_THUMBPRINT" `
    -ApplicationId "YOUR_APP_ID" `
    -Tenant "YOUR_TENANT_ID" `
    -ServicePrincipal

# Get a token for the Monitor endpoint
$context = Get-AzContext
$token = (Get-AzAccessToken -ResourceUrl "https://monitor.azure.com").Token

Write-Host "Token acquired successfully" -ForegroundColor Green
```

### Send a Test Payload

```powershell
$dceUri = "https://YOUR-DCE-NAME.region.ingest.monitor.azure.com"
$dcrImmutableId = "dcr-00000000000000000000000000000000"
$streamName = "Custom-ESIExchangeOnlineConfig"

$uri = "$dceUri/dataCollectionRules/$dcrImmutableId/streams/$($streamName)?api-version=2023-01-01"

$testData = @(
    @{
        TimeGenerated        = (Get-Date).ToUniversalTime().ToString("o")
        EntryDate            = (Get-Date).ToUniversalTime().ToString("o")
        GenerationInstanceID = "test-validation"
        ESIEnvironment       = "TestEnvironment"
        Section              = "ValidationTest"
        RawData              = '{"test": true}'
    }
) | ConvertTo-Json -AsArray

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type"  = "application/json"
}

$response = Invoke-RestMethod -Uri $uri -Method Post -Body $testData -Headers $headers
Write-Host "Data sent successfully" -ForegroundColor Green
```

### Verify Data in Log Analytics

Wait a few minutes, then query your workspace:

```kql
ESIAPIExchangeOnlineConfig_CL
| where ESIEnvironment_s == "TestEnvironment"
| where Section_s == "ValidationTest"
| project TimeGenerated, ESIEnvironment_s, Section_s, GenerationInstanceID_g
```

## Stream Names Reference

When the collector sends data via the Log Ingestion API, it targets these stream names:

| Table                              | Stream Name                              |
|------------------------------------|------------------------------------------|
| `ESIAPIExchangeOnPremConfig_CL`    | `Custom-ESIExchangeConfig`               |
| `ESIAPIExchangeOnlineConfig_CL`    | `Custom-ESIExchangeOnlineConfig`         |
| `ExchangeOnlineMessageTracking_CL` | `Custom-ExchangeOnlineMessageTracking`   |

> [!NOTE]
> The on-premises and online configuration tables also expose extracted `Identity_*` sub-property columns (`Identity_Depth_d`, `Identity_DistinguishedName_s`, `Identity_ObjectGuid_g`, ...). These are populated by the DCR `transformKql` from the source `Identity` object using `parse_json`. See the full column list in [README_LogIngestionAPI.md](README_LogIngestionAPI.md#table-schemas).

## Troubleshooting

### Authentication Errors (401 / 403)

1. Verify the certificate thumbprint matches the one uploaded to the Entra ID Application
2. Confirm the Tenant ID and Application ID in the configuration
3. Check that the **Monitoring Metrics Publisher** role is correctly assigned on the DCR (not the DCE or workspace)

### DCE Not Reachable

1. Validate the `DataCollectionEndpointURI` from the deployment outputs
2. Ensure firewall or NSG rules allow outbound HTTPS to `*.ingest.monitor.azure.com`
3. If using a proxy, configure `Useproxy` and `ProxyUrl` in the Advanced section of the configuration

### Data Not Appearing in Tables

1. Verify the `DCRImmutableId` corresponds to the correct DCR for the target table
2. Check that table schema columns match the stream declaration in the DCR
3. Review collector logs for payload size errors (1 MB limit per API call for Log Ingestion API)
4. Ensure `SentinelLogIngestionAPIActivated` is set to `"true"` in the configuration

### Payload Size Errors

The Log Ingestion API limits each request to 1 MB. The collector automatically segments larger payloads. If segmentation errors persist, reduce the `MaximalSentinelPacketSizeMb` value in the Advanced configuration section.

## Complete Setup Checklist

Use this checklist to track your progress:

- [ ] Generate or obtain a certificate (Step 1)
- [ ] Record the certificate thumbprint
- [ ] Register an Entra ID Application (Step 2)
- [ ] Record the Application (Client) ID
- [ ] Record the Tenant ID
- [ ] Upload the certificate to the Application
- [ ] Deploy DCE, DCR, and tables via ARM template (Step 3)
- [ ] Record the DCE URI from deployment outputs
- [ ] Record the DCR Immutable ID(s) from deployment outputs
- [ ] Assign Monitoring Metrics Publisher role on each DCR (Step 4)
- [ ] Update `CollectExchSecConfiguration.json` with all values (Step 5)
- [ ] Validate authentication and test data ingestion (Step 6)
- [ ] Verify data appears in Log Analytics tables

## Cleanup

To remove all deployed resources:

```powershell
# Remove role assignments first (repeat per DCR you assigned)
Remove-AzRoleAssignment `
    -ObjectId "SERVICE_PRINCIPAL_OBJECT_ID" `
    -RoleDefinitionName "Monitoring Metrics Publisher" `
    -Scope "/subscriptions/YOUR_SUB_ID/resourceGroups/rg-sentinel-esi/providers/Microsoft.Insights/dataCollectionRules/DCR-ESI-OnlineConfig"

# Delete DCRs
Remove-AzDataCollectionRule -Name "DCR-ESI-OnPremisesConfig" -ResourceGroupName "rg-sentinel-esi"
Remove-AzDataCollectionRule -Name "DCR-ESI-OnlineConfig"     -ResourceGroupName "rg-sentinel-esi"
Remove-AzDataCollectionRule -Name "DCR-ESI-MessageTracking"  -ResourceGroupName "rg-sentinel-esi"

# Delete DCE
Remove-AzDataCollectionEndpoint -Name "DCE-ESI-LogIngestion" -ResourceGroupName "rg-sentinel-esi"

# Delete the Entra ID Application (optional)
Remove-MgApplication -ApplicationId "APP_OBJECT_ID"
```

> [!CAUTION]
> Custom Log Analytics tables cannot be deleted via API. They can only be removed through the Log Analytics workspace in the Azure Portal. Removing the workspace deletes all tables and data.
