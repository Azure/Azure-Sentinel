# Ivanti Unified Endpoint Management

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-07-05 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ivanti%20Unified%20Endpoint%20Management](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ivanti%20Unified%20Endpoint%20Management) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Ivanti Unified Endpoint Management](../connectors/ivantiuem.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] Ivanti Unified Endpoint Management](../connectors/ivantiuem.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [IvantiUEMEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ivanti%20Unified%20Endpoint%20Management/Parsers/IvantiUEMEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 27-12-2024                     | Removed Deprecated **Data Connectors**      |
| 3.0.0       | 24-07-2024                     | Deprecated Data Connectors                  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
