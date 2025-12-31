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

This solution provides **2 data connector(s)**:

- [Common Event Format (CEF)](../connectors/cef.md)
- [Common Event Format (CEF) via AMA](../connectors/cefama.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`All_DeviceProduct_Table`](../tables/all-deviceproduct-table.md) | - | Workbooks |
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [Common Event Format (CEF)](../connectors/cef.md), [Common Event Format (CEF) via AMA](../connectors/cefama.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [CEFOverviewWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Common%20Event%20Format/Workbooks/CEFOverviewWorkbook.json) | [`All_DeviceProduct_Table`](../tables/all-deviceproduct-table.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md) |

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

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
