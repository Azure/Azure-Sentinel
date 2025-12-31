# OSSEC

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-19 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OSSEC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OSSEC) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] OSSEC via Legacy Agent](../connectors/ossec.md)
- [[Deprecated] OSSEC via AMA](../connectors/ossecama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] OSSEC via AMA](../connectors/ossecama.md), [[Deprecated] OSSEC via Legacy Agent](../connectors/ossec.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [OSSECEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OSSEC/Parsers/OSSECEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 21-11-2024                     | Removed Deprecated **Data Connectors**                             |
| 3.0.1 	  | 12-07-2024 					   | Deprecated **Data Connector** 										|
| 3.0.0       | 28-08-2023                     | Addition of new OSSEC AMA **Data Connector**                    	|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
