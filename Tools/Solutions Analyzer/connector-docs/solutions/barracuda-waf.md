# Barracuda WAF

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Barracuda |
| **Support Tier** | Partner |
| **Support Link** | [https://www.barracuda.com/support](https://www.barracuda.com/support) |
| **Categories** | domains |
| **First Published** | 2022-05-13 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Barracuda%20WAF](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Barracuda%20WAF) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Barracuda Web Application Firewall via Legacy Agent](../connectors/barracuda.md)

**Publisher:** Barracuda

The Barracuda Web Application Firewall (WAF) connector allows you to easily connect your Barracuda logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization’s network and improves your security operation capabilities.



[For more information >​](https://aka.ms/CEF-Barracuda)

| | |
|--------------------------|---|
| **Tables Ingested** | `Barracuda_CL` |
| | `CommonSecurityLog` |
| | `barracuda_CL` |
| **Connector Definition Files** | [template_Barracuda.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Barracuda%20WAF/Data%20Connectors/template_Barracuda.json) |

[→ View full connector details](../connectors/barracuda.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Barracuda_CL` | [[Deprecated] Barracuda Web Application Firewall via Legacy Agent](../connectors/barracuda.md) |
| `CommonSecurityLog` | [[Deprecated] Barracuda Web Application Firewall via Legacy Agent](../connectors/barracuda.md) |
| `barracuda_CL` | [[Deprecated] Barracuda Web Application Firewall via Legacy Agent](../connectors/barracuda.md) |

[← Back to Solutions Index](../solutions-index.md)
