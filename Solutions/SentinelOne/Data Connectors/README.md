# SentinelOne Integration for Microsoft Sentinel

## Introduction

This folder contains the Azure function time trigger code for SentinelOne-Microsoft Sentinel connector. The connector will run periodically and ingest the SentinelOne data into the Microsoft Sentinel logs custom table `SentinelOne_CL`. 
## Folders

1. `SentinelOne/` - This contains the package, requirements, ARM JSON file, connector page template JSON, and other dependencies. 
2. `SentinelOneSentinelConnector/` - This contains the Azure function source code along with sample data.


## Installing for the users

After the solution is published, we can find the connector in the connector gallery of Microsoft Sentinel among other connectors in Data connectors section of Sentinel. 

i. Go to Microsoft Sentinel -> Data Connectors

ii. Click on the SentinelOne connector, connector page will open. 

iii. Click on the blue `Deploy to Azure` button.   


It will lead to a custom deployment page where after entering accurate credentials and other information, the resources will get created. 


The connector should start ingesting the data into the logs in next 10-15 minutes.


## Installing for testing


i. Log in to Azure portal using the URL - [https://portal.azure.com/?feature.BringYourOwnConnector=true](https://portal.azure.com/?feature.BringYourOwnConnector=true).

ii. Go to Microsoft Sentinel -> Data Connectors

iii. Click the “import” button at the top and select the json file `SentinelOne_API_FunctionApp.JSON` downloaded on your local machine from Github.

iv. This will load the connector page and rest of the process will be same as the Installing for users guideline above.


Each invocation and its logs of the function can be seen in Function App service of Azure, available in the Azure Portal outside the Microsoft Sentinel.

i. Go to Function App and click on the function which you have deployed, identified with the given name at the deployment stage.

ii. Go to Functions -> SentinelOneSentinelConnector -> Monitor

iii. By clicking on invocation time, you can see all the logs for that run. 

**Note: Furthermore we can check logs in Application Insights of the given function in detail if needed. We can search the logs by operation ID in Transaction search section.**
