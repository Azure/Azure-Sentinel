# CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `CrowdStrikeFalconS3CCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`CrowdStrike_Additional_Events_CL`](../tables-index.md#crowdstrike_additional_events_cl), [`CrowdStrike_Audit_Events_CL`](../tables-index.md#crowdstrike_audit_events_cl), [`CrowdStrike_Auth_Events_CL`](../tables-index.md#crowdstrike_auth_events_cl), [`CrowdStrike_DNS_Events_CL`](../tables-index.md#crowdstrike_dns_events_cl), [`CrowdStrike_File_Events_CL`](../tables-index.md#crowdstrike_file_events_cl), [`CrowdStrike_Network_Events_CL`](../tables-index.md#crowdstrike_network_events_cl), [`CrowdStrike_Process_Events_CL`](../tables-index.md#crowdstrike_process_events_cl), [`CrowdStrike_Registry_Events_CL`](../tables-index.md#crowdstrike_registry_events_cl), [`CrowdStrike_Secondary_Data_CL`](../tables-index.md#crowdstrike_secondary_data_cl), [`CrowdStrike_User_Events_CL`](../tables-index.md#crowdstrike_user_events_cl) |
| **Used in Solutions** | [CrowdStrike Falcon Endpoint Protection](../solutions/crowdstrike-falcon-endpoint-protection.md) |
| **Connector Definition Files** | [DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/CrowdStrikeS3FDR_ccp/DataConnectorDefinition.json) |

The Crowdstrike Falcon Data Replicator (S3) connector provides the capability to ingest FDR event datainto Microsoft Sentinel from the AWS S3 bucket where the FDR logs have been streamed. The connector provides ability to get events from Falcon Agents which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.<p><span style='color:red; font-weight:bold;'>NOTE:</span></p><div style='margin-left:20px;'><p>1. CrowdStrike FDR license must be available & enabled.</p><p>2. The connector requires an IAM role to be configured on AWS to allow access to the AWS S3 bucket and may not be suitable for environments that leverage CrowdStrike - managed buckets.</p><p>3. For environments that leverage CrowdStrike-managed buckets, please configure the <strong>CrowdStrike Falcon Data Replicator (CrowdStrike-Managed AWS S3)</strong> connector.</p></div>

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

#### Requirements: 
 In order to use the Falcon Data Replicator feature the following are required: 
 1. **Subscription:** 
 1.1.  Falcon Data Replicator. 
 1.2. Falcon Insight XDR. 
 2. **Roles:** 
 2.1. Falcon Administrator.
#### 1. Setup your CrowdStrike & AWS environments 
 To configure access on AWS, use the following two templates provided to set up the AWS environment. This will enable sending logs from an S3 bucket to your Log Analytics Workspace.
 #### For each template, create Stack in AWS: 
 1. Go to [AWS CloudFormation Stacks](https://aka.ms/awsCloudFormationLink#/stacks/create). 
 2. Choose the ‘Specify template’ option, then ‘Upload a template file’ by clicking on ‘Choose file’ and selecting the appropriate CloudFormation template file provided below. click ‘Choose file’ and select the downloaded template. 
 3. Click 'Next' and 'Create stack'.
Make sure that your bucket will be created in the same AWS region as your Falcon CID where the FDR feed is provisioned. 
 | CrowdStrike region | AWS region | 
 |-----------------|-----------|
 | US-1 | us-west-1    |
 | US-2 | us-west-2 | 
 | EU-1 | eu-central-1 
- **Template 1: OpenID connect authentication deployment**: `Oidc`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Template 2: AWS CrowdStrike resources deployment**: `CrowdStrike`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
#### Using your own S3 Bucket 
 In order to use your own S3 bucket you can refernace the following guide [Use your own S3 bucket](https://falcon.us-2.crowdstrike.com/documentation/page/fa572b1c/falcon-data-replicator#g4f79236) or follow this steps: 
 1. Create support case with the following Name: **Using Self S3 bucket for FDR** 
 2. Add the following information: 
 2.1. The Falcon CID where your FDR feed is provisioned 
 2.2. Indicate which types of events you wish to have provided in this new FDR feed. 
 2.3. Indicate which types of events you wish to have provided in this new FDR feed. 
 2.4. Do not use any partitions. 
 | Event type      | S3 prefix | 
 |-----------------|-----------|
 | Primary Events | data/    |
 | Secondary Events | fdrv2/ 
#### 2. Connect new collectors 
 To enable AWS S3 for Microsoft Sentinel, click the Add new collector button, fill the required information in the context pane and click on Connect.
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **Role ARN**
- **Queue URL**
- **Stream name**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

**Add new controller**

*AWS S3 connector*

When you click the "Add new collector" button in the portal, a configuration form will open. You'll need to provide:

*Account details*

- **Role ARN** (required)
- **Queue URL** (required)
- **Data type** (required): Select from available options
  - Primary Events
  - Secondary Events

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

[← Back to Connectors Index](../connectors-index.md)
