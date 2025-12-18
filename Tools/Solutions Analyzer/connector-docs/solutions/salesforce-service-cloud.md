# Salesforce Service Cloud

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Salesforce%20Service%20Cloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Salesforce%20Service%20Cloud) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[DEPRECATED] Salesforce Service Cloud](../connectors/salesforceservicecloud.md)

**Publisher:** Salesforce

### [Salesforce Service Cloud (via Codeless Connector Framework)](../connectors/salesforceservicecloudccpdefinition.md)

**Publisher:** Microsoft

The Salesforce Service Cloud data connector provides the capability to ingest information about your Salesforce operational events into Microsoft Sentinel through the REST API. The connector provides ability to review events in your org on an accelerated basis, get [event log files](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/event_log_file_hourly_overview.htm) in hourly increments for recent activity.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **Salesforce Service Cloud API access**: Access to the Salesforce Service Cloud API through a Connected App is required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect to Salesforce Service Cloud API to start collecting event logs in Microsoft Sentinel**

Follow [Create a Connected App in Salesforce for OAuth](https://help.salesforce.com/s/articleView?id=platform.ev_relay_create_connected_app.htm&type=5) and [Configure a Connected App for the OAuth 2.0 Client Credentials Flow](https://help.salesforce.com/s/articleView?id=xcloud.connected_app_client_credentials_setup.htm&type=5) to create a Connected App with access to the Salesforce Service Cloud API. Through those instructions, you should get the Consumer Key and Consumer Secret.
 For Salesforce Domain name, Go to Setup, type My Domain in the Quick Find box, and select My Domain to view your domain details. Make sure to enter the domain name without a trailing slash (e.g., https://your-domain.my.salesforce.com). Fill the form below with that information.
- **Salesforce Domain Name**: Salesforce Domain Name
- **Log Collection Interval** (select)
  - Hourly
  - Daily
- **OAuth Configuration**:
  - Consumer Key
  - Consumer Secret
  - Click 'Connect' to authenticate

| | |
|--------------------------|---|
| **Tables Ingested** | `SalesforceServiceCloudV2_CL` |
| **Connector Definition Files** | [SalesforceServiceCloud_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Salesforce%20Service%20Cloud/Data%20Connectors/SalesforceSentinelConnector_CCP/SalesforceServiceCloud_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/salesforceservicecloudccpdefinition.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SalesforceServiceCloudV2_CL` | [Salesforce Service Cloud (via Codeless Connector Framework)](../connectors/salesforceservicecloudccpdefinition.md), [[DEPRECATED] Salesforce Service Cloud](../connectors/salesforceservicecloud.md) |
| `SalesforceServiceCloud_CL` | [[DEPRECATED] Salesforce Service Cloud](../connectors/salesforceservicecloud.md) |

[← Back to Solutions Index](../solutions-index.md)
