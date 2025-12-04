# F5 Networks

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | F5 |
| **Support Tier** | Partner |
| **Support Link** | [https://www.f5.com/services/support](https://www.f5.com/services/support) |
| **Categories** | domains |
| **First Published** | 2022-05-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/F5%20Networks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/F5%20Networks) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] F5 Networks via Legacy Agent](../connectors/f5.md)

**Publisher:** F5 Networks

### [[Deprecated] F5 Networks via AMA](../connectors/f5ama.md)

**Publisher:** F5 Networks

The F5 firewall connector allows you to easily connect your F5 logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_F5NetworksAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/F5%20Networks/Data%20Connectors/template_F5NetworksAMA.json) |

[→ View full connector details](../connectors/f5ama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] F5 Networks via AMA](../connectors/f5ama.md), [[Deprecated] F5 Networks via Legacy Agent](../connectors/f5.md) |

[← Back to Solutions Index](../solutions-index.md)
