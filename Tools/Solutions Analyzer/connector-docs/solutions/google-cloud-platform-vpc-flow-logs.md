# Google Cloud Platform VPC Flow Logs

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-02-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20VPC%20Flow%20Logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20VPC%20Flow%20Logs) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [GCP Pub/Sub VPC Flow Logs (via Codeless Connector Framework)](../connectors/gcpvpcflowlogsccpdefinition.md)

**Publisher:** Microsoft

The Google Cloud Platform (GCP) VPC Flow Logs enable you to capture network traffic activity at the VPC level, allowing you to monitor access patterns, analyze network performance, and detect potential threats across GCP resources.

| | |
|--------------------------|---|
| **Tables Ingested** | `GCPVPCFlow` |
| **Connector Definition Files** | [GCPVPCFlowLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20VPC%20Flow%20Logs/Data%20Connectors/GCPVPCFlowLogs_GCP_CCP/GCPVPCFlowLogs_ConnectorDefinition.json) |

[→ View full connector details](../connectors/gcpvpcflowlogsccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPVPCFlow` | [GCP Pub/Sub VPC Flow Logs (via Codeless Connector Framework)](../connectors/gcpvpcflowlogsccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
