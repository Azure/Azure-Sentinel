# VMware Carbon Black Cloud

| | |
|----------|-------|
| **Connector ID** | `VMwareCarbonBlack` |
| **Publisher** | VMware |
| **Tables Ingested** | [`CarbonBlackAuditLogs_CL`](../tables-index.md#carbonblackauditlogs_cl), [`CarbonBlackEvents_CL`](../tables-index.md#carbonblackevents_cl), [`CarbonBlackNotifications_CL`](../tables-index.md#carbonblacknotifications_cl) |
| **Used in Solutions** | [VMware Carbon Black Cloud](../solutions/vmware-carbon-black-cloud.md) |
| **Connector Definition Files** | [VMwareCarbonBlack_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud/Data%20Connectors/VMwareCarbonBlack_API_FunctionApp.json) |

The [VMware Carbon Black Cloud](https://www.vmware.com/products/carbon-black-cloud.html) connector provides the capability to ingest Carbon Black data into Microsoft Sentinel. The connector provides visibility into Audit, Notification and Event logs in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **VMware Carbon Black API Key(s)**: Carbon Black API and/or SIEM Level API Key(s) are required. See the documentation to learn more about the [Carbon Black API](https://developer.carbonblack.com/reference/carbon-black-cloud/cb-defense/latest/rest-api/).
 - A Carbon Black **API** access level API ID and Key is required for [Audit](https://developer.carbonblack.com/reference/carbon-black-cloud/cb-defense/latest/rest-api/#audit-log-events) and [Event](https://developer.carbonblack.com/reference/carbon-black-cloud/platform/latest/data-forwarder-config-api/) logs. 
 - A Carbon Black **SIEM** access level  API ID and Key is required for [Notification](https://developer.carbonblack.com/reference/carbon-black-cloud/cb-defense/latest/rest-api/#notifications) alerts.
- **Amazon S3 REST API Credentials/permissions**: **AWS Access Key Id**, **AWS Secret Access Key**, **AWS S3 Bucket Name**, **Folder Name in AWS S3 Bucket** are required for Amazon S3 REST API.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to VMware Carbon Black to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**STEP 1 - Configuration steps for the VMware Carbon Black API**

 [Follow these instructions](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#creating-an-api-key) to create an API Key.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the VMware Carbon Black connector, have the Workspace ID and Workspace Primary Key (can be copied from the following), as well as the VMware Carbon Black API Authorization Key(s), readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Option 1 - Azure Resource Manager (ARM) Template**

This method provides an automated deployment of the VMware Carbon Black connector using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinelcarbonblackazuredeploy) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/sentinelcarbonblackazuredeploy-gov)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Workspace ID**, **Workspace Key**, **Log Types**, **API ID(s)**, **API Key(s)**, **Carbon Black Org Key**, **S3 Bucket Name**, **AWS Access Key Id**, **AWS Secret Access Key**, **EventPrefixFolderName**,**AlertPrefixFolderName**,  and validate the **URI**.
> - Enter the URI that corresponds to your region. The complete list of API URLs can be [found here](https://community.carbonblack.com/t5/Knowledge-Base/PSC-What-URLs-are-used-to-access-the-APIs/ta-p/67346)
 - The default **Time Interval** is set to pull the last five (5) minutes of data. If the time interval needs to be modified, it is recommended to change the Function App Timer Trigger accordingly (in the function.json file, post deployment) to prevent overlapping data ingestion. 
 - Carbon Black requires a seperate set of API ID/Keys to ingest Notification alerts. Enter the SIEM API ID/Key values or leave blank, if not required. 
> - Note: If using Azure Key Vault secrets for any of the values above, use the`@Microsoft.KeyVault(SecretUri={Security Identifier})`schema in place of the string values. Refer to [Key Vault references documentation](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) for further details. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

**4. Option 2 - Manual Deployment of Azure Functions**

Use the following step-by-step instructions to deploy the VMware Carbon Black connector manually with Azure Functions.

**1. Create a Function App**

1.  From the Azure Portal, navigate to [Function App](https://portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/Microsoft.Web%2Fsites/kind/functionapp), and select **+ Add**.
2. In the **Basics** tab, ensure Runtime stack is set to **Powershell Core**. 
3. In the **Hosting** tab, ensure the **Consumption (Serverless)** plan type is selected.
4. Make other preferrable configuration changes, if needed, then click **Create**.

**2. Import Function App Code**

1. In the newly created Function App, select **Functions** on the left pane and click **+ Add**.
2. Select **Timer Trigger**.
3. Enter a unique Function **Name** and modify the cron schedule, if needed. The default value is set to run the Function App every 5 minutes. (Note: the Timer trigger should match the `timeInterval` value below to prevent overlapping data), click **Create**.
4. Click on **Code + Test** on the left pane. 
5. Copy the [Function App Code](https://aka.ms/sentinelcarbonblackazurefunctioncode) and paste into the Function App `run.ps1` editor.
5. Click **Save**.

**3. Configure the Function App**

1. In the Function App, select the Function App Name and select **Configuration**.
2. In the **Application settings** tab, select **+ New application setting**.
3. Add each of the following thirteen to sixteen (13-16) application settings individually, with their respective string values (case-sensitive): 
		apiId
		apiKey
		workspaceID
		workspaceKey
		uri
		timeInterval
		CarbonBlackOrgKey
		CarbonBlackLogTypes 
		s3BucketName 
		EventPrefixFolderName 
		AlertPrefixFolderName 
		AWSAccessKeyId 
		AWSSecretAccessKey 
		SIEMapiId (Optional)
		SIEMapiKey (Optional)
		logAnalyticsUri (optional) 
> - Enter the URI that corresponds to your region. The complete list of API URLs can be [found here](https://community.carbonblack.com/t5/Knowledge-Base/PSC-What-URLs-are-used-to-access-the-APIs/ta-p/67346). The `uri` value must follow the following schema: `https://<API URL>.conferdeploy.net` - There is no need to add a time suffix to the URI, the Function App will dynamically append the Time Value to the URI in the proper format.
> - Set the `timeInterval` (in minutes) to the default value of `5` to correspond to the default Timer Trigger of every `5` minutes. If the time interval needs to be modified, it is recommended to change the Function App Timer Trigger accordingly to prevent overlapping data ingestion.
> - Carbon Black requires a seperate set of API ID/Keys to ingest Notification alerts. Enter the `SIEMapiId` and `SIEMapiKey` values, if needed, or omit, if not required. 
> - Note: If using Azure Key Vault, use the`@Microsoft.KeyVault(SecretUri={Security Identifier})`schema in place of the string values. Refer to [Key Vault references documentation](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) for further details. 
> - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`
4. Once all application settings have been entered, click **Save**.

[← Back to Connectors Index](../connectors-index.md)
