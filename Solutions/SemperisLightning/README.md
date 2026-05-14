# Semperis Lightning Connector for Microsoft Sentinel

This connector ingests all data sources from Semperis Lightning into Microsoft Sentinel/Log Analytics:
- Tier0 Nodes (Identity Graph)
- Attack Paths 
- Attack Path Links
- Tier0 Attackers (Zone Access Objects)
- Indicator Executions
- IoES Metadata
- IoE Results

## Prerequisites

1. **Azure Subscription** with permissions to create resources
2. **Log Analytics Workspace** (existing)
3. **Semperis Lightning API Key** from your Semperis instance
4. **Azure CLI** (for deployment) or Azure Portal

## Deployment

### Option 1: Azure Portal (Recommended)

1. Click the button below or go to Azure Portal
   ```
   https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSemperisLightning%2FData%2520Connectors%2FSemperisLightningLogs%2Fazuredeploy_Connector_SemperisLightning_AzureFunction.json
   ```

2. Fill in the required parameters:
   - **Log Analytics Workspace Resource ID**: Get from your workspace's JSON View
   - **Semperis API Key**: Your Semperis Lightning API key
   - **Semperis Zone**: Select na (North America) or eu (Europe)
   - **Connector Schedule**: Default is `0 * * * * *` (every 1 hour)

3. Click **Review + Create** then **Create**

### Option 2: Azure CLI

```bash
# Set variables
export RESOURCE_GROUP="myResourceGroup"
export WORKSPACE_ID="/subscriptions/xxx/resourcegroups/xxx/providers/microsoft.operationalinsights/workspaces/xxx"
export API_KEY="your-semperis-api-key"
export LOCATION="eastus"

# Deploy
az deployment group create \
  --name semperis-connector \
  --resource-group $RESOURCE_GROUP \
  --template-file azuredeploy_Connector_SemperisLightning_AzureFunction.json \
  --parameters \
    LogAnalyticsWorkspaceResourceID="$WORKSPACE_ID" \
    SemperisApiKey="$API_KEY" \
    SemperisZone="na" \
   ConnectorSchedule="0 * * * * *"
```

## What Gets Created

The template creates:
- **7 Custom Log Analytics Tables** (all with `_CL` suffix)
- **1 Data Collection Endpoint (DCE)**
- **7 Data Collection Rules (DCRs)**
- **Azure Function App** (Python 3.11, Elastic Premium Plan)
- **Storage Accounts** (for function runtime and state)
- **Key Vault** (for secure API key storage)
- **Application Insights** (for monitoring)
- **User-Assigned Managed Identity** (for authentication)

## Data Ingestion Schedule

By default, the connector ingests data every 1 hour. You can modify the schedule using CRON expressions:

| Expression | Frequency |
|---|---|
| `0 * * * * *` | Every 1 hour (default) |
| `0 */4 * * * *` | Every 4 hours |
| `0 * * * * *` | Every hour |
| `0 0 * * * *` | Daily at midnight UTC |

## Monitoring

1. **Application Insights**: Check function health in Azure Portal
2. **Log Analytics**: Query the custom tables for data
   ```kusto
   LightningTier0Nodes_CL
   | where TimeGenerated > ago(24h)
   | count
   ```

## Field Mappings

### Tier0 Nodes
| API Field | Log Analytics Field |
|---|---|
| `id` | `NodeId` |
| `type` | `NodeType` |
| `IDS` | `IdentitySource` |
| `totalIncomingEdgesOfConcern` | `IncomingEdgesOfConcern` |

### Attack Paths
| API Field | Log Analytics Field |
|---|---|
| `Id` | `PathId` |
| `Target.label` | `TargetLabel` |
| `Source.type` | `SourceType` |
| `RiskScore` | `RiskScore` |

## Troubleshooting

### No data appears in Log Analytics
1. Check Function App logs in Application Insights
2. Verify API key is correct
3. Confirm Semperis zone matches your instance (na/eu)
4. Ensure Log Analytics workspace exists and user has permissions

### Function App shows errors
1. Navigate to Function App > Application Insights > Logs
2. Query for errors: `traces | where severityLevel > 1`
3. Check Key Vault access permissions

### Deployment fails
1. Ensure Log Analytics Workspace Resource ID is in correct format
2. Verify you have required Azure permissions
3. Check regional availability of Premium tier

## Support

For issues with:
- **Semperis Lightning**: Contact Semperis support
- **Azure deployment**: Open an issue on GitHub
- **Log Analytics**: See Microsoft Sentinel documentation

## Security

- API keys are stored in Azure Key Vault
- Function uses User-Assigned Managed Identity
- All communication is encrypted (HTTPS/TLS 1.2+)
- Least privilege RBAC roles assigned

## Costs

Estimated monthly costs (US East):
- Function App (EP1): ~$308/month
- Storage Accounts: ~$1-2/month
- Key Vault: ~$0.33/month
- Log Analytics (ingestion): Varies by data volume
- Application Insights: ~$0.30/month

*Actual costs vary by region and usage*
