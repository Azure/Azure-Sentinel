# VirtualMetric DataStream

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | VirtualMetric |
| **Support Tier** | Partner |
| **Support Link** | [https://support.virtualmetric.com](https://support.virtualmetric.com) |
| **Categories** | domains |
| **Author** | VirtualMetric |
| **First Published** | 2025-09-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirtualMetric%20DataStream](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirtualMetric%20DataStream) |

## Data Connectors

This solution provides **3 data connector(s)**:

- [VirtualMetric Director Proxy](../connectors/virtualmetricdirectorproxy.md)
- [VirtualMetric DataStream for Microsoft Sentinel](../connectors/virtualmetricmssentinelconnector.md)
- [VirtualMetric DataStream for Microsoft Sentinel data lake](../connectors/virtualmetricmssentineldatalakeconnector.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [VirtualMetric DataStream for Microsoft Sentinel](../connectors/virtualmetricmssentinelconnector.md), [VirtualMetric DataStream for Microsoft Sentinel data lake](../connectors/virtualmetricmssentineldatalakeconnector.md), [VirtualMetric Director Proxy](../connectors/virtualmetricdirectorproxy.md) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 19-09-2025                     | Initial Solution Release.                   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
