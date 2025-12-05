# Amazon Web Services S3 DNS Route53 (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `AWSRoute53ResolverCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AWSRoute53Resolver`](../tables-index.md#awsroute53resolver) |
| **Used in Solutions** | [Amazon Web Services Route 53](../solutions/amazon-web-services-route-53.md) |
| **Connector Definition Files** | [AWSRoute53Resolver_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services%20Route%2053/Data%20Connectors/AWSRoute53Resolver_CCP/AWSRoute53Resolver_DataConnectorDefinition.json) |

This connector enables ingestion of AWS Route 53 DNS logs into Microsoft Sentinel for enhanced visibility and threat detection. It supports DNS Resolver query logs ingested directly from AWS S3 buckets, while Public DNS query logs and Route 53 audit logs can be ingested using Microsoft Sentinel's AWS CloudWatch and CloudTrail connectors. Comprehensive instructions are provided to guide you through the setup of each log type. Leverage this connector to monitor DNS activity, detect potential threats, and improve your security posture in cloud environments.

[← Back to Connectors Index](../connectors-index.md)
