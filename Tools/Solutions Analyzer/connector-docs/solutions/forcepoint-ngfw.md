# Forcepoint NGFW

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

The Forcepoint NGFW (Next Generation Firewall) connector allows you to automatically export user-defined Forcepoint NGFW logs into Microsoft Sentinel in real-time. This enriches visibility into user activities recorded by NGFW, enables further correlation with data from Azure workloads and other feeds, and improves monitoring capability with Workbooks inside Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [FORCEPOINT_NGFW.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20NGFW/Data%20Connectors/FORCEPOINT_NGFW.json) |

[→ View full connector details](../connectors/forcepointngfw.md)

### [[Deprecated] Forcepoint NGFW via AMA](../connectors/forcepointngfwama.md)

**Publisher:** Forcepoint

The Forcepoint NGFW (Next Generation Firewall) connector allows you to automatically export user-defined Forcepoint NGFW logs into Microsoft Sentinel in real-time. This enriches visibility into user activities recorded by NGFW, enables further correlation with data from Azure workloads and other feeds, and improves monitoring capability with Workbooks inside Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_FORCEPOINT_NGFWAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20NGFW/Data%20Connectors/template_FORCEPOINT_NGFWAMA.json) |

[→ View full connector details](../connectors/forcepointngfwama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Forcepoint NGFW via AMA](../connectors/forcepointngfwama.md), [[Deprecated] Forcepoint NGFW via Legacy Agent](../connectors/forcepointngfw.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 19-11-2024                     |    Removed Deprecated **Data Connectors**                          |
| 3.0.1       | 15-07-2024                     |	Deprecating data connectors                                     |
| 3.0.0       | 29-08-2023                     |	Addition of new Forcepoint NGFW AMA **Data Connector**          |

[← Back to Solutions Index](../solutions-index.md)
