# MongoDB Atlas API Connector for Microsoft Sentinel
Author: Steve Lord

This custom data connector uses a Function App to pull MongoDB Atlas (MDBA) logs from the MongoDB Atlas Administration API and upload them into the selected Log Analytics workspace via the Log Ingestion API. 

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#view/Microsoft_Azure_CreateUIDef/CustomDeploymentBlade/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMongoDBAtlas%2FData%20Connectors%2FMongoDBAtlasLogs%2Fazuredeploy_Connector_MongoDBAtlasLogs_AzureFunction.json/uiFormDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMongoDBAtlas%2FData%20Connectors%2FMongoDBAtlasLogs%2FcreateUiDef.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#view/Microsoft_Azure_CreateUIDef/CustomDeploymentBlade/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMongoDBAtlas%2FData%20Connectors%2FMongoDBAtlasLogs%2Fazuredeploy_Connector_MongoDBAtlasLogs_AzureFunction.json/uiFormDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMongoDBAtlas%2FData%20Connectors%2FMongoDBAtlasLogs%2FcreateUiDef.json)

- [Release Notes](releaseNotes.md)
- [Pre-requisites](#pre-requisites)
- [Deployment Process](#deployment-process)

## **Pre-requisites**
1. An Azure Subscription
2. A Resource Group
2. A Microsoft Sentinel/Log Analytics workspace
3. Roles required to deploy resources:
    - User Access Administrator
    - Contributor
    - Application Administrator
    - Directory Readers
    - Directory Writers
    - Privileged Role Administrator
4. A MongoDB Atlas account:
    - Cluster Id
    - Group Id
    - Client Id
    - Client Secret

## **Deployment Process**
## 1. Deploy Azure Resources
1. Click the **Deploy to Azure** button above.
2. Once in the Azure Portal, select the **Subscription** and **Resource Group** to deploy the resources into.
3. Click 'Yes' for 'Use existing Log Analytics Workspace?'
4. Select a workspace from the list of **Log Analytics Workspaces**.
5. In the MongoDB connection tab, enter fields for the MongoDB Atlas instance from which you are collecting logs
    - Cluster Id
    - Group Id
    - Client Id
    - Client Secret
6. Review the MongoDB filters tab and ensure that at least one of: **Include Access Logs**, **Include Network Logs** or **Include Query Logs** are checked.
6. Scheduling - this uses the [CRON syntax](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=python-v2%2Cisolated-process%2Cnodejs-v4&pivots=programming-language-csharp#ncrontab-expressions) to specify the rate at which the logs are collected. The MongoDB Atlas Administration API will publish new logs every 5 minutes.
7. Click **Review and Create**.
8. Click **Create**.

## 2. Run Function App
The Function App is configured to run every 5 minutes by default.

After a successful run, you should see data populated in the MDBA custom table: MDBALogTable_CL.
