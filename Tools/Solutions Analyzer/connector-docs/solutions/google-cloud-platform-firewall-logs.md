# Google Cloud Platform Firewall Logs

## Solution Information

| | |
|------------------------|-------|
| **Publisher** |  |
| **Support Tier** |  |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Firewall%20Logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Firewall%20Logs) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [GCP Pub/Sub Firewall Logs](../connectors/gcpfirewalllogsccpdefinition.md)

**Publisher:** Microsoft

The Google Cloud Platform (GCP) firewall logs, enable you to capture network inbound and outbound activity to monitor access and detect potential threats across Google Cloud Platform (GCP) resources.

| | |
|--------------------------|---|
| **Tables Ingested** | `GCPFirewallLogs` |
| **Connector Definition Files** | [GCP_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Firewall%20Logs/Data%20Connectors/GCPFirewallLogs_ccp/GCP_ConnectorDefinition.json) |

[→ View full connector details](../connectors/gcpfirewalllogsccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPFirewallLogs` | [GCP Pub/Sub Firewall Logs](../connectors/gcpfirewalllogsccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
