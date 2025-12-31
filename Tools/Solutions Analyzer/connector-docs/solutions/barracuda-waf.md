# Barracuda WAF

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Barracuda |
| **Support Tier** | Partner |
| **Support Link** | [https://www.barracuda.com/support](https://www.barracuda.com/support) |
| **Categories** | domains |
| **First Published** | 2022-05-13 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Barracuda%20WAF](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Barracuda%20WAF) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Barracuda Web Application Firewall via Legacy Agent](../connectors/barracuda.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Barracuda_CL`](../tables/barracuda-cl.md) | [[Deprecated] Barracuda Web Application Firewall via Legacy Agent](../connectors/barracuda.md) | - |
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Barracuda Web Application Firewall via Legacy Agent](../connectors/barracuda.md) | - |
| [`barracuda_CL`](../tables/barracuda-cl.md) | [[Deprecated] Barracuda Web Application Firewall via Legacy Agent](../connectors/barracuda.md) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                             |
|-------------|--------------------------------|------------------------------------------------|
| 3.0.0       | 09-07-2024                     | Deprecating data connectors.                   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
