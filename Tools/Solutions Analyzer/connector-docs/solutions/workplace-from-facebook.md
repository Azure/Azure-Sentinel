# Workplace from Facebook

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Workplace%20from%20Facebook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Workplace%20from%20Facebook) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Workplace from Facebook](../connectors/workplacefacebook.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Workplace_Facebook_CL`](../tables/workplace-facebook-cl.md) | [Workplace from Facebook](../connectors/workplacefacebook.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Workplace_Facebook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Workplace%20from%20Facebook/Parsers/Workplace_Facebook.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 03-05-2024                     | Repackaged for parser issue fix on reinstall |
| 3.0.0       | 18-04-2024                     | Updated **Dataconnector** with step by step guidelines and </br> Added Deploy to Azure Goverment button for Government portal|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
