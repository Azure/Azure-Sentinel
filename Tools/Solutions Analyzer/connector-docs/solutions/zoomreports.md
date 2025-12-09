# ZoomReports

## Solution Information

| | |
|------------------------|-------|
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

| | |
|--------------------------|---|
| **Tables Ingested** | `Zoom_CL` |
| **Connector Definition Files** | [ZoomReports_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZoomReports/Data%20Connectors/ZoomReports_API_FunctionApp.json) |

[→ View full connector details](../connectors/zoom.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Zoom_CL` | [Zoom Reports](../connectors/zoom.md) |

[← Back to Solutions Index](../solutions-index.md)
