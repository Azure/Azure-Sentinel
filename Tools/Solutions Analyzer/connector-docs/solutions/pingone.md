# PingOne

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-04-20 |
| **Last Updated** | 2025-04-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingOne](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingOne) |\n\n## Data Connectors

This solution provides **1 data connector(s)**.

### Ping One (via Codeless Connector Framework)

**Publisher:** Microsoft

This connector ingests **audit activity logs** from the PingOne Identity platform into Microsoft Sentinel using a Codeless Connector Framework.

**Tables Ingested:**

- `PingOne_AuditActivitiesV2_CL`

**Connector Definition Files:**

- [PingOneAuditLogs_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingOne/Data%20Connectors/PingOneAuditLogs_ccp/PingOneAuditLogs_DataConnectorDefinition.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `PingOne_AuditActivitiesV2_CL` | Ping One (via Codeless Connector Framework) |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n