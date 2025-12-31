# OpenVPN

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-08-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OpenVPN](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OpenVPN) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] OpenVPN Server](../connectors/openvpn.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] OpenVPN Server](../connectors/openvpn.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [OpenVpnEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OpenVPN/Parsers/OpenVpnEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 18-12-2024                     | Removed Deprecated **Data Connector**       |
| 3.0.0       | 19-07-2024                     | Deprecated **Data Connector**               |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
