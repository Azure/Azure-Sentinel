# Deployment of Sentinel Connector for SecurityBridge Threat Detection for SAP through Content Hub
This ARM template will deploy a connecter for "SecurityBridge Threat Detection for SAP" with the following elements:
* Connector
* Workbook
* Parser Function

Follow the below steps to deploy this solution in your environment:
* Log on to Azure Portal
* Navigate to Azure Sentinel and select your workspace
* Select `Content Hub`
* Search for `SecurityBridge Threat Detection for SAP`
* Click on `Install` and then click on `Create`
* Follow the steps to install the connector

# Deployment of Sentinel Connector for SecurityBridge Threat Detection for SAP through ARM template

This ARM template will deploy a connecter for "SecurityBridge Threat Detection for SAP" with the following elements:
* Connector
* Workbook
* Parser Function

This is only a temporary solution to deploy the connector manually until the official connector is available on the content hub.

### Pre-reqs
* Log in: You should be logged into the Azure Sentinel Environment
* Workspace Name: Workspace id of the azure sentinel.
* Workspace Location: You can get that from Sentinel > Settings > Workspace Settings > Properties > Location.  For example `southcentralus`
* Installation of Azure Sentinel Agent on the SAP Machine
* Path of logs file generation
* Cron job to be added to the machine to append the newly created logs into an already existing file
* Logs reception in a custom table named "SecurityBridgeLogs_CL"

### Installation Steps 
* Click on the Deploy to Azure button below
* Select the **Resource Group** where Azure Sentinel is deployed
* Add the name of the **Azure Sentinel Workspace** in the Workspace box
* Leave rest of the items intact 
* Click on **Review + create** button
* Wait for the validation to complete
* Click on **Create**

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Ffrozenstrawberries%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSecurityBridge%2FPackage%2FmainTemplate.json)