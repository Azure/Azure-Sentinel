# Google Cloud Platform Load Balancer Logs

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2025-02-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Load%20Balancer%20Logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Load%20Balancer%20Logs) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [GCP Pub/Sub Load Balancer Logs (via Codeless Connector Platform).](../connectors/gcpfloadbalancerlogsccpdefinition.md)

**Publisher:** Microsoft

Google Cloud Platform (GCP) Load Balancer logs provide detailed insights into network traffic, capturing both inbound and outbound activities. These logs are used for monitoring access patterns and identifying potential security threats across GCP resources. Additionally, these logs also include GCP Web Application Firewall (WAF) logs, enhancing the ability to detect and mitigate risks effectively.

| | |
|--------------------------|---|
| **Tables Ingested** | `GCPLoadBalancerLogs_CL` |
| **Connector Definition Files** | [GCPFLoadBalancerLogs_Definition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Load%20Balancer%20Logs/Data%20Connectors/GCPFLoadBalancerLogs_GCP_CCP/GCPFLoadBalancerLogs_Definition.json) |

[→ View full connector details](../connectors/gcpfloadbalancerlogsccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPLoadBalancerLogs_CL` | [GCP Pub/Sub Load Balancer Logs (via Codeless Connector Platform).](../connectors/gcpfloadbalancerlogsccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
