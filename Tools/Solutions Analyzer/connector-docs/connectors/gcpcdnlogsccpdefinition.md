# Google Cloud Platform CDN (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `GCPCDNLogsCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`GCPCDN`](../tables-index.md#gcpcdn) |
| **Used in Solutions** | [GoogleCloudPlatformCDN](../solutions/googlecloudplatformcdn.md) |
| **Connector Definition Files** | [GCPCDNLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformCDN/Data%20Connectors/GCPCDNLogs_ccp/GCPCDNLogs_ConnectorDefinition.json) |

The Google Cloud Platform CDN data connector provides the capability to ingest Cloud CDN Audit logs and Cloud CDN Traffic logs into Microsoft Sentinel using the Compute Engine API. Refer the [Product overview](https://cloud.google.com/cdn/docs/overview) document for more details.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect GCP CDN to Microsoft Sentinel**
#### 1. Setup the GCP environment 
 Ensure to have the following resources from the GCP Console:
 Project ID, Project Name, GCP Subscription name for the project, Workload Identity Pool ID, Workspace Identity Provider ID, and a Service Account to establish the connection.
 For more information, refer the [Connector tutorial](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformCDN/Data%20Connectors/README.md) for log setup and authentication setup tutorial.

 Find the Log set up script [**here**](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPCDNLogsSetup)
 & the Authentication set up script [**here**](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPInitialAuthenticationSetup)

**Government Cloud:**
#### 1. Setup the GCP environment 
 Ensure to have the following resources from the GCP Console:
 Project ID, Project Name, GCP Subscription name for the project, Workload Identity Pool ID, Workspace Identity Provider ID, and a Service Account to establish the connection.
 For more information, refer the [Connector tutorial](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformCDN/Data%20Connectors/README.md) for log setup and authentication setup tutorial.

 Find the Log set up script [**here**](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation_gov/GCPCDNLogsSetup)
 & the Authentication set up script [**here**](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation_gov/GCPInitialAuthenticationSetupGov)
- **Tenant ID: A unique identifier that is used as an input in the Terraform configuration within a GCP environment.**: `TenantId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
#### 2. Enable CDN logs 
 In the Google Cloud Console, enable cloud logging if not enabled previously, and save the changes. Navigate to Cloud CDN section and click on Add origin to create backends as per link provided below. 

 Reference Link: [Link to documentation](https://cloud.google.com/cdn/docs/using-cdn)
#### 3. Connect new collectors 
 To enable GCP Cloud CDN Logs for Microsoft Sentinel, click on Add new collector button, provide the required information in the pop up and click on Connect.
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
