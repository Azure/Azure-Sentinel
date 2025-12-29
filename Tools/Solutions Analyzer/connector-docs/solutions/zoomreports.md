# ZoomReports

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZoomReports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZoomReports) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Zoom Reports](../connectors/zoom.md)

**Publisher:** Zoom

The [Zoom](https://zoom.us/) Reports data connector provides the capability to ingest [Zoom Reports](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#tag/Reports) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://developers.zoom.us/docs/api/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Zoom_CL` |
| **Connector Definition Files** | [ZoomReports_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZoomReports/Data%20Connectors/ZoomReports_API_FunctionApp.json) |

[→ View full connector details](../connectors/zoom.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Zoom_CL` | [Zoom Reports](../connectors/zoom.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.5       | 29-08-2024                     | Updated the python runtime version to 3.11  | 
| 3.0.4       | 26-04-2024                     | Repackaged for fix on parser in maintemplate to have old parsername and parentid                    |
| 3.0.3       | 18-04-2024                     | Repackaged for fix on parser in maintemplate                    |
| 3.0.2       | 10-04-2024                     | Added Azure Deploy button for government portal deployments                    |
| 3.0.1       | 04-12-2023                     | Authentication changes for zoom reports with server to server **Oauth app**     | 
| 3.0.0       | 04-07-2023                     | Fixed broken links for **Data Connector** & Added **Workbook** in Solution content      |

[← Back to Solutions Index](../solutions-index.md)
