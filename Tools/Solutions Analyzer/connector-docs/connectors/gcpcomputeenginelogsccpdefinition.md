# Google Cloud Platform Compute Engine (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `GCPComputeEngineLogsCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`GCPComputeEngine`](../tables-index.md#gcpcomputeengine) |
| **Used in Solutions** | [Google Cloud Platform Compute Engine](../solutions/google-cloud-platform-compute-engine.md) |
| **Connector Definition Files** | [GCPComputeEngineLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Compute%20Engine/Data%20Connectors/GCPComputeEngineLog_CCP/GCPComputeEngineLog_ConnectorDefinition.json) |

The Google Cloud Platform Compute Engine data connector provides the capability to ingest Compute Engine Audit logs into Microsoft Sentinel using the Google Cloud Compute Engine API. Refer to [Cloud Compute Engine API](https://cloud.google.com/compute/docs/reference/rest/v1) documentation for more information.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect GCP Compute Engine to Microsoft Sentinel**
#### 1. Setup the GCP environment 
 Ensure to have the following resources from the GCP Console:
 Project ID, Project Name, GCP Subscription name for the project, Workload Identity Pool ID, Workspace Identity Provider ID, and a Service Account to establish the connection.
 For more information, refer the [Connector tutorial](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Compute%20Engine/Data%20Connectors/GCPComputeEngineReadme.md) for log setup and authentication setup tutorial.
 Log set up script: [Click Here](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPComputeEngineLogsSetup/GCPComputeEngineLogSetup.tf)
Authentication set up script: [Click here](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPInitialAuthenticationSetup)

**Government Cloud:**
#### 1. Setup the GCP environment 
 Ensure to have the following resources from the GCP Console:
 Project ID, Project Name, GCP Subscription name for the project, Workload Identity Pool ID, Workspace Identity Provider ID, and a Service Account to establish the connection.
 For more information, refer the [Connector tutorial](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Compute%20Engine/Data%20Connectors/GCPComputeEngineReadme.md) for log setup and authentication setup tutorial.
 Log set up script: [Click Here](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/GCP/Terraform/sentinel_resources_creation_gov/GCPComputeEngineLogsSetup/GCPComputeEngineLogSetup.tf)
Authentication set up script: [Click here](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation_gov/GCPInitialAuthenticationSetupGov)
- **Tenant ID: A unique identifier that is used as an input in the Terraform configuration within a GCP environment.**: `TenantId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
#### 2. Enable Compute Engine logs 
 In the Google Cloud Console, enable Compute Engine API, if not enabled previously, and save the changes.
#### 3. Connect new collectors 
 To enable Compute Engine Logs for Microsoft Sentinel, click on Add new collector button, provide the required information in the pop up and click on Connect.
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
