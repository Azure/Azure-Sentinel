# GoogleCloudPlatformDNS

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-07-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[DEPRECATED] Google Cloud Platform DNS](../connectors/gcpdnsdataconnector.md)

**Publisher:** Google

### [Google Cloud Platform DNS (via Codeless Connector Framework)](../connectors/gcpdnslogsccpdefinition.md)

**Publisher:** Microsoft

The Google Cloud Platform DNS data connector provides the capability to ingest Cloud DNS Query logs and Cloud DNS Audit logs into Microsoft Sentinel using the Google Cloud DNS API. Refer to [Cloud DNS API](https://cloud.google.com/dns/docs/reference/rest/v1) documentation for more information.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect GCP DNS to Microsoft Sentinel**
>**NOTE:** If both Azure Function and CCP connector are running simultaneously, duplicate data is populated in the tables.
#### 1. Setup the GCP environment 
 Ensure to have the following resources from the GCP Console:
 Project ID, Project Name, GCP Subscription name for the project, Workload Identity Pool ID, Workspace Identity Provider ID, and a Service Account to establish the connection.
 For more information, refer the [Connector tutorial](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Data%20Connectors/README.md) for log setup and authentication setup tutorial.
 Log set up script: [Click Here](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPDNS_CCPLogsSetup)
Authentication set up script: [Click here](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPInitialAuthenticationSetup)

**Government Cloud:**
#### 1. Setup the GCP environment 
 Ensure to have the following resources from the GCP Console:
 Project ID, Project Name, GCP Subscription name for the project, Workload Identity Pool ID, Workspace Identity Provider ID, and a Service Account to establish the connection.
 For more information, refer the [Connector tutorial](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Data%20Connectors/README.md) for log setup and authentication setup tutorial.
 Log set up script: [Click Here](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation_gov/GCPDNS_CCPLogsSetupGov)
Authentication set up script: [Click here](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation_gov/GCPInitialAuthenticationSetupGov)
- **Tenant ID: A unique identifier that is used as an input in the Terraform configuration within a GCP environment.**: `TenantId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
#### 2. Enable DNS logs 
 In the Google Cloud Console, navigate to Cloud DNS Section. Enable cloud logging if not enabled previously, and save the changes. Here, you can manage the existing zones, or create a new zone and create policies for the zone which you want to monitor.

For more information: [Link to documentation](https://cloud.google.com/dns/docs/zones/zones-overview)
#### 3. Connect new collectors 
 To enable GCP DNS Logs for Microsoft Sentinel, click on Add new collector button, provide the required information in the pop up and click on Connect.
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
| **Tables Ingested** | `GCPDNS` |
| **Connector Definition Files** | [GCPDNSLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Data%20Connectors/GCPDNSLog_CCP/GCPDNSLog_ConnectorDefinition.json) |

[→ View full connector details](../connectors/gcpdnslogsccpdefinition.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPDNS` | [Google Cloud Platform DNS (via Codeless Connector Framework)](../connectors/gcpdnslogsccpdefinition.md) |
| `GCP_DNS_CL` | [[DEPRECATED] Google Cloud Platform DNS](../connectors/gcpdnsdataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
