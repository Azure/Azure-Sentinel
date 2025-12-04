# Amazon Web Services

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services) |

## Data Connectors

This solution provides **3 data connector(s)**.

### [Amazon Web Services](../connectors/aws.md)

**Publisher:** Amazon

Follow these instructions to connect to AWS and stream your CloudTrail logs into Microsoft Sentinel. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2218883&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| | |
|--------------------------|---|
| **Tables Ingested** | `AWSCloudTrail` |
| **Connector Definition Files** | [template_AWS.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Data%20Connectors/template_AWS.json) |

[→ View full connector details](../connectors/aws.md)

### [Amazon Web Services S3](../connectors/awss3.md)

**Publisher:** Amazon

This connector allows you to ingest AWS service logs, collected in AWS S3 buckets, to Microsoft Sentinel. The currently supported data types are: 

* AWS CloudTrail

* VPC Flow Logs

* AWS GuardDuty

* AWSCloudWatch



For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2218883&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| | |
|--------------------------|---|
| **Tables Ingested** | `AWSCloudTrail` |
| | `AWSCloudWatch` |
| | `AWSGuardDuty` |
| | `AWSVPCFlow` |
| **Connector Definition Files** | [template_AwsS3.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Data%20Connectors/template_AwsS3.json) |

[→ View full connector details](../connectors/awss3.md)

### [Amazon Web Services S3 WAF](../connectors/awss3wafccpdefinition.md)

**Publisher:** Microsoft

This connector allows you to ingest AWS WAF logs, collected in AWS S3 buckets, to Microsoft Sentinel. AWS WAF logs are detailed records of traffic that web access control lists (ACLs) analyze, which are essential for maintaining the security and performance of web applications. These logs contain information such as the time AWS WAF received the request, the specifics of the request, and the action taken by the rule that the request matched.

| | |
|--------------------------|---|
| **Tables Ingested** | `AWSWAF` |
| **Connector Definition Files** | [AwsS3_WAF_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services/Data%20Connectors/AWS_WAF_CCP/AwsS3_WAF_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/awss3wafccpdefinition.md)

## Tables Reference

This solution ingests data into **5 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AWSCloudTrail` | Amazon Web Services, Amazon Web Services S3 |
| `AWSCloudWatch` | Amazon Web Services S3 |
| `AWSGuardDuty` | Amazon Web Services S3 |
| `AWSVPCFlow` | Amazon Web Services S3 |
| `AWSWAF` | Amazon Web Services S3 WAF |

[← Back to Solutions Index](../solutions-index.md)
