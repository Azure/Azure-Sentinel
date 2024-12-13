# Ingest LookOut Cloud Security events into sentinel through LookOut Cloud Security dataconnector
Author: Prathibha Tadikamalla

 The Azure function based LookOut Cloud Security dataconnector pulls all the LookOut cloud security events into Sentinel. This function app contains three different functions to fetch activity events, Violation events and Anamoly events respectivley. Every time the internal function runs, it identifies the last event received date and time and stored into a file share. This value will be used as a start time for every next run. And this function also provides a provision to delay the records through a "FetchDelay" config value to prevent any data loss scenarios. And it also provides a provision to fetch the historical data for the first time function runs through a config value "PastDays". All these events will be placed into the table called "LookoutCloudSecurity_CL". As of now the solution has 3 parsers based on the below events:
  *	[Lookout Cloud Security Activities](https://aka.ms/sentinel-Lookout-Cloud-Security-Activities)
  *	[Lookout Cloud Security Anomalies](https://aka.ms/sentinel-Lookout-Cloud-Security-Anomalies)
  *	[Lookout Cloud Security Violations](https://aka.ms/sentinel-Lookout-Cloud-Security-Violations)
  

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
"FunctionName": The name of the Azure function. Default value will be given as "fnLoCSCon"
"Workspace Id": The Sentinel Log Analytics Workspace Id  
"Primary Key": The Sentinel Log Analytics Workspace Primary Key
"LookoutClientId": The unique ID that was provided for this client
"LookoutApiSecret": The API secret that was provided for this client
"Baseurl": The URL used to access this client. The url must start with "https://"
"Schedule": A cron expression which is a string that defines a set of times, using six fields separated by white space. Each field in the cron expression represents a set of values that determine when a task should be executed. For example, the following cron expression would run a task every 5 minutes: Ex: "0 */5 * * * *" 
"MaxResults": Maximum Results to be returned from API as per source capacity
"FetchDelay": This integer value represents the number of minutes to be delayed while fetching of the results to prevent data loss due to delays at source.
"PastDays": The integer value represents the number of days to get historical data during the start of the function app via config
```	

