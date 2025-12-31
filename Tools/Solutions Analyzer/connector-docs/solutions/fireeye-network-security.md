# FireEye Network Security

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FireEye%20Network%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FireEye%20Network%20Security) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] FireEye Network Security (NX) via Legacy Agent](../connectors/fireeyenx.md)
- [[Deprecated] FireEye Network Security (NX) via AMA](../connectors/fireeyenxama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] FireEye Network Security (NX) via AMA](../connectors/fireeyenxama.md), [[Deprecated] FireEye Network Security (NX) via Legacy Agent](../connectors/fireeyenx.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [FireEyeNXEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FireEye%20Network%20Security/Parsers/FireEyeNXEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 21-11-2024                     | Removed Deprecated **Data Connectors**                             |
| 3.0.1 	  | 10-07-2024 					   | Deprecated **Data Connector** 										|
| 3.0.0       | 01-09-2023                     |	Addition of new FireEye Network Security AMA **Data Connector** |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
