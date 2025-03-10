 # AS-Microsoft-DCR-Log-Ingestion

Author: Accelerynt

For any technical questions, please contact info@accelerynt.com  

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Microsoft-DCR-Log-Ingestion%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Microsoft-DCR-Log-Ingestion%2Fazuredeploy.json)           

This playbook is designed for multitenant environments to facilitate Microsoft Entra and Microsoft Office log collection in Microsoft Sentinel via Data Collection Endpoints and Data Collection Rules (DCRs). Microsoft’s built-in connectors lack multitenant support, so this playbook bridges that limitation by retrieving logs from a designated tenant and integrating them into another tenant’s Sentinel workspace. It supports the following log types:
* [Microsoft Graph Sign-In Logs](https://learn.microsoft.com/en-us/graph/api/signin-get?view=graph-rest-1.0&tabs=http)
* [Microsoft Graph Audit Logs](https://learn.microsoft.com/en-us/graph/api/directoryaudit-get?view=graph-rest-1.0&tabs=http)
* [Microsoft Office Activity Logs](https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-reference)
                                                                                                                                     
![DCRLogIngestion_Demo_1](Images/DCRLogIngestion_Demo_1.png)

![DCRLogIngestion_Demo_2](Images/DCRLogIngestion_Demo_2.png)

> [!NOTE]  
> Estimated Time to Complete: 3 hours

> [!TIP]
> Required deployment variables are noted throughout. Reviewing the deployment page and filling out fields as you proceed is recommended.

#
### Requirements
                                                                                                                                     
The following items are required under the template settings during deployment: 

**Log Source**:

* **Subscription ID** - this can be found by logging into your source tenant and navigating to the [Microsoft subscriptions page](https://portal.azure.com/#view/Microsoft_Azure_Billing/SubscriptionsBladeV2).
* **Entra App Registration** - this needs to be created to send data to the DCR, with admin consent granted for "**AuditLog.Read.All**" and "**Activity.Feed.Read**". [Documentation link](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-an-app-registration).

**Log Destination**:

* **Entra App Registration** - this needs to be created to access the DCR, with the "**Monitoring Metrics Publisher**" role assigned from each DCR you create. [Documentation link](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-an-app-registration).
* **Azure Key Vault Secrets** - these will store both source and destination app registration client secrets. Documentation links: [source](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-an-app-registration-azure-key-vault-secret), [destination](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-an-azure-key-vault-secret).
* **Workspace Location** - this will need to be noted as it must be consistent in creating resources such as data collection rules and endpoints. This is the value under "**Location**" on the [Microsoft workspaces page](https://portal.azure.com/#browse/Microsoft.OperationalInsights%2Fworkspaces).
* **Data Collection Endpoints** - these will need to be created for each of the three log sources. [Documentation link](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-the-data-collection-endpoints).
* **Data Collection Rules** - these will need to be created for each of the three log sources. [Documentation link](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-the-data-collection-rules).

#
### Role Requirements

If the user that will be performing the setup and deployment steps does not have the "**Owner**" or "**Global Administrator**" role assigned in both tenants, the following additional roles may be required:

**Log Source Tenant Roles**: 

* **Privileged Role Administrator** - This role will need to be assigned to the user from Entra ID.
* **Application Administrator** - By default, any user can create an app registration. However, if this has been locked down, this role will need to be assigned from Entra ID.

**Log Destination Tenant Roles**: 

* **Key Vault Secrets Officer** - In order to create and manage secrets within the desired key vault, this role will need to be assigned to the user from the key vault access control (IAM) page.
* **User Access Administrator** - In order to add role assignments to DCRs, this role will need to be assigned to the user from the resource group.
* **Contributor** - In order to add role assignments to DCRs, this role will need to be assigned to the user from the resource group.

# 
### Setup

#### Create an App Registration

From the tenant holding the **log source** data, navigate to the Microsoft Azure Active Directory app registration page: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade

Click "**New registration**".

![DCRLogIngestion_App_Registration_1](Images/DCRLogIngestion_App_Registration_1.png)

Enter something like "**AS-Send-Logs-to-DCR**" as the name and select "**Accounts in any organizational directory**" for "**Supported account types**". All remaining fields can be left unchanged. Click "**Register**"

![DCRLogIngestion_App_Registration_2](Images/DCRLogIngestion_App_Registration_2.png)

Once the app registration is created, you will be redirected to the "**Overview**" page. Under the "**Essentials**" section, take note of the "**Application (client) ID**" and the "**Directory (tenant) ID**", as both will be needed for deployment.

![DCRLogIngestion_App_Registration_3](Images/DCRLogIngestion_App_Registration_3.png)

Next, you will need to add permissions for the app registration to call the Microsoft Graph and Office 365 API endpoints. From the left menu blade, click "**API permissions**" under the "**Manage**" section. Then, click "**Add a permission**".

![DCRLogIngestion_App_Registration_4](Images/DCRLogIngestion_App_Registration_4.png)

From the "**Select an API**" pane, click the "**Microsoft APIs**" tab and select "**Microsoft Graph**".

![DCRLogIngestion_App_Registration_5](Images/DCRLogIngestion_App_Registration_5.png)

Click "**Application permissions**", then paste "**AuditLog.Read.All**" in the search bar. Click the option matching the search, then click "**Add permission**".

![DCRLogIngestion_App_Registration_6](Images/DCRLogIngestion_App_Registration_6.png)

This process will need to be repeated for the Office 365 API. Click "**Add a permission**" once again and from the "**Select an API**" pane, click the "**Microsoft APIs**" tab and select "**Office 365 Management APIs**".

![DCRLogIngestion_App_Registration_7](Images/DCRLogIngestion_App_Registration_7.png)

Click "**Application permissions**", then paste "**ActivityFeed.Read**" in the search bar. Click the option matching the search, then click "**Add permission**".

![DCRLogIngestion_App_Registration_8](Images/DCRLogIngestion_App_Registration_8.png)

Admin consent will be needed before your app registration can use the assigned permission. Click "**Grant admin consent for (name)**".

![DCRLogIngestion_App_Registration_9](Images/DCRLogIngestion_App_Registration_9.png)

Lastly, a client secret will need to be generated for the app registration. From the left menu blade, click "**Certificates & secrets**" under the "**Manage**" section. Then, click "**New client secret**".

![DCRLogIngestion_App_Registration_10](Images/DCRLogIngestion_App_Registration_10.png)

Enter a description and select the desired expiration date, then click "**Add**".

![DCRLogIngestion_App_Registration_11](Images/DCRLogIngestion_App_Registration_11.png)

Copy the value of the secret that is generated, as this will be needed for [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-an-azure-key-vault-secret).

![DCRLogIngestion_App_Registration_12](Images/DCRLogIngestion_App_Registration_12.png)

#### Create an App Registration Azure Key Vault Secret

The secret from the previous step will need to be stored in the **log destination tenant**, as this is where the logic app will be deployed. Navigate to the Azure key vaults page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults

Navigate to an existing key vault or create a new one. From the key vault overview page, click the "**Secrets**" menu option, found under the "**Settings**" section. Click "**Generate/Import**".

![DCRLogIngestion_Key_Vault_1](Images/DCRLogIngestion_Key_Vault_1.png)

Choose a name for the secret, such as "**DCRLogIngestion-LogSourceAppRegClientSecret**", taking note of the value used, as it will be needed for deployment. Next, enter the client secret copied in the [previous section](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-an-app-registration). All other settings can be left as is. Click "**Create**". 

![DCRLogIngestion_Key_Vault_2](Images/DCRLogIngestion_Key_Vault_2.png)

#### Create the Data Collection Endpoints

From the tenant holding the **log destination** data, navigate to the Microsoft data collection endpoints page: https://portal.azure.com/#browse/microsoft.insights%2Fdatacollectionendpoints

Click "**Create**".

![DCRLogIngestion_Data_Collection_Endpoint_1](Images/DCRLogIngestion_Data_Collection_Endpoint_1.png)

Enter something like "**EntraSignInLogsDCE**" as the endpoint name and select the subscription and resource group. These should match the subscription and resource group of the playbook you will deploy later. Ensure the region matches the location of your workspace.  Click "**Review + create**".

![DCRLogIngestion_Data_Collection_Endpoint_2](Images/DCRLogIngestion_Data_Collection_Endpoint_2.png)

Click "**Create**".

![DCRLogIngestion_Data_Collection_Endpoint_3](Images/DCRLogIngestion_Data_Collection_Endpoint_3.png)

Repeat this process for "**EntraAuditLogsDCE**".

![DCRLogIngestion_Data_Collection_Endpoint_4](Images/DCRLogIngestion_Data_Collection_Endpoint_4.png)

Repeat this process for "**OfficeActivityLogsDCE**".

![DCRLogIngestion_Data_Collection_Endpoint_5](Images/DCRLogIngestion_Data_Collection_Endpoint_5.png)

From each of the created Data Collection Endpoint overview pages, take note of the "**Logs Ingestion**" URLs, as they will be needed for deployment.

![DCRLogIngestion_Data_Collection_Endpoint_6](Images/DCRLogIngestion_Data_Collection_Endpoint_6.png)

#### Create the Data Collection Rules

From the tenant holding the **log destination** data, navigate to the Microsoft Log Analytics Workspace page: https://portal.azure.com/#browse/Microsoft.OperationalInsights%2Fworkspaces

Select the desired workspace.

![DCRLogIngestion_Data_Collection_Rule_1](Images/DCRLogIngestion_Data_Collection_Rule_1.png)

From the selected workspace, navigate to "**Tables**" located under settings, click "**Create**" and select "**New custom log (DCR based)**".

![DCRLogIngestion_Data_Collection_Rule_2](Images/DCRLogIngestion_Data_Collection_Rule_2.png)

First, click "**Create a new Data Collection Rule**" below the Data Collection Rule field. Then enter something like "**EntraSignInLogsDCR**" for the name in the window that appears on the right. Ensure the Subscription, Resource Group, and Region all look correct, then click "**Done**".

![DCRLogIngestion_Data_Collection_Rule_3](Images/DCRLogIngestion_Data_Collection_Rule_3.png)

Next enter something like "**EntraSignInLogs**" as the table name and select "**EntraSignInLogsDCE**" from the drop-down list. If this option is not populating, double check the region used for the Data Collection Endpoint created in the previous step. Click "**Next**".

![DCRLogIngestion_Data_Collection_Rule_4](Images/DCRLogIngestion_Data_Collection_Rule_4.png)

The next step will prompt you for a data sample.

![DCRLogIngestion_Data_Collection_Rule_5](Images/DCRLogIngestion_Data_Collection_Rule_5.png)

Upload the file content located at [Samples/SignInLogsSample.json](https://github.com/Accelerynt-Security/AS-Microsoft-DCR-Log-Ingestion/blob/main/Samples/SignInLogsSample.json), then click "**Next**".

![DCRLogIngestion_Data_Collection_Rule_6](Images/DCRLogIngestion_Data_Collection_Rule_6.png)

Click "**Create**".

![DCRLogIngestion_Data_Collection_Rule_7](Images/DCRLogIngestion_Data_Collection_Rule_7.png)

This process will need to be repeated for "**EntraAuditLogsDCR**". After creating the "**EntraAuditLogsDCR**" Data Collection Rule in the way that was shown for "**EntraSignInLogsDCR**", enter something like "**EntraAuditLogs**" as the table name and select "**EntraAuditLogsDCE**" from the drop-down list.

![DCRLogIngestion_Data_Collection_Rule_8](Images/DCRLogIngestion_Data_Collection_Rule_8.png)

Upload the file content located at [Samples/AuditLogsSample.json](https://github.com/Accelerynt-Security/AS-Microsoft-DCR-Log-Ingestion/blob/main/Samples/AuditLogsSample.json), then click "**Next**".

![DCRLogIngestion_Data_Collection_Rule_9](Images/DCRLogIngestion_Data_Collection_Rule_9.png)

Click "**Create**".

![DCRLogIngestion_Data_Collection_Rule_10](Images/DCRLogIngestion_Data_Collection_Rule_10.png)

This process will need to be repeated for "**OfficeActivityLogsDCR**". After creating the "**OfficeActivityLogsDCR**" Data Collection Rule in the way that was shown for “**EntraSignInLogsDCR**", enter something like "**OfficeActivityLogs**" as the table name and select "**OfficeActivityLogsDCE**" from the drop down list.

![DCRLogIngestion_Data_Collection_Rule_11](Images/DCRLogIngestion_Data_Collection_Rule_11.png)

Upload the file content located at [Samples/OfficeActivityLogsSample.json](https://github.com/Accelerynt-Security/AS-Microsoft-DCR-Log-Ingestion/blob/main/Samples/O365GeneralAuditLogsSample.json), then click "**Next**".

![DCRLogIngestion_Data_Collection_Rule_12](Images/DCRLogIngestion_Data_Collection_Rule_12.png)

Click "**Create**".

![DCRLogIngestion_Data_Collection_Rule_13](Images/DCRLogIngestion_Data_Collection_Rule_13.png)

From each of the created [Data Collection Rule overview pages](https://portal.azure.com/#browse/microsoft.insights%2Fdatacollectionrules), take note of the "**Immutable ID**" values, as they will be needed for deployment.

![DCRLogIngestion_Data_Collection_Rule_14](Images/DCRLogIngestion_Data_Collection_Rule_14.png)

Lastly, from each of the created Data Collection Rule data sources pages, take note of the "**Data source**" values, as they will be needed for deployment.

![DCRLogIngestion_Data_Collection_Rule_15](Images/DCRLogIngestion_Data_Collection_Rule_15.png)

#### Create an App Registration for the DCRs

From the tenant holding the **log destination** data, navigate to the Microsoft Azure Active Directory app registration page: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade

Click "**New registration**".

![DCRLogIngestion_App_Registration_DCR_1](Images/DCRLogIngestion_App_Registration_DCR_1.png)

Enter something like "**DCRLogIngestionAppReg**" for the name and select "**Accounts in this organizational directory only**" for "**Supported account types**. All remaining fields can be left unchanged. Click "**Register**"

![DCRLogIngestion_App_Registration_DCR_2](Images/DCRLogIngestion_App_Registration_DCR_2.png)

Once the app registration is created, you will be redirected to the "**Overview**" page. Under the "**Essentials**" section, take note of the "**Application (client) ID**", as this will be needed for deployment.

![DCRLogIngestion_App_Registration_DCR_3](Images/DCRLogIngestion_App_Registration_DCR_3.png)

A client secret will need to be generated for the app registration. From the left menu blade, click "**Certificates & secrets**" under the "**Manage**" section. Then, click "**New client secret**”. Enter a description and select the desired expiration date, then click "**Add**".

![DCRLogIngestion_App_Registration_DCR_4](Images/DCRLogIngestion_App_Registration_DCR_4.png)

Copy the value of the secret that is generated, as this will be needed for [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-an-azure-key-vault-secret).

![DCRLogIngestion_App_Registration_DCR_5](Images/DCRLogIngestion_App_Registration_DCR_5.png)

Next, IAM access for this app registration will need to be added from each of the DCRs created in the previous step. Navigate to the data collection rules page: https://portal.azure.com/#browse/microsoft.insights%2Fdatacollectionrules

Select the "**EntraSignInLogsDCR**" and select "**Access control (IAM)**". Click "**Add**" and select "**Add role assignment**".

![DCRLogIngestion_App_Registration_DCR_6](Images/DCRLogIngestion_App_Registration_DCR_6.png)

Select "**Monitoring Metrics Publisher**" and click "**Next**".

![DCRLogIngestion_App_Registration_DCR_7](Images/DCRLogIngestion_App_Registration_DCR_7.png)

Select "**User, group, or service principal**" as the access option, then click "**Select members**". Paste "**DCRLogIngestionAppReg**" into the search bar at the top of the right pane and select the app registration that appears, then click "**Select**".

![DCRLogIngestion_App_Registration_DCR_8](Images/DCRLogIngestion_App_Registration_DCR_8.png)

Click "**Review + assign**".

![DCRLogIngestion_App_Registration_DCR_9](Images/DCRLogIngestion_App_Registration_DCR_9.png)

Repeat this process for the "**EntraAuditLogsDCR**".

![DCRLogIngestion_App_Registration_DCR_10](Images/DCRLogIngestion_App_Registration_DCR_10.png)

Lastly, repeat this process for "**OfficeActivityLogsDCR**".

![DCRLogIngestion_App_Registration_DCR_11](Images/DCRLogIngestion_App_Registration_DCR_11.png)

#### Create a Log Destination App Registration Azure Key Vault Secret

As before, the secret from the previous step will need to be stored in the **log destination tenant**. Navigate to the Azure key vaults page: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults

Navigate to an existing key vault or create a new one. From the key vault overview page, click the "**Secrets**" menu option, found under the "**Settings**" section. Click "**Generate/Import**".

![DCRLogIngestion_Receiving_Key_Vault_1](Images/DCRLogIngestion_Receiving_Key_Vault_1.png)

Choose a name for the secret, such as "**DCRLogIngestion-Log-DestinationAppRegClientSecret**", taking note of the value used, as it will be needed for deployment. Next, enter the client secret copied in the [previous section](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-an-app-registration). All remaining fields can be left unchanged. Click "**Create**". 

![DCRLogIngestion_Receiving_Key_Vault_2](Images/DCRLogIngestion_Receiving_Key_Vault_2.png)

#
### Deployment

To configure and deploy this playbook:
 
Open your browser and ensure you are logged into your Microsoft Sentinel workspace From the tenant holding the **log destination** data. In a separate tab, open the link to our playbook on the Accelerynt Security GitHub repository:

https://github.com/Accelerynt-Security/AS-Microsoft-DCR-Log-Ingestion

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Microsoft-DCR-Log-Ingestion%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-Microsoft-DCR-Log-Ingestion%2Fazuredeploy.json)                                                  

Click the "**Deploy to Azure**" button at the bottom and it will bring you to the custom deployment template.

In the **Project Details** section:

* Select the "**Subscription**" and "**Resource Group**" from the dropdown boxes you would like the playbook deployed to.  

In the **Instance Details** section:

* **Playbook Name**: This can be left as "**AS-Microsoft-DCR-Log-Ingestion**" or you may change it.

* **Log Source App Registration Tenant ID**: Enter the Directory (tenant) ID of the app registration that will be used to access the log source data, referenced in [Create an App Registration](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-an-app-registration).

* **Log Source App Registration Client ID**: Enter the Application (client) ID of the app registration that will be used to access the log source data, referenced in [Create an App Registration](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-an-app-registration).

* **Log Source Tenant Subscription ID**: Enter the [subscription ID](https://portal.azure.com/#view/Microsoft_Azure_Billing/SubscriptionsBladeV2) of the tenant holding the log source data.

* **Log Destination App Registration Client ID**: Enter the Application (client) ID of the app registration that will be used to store the log destination data, referenced in [Create an App Registration for the DCRs](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-an-app-registration-for-the-dcrs).

* **Key Vault Name**: Enter the name of the key vault referenced in [Create an Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-an-azure-key-vault-secret).

* **Log Source App Registration Key Vault Secret Name**: Name of key vault secret that contains the log source app registration client secret, created in [Create an App Registration Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-an-app-registration-azure-key-vault-secret).

* **Log Destination App Registration Key Vault Secret Name**: Name of key vault secret that contains the log destination app registration client secret, created in [Create a Log Destination App Registration Azure Key Vault Secret](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-a-log-destination-app-registration-azure-key-vault-secret).

* **Entra Sign In Logs Ingestion URL**: Enter the logs ingestion URL from the EntraSignInLogs DCE, referenced in [Create the Data Collection Endpoints](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-the-data-collection-endpoints).

* **Entra Sign In Logs Immutable ID**: Enter the logs ingestion immutable ID from the EntraSignInLogs DCR, referenced in [Create the Data Collection Rules](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-the-data-collection-rules).

* **Entra Sign In Logs Data Source**: Enter the logs ingestion data source from the EntraSignInLogs DCR, referenced in [Create the Data Collection Rules](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-the-data-collection-rules).

* **Entra Audit Logs Ingestion URL**: Enter the logs ingestion URL from the EntraAuditLogs DCE, referenced in [Create the Data Collection Endpoints](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-the-data-collection-endpoints).

* **Entra Audit Logs Immutable ID**: Enter the logs ingestion immutable ID from the EntraAuditLogs DCR, referenced in [Create the Data Collection Rules](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-the-data-collection-rules).

* **Entra Audit Logs Data Source**: Enter the logs ingestion data source from the EntraAuditLogs DCR, referenced in [Create the Data Collection Rules](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-the-data-collection-rules).

* **Office Activity Ingestion URL**: Enter the logs ingestion URL from the OfficeActivityLogs DCE, referenced in [Create the Data Collection Endpoints](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-the-data-collection-endpoints).

* **Office Activity Immutable ID**: Enter the logs ingestion immutable ID from the OfficeActivityLogs DCR, referenced in [Create the Data Collection Rules](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-the-data-collection-rules).

* **Office Activity Data Source**: Enter the logs ingestion data source from the OfficeActivityLogs DCR, referenced in [Create the Data Collection Rules](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-the-data-collection-rules).

Towards the bottom, click on "**Review + create**". 

![DCRLogIngestion_Deploy_1](Images/DCRLogIngestion_Deploy_1.png)

Once the resources have validated, click on "**Create**".

![DCRLogIngestion_Deploy_2](Images/DCRLogIngestion_Deploy_2.png)

The resources should take around a minute to deploy. Once the deployment is complete, you can expand the "**Deployment details**" section to view them.
Click the one corresponding to the Logic App.

![DCRLogIngestion_Deploy_3](Images/DCRLogIngestion_Deploy_3.png)

#
### Granting Access to Azure Key Vault

Before the Logic App can run successfully, the key vault connection created during deployment must be granted access to the key vault storing your app registration client secrets, located in the **log destination tenant**.

From the Logic App menu blade, select the "**Identity**" tab, located under the "**Settings**" section. Click "**Azure role assignments**".

![DCRLogIngestion_Key_Vault_Access_1](Images/DCRLogIngestion_Key_Vault_Access_1.png)

Click "**Add role assignment**" then select "**Key Vault**" as the scope, select your key vault name, then select "**Key Vault Secrets User**" for the role. Click "**Save**".

![DCRLogIngestion_Key_Vault_Access_2](Images/DCRLogIngestion_Key_Vault_Access_2.png)

#
### Ensuring your Subscription is Enabled

To ensure the subscription is enabled for the app registration used to access the "**O365 Audit General Logs**", the [OfficeAuditSubscriptionEnable](https://github.com/Accelerynt-Security/AS-Microsoft-DCR-Log-Ingestion/blob/main/Scripts/OfficeAuditSubscriptionEnable.ps1) should be run from an [Azure Cloud Shell Window](https://learn.microsoft.com/en-us/azure/cloud-shell/new-ui-shell-window) From the tenant holding the **log source** data.

![DCRLogIngestion_Azure_Cloud_Shell_1](Images/DCRLogIngestion_Azure_Cloud_Shell_1.png)

Click the "**PowerShell**" option, then select the appropriate subscription for the log source tenant.

![DCRLogIngestion_Azure_Cloud_Shell_2](Images/DCRLogIngestion_Azure_Cloud_Shell_2.png)

Copy and paste the script into the Azure Cloud Shell PowerShell window and hit enter. You will be prompted to enter your **log source** tenant, as well as the **log source** app registration client ID and client secret.

![DCRLogIngestion_Azure_Cloud_Shell_3](Images/DCRLogIngestion_Azure_Cloud_Shell_3.png)

You should see a status of "**enabled**" once the script runs successfully.

![DCRLogIngestion_Azure_Cloud_Shell_4](Images/DCRLogIngestion_Azure_Cloud_Shell_4.png)

#
### Enable the Logic App

After all of the above steps are completed, from the Logic App Overview page, click "**Enable**".

![DCRLogIngestion_Logic_App_Enable_1](Images/DCRLogIngestion_Logic_App_Enable_1.png)

Once the playbook has run successfully, navigate to https://portal.azure.com/#browse/microsoft.securityinsightsarg%2Fsentinel in your log destination tenant.
Select the corresponding workspace and navigate to "**Logs**". 
From there, the tables you created in the [Create the Data Collection Endpoints section](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/AS-Microsoft-DCR-Log-Ingestion#create-the-data-collection-endpoints) can be queried to verify that the data is flowing to your log destination tenant properly.

![DCRLogIngestion_Logic_App_Enable_2](Images/DCRLogIngestion_Logic_App_Enable_2.png)
