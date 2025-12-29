# Transmit Security Connector

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `TransmitSecurity` |
| **Publisher** | TransmitSecurity |
| **Used in Solutions** | [TransmitSecurity](../solutions/transmitsecurity.md) |
| **Collection Method** | Azure Function |
| **Connector Definition Files** | [TransmitSecurity_API_FunctionApp.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TransmitSecurity/Data%20Connectors/TransmitSecurity_API_FunctionApp.JSON) |

The [Transmit Security] data connector provides the capability to ingest common Transmit Security API events into Microsoft Sentinel through the REST API. [Refer to API documentation for more information](https://developer.transmitsecurity.com/). The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`TransmitSecurityActivity_CL`](../tables/transmitsecurityactivity-cl.md) | — | — |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Microsoft.Web/sites permissions**: Read and write permissions to Azure Functions to create a Function App is required. [See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
- **REST API Client ID**: **TransmitSecurityClientID** is required. See the documentation to learn more about API on the `https://developer.transmitsecurity.com/`.
- **REST API Client Secret**: **TransmitSecurityClientSecret** is required. See the documentation to learn more about API on the `https://developer.transmitsecurity.com/`.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This connector uses Azure Functions to connect to the Transmit Security API to pull its logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

>**(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.

**STEP 1 - Configuration steps for the Transmit Security API**

Follow the instructions to obtain the credentials.

1. Log in to the Transmit Security Portal.
2. Configure a [management app](https://developer.transmitsecurity.com/guides/user/management_apps/). Give the app a suitable name, for example, MyAzureSentinelCollector.
3. Save credentials of the new user for using in the data connector.

**STEP 2 - Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function**

>**IMPORTANT:** Before deploying the Transmit Security data connector, have the Workspace ID and Workspace Primary Key (can be copied from the following).
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Option 1 - Azure Resource Manager (ARM) Template**

Use this method for automated deployment of the Transmit Security data connector using an ARM Template.

1. Click the **Deploy to Azure** button below.

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-TransmitSecurityAPI-azuredeploy) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/sentinel-TransmitSecurityAPI-azuredeploy-gov)

2. Select the preferred **Subscription**, **Resource Group**, and **Location**.

> **NOTE:** Within the same resource group, you can't mix Windows and Linux apps in the same region. Select an existing resource group without Windows apps in it or create a new resource group.

3. Enter the **TransmitSecurityClientID**, **TransmitSecurityClientSecret**, **TransmitSecurityPullEndpoint**, **TransmitSecurityTokenEndpoint**, and deploy.

4. Mark the checkbox labeled **I agree to the terms and conditions stated above**.

5. Click **Purchase** to deploy.

**4. Option 2 - Manual Deployment of Azure Functions**

Use the following step-by-step instructions to deploy the Transmit Security data connector manually with Azure Functions (Deployment via Visual Studio Code).

**1. Deploy a Function App**

> **NOTE:** You will need to [prepare VS Code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

1. Download the [Azure Function App](https://aka.ms/sentinel-TransmitSecurityAPI-functionapp) file. Extract the archive to your local development computer.

2. Start VS Code. Choose **File** in the main menu and select **Open Folder**.

3. Select the top-level folder from the extracted files.

4. Choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose the **Deploy to function app** button.

   If you aren't already signed in, choose the Azure icon in the Activity bar, then in the **Azure: Functions** area, choose **Sign in to Azure**.

   If you're already signed in, go to the next step.

5. Provide the following information at the prompts:

   a. **Select folder:** Choose a folder from your workspace or browse to one that contains your function app.

   b. **Select Subscription:** Choose the subscription to use.

   c. Select **Create new Function App in Azure** (Don't choose the Advanced option).

   d. **Enter a globally unique name for the function app:** Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions.

   e. **Select a runtime:** Choose Python 3.11.

   f. Select a location for new resources. For better performance and lower costs, choose the same [region](https://azure.microsoft.com/regions/) where Microsoft Sentinel is located.

6. Deployment will begin. A notification is displayed after your function app is created and the deployment package is applied.

7. Go to the Azure Portal for the Function App configuration.

**2. Configure the Function App**

1. In the Function App, select the Function App Name and select **Configuration**.

2. Select **Environment variables**.

3. Add each of the following application settings individually, with their respective string values (case-sensitive):

   - **TransmitSecurityClientID**
   - **TransmitSecurityClientSecret**
   - **TransmitSecurityPullEndpoint**
   - **TransmitSecurityTokenEndpoint**
   - **WorkspaceID**
   - **WorkspaceKey**
   - **logAnalyticsUri** (optional)

   > - Use **logAnalyticsUri** to override the log analytics API endpoint for a dedicated cloud. For example, for the public cloud, leave the value empty; for the Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`.

4. Once all application settings have been entered, click **Apply**.

## Additional Documentation

> 📄 *Source: [TransmitSecurity\Data Connectors\readme.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TransmitSecurity\Data Connectors\readme.md)*

# Transmit Security Integration for Microsoft Sentinel

## Introduction

This folder contains the Azure Function Time Trigger code for the Transmit Security-Microsoft Sentinel connector. The connector will run periodically and ingest Transmit Security data into the Microsoft Sentinel logs custom table `TransmitSecurityActivity_CL`.

## Folders

1. **TransmitSecurity/** - Contains the package, requirements, ARM JSON file, connector page template JSON, and other dependencies.
2. **TransmitSecurityConnector/** - Contains the Azure Function source code along with sample data.

## Installing for Users

After the solution is published, you can find the connector in the connector gallery of Microsoft Sentinel among other connectors in the Data Connectors section.

1. Go to **Microsoft Sentinel** -> **Data Connectors**.
2. Click on the **Transmit Security connector**; the connector page will open.
3. Click on the blue **Deploy to Azure** button.

This will lead to a custom deployment page where, after entering accurate credentials and other information, the resources will be created.

The connector should start ingesting data into the logs within the next 10-15 minutes.

## Installing for Testing

1. Log in to the Azure portal using the URL - [https://aka.ms/sentineldataconnectorvalidateurl](https://aka.ms/sentineldataconnectorvalidateurl).
2. Go to **Microsoft Sentinel** -> **Data Connectors**.
3. Click the **Import** button at the top and select the JSON file `TransmitSecurity_API_FunctionApp.JSON` downloaded on your local machine from GitHub.
4. This will load the connector page; the rest of the process will be the same as the **Installing for Users** guideline above.

## Monitoring the Function

Each invocation and its logs of the function can be seen in the Function App service of Azure, available in the Azure Portal outside Microsoft Sentinel.

1. Go to **Function App** and click on the function you have deployed, identified by the name given at the deployment stage.
2. Go to **Functions** -> **TransmitSecurityConnector** -> **Monitor**.
3. By clicking on the invocation time, you can see all the logs for that run.

**Note:** For more detailed logs, check Application Insights of the function. You can search the logs by operation ID in the Transaction search section.

[← Back to Connectors Index](../connectors-index.md)
