# OracleWebLogicServer

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-01-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Oracle WebLogic Server](../connectors/oracleweblogicserver.md)

**Publisher:** Oracle

OracleWebLogicServer data connector provides the capability to ingest [OracleWebLogicServer](https://docs.oracle.com/en/middleware/standalone/weblogic-server/index.html) events into Microsoft Sentinel. Refer to [OracleWebLogicServer documentation](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/index.html) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `OracleWebLogicServer_CL` |
| **Connector Definition Files** | [Connector_OracleWebLogicServer_agent.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleWebLogicServer/Data%20Connectors/Connector_OracleWebLogicServer_agent.json) |

[→ View full connector details](../connectors/oracleweblogicserver.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `OracleWebLogicServer_CL` | [[Deprecated] Oracle WebLogic Server](../connectors/oracleweblogicserver.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                           |
|-------------|--------------------------------|------------------------------------------------------------------------------|
| 3.0.2       | 23-12-2024                     | Removed Deprecated **Data connector**                                        |
| 3.0.1       | 09-08-2024                     | Deprecating data connectors                                                  |
| 3.0.0       | 15-12-2023                     | Updated the **Parser** field TreadId to ThreadId                             |

[← Back to Solutions Index](../solutions-index.md)
