# AWS_AccessLogs

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-02-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_AccessLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_AccessLogs) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [AWS S3 Server Access Logs (via Codeless Connector Framework)](../connectors/awss3serveraccesslogsdefinition.md)

**Publisher:** Microsoft

This connector allows you to ingest AWS S3 Server Access Logs into Microsoft Sentinel. These logs contain detailed records for requests made to S3 buckets, including the type of request, resource accessed, requester information, and response details. These logs are useful for analyzing access patterns, debugging issues, and ensuring security compliance.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `AWSS3ServerAccess` |
| **Connector Definition Files** | [AWSS3ServerAccessLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_AccessLogs/Data%20Connectors/AwsS3ServerAccessLogsDefinition_CCP/AWSS3ServerAccessLogs_ConnectorDefinition.json) |

[→ View full connector details](../connectors/awss3serveraccesslogsdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AWSS3ServerAccess` | [AWS S3 Server Access Logs (via Codeless Connector Framework)](../connectors/awss3serveraccesslogsdefinition.md) |

## Release Notes

**Version** | **Date Modified (DD-MM-YYYY)**| **ChangeHistory**                                                                         |
|------------|-------------------------------|-------------------------------------------------------------------------------------------|
| 3.0.1      | 10-06-2025                    | AWS S3 Server Access Log CCF **Data Connector** Moving to GA.  |
| 3.0.0      | 08-08-2025                    | Initial Solution Release. <br/>New CCF **Data Connector** for AWS_AccessLogs.  |

[← Back to Solutions Index](../solutions-index.md)
