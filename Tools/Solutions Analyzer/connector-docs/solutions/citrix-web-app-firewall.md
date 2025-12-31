# Citrix Web App Firewall

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Citrix Systems |
| **Support Tier** | Partner |
| **Support Link** | [https://www.citrix.com/support/](https://www.citrix.com/support/) |
| **Categories** | domains |
| **First Published** | 2022-05-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20Web%20App%20Firewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20Web%20App%20Firewall) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Citrix WAF (Web App Firewall) via Legacy Agent](../connectors/citrixwaf.md)
- [[Deprecated] Citrix WAF (Web App Firewall) via AMA](../connectors/citrixwafama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Citrix WAF (Web App Firewall) via AMA](../connectors/citrixwafama.md), [[Deprecated] Citrix WAF (Web App Firewall) via Legacy Agent](../connectors/citrixwaf.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [CitrixWAF](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20Web%20App%20Firewall/Workbooks/CitrixWAF.json) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 29-11-2024                     |    Removed Deprecated **Data Connectors**                          |
| 3.0.1       | 10-07-2024                     |    Deprecating data connectors.                                    |
| 3.0.0       | 08-09-2023                     |	Addition of new Citrix Web App Firewall AMA **Data Connector**  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
