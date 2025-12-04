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
