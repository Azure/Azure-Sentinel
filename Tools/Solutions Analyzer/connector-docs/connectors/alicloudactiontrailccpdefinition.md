# Alibaba Cloud ActionTrail (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `AliCloudActionTrailCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AliCloudActionTrailLogs_CL`](../tables-index.md#alicloudactiontraillogs_cl) |
| **Used in Solutions** | [Alibaba Cloud ActionTrail](../solutions/alibaba-cloud-actiontrail.md) |
| **Connector Definition Files** | [AliCloudActionTrail_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Alibaba%20Cloud%20ActionTrail/Data%20Connectors/AliCloudCloudTrailConnector_CCP/AliCloudActionTrail_DataConnectorDefinition.json) |

The [Alibaba Cloud ActionTrail](https://www.alibabacloud.com/product/actiontrail) data connector provides the capability to retrieve actiontrail events stored into [Alibaba Cloud Simple Log Service](https://www.alibabacloud.com/product/log-service) and store them into Microsoft Sentinel through the [SLS REST API](https://www.alibabacloud.com/help/sls/developer-reference/api-sls-2020-12-30-getlogs). The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

[← Back to Connectors Index](../connectors-index.md)
