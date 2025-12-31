# Zinc Open Source

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-10-03 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zinc%20Open%20Source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zinc%20Open%20Source) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **1 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`DeviceInfo`](../tables/deviceinfo.md) | Analytics |

## Content Items

This solution includes **3 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 3 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [AV detections related to Zinc actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zinc%20Open%20Source/Analytic%20Rules/ZincOctober2022_AVHits_IOC.yaml) | High | Impact | [`DeviceInfo`](../tables/deviceinfo.md) |
| [Zinc Actor IOCs files - October 2022](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zinc%20Open%20Source/Analytic%20Rules/ZincOctober2022_Filename_Commandline_IOC.yaml) | High | Persistence | - |
| [[Deprecated] - Zinc Actor IOCs domains hashes IPs and useragent - October 2022](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zinc%20Open%20Source/Analytic%20Rules/ZincOctober2022_IP_Domain_Hash_IOC.yaml) | High | Persistence | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                            |
|-------------|--------------------------------|-------------------------------------------------------------------------------|
| 3.0.3       | 30-05-2024                     | Added missing AMA **Data Connector** reference in **Analytic rules**  |
| 3.0.2       | 27-02-2024                     | Tagged for dependent solutions for deployment                                 |
| 3.0.1       | 19-12-2023                     | Corrected typo mistake *Microsoft Windows DNS* to *Windows Server DNS*        |
| 3.0.0       | 25-10-2023                     | Changes for rebranding from Microsoft 365 Defender to Microsoft Defender XDR  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
