# BeyondTrust PM Cloud Solution for Microsoft Sentinel

## Solution Overview

The BeyondTrust PM Cloud solution provides comprehensive visibility into privilege management activities and endpoint security events from BeyondTrust Privilege Management Cloud.

**Included Components:**
- **Data Connectors:** 1
- **Workbooks:** 1

### In this article
[Solution Overview](#solution-overview)\
[Connector Attributes](#connector-attributes)\
[Data Tables](#data-tables)\
[Query Samples](#query-samples)\
[Prerequisites](#prerequisites)\
[Installation](#installation)\
[Next Steps](#next-steps)

## Connector Attributes
| Connector attribute           | Description                                   |
| ----------------------------- | --------------------------------------------- |
| Azure function app code       | https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/BeyondTrustPMCloud/Data%20Connectors |
| Log Analytics table(s)        | BeyondTrustPM_ActivityAudits_CL<br/>BeyondTrustPM_ClientEvents_CL |
| Data collection rules support | Yes (Logs Ingestion API with DCRs)            |
| Supported by                  | BeyondTrust                                   |

## Data Tables

The connector automatically creates two custom tables in your Log Analytics workspace during deployment:

- **`BeyondTrustPM_ActivityAudits_CL`** (~40 columns) - Administrative activities, policy changes, user management, configuration audits
- **`BeyondTrustPM_ClientEvents_CL`** (~50+ columns) - Endpoint security events in Elastic Common Schema (ECS) format with comprehensive host, user, file, and process context

The data connector retrieves data from two primary API endpoints:

1. **Activity Audits** (`/v3/ActivityAudits/Details`) - Administrative and configuration activities
2. **Client Events** (`/v3/Events/FromStartDate`) - Endpoint security events in ECS format

The connector uses:
- **Authentication:** OAuth 2.0 client credentials flow
- **Ingestion:** Azure Monitor Logs Ingestion API with Data Collection Rules (DCRs)
- **Rate Limiting:** Compliance with BeyondTrust API limits (1000 requests per 100 seconds)
- **State Management:** Azure Table Storage for incremental data retrieval

## Query Samples

#### All Activity Audits
```kusto
BeyondTrustPM_ActivityAudits_CL
| sort by TimeGenerated desc
```

#### All Client Events
```kusto
BeyondTrustPM_ClientEvents_CL
| sort by TimeGenerated desc
```

## Prerequisites

To integrate with BeyondTrust PM Cloud make sure you have the following:

- **Microsoft.Web/sites permissions:** Read and write permissions to Azure Functions to create a Function App is required. See the [Azure Functions documentation](https://learn.microsoft.com/azure/azure-functions/) for details.
- **BeyondTrust PM Cloud API credentials:** OAuth Client ID and Client Secret with appropriate permissions. Contact BeyondTrust support to obtain API access credentials.
- **Azure Log Analytics workspace** configured for Microsoft Sentinel

## Installation

> **Note:** This connector uses Azure Functions to connect to the BeyondTrust PM Cloud API to pull logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

### Install the Solution

1. Install the BeyondTrust PM Cloud solution from the Microsoft Sentinel Content Hub or Azure Marketplace.
2. After installation, navigate to **Data Connectors** in Microsoft Sentinel.
3. Find and select **BeyondTrust PM Cloud**.
4. Follow the configuration steps in the connector page.

### Deploy the Data Connector

For detailed deployment instructions, see the [Data Connector deployment guide](./Data%20Connectors/README.md).

Quick deployment using ARM template:

1. Click the **Deploy to Azure** button:\
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FBeyondTrustPMCloud%2FData%2520Connectors%2Fazuredeploy_BeyondTrustPMCloud_API_FunctionApp.json)
2. Select the preferred **Subscription**, **Resource Group** (containing your Log Analytics workspace), and **Location**.
3. Enter the required parameters:
   - **Workspace Name**: Your Log Analytics workspace name (must be in the same resource group)
   - **BeyondTrust Tenant Name**: Your BeyondTrust PM Cloud tenant name (e.g., `yourcompany`)
   - **BeyondTrust Client ID**: OAuth Client ID
   - **BeyondTrust Client Secret**: OAuth Client Secret
4. Click **Review + Create**, then **Create**.

> **Note:** The deployment automatically creates the custom tables and Data Collection Rules. No pre-deployment scripts are required. Data ingestion begins within 5-15 minutes after deployment completes.

## Next Steps

For more information:
- Review the [Release Notes](./ReleaseNotes.md)
- Explore the included workbook for data visualization
- Go to the related solution in the Azure Marketplace

---

# Data Connector Technical Documentation

> **📝 Note About Placeholders**: Throughout this documentation, you'll see placeholders that you need to replace with your actual values:
> - `<YOUR-FUNCTION-APP-NAME>` - Your deployed function app name (e.g., `beyondtrust-pmcloud-abc123xyz`)
> - `<YOUR-RESOURCE-GROUP>` - Your Azure resource group name (e.g., `rg-sentinel-prod`)
> - `<YOUR-WORKSPACE-NAME>` - Your Log Analytics workspace name

## Data Tables

The connector creates two custom tables in your Log Analytics workspace:

- `BeyondTrustPM_ActivityAudits_CL` - Management activities, policy changes, user management
- `BeyondTrustPM_ClientEvents_CL` - Endpoint security events (process execution, authentication, etc.)

## Prerequisites

1. **BeyondTrust PM Cloud tenant** with API access enabled
2. **OAuth Client Credentials** for BeyondTrust PM Cloud Management API
3. **Azure Log Analytics workspace** configured for Azure Sentinel
4. **Azure subscription** with permissions to deploy Azure Functions

### 📋 **Information You'll Need Before Deployment**

Before starting deployment, gather these required values:

#### **From Azure Log Analytics Workspace:**
1. **Workspace ID** (GUID format):
   - Navigate to: Azure Portal → Log Analytics workspaces → [Your workspace] → Overview
   - Copy the **Workspace ID** field (e.g., `12345678-1234-1234-1234-123456789012`)

2. **Workspace Key** (Base64 string):
   - Navigate to: Azure Portal → Log Analytics workspaces → [Your workspace] → Settings → Agents
   - Copy the **Primary Key** field (long base64 string)

#### **From BeyondTrust PM Cloud:**
1. **PM Cloud Base URL**: Your tenant URL (e.g., `https://yourcompany.beyondtrustcloud.com`)
2. **OAuth Client ID**: From Configuration → API Clients
3. **OAuth Client Secret**: From Configuration → API Clients

💡 **Pro Tip**: Use the included `Get-WorkspaceInfo.ps1` script to automatically retrieve workspace information:
```powershell
.\Get-WorkspaceInfo.ps1 -WorkspaceName "YourWorkspaceName" -ResourceGroupName "YourResourceGroup"
```

## Deployment

### Option 1: Azure Portal (Recommended)

1. Click the "Deploy to Azure" button below:

   [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FBeyondTrustPMCloud%2Fazuredeploy_BeyondTrustPMCloud.json)

2. Fill in the required parameters:
   - **WorkspaceId**: Your Azure Log Analytics Workspace ID
   - **WorkspaceKey**: Your Azure Log Analytics Workspace Primary Key
   - **BeyondTrustPMCloudBaseUrl**: Your BeyondTrust PM Cloud base URL (e.g., https://yourcompany.beyondtrustcloud.com)
   - **BeyondTrustClientId**: OAuth Client ID from BeyondTrust PM Cloud
   - **BeyondTrustClientSecret**: OAuth Client Secret from BeyondTrust PM Cloud
   - **ActivityAuditsPollingIntervalMinutes**: Polling interval for Activity Audits (default: 15)
   - **ClientEventsPollingIntervalMinutes**: Polling interval for Client Events (default: 5)
   - **HistoricalDataTimeframe**: How far back to retrieve events on first run (default: 1d)
     - Format: number followed by 'd' (days), 'h' (hours), or 'm' (minutes)
     - Examples: '7d' (7 days), '12h' (12 hours), '30m' (30 minutes)
     - Use '0' to start from current time (no historical data)

3. Click "Review + create" and then "Create"

### Option 2: Azure CLI

```bash
# Create resource group
az group create --name "rg-beyondtrust-pmcloud" --location "East US"

# Deploy the template
az deployment group create `
  --resource-group "rg-beyondtrust-pmcloud" `
  --template-file "azuredeploy_BeyondTrustPMCloud.json" `
  --parameters `
    WorkspaceId="your-workspace-id" `
    WorkspaceKey="your-workspace-key" `
    BeyondTrustPMCloudBaseUrl="https://yourcompany.beyondtrustcloud.com" `
    BeyondTrustClientId="your-client-id" `
    BeyondTrustClientSecret="your-client-secret" `
    HistoricalDataTimeframe="1d"
```

## Configuration

### BeyondTrust PM Cloud Setup

1. **Create API Client**:
   - Log into your BeyondTrust PM Cloud management console
   - Navigate to Configuration > API Clients
   - Create a new API client with the required permissions for Activity Audits and Events
   - Note the Client ID and Client Secret

2. **Required API Permissions**:
   - `urn:management:api` scope
   - Access to `/v3/ActivityAudits/Details` endpoint
   - Access to `/v3/Events/FromStartDate` endpoint

### Polling Intervals

**Important**: Consider the API rate limits when setting polling intervals:
- BeyondTrust PM Cloud APIs are limited to **1000 requests per 100 seconds**
- Default intervals are conservative but can be adjusted based on your data volume
- **Activity Audits**: Default 15 minutes (administrative events, lower frequency)
- **Client Events**: Default 5 minutes (security events, higher frequency)

### Customizing Polling Intervals

You can adjust polling intervals in the Azure Function App settings:
- `BeyondTrust:ActivityAuditsPollingIntervalMinutes`
- `BeyondTrust:ClientEventsPollingIntervalMinutes`

### Historical Data Timeframe

When the connector runs for the first time (or when state is reset), it retrieves historical events based on the `HistoricalDataTimeframe` parameter:

- **Default**: `1d` (1 day of historical data)
- **Format**: Number followed by 'd' (days), 'h' (hours), or 'm' (minutes)
- **Examples**:
  - `7d` - Retrieve last 7 days of events
  - `12h` - Retrieve last 12 hours of events
  - `30m` - Retrieve last 30 minutes of events
  - `0` - No historical data (start from current time)

**Note**: After the initial run, the connector tracks state and only retrieves new events since the last successful run.

You can adjust this setting in the Azure Function App settings:
- `BeyondTrust:HistoricalDataTimeframe` (Consumption/Premium plans)
- `BeyondTrust__HistoricalDataTimeframe` (Flex Consumption plan)

### BeyondTrust PM Cloud Base URL

The connector requires your specific BeyondTrust PM Cloud base URL. For example:
- If your PM Cloud portal is accessed at `https://yourcompany.beyondtrustcloud.com`
- Enter: `https://yourcompany.beyondtrustcloud.com`

The connector will automatically:
1. Add `-services` to the subdomain (e.g., `yourcompany-services.beyondtrustcloud.com`)
2. Append the appropriate API paths (`/management-api` and `/oauth/connect/token`)
3. Handle trailing slashes appropriately

**Note**: If your URL already contains `-services`, the connector will not add it again.

## Data Schema

### BeyondTrustPM_ActivityAudits_CL

| Field | Type | Description |
|-------|------|-------------|
| TimeGenerated | datetime | Log Analytics ingestion timestamp |
| Id | int | Unique audit record ID |
| Details | string | Description of the activity |
| User | string | User who performed the action |
| Entity | string | Type of entity modified |
| EntityName | string | Name of the entity |
| AuditType | string | Type of audit action |
| Created | datetime | When the activity occurred |
| ChangedBy | string | Source of the change |

### BeyondTrustPM_ClientEvents_CL

| Field | Type | Description |
|-------|------|-------------|
| TimeGenerated | datetime | Log Analytics ingestion timestamp |
| EventId | string | Unique event identifier |
| EventCode | string | Event type code |
| EventAction | string | Action performed |
| EventOutcome | string | Success/failure outcome |
| HostHostname | string | Source hostname |
| UserName | string | User involved in event |
| FileName | string | File involved (if applicable) |
| FilePath | string | Full file path |
| EventReason | string | Reason for the event |

## Sample Queries

### Activity Audits

```kusto
// Recent administrative activities
BeyondTrustPM_ActivityAudits_CL
| where TimeGenerated >= ago(24h)
| project TimeGenerated, User, AuditType, Entity, EntityName, Details
| order by TimeGenerated desc

// Policy changes
BeyondTrustPM_ActivityAudits_CL
| where AuditType contains "Policy"
| project TimeGenerated, User, AuditType, EntityName, Details
| order by TimeGenerated desc
```

### Client Events

```kusto
// Blocked process executions
BeyondTrustPM_ClientEvents_CL
| where EventAction == "process-start-blocked"
| project TimeGenerated, HostHostname, UserName, FileName, FilePath, EventReason
| order by TimeGenerated desc

// Authentication events
BeyondTrustPM_ClientEvents_CL
| where EventCategory contains "authentication"
| project TimeGenerated, HostHostname, UserName, EventAction, EventOutcome
| order by TimeGenerated desc

// High-risk file executions
BeyondTrustPM_ClientEvents_CL
| where EventAction contains "process-start" and EventOutcome == "success"
| where FileName has_any ("powershell.exe", "cmd.exe", "wscript.exe", "cscript.exe")
| project TimeGenerated, HostHostname, UserName, FileName, FilePath
| order by TimeGenerated desc
```

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](docs/) folder:

### Quick Links
- **[Deployment Guide](docs/DEPLOYMENT-WITH-CONFIGURABLE-PLANS.md)** - Deploy with configurable hosting plans (Consumption, Flex, Premium)
- **[Sentinel Setup Guide](docs/SENTINEL-SETUP-GUIDE.md)** - Post-deployment Sentinel integration
- **[How to Pause Ingestion](docs/HOW-TO-PAUSE-INGESTION.md)** - Stop or pause data collection
- **[How to Remove Deployment](docs/HOW-TO-REMOVE-DEPLOYMENT.md)** - Clean up resources
- **[Where Do Logs Go](docs/WHERE-DO-LOGS-GO.md)** - Understanding Application Insights logging
- **[Sentinel Connector FAQ](docs/SENTINEL-CONNECTOR-FAQ.md)** - Common questions

See the **[Documentation Index](docs/README.md)** for the complete list.

## Monitoring and Troubleshooting

### Function App Monitoring

1. **Application Insights**: The deployment creates an Application Insights instance for monitoring
2. **Function Logs**: View execution logs in the Azure portal under Function App > Functions > Monitor
3. **State Management**: The connector maintains state in Azure Table Storage for incremental data retrieval

For detailed information on viewing and querying logs, see **[Where Do Logs Go](docs/WHERE-DO-LOGS-GO.md)**.

### Common Issues

1. **Authentication Failures**:
   - Verify Client ID and Client Secret are correct
   - Ensure OAuth client has proper permissions in BeyondTrust PM Cloud

2. **Rate Limiting**:
   - If you see rate limit warnings, increase polling intervals
   - Monitor Application Insights for rate limit exceptions

3. **No Data Ingestion**:
   - Check Function App logs for errors
   - Verify Log Analytics Workspace ID and Key
   - Ensure BeyondTrust PM Cloud has data in the specified time range

### Log Levels

Set the log level in Function App settings:
- `Logging:LogLevel:Default` = Information (default)
- Options: Critical, Error, Warning, Information, Debug, Trace

## Security Considerations

1. **Credentials**: All sensitive configuration is stored in Azure Function App settings
2. **HTTPS**: All API communications use HTTPS/TLS
3. **Minimal Permissions**: OAuth client should have only required API permissions
4. **Network Security**: Consider implementing network restrictions if required

## Support

For issues related to:
- **BeyondTrust PM Cloud API**: Contact BeyondTrust support
- **Azure Sentinel/Log Analytics**: Contact Microsoft support
- **Data Connector Issues**: Review logs and documentation

## Cost Considerations

- **Azure Functions**: Consumption plan charges per execution
- **Log Analytics**: Charges based on data ingestion volume
- **Storage**: Minimal cost for state management tables

Estimated monthly costs depend on data volume and polling frequency. Monitor usage through Azure Cost Management.

## Version History

- **v1.0**: Initial release with Activity Audits and Client Events support
- OAuth 2.0 authentication with automatic token refresh
- Rate limiting and state management
- Configurable polling intervals
- Comprehensive error handling and logging
