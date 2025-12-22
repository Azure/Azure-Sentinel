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

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

#### 1. Set up your GCP environment 
 You must have the following GCP resources defined and configured: topic, subscription for the topic, workload identity pool, workload identity provider and service account with permissions to get and consume from subscription. 
 Terraform provides API for the IAM that creates the resources. [Link to Terraform scripts](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation).

**Government Cloud:**
#### 1. Set up your GCP environment 
 You must have the following GCP resources defined and configured: topic, subscription for the topic, workload identity pool, workload identity provider and service account with permissions to get and consume from subscription. 
 Terraform provides API for the IAM that creates the resources. [Link to Gov Terraform scripts](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation_gov).
- **Tenant ID: A unique identifier that is used as an input in the Terraform configuration within a GCP environment.**: `TenantId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
#### 2. Enable Load Balancer logs 
In your GCP account, navigate to the Load Balancer section. In here you can nevigate to [**Backend Service**] -> [**Edit**], once you are in the [**Backend Service**]  on the [**Logging**] section **enable** the checkbox of [**Enable Logs**]. Once you open the rule, switch the toggle button under the **Logs** section to **On**, and save the changes.

For more information: [Link to documentation](https://cloud.google.com/load-balancing/docs/https/https-logging-monitoring)
#### 3. Connect new collectors 
 To enable GCP Load Balancer Logs for Microsoft Sentinel, click the Add new collector button, fill the required information in the context pane and click on Connect.
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
| **Tables Ingested** | `GCPLoadBalancerLogs_CL` |
| **Connector Definition Files** | [GCPFLoadBalancerLogs_Definition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Load%20Balancer%20Logs/Data%20Connectors/GCPFLoadBalancerLogs_GCP_CCP/GCPFLoadBalancerLogs_Definition.json) |

[→ View full connector details](../connectors/gcpfloadbalancerlogsccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPLoadBalancerLogs_CL` | [GCP Pub/Sub Load Balancer Logs (via Codeless Connector Platform).](../connectors/gcpfloadbalancerlogsccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
