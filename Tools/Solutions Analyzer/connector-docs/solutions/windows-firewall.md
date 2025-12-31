# Windows Firewall

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Firewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Firewall) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Windows Firewall](../connectors/windowsfirewall.md)
- [Windows Firewall Events via AMA](../connectors/windowsfirewallama.md)

## Tables Reference

This solution uses **5 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ASimNetworkSessionLogs`](../tables/asimnetworksessionlogs.md) | [Windows Firewall Events via AMA](../connectors/windowsfirewallama.md) | - |
| [`Heartbeat`](../tables/heartbeat.md) | - | Workbooks |
| [`SecurityEvent`](../tables/securityevent.md) | - | Workbooks |
| [`SigninLogs`](../tables/signinlogs.md) | - | Workbooks |
| [`WindowsFirewall`](../tables/windowsfirewall.md) | [Windows Firewall](../connectors/windowsfirewall.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [WindowsFirewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Firewall/Workbooks/WindowsFirewall.json) | [`Heartbeat`](../tables/heartbeat.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SigninLogs`](../tables/signinlogs.md)<br>[`WindowsFirewall`](../tables/windowsfirewall.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                 |
|-------------|--------------------------------|--------------------------------------------------- |
| 3.0.3       | 16-07-2025                     | Changed **Data Connector** template_WindowsFirewallAma.json to GA  |
| 3.0.2       | 07-06-2024                     | Changed **Data Connector** description template_WindowsFirewallAma.json  |
| 3.0.1       | 27-10-2023                     | New **Data Connector** added WindowsFirewallAma    |
| 3.0.0       | 19-07-2023                     | Initial Solution Release                           |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
