# Microsoft 365

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Microsoft 365 (formerly, Office 365)](../connectors/office365.md)

**Publisher:** Microsoft

The Microsoft 365 (formerly, Office 365) activity log connector provides insight into ongoing user activities. You will get details of operations such as file downloads, access requests sent, changes to group events, set-mailbox and details of the user who performed the actions. By connecting Microsoft 365 logs into Microsoft Sentinel you can use this data to view dashboards, create custom alerts, and improve your investigation process. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2219943&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `OfficeActivity` |
| | `exchange` |
| | `sharePoint` |
| | `teams` |
| **Connector Definition Files** | [Microsoft365.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Data%20Connectors/Microsoft365.JSON) |

[→ View full connector details](../connectors/office365.md)

## Tables Reference

This solution ingests data into **4 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `OfficeActivity` | [Microsoft 365 (formerly, Office 365)](../connectors/office365.md) |
| `exchange` | [Microsoft 365 (formerly, Office 365)](../connectors/office365.md) |
| `sharePoint` | [Microsoft 365 (formerly, Office 365)](../connectors/office365.md) |
| `teams` | [Microsoft 365 (formerly, Office 365)](../connectors/office365.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.5       | 04-02-2025                     | Updated **Analytic Rule** MailItemsAccessedTimeSeries.yaml    |
| 3.0.4       | 27-08-2024                     | Updated **Analytic Rule**  for Same names     |
| 3.0.3       | 12-06-2024                     | Updated **Analytic Rule**  for Bug Fixes ExternalUserAddedRemovedInTeams.yaml      |
| 3.0.2       | 09-05-2024					   | Updated **Analytic Rule** to get expected result and Entity Mapping exchange_auditlogdisabled.yaml	and fixed typo description in **Analytic Rules** ExternalUserAddedRemovedInTeams.yaml	   |
| 3.0.1       | 04-01-2024                     | Updated **Analytic Rules**, **Hunting Queries** and **Workbook** for Bug Fixes |
| 3.0.0       | 08-08-2023                     | Renamed **Data Connector** in the solution to Microsoft 365 (formerly, Office 365) so that the naming aligns in Content Hub and Data Connector gallery.<br/> Updated **Hunting Queries** to have descriptions that meet the 255 characters limit.      |

[← Back to Solutions Index](../solutions-index.md)
