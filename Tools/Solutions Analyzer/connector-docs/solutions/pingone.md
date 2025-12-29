# PingOne

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-04-20 |
| **Last Updated** | 2025-04-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingOne](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingOne) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Ping One (via Codeless Connector Framework)](../connectors/pingoneauditlogsccpdefinition.md)

**Publisher:** Microsoft

This connector ingests **audit activity logs** from the PingOne Identity platform into Microsoft Sentinel using a Codeless Connector Framework.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `PingOne_AuditActivitiesV2_CL` |
| **Connector Definition Files** | [PingOneAuditLogs_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingOne/Data%20Connectors/PingOneAuditLogs_ccp/PingOneAuditLogs_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/pingoneauditlogsccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `PingOne_AuditActivitiesV2_CL` | [Ping One (via Codeless Connector Framework)](../connectors/pingoneauditlogsccpdefinition.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                           |
|-------------|--------------------------------|------------------------------------------------------------------------------| 
| 3.0.2       | 14-08-2025                     | PingOne **CCF Data Connector** moving to GA		                  	      | 
| 3.0.1       | 23-07-2025                     | Update to **CCF Data Connector** Readme File Link                  	      |        
| 3.0.0       | 23-06-2025                     | Initial Solution release with one **CCF Data Connector**                     |

[← Back to Solutions Index](../solutions-index.md)
