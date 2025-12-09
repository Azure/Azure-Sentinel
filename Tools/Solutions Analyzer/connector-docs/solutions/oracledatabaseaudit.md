# OracleDatabaseAudit

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-11-05 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Oracle Database Audit](../connectors/oracledatabaseaudit.md)

**Publisher:** Oracle

The Oracle DB Audit data connector provides the capability to ingest [Oracle Database](https://www.oracle.com/database/technologies/) audit events into Microsoft Sentinel through the syslog. Refer to [documentation](https://docs.oracle.com/en/database/oracle/oracle-database/21/dbseg/introduction-to-auditing.html#GUID-94381464-53A3-421B-8F13-BD171C867405) for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_OracleDatabaseAudit.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OracleDatabaseAudit/Data%20Connectors/Connector_OracleDatabaseAudit.json) |

[→ View full connector details](../connectors/oracledatabaseaudit.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Oracle Database Audit](../connectors/oracledatabaseaudit.md) |

[← Back to Solutions Index](../solutions-index.md)
