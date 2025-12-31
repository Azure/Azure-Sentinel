# GCP Cloud Run (via Codeless Connector Framework)

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `GCPCloudRunLogs_ConnectorDefinition` |
| **Publisher** | Microsoft |
| **Used in Solutions** | [Google Cloud Platform Cloud Run](../solutions/google-cloud-platform-cloud-run.md) |
| **Collection Method** | CCF |
| **Connector Definition Files** | [GCPCloudRunLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Cloud%20Platform%20Cloud%20Run/Data%20Connectors/GCPCloudRunLog_CCF/GCPCloudRunLogs_ConnectorDefinition.json) |

The GCP Cloud Run data connector provides the capability to ingest Cloud Run request logs into Microsoft Sentinel using Pub/Sub. Refer the [Cloud Run Overview](https://cloud.google.com/run/docs/logging) for more details.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`GCPCloudRun`](../tables/gcpcloudrun.md) | ✓ | ✗ |

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

## Additional Documentation

> 📄 *Source: [Google Cloud Platform Cloud Run\Data Connectors\README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google Cloud Platform Cloud Run\Data Connectors\README.md)*

# Integrating Google Cloud Platform Cloud Run into Microsoft Sentinel
## Table of contents
- [Introduction](#intro)
- [Prerequisites](#step2)
- [Steps to execute Terraform Scripts for log setup](#log)
- [Steps to execute Terraform Scripts for Authentication setup](#auth)


<a name="intro">

## Introduction
The Google Cloud Platform Cloud Run Codeless Connector for Microsoft Sentinel enables seamless integration of Google Cloud Platform Cloud Run logs with Microsoft Sentinel without the need for custom code. Developed as part of the Codeless Connector Framework(CCF), this connector simplifies the process of collecting and ingesting Cloud Run Request logs, Container logs and audit logs from Google Cloud Platform into Sentinel.


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
To access the terraform script for Log Setup [Click here](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPCloudRunLogsSetup).
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
- If these fields are not generated previously, execute the Authentication Setup file.
- To access the Authentication Setup file [Click Here](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/GCP/Terraform/sentinel_resources_creation/GCPInitialAuthenticationSetup).
- To Execute the Authentication Setup file [Click Here](https://learn.microsoft.com/en-us/azure/sentinel/connect-google-cloud-platform?tabs=terraform%2Cauditlogs#gcp-authentication-setup).
- After executing the authentication setup file, `Workload Identity Pool ID` and `Workload Identity Provider ID` are generated in the project.Save those details for future reference.

[← Back to Connectors Index](../connectors-index.md)
