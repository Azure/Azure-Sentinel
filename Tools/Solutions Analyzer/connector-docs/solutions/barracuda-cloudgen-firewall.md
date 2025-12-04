# Barracuda CloudGen Firewall

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2021-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Barracuda%20CloudGen%20Firewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Barracuda%20CloudGen%20Firewall) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Barracuda CloudGen Firewall](../connectors/barracudacloudfirewall.md)

**Publisher:** Barracuda

The Barracuda CloudGen Firewall (CGFW) connector allows you to easily connect your Barracuda CGFW logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [template_BarracudaCloudFirewall.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Barracuda%20CloudGen%20Firewall/Data%20Connectors/template_BarracudaCloudFirewall.json) |

[→ View full connector details](../connectors/barracudacloudfirewall.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Barracuda CloudGen Firewall](../connectors/barracudacloudfirewall.md) |

[← Back to Solutions Index](../solutions-index.md)
