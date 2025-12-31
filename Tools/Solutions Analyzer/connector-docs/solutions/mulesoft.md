# Mulesoft

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-07-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mulesoft](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mulesoft) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [MuleSoft Cloudhub](../connectors/mulesoft.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`MuleSoft_Cloudhub_CL`](../tables/mulesoft-cloudhub-cl.md) | [MuleSoft Cloudhub](../connectors/mulesoft.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [MuleSoftCloudhub](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mulesoft/Parsers/MuleSoftCloudhub.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYY)** | **Change History**                              |
|-------------|-------------------------------|-------------------------------------------------| 
| 3.0.2       |	09-09-2024	                  | Updated the python runtime version to 3.11         |
| 3.0.1       | 13-06-2024                    | Updated **Data Connector** instructions to notify Cloudhub Application support.     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
