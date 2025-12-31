# Google Cloud Platform Firewall Logs

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2024-11-03 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Firewall%20Logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Firewall%20Logs) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [GCP Pub/Sub Firewall Logs](../connectors/gcpfirewalllogsccpdefinition.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`GCPFirewallLogs`](../tables/gcpfirewalllogs.md) | [GCP Pub/Sub Firewall Logs](../connectors/gcpfirewalllogsccpdefinition.md) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                 |
|-------------|--------------------------------|----------------------------------------------------|
| 3.0.1       | 28-05-2025                     | Updated **Data Connector** to add support for multiple collectors |
| 3.0.0       | 19-11-2024                     | Initial Solution release		                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
