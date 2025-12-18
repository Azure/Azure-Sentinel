# GoogleCloudPlatformResourceManager

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2025-03-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformResourceManager](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformResourceManager) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Google Cloud Platform Resource Manager (via Codeless Connector Framework)](../connectors/gcpresourcemanagerlogsccfdefinition.md)

**Publisher:** Microsoft

The Google Cloud Platform Resource Manager data connector provides the capability to ingest Resource Manager [Admin Activity and Data Access Audit logs](https://cloud.google.com/resource-manager/docs/audit-logging) into Microsoft Sentinel using the Cloud Resource Manager API. Refer the [Product overview](https://cloud.google.com/resource-manager/docs/cloud-platform-resource-hierarchy) document for more details.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect GCP Resource Manager to Microsoft Sentinel**
#### 1. Setup the GCP environment 
 Ensure to have the following resources from the GCP Console:
 Project ID, Project Name, GCP Subscription name for the project, Workload Identity Pool ID, Workspace Identity Provider ID, and a Service Account to establish the connection.
 For more information, refer the [Connector tutorial](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/GoogleCloudPlatformResourceManager/Data%20Connectors/README.md) for log setup and authentication setup tutorial.

 Find the Log set up script [**here**](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPResourceManagerLogsSetup/GCPResourceManagerLogSetup.tf)
 & the Authentication set up script [**here**](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPInitialAuthenticationSetup)

**Government Cloud:**
#### 1. Setup the GCP environment 
 Ensure to have the following resources from the GCP Console:
 Project ID, Project Name, GCP Subscription name for the project, Workload Identity Pool ID, Workspace Identity Provider ID, and a Service Account to establish the connection.
 For more information, refer the [Connector tutorial](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/GoogleCloudPlatformResourceManager/Data%20Connectors/README.md) for log setup and authentication setup tutorial.

 Find the Log set up script [**here**](https://raw.githubusercontent.com/Azure/Azure-Sentinel/c1cb589dad1add228f78e629073a9b069ce52991/DataConnectors/GCP/Terraform/sentinel_resources_creation_gov/GCPResourceManagerLogsSetup/GCPResourceManagerLogSetup.tf)
 & the Authentication set up script [**here**](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation_gov/GCPInitialAuthenticationSetupGov)
- **Tenant ID: A unique identifier that is used as an input in the Terraform configuration within a GCP environment.**: `TenantId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
#### 2. Enable Resource Manager logs 
 In the Google Cloud Console, enable cloud resource manager API if not enabled previously, and save the changes. Make sure to have organization level IAM permissions for your account to see all logs in the resource hierarchy. You can refer the document links for different IAM permissions for access control with IAM at each level provided in this [link](https://cloud.google.com/resource-manager/docs/how-to)
#### 3. Connect new collectors 
 To enable GCP Resource Manager Logs for Microsoft Sentinel, click on Add new collector button, provide the required information in the pop up and click on Connect.
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
| **Tables Ingested** | `GCPResourceManager` |
| **Connector Definition Files** | [GCPResourceManagerAuditLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformResourceManager/Data%20Connectors/GCPResourceManagerAuditLogs_ccf/GCPResourceManagerAuditLogs_ConnectorDefinition.json) |

[→ View full connector details](../connectors/gcpresourcemanagerlogsccfdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPResourceManager` | [Google Cloud Platform Resource Manager (via Codeless Connector Framework)](../connectors/gcpresourcemanagerlogsccfdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
