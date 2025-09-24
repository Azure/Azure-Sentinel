# Netskope Alerts and Events - Multiple Instance Deployment

## Problem Statement

Microsoft Sentinel's Content Hub does not allow multiple instances of the same data connector type to be deployed within a single workspace. This limitation prevents customers from connecting multiple Netskope environments (e.g., PROD and DEV) to the same Microsoft Sentinel workspace using the standard UI deployment method.

### Customer Scenario
- Customer has separate Netskope environments for PROD and DEV with different organization URLs
- Customer wants both environments' data in the same Microsoft Sentinel workspace
- Customer wants to use identical table schemas for easy querying and analysis
- Customer prefers to maintain a single workspace rather than separate workspaces for each environment
- Customer has implemented policy naming conventions with "PROD" and "DEV" prefixes for easy data differentiation

## Solution Overview

This PowerShell script solution deploys a second instance of the Netskope Alerts and Events connector by creating additional data connector pollers with unique names ("Dev" suffix) that point to the DEV Netskope environment while using the same Data Collection Rules and table schemas as the existing PROD deployment.

### Key Benefits
- ✅ **Single Workspace**: Both PROD and DEV data in same workspace
- ✅ **Identical Table Schemas**: Same table structure for easy querying
- ✅ **Policy Name Differentiation**: Customer's PROD/DEV policy prefixes enable clean data separation
- ✅ **Minimal Infrastructure**: Uses existing Data Collection Rules
- ✅ **Quick Deployment**: 5-10 minute execution time
- ✅ **Repeatable Process**: Script can be run multiple times safely

## Architecture

```
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Netskope PROD │    │                      │    │                     │
│                 │────┤   Microsoft Sentinel │    │   Same Log Tables   │
│ company-prod... │    │      Workspace       │    │                     │
└─────────────────┘    │                      │    │  • NetskopeAlerts_CL│
                       │  ┌─────────────────┐ │    │  • NetskopeEvents*  │
┌─────────────────┐    │  │ PROD Connectors │ │    │  • Policy Names:    │
│   Netskope DEV  │    │  │ (Original)      │ │────┤    - PROD-*         │
│                 │────┤  └─────────────────┘ │    │    - DEV-*          │
│ company-dev...  │    │                      │    │                     │
└─────────────────┘    │  ┌─────────────────┐ │    │                     │
                       │  │ DEV Connectors  │ │────┤                     │
                       │  │ (Script Deploy) │ │    │                     │
                       │  └─────────────────┘ │    │                     │
                       └──────────────────────┘    └─────────────────────┘
```

## Prerequisites

### Azure Requirements
- **Azure PowerShell Modules**: `Az.Accounts`, `Az.Resources`, `Az.OperationalInsights`
- **Azure Permissions**: Contributor access to the resource group containing Microsoft Sentinel
- **Existing Setup**: Working Netskope Alerts and Events connector for PROD environment

### Netskope Requirements
- **DEV Environment**: Separate Netskope tenant/organization for DEV
- **DEV API Token**: Valid API token with appropriate permissions for DEV environment
- **Policy Naming**: PROD/DEV prefixes implemented in Netskope policy names

### Information to Gather
Before running the script, collect the following information from your existing PROD setup:

1. **Azure Resource Details**:
   - Resource Group Name
   - Log Analytics Workspace Name

2. **DEV Netskope Details**:
   - DEV Organization URL (e.g., `company-dev.goskope.com`)
   - DEV API Token

3. **Data Collection Rule Details** (from existing PROD setup):
   - Data Collection Endpoint URL
   - Data Collection Rule Immutable ID

#### How to Find DCR Details
1. Go to Azure Portal → Resource Groups → [Your Sentinel RG]
2. Find resources of type "Data collection rule"
3. Open the Netskope-related DCR
4. Copy the **Data Collection Endpoint** and **Immutable ID**

## Files Included

### 1. Deploy-NetskopeDevInstance.ps1
Main PowerShell deployment script that creates 21 data connector pollers for the DEV environment.

### 2. parameters.json
Configuration file containing environment-specific values. Customize this file with your actual values.

### 3. VerificationQueries.kql
Sample KQL queries to verify the deployment and test data separation using policy name prefixes.

### 4. README.md
This documentation file.

## Usage Instructions

### Method 1: Using Parameter File (Recommended)

1. **Customize parameters.json**:
   ```json
   {
     "ResourceGroupName": "your-sentinel-resource-group",
     "WorkspaceName": "your-log-analytics-workspace",
     "DevOrgUrl": "company-dev.goskope.com",
     "DevApiKey": "your-dev-api-token",
     "DevIndex": "DevInstance",
     "DataCollectionEndpoint": "https://dce-xxx.eastus-1.ingest.monitor.azure.com",
     "DataCollectionRuleId": "dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   }
   ```

2. **Run the deployment**:
   ```powershell
   # Connect to Azure
   Connect-AzAccount
   
   # Run the deployment script
   .\Deploy-NetskopeDevInstance.ps1 -ParameterFile ".\parameters.json"
   ```

### Method 2: Using Command Line Parameters

```powershell
.\Deploy-NetskopeDevInstance.ps1 `
  -ResourceGroupName "rg-sentinel-prod" `
  -WorkspaceName "law-sentinel-prod" `
  -DevOrgUrl "company-dev.goskope.com" `
  -DevApiKey (ConvertTo-SecureString "your-dev-api-key" -AsPlainText -Force) `
  -DataCollectionEndpoint "https://dce-xxx.eastus-1.ingest.monitor.azure.com" `
  -DataCollectionRuleId "dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## Verification Steps

### 1. Check Data Connectors
1. Go to Microsoft Sentinel → **Data Connectors**
2. Search for "Netskope"
3. You should see multiple connector instances (both PROD and DEV pollers)
4. Verify all show as "Connected"

### 2. Verify Data Flow
Run the verification queries from `VerificationQueries.kql`:

```kusto
// Check data from both environments
union 
NetskopeAlerts_CL,
NetskopeEventsApplication_CL
| extend Environment = case(
    PolicyName startswith "DEV", "DEV",
    PolicyName startswith "PROD", "PROD",
    "Unknown"
)
| where TimeGenerated > ago(1h)
| summarize Count = count(), LatestEvent = max(TimeGenerated) by Environment, TableName = $table
| order by Environment, TableName
```

### 3. Test Data Separation
Verify that policy name prefixes correctly identify environments:

```kusto
NetskopeAlerts_CL
| where TimeGenerated > ago(24h)
| extend Environment = case(
    PolicyName startswith "DEV", "DEV",
    PolicyName startswith "PROD", "PROD",
    "Mixed/Unknown"
)
| summarize AlertCount = count() by Environment, AlertType
| order by Environment, AlertType
```

## Troubleshooting

### Common Issues

#### 1. Authentication Errors
**Error**: "Unable to authenticate to Azure"
**Solution**: Ensure you're logged in with `Connect-AzAccount` and have appropriate permissions.

#### 2. Resource Not Found
**Error**: "Workspace not found"
**Solution**: Verify resource group name and workspace name are correct.

#### 3. DCR Configuration Issues
**Error**: "Invalid Data Collection Rule"
**Solution**: 
- Verify DCR endpoint and immutable ID are correct
- Ensure DCR exists and is accessible
- Check that DCR is configured for Netskope data types

#### 4. API Key Issues
**Error**: "Authentication failed" for Netskope API
**Solution**:
- Verify DEV API key is valid and has appropriate permissions
- Ensure DEV organization URL is correct (without https://)
- Check API key hasn't expired

### Deployment Failures
If some connectors fail to deploy:
1. Check the error messages in the script output
2. Verify all parameters are correct
3. Re-run the script (it's safe to run multiple times)
4. Check Azure Activity Log for detailed error information

## Data Analysis Examples

### Environment-Specific Queries

```kusto
// DEV environment alerts only
NetskopeAlerts_CL
| where PolicyName startswith "DEV"
| where TimeGenerated > ago(24h)
| summarize count() by AlertType

// PROD environment events only  
NetskopeEventsApplication_CL
| where PolicyName startswith "PROD"
| where TimeGenerated > ago(24h)
| summarize count() by ActivityType

// Cross-environment comparison
union NetskopeAlerts_CL, NetskopeEventsApplication_CL
| extend Environment = case(
    PolicyName startswith "DEV", "DEV",
    PolicyName startswith "PROD", "PROD",
    "Unknown"
)
| where TimeGenerated > ago(7d)
| summarize EventCount = count() by Environment, bin(TimeGenerated, 1d)
| render timechart
```

### Dashboard Integration
The environment tagging enables easy filtering in workbooks:
- Create dropdown parameter for Environment selection
- Filter all visualizations based on policy name prefixes
- Build environment-specific dashboards or combined views

## Security Considerations

- **API Key Storage**: The script handles API keys securely using SecureString
- **Credential Management**: Consider using Azure Key Vault for production deployments
- **Access Control**: Ensure appropriate RBAC permissions for script execution
- **Audit Trail**: All deployments are logged in Azure Activity Log

## Maintenance

### Updating Connectors
- Script can be re-run safely to update configurations
- Individual connectors can be removed through Azure Portal if needed
- Monitor connector health through Sentinel Data Connectors page

### Scaling
- Additional environments can be added by modifying the script
- Consider separate scripts for different environment types (staging, test, etc.)

## Support

For issues with this deployment script:
1. Check the troubleshooting section above
2. Review Azure Activity Log for detailed error information
3. Verify all prerequisites are met
4. Contact Microsoft Support for Sentinel-specific issues

---

**Version**: 1.0  
**Last Updated**: September 2025  
**Compatibility**: Microsoft Sentinel, Netskope Alerts and Events connector (Netskopev2 solution)