# RSAIDPlus_AdminLogs_Connector

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | RSA Support Team |
| **Support Tier** | Partner |
| **Support Link** | [https://community.rsa.com/](https://community.rsa.com/) |
| **Categories** | domains,verticals |
| **First Published** | 2025-10-14 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RSAIDPlus_AdminLogs_Connector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RSAIDPlus_AdminLogs_Connector) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [RSA ID Plus Admin Logs Connector](../connectors/rsaidplus-adminglogs-connector.md)

**Publisher:** RSA

The RSA ID Plus AdminLogs Connector provides the capability to ingest [Cloud Admin Console Audit Events](https://community.rsa.com/s/article/Cloud-Administration-Event-Log-API-5d22ba17) into Microsoft Sentinel using Cloud Admin APIs.

| | |
|--------------------------|---|
| **Tables Ingested** | `RSAIDPlus_AdminLogs_CL` |
| **Connector Definition Files** | [RSAIDPlus_AdminLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RSAIDPlus_AdminLogs_Connector/Data%20Connectors/RSIDPlus_AdminLogs_Connector_CCP/RSAIDPlus_AdminLogs_ConnectorDefinition.json) |

[→ View full connector details](../connectors/rsaidplus-adminglogs-connector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `RSAIDPlus_AdminLogs_CL` | [RSA ID Plus Admin Logs Connector](../connectors/rsaidplus-adminglogs-connector.md) |

[← Back to Solutions Index](../solutions-index.md)
