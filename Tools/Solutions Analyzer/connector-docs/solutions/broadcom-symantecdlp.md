# Broadcom SymantecDLP

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Broadcom%20SymantecDLP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Broadcom%20SymantecDLP) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Broadcom Symantec DLP via Legacy Agent](../connectors/broadcomsymantecdlp.md)
- [[Deprecated] Broadcom Symantec DLP via AMA](../connectors/broadcomsymantecdlpama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Broadcom Symantec DLP via AMA](../connectors/broadcomsymantecdlpama.md), [[Deprecated] Broadcom Symantec DLP via Legacy Agent](../connectors/broadcomsymantecdlp.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [SymantecDLP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Broadcom%20SymantecDLP/Parsers/SymantecDLP.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.3       | 27-11-2024                     | Removed Deprecated **Data Connectors**                             |
| 3.0.2       | 08-07-2024                     | Deprecated **Data Connector**   								    |
| 3.0.1       | 01-09-2023                     | Addition of new Broadcom SymantecDLP AMA **Data Connector**        |
| 3.0.0       | 27-07-2023                     | Corrected the links in the solution.                               |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
