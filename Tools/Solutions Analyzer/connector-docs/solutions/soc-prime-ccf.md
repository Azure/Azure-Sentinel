# SOC Prime CCF

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | SOC Prime |
| **Support Tier** | Partner |
| **Support Link** | [https://socprime.com/](https://socprime.com/) |
| **Categories** | domains |
| **First Published** | 2025-09-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Prime%20CCF](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Prime%20CCF) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [SOC Prime Platform Audit Logs Data Connector](../connectors/socprimeauditlogsdataconnector.md)

**Publisher:** Microsoft

The [SOC Prime Audit Logs](https://help.socprime.com/en/articles/6265791-api) data connector allows ingesting logs from the SOC Prime Platform API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform. It uses the SOC Prime Platform API to fetch SOC Prime platform audit logs and it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security data into a custom table, thus resulting in better performance.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SOCPrimeAuditLogs_CL` |
| **Connector Definition Files** | [SOCPrime_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Prime%20CCF/Data%20Connectors/SOCPrime_ccp/SOCPrime_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/socprimeauditlogsdataconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SOCPrimeAuditLogs_CL` | [SOC Prime Platform Audit Logs Data Connector](../connectors/socprimeauditlogsdataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
