# Symantec Endpoint Protection

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-07-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Symantec%20Endpoint%20Protection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Symantec%20Endpoint%20Protection) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Symantec Endpoint Protection](../connectors/symantecendpointprotection.md)

**Publisher:** Broadcom

The [Broadcom Symantec Endpoint Protection (SEP)](https://www.broadcom.com/products/cyber-security/endpoint/end-user/enterprise) connector allows you to easily connect your SEP logs with Microsoft Sentinel. This gives you more insight into your organization's network and improves your security operation capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_Syslog_SymantecEndpointProtection.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Symantec%20Endpoint%20Protection/Data%20Connectors/Connector_Syslog_SymantecEndpointProtection.json) |

[→ View full connector details](../connectors/symantecendpointprotection.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Symantec Endpoint Protection](../connectors/symantecendpointprotection.md) |

[← Back to Solutions Index](../solutions-index.md)
