# Workday

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2024-02-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Workday](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Workday) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Workday User Activity](../connectors/workdayccpdefinition.md)

**Publisher:** Microsoft

The [Workday](https://www.workday.com/) User Activity data connector provides the capability to ingest User Activity Logs from [Workday API](https://community.workday.com/sites/default/files/file-hosting/restapi/index.html#privacy/v1/get-/activityLogging) into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `ASimAuditEventLogs` |
| **Connector Definition Files** | [Workday_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Workday/Data%20Connectors/Workday_ccp/Workday_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/workdayccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ASimAuditEventLogs` | [Workday User Activity](../connectors/workdayccpdefinition.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                           |
|-------------|--------------------------------|--------------------------------------------------------------|
| 3.0.2       | 02-04-2025                     | Updated **Data Connector** guidelines.     |
| 3.0.1       | 10-01-2025                     | Transitioned the **CCP Connector** to General Availability (GA).     |
| 3.0.0       | 13-03-2024                     | Initial Solution Release.                                     |

[← Back to Solutions Index](../solutions-index.md)
