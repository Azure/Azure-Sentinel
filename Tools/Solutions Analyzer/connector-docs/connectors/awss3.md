# Amazon Web Services S3

| | |
|----------|-------|
| **Connector ID** | `AwsS3` |
| **Publisher** | Amazon |
| **Tables Ingested** | [`AWSCloudTrail`](../tables-index.md#awscloudtrail), [`AWSCloudWatch`](../tables-index.md#awscloudwatch), [`AWSGuardDuty`](../tables-index.md#awsguardduty), [`AWSVPCFlow`](../tables-index.md#awsvpcflow) |
| **Used in Solutions** | [Amazon Web Services](../solutions/amazon-web-services.md) |
| **Connector Definition Files** | [template_AwsS3.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Data%20Connectors/template_AwsS3.json) |

This connector allows you to ingest AWS service logs, collected in AWS S3 buckets, to Microsoft Sentinel. The currently supported data types are: 

* AWS CloudTrail

* VPC Flow Logs

* AWS GuardDuty

* AWSCloudWatch



For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2218883&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[← Back to Connectors Index](../connectors-index.md)
