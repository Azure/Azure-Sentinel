# Google Cloud Platform NAT (via Codeless Connector Framework)

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `GCPNATLogsCCPDefinition` |
| **Publisher** | Microsoft |
| **Used in Solutions** | [GoogleCloudPlatformNAT](../solutions/googlecloudplatformnat.md) |
| **Collection Method** | CCF |
| **Connector Definition Files** | [GCPNATLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformNAT/Data%20Connectors/GCPNATLogs_ccp/GCPNATLogs_ConnectorDefinition.json) |

The Google Cloud Platform NAT data connector provides the capability to ingest Cloud NAT Audit logs and Cloud NAT Traffic logs into Microsoft Sentinel using the Compute Engine API. Refer the [Product overview](https://cloud.google.com/nat/docs/overview) document for more details.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`GCPNAT`](../tables/gcpnat.md) | — | ✗ |
| [`GCPNATAudit`](../tables/gcpnataudit.md) | — | ✗ |

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

## Additional Documentation

> 📄 *Source: [GoogleCloudPlatformNAT\Data Connectors\README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformNAT\Data Connectors\README.md)*

# Integrating GCP Cloud NAT into Microsoft Sentinel
## Table of contents
- [Integrating GCP Cloud NAT into Microsoft Sentinel](#integrating-gcp-cloud-nat-into-microsoft-sentinel)
  - [Table of contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Steps to execute Terraform scripts for Log Setup](#steps-to-execute-terraform-scripts-for-log-setup)
  - [Steps to execute Terraform script for Authentication setup](#steps-to-execute-terraform-script-for-authentication-setup)


<a name="intro">

## Introduction
The GCP Cloud NAT Codeless Connector for Microsoft Sentinel enables seamless integration of GCP Cloud NAT logs with Microsoft Sentinel without the need for custom code. Developed as part of the Codeless Connector Platform(CCP), this connector simplifies the process of collecting and ingesting Cloud NAT logs from Google Cloud Platform into Microsoft Sentinel.

<a name="step2">
   
## Prerequisites
The below mentioned resources are required to connect GCP with Sentinel.
- Project ID
- Project Number
- GCP Subscription Name
- Workload Identity Pool ID
- Service Account
- Workload Identity Provider ID

To generate the above resources, you must execute the following terraform scripts.

- Log Setup File
- Authentication setup file
  
<a name="log">

## Steps to execute Terraform scripts for Log Setup
To access the terraform script for Log Setup [Click here](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPCloudNATLogsSetup/GCPCloudNATLogsSetup.tf).
- Launch the cloud shell in Google Cloud Console.
- Execute the below mentioned commands.
- create a directory
  ```
  mkdir <dir_name>
  ```
- Navigate to the directory
  ```
  cd <dir_name>
  ```
- Copy the github raw link of the Terraform script and get the content of the file into a shell using the following command:
   ```
   wget <raw link of the file> -O <filename.tf>
   ```
- Initializes your terraform working directory, downloads provider plugins, and configures the backend for state storage.
   ```
   terraform init
   ```
- Creates an execution plan to show what actions terraform will take to achieve the desired state of your infrastructure.
   ```
   terraform plan
   ```
   Once you execute this command it will ask to "Enter your project ID". Please enter your GCP Project ID.
  
- Executes the actions proposed in the Terraform plan to create, update, or destroy resources in your infrastructure.
   ```
   terraform apply
   ```
   Once you execute this command it will again ask to "Enter your project ID". Please enter your GCP Project ID one more time.
  
- After successfully executing the Log Setup file, `topic name`, `subscription name` is generated in the GCP Project. Save those details for future reference.

<a name="auth">
  
## Steps to execute Terraform script for Authentication setup
- If the Authentication setup file is previously executed in the project while configuring any other GCP data connectors, there is no need to execute the Authentication setup file again. You can use the existing `Workload Identity Pool ID` and `Workload Identity Provider ID` for authentication  purpose.
- If these fields are not generated previously, execute the Authentication Setup file with the same commands mentioned above.
- To access the Authentication Setup file [Click Here](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPInitialAuthenticationSetup).
- To Execute the Authentication Setup file [Click Here](https://learn.microsoft.com/en-us/azure/sentinel/connect-google-cloud-platform?tabs=terraform%2Cauditlogs#gcp-authentication-setup).
- After executing the authentication setup file, `Workload Identity Pool ID` and `Workload Identity Provider ID` are generated in the project.

[← Back to Connectors Index](../connectors-index.md)
