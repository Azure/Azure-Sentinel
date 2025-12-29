# OneLoginIAM

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-08-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OneLoginIAM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OneLoginIAM) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[DEPRECATED] OneLogin IAM Platform](../connectors/onelogin.md)

**Publisher:** OneLogin

The [OneLogin](https://www.onelogin.com/) data connector provides the capability to ingest common OneLogin IAM Platform events into Microsoft Sentinel through Webhooks. The OneLogin Event Webhook API which is also known as the Event Broadcaster will send batches of events in near real-time to an endpoint that you specify. When a change occurs in the OneLogin, an HTTPS POST request with event information is sent to a callback data connector URL.  Refer to [Webhooks documentation](https://developers.onelogin.com/api-docs/1/events/webhooks) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `OneLoginEventsV2_CL` |
| | `OneLoginUsersV2_CL` |
| | `OneLogin_CL` |
| **Connector Definition Files** | [OneLogin_Webhooks_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OneLoginIAM/Data%20Connectors/OneLogin_Webhooks_FunctionApp.json) |

[→ View full connector details](../connectors/onelogin.md)

### [OneLogin IAM Platform (via Codeless Connector Framework)](../connectors/oneloginiamlogsccpdefinition.md)

**Publisher:** Microsoft

The [OneLogin](https://www.onelogin.com/) data connector provides the capability to ingest common OneLogin IAM Platform events into Microsoft Sentinel through REST API by using OneLogin [Events API](https://developers.onelogin.com/api-docs/1/events/get-events) and OneLogin [Users API](https://developers.onelogin.com/api-docs/1/users/get-users). The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `OneLoginEventsV2_CL` |
| | `OneLoginUsersV2_CL` |
| **Connector Definition Files** | [OneLoginIAMLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OneLoginIAM/Data%20Connectors/OneLoginIAMLogs_ccp/OneLoginIAMLogs_ConnectorDefinition.json) |

[→ View full connector details](../connectors/oneloginiamlogsccpdefinition.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `OneLoginEventsV2_CL` | [OneLogin IAM Platform (via Codeless Connector Framework)](../connectors/oneloginiamlogsccpdefinition.md), [[DEPRECATED] OneLogin IAM Platform](../connectors/onelogin.md) |
| `OneLoginUsersV2_CL` | [OneLogin IAM Platform (via Codeless Connector Framework)](../connectors/oneloginiamlogsccpdefinition.md), [[DEPRECATED] OneLogin IAM Platform](../connectors/onelogin.md) |
| `OneLogin_CL` | [[DEPRECATED] OneLogin IAM Platform](../connectors/onelogin.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.3       | 29-07-2025                     |  Removed Deprecated **Data Connector**. | 
| 3.0.2       | 30-06-2025                     |  OneLoginIAM **CCF Data Connector** moving to GA.  		                |
| 3.0.1       | 10-04-2025                     |  Migrated the **Function app** connector to **CCF Data Connector** and Updated **Parser**.<br/>Added Preview tag to **CCF Data Connector**.   		                |
| 3.0.0       | 25-09-2023                     |  Modified **Parser** for query optimization. 		                |
|             |                                |  Manual deployment instructions updated for **Data Connector**.     |

[← Back to Solutions Index](../solutions-index.md)
