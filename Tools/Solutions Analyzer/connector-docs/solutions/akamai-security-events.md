# Akamai Security Events

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-03-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Akamai%20Security%20Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Akamai%20Security%20Events) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Akamai Security Events via Legacy Agent](../connectors/akamaisecurityevents.md)
- [[Deprecated] Akamai Security Events via AMA](../connectors/akamaisecurityeventsama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Akamai Security Events via AMA](../connectors/akamaisecurityeventsama.md), [[Deprecated] Akamai Security Events via Legacy Agent](../connectors/akamaisecurityevents.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [AkamaiSIEMEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Akamai%20Security%20Events/Parsers/AkamaiSIEMEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 12-11-2024                     |    Removed Deprecated **Data Connector**                           |
| 3.0.1       | 08-07-2024                     |    Deprecated **Data Connector**                                   |
| 3.0.0       | 20-09-2023                     |    Addition of new Akamai Security Events AMA **Data Connector**   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
