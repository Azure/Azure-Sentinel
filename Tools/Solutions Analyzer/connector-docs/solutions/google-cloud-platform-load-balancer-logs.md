# Google Cloud Platform Load Balancer Logs

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2025-02-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Load%20Balancer%20Logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Load%20Balancer%20Logs) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [GCP Pub/Sub Load Balancer Logs (via Codeless Connector Platform).](../connectors/gcpfloadbalancerlogsccpdefinition.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`GCPLoadBalancerLogs_CL`](../tables/gcploadbalancerlogs-cl.md) | [GCP Pub/Sub Load Balancer Logs (via Codeless Connector Platform).](../connectors/gcpfloadbalancerlogsccpdefinition.md) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                             |
|-------------|--------------------------------|------------------------------------------------|
| 3.0.1       | 28-03-2025                     | Moving Solution from Public Preview to Globally available.                       |
| 3.0.0       | 14-02-2025                     | Initial Solution Release.                       |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
