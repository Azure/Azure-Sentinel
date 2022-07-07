# Ingest GitHub events into sentinel through Webhook dataconnector
Author: Prathibha Tadikamalla

 The Azure function based github dataconnector using webhook pushes all the github subscribed events into Sentinel. All these events will be placed into the table called "githubscanaudit_CL". As of now the solution has 3 parsers based on the below events.
  *	https://docs.github.com/en/rest/reference/code-scanning
  *	https://docs.github.com/en/rest/reference/dependabot
  *	https://docs.github.com/en/rest/reference/secret-scanning

Following are the configuration steps to deploy Function App.

## **Pre-requisites**

## Configuration Steps to Deploy Function App
1. Click on Deploy to Azure (For both Commercial & Azure GOV)  
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-GitHubwebhookAPI-azuredeploy)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/sentinel-GitHubwebhookAPI-azuredeploy-gov)
  

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
## **Post Deployment Steps**
   #### **Get the Function app endpoint**
1. Follow the below steps to get the endpoint. 
	 * Go to Azure function Overview page and go to "Functions" and click on "GithubwebhookConnector"      
         ![](Images/GotoFunction.jpg)
	 * Go to "GetFunctionUrl" highlighted in the below image and copy the function url.
         ![](Images/functionappcompleteurl.jpg)
	 * You can also generate a new function key as provided in the below image and replace the {code} parameter value in the function app url.
    Ex: https://fngithubwebhookconnector.azurewebsites.net/api/GithubWebhookConnector?code={apikey}
	    ![](Images/FunctionAppfunctionKey.jpg)

   ### **Configure Webhook to Github Organization**        
    *  Go to github and open your account and click on "Your Organizations"

       ![](Images/Githubstep1.JPG)

    *  Click on Settings

       ![](Images/GithubStep2.jpg)

    *  Click on "Webhooks" and configure the function app endpoint as shown below. 

       ![](Images/GithubStep3.jpg)

4. With that you are done with the github configuration. After the delay of 10 to 20 mins (since LogAnalytics needs sometime to spin up the resources for the first time), you should be able to see all the transactional events from the Github into LogAnalytics workspace table called "githubscanaudit_CL" as shown below.	

    ![](Images/LogAnalyticsdata.jpg)
