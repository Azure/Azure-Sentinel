# Google Cloud Platform IAM (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `GCPIAMCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`GCPIAM`](../tables-index.md#gcpiam) |
| **Used in Solutions** | [GoogleCloudPlatformIAM](../solutions/googlecloudplatformiam.md) |
| **Connector Definition Files** | [GCPIAMLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Data%20Connectors/GCPIAMLog_CCP/GCPIAMLog_ConnectorDefinition.json) |

The Google Cloud Platform IAM data connector provides the capability to ingest the Audit logs relating to Identity and Access Management (IAM) activities within Google Cloud into Microsoft Sentinel using the Google IAM API. Refer to [GCP IAM API](https://cloud.google.com/iam/docs/reference/rest) documentation for more information.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect GCP IAM to Microsoft Sentinel**
>**NOTE:** If both Azure Function and CCF connector are running parallelly, duplicate data is populated in the tables.
#### 1. Setup the GCP environment 
 Ensure to have the following resources from the GCP Console:
 Project ID, Project Name, GCP Subscription name for the project, Workload Identity Pool ID, Workspace Identity Provider ID, and a Service Account to establish the connection.
 For more information, refer the [Connector tutorial](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Data%20Connectors/README.md) for log setup and authentication setup tutorial.
 Log set up script: [Click Here](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPIAMCCPLogsSetup)
Authentication set up script: [Click here](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPInitialAuthenticationSetup)

**Government Cloud:**
#### 1. Setup the GCP environment 
 Ensure to have the following resources from the GCP Console:
 Project ID, Project Name, GCP Subscription name for the project, Workload Identity Pool ID, Workspace Identity Provider ID, and a Service Account to establish the connection.
 For more information, refer the [Connector tutorial](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Data%20Connectors/README.md) for log setup and authentication setup tutorial.
 Log set up script: [Click Here](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation_gov/GCPIAMCCPLogsSetup)
Authentication set up script: [Click here](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation_gov/GCPInitialAuthenticationSetupGov)
- **Tenant ID: A unique identifier that is used as an input in the Terraform configuration within a GCP environment.**: `TenantId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
#### 2. To enable IAM logs 
 In your GCP account, navigate to the IAM section. From there, you can either create a new user or modify an existing user's role that you want to monitor. Be sure to save your changes..

For more information: [Link to documentation](https://cloud.google.com/assured-workloads/docs/iam-roles?hl=en)
#### 3. Connect new collectors 
 To enable GCPIAM Logs for Microsoft Sentinel, click the Add new collector button, fill the required information in the context pane and click on Connect.
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
