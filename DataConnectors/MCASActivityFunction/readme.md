# Ingest MCAS Activity Log
Author: Nicholas DiCola

This function ingests MCAS Activities via (API)[https://docs.microsoft.com/cloud-app-security/api-activities-list] and writes them to a custom log table called MCASActivity_CL.

Following are the configuration steps to deploy Function App.

## **Pre-requisites**

A MCAS API Token is required. See the documentation to learn more about the [API Token](https://docs.microsoft.com/cloud-app-security/api-authentication).


## Configuration Steps to Deploy Function App
1. Click on Deploy to Azure (For both Commercial & Azure GOV)  
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FMCASActivityFunction%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FMCASActivityFunction%2Fazuredeploy.json)
  

2. Select the preferred **Subscription**, **Resource Group** and **Location**  
   **Note**  
   Best practice : Create new Resource Group while deploying - all the resources of your custom Data connector will reside in the newly created Resource 
   Group
   
3. Enter the following value in the ARM template deployment
	```
	"APIToken": This is the MCAS API Token​  
	"MCASURL": This is the MCAS URL.  See About in the portal for specfici url.
	"Workspace Id": The Sentinel Log Analytics Workspace Id  
	"Workspace Key": The Sentinel Log Analytics Workspace Key  
	"Function Schedule": The `TimerTrigger` makes it incredibly easy to have your functions executed on a schedule  
	"Lookback": The number of minutes between runs
	```

## Post Deployment Steps
1. API Token and Workspace Key will be placed as "Secrets" in the Azure KeyVault `<<Function App Name>><<uniqueid>>` with only Azure Function access policy. If you want to see/update these secrets,

	```
		a. Go to Azure KeyVault `<<Function App Name>><<uniqueid>>`
		b. Click on "Access Policies" under Settings
		c. Click on "Add Access Policy"
			i. Configure from template : Secret Management
			ii. Key Permissions : GET, LIST, SET
			iii. Select Prinicpal : <<Your Account>>
			iv. Add
		d. Click "Save"

	```

2. The `TimerTrigger` makes it incredibly easy to have your functions executed on a schedule. This sample demonstrates a simple use case of calling your function based on your schedule provided while deploying. If you want to change
   the schedule 
   ```
   a.	Click on Function App "Configuration" under Settings 
   b.	Click on "Schedule" under "Application Settings"
   c.	Update your own schedule using cron expression.
   ```
   **Note: For a `TimerTrigger` to work, you provide a schedule in the form of a [cron expression](https://en.wikipedia.org/wiki/Cron#CRON_expression)(See the link for full details). A cron expression is a string with 6 separate expressions which represent a given schedule via patterns. The pattern we use to represent every 5 minutes is `0 */5 * * * *`. This, in plain text, means: "When seconds is equal to 0, minutes is divisible by 5, for any hour, day of the month, month, day of the week, or year".**

3. If you change the TimerTigger you need to configure the Lookback setting to match the number of minutes between runs. If you want to change
   the Lookback 
   ```
   a.	Click on Function App "Configuration" under Settings 
   b.	Click on "Lookback" under "Application Settings"
   c.	Update your Lookback using a number of minutes (e.g 10).
   ```

	
Note: there are  parsers (here)[https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/MCAS] to make the logs useful
