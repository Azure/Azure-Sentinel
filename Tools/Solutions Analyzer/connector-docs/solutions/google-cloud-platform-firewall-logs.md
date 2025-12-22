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

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

#### 1. Set up your GCP environment 
 You must have the following GCP resources defined and configured: topic, subscription for the topic, workload identity pool, workload identity provider and service account with permissions to get and consume from subscription. 
 Terraform provides API for the IAM that creates the resources. [Link to Terraform scripts](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation)
 Connector tutorial: [Link to tutorial](https://learn.microsoft.com/en-us/azure/sentinel/connect-google-cloud-platform?tabs=terraform%2Cauditlogs#gcp-authentication-setup) .

**Government Cloud:**
#### 1. Set up your GCP environment 
 You must have the following GCP resources defined and configured: topic, subscription for the topic, workload identity pool, workload identity provider and service account with permissions to get and consume from subscription. 
 Terraform provides API for the IAM that creates the resources. [Link to Gov Terraform scripts](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation_gov)
 Connector tutorial: [Link to tutorial](https://learn.microsoft.com/en-us/azure/sentinel/connect-google-cloud-platform?tabs=terraform%2Cauditlogs#gcp-authentication-setup).
- **Tenant ID: A unique identifier that is used as an input in the Terraform configuration within a GCP environment.**: `TenantId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
#### 2. Enable Firewall logs 
In your GCP account, navigate to the Firewall section. Here, you can either create a new rule or edit an existing one that you want to monitor. Once you open the rule, switch the toggle button under the **Logs** section to **On**, and save the changes.

For more information: [Link to documentation](https://cloud.google.com/firewall/docs/using-firewall-rules-logging?_gl=1*1no0nhk*_ga*NDMxNDIxODI3LjE3MjUyNjUzMzc.*_ga_WH2QY8WWF5*MTcyNTUyNzc4MS4xMS4xLjE3MjU1MjgxNTIuNDYuMC4w)
#### 3. Connect new collectors 
 To enable GCP Firewall Logs for Microsoft Sentinel, click the Add new collector button, fill the required information in the context pane and click on Connect.
**GCP Collector Management**

📊 **View GCP Collectors**: A management interface displays your configured Google Cloud Platform data collectors.

➕ **Add New Collector**: Click "Add new collector" to configure a new GCP data connection.

> 💡 **Portal-Only Feature**: This configuration interface is only available in the Microsoft Sentinel portal.

**GCP Connection Configuration**

When you click "Add new collector" in the portal, you'll be prompted to provide:
- **Project ID**: Your Google Cloud Platform project ID
- **Service Account**: GCP service account credentials with appropriate permissions
- **Subscription**: The Pub/Sub subscription to monitor for log data

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

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
