# Windows Forwarded Events

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Forwarded%20Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Forwarded%20Events) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Windows Forwarded Events](../connectors/windowsforwardedevents.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Event`](../tables/event.md) | - | Analytics |
| [`WindowsEvent`](../tables/windowsevent.md) | [Windows Forwarded Events](../connectors/windowsforwardedevents.md) | Analytics |

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 4 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Caramel Tsunami Actor IOC - July 2021](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Forwarded%20Events/Analytic%20Rules/CaramelTsunami_IOC_WindowsEvent.yaml) | High | Persistence | [`WindowsEvent`](../tables/windowsevent.md) |
| [Chia_Crypto_Mining IOC - June 2021](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Forwarded%20Events/Analytic%20Rules/ChiaCryptoMining_WindowsEvent.yaml) | Low | Impact | [`WindowsEvent`](../tables/windowsevent.md) |
| [Progress MOVEIt File transfer above threshold](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Forwarded%20Events/Analytic%20Rules/moveit_file_transfer_above_threshold.yaml) | Medium | Exfiltration | [`Event`](../tables/event.md) |
| [Progress MOVEIt File transfer folder count above threshold](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Forwarded%20Events/Analytic%20Rules/moveit_file_transfer_folders_above_threshold.yaml) | Medium | Exfiltration | [`Event`](../tables/event.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 10-04-2024                     | Updated entity mappings of **Analytical Rule**   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
