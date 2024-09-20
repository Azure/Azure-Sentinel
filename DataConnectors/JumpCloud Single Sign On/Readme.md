# Azure Sentinel Data Connector for JumpCloud SSO event logs

This Azure Function App will connect to the JumpCloud Rest-API using your JumpCloud api Token and retrieve the event logs and ingest them into a custom table called "JumpCloud" in your Log Anaytics Workspace used by Azure Sentinel.


The Azure Function has bee setup to trigger once every 5 minutes and trigger a seperate execution for each log type listed in the configuration you setup. 

### Prerequisites
Before deplying this Arm Template 
1. Decide which of the JumpCloud logs you want to ingest into Azure Sentinel, details on the log types available are found in their documentation [**here**](https://jumpcloud-insights.api-docs.io/1.0/how-to-use-the-directory-insights-api/json-post-request-body). You can choose any combination of event type for ingestion **However Do not mix 'ALL' type with any other or duplicate events will be ingested.**
2. You may need a JumpCloud license that enables Directory Insights to be able to access the Rest-API.
3. Follow the instructions on the [JumpCloud docs](https://jumpcloud-insights.api-docs.io/1.0/authentication-and-authorization/authentication) on how to access your API Key.
4. You will need your WorkspaceID and WorkspaceKey for the Log Analytics Workspace you want the logs to be ingested into.

**NOTE:** There maybe additional charges incurred on your Azure Subscription if you run this Azure Function

#### Deployment
The simplest way to deploy is to launch the Deployment template from the Deploy to [**Azure Button below**]

**NOTES:** 
1. Where possible details in the Deployment Template have been prepopulated.
2. The function name needs to be globally unique, a random character generator will generate several charactors to append to your entered name. Be aware that this name is also used for the associated storage account so if your prefix is too long the template will fail validation becuase the name is longer than the permitted length for a storage Account Name.
3. Once successfully deployed the function will start triggering within 5 minutes and the inital request to JumpCloud will be for logs since the previous midnight UTC time. 


[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fcabberley%2FJumpCloudSSO%2Fmaster%2Fazuredeploy_JumpCloud_API_FunctionApp.json)
