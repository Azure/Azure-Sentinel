# Netwrix Auditor

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netwrix%20Auditor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netwrix%20Auditor) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Netwrix Auditor via Legacy Agent](../connectors/netwrix.md)
- [[Deprecated] Netwrix Auditor via AMA](../connectors/netwrixama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Netwrix Auditor via AMA](../connectors/netwrixama.md), [[Deprecated] Netwrix Auditor via Legacy Agent](../connectors/netwrix.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [NetwrixAuditor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netwrix%20Auditor/Parsers/NetwrixAuditor.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 22-11-2024                     | Removed Deprecated **Data Connectors**                             |
| 3.0.1 	  | 10-07-2024 					   | Deprecated **Data Connector** 										|
| 3.0.0       | 29-08-2023                     | Addition of new Netwrix Auditor AMA **Data Connector**             |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
