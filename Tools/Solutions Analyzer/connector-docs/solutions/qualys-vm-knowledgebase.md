# Qualys VM Knowledgebase

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Qualys%20VM%20Knowledgebase](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Qualys%20VM%20Knowledgebase) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Qualys VM KnowledgeBase](../connectors/qualyskb.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`QualysKB_CL`](../tables/qualyskb-cl.md) | [Qualys VM KnowledgeBase](../connectors/qualyskb.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [QualysKB](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Qualys%20VM%20Knowledgebase/Parsers/QualysKB.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 03-05-2024                     | Added Deploy to Azure Goverment button for Government portal in **Dataconnector** <br/> Fixed Metadata issue for ParserName and ParentId mismatch  |
| 3.0.0       | 12-10-2023                     | Manual deployment instructions updated for **Data Connector**		|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
