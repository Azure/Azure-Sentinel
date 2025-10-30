# Azure Monitor Http Data Collector API Sample

## Description
This repository contains a very simple C# console application to demonstrate how you can leverage the Azure Monitor Http Data Collector API to post your custom log data to your Azure Log Analytics Custom logs. The posted data can then be accessed via your Azure Log Analytics Custom logs or Azure Sentinel Custom Log table.


## Prerequisites
To configure the tool, the following assembly is required to post custom data to Azure Log Analytics custom logs via Azure Monitor Http Data Collector API.

1. **Active Azure Subscription**, if you don't have one, create a [free account](https://azure.microsoft.com/free/?WT.mc_id=A261C142F) before you begin.

2. Obtain **domain** by following these steps:
    1. Login into [Azure Management Portal](https://portal.azure.com)
    1. Navigate to the **Azure Active Directory** blade
    1. Click on **Custom Domain Names**. Copy your domain name as you will need it later to run the application.

3. **Log Analytics workspace**. If you don't have one, [create a Log Analytics workspace](https://docs.microsoft.com/azure/azure-monitor/learn/quick-create-workspace).

4. Obtain **WorkSpaceId** and **Key** following these steps. Copy this workspace Id and Key as you will need them later to run the application.
   1. In the Azure portal, search for and select **Log Analytics workspaces**
   1. In your list of Log Analytics workspaces, select the workspace you intend on configuring the agent to report to.
   1. Select **Advanced Settings**.

5. To enable Azure Sentinel, you need **contributor** permissions to the subscription in which the Azure Sentinel workspace resides. Learn more to [onboard Azure Sentinel](https://docs.microsoft.com/azure/sentinel/quickstart-onboard#enable-azure-sentinel-).

6. To use Azure Sentinel, you need either **contributor** or **reader** permissions on the resource group that the workspace belongs to.

## Setup
1) Clone Azure Sentinel repository by running this command: git clone https://github.com/Azure/Azure-Sentinel.git
2) In the cloned repo, navigate to the **Tools** directory, then in **HttpDataCollectorAPI** folder, open **HttpDataCollectorAPI.sln**.
3) Install necessary dependencies: In Visual Studio, right click the **HttpDataCollectorAPI** solution.
Click **Restore NuGet Packages**.
4) Open **Program.cs** file, fill in the values of the following variables using the information you've saved from the [Prerequisites](#Prerequisites) section.
The TimeStampField is optional from the data. If the time field is not specified, Azure Monitor assumes the time is the message ingestion time.

		static string customerId = "enter_your_workspaceId";
		static string sharedKey = "enter_your_workspace_key";
		static string LogName = "enter_your_log_name";
		static string TimeStampField = "";

5) For this following custom data section, you can either replace the value of the string json variable with your own custom data or comment this out and create your own json file with custom log data in the solution. For creating your own file option, you will need to modify the code to read the json file in the API call.
		static string json = @"[{""DemoField1"":""DemoValue1"",""DemoField2"":""DemoValue2""},{""DemoField3"":""DemoValue3"",""DemoField4"":""DemoValue4""}]"; 
6) Once changes are complete, save the file.
Now you can run the application. Please note that the "Main" function in the Program.cs class is the entry point for the application.

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
