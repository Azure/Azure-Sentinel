# Box

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Box](../connectors/boxdataconnector.md)

**Publisher:** Box

The Box data connector provides the capability to ingest [Box enterprise's events](https://developer.box.com/guides/events/#admin-events) into Microsoft Sentinel using the Box REST API. Refer to [Box  documentation](https://developer.box.com/guides/events/enterprise-events/for-enterprise/) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `BoxEvents_CL` |
| **Connector Definition Files** | [Box_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Data%20Connectors/Box_API_FunctionApp.json) |

[→ View full connector details](../connectors/boxdataconnector.md)

### [Box Events (CCP)](../connectors/boxeventsccpdefinition.md)

**Publisher:** Microsoft

The Box data connector provides the capability to ingest [Box enterprise's events](https://developer.box.com/guides/events/#admin-events) into Microsoft Sentinel using the Box REST API. Refer to [Box  documentation](https://developer.box.com/guides/events/enterprise-events/for-enterprise/) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `BoxEventsV2_CL` |
| | `BoxEvents_CL` |
| **Connector Definition Files** | [BoxEvents_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Box/Data%20Connectors/BoxEvents_ccp/BoxEvents_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/boxeventsccpdefinition.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `BoxEventsV2_CL` | [Box Events (CCP)](../connectors/boxeventsccpdefinition.md) |
| `BoxEvents_CL` | [Box](../connectors/boxdataconnector.md), [Box Events (CCP)](../connectors/boxeventsccpdefinition.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.1.2       | 29-10-2025                     | Updated KQL queries in Workbook to use EventEndTime instead of TimeGenerated for time-based filtering |
| 3.1.1       | 10-02-2025                     | Advancing CCP **Data Connector** from Public preview to Global Availability.|
| 3.1.0       | 06-12-2024                     | Added new CCP **Data Connector** and modified **Parser**.           |
| 3.0.1       | 18-08-2023                     | Added text 'using Azure Functions' in **Data Connector** page.      |
| 3.0.0       | 19-07-2023                     | Manual deployment instructions updated for **Data Connector**.		|

[← Back to Solutions Index](../solutions-index.md)
