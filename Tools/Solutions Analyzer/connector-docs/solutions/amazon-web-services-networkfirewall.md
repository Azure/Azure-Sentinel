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

This solution provides **1 data connector(s)**.

### [Amazon Web Services NetworkFirewall (via Codeless Connector Framework)](../connectors/awsnetworkfirewallccpdefinition.md)

**Publisher:** Microsoft

This data connector allows you to ingest AWS Network Firewall logs into Microsoft Sentinel for advanced threat detection and security monitoring. By leveraging Amazon S3 and Amazon SQS, the connector forwards network traffic logs, intrusion detection alerts, and firewall events to Microsoft Sentinel, enabling real-time analysis and correlation with other security data

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `AWSNetworkFirewallAlert` |
| | `AWSNetworkFirewallFlow` |
| | `AWSNetworkFirewallTls` |
| **Connector Definition Files** | [AWSNetworkFirewallLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services%20NetworkFirewall/Data%20Connectors/AWSNetworkFirewallLogs_CCP/AWSNetworkFirewallLog_ConnectorDefinition.json) |

[→ View full connector details](../connectors/awsnetworkfirewallccpdefinition.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AWSNetworkFirewallAlert` | [Amazon Web Services NetworkFirewall (via Codeless Connector Framework)](../connectors/awsnetworkfirewallccpdefinition.md) |
| `AWSNetworkFirewallFlow` | [Amazon Web Services NetworkFirewall (via Codeless Connector Framework)](../connectors/awsnetworkfirewallccpdefinition.md) |
| `AWSNetworkFirewallTls` | [Amazon Web Services NetworkFirewall (via Codeless Connector Framework)](../connectors/awsnetworkfirewallccpdefinition.md) |

## Release Notes

**Version** | **Date Modified (DD-MM-YYYY)**| **ChangeHistory**                                                                         |
|------------|-------------------------------|-------------------------------------------------------------------------------------------|
| 3.0.2      | 19-08-2025                    | **CCF Connector** moving to GA.  | 
| 3.0.1      | 23-07-2025                    | Updated AWS Network Firewall Readme file and the associated links for the **CCF Data Connector**  |   
| 3.0.0      | 20-03-2025                    | Initial Solution Release                                               					 |

[← Back to Solutions Index](../solutions-index.md)
