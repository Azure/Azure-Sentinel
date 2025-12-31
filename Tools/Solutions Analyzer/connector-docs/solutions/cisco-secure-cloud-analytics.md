# Cisco Secure Cloud Analytics

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Cloud%20Analytics](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Cloud%20Analytics) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Cisco Secure Cloud Analytics](../connectors/stealthwatch.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] Cisco Secure Cloud Analytics](../connectors/stealthwatch.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [StealthwatchEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Cloud%20Analytics/Parsers/StealthwatchEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 20-12-2024                     |    Removed Deprecated **Data connector**                           |
| 3.0.1       | 23-07-2024                     |	Deprecating data connectors                                     | 
| 3.0.0       | 13-05-2024                     |	Changes for rebranding from Cisco Stealthwatch to Cisco Secure Cloud Analytics         |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
