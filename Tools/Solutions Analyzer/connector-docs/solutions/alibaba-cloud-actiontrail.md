# Alibaba Cloud ActionTrail

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-07-03 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alibaba%20Cloud%20ActionTrail](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alibaba%20Cloud%20ActionTrail) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Alibaba Cloud ActionTrail (via Codeless Connector Framework)](../connectors/alicloudactiontrailccpdefinition.md)

**Publisher:** Microsoft

The [Alibaba Cloud ActionTrail](https://www.alibabacloud.com/product/actiontrail) data connector provides the capability to retrieve actiontrail events stored into [Alibaba Cloud Simple Log Service](https://www.alibabacloud.com/product/log-service) and store them into Microsoft Sentinel through the [SLS REST API](https://www.alibabacloud.com/help/sls/developer-reference/api-sls-2020-12-30-getlogs). The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

| | |
|--------------------------|---|
| **Tables Ingested** | `AliCloudActionTrailLogs_CL` |
| **Connector Definition Files** | [AliCloudActionTrail_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alibaba%20Cloud%20ActionTrail/Data%20Connectors/AliCloudCloudTrailConnector_CCP/AliCloudActionTrail_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/alicloudactiontrailccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AliCloudActionTrailLogs_CL` | [Alibaba Cloud ActionTrail (via Codeless Connector Framework)](../connectors/alicloudactiontrailccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
