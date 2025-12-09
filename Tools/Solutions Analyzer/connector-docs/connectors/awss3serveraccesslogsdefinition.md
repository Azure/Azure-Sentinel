# AWS S3 Server Access Logs (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `AwsS3ServerAccessLogsDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AWSS3ServerAccess`](../tables-index.md#awss3serveraccess) |
| **Used in Solutions** | [AWS_AccessLogs](../solutions/aws-accesslogs.md) |
| **Connector Definition Files** | [AWSS3ServerAccessLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_AccessLogs/Data%20Connectors/AwsS3ServerAccessLogsDefinition_CCP/AWSS3ServerAccessLogs_ConnectorDefinition.json) |

This connector allows you to ingest AWS S3 Server Access Logs into Microsoft Sentinel. These logs contain detailed records for requests made to S3 buckets, including the type of request, resource accessed, requester information, and response details. These logs are useful for analyzing access patterns, debugging issues, and ensuring security compliance.

[← Back to Connectors Index](../connectors-index.md)
