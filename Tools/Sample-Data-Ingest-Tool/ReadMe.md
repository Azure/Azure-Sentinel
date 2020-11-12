# Sample Data Ingest Tool

## Description
This repository contains a tool in C# console application that allows users to post sample data of custom format to their Azure Log Analytics Custom logs. The sample data is found in Custom folder under Sample Data directory. The posted data can then be accessed via their Azure Log Analytics Custom logs or Azure Sentinel Custom Log table.

Two options are available using the tool. The Prerequisites and App Registration steps are required for both options.

## Prerequisites
To configure the tool, the following assembly is required to post sample data to Azure Log Analytics custom logs via Azure Monitor Http Data Collector API.

1. **Active Azure Subscription**, if you don't have one, create a [free account](https://azure.microsoft.com/free/?WT.mc_id=A261C142F) before you begin.

2. *\[Optional\]* Obtain **domain** by following these steps:
    1. Login into [Azure Management Portal](https://portal.azure.com)
    1. Navigate to the **Azure Active Directory** blade
    1. Click on **Custom Domain Names**. Copy your domain name as you will need it later to run the application.

3. **Log Analytics workspace**. If you don't have one, [create a Log Analytics workspace](https://docs.microsoft.com/azure/azure-monitor/learn/quick-create-workspace).

4. Obtain **WorkSpaceId** and **PrimaryKey** following these steps. Copy this workspace Id and PrimaryKey as you will need them later to run the application.
   1. In the Azure portal, search for and select **Log Analytics workspaces**
   1. In your list of Log Analytics workspaces, select the workspace you intend on configuring the agent to report to.
   1. Select **Agents management**.

5. To enable Azure Sentinel, you need **contributor** permissions to the subscription in which the Azure Sentinel workspace resides. Learn more to [onboard Azure Sentinel](https://docs.microsoft.com/azure/sentinel/quickstart-onboard#enable-azure-sentinel-).

6. To use Azure Sentinel, you need either **contributor** or **reader** permissions on the resource group that the workspace belongs to.

7. [.NET Core](https://dotnet.microsoft.com/download) installed locally.

## App Registration
To use Log Analytics API in the application, you'll need to register a new application in the Microsoft [Application Registration Portal](https://portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/RegisteredApps).
Follow these steps to register a new application:
1. Sign in to the [Application Registration Portal](https://portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/RegisteredApps) using either your personal or work or school account.

2. Choose **New registration**.

3. Enter an application name, and choose **Register** (keep the default values for the other fields).

4. Next you'll see the overview page for your app. Copy and save the **Application Id (clientId)** field. You will need it later to complete the configuration process. If the app is not registered under the domain listed above, you will also need to copy and save the **Directory ID (tenantId)**.

5. Under **Certificates & secrets**, choose **New client secret** and add a quick description. A new secret will be displayed in the **Value** column. Copy this password. You will need it later to complete the configuration process and it will not be shown again.

6. Link Log Analytics workspace to your registered application by following these steps:
   1. Navigate to your Azure portal, and select or search for **Log Analytics**.
   1. Select your workspace from the list of available options, or search for it.
   1. From the left menu that opens, select **Access Control (IAM)**. Click Add, and select **Log Analytics Reader** for the Role in the blade that appears. Search for your AAD App by name, and then click save.
   1. You app is now setup to make API calls to your workspace.

## Option 1: Post existing custom log data
This option allows users to post the readily available sample custom data in the **Sample Data** directory to Azure Log Analytics Custom logs.

### Setup
1) Clone Azure Sentinel repository by running this command: git clone https://github.com/Azure/Azure-Sentinel.git

2) In the cloned repo, navigate to the **Tools** directory, and open **SampleDataIngestTool** solution.

3) Install necessary dependencies: In Visual Studio, right click the **SampleDataIngestTool** solution.
Click **Restore NuGet Packages**.

4) Open **config.txt** file, enter the following credentials using the information you've saved from the [Prerequisites](#Prerequisites) and App Registration section.

        "workspaceId": "enter_your_workspaceId_or_customerId_here",
        "sharedKey": "enter_your_workspace_primary_key_here",
        "clientId": "enter_your_clientId_here",
        "clientSecret": "enter_your_client_secret_here",
        "domain": "enter_your_app_domain_or_tenantId_here";

5) Once changes are complete, save the file.
Now you can run the application. Please note that the "Main" function in the Program.cs class is the entry point for the application.
   1. If it's the first time the application is run, all custom data files of json format are posted to the Log Analytics custom logs. Once the application finishes running, check the Console to see the names of the file that have been successfully pushed.
   1. In the next runs after the first run, you are asked to enter your response to a prompt in the Console. Enter your reponse (Yes/No) to indicate whether or not you'd like to post the sample data again.
   1. If the response is Yes, the sample data is pushed again to the Log Analytics custom logs.
   1. View the sample data in your Log Analytics Custom Logs or Azure Sentinel Custom Log.

## Option 2: Post your own custom log data
This option allows users to post their own custom log data to Azure Log Analytics Custom logs.

### Setup
   1. Follow step 1-4 from the [Setup](#Setup) section under Option 1 above.
   1. In the Custom folder under Sample Data directory of the cloned repo, create a new file with your custom log data in a json format with a "_CL" suffix. For example, "testdata_CL.json" is a valid custom log file name.
   1. Follow step 5 from the [Setup](#Setup) section under Option 1 above.

### Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

### Copyright
Copyright (c) 2020 Microsoft. All rights reserved.
