# Netskope

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Netskope |
| **Support Tier** | Partner |
| **Support Link** | [https://www.netskope.com/services#support](https://www.netskope.com/services#support) |
| **Categories** | domains |
| **First Published** | 2022-05-05 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskope](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskope) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Netskope](../connectors/netskope.md)

**Publisher:** Netskope

The [Netskope Cloud Security Platform](https://www.netskope.com/platform) connector provides the capability to ingest Netskope logs and events into Microsoft Sentinel. The connector provides visibility into Netskope Platform Events and Alerts in Microsoft Sentinel to improve monitoring and investigation capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `Netskope_CL` |
| **Connector Definition Files** | [Netskope_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskope/Data%20Connectors/Netskope/Netskope_API_FunctionApp.json) |

[→ View full connector details](../connectors/netskope.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Netskope_CL` | [Netskope](../connectors/netskope.md) |

[← Back to Solutions Index](../solutions-index.md)
