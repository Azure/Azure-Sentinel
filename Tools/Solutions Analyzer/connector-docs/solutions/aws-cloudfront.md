# AWS CloudFront

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-03-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20CloudFront](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20CloudFront) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Amazon Web Services CloudFront (via Codeless Connector Framework) (Preview)](../connectors/awscloudfrontccpdefinition.md)

**Publisher:** Microsoft

This data connector enables the integration of AWS CloudFront logs with Microsoft Sentinel to support advanced threat detection, investigation, and security monitoring. By utilizing Amazon S3 for log storage and Amazon SQS for message queuing, the connector reliably ingests CloudFront access logs into Microsoft Sentinel

| | |
|--------------------------|---|
| **Tables Ingested** | `AWSCloudFront_AccessLog_CL` |
| **Connector Definition Files** | [AWSCloudFrontLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20CloudFront/Data%20Connectors/AWSCloudFrontLog_CCF/AWSCloudFrontLog_ConnectorDefinition.json) |

[→ View full connector details](../connectors/awscloudfrontccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AWSCloudFront_AccessLog_CL` | [Amazon Web Services CloudFront (via Codeless Connector Framework) (Preview)](../connectors/awscloudfrontccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
