# NozomiNetworks

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-07-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NozomiNetworks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NozomiNetworks) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Nozomi Networks N2OS via Legacy Agent](../connectors/nozominetworksn2os.md)
- [[Deprecated] Nozomi Networks N2OS via AMA](../connectors/nozominetworksn2osama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Nozomi Networks N2OS via AMA](../connectors/nozominetworksn2osama.md), [[Deprecated] Nozomi Networks N2OS via Legacy Agent](../connectors/nozominetworksn2os.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [NozomiNetworksEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NozomiNetworks/Parsers/NozomiNetworksEvents.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.3       | 21-11-2024                     | Removed Deprecated **Data Connectors**                             |
| 3.0.2 	  | 12-07-2024 					   | Deprecated **Data Connector** 										|
| 3.0.1       | 22-12-2023                     | Query issue fixed in AMA **Data Connector**                     	|
| 3.0.0       | 13-09-2023                     | Addition of new NozomiNetworks AMA **Data Connector**           	|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
