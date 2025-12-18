# Google Cloud Platform NAT (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `GCPNATLogsCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`GCPNAT`](../tables-index.md#gcpnat), [`GCPNATAudit`](../tables-index.md#gcpnataudit) |
| **Used in Solutions** | [GoogleCloudPlatformNAT](../solutions/googlecloudplatformnat.md) |
| **Connector Definition Files** | [GCPNATLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformNAT/Data%20Connectors/GCPNATLogs_ccp/GCPNATLogs_ConnectorDefinition.json) |

The Google Cloud Platform NAT data connector provides the capability to ingest Cloud NAT Audit logs and Cloud NAT Traffic logs into Microsoft Sentinel using the Compute Engine API. Refer the [Product overview](https://cloud.google.com/nat/docs/overview) document for more details.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect GCP NAT to Microsoft Sentinel**
#### 1. Setup the GCP environment 
 Ensure to have the following resources from the GCP Console:
 Project ID, Project Name, GCP Subscription name for the project, Workload Identity Pool ID, Workspace Identity Provider ID, and a Service Account to establish the connection.
 For more information, refer the [Connector tutorial](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformNAT/Data%20Connectors/README.md) for log setup and authentication setup tutorial.

 Find the Log set up script [**here**](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPCloudNATLogsSetup/GCPCloudNATLogsSetup.tf)
 & the Authentication set up script [**here**](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPInitialAuthenticationSetup)

**Government Cloud:**
#### 1. Setup the GCP environment 
 Ensure to have the following resources from the GCP Console:
 Project ID, Project Name, GCP Subscription name for the project, Workload Identity Pool ID, Workspace Identity Provider ID, and a Service Account to establish the connection.
 For more information, refer the [Connector tutorial](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformNAT/Data%20Connectors/README.md) for log setup and authentication setup tutorial.

 Find the Log set up script [**here**](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/GCP/Terraform/sentinel_resources_creation_gov/GCPCloudNATLogsSetup/GCPCloudNATLogsSetup.tf)
 & the Authentication set up script [**here**](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation_gov/GCPInitialAuthenticationSetupGov)
- **Tenant ID: A unique identifier that is used as an input in the Terraform configuration within a GCP environment.**: `TenantId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
#### 2. Enable NAT logs 
 In the Google Cloud Console, enable cloud logging if not enabled previously, and save the changes. Navigate to Cloud NAT section and click on Add origin to create backends as per link provided below. 

 Reference Link: [Link to documentation](https://cloud.google.com/nat/docs/monitoring)
#### 3. Connect new collectors 
 To enable GCP Cloud NAT Logs for Microsoft Sentinel, click on Add new collector button, provide the required information in the pop up and click on Connect.
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
