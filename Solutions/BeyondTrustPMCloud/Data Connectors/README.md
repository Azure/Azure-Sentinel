# BeyondTrust Privilege Management Cloud Data Connector for Microsoft Sentinel

This data connector ingests security events and administrative activity from BeyondTrust Privilege Management Cloud into Microsoft Sentinel using REST API polling with Azure Functions.

> **📝 Note About Placeholders**: Throughout this documentation, you'll see placeholders that you need to replace with your actual values:
> - `<YOUR-FUNCTION-APP-NAME>` - Your deployed function app name (e.g., `beyondtrust-pmcloud-abc123xyz`)
> - `<YOUR-RESOURCE-GROUP>` - Your Azure resource group name (e.g., `rg-sentinel-prod`)
> - `<YOUR-WORKSPACE-NAME>` - Your Log Analytics workspace name

## Overview

The BeyondTrust PM Cloud Data Connector retrieves data from two primary API endpoints:

1. **Activity Audits** (`/v3/ActivityAudits/Details`) - Administrative and configuration activities
2. **Client Events** (`/v3/Events/FromStartDate`) - Endpoint security events in ECS format

The connector uses OAuth 2.0 client credentials flow for authentication and implements rate limiting to comply with BeyondTrust API limits (1000 requests per 100 seconds).

## Data Tables

The connector creates two custom tables in your Log Analytics workspace:

- `BeyondTrustPM_ActivityAudits_CL` - Management activities, policy changes, user management
- `BeyondTrustPM_ClientEvents_CL` - Endpoint security events (process execution, authentication, etc.)

## Prerequisites

1. **BeyondTrust PM Cloud tenant** with API access enabled
2. **OAuth Client Credentials** for BeyondTrust PM Cloud Management API
3. **Azure Log Analytics workspace** configured for Microsoft Sentinel (must be in the same resource group as the deployment)
4. **Azure subscription** with permissions to deploy Azure Functions and Data Collection Rules

### 📋 **Information You'll Need Before Deployment**

Before starting deployment, gather these required values:

#### **From Azure:**
1. **Resource Group Name**: The resource group containing your Log Analytics workspace (deployment will create resources here)
2. **Workspace Name**: Your Log Analytics workspace name (not the GUID - just the name)
   - Navigate to: Azure Portal → Log Analytics workspaces → [Your workspace] → Overview
   - Copy the workspace name (e.g., `beyondtrust-pmcloud`)

#### **From BeyondTrust PM Cloud:**
1. **Tenant Name**: Your BeyondTrust PM Cloud tenant name (e.g., if your URL is `https://yourcompany.beyondtrustcloud.com`, use `yourcompany`)
2. **OAuth Client ID**: From Configuration → API Clients
3. **OAuth Client Secret**: From Configuration → API Clients

## Deployment

### Option 1: Azure Portal (Recommended)

1. Click the "Deploy to Azure" button below:

   [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FBeyondTrustPMCloud%2Fazuredeploy_BeyondTrustPMCloud.json)

2. Fill in the required parameters:
   - **WorkspaceName**: Your Azure Log Analytics workspace name (e.g., `beyondtrust-pmcloud`)
   - **BeyondTrustTenantName**: Your BeyondTrust PM Cloud tenant name (e.g., `yourcompany`)
   - **BeyondTrustClientId**: OAuth Client ID from BeyondTrust PM Cloud
   - **BeyondTrustClientSecret**: OAuth Client Secret from BeyondTrust PM Cloud
   - **ActivityAuditsPollingIntervalMinutes**: Polling interval for Activity Audits (default: 15)
   - **ClientEventsPollingIntervalMinutes**: Polling interval for Client Events (default: 5)
   - **HistoricalDataTimeframe**: How far back to retrieve events on first run (default: 1d)
     - Format: number followed by 'd' (days), 'h' (hours), or 'm' (minutes)
     - Examples: '7d' (7 days), '12h' (12 hours), '30m' (30 minutes)
     - Use '0' to start from current time (no historical data)

3. Click "Review + create" and then "Create"

> **Note:** The deployment automatically creates the custom tables (`BeyondTrustPM_ActivityAudits_CL` and `BeyondTrustPM_ClientEvents_CL`) and Data Collection Rules (DCRs) for log ingestion. No pre-deployment scripts are required.

### Option 2: Azure CLI

```bash
# Create resource group
az group create --name "rg-beyondtrust-pmcloud" --location "East US"

# Deploy the template
az deployment group create `
  --resource-group "rg-beyondtrust-pmcloud" `
  --template-file "azuredeploy_BeyondTrustPMCloud_API_FunctionApp.json" `
  --parameters `
    WorkspaceName="your-workspace-name" `
    BeyondTrustTenantName="yourcompany" `
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

The Activity Audits table captures administrative and configuration changes in BeyondTrust PM Cloud with comprehensive audit details.

**Core Fields:**
| Field | Type | Description |
|-------|------|-------------|
| TimeGenerated | datetime | Log Analytics ingestion timestamp |
| id | int | Unique audit record ID |
| details | string | Description of the activity |
| userId | int | Numeric user ID |
| user | string | User who performed the action |
| entity | string | Type of entity modified |
| entityName | string | Name of the entity |
| auditType | string | Type of audit action |
| created | datetime | When the activity occurred |
| changedBy | string | Source of the change |
| timeTransmitted | datetime | When transmitted to Azure |

**Audit Detail Fields (dynamic type for complex nested data):**
- `apiClientDataAuditing`, `computerDataAuditing`, `groupDataAuditing`, `installationKeyDataAuditing`
- `policyDataAuditing`, `policyRevisionDataAuditing`, `settingsDataAuditing`, `userDataAuditing`
- `mapToIdentityProviderGroupAuditing`, `openIdConfigDataAuditing`, `mmcRemoteClientDataAuditing`
- `computerPolicyDataAuditing`, `azureADIntegrationDataAuditing`, `authorizationRequestDataAuditing`
- `reputationSettingsDataAuditing`, `securitySettingsDataAuditing`, `siemIntegration*` (multiple)
- `agentDataAuditing`, `managementRuleDataAuditing`, `autoUpdate*` (multiple)
- `permissionGroupDataAuditing`, `identityProviderGroupDataAuditing`

> **Note:** Total ~40 columns. Dynamic fields contain detailed JSON objects with before/after state for configuration changes.

### BeyondTrustPM_ClientEvents_CL

The Client Events table captures endpoint security events in Elastic Common Schema (ECS) format with comprehensive context.

**Event Fields:**
| Field | Type | Description |
|-------|------|-------------|
| TimeGenerated | datetime | Log Analytics ingestion timestamp |
| eventId | string | Unique event identifier |
| eventCode | string | Event type code |
| eventKind | string | Event kind (event, alert, etc.) |
| eventCategory | string | Event category |
| eventAction | string | Action performed |
| eventOutcome | string | Success/failure outcome |
| eventType | string | Event type classification |
| eventProvider | string | Event source provider |
| eventIngested | datetime | When event was ingested |
| eventReason | string | Reason for the event |

**Host Fields:**
| Field | Type | Description |
|-------|------|-------------|
| hostHostname | string | Source hostname |
| hostName | string | Host name |
| hostId | string | Unique host identifier |
| hostIp | string | Host IP address |
| hostArchitecture | string | System architecture |
| hostDomain | string | Domain name |
| hostOsType | string | OS type (Windows, Linux, etc.) |
| hostOsPlatform | string | OS platform |
| hostOsName | string | OS name |
| hostOsVersion | string | OS version |

**User & Identity Fields:**
| Field | Type | Description |
|-------|------|-------------|
| userId | string | User identifier |
| userName | string | Username |
| userDomain | string | User domain |

**File Fields:**
| Field | Type | Description |
|-------|------|-------------|
| fileName | string | File name |
| filePath | string | Full file path |
| fileHashMd5 | string | MD5 hash |
| fileHashSha1 | string | SHA1 hash |
| fileHashSha256 | string | SHA256 hash |

**Process Fields:**
| Field | Type | Description |
|-------|------|-------------|
| processPid | int | Process ID |
| processExecutable | string | Process executable path |
| processCommandLine | string | Command line arguments |

**EPM-Specific Fields:**
| Field | Type | Description |
|-------|------|-------------|
| epmSchemaVersion | string | EPM schema version |
| epmGroupId | int | EPM group ID |
| epmTenantId | int | EPM tenant ID |
| epmEventAction | string | EPM-specific action |
| epmEventType | string | EPM-specific event type |

**Additional Fields:**
| Field | Type | Description |
|-------|------|-------------|
| ecsVersion | string | ECS version |
| tags | string | Event tags |
| timestamp | datetime | Original event timestamp |
| timeTransmitted | datetime | When transmitted to Azure |

**Complex Data Fields (dynamic type for nested JSON):**
- `hostData`, `userData`, `fileData`, `processData`, `epmConfigurationData`
- `networkData`, `destinationData`, `sourceData`, `relatedData`

> **Note:** Total ~50+ columns. Dynamic fields contain detailed nested objects with full context for security analysis.

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
- **Microsoft Sentinel/Log Analytics**: Contact Microsoft support
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
