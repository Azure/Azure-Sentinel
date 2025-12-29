# Okta Single Sign-On

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `OktaSSO` |
| **Publisher** | Okta |
| **Used in Solutions** | [Okta Single Sign-On](../solutions/okta-single-sign-on.md) |
| **Collection Method** | Azure Function |
| **Connector Definition Files** | [Connector_REST_API_FunctionApp_Okta.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta%20Single%20Sign-On/Data%20Connectors/OktaSingleSign-On/Connector_REST_API_FunctionApp_Okta.json) |

The [Okta Single Sign-On (SSO)](https://www.okta.com/products/single-sign-on/) connector provides the capability to ingest audit and event logs from the Okta API into Microsoft Sentinel. The connector provides visibility into these log types in Microsoft Sentinel to view dashboards, create custom alerts, and to improve monitoring and investigation capabilities.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`Okta_CL`](../tables/okta-cl.md) | — | — |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **Okta API Token**: An Okta API Token is required. See the documentation to learn more about the [Okta System Log API](https://developer.okta.com/docs/reference/api/system-log/).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to Okta SSO to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**NOTE:** This connector has been updated, if you have previously deployed an earlier version, and want to update, please delete the existing Okta Azure Function before redeploying this version.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**STEP 1 - Configuration steps for the Okta SSO API**

 [Follow these instructions](https://developer.okta.com/docs/guides/create-an-api-token/create-the-token/) to create an API Token.

**Note** - For more information on the rate limit restrictions enforced by Okta, please refer to the **[documentation](https://developer.okta.com/docs/reference/rl-global-mgmt/)**.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Okta SSO connector, have the Workspace ID and Workspace Primary Key (can be copied from the following), as well as the Okta SSO API Authorization Token, readily available.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**Option 1 - Azure Resource Manager (ARM) Template**

  This method provides an automated deployment of the Okta SSO connector using an ARM Tempate.

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentineloktaazuredeployv2-solution)  [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/sentineloktaazuredeployv2-solution-gov)
2. Select the preferred **Subscription**, **Resource Group** and **Location**. 
3. Enter the **Workspace ID**, **Workspace Key**, **API Token** and **URI**. 
 - Use the following schema for the `uri` value: `https://<OktaDomain>/api/v1/logs?since=` Replace `<OktaDomain>` with your domain. [Click here](https://developer.okta.com/docs/reference/api-overview/#url-namespace) for further details on how to identify your Okta domain namespace. There is no need to add a time value to the URI, the Function App will dynamically append the inital start time of logs to UTC 0:00 for the current UTC date as time value to the URI in the proper format. 
 - Note: If using Azure Key Vault secrets for any of the values above, use the`@Microsoft.KeyVault(SecretUri={Security Identifier})`schema in place of the string values. Refer to [Key Vault references documentation](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) for further details. 
4. Mark the checkbox labeled **I agree to the terms and conditions stated above**. 
5. Click **Purchase** to deploy.

  **Option 2 - Manual Deployment of Azure Functions**

  Use the following step-by-step instructions to deploy the Okta SSO connector manually with Azure Functions (Deployment via Visual Studio Code).
**Step 1 - Deploy a Function App**

    1. Download the [Azure Function App](https://aka.ms/sentineloktaazurefunctioncodev2) file. Extract archive to your local development computer.
2. Follow the [function app manual deployment instructions](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/AzureFunctionsManualDeployment.md#function-app-manual-deployment-instructions) to deploy the Azure Functions app using VSCode.
3. After successful deployment of the function app, follow next steps for configuring it.

    **Step 2 - Configure the Function App**

    1. Go to Azure Portal for the Function App configuration.
2. In the Function App, select the Function App Name and select **Configuration**.
3. In the **Application settings** tab, select **+ New application setting**.
4. Add each of the following five (5) application settings individually, with their respective string values (case-sensitive): 
		apiToken
		workspaceID
		workspaceKey
		uri
		logAnalyticsUri (optional)
 - Use the following schema for the `uri` value: `https://<OktaDomain>/api/v1/logs?since=` Replace `<OktaDomain>` with your domain. [Click here](https://developer.okta.com/docs/reference/api-overview/#url-namespace) for further details on how to identify your Okta domain namespace. There is no need to add a time value to the URI, the Function App will dynamically append the inital start time of logs to UTC 0:00 for the current UTC date as time value to the URI in the proper format.
 - Note: If using Azure Key Vault secrets for any of the values above, use the`@Microsoft.KeyVault(SecretUri={Security Identifier})`schema in place of the string values. Refer to [Key Vault references documentation](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) for further details.
 - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: https://<CustomerId>.ods.opinsights.azure.us. 
5. Once all application settings have been entered, click **Save**.

## Additional Documentation

> 📄 *Source: [Okta Single Sign-On\Data Connectors\OktaSingleSign-On\CHANGELOG.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Okta Single Sign-On\Data Connectors\OktaSingleSign-On\CHANGELOG.md)*

## 2.1.1
- Moved version 2.1.0 to sub folder AzureFunctionOktaSSO_V2 under Azure-Sentinel/DataConnectors/Okta Single Sign-On/
- Created V2 versions of Azure Deploy and Connector Json files to enable both versions to co-exist
- Changed zip file reference to use 'https://aka.ms/sentineloktaazuredeployv2' in Azure Deploy json file
- Changed run.ps1 reference to use 'https://aka.ms/sentineloktaazurefunctioncodev2' in Connector json file

## 2.1.0
- Modified Okta Event log tracking to use next URI link from header
- Fixed Total record counter to record correctly the total number of records ingested

## 2.0.2
- Added  ACN_CD_OktaIssue925 resolution to add domain to output records

## 2.0.1
- Added CHANGELOG.md to track future code changes
- Complete rewrite of Azure Function code to address the following
    - Code needs to loop requests to Okta as each response from Okta is limited to max of 1000 records
    - relying on Timetrigger time minus (-) 5 minutes is unreliable and may result in duplicates and missing records
    - Okta communicates via HTTP Headers details about log event pagination orginal version did not utilise this information
- Added using a table on Azure Storage account of function to maintain state of latest event time provided in OKTA Response 
- Added logic to use OKTA time detials in records to track last record returned from OKTA
- Added Loop to continue getting paged results from OKTA until either all records retrieved or getting close (260 seconds) to Azure Function default timeout (300 seconds)
- Added dependency on Powershell modules 'AZTable' and 'Az.OperationalInsights'
- Fixed Timestamp to corret field from OKTA "published" field for Azure Log Analytics Time Generated header in Post HTTP
- Fixed HTTP Request to OKTA, we need the Headers and 'Invoke-RestMethod' won't provide them
- Fixed HTTP request to OKTA to use limit, since and after parameters to make sure we get all records and also don't get duplicates
- Removed need for Environment setting of 'TimeTrigger' Function is now self managing event log times
- Cleanup of Azure Function Log messages, consistent format of output
- Added inline comments to explain code logic

## 1.1
- Added Hardcoded table name

[← Back to Connectors Index](../connectors-index.md)
