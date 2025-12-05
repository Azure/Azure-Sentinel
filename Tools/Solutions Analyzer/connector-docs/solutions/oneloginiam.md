# OneLoginIAM

## Solution Information

| | |
|------------------------|-------|
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

### [OneLogin IAM Platform (via Codeless Connector Framework)](../connectors/oneloginiamlogsccpdefinition.md)

**Publisher:** Microsoft

The [OneLogin](https://www.onelogin.com/) data connector provides the capability to ingest common OneLogin IAM Platform events into Microsoft Sentinel through REST API by using OneLogin [Events API](https://developers.onelogin.com/api-docs/1/events/get-events) and OneLogin [Users API](https://developers.onelogin.com/api-docs/1/users/get-users). The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

| | |
|--------------------------|---|
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

[← Back to Solutions Index](../solutions-index.md)
