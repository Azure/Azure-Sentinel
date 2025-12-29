# Salesforce Service Cloud

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

The Salesforce Service Cloud data connector provides the capability to ingest information about your Salesforce operational events into Microsoft Sentinel through the REST API. The connector provides ability to review events in your org on an accelerated basis, get [event log files](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/event_log_file_hourly_overview.htm) in hourly increments for recent activity.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SalesforceServiceCloudV2_CL` |
| | `SalesforceServiceCloud_CL` |
| **Connector Definition Files** | [SalesforceServiceCloud_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Salesforce%20Service%20Cloud/Data%20Connectors/SalesforceServiceCloud_API_FunctionApp.json) |

[→ View full connector details](../connectors/salesforceservicecloud.md)

### [Salesforce Service Cloud (via Codeless Connector Framework)](../connectors/salesforceservicecloudccpdefinition.md)

**Publisher:** Microsoft

The Salesforce Service Cloud data connector provides the capability to ingest information about your Salesforce operational events into Microsoft Sentinel through the REST API. The connector provides ability to review events in your org on an accelerated basis, get [event log files](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/event_log_file_hourly_overview.htm) in hourly increments for recent activity.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SalesforceServiceCloudV2_CL` |
| **Connector Definition Files** | [SalesforceServiceCloud_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Salesforce%20Service%20Cloud/Data%20Connectors/SalesforceSentinelConnector_CCP/SalesforceServiceCloud_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/salesforceservicecloudccpdefinition.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SalesforceServiceCloudV2_CL` | [Salesforce Service Cloud (via Codeless Connector Framework)](../connectors/salesforceservicecloudccpdefinition.md), [[DEPRECATED] Salesforce Service Cloud](../connectors/salesforceservicecloud.md) |
| `SalesforceServiceCloud_CL` | [[DEPRECATED] Salesforce Service Cloud](../connectors/salesforceservicecloud.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.9       | 17-11-2025                     | Resolved bug in **CCF Data Connector** related to column names     |
| 3.0.8       | 04-11-2025                     | Resolved bugs in **Analytic rules** related to TimestampDerived field.         |
| 3.0.7       | 02-11-2025                     | Updated CCF Data Connector polling config to v65.0.                |
| 3.0.6       | 17-10-2025                     | Updated KQL transformation logic to map USER_NAME to the UserEmail column instead of USER_EMAIL.|
| 3.0.5       | 20-08-2025                     | Moving Salesforce Service cloud **CCF Data Connector** to GA.		|
| 3.0.4       | 11-07-2025                     | Salesforce **Workbook** updated with new ThreatIntelIndicators.	|
| 3.0.3       | 03-07-2025                     | Added Preview tag to CCF Connector title.<br/>Deprecated Function app Connector.		|
| 3.0.2       | 24-03-2025                     | Updated **Analytic rules** query to use TimeStampDerived column rather than TimeGenerated. |
| 3.0.1       | 06-02-2025                     | Updated timeframes for Salesforce cloud **Analytic rules**.			|
| 3.0.0       | 05-09-2023                     | Manual deployment instructions updated for **Data Connector**.		|

[← Back to Solutions Index](../solutions-index.md)
