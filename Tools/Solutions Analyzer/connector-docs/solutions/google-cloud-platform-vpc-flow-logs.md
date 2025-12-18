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

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

#### 1. Set up your GCP environment 
 You must have the following GCP resources defined and configured: topic, subscription for the topic, workload identity pool, workload identity provider, and service account with permissions to get and consume from the subscription. 
 To configure this data connector, execute the following Terraform scripts:
 1. Setup Required Resources: [Configuration Guide](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPVPCFlowLogsSetup/readme.md)
 2. Setup Authentication: [Authentication tutorial](https://learn.microsoft.com/en-us/azure/sentinel/connect-google-cloud-platform?tabs=terraform%2Cauditlogs#gcp-authentication-setup). Note: If Authentication is already setup using another GCP data connector , kindly skip this step and use the existing service account and workload identity pool.

**Government Cloud:**
#### 1. Set up your GCP environment 
 You must have the following GCP resources defined and configured: topic, subscription for the topic, workload identity pool, workload identity provider, and service account with permissions to get and consume from the subscription. 
 To configure this data connector, execute the following Terraform scripts:
 1. Setup Required Resources: [Configuration Guide]https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPVPCFlowLogsSetup/readme.md)
 2. Setup Authentication: [Authentication tutorial](https://learn.microsoft.com/en-us/azure/sentinel/connect-google-cloud-platform?tabs=terraform%2Cauditlogs#gcp-authentication-setup). Note: If Authentication is already setup using another GCP data connector , kindly skip this step and use the existing service account and workload identity pool.
- **Tenant ID: A unique identifier that is used as an input in the Terraform configuration within a GCP environment.**: `TenantId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
#### 2. Enable VPC Flow Logs 
In your GCP account, navigate to the VPC network section. Select the subnet you want to monitor and enable Flow Logs under the Logging section.

For more information: [Google Cloud Documentation](https://cloud.google.com/vpc/docs/using-flow-logs)
#### 3. Connect new collectors 
 To enable GCP VPC Flow Logs for Microsoft Sentinel, click the Add new collector button, fill in the required information in the context pane, and click Connect.
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
| **Tables Ingested** | `GCPVPCFlow` |
| **Connector Definition Files** | [GCPVPCFlowLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20VPC%20Flow%20Logs/Data%20Connectors/GCPVPCFlowLogs_GCP_CCP/GCPVPCFlowLogs_ConnectorDefinition.json) |

[→ View full connector details](../connectors/gcpvpcflowlogsccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPVPCFlow` | [GCP Pub/Sub VPC Flow Logs (via Codeless Connector Framework)](../connectors/gcpvpcflowlogsccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
