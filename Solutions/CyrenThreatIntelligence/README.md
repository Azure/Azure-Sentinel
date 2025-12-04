# Cyren Threat Intelligence Solution for Microsoft Sentinel

## Overview

The **Cyren Threat Intelligence** solution provides real-time IP reputation and malware URL feeds to detect and block malicious infrastructure. This solution deploys CCF (Codeless Connector Framework) data connectors and visualization workbooks to help security teams identify and respond to network-based threats.

## What's Included

### Data Connectors (2)
- **Cyren IP Reputation** - RestApiPoller connector for IP threat intelligence
- **Cyren Malware URLs** - RestApiPoller connector for malicious URL intelligence

### Workbooks (2)
- **Cyren Threat Intelligence** - Overview dashboard with key metrics
- **Cyren Threat Intelligence (Enhanced)** - Advanced analytics and threat hunting views

### Infrastructure
- Data Collection Endpoint (DCE)
- Data Collection Rules (DCRs) for both feeds
- Custom Log Analytics table (`Cyren_Indicators_CL`)
- User-Assigned Managed Identity for secure authentication
- Optional Azure Key Vault integration for JWT token storage

## Prerequisites

Before deploying this solution, ensure you have:

1. **Microsoft Sentinel Workspace**
   - Active Microsoft Sentinel workspace
   - Contributor permissions on the workspace

2. **Cyren API Credentials**
   - JWT Token for IP Reputation feed
   - JWT Token for Malware URLs feed
   - Obtain these from [Cyren Portal](https://www.cyren.com/)

3. **Azure Permissions**
   - Contributor role on the resource group
   - Permission to create managed identities
   - Permission to assign RBAC roles

## Deployment

### Option 1: Azure Portal (Recommended)

1. Navigate to **Microsoft Sentinel** → **Content Hub**
2. Search for **"Cyren Threat Intelligence"**
3. Click **Install**
4. Follow the deployment wizard:
   - **Basics**: Select subscription, resource group, and workspace
   - **Data Connectors**: Enter your Cyren JWT tokens
   - **Security Options**: (Optional) Enable Key Vault for secure token storage
   - **Workbooks**: Choose which workbooks to deploy

5. Click **Review + Create** → **Create**

### Option 2: ARM Template Deployment

```powershell
# Set your parameters
$subscriptionId = "your-subscription-id"
$resourceGroupName = "your-resource-group"
$workspaceName = "your-sentinel-workspace"
$cyrenIPJwtToken = "your-ip-reputation-jwt-token"
$cyrenMalwareJwtToken = "your-malware-urls-jwt-token"

# Deploy the solution
az deployment group create \
  --subscription $subscriptionId \
  --resource-group $resourceGroupName \
  --template-file mainTemplate.json \
  --parameters workspace=$workspaceName \
               cyrenIPJwtToken=$cyrenIPJwtToken \
               cyrenMalwareJwtToken=$cyrenMalwareJwtToken \
               deployConnectors=true \
               deployWorkbooks=true
```

### Option 3: Automated PowerShell Script (DEPLOY-Cyren-CCF-Clean.ps1)

Use this option if you prefer a **one-command deployment** that creates (or reuses) the resource group and workspace, onboards Microsoft Sentinel, and deploys the full Cyren CCF solution while automatically archiving detailed logs.

#### Prerequisites

- **Azure CLI** installed and logged in (`az login`).
- **PowerShell 7+** (recommended).
- A **Cyren configuration file** named `client-config-COMPLETE.json` located **one folder above** `Cyren-CCF-Clean`.
  - Must include:
    - `azure.value.subscriptionId`
    - `azure.value.location`
    - `cyren.value.ipReputation.jwtToken`
    - `cyren.value.malwareUrls.jwtToken`

#### What the script does

- Reads `client-config-COMPLETE.json` to get:
  - Subscription ID and location.
  - Cyren JWT tokens (IP Reputation and Malware URLs).
- Ensures the target **resource group** and **Log Analytics workspace** exist (creates them if needed).
- Onboards the workspace to **Microsoft Sentinel**.
- Deploys `mainTemplate.json` with the workspace and Cyren JWT tokens.
- Creates a timestamped log folder under:
  - `Project/Docs/Validation/Cyren/`
  and stores:
  - `deploy-cyren-ccf-clean.log`
  - `arm-deployment-result.json`.

#### How to run the script

1. Open a PowerShell session and change directory to the `Cyren-CCF-Clean` folder.
2. Ensure you are logged in and the subscription in `client-config-COMPLETE.json` is available:
   ```powershell
   az login
   az account set --subscription "<subscription-id-from-config>"
   ```
3. Run the deployment script with default names:
   ```powershell
   .\DEPLOY-Cyren-CCF-Clean.ps1
   ```
   This will use:
   - Resource group: `Cyren-Production-Test-RG`
   - Workspace: `Cyren-Production-Test-Workspace`

4. (Optional) Override names or location:
   ```powershell
   .\DEPLOY-Cyren-CCF-Clean.ps1 \
     -EnvironmentPrefix "Cyren-Prod" \
     -ResourceGroupName "Cyren-Prod-RG" \
     -WorkspaceName "Cyren-Prod-Workspace" \
     -Location "eastus"
   ```

#### After the script completes

- The console output will show whether the ARM deployment **succeeded** or **failed** and the path to the log folder.
- Review the log files in `Project/Docs/Validation/Cyren/` if you need detailed diagnostics.
- Then follow the **Post-Deployment Configuration** and **Data Ingestion** checks described below.

## Post-Deployment Configuration

### 1. Verify Connector Status

1. Navigate to **Microsoft Sentinel** → **Data connectors**
2. Search for **"Cyren"**
3. Verify both connectors show **"Connected"** status

### 2. Check Data Ingestion

Run this KQL query in your Log Analytics workspace:

```kql
Cyren_Indicators_CL
| summarize Count = count(),
          FirstSeen = min(TimeGenerated),
          LastSeen = max(TimeGenerated)
| extend LastSeenHoursAgo = datetime_diff('hour', now(), LastSeen)
```

**Expected Timeline:**
- First data ingestion: 60-90 minutes after deployment
- Polling interval: Every 60 minutes

### 3. Split by Feed Type

```kql
Cyren_Indicators_CL
| extend Feed = case(
    isnotempty(ip_s) and isempty(url_s), "IP Reputation",
    isnotempty(url_s), "Malware URLs",
    "Unknown"
)
| summarize count() by Feed, bin(TimeGenerated, 1h)
| order by TimeGenerated desc
```

## Data Schema

### Cyren_Indicators_CL Table

| Column | Type | Description |
|--------|------|-------------|
| `TimeGenerated` | datetime | Ingestion timestamp |
| `url_s` | string | Malicious URL (Malware URLs feed) |
| `ip_s` | string | Malicious IP address (IP Reputation feed) |
| `fileHash_s` | string | Associated file hash |
| `domain_s` | string | Associated domain |
| `protocol_s` | string | Network protocol (http, https, etc.) |
| `port_d` | int | Network port |
| `category_s` | string | Threat category |
| `risk_d` | int | Risk score (0-100) |
| `firstSeen_t` | datetime | First observed timestamp |
| `lastSeen_t` | datetime | Last observed timestamp |
| `source_s` | string | Threat intelligence source |
| `relationships_s` | string | Related indicators |
| `detection_methods_s` | string | Detection methods used |
| `action_s` | string | Recommended action |
| `type_s` | string | Indicator type (ip, url, domain) |
| `identifier_s` | string | Unique indicator ID |
| `detection_ts_t` | datetime | Detection timestamp |
| `object_type_s` | string | Object type (ipv4, url, etc.) |

## Sample Queries

### High-Risk Indicators (Last 7 Days)

```kql
Cyren_Indicators_CL
| where TimeGenerated >= ago(7d)
| where risk_d >= 70
| project TimeGenerated, type_s, identifier_s, risk_d, category_s, source_s
| order by risk_d desc, TimeGenerated desc
```

### IP Reputation Trends

```kql
Cyren_Indicators_CL
| where isnotempty(ip_s)
| summarize count() by category_s, bin(TimeGenerated, 1h)
| render timechart
```

### Malware URL Patterns

```kql
Cyren_Indicators_CL
| where isnotempty(url_s)
| extend Domain = extract(@"^(?:https?://)?([^/]+)", 1, url_s)
| summarize URLCount = count() by Domain, category_s
| order by URLCount desc
| take 20
```

### Risk Distribution

```kql
Cyren_Indicators_CL
| extend RiskLevel = case(
    risk_d >= 80, "Critical",
    risk_d >= 60, "High",
    risk_d >= 40, "Medium",
    risk_d >= 20, "Low",
    "Informational"
)
| summarize count() by RiskLevel
| render piechart
```

## Troubleshooting

### No Data After 2 Hours

1. **Check Connector Status:**
   ```powershell
   az rest --method GET \
     --url "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.OperationalInsights/workspaces/{workspace}/providers/Microsoft.SecurityInsights/dataConnectors?api-version=2023-02-01-preview"
   ```

2. **Verify JWT Tokens:**
   - Ensure tokens are not expired
   - Test tokens directly against Cyren API
   - Check Key Vault access if using Key Vault

3. **Check DCR Configuration:**
   ```powershell
   az monitor data-collection rule show \
     --resource-group {rg} \
     --name dcr-cyren-ip-reputation
   ```

4. **Review Diagnostics:**
   ```kql
   AzureDiagnostics
   | where ResourceType == "DATAOLLECTIONRULES"
   | where Resource has "cyren"
   | order by TimeGenerated desc
   ```

### Connector Shows "Disconnected"

1. Verify managed identity has correct RBAC roles
2. Check DCR and DCE exist and are correctly configured
3. Ensure workspace is in a supported region

### Data Ingestion Stopped

1. Check JWT token expiration
2. Verify Cyren API is accessible from Azure
3. Review rate limiting (10 QPS per connector)

## Security Considerations

### JWT Token Storage

**Option 1: Secure Parameters (Default)**
- Tokens passed as `securestring` parameters
- Not stored in ARM template
- Recommended for testing

**Option 2: Azure Key Vault (Recommended for Production)**
- Tokens stored encrypted in Key Vault
- Managed identity retrieves tokens at runtime
- Full audit logging
- Enable during deployment with `enableKeyVault=true`

### Network Security

- Connectors use HTTPS only
- No inbound connections required
- Outbound to `api-feeds.cyren.com` required

### RBAC

The solution creates a User-Assigned Managed Identity with:
- **Sentinel Contributor** on the workspace
- **Contributor** on the resource group

## Support

### Cyren Support
- **Email:** support@cyren.com
- **Website:** https://www.cyren.com/support
- **Documentation:** https://www.cyren.com/docs

### Microsoft Sentinel Support
- **Documentation:** https://learn.microsoft.com/azure/sentinel/
- **Community:** https://techcommunity.microsoft.com/t5/microsoft-sentinel/bd-p/MicrosoftSentinel

## Version History

### Version 1.0.0 (2025-11-16)
- Initial release
- IP Reputation and Malware URLs connectors
- 2 visualization workbooks
- CCF RestApiPoller implementation
- Azure Key Vault integration

## License

This solution is provided by Cyren. Please refer to Cyren's licensing terms.

## Additional Resources

- [Cyren Threat Intelligence Platform](https://www.cyren.com/)
- [Microsoft Sentinel Documentation](https://learn.microsoft.com/azure/sentinel/)
- [CCF Data Connector Reference](https://learn.microsoft.com/azure/sentinel/data-connector-connection-rules-reference)
