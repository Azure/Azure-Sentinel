# Google Cloud Platform VPC Flow Logs

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-02-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20VPC%20Flow%20Logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20VPC%20Flow%20Logs) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [GCP Pub/Sub VPC Flow Logs (via Codeless Connector Framework)](../connectors/gcpvpcflowlogsccpdefinition.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`GCPVPCFlow`](../tables/gcpvpcflow.md) | [GCP Pub/Sub VPC Flow Logs (via Codeless Connector Framework)](../connectors/gcpvpcflowlogsccpdefinition.md) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 26-06-2025                     | GCP Pub/Sub VPC Flow Logs **CCF Connector** moving to GA.  |
| 3.0.0       | 26-02-2025                     | Initial Solution Release.<br/>New CCP **Data Connector** 'GCP Pub/Sub VPC Flow Logs'.  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
