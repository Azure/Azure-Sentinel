# Amazon Web Services NetworkFirewall (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `AwsNetworkFirewallCcpDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AWSNetworkFirewallAlert`](../tables-index.md#awsnetworkfirewallalert), [`AWSNetworkFirewallFlow`](../tables-index.md#awsnetworkfirewallflow), [`AWSNetworkFirewallTls`](../tables-index.md#awsnetworkfirewalltls) |
| **Used in Solutions** | [Amazon Web Services NetworkFirewall](../solutions/amazon-web-services-networkfirewall.md) |
| **Connector Definition Files** | [AWSNetworkFirewallLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Amazon%20Web%20Services%20NetworkFirewall/Data%20Connectors/AWSNetworkFirewallLogs_CCP/AWSNetworkFirewallLog_ConnectorDefinition.json) |

This data connector allows you to ingest AWS Network Firewall logs into Microsoft Sentinel for advanced threat detection and security monitoring. By leveraging Amazon S3 and Amazon SQS, the connector forwards network traffic logs, intrusion detection alerts, and firewall events to Microsoft Sentinel, enabling real-time analysis and correlation with other security data

[← Back to Connectors Index](../connectors-index.md)
