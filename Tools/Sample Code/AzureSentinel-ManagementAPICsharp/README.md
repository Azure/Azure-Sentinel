# Azure Sentinel Management API C# Sample
Author: Chi Nguyen

## Description
This repo contains a C# .NET Core 3.1 console application to demonstrate how you can leverage the Azure Sentinel Management API to programmatically manage your Azure Sentinel workspace(s).

The application uses OAuth 2.0 client credentials flow on Microsoft Identity Platform for authentication. Essentially, the flow permits the application to use its own credentials, instead of impersonating a user, to authenticate when calling the Azure Sentinel API. Please refer to [OAuth 2.0 client credentials flow](https://docs.microsoft.com/azure/active-directory/develop/v2-oauth2-client-creds-grant-flow) for more details on the authentication mechanism.

What can you use this solution for? 
1. For starters, it serves as a quickstart to help you set up a custom application to call the Azure Sentinel REST API to automate your management tasks on Azure Sentinel. Some examples include importing and exporting analytic rules, disable and enable an analytic rules, updating multiple incidents at once across workspaces, and many other use cases. The app can handle multiple Azure Sentinel workspaces cross-tenant at once, so if you manage multiple workspaces for multiple clients as a MSSP, this can be a solution.
2. Additionally, the solution can be combined and integrated with other tools within your organization to achieve a more comprehensive security solution.

Please refer to the documentation and specs below for more details on Azure Sentinel API.
* [Sentinel API documentation](https://docs.microsoft.com/rest/api/securityinsights/)
* [Saved Searches/Hunting queries API documentation](https://docs.microsoft.com/rest/api/loganalytics/savedsearches)
* [Sentinel API specs - Stable: 2020-01-01 version](https://github.com/Azure/azure-rest-api-specs/blob/master/specification/securityinsights/resource-manager/Microsoft.SecurityInsights/stable/2020-01-01/SecurityInsights.json)
* [Sentinel API specs - Preview: 2019-01-01 version](https://github.com/Azure/azure-rest-api-specs/blob/master/specification/securityinsights/resource-manager/Microsoft.SecurityInsights/preview/2019-01-01-preview/SecurityInsights.json)

This sample provides examples of the following Sentinel API operation groups.

| Entity | Operation | API version | 
| -----------|-----------|--------|
| Alert Rule | Get, Create, Update, Delete | Stable |
| Alert Rule Templates | Get | Stable |
| Data Connector | Get, Create, Delete | Stable |
| Incidents | Get, Create, Update, Delete | Stable|
| Incident Comments | Get, Create | Stable |
| Incident Relation | Get, Create, Update, Delete | Preview |
| Bookmarks | Get, Create, Delete | Stable|
| Playbooks | Get, Create, Delete| Stable|
| Hunting Queries | Get, Create, Update, Delete | Stable |


## Prerequisites
To configure the tool, the following assembly is required to authenticate and make requests to the Azure Sentinel Management API.

### _Azure Sentinel_
1. **Active Azure Subscription**, if you don't have one, create a [free account](https://azure.microsoft.com/free/?WT.mc_id=A261C142F) before you begin.

2. **Log Analytics workspace**. If you don't have one, [create a Log Analytics workspace](https://docs.microsoft.com/azure/azure-monitor/learn/quick-create-workspace).

3. Obtain **WorkSpaceId** and **WorkspaceKey** following these steps. Copy this workspace Id and Key as you will need them later to run the application.
   1. In the Azure portal, search for and select **Log Analytics workspaces**
   1. In your list of Log Analytics workspaces, select the workspace you intend on configuring the agent to report to.
   1. Select **Advanced Settings**.

4. To enable Azure Sentinel, you need **Contributor** permissions to the subscription in which the Azure Sentinel workspace resides. Learn more to [onboard Azure Sentinel](https://docs.microsoft.com/azure/sentinel/quickstart-onboard#enable-azure-sentinel-).

5. To use Azure Sentinel, you need either **contributor** or **reader** permissions on the resource group that the workspace belongs to.

### _AAD Application Registration_
To configure the sample, you'll need to register a new Azure Active Directory application (Service Principal) in the Microsoft [Application Registration Portal](https://portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/RegisteredApps).
Follow these steps to register a new application:
1. Sign in to the [Application Registration Portal](https://portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/RegisteredApps) using either your personal or work or school account.

2. Choose **New registration**.

3. Enter an application name, and choose **Register**.

4. Open the **Overview** page of your app. Copy and save the **Application Id** field. You will need it later to complete the configuration process.

5. Under **Certificates & secrets**, choose **New client secret** and add a quick description. A new secret will be displayed in the **Value** column. Copy this password. You will need it later to complete the configuration process and it will not be shown again.

### _Permissions_
 Adhering to the principle of least privilege, always grant the lowest possible permissions required to your API. 

1.  Azure Sentinel permissions
    1. To access your Azure Sentinel workspace, your app needs **Sentinel Contributor / Azure Sentinel Responder / Azure Sentinel Reader**” permissions. If you have multiple Azure Sentinel workspaces, repeat these steps for each of the workspaces.
        1. In the Resource Group where Azure Sentinel has been built, open **Access Control (IAM)** setting.
        2. Select **Add a role assignment**.
        3. Under **Role** search box, search for and select one of the roles above.
        4. Under **Select** search box, search for your app name and select it.
        5. Select **Save** to finish the role assignment.

        ![Azure Sentinel permission](./Images/AzureSentinel-permission.png)
2. Logic Apps permissions
    1. To get/enable/disable a security playbook associated with an analytic rule, your app needs **Logic App Contributor / Logic App Operator** permission. If you have multiple Azure Sentinel workspaces, repeat these steps for each of the workspaces.
         1. In the Resource Group where Azure Sentinel has been built, open **Access Control (IAM)** setting.
        2. Select **Add a role assignment**.
        3. Under **Role** search box, search for and select one of the roles above.
        4. Under **Select** search box, search for your app name and select it.
        5. Select **Save** to finish the role assignment.
        
        ![Logic Apps permission](./Images/LogicApp-permission.png)

3. If you have Azure Sentinel workspaces in multiple tenants, then follow these additional steps to grant other tenants access to your app.
    1. Provide your Administrator your **Application Id** that you get in the previous steps. Your organization’s Admin (or other user authorized to grant consent for organizational resources) is required to grant consent to the application.
    
    2. As the tenant Admin for your organization, open a browser window and craft the following URL in the address bar. Make sure to replace APPLICATION_ID with the **application Id** of your app, then select **Accept**.
    ```https://login.microsoftonline.com/common/adminconsent?client_id=APPLICATION_ID```

    3. After logging in, the tenant Admin will be presented with a dialog like the following (depending on which permissions the application is requesting):
    
        ![Scope consent dialog](./Images/admin-consent.png)

    4. When the tenant Admin agrees to this dialog, he/she is granting consent for all users of their organization to use this application. If a message like the following screenshot appears, then ignore it. That is expected for a daemon app without a Redirect URI.
        
        ![After admin consent dialog](./Images/After-consent.png)

### _Azure Key Vault_
Although Azure Key Vault is an optional component, we highly recommend it.
TODO: Wire up Azure Key Vault to manage application and Azure Sentinel credentials in this solution.

## Setup

1. Create a new folder called **Samples** in your local machine.
2. Open a command prompt.
3. In the command prompt, navigate to this **Samples** folder. Clone Azure Sentinel repository to the folder by running this command: git clone https://github.com/Azure/Azure-Sentinel.git
4. In explorer, navigate to the cloned repo, then navigate to the **Tools** directory, select **Sample Code**. Then in **AzureSentinel-ManagementAPICsharp** folder, open **AzureSentinel_ManagementAPI.sln** in Visual Studio 2017 or later.
5. Install necessary dependencies: In Visual Studio, right click the **AzureSentinel_ManagementAPI** solution, then select **Restore NuGet Packages**.
6. Open **Appsettings.json** file, fill in the values of the following variables using the information you've saved from the [Prerequisites](#Prerequisites) section.
    1. **InstanceName**: a name of your choice for your Azure Sentinel.
    2. **TenantId**: ID value of your tenant where your app resides.
    3. **AppId**: your application ID.
    4. **AppSecret**: your application secret.
    5. **SubscriptionId**: ID value of your subscription where your app resides.
    6. **ResourceGroupName**: name of your resource group where you've granted Azure Sentinel and Logic Apps permissions to your app.
    7. **WorkspaceName**: name of your Azure Sentinel workspace.
    8. **FilterQuery**: customize the filter clause to your needs. In the following example, I filter incidents by incident **LastModifiedDateTime**, **Status**, and an analyst who the incident's assigned to.
    9. Repeat step 1-8 above if you have multiple Azure Sentinel instances.

        ```
        "Instances": [
            {
                "InstanceName": "<enter_your_AzureSentinel_instance_name>",
                "TenantId": "<enter_your_tenantID>",
                "AppId": "<enter_your_appID>",
                "AppSecret": "<enter_your_appSecret>",
                "SubscriptionId": "<enter_your_subscriptionID>",
                "ResourceGroupName": "<enter_your_resourcegroup_name>",
                "WorkspaceName": "<enter_your_AzureSentinel_workspace_name>",
                "ApiVersion": "2020-01-01",
                "PreviewApiVersion": "2019-01-01-preview",
                "FilterQuery": "&$filter=properties/lastModifiedTimeUtc gt 2020-08-10T07:00:00.000000Z and properties/status eq 'Active' and properties/owner/assignedTo eq 'analyst@contoso.com'",
                "UrlTemplate": "https://management.azure.com/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.OperationalInsights/workspaces/{2}/providers/Microsoft.SecurityInsights"
            },
        ```

## Run The Application
Follow these steps to run the application in Visual Studio.

1. The **Templates** folder contains templates of the request body or payload for **CREATE/UPDATE** API requests in json format. Modify the payload for each entity you'd like to make a request. For example, **IncidentPayload.json** file is where you can edit your payload you'd like to send when making for CreateIncidents request.
2. Choose the **AzureSentinel_ManagementAPI** button on the toolbar to run the application in Debug mode. (Or, you can press F5.)

    ![Start application](./Images/start-button.png)

3. Once the app is running, a menu like the folowing screenshot appears in the console window.
    1. Each API call is represented by each option in the menu. Enter a number corresponding with your API request in the console. For example, next to the **Option**, enter number **22** to create an incident. The content of the incident comes from the **IncidentPayload.json** file you've filled in.
    2. Press ENTER  or Ctrl + C if you want to close the application.

    ![View Console](./Images/console-menu.png)

4. The **Results** folder contains responses from all GET requests you make. For example, when you make a GetIncidents request, the app will export the incidents returned from the request to a file starting with **GetIncidents.json** in the Results folder.

## Important Notes
The API currently has some limitations, and here are a few things to note regarding this sample.

1. Data Connectors: For CREATE data connector request to enable a data connection in Azure Sentinel, the API currently supports **User-Delegated** mode of authentication only, which requires a user sign-in. This solution is using **Application-Only** authentication, as the app is a daemon service running in the background without a user sign-in, so it isn't currently working if you enable a data connector via this solution.

2. Incidents: To close an incident (option 26 or 27 in the option menu), these following fields must be filled with values. Go to **Templates** folder, open **IncidentPayload.json** file, and make the modification accordingly.
        
        "classification": "",
        "classificationComment": "",
        "classificationReason": ""

3. Actions: To select a playbook for an analytic rule, you can either use Option 1 (Create Action) or option 9 (Create Alert rule) in the menu. Open your **ActionPayload.json** file in **templates** folder and ill in values of these fields:
    1. **triggerUri**: Callback URL for your playbook trigger. To get this URL, make a POST request to [WorkflowTrigger CallbackUrl](https://docs.microsoft.com/rest/api/logic/workflowtriggers/listcallbackurl). You can easily obtain the value using this [code-try](https://docs.microsoft.com/rest/api/logic/workflowtriggers/listcallbackurl#code-try-0). The **value** field in the response should be the URL.
    2. **logicAppResourceId**: Azure ARM resource ID of your logic app. Fill in the Subscription Id, Resource Group Name, and Playbook Name in the value.

    ```[
        {
            "properties": {
            "triggerUri": "<enter_Trigger_URI_of_your_playbook>",
            "logicAppResourceId": "/subscriptions/<subscrition-ID>/resourceGroups/<resource-group-name>/providers/Microsoft.Logic/workflows/<logic-app-name>"
            }
        },
    ```

### Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

### Copyright
Copyright (c) 2020 Microsoft. All rights reserved.
