# Amazon Web Services S3 WAF

| | |
|----------|-------|
| **Connector ID** | `AwsS3WafCcpDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AWSWAF`](../tables-index.md#awswaf) |
| **Used in Solutions** | [Amazon Web Services](../solutions/amazon-web-services.md) |
| **Connector Definition Files** | [AwsS3_WAF_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Data%20Connectors/AWS_WAF_CCP/AwsS3_WAF_DataConnectorDefinition.json) |

This connector allows you to ingest AWS WAF logs, collected in AWS S3 buckets, to Microsoft Sentinel. AWS WAF logs are detailed records of traffic that web access control lists (ACLs) analyze, which are essential for maintaining the security and performance of web applications. These logs contain information such as the time AWS WAF received the request, the specifics of the request, and the action taken by the rule that the request matched.

[← Back to Connectors Index](../connectors-index.md)
