# Cisco ACI

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-07-03 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ACI](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ACI) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Cisco Application Centric Infrastructure](../connectors/ciscoaci.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] Cisco Application Centric Infrastructure](../connectors/ciscoaci.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CiscoACIEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ACI/Parsers/CiscoACIEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 24-12-2024                     | Removed Deprecated **Data connector**       |
| 3.0.0       | 23-07-2024                     | Deprecating data connectors                 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
