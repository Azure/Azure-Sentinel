# Workday

## Solution Information

| | |
|------------------------|-------|
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

| | |
|--------------------------|---|
| **Tables Ingested** | `ASimAuditEventLogs` |
| **Connector Definition Files** | [Workday_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Workday/Data%20Connectors/Workday_ccp/Workday_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/workdayccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ASimAuditEventLogs` | [Workday User Activity](../connectors/workdayccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
