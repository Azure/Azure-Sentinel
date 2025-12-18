# GCP Cloud SQL (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `GCPCloudSQLCCFDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`GCPCloudSQL`](../tables-index.md#gcpcloudsql) |
| **Used in Solutions** | [GoogleCloudPlatformSQL](../solutions/googlecloudplatformsql.md) |
| **Connector Definition Files** | [GCPCloudSQLLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformSQL/Data%20Connectors/GCPCloudSQLLog_CCF/GCPCloudSQLLog_ConnectorDefinition.json) |

The GCP Cloud SQL data connector provides the capability to ingest Audit logs into Microsoft Sentinel using the GCP Cloud SQL API. Refer to [GCP cloud SQL Audit Logs](https://cloud.google.com/sql/docs/mysql/audit-logging) documentation for more information.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect GCP Cloud SQL to Microsoft Sentinel**
#### 1. Setup the GCP environment 
 Ensure to have the following resources from the GCP Console:
 Project ID, Project Name, GCP Subscription name for the project, Workload Identity Pool ID, Workspace Identity Provider ID, and a Service Account to establish the connection.
 For more information, refer the [Connector tutorial](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformSQL/Data%20Connectors/Readme.md) for log setup and authentication setup tutorial.
 Log set up script: [Click Here](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPCloudSQLLogsSetup/GCPCloudSQLLogsSetup.tf)
Authentication set up script: [Click here](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPInitialAuthenticationSetup)

**Government Cloud:**
#### 1. Setup the GCP environment 
 Ensure to have the following resources from the GCP Console:
 Project ID, Project Name, GCP Subscription name for the project, Workload Identity Pool ID, Workspace Identity Provider ID, and a Service Account to establish the connection.
 For more information, refer the [Connector tutorial](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformSQL/Data%20Connectors/Readme.md) for log setup and authentication setup tutorial.
 Log set up script: [Click Here](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/GCP/Terraform/sentinel_resources_creation_gov/GCPCloudSQLLogsSetup/GCPCloudSQLLogsSetup.tf)
Authentication set up script: [Click here](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation_gov/GCPInitialAuthenticationSetupGov)
- **Tenant ID: A unique identifier that is used as an input in the terraform configuration within a GCP environment.**: `TenantId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
#### 2. In the Google Cloud Console, enable Cloud SQL API, if not enabled previously, and save the changes.
#### 3. Connect new collectors 
 To enable GCP Cloud SQL Logs for Microsoft Sentinel, click the Add new collector button, fill the required information in the context pane and click on Connect.
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
