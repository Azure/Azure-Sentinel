# Netskope Multiple Instance Deployment Solution

This folder contains scripts and documentation for deploying multiple Netskope data connector instances in the same Microsoft Sentinel workspace.

## Problem Statement

By design, Microsoft Sentinel's Content Hub only allows deploying one instance of the Netskope Alerts and Events data connector per workspace. However, many organizations need to collect data from multiple Netskope environments (e.g., PROD and DEV) in a single Sentinel workspace while maintaining data separation and identical table schemas.

## Solution Overview

This PowerShell-based deployment solution creates a second set of Netskope data pollers with unique names, allowing both PROD and DEV environments to send data to the same Log Analytics tables. Environment separation is achieved through policy name prefixes rather than separate connectors.

### Key Benefits

- ✅ **Same Table Schema**: Both environments write to identical Log Analytics tables
- ✅ **Environment Separation**: Uses policy name prefixes (PROD-/DEV-) for clear identification
- ✅ **Simple Deployment**: Single PowerShell script handles all 21 connector types
- ✅ **Cost Effective**: No duplicate storage or complex data transformation
- ✅ **Analytics Compatibility**: Existing queries work with simple filtering additions

## Files in This Solution

| File | Description |
|------|-------------|
| `Deploy-NetskopeDevInstance.ps1` | Main deployment script that creates DEV data pollers |
| `parameters.json` | Template for deployment parameters |
| `VerificationQueries.kql` | KQL queries to validate deployment and data ingestion |
| `README.md` | This documentation file |

## Prerequisites

Before running the deployment script, ensure you have:

1. **Azure PowerShell Modules**:
   ```powershell
   Install-Module -Name Az.Accounts, Az.Resources, Az.OperationalInsights -Force
   ```

2. **Azure Authentication**:
   ```powershell
   Connect-AzAccount
   ```

3. **Existing Resources**:
   - Log Analytics workspace
   - PROD Netskope connector already deployed via Content Hub
   - Appropriate Azure permissions (Contributor role on resource group)

4. **Netskope Configuration**:
   - Access to both PROD and DEV Netskope tenants
   - Ability to configure data export policies

## Deployment Steps

### Step 1: Prepare Parameters

Edit the `parameters.json` file or prepare the following information:

```json
{
  "subscriptionId": "your-subscription-id",
  "resourceGroupName": "your-resource-group",
  "workspaceName": "your-log-analytics-workspace",
  "location": "eastus"
}
```

### Step 2: Run Deployment Script

Execute the PowerShell script with your parameters:

```powershell
.\Deploy-NetskopeDevInstance.ps1 `
  -SubscriptionId "12345678-1234-1234-1234-123456789012" `
  -ResourceGroupName "rg-sentinel" `
  -WorkspaceName "law-sentinel" `
  -Location "eastus"
```

Optional parameters:
- `-DevPrefix "DEV"` (default)
- `-ProdPrefix "PROD"` (default)

### Step 3: Configure Netskope Tenants

After successful deployment:

1. **PROD Environment**: Configure policies with prefix `PROD-`
   - Example: `PROD-WebPolicy`, `PROD-DLPPolicy`

2. **DEV Environment**: Configure policies with prefix `DEV-`
   - Example: `DEV-WebPolicy`, `DEV-DLPPolicy`

3. **Data Export**: Configure both tenants to send data to their respective endpoints

### Step 4: Verify Deployment

Use the queries in `VerificationQueries.kql` to confirm:
- Data collection rules are created
- Data is flowing from both environments
- Policy name prefixes are working correctly

## Architecture

The solution creates the following resources for each of the 21 Netskope event types:

```
PROD Environment (via Content Hub):
├── DCE: dce-NetskopeAlertsEvents-ApplicationEvents
├── DCR: dcr-NetskopeAlertsEvents-ApplicationEvents
└── Target: NetskopeApplicationEvents_CL

DEV Environment (via this script):
├── DCE: dce-DEV-NetskopeAlertsEvents-ApplicationEvents  
├── DCR: dcr-DEV-NetskopeAlertsEvents-ApplicationEvents
└── Target: NetskopeApplicationEvents_CL (same table!)
```

## Supported Event Types

The script deploys connectors for all 21 Netskope event types:

| Event Type | Target Table |
|------------|--------------|
| Application Events | NetskopeApplicationEvents_CL |
| Audit Events | NetskopeAuditEvents_CL |
| Connection Events | NetskopeConnectionEvents_CL |
| Infrastructure Events | NetskopeInfrastructureEvents_CL |
| Network Events | NetskopeNetworkEvents_CL |
| Pages Events | NetskopePagesEvents_CL |
| Alerts Events | NetskopeAlertsEvents_CL |
| Behavior Analytics | NetskopeBehaviorAnalyticsAlertsEvents_CL |
| Compromised Credentials | NetskopeCompromisedCredentialsAlertsEvents_CL |
| DLP Alerts | NetskopeDLPAlertsEvents_CL |
| Legal Hold | NetskopeLegalHoldAlertsEvents_CL |
| Malsite Alerts | NetskopeMalsiteAlertsEvents_CL |
| Malware Alerts | NetskopeMalwareAlertsEvents_CL |
| Policy Alerts | NetskopePolicyAlertsEvents_CL |
| Quarantine Alerts | NetskopeQuarantineAlertsEvents_CL |
| Remediation Alerts | NetskopeRemediationAlertsEvents_CL |
| Security Assessment | NetskopeSecurityAssessmentAlertsEvents_CL |
| UBA Alerts | NetskopeUBAAlertsEvents_CL |
| Watchlist Alerts | NetskopeWatchlistAlertsEvents_CL |
| WebTx Alerts | NetskopeWebTxAlertsEvents_CL |
| CTEP Alerts | NetskopeCTEPAlertsEvents_CL |

## Data Separation Strategy

Instead of using separate tables or workspaces, this solution uses **policy name prefixes** for environment separation:

### Analytics Rule Example

Update your existing analytics rules to filter by environment:

```kql
// Original query
NetskopeApplicationEvents_CL
| where TimeGenerated > ago(1h)
| where RiskLevel == "High"

// Updated query for PROD only
NetskopeApplicationEvents_CL
| where TimeGenerated > ago(1h)
| where RiskLevel == "High"
| where PolicyName startswith "PROD-"

// Updated query for DEV only  
NetskopeApplicationEvents_CL
| where TimeGenerated > ago(1h)
| where RiskLevel == "High"
| where PolicyName startswith "DEV-"

// Query both environments
NetskopeApplicationEvents_CL
| where TimeGenerated > ago(1h)
| where RiskLevel == "High"
| extend Environment = case(
    PolicyName startswith "PROD-", "Production",
    PolicyName startswith "DEV-", "Development", 
    "Unknown"
)
```

## Troubleshooting

### Common Issues

1. **Permission Errors**
   ```
   Error: Insufficient privileges to complete the operation
   ```
   **Solution**: Ensure you have Contributor role on the resource group

2. **Workspace Not Found**
   ```
   Error: Log Analytics workspace 'workspace-name' not found
   ```
   **Solution**: Verify workspace name and resource group are correct

3. **Resource Already Exists**
   ```
   Error: Resource with name 'dce-DEV-...' already exists
   ```
   **Solution**: Run the script with `-Force` parameter or manually delete existing resources

4. **Module Not Found**
   ```
   Error: The term 'New-AzResource' is not recognized
   ```
   **Solution**: Install required Azure PowerShell modules

### Validation Queries

Check resource creation:
```powershell
# List all DCEs
Get-AzResource -ResourceGroupName $ResourceGroupName -ResourceType "Microsoft.Insights/dataCollectionEndpoints" | Where-Object {$_.Name -like "*DEV*"}

# List all DCRs  
Get-AzResource -ResourceGroupName $ResourceGroupName -ResourceType "Microsoft.Insights/dataCollectionRules" | Where-Object {$_.Name -like "*DEV*"}
```

### Data Flow Verification

Use KQL queries in `VerificationQueries.kql` to verify data is flowing correctly from both environments.

## Cost Considerations

This solution has minimal additional cost impact:

- **Data Collection Endpoints (DCE)**: ~$0.50/month each
- **Data Collection Rules (DCR)**: No additional charge
- **Data Ingestion**: Same cost as single environment (no duplication)
- **Storage**: Same tables, no additional storage cost

**Total Additional Cost**: ~$10-15/month for 21 DCEs

## Support and Maintenance

### Updates

When updating Netskope connector configurations:

1. Update PROD environment via Content Hub as usual
2. Re-run this script if schema changes require DCR updates
3. Test with DEV environment first

### Monitoring

Set up monitoring for both environments:

```kql
// Monitor data ingestion by environment
union NetskopePl*_CL
| where TimeGenerated > ago(1h) 
| extend Environment = case(
    PolicyName startswith "PROD-", "Production",
    PolicyName startswith "DEV-", "Development",
    "Unknown"
)
| summarize EventCount = count() by Environment, bin(TimeGenerated, 5m)
| render timechart
```

## Contributing

This solution is part of the Microsoft Sentinel community repository. To contribute improvements:

1. Test changes in a development environment
2. Update documentation as needed
3. Submit pull requests with clear descriptions

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12-24 | Initial release with support for all 21 Netskope event types |

## License

This solution is provided under the same license as the Microsoft Sentinel community repository.

---

**Questions or Issues?** 
- Review the troubleshooting section above
- Check the verification queries for data flow issues
- Consult Microsoft Sentinel documentation for DCE/DCR concepts