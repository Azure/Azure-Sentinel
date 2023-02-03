# Ingest LookOut Cloud Security events into sentinel through LookOut Cloud Security dataconnector
Author: Prathibha Tadikamalla

 The Azure function based LookOut Cloud Security dataconnector pulls all the LookOut cloud security events into Sentinel. All these events will be placed into the table called "Lookoutlogs_CL". As of now the solution has 3 parsers based on the below events:
  *	[Lookout Cloud Security Activities](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#code_scanning_alert)
  *	[Lookout Cloud Security Anomalies](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#repository_vulnerability_alert)
  *	[Lookout Cloud Security Violations](https://docs.github.com/en/enterprise-cloud@latest/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#secret_scanning_alert)
  

Following are the configuration steps to deploy Function App.

## **Pre-requisites**

## Configuration Steps to Deploy Function App
1. Click on Deploy to Azure (For both Commercial & Azure GOV)  
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-LookoutCS-azuredeploy)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/sentinel-LookoutCS-azuredeploy-gov)
  

2. Select the preferred **Subscription**, **Resource Group** and **Location**  
   **Note**  
   Best practice : Create new Resource Group while deploying - all the resources of your custom Data connector will reside in the newly created Resource 
   Group
   
3. Enter the following value in the ARM template deployment
```
"FunctionName": The name of the Azure function. Default value will be given as "fngithubwebhook"
"Workspace Id": The Sentinel Log Analytics Workspace Id  
"Workspace Key": The Sentinel Log Analytics Workspace Key  
```	

