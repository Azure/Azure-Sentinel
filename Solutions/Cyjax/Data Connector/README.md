# Cyjax IOC Data Connector for Microsoft Sentinel

This directory contains the Cyjax IOC (Indicators of Compromise) Data Connector for Microsoft Sentinel, which enables ingestion of threat intelligence indicators from the Cyjax API v2 into Microsoft Sentinel.

## Overview

The Cyjax IOC Data Connector provides the capability to:
- Ingest IOCs from Cyjax API v2 into Microsoft Sentinel as STIX 2.1 Threat Intelligence indicators
- Fetch various types of IOCs including IPs, domains, URLs, file hashes, emails, and hostnames
- Enrich IOCs with GeoIP, ASN, and sighting data
- Upload indicators to Microsoft Sentinel via the Upload Indicator API
- Support automated IOC collection with configurable schedules
- Incremental fetching with checkpoint management

## Files in this Directory

### Configuration Files
- `CyjaxIOC_API_FunctionApp.json` - Microsoft Sentinel data connector definition file
- `azuredeploy_Connector_CyjaxIOC_AzureFunction.json` - ARM template for automated deployment

### Source Code
- `CyjaxIOCIngestion/` - Azure Function source code for the connector
- `SharedCode/` - Shared utility code and libraries

### Function App Configuration
- `host.json` - Azure Functions host configuration
- `requirements.txt` - Python dependencies for the Azure Function

## Prerequisites

1. **Azure Subscription** with owner role to register applications and assign roles
2. **Microsoft Sentinel** workspace with appropriate permissions
3. **Cyjax API v2** access token (Bearer Token)
4. **Azure App Registration** with the following:
   - Application (Client) ID
   - Tenant ID
   - Client Secret

## Deployment Options

### Option 1: Automated Deployment via ARM Template

1. Click the "Deploy to Azure" button in the Microsoft Sentinel portal
2. Provide the following parameters:
   - **FunctionName**: Unique Function App name (max 11 characters)
   - **Location**: Region for deployment
   - **WorkspaceID**: Log Analytics Workspace ID
   - **AzureClientID**: Azure Client ID from App Registration
   - **AzureClientSecret**: Azure Client Secret from App Registration
   - **AzureTenantID**: Azure Tenant ID
   - **CyjaxBaseURL**: Cyjax API v2 Base URL (default: https://api.cymon.co/v2)
   - **CyjaxAccessToken**: Cyjax API Bearer Token
   - **LookbackDays**: Days to look back on first run (default: 1)
   - **EnableEnrichment**: Set to `true` to enrich IOCs with GeoIP, ASN, and sighting data. Set to `false` to skip enrichment and reduce API calls and execution time (default: `true`)
   - **IOCQuery**: Optional free-text search query to filter IOCs from the Cyjax API (e.g. a keyword, threat actor, or campaign name). Leave empty to fetch all available IOCs
   - **IndicatorType**: Filter IOCs by type. Enter comma-separated values (e.g., URL,Domain,IPv4). Supported types: URL, Domain, IPv4, IPv6, Hostname, Email, FileHash-SHA1, FileHash-SHA256, FileHash-MD5, FileHash-SSDEEP. Leave empty to fetch all types
   - **Schedule**: Quartz Cron-Expression (default: every 10 minutes)
   - **LogLevel**: Log level (default: Info)
   - **AppInsightsWorkspaceResourceID**: Application Insights Workspace Resource ID (optional)

### Option 2: Manual Deployment via Visual Studio Code

1. Deploy the Function App using VS Code
2. Configure application settings in Azure Portal
3. Required application settings:
   - `WorkspaceID`: Your Log Analytics Workspace ID
   - `AzureClientID`: Azure Client ID from App Registration
   - `AzureClientSecret`: Azure Client Secret from App Registration
   - `AzureTenantID`: Your Azure Tenant ID
   - `CyjaxBaseURL`: Cyjax API v2 Base URL
   - `CyjaxAccessToken`: Your Cyjax API Bearer Token
   - `LookbackDays`: Number of days to look back (default: 1)
   - `ENABLE_ENRICHMENT`: Set to `true` to enrich IOCs with GeoIP, ASN, and sighting data. Set to `false` to skip enrichment (default: `true`)
   - `IOC_QUERY`: Optional free-text search query to filter IOCs (e.g. keyword, threat actor, campaign name). Leave empty for no filter (optional)
   - `Indicator_Type`: Filter IOCs by type. Enter comma-separated values (e.g., URL,Domain,IPv4). Supported types: URL, Domain, IPv4, IPv6, Hostname, Email, FileHash-SHA1, FileHash-SHA256, FileHash-MD5, FileHash-SSDEEP. Leave empty to fetch all types (optional)
   - `Schedule`: Quartz Cron-Expression
   - `LogLevel`: Log level (Info/Debug/Error/Warning)
   - `AppInsightsWorkspaceResourceID`: Application Insights Workspace Resource ID (optional)
   - `logAnalyticsUri`: Log Analytics API endpoint override (optional)

## Configuration Steps

### 1. App Registration in Microsoft Entra ID

1. Sign in to the [Azure portal](https://portal.azure.com/)
2. Navigate to **Microsoft Entra ID** → **App registrations** → **New registration**
3. Enter a display name for your application
4. Select **Register**
5. Note the **Application (client) ID** and **Tenant ID**

### 2. Add Client Secret

1. In your app registration, go to **Certificates & secrets** → **Client secrets**
2. Click **New client secret**
3. Add a description and expiration
4. Select **Add** and copy the secret value immediately

### 3. Assign Microsoft Sentinel Contributor Role

1. Go to your Log Analytics workspace
2. Select **Access control (IAM)** → **Add role assignment**
3. Choose **Microsoft Sentinel Contributor** role
4. Select your app registration as the member
5. Click **Review + assign**

### 4. Obtain Cyjax API Credentials

Contact Cyjax to obtain your API v2 access token (Bearer Token)

## Data Types

The connector ingests data into the following table:
- **ThreatIntelIndicators** - Microsoft Sentinel's built-in threat intelligence table

## Monitoring and Troubleshooting

### Monitoring
- Use Application Insights to monitor function execution
- Check the Azure Function logs for errors and warnings
- Monitor data ingestion in Microsoft Sentinel

### Common Issues
1. **Authentication failures**: Verify Azure App credentials and Cyjax API token
2. **Permission errors**: Ensure Microsoft Sentinel Contributor role is assigned
3. **Data not appearing**: Check function logs and verify schedule configuration

