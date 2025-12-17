# VMware Carbon Black Cloud via AWS S3

| | |
|----------|-------|
| **Connector ID** | `carbonBlackAWSS3` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`ASimAuthenticationEventLogs`](../tables-index.md#asimauthenticationeventlogs), [`ASimFileEventLogs`](../tables-index.md#asimfileeventlogs), [`ASimNetworkSessionLogs`](../tables-index.md#asimnetworksessionlogs), [`ASimProcessEventLogs`](../tables-index.md#asimprocesseventlogs), [`ASimRegistryEventLogs`](../tables-index.md#asimregistryeventlogs), [`CarbonBlack_Alerts_CL`](../tables-index.md#carbonblack_alerts_cl), [`CarbonBlack_Watchlist_CL`](../tables-index.md#carbonblack_watchlist_cl) |
| **Used in Solutions** | [VMware Carbon Black Cloud](../solutions/vmware-carbon-black-cloud.md) |
| **Connector Definition Files** | [CarbonBlackViaAWSS3_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud/Data%20Connectors/CarbonBlackViaAWSS3_ConnectorDefinition.json), [CarbonBlack_DataConnectorDefination.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud/Data%20Connectors/VMwareCarbonBlackCloud_ccp/CarbonBlack_DataConnectorDefination.json) |

The [VMware Carbon Black Cloud](https://www.vmware.com/products/carbon-black-cloud.html) via AWS S3 data connector provides the capability to ingest watchlist, alerts, auth and endpoints events via AWS S3 and stream them to ASIM normalized tables. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission.

**Custom Permissions:**
- **Environment**: You must have the following AWS resources defined and configured: S3, Simple Queue Service (SQS), IAM roles and permissions policies
- **Environment**: You must have the a Carbon black account and required permissions to create a Data Forwarded to AWS S3 buckets. 
For more details visit [Carbon Black Data Forwarder Docs](https://docs.vmware.com/en/VMware-Carbon-Black-Cloud/services/carbon-black-cloud-user-guide/GUID-E8D33F72-BABB-4157-A908-D8BBDB5AF349.html)

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

#### 1. AWS CloudFormation Deployment 
 To configure access on AWS, two templates has been generated to set up the AWS environment to send logs from S3 bucket to your Log Analytics Workspace.
 #### For each template, create Stack in AWS: 
 1. Go to [AWS CloudFormation Stacks](https://aka.ms/awsCloudFormationLink#/stacks/create) 
 2. In AWS, choose the 'Upload a template file' option and click on 'Choose file'. Select the downloaded template 
 3. Click 'Next' and 'Create stack'
- **Template 1: OpenID connect authentication deployment**: `Oidc`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Template 2: AWS Carbon Black resources deployment**: `CarbonBlack`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
When deploying 'Template 2: AWS Carbon Black resources deployment' template you'll need supply a few parameters 
 * **Stack Name**: A stack name of your choosing (will appear in the list of stacks in AWS)
 * **Role Name**: Must begin with 'OIDC_' prefix, has a default value. 
 * **Bucket Name**: Bucket name of your choosing, if you already have an existing bucket paste the name here 
 * **CreateNewBucket**: If you already have an existing bucket that you would like to use for this connector select 'false' for this option, otherwise a bucket with the name you entered in 'Bucket Name' will be created from this stack. 
 * **Region**: This is the region of the AWS resources based on Carbon Black's mapping - for more information please see [Carbon Black documentation](https://developer.carbonblack.com/reference/carbon-black-cloud/integrations/data-forwarder/quick-setup/#create-a-bucket).
 * **SQSQueuePrefix**: The stack create multiple queues, this prefix will be added to each one of them. 
 * **WorkspaceID**: Use the Workspace ID provided below.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
Once the deployment is complete - head to the 'Outputs' tab, you will see: Role ARN, S3 bucket and 4 SQS resources created. You will need those resources in the next step when configuring Carbon Black's data forwarders and the data connector.
#### 2. Carbon Black data forwarder configuration 
 After all AWS resources has been created you'll need to configure Carbon Black to forward the events to the AWS buckets for Microsoft Sentinel to ingest them. Follow [Carbon Black's documentation on how to create a 'Data Forwarders'](https://developer.carbonblack.com/reference/carbon-black-cloud/integrations/data-forwarder/quick-setup/#2-create-a-forwarder) Use the first recommended option. When asked to input a bucket name use the bucket created in the previous step. 
 You will be required to add 'S3 prefix' for each forwarder, please use this mapping:
 | Event type      | S3 prefix | 
 |-----------------|-----------|
 | Alert           | carbon-black-cloud-forwarder/Alerts    |
 | Auth Events     | carbon-black-cloud-forwarder/Auth      |
 | Endpoint Events | carbon-black-cloud-forwarder/Endpoint  |
 | Watchlist Hit   | carbon-black-cloud-forwarder/Watchlist |
#### 2.1. Test your data forwarder (Optional) 
 To validate the data forwarder is configured as expected, in Carbon Black's portal search for the data forwarder that you just created and click on 'Test Forwarder' button under the 'Actions' column, this will generate a 'HealthCheck' file in the S3 Bucket, you should see it appear immediately.
#### 3. Connect new collectors 
 To enable AWS S3 for Microsoft Sentinel, click the 'Add new collector' button, fill the required information, the ARN role and the SQS URL are created in step 1, note that you will need to enter the correct SQS URL and select the appropriate event type from the dropdown, for example if you want to ingest Alert events you will need to copy the Alerts SQS URL and select the 'Alerts' event type in the dropdown

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
  - Alerts
  - Auth Events
  - Endpoint Events
  - Watchlist

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

[← Back to Connectors Index](../connectors-index.md)
