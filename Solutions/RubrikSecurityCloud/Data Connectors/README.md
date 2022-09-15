# Rubrik Security Cloud data connector

## Introduction

This folder contains the Azure function http trigger code for 3 azure functions of Rubrik's Microsoft Sentinel connector. The connector will run when any of the events(Anomaly, Ransomware Investigation Analysis or ThreatHunt) data will be pushed via webhook and ingest the triggered event data into the respective Microsoft Sentinel logs custom table `Rubrik_Anomaly_Data_CL`,`Rubrik_Ransomware_Data_CL` and `Rubrik_ThreatHunt_Data_CL`.

## Description

The Rubrik Security Cloud data connector enables security operations teams to integrate insights from Rubrik’s Data Observability services into Microsoft Sentinel. The insights include identification of anomalous filesystem behavior associated with ransomware and mass deletion, assess the blast radius of a ransomware attack, and sensitive data operators to prioritize and more rapidly investigate potential incidents.

## Folders

1. `RubrikWebhookEventsApp/` - This contains the package, requirements, ARM JSON file, connector page template JSON, and other dependencies.
2. `RubrikAnomalyEvent/` - This contains the Azure function source code to receive Anomaly event data via rubrik webhook and post into Microsoft Sentinel along with sample data.
3. `RubrikRansomwareAnalysisEvent/` - This contains the Azure function source code to receive Ransomware Analysis event data via rubrik webhook and post into Microsoft Sentinel along with sample data.
4. `RubrikThreatHuntEvent/` - This contains the Azure function source code to receive ThreatHunt event data via rubrik webhook and post into Microsoft Sentinel along with sample data.


## Installing for the users

After the solution is published, we can find the connector in the connector gallery of Microsoft Sentinel among other connectors in Data connectors section of Microsoft Sentinel.

i. Go to Microsoft Sentinel -> Data Connectors

ii. Click on the SecurityScorecard connector, connector page will open.

iii. Click on the blue `Deploy to Azure` button.


It will lead to a custom deployment page where after user need to select **Subscription**, **Resource Group** and **Location**.
And need to enter below information to configure Rubrik data connector for Microsoft Sentinel.
```Function Name
   Workspace ID
   Workspace Key
   Anomalies_table_name
   RansomwareAnalysis_table_name
   ThreatHunts_table_name
```

## **Post Deployment Steps**

* Steps to Configure the webhook using function url.

1. Note down the Function App URL and Function access key

2. Follow the Rubrik User Guide instructions to [Add a Webhook](https://docs.rubrik.com/en-us/saas/saas/common/adding_webhook.html) to begin receiving event information related to Ransomware Anomalies.
    - Select the Generic as the webhook Provider
    - This will use CEF formatted event information
    - Enter the Function App URL as the webhook URL endpoint for the Rubrik Solution for Microsoft Sentinel
    - Select the Custom Authentication option
    - Enter x-function-key as the HTTP header
    - Enter the Function access key as the HTTP value
Note: if you change this function access key in Microsoft Sentinel in the future you will need to update this webhook configuration
3. Select the following Event types:
    - Anomaly
    - Ransomware Investigation Analysis
    - Threat Hunt
4. Select the following severity levels:
    - Critical
    - Warning
    - Informational


The connector should ingest the data into the logs when it receives data from webhook via Http request.


## Installing for testing


i. Log in to Azure portal using the URL - [https://preview.portal.azure.com/?feature.BringYourOwnConnector=true](https://preview.portal.azure.com/?feature.BringYourOwnConnector=true).

ii. Go to Microsoft Sentinel -> Data Connectors

iii. Click the “import” button at the top and select the json file `RubrikWebhookEvents_API_FunctionApp.json` downloaded on your local machine from Github.

iv. This will load the connector page and rest of the process will be same as the Installing for users guideline above.


Each invocation and its logs of the function can be seen in Function App service of Azure, available in the Azure Portal outside of Microsoft Sentinel.

i. Go to Function App and click on the function which you have deployed, identified with the given name at the deployment stage.

ii. Go to Functions -> RubrikAnomalyEvent -> Monitor

iii. By clicking on invocation time, you can see all the logs for that run.

**Note: Furthermore we can check logs in Application Insights of the given function in detail if needed. We can search the logs by operation ID in Transaction search section.**
