# AWS Security Hub

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-03-12 |
| **Last Updated** | 2025-03-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [AWS Security Hub Findings (via Codeless Connector Framework)](../connectors/awssecurityhubfindingsccpdefinition.md)

**Publisher:** Microsoft

This connector enables the ingestion of AWS Security Hub Findings, which are collected in AWS S3 buckets, into Microsoft Sentinel. It helps streamline the process of monitoring and managing security alerts by integrating AWS Security Hub Findings with Microsoft Sentinel's advanced threat detection and response capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `AWSSecurityHubFindings` |
| **Connector Definition Files** | [AWSSecurityHubFindings_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Data%20Connectors/AWSSecurityHubFindings_CCP/AWSSecurityHubFindings_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/awssecurityhubfindingsccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AWSSecurityHubFindings` | [AWS Security Hub Findings (via Codeless Connector Framework)](../connectors/awssecurityhubfindingsccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
