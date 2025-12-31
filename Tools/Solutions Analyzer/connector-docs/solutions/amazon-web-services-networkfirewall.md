# Amazon Web Services NetworkFirewall

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-03-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services%20NetworkFirewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services%20NetworkFirewall) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Amazon Web Services NetworkFirewall (via Codeless Connector Framework)](../connectors/awsnetworkfirewallccpdefinition.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AWSNetworkFirewallAlert`](../tables/awsnetworkfirewallalert.md) | [Amazon Web Services NetworkFirewall (via Codeless Connector Framework)](../connectors/awsnetworkfirewallccpdefinition.md) | - |
| [`AWSNetworkFirewallFlow`](../tables/awsnetworkfirewallflow.md) | [Amazon Web Services NetworkFirewall (via Codeless Connector Framework)](../connectors/awsnetworkfirewallccpdefinition.md) | - |
| [`AWSNetworkFirewallTls`](../tables/awsnetworkfirewalltls.md) | [Amazon Web Services NetworkFirewall (via Codeless Connector Framework)](../connectors/awsnetworkfirewallccpdefinition.md) | - |

## Release Notes

**Version** | **Date Modified (DD-MM-YYYY)**| **ChangeHistory**                                                                         |
|------------|-------------------------------|-------------------------------------------------------------------------------------------|
| 3.0.2      | 19-08-2025                    | **CCF Connector** moving to GA.  | 
| 3.0.1      | 23-07-2025                    | Updated AWS Network Firewall Readme file and the associated links for the **CCF Data Connector**  |   
| 3.0.0      | 20-03-2025                    | Initial Solution Release                                               					 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
