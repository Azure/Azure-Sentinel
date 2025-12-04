# Amazon Web Services Route 53

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-03-21 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services%20Route%2053](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services%20Route%2053) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Amazon Web Services S3 DNS Route53 (via Codeless Connector Framework)](../connectors/awsroute53resolverccpdefinition.md)

**Publisher:** Microsoft

This connector enables ingestion of AWS Route 53 DNS logs into Microsoft Sentinel for enhanced visibility and threat detection. It supports DNS Resolver query logs ingested directly from AWS S3 buckets, while Public DNS query logs and Route 53 audit logs can be ingested using Microsoft Sentinel's AWS CloudWatch and CloudTrail connectors. Comprehensive instructions are provided to guide you through the setup of each log type. Leverage this connector to monitor DNS activity, detect potential threats, and improve your security posture in cloud environments.

| | |
|--------------------------|---|
| **Tables Ingested** | `AWSRoute53Resolver` |
| **Connector Definition Files** | [AWSRoute53Resolver_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services%20Route%2053/Data%20Connectors/AWSRoute53Resolver_CCP/AWSRoute53Resolver_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/awsroute53resolverccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AWSRoute53Resolver` | [Amazon Web Services S3 DNS Route53 (via Codeless Connector Framework)](../connectors/awsroute53resolverccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
