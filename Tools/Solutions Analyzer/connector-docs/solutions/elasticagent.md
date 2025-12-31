# ElasticAgent

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-11-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ElasticAgent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ElasticAgent) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Elastic Agent](../connectors/elasticagent.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ElasticAgentLogs_CL`](../tables/elasticagentlogs-cl.md) | [Elastic Agent](../connectors/elasticagent.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ElasticAgentEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ElasticAgent/Parsers/ElasticAgentEvent.yaml) | - | - |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
