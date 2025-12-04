# Zscaler Private Access (ZPA)

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-01-31 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Zscaler Private Access](../connectors/zscalerprivateaccess.md)

**Publisher:** Zscaler

The [Zscaler Private Access (ZPA)](https://help.zscaler.com/zpa/what-zscaler-private-access) data connector provides the capability to ingest [Zscaler Private Access events](https://help.zscaler.com/zpa/log-streaming-service) into Microsoft Sentinel. Refer to [Zscaler Private Access documentation](https://help.zscaler.com/zpa) for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `ZPA_CL` |
| **Connector Definition Files** | [Connector_LogAnalytics_agent_Zscaler_ZPA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Private%20Access%20%28ZPA%29/Data%20Connectors/Connector_LogAnalytics_agent_Zscaler_ZPA.json) |

[→ View full connector details](../connectors/zscalerprivateaccess.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ZPA_CL` | [[Deprecated] Zscaler Private Access](../connectors/zscalerprivateaccess.md) |

[← Back to Solutions Index](../solutions-index.md)
