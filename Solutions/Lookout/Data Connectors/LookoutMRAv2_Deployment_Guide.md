# Lookout Mobile Risk API v2 - Comprehensive ARM Template Deployment Guide

## Overview

This guide provides complete instructions for deploying the Lookout Mobile Risk API v2 comprehensive data connector using the single ARM template that includes all required components:

- **Data Collection Endpoint (DCE)**: Secure ingestion endpoint
- **Data Collection Rule (DCR)**: Field extraction and transformation logic
- **Custom Table**: LookoutMtdV2_CL with 60+ fields
- **Codeless Connector**: SSE-based streaming connector
- **Parser Function**: LookoutEvents KQL function for normalized querying

## Prerequisites

### Required Permissions

- **Microsoft Sentinel Contributor** role on the target workspace
- **Log Analytics Contributor** role for table creation
- **Monitoring Contributor** role for DCE/DCR creation
- **Resource Group Contributor** role for resource deployment

### Required Information

1. **Lookout API Key**: OAuth2 API key from Lookout console
2. **Microsoft Sentinel Workspace**: Target workspace name
3. **Resource Group**: Target resource group for deployment
4. **Azure Subscription**: Subscription with Microsoft Sentinel enabled

## Deployment Methods

### Method 1: Azure Portal Deployment

1. **Download Template**
   ```bash
   wget https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Lookout/Data%20Connectors/LookoutMRAv2_Comprehensive.json
   ```

2. **Navigate to Azure Portal**
   - Go to [Azure Portal](https://portal.azure.com)
   - Search for "Deploy a custom template"
   - Select "Build your own template in the editor"

3. **Upload Template**
   - Click "Load file" and select `LookoutMRAv2_Comprehensive.json`
   - Click "Save"

4. **Configure Parameters**
   - **Subscription**: Select target subscription
   - **Resource Group**: Select or create resource group
   - **Region**: Select deployment region
   - **Workspace**: Enter Microsoft Sentinel workspace name
   - **Lookout Api Key**: Enter your Lookout API key (secure)
   - **Enable Debug Logging**: Set to `true` for initial deployment

5. **Deploy**
   - Review terms and conditions
   - Click "Purchase" to deploy

### Method 2: Azure CLI Deployment

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "your-subscription-id"

# Deploy template
az deployment group create \
  --resource-group "your-resource-group" \
  --template-file "LookoutMRAv2_Comprehensive.json" \
  --parameters \
    workspace="your-sentinel-workspace" \
    lookoutApiKey="your-lookout-api-key" \
    enableDebugLogging=true
```

### Method 3: PowerShell Deployment

```powershell
# Connect to Azure
Connect-AzAccount

# Set subscription context
Set-AzContext -SubscriptionId "your-subscription-id"

# Deploy template
New-AzResourceGroupDeployment `
  -ResourceGroupName "your-resource-group" `
  -TemplateFile "LookoutMRAv2_Comprehensive.json" `
  -workspace "your-sentinel-workspace" `
  -lookoutApiKey "your-lookout-api-key" `
  -enableDebugLogging $true
```

## Template Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `workspace` | string | Yes | - | Microsoft Sentinel workspace name |
| `location` | string | No | Resource Group location | Azure region for deployment |
| `lookoutApiKey` | securestring | Yes | - | Lookout API OAuth2 key |
| `dataCollectionEndpointName` | string | No | `{workspace}-lookout-dce` | DCE resource name |
| `dataCollectionRuleName` | string | No | `{workspace}-lookout-dcr` | DCR resource name |
| `connectorName` | string | No | `LookoutMRAv2-{uniqueString}` | Connector instance name |
| `enableDebugLogging` | bool | No | `false` | Enable debug logging |

## Post-Deployment Validation

### 1. Verify Resource Creation

Check that all resources were created successfully:

```bash
# List deployed resources
az resource list --resource-group "your-resource-group" --query "[?contains(name, 'lookout')]"
```

Expected resources:
- Data Collection Endpoint: `{workspace}-lookout-dce`
- Data Collection Rule: `{workspace}-lookout-dcr`
- Custom Table: `LookoutMtdV2_CL`
- Data Connector: `LookoutMRAv2-{uniqueString}`
- Parser Function: `LookoutEvents`

### 2. Validate Data Ingestion

Wait 5-10 minutes after deployment, then run these KQL queries:

```kql
// Check if table exists and has data
LookoutMtdV2_CL
| take 10

// Verify event types are being ingested
LookoutMtdV2_CL
| summarize count() by event_type
| order by count_ desc

// Test parser function
LookoutEvents
| take 5
```

### 3. Verify Field Extraction

```kql
// Check field extraction is working
LookoutMtdV2_CL
| where isnotempty(device_guid)
| project TimeGenerated, event_type, device_guid, device_platform, threat_severity
| take 10

// Verify dynamic fields are preserved
LookoutMtdV2_CL
| where isnotempty(device)
| project device, threat, audit, smishing_alert
| take 5
```

## Troubleshooting

### Common Issues

#### 1. No Data Ingestion

**Symptoms**: No data appearing in `LookoutMtdV2_CL` table

**Solutions**:
1. Verify Lookout API key is correct and has proper permissions
2. Check DCR transformation logic in Azure Monitor
3. Enable debug logging and check connector logs
4. Verify network connectivity to Lookout API endpoints

**Diagnostic Queries**:
```kql
// Check for any ingestion errors
_LogOperation
| where Category == "DataCollection"
| where Detail contains "LookoutMtdV2"
| order by TimeGenerated desc
```

#### 2. Field Extraction Issues

**Symptoms**: Data ingested but extracted fields are empty

**Solutions**:
1. Verify DCR transformation KQL syntax
2. Check source data format matches expected schema
3. Review field mapping in DCR configuration

**Diagnostic Queries**:
```kql
// Check raw data structure
LookoutMtdV2_CL
| extend RawDevice = tostring(device)
| project TimeGenerated, event_type, RawDevice
| take 5
```

#### 3. Authentication Failures

**Symptoms**: Connector shows authentication errors

**Solutions**:
1. Regenerate Lookout API key
2. Verify OAuth2 token endpoint accessibility
3. Check API key format and encoding

### Debug Mode

Enable debug logging for detailed troubleshooting:

```json
{
  "enableDebugLogging": true
}
```

This will log detailed request/response information for analysis.

## Security Considerations

### API Key Management

- Store API keys in Azure Key Vault for production deployments
- Rotate API keys regularly (recommended: every 90 days)
- Use managed identities where possible

### Network Security

- Configure network access controls on DCE if required
- Monitor data ingestion patterns for anomalies
- Implement proper RBAC on the workspace

### Data Privacy

- Review data retention policies (default: 90 days)
- Implement data classification and labeling
- Ensure compliance with organizational data policies

## Performance Optimization

### Monitoring

Monitor these key metrics:

```kql
// Ingestion volume
LookoutMtdV2_CL
| summarize count() by bin(TimeGenerated, 1h)
| render timechart

// Event type distribution
LookoutMtdV2_CL
| summarize count() by event_type
| render piechart

// Query performance
LookoutEvents
| summarize count() by EventType
```

### Scaling Considerations

- Default rate limit: 10 QPS (configurable)
- Query window: 3 minutes (configurable)
- Table retention: 90 days (configurable)

## Maintenance

### Regular Tasks

1. **Monthly**: Review ingestion volumes and costs
2. **Quarterly**: Rotate API keys
3. **Annually**: Review and update field mappings

### Updates

To update the connector configuration:

1. Modify template parameters
2. Redeploy using same resource names
3. Validate data continuity

## Support

### Lookout Support

- **Email**: support@lookout.com
- **Documentation**: [Lookout API Documentation](https://docs.lookout.com)
- **Support Portal**: [Lookout Support](https://support.lookout.com)

### Microsoft Support

- **Azure Support**: [Azure Support Portal](https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade)
- **Microsoft Sentinel Documentation**: [Microsoft Sentinel Docs](https://docs.microsoft.com/azure/sentinel/)

## Appendix

### Sample Deployment Script

```bash
#!/bin/bash

# Lookout MRA v2 Deployment Script
RESOURCE_GROUP="rg-sentinel-prod"
WORKSPACE="sentinel-workspace-prod"
LOCATION="East US"
API_KEY="your-lookout-api-key"

echo "Deploying Lookout MRA v2 Comprehensive Connector..."

az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file "LookoutMRAv2_Comprehensive.json" \
  --parameters \
    workspace="$WORKSPACE" \
    location="$LOCATION" \
    lookoutApiKey="$API_KEY" \
    enableDebugLogging=false

echo "Deployment completed. Validating..."

# Wait for deployment to complete
sleep 300

# Validate data ingestion
az monitor log-analytics query \
  --workspace "$WORKSPACE" \
  --analytics-query "LookoutMtdV2_CL | take 5" \
  --output table

echo "Validation completed."
```

### Template Outputs

The template provides these outputs for reference:

- `dataCollectionEndpointId`: DCE resource ID
- `dataCollectionRuleId`: DCR resource ID  
- `dataCollectionRuleImmutableId`: DCR immutable ID for connector configuration
- `tableName`: Custom table name (LookoutMtdV2_CL)
- `connectorName`: Data connector instance name
- `parserFunction`: Parser function name (LookoutEvents)
- `deploymentStatus`: Deployment completion status