# MongoDB Atlas API Connector for Microsoft Sentinel
Author: Steve Lord

This custom data connector uses a Function App to pull MongoDB Atlas (MDBA) logs from the MongoDB Atlas Administration API and upload them into the selected Log Analytics workspace via the Log Ingestion API. 

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fgithub.com%2Fmongodb-partners%2FMicrosoft_Sentinel_Integration%2Fblob%2Ftimer-trigger%2FazureDeploy.json)

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
    - Priviledged Role Administrator
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
4. Select and from the list of **Log Analytics Workspaces**.
5. Enter fields for the MongoDB Atlas instance from which you are collecting logs
    - Cluster Id
    - Group Id
    - Client Id
    - Client Secret
6. Scheduling - this uses the CRON syntax to specify the rate at which the logs are collected.
7. Click **Review and Create**.
8. Click **Create**.

## 2. Run Function App
The Function App is configured to run every 5 minutes.

After a successful run, you should see data populated in the MDBA custom table.
