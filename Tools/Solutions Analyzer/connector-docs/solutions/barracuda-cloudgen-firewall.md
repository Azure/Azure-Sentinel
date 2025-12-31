# Barracuda CloudGen Firewall

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2021-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Barracuda%20CloudGen%20Firewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Barracuda%20CloudGen%20Firewall) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Barracuda CloudGen Firewall](../connectors/barracudacloudfirewall.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | - | Workbooks |
| [`Syslog`](../tables/syslog.md) | [[Deprecated] Barracuda CloudGen Firewall](../connectors/barracudacloudfirewall.md) | Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |
| Parsers | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Barracuda](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Barracuda%20CloudGen%20Firewall/Workbooks/Barracuda.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`Syslog`](../tables/syslog.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CGFWFirewallActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Barracuda%20CloudGen%20Firewall/Parsers/CGFWFirewallActivity.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.2       | 19-12-2024                     | Removed Deprecated **Data connector**       |
| 3.0.1       | 18-07-2024                     | Deprecating data connectors                 |
| 3.0.0       | 12-10-2023                     | The support information is revised/updated. |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
