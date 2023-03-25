# Cofense Triage Data Connector
* [Introduction](#Introduction)
* [Prerequisites](#Prerequisites)
* [Folders](#Folders)
* [Configuration](#Configuration)
* [Deployment](#Deployment)

## Introduction<a name="Introduction"></a>

The Cofense-Triage data connector provides the following capabilities:

1. CofenseBasedIndicatorCreator:
Get Threat Indicators from the Cofense Triage platform and create Threat Intelligence Indicators in Microsoft Sentinel.
Ingest Cofense Indicator ID and report links into custom logs table.
2. NonCofenseBasedIndicatorCreatorToCofense:
Get Non-Cofense Threat Intelligence Indicators from Microsoft Sentinel Threat Intelligence and create/update Indicators in Cofense Triage platform
3. IndicatorCreatorToDefender:
Get Cofense Triage Threat Intelligence Indicators from Microsoft Sentinel Threat Intelligence and create/update Indicators in Microsoft Defender for Endpoints.


For more details of REST APIs refer to the below two documentations:

1. Cofense API documentation:
 `https://<your-cofense-instance-name>/docs/api/v2/index.html`
2. Microsoft Threat Intelligence Indicator documentation:
 https://learn.microsoft.com/rest/api/securityinsights/preview/threat-intelligence-indicator
3. Microsoft Defender for Endpoints Indicator documentation:
https://learn.microsoft.com/microsoft-365/security/defender-endpoint/ti-indicator?view=o365-worldwide

## Prerequisites<a name="Prerequisites"></a>
To integrate with Cofense Triage make sure you have:
1. **Azure Subscription:**  Azure Subscription with owner role is required to register an application in azure active directory(AAD) and assign role of contributor to AAD application in resource group.
2. **Workspace:** read and write permissions on the workspace are required.
3. **Keys:** read permissions to shared keys for the workspace are required.[See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).
4. **Microsoft.Web/sites permissions:** Read and write permissions to Azure Functions to create a Function App is required.[See the documentation to learn more about Azure Functions](https://docs.microsoft.com/azure/azure-functions/).
5. **REST API Credentials/permissions:** **Cofense Client ID** and **Client Secret** is required. See the documentation to learn more about API on the `https://<your-cofense-instance-name>/docs/api/v2/index.html`.
6. **Microsoft Defender for Endpoints:** **Microsoft Defender for Endpoints License** is required for IndicatorCreatorToDefender function.

## Folders<a name="Folders"></a>

1. `CofenseDataConnector/` - This contains the package, requirements, ARM JSON file, connector page template JSON, and other dependencies.

2. `CofenseBasedIndicatorCreator/` - This contains the Azure function source code to ingest Cofense Triage Threat Indicators into Microsoft Sentinel Threat Intelligence indicators .

3. `NonCofenseBasedIndicatorCreatorToCofense` - This contains the Azure function source code to ingest Microsoft Sentinel Threat Intelligence indicators into Cofense Triage Threat Indicators.

4. `IndicatorCreatorToDefender` - This contains the Azure function source code to ingest Cofense Threat Indicators from  Microsoft Sentinel Threat Intelligence into Microsoft Defender for Endpoints.

5. `SharedCode` - This contains the common source code for the execution of both `CofenseBasedIndicatorCreator` and `NonCofenseBasedIndicatorCreatorToCofense` Azure functions.

## Configuration<a name="Configuration"></a>

> **NOTE**: This connector uses Azure Functions to connect to the Cofense APIs to pull its Threat Indicators and create Threat Intelligence Indicators into Microsoft Sentinel Threat Intelligence and pulls Non-Cofense Threat Intelligence Indicators from Microsoft Sentinel and create/update Threat Indicators in Cofense. Likewise, it also creates/updates Cofense Based Threat Indicators in Microsoft Defender for Endpoints. All this might result in additional indicator and data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

> **(Optional Step)** Securely store workspace and API authorization key(s) or token(s) in Azure Key Vault. Azure Key Vault provides a secure mechanism to store and retrieve key values. [Follow these instructions](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references) to use Azure Key Vault with an Azure Function App.


### STEP 1 - Registration steps for the Microsoft Azure Active Directory Application

This integration requires an App registration in the Azure portal. Follow the steps in this section to create a new Azure Active Directory application:

1. Sign in to the [Azure portal](https://portal.azure.com/).
2. Search for and select **Azure Active Directory**.
3. Under **Manage**, select **App registrations > New registration**.
4. Enter a display **Name** for your application.
5. Select **Register** to complete the initial app registration.
6. When registration finishes, the Azure portal displays the app registration's Overview pane. You see the **Application (client) ID** and **Tenant ID**. The client ID and Tenant ID is required as configuration parameters for the execution of CofenseTriage Data Connector.

> **Reference link:** [https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app)

### STEP 2 - Add a client secret for Microsoft Azure Active Directory Application

Sometimes called an application password, a client secret is a string value required for the execution of CofenseTriage Data Connector. Follow the steps in this section to create a new Client Secret:

1. In the Azure portal, in **App registrations**, select your application.
2. Select **Certificates & secrets > Client secrets > New client secret**.
3. Add a description for your client secret.
4. Select an expiration for the secret or specify a custom lifetime. Limit is 24 months.
5. Select **Add**.
6. *Record the secret's value for use in your client application code. This secret value is never displayed again after you leave this page.* The secret value is required as configuration parameter for the execution of CofenseTriage Data Connector.

> **Reference link:** [https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app#add-a-client-secret](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app#add-a-client-secret)"

### STEP 3 - Assign role of Contributor to Microsoft Azure Active Directory Application

Follow the steps in this section to assign the role:

1. In the Azure portal, Go to **Resource Group** and select your resource group.
2. Go to **Access control (IAM)** from left panel.
3. Click on **Add**, and then select **Add role assignment**.
4. Select **Contributor** as role and click on next.
5. In **Assign access to**, select `User, group, or service principal`.
6. Click on **add members** and type **your app name** that you have created and select it.
7. Now click on **Review + assign** and then again click on **Review + assign**.

> **Reference link:** [https://learn.microsoft.com/azure/role-based-access-control/role-assignments-portal](https://learn.microsoft.com/azure/role-based-access-control/role-assignments-portal)

### STEP 4 - Assign Defender Threat Indicator permissions to Microsoft Azure Active Directory Application

Follow the steps in this section to assign the permissions:

1. In the Azure portal, in **App registrations**, select **your application**.
2. To enable an app to access Defender for Endpoint indicators, assign it **'Ti.ReadWrite.All'** permission, on your application page, select **API Permissions > Add permission > APIs my organization uses >, type WindowsDefenderATP, and then select WindowsDefenderATP**.
3. Select **Application permissions > Ti.ReadWrite.All**, and then select **Add permissions**.
4. Select **Grant consent**.

> **Reference link:** [https://docs.microsoft.com/microsoft-365/security/defender-endpoint/exposed-apis-create-app-webapp?view=o365-worldwide](https://docs.microsoft.com/microsoft-365/security/defender-endpoint/exposed-apis-create-app-webapp?view=o365-worldwide)

### STEP 5 - Configuration steps for the Cofense Client ID and Client Secret

Follow the steps in this section to create/get **Cofense Client ID** and **Client Secret**:

1. Go to **Administration > API Management > Version 2 tab > Applications**
2. Click on **New Application**
3. Add the required information and click on **submit**."

## Deployment<a name="Deployment"></a>
**Choose ONE from the following two deployment options to deploy the connector and the associated Azure Function:**

> **IMPORTANT:** Before deploying the Cofense Threat Indicators data connector, have the  Workspace ID and Workspace Primary Key.

#### Option 1 - Azure Resource Manager (ARM) Template
Use this method for automated deployment of the Cofense connector.

1. Go to Microsoft Sentinel -> Data Connectors.
3. Click on the Cofense Triage Data Connector, connector page will open.
4. Click the **Deploy to Azure** button.
5. Select the preferred Subscription, Resource Group and Location.
6. Enter the below information :
    ```
     Function Name
     Workspace ID
     Workspace Key
     Cofense URL (https://<your-cofense-instance-name>/)
     Cofense Client ID
     Cofense Client Secret
     Azure Client ID
     Azure Client Secret
     Azure Tenant ID
     Azure Resource Group Name
     Azure Workspace Name
     Azure Subscription ID
     Threat Level
     Proxy Username (optional)
     Proxy Password (optional)
     Proxy URL (optional)
     Proxy Port (optional)
     Throttle Limit for Non-Cofense Indicators (optional)
     LogLevel (optional)
     Reports Table Name
     Schedule
     ```
5. Mark the checkbox labeled **I agree to the terms and conditions stated above**.
6. Click **Purchase** to deploy.

#### Option 2 - Manual Deployment of Azure Functions
Use the following step-by-step instructions to deploy the Cofense Threat Indicators data connector manually with Azure Functions (Deployment via Visual Studio Code).

**1. Deploy a Function App**

   > **NOTE:** You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

  1. Download the [Azure Function App](https://aka.ms/sentinel-CofenseThreatIndicatorsAPI-functionapp) App file. Extract archive to your local development computer.
  2. Start VS Code. Choose File in the main menu and select Open Folder.
  3. Select the top level folder from extracted files.
  4. Choose the Azure icon in the Activity bar, then in the Azure: Functions area, choose the Deploy to function app button. If you aren't already signed in, choose the Azure icon in the Activity bar, then in the Azure: Functions area, choose Sign in to Azure If you're already signed in, go to the next step.
  5. Provide the following information at the prompts:
        1. Select folder: Choose a folder from your workspace or browse to one that contains your function app.
        2. Select Subscription: Choose the subscription to use.
        3. Select Create new Function App in Azure (Don't choose the Advanced option)
        4. Enter a globally unique name for the function app: Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. CofenseXXXXX).
        5. Select a runtime: Choose Python 3.8 or above.
        6. Select a location for new resources. For better performance and lower costs choose the same region where Microsoft Sentinel is located.
  6. Deployment will begin. A notification is displayed after your function app is created and the deployment package is applied.
  7. Go to Azure Portal for the Function App configuration.



**2. Configure the Function App**

1. In the Function App, select the Function App Name and select Configuration.
2. In the Application settings tab, select + New application setting.
3. Add each of the following application settings individually, with their respective values (case-sensitive):
    ```
     Workspace ID
     Workspace Key
     Cofense URL (https://<your-cofense-instance-name>/)
     Cofense Client ID
     Cofense Client Secret
     Azure Client ID
     Azure Client Secret
     Azure Tenant ID
     Azure Resource Group Name
     Azure Workspace Name
     Azure Subscription ID
     Threat Level
     Proxy Username (optional)
     Proxy Password (optional)
     Proxy URL (optional)
     Proxy Port (optional)
     Throttle Limit for Non-Cofense Indicators (optional)
     LogLevel (optional)
     Reports Table Name
     Schedule
     logAnalyticsUri (optional)
      ```
    - Use logAnalyticsUri to override the log analytics API endpoint for dedicated cloud. For example, for public cloud, leave the value empty; for Azure GovUS cloud environment, specify the value in the following format: `https://<CustomerId>.ods.opinsights.azure.us`.
4. Once all application settings have been entered, click **Save**.
