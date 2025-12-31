# Cisco UCS

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20UCS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20UCS) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Cisco UCS](../connectors/ciscoucs.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] Cisco UCS](../connectors/ciscoucs.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CiscoUCS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20UCS/Parsers/CiscoUCS.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 24-12-2024                     | Removed Deprecated **Data Connector**                              |
| 3.0.0       | 30-07-2024                     | Update the **Parser** as part of Syslog migration                  |
|             |                                | Deprecating data connectors                                        |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
