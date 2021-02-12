# Ingest GitHub AuditLog and API Data
Author: Nicholas DiCola, Sreedhar Ande

 GitHubLogs Azure Function ingests the following logs from GitHub
 1. AuditLog via (GraphQL)[https://developer.github.com/v4/interface/auditentry/] events and writes them to a custom log table called GitHub_CL.  
 2. Traffic Logs [https://developer.github.com/v3/repos/traffic/] data and writes them to a custom log table called GitHubRepoLogs_CL. 
 3. Security Vulnerability logs [https://developer.github.com/v4/object/securityvulnerability/] data and writes them to a custom log table called GitHubRepoLogs_CL

Following are the configuration steps to deploy Function App.

## **Pre-requisites**

A GitHub API Token is required. See the documentation to learn more about the [GitHub Personal Access Token](https://github.com/settings/tokens/).

## Configuration Steps
1. Deploy the ARM template and fill in the parameters.
	```
	"PersonalAccessToken": This is the GITHUB PAT​
	"Workspace Id": The Sentinel Log Analytics Workspace Id​
	"Workspace Key": The Sentinel Log Analytics Workspace Key
	"Function Schedule": The `TimerTrigger` makes it incredibly easy to have your functions executed on a schedule
	```
2. There are two json files (ORGS.json and lastrun-Audit.json) in Function Dependencies folder
3. Edit the ORGS.json file and update "org": "sampleorg" and replace sample org with your org name. 
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

4. Edit lastrun-Audit.json and update "org": "sampleorg" and replace sample org with your org name

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

5. Upload the following files to the storage account "github-repo-logs" container from 
	```
	ORGS.json
	lastrun-Audit.json
	```

6. PersonalAccessToken and Workspace Key will be placed as "Secrets" in the Azure KeyVault `githubkv<<uniqueid>>` with only Azure Function access policy. If you want to see/update these secrets,

	```
		a. Go to Azure KeyVault "githubkv<<uniqueid>>"
		b. Click on "Access Policies" under Settings
		c. Click on "Add Access Policy"
			i. Configure from template : Secret Management
			ii. Key Permissions : GET, LIST, SET
			iii. Select Prinicpal : <<Your Account>>
			iv. Add
		d. Click "Save"

	```

7. The `TimerTrigger` makes it incredibly easy to have your functions executed on a schedule. This sample demonstrates a simple use case of calling your function based on your schedule provided while deploying. If you want to change
   the schedule 
   ```
   a.	Click on Function App "Configuration" under Settings 
   b.	Click on "Schedule" under "Application Settings"
   c.	Update your own schedule using cron expression.
   ```
   **Note: For a `TimerTrigger` to work, you provide a schedule in the form of a [cron expression](https://en.wikipedia.org/wiki/Cron#CRON_expression)(See the link for full details). A cron expression is a string with 6 separate expressions which represent a given schedule via patterns. The pattern we use to represent every 5 minutes is `0 */5 * * * *`. This, in plain text, means: "When seconds is equal to 0, minutes is divisible by 5, for any hour, day of the month, month, day of the week, or year".**

8. Once Azure Function App is deployed
	 ```
	a.	Go to `githublogs<<uniqueid>>`
	b.	Click on "Advanced Tools" under Development Tools 
	c.	Click on Go --> You will be redirected to Web App --> Check Temp folder path. 
	d.	It can be either C:\local\Temp\ or D:\local\Temp\.
	 ```
9. After finding Temp folder path
	```
	a.	Go to `githublogs<<uniqueid>>`
	b.	Click on "Configuration" under Settings
	c.	Click on "TMPDIR" under "Application Settings"
	d.	Update Drive (C//D) based on your findings from Step 9.
	```
	**Note: Make sure the value in "TMPDIR" doesnt have "\\" at the end.**

10. **[Previous Version (prior to 2/9/2021) deployed users only ]**. If you want to ingest GitHub Audit & Repo logs into New custom logs, follow the steps  
	```
	a.	Go to `githublogs<<uniqueid>>`
	b.	Click on "Configuration" under Settings
	c.	Click on "New Application Setting"
	d.	Name --> GitHubAuditLogsTableName.
	e.  Value --> <<Your preferred table name for GitHub Audit Logs, for example GitHubAuditLogs>>
	f.  Click on "Ok"
	g.  Click on "New Application Setting"
	h.  Name --> GitHubRepoLogsTableName.
	i.  Value --> <<Your preferred table name for GitHub Repo Logs, for example GitHubRepoLogs>>
	j.  Click on "Ok"
	```
	**Note**
	If you don't create these new environment variable, then it will be ingested to default  
	Audit Logs --> GitHub_CL  
	Repo Logs --> GitHubRepoLogs_CL  
	
11.	**For Azure Gov customers only**, You will see additional environment variable "Azure Tenant" under "Configuration" --> "Application Settings" and its default value is ".us"
	Currently this Function App supports "Azure Gov(.US)" tenants
	Ex: https://portal.azure.us
	
Note: there are two parsers (here)[https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/GitHub] to make the logs useful

## Deploy the Function App template
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FGithubFunction%2Fazurecomdeploy_dotcomtenants.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FGithubFunction%2Fazuregovdeploy_dotustenants.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>
