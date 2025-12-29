# Common Event Format

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-30 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Common%20Event%20Format](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Common%20Event%20Format) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Common Event Format (CEF)](../connectors/cef.md)

**Publisher:** Any

Common Event Format (CEF) is an industry standard format on top of Syslog messages, used by many security vendors to allow event interoperability among different platforms. By connecting your CEF logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2223902&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [CEF.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Common%20Event%20Format/Data%20Connectors/CEF.JSON) |

[→ View full connector details](../connectors/cef.md)

### [Common Event Format (CEF) via AMA](../connectors/cefama.md)

**Publisher:** Microsoft

Common Event Format (CEF) is an industry standard format on top of Syslog messages, used by many security vendors to allow event interoperability among different platforms. By connecting your CEF logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2223547&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [CEF%20AMA.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Common%20Event%20Format/Data%20Connectors/CEF%20AMA.JSON) |

[→ View full connector details](../connectors/cefama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [Common Event Format (CEF)](../connectors/cef.md), [Common Event Format (CEF) via AMA](../connectors/cefama.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                           |
|-------------|--------------------------------|------------------------------------------------------------------------------|
| 3.0.6       | 20-08-2025                     | The main template solution has been updated by changing arrays to fields for datatypes, graphqueries and samplequeries. |
| 3.0.5       | 08-07-2025                     | Modifying the availability status.|
| 3.0.4       | 24-06-2025                     | Updated Connector kind of Legacy CEF **Data Connector** so that the queries will be reflected.|
| 3.0.3       | 18-06-2025                     | Updated Connectivity Criteria for Legacy CEF **Data Connector** to add Device Vendors|
| 3.0.2       | 30-04-2025                     | Updated Connectivity Criteria for CEFAMA **Data Connector**                  |
| 3.0.1       | 04-07-2024                     | CEFOverview workbook added                                                   |
| 3.0.0       | 22-05-2024                     | Updated connectivity criteria for **Data Connector**   					  |

[← Back to Solutions Index](../solutions-index.md)
