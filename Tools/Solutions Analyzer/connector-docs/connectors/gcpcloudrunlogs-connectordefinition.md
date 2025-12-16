# GCP Cloud Run (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `GCPCloudRunLogs_ConnectorDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`GCPCloudRun`](../tables-index.md#gcpcloudrun) |
| **Used in Solutions** | [Google Cloud Platform Cloud Run](../solutions/google-cloud-platform-cloud-run.md) |
| **Connector Definition Files** | [GCPCloudRunLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Cloud%20Run/Data%20Connectors/GCPCloudRunLog_CCF/GCPCloudRunLogs_ConnectorDefinition.json) |

The GCP Cloud Run data connector provides the capability to ingest Cloud Run request logs into Microsoft Sentinel using Pub/Sub. Refer the [Cloud Run Overview](https://cloud.google.com/run/docs/logging) for more details.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect GCP Cloud Run to Microsoft Sentinel**
#### 1. Setup the GCP environment 
 Ensure to have the following resources from the GCP Console:
 Project ID, Project Name, GCP Subscription name for the project, Workload Identity Pool ID, Workspace Identity Provider ID, and a Service Account to establish the connection.
 For more information, refer the [Connector tutorial](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Cloud%20Run/Data%20Connectors/README.md) for log setup and authentication setup tutorial.

 Find the Log set up script [**here**](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPCloudRunLogsSetup)
 & the Authentication set up script [**here**](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPInitialAuthenticationSetup)

**Government Cloud:**
#### 1. Setup the GCP environment 
 Ensure to have the following resources from the GCP Console:
 Project ID, Project Name, GCP Subscription name for the project, Workload Identity Pool ID, Workspace Identity Provider ID, and a Service Account to establish the connection.
 For more information, refer the [Connector tutorial](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Cloud%20Run/Data%20Connectors/README.md) for log setup and authentication setup tutorial.

 Find the Log set up script [**here**](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation_gov/GCPCloudRunLogsSetup)
 & the Authentication set up script [**here**](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation_gov/GCPInitialAuthenticationSetupGov)
- **Tenant ID: A unique identifier that is used as an input in the Terraform configuration within a GCP environment.**: `TenantId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
#### 2. Enable Cloud Run logs 
 In the Google Cloud Console, enable cloud logging if not enabled previously, and save the changes.Deploy or update your Cloud Run services with logging enabled.

 Reference Link: [Link to documentation](https://cloud.google.com/run/docs/setup)
#### 3. Connect new collectors 
 To enable GCP Cloud Run Request Logs for Microsoft Sentinel, click on Add new collector button, provide the required information in the pop up and click on Connect.
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

[← Back to Connectors Index](../connectors-index.md)
