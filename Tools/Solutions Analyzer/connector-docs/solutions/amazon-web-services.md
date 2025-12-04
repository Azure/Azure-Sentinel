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

### [Amazon Web Services S3](../connectors/awss3.md)

**Publisher:** Amazon

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
| `AWSCloudTrail` | [Amazon Web Services](../connectors/aws.md), [Amazon Web Services S3](../connectors/awss3.md) |
| `AWSCloudWatch` | [Amazon Web Services S3](../connectors/awss3.md) |
| `AWSGuardDuty` | [Amazon Web Services S3](../connectors/awss3.md) |
| `AWSVPCFlow` | [Amazon Web Services S3](../connectors/awss3.md) |
| `AWSWAF` | [Amazon Web Services S3 WAF](../connectors/awss3wafccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
