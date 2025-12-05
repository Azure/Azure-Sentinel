# ElasticAgent

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-11-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ElasticAgent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ElasticAgent) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Elastic Agent](../connectors/elasticagent.md)

**Publisher:** Elastic

The [Elastic Agent](https://www.elastic.co/security) data connector provides the capability to ingest Elastic Agent logs, metrics, and security data into Microsoft Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `ElasticAgentLogs_CL` |
| **Connector Definition Files** | [Connector_ElasticAgent.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ElasticAgent/Data%20Connectors/Connector_ElasticAgent.json) |

[→ View full connector details](../connectors/elasticagent.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ElasticAgentLogs_CL` | [Elastic Agent](../connectors/elasticagent.md) |

[← Back to Solutions Index](../solutions-index.md)
