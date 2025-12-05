# AWS VPC Flow Logs

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-07-30 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20VPC%20Flow%20Logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20VPC%20Flow%20Logs) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Amazon Web Services S3 VPC Flow Logs](../connectors/awss3vpcflowlogsparquetdefinition.md)

**Publisher:** Microsoft

This connector allows you to ingest AWS VPC Flow Logs, collected in AWS S3 buckets, to Microsoft Sentinel. AWS VPC Flow Logs provide visibility into network traffic within your AWS Virtual Private Cloud (VPC), enabling security analysis and network monitoring.

| | |
|--------------------------|---|
| **Tables Ingested** | `AWSVPCFlow` |
| **Connector Definition Files** | [AWSVPCFlowLogs_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20VPC%20Flow%20Logs/Data%20Connectors/AWSVPCFlowLogs_CCP/AWSVPCFlowLogs_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/awss3vpcflowlogsparquetdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AWSVPCFlow` | [Amazon Web Services S3 VPC Flow Logs](../connectors/awss3vpcflowlogsparquetdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
