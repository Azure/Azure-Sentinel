# Ingest GitHub events into sentinel
Author: Prathibha Tadikamalla

 Githubwebhook connector Azure Function ingests the following logs from GitHub. All these logs will be placed into the table called "GitHubScanAudit_CL"
  *	https://docs.github.com/en/rest/reference/code-scanning
  *	https://docs.github.com/en/rest/reference/dependabot
  *	https://docs.github.com/en/rest/reference/secret-scanning

Following are the configuration steps to deploy Function App.

## **Pre-requisites**

## Configuration Steps to Deploy Function App
1. Click on Deploy to Azure (For both Commercial & Azure GOV)  
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FGithubFunction%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FGithubFunction%2Fazuredeploy.json)
  

2. Select the preferred **Subscription**, **Resource Group** and **Location**  
   **Note**  
   Best practice : Create new Resource Group while deploying - all the resources of your custom Data connector will reside in the newly created Resource 
   Group
   
3. Enter the following value in the ARM template deployment
	```
	"Workspace Id": The Sentinel Log Analytics Workspace Id  
	"Workspace Key": The Sentinel Log Analytics Workspace Key  
	
## Post Deployment Steps
1. Build the funtion app endpoint to which Github needs to be connected and post the events here.
2. Follow the below steps to buidl the endpoint. 
	 * Go to Azure function Overview page and go to url which is in the format of 
       ### https://{FunctionName}.azurewebsites.net
         ![](/Images/FunctionAppUrlPart1.jpg)
	 * Append the below route prefix to the function app url from above step.
         ![](/Images/FuncionAppUrlPart2.jpg)
	 * Append the internal Function Name.
         ![](/images/FunctionAppUrlfunctionNamePart3.JPG)
	 * Copy the key you have generated. You can generate a new api key and provide in the query parameter as code = {}
	    ![](Images/FunctionAppfunctionKey.jpg)
Ex: https://fn-githubwebhookconnector.azurewebsites.net/github/GithubWebhookConnector?code={functionKey}
3. Configure the above endpoint to your Gitbug organaization as webhook as given below.
    * Go to settings
    ![](images/Githubstep1.JPG)
    * Click on "Webhooks" and configure the function app endpoint as shown in below figure. 
     ![](images/Githubwebhooksettings.jpg)

4. The `http Trigger` makes it incredibly easy to push your notifications on demand. 	
5. there are three parsers (here)[https://github.com/Azure/Azure-Sentinel/Solutions/GitHub/Parsers] to make the logs useful. This parser pulls the logs those are collected into a custom log table entitled githubscanaudit_CL. This table supports all the possible events from Github and it will create columns only for first level nodes of the json payload and inserts data as string. Please refer below images for more details.
    *Sample security_Advisory json payload from github
      ![](images/GithubSamplePayload.JPG)
    * security_advisory json will be inserted into "githubscanaudit_CL" table as string as given below.
      ![](images/LogAnalyticsdata.jpg)
