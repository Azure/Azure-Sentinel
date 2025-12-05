# Forcepoint NGFW

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2022-05-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20NGFW](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20NGFW) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Forcepoint NGFW via Legacy Agent](../connectors/forcepointngfw.md)

**Publisher:** Forcepoint

### [[Deprecated] Forcepoint NGFW via AMA](../connectors/forcepointngfwama.md)

**Publisher:** Forcepoint

The Forcepoint NGFW (Next Generation Firewall) connector allows you to automatically export user-defined Forcepoint NGFW logs into Microsoft Sentinel in real-time. This enriches visibility into user activities recorded by NGFW, enables further correlation with data from Azure workloads and other feeds, and improves monitoring capability with Workbooks inside Microsoft Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_FORCEPOINT_NGFWAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20NGFW/Data%20Connectors/template_FORCEPOINT_NGFWAMA.json) |

[→ View full connector details](../connectors/forcepointngfwama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Forcepoint NGFW via AMA](../connectors/forcepointngfwama.md), [[Deprecated] Forcepoint NGFW via Legacy Agent](../connectors/forcepointngfw.md) |

[← Back to Solutions Index](../solutions-index.md)
