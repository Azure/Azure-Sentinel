# Ingest GitHub AuditLog and API Data
Author: Nicholas DiCola, Sreedhar Ande

 GitHubLogs Azure Function ingests the following logs from GitHub
 1. AuditLog via (GraphQL)[https://developer.github.com/v4/interface/auditentry/] events and writes them to a custom log table called GitHub_CL.  
 2. Traffic Logs [https://developer.github.com/v3/repos/traffic/] data and writes them to a custom log table called GitHubRepoLogs_CL. 
 3. Security Vulnerability logs [https://developer.github.com/v4/object/securityvulnerability/] data and writes them to a custom log table called GitHubRepoLogs_CL

Following are the configuration steps to deploy Function App.

## **Pre-requisites**

A GitHub API Token is required. See the documentation to learn more about the [GitHub Personal Access Token](https://github.com/settings/tokens/).


## Configuration Steps to Deploy Function App
1. Click on Deploy to Azure (For both Commercial & Azure GOV)  
   <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FGithubFunction%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
	</a>
  

2. Select the preferred **Subscription**, **Resource Group** and **Location**  
   **Note**  
   Best practice : Create new Resource Group while deploying - all the resources of your custom Data connector will reside in the newly created Resource 
   Group
   
3. Enter the following value in the ARM template deployment
	```
	"PersonalAccessToken": This is the GITHUB PAT  
	"Workspace Id": The Sentinel Log Analytics Workspace Id  
	"Workspace Key": The Sentinel Log Analytics Workspace Key  
	"Function Schedule": The `TimerTrigger` makes it incredibly easy to have your functions executed on a schedule  
	```

## Post Deployment Steps
1. There are two json files (ORGS.json and lastrun-Audit.json) in Function Dependencies folder
2. Edit the ORGS.json file and update "org": "sampleorg" and replace sample org with your org name. 
	```
	If you have single org
	[
		{
			"org": "sampleorg1"
		}
	]  

	If you have multiple org's
	[
		{
			"org": "sampleorg1"
		},
		{
			"org": "sampleorg2"
		},
		{
			"org": "sampleorg3"
		}
	]
	```

3. Edit lastrun-Audit.json and update "org": "sampleorg" and replace sample org with your org name

	```
	If you have single org

	[
		{
			"org":  "sampleorg1",
			"lastContext":  "",
			"lastRun":  ""
		}
	]  

	If you have multiple org's

	[
		{
			"org":  "sampleorg1",
			"lastContext":  "",
			"lastRun":  ""
		},
		{
			"org":  "sampleorg2",
			"lastContext":  "",
			"lastRun":  ""
		}
	]
	```

4. Upload the following files to the storage account "github-repo-logs" container from 
	```
	ORGS.json
	lastrun-Audit.json
	```

5. PersonalAccessToken and Workspace Key will be placed as "Secrets" in the Azure KeyVault `<<Function App Name>><<uniqueid>>` with only Azure Function access policy. If you want to see/update these secrets,

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

6. The `TimerTrigger` makes it incredibly easy to have your functions executed on a schedule. This sample demonstrates a simple use case of calling your function based on your schedule provided while deploying. If you want to change
   the schedule 
   ```
   a.	Click on Function App "Configuration" under Settings 
   b.	Click on "Schedule" under "Application Settings"
   c.	Update your own schedule using cron expression.
   ```
   **Note: For a `TimerTrigger` to work, you provide a schedule in the form of a [cron expression](https://en.wikipedia.org/wiki/Cron#CRON_expression)(See the link for full details). A cron expression is a string with 6 separate expressions which represent a given schedule via patterns. The pattern we use to represent every 5 minutes is `0 */5 * * * *`. This, in plain text, means: "When seconds is equal to 0, minutes is divisible by 5, for any hour, day of the month, month, day of the week, or year".**

	
Note: there are two parsers (here)[https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/GitHub] to make the logs useful
