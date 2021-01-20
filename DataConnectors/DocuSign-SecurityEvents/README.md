# Ingest DocuSign Security Events
Author: Sreedhar Ande

DocuSign-SecurityEvents Data connector ingests security events for your DocuSign account into Azure Log Analytics Workspace using DocuSign Monitor REST API

Following are the configuration steps to deploy Data connector.

## **Pre-requisites**
1. Obtain DocuSign OAuth Token  
   Option #1  
   DocuSign OAuth Token is required. See the documentation to obtain https://developers.docusign.com/platform/auth/jwt/jwt-get-token/
 

   Option #2
   1. https://apiexplorer.docusign.com/
   2. Authenticate using your credentials
   3. Select any API end point and click on "Send Request" 
   4. If you receive "Success" response - copy the Authorization Bearer token (token only without Bearer prefix)  

2. Copy two json files (ORGS.json and lastrun-Monitor.json) from Function Dependencies folder to your local drive
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

4. Edit lastrun-Monitor.json and update "org": "sampleorg" and replace sample org with your org name

	```
	If you have single org

	[
		{
			"org":  "sampleorg1",
			"lastRunEndCursor":  "",
			"lastRun":  ""
		}
	]  

	If you have multiple org's

	[
		{
			"org":  "sampleorg1",
			"lastRunEndCursor":  "",
			"lastRun":  ""
		},
		{
			"org":  "sampleorg2",
			"lastRunEndCursor":  "",
			"lastRun":  ""
		}
	]
	```

## Deploy the Function App template
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FDocuSign-SecurityEvents%2Fazuredeploy_dotcomtenants.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FDocuSign-SecurityEvents%2Fazuredeploy_dotgovtenants.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

## Configuration Steps to Deploy Function App
1. Click on Deploy to Azure/Deploy to Azure Gov button

2. Select the preferred **Subscription**, **Resource Group** and **Location**  
   **Note**  
   Best practice : Create new Resource Group while deploying - all the resources of your custom Data connector will reside in the newly created Resource 
   Group
3. Enter the following value in the ARM template deployment
	```
	"DocuSignAccessToken": This is the DocuSign OAuth Token
	"Workspace Id": Azure Log Analytics Workspace Id​
	"Workspace Key": Azure Log Analytics Workspace Key
	"CustomLogTableName": Azure Log Analytics Custom Log Table Name
	"Function Schedule": The `TimerTrigger` makes it incredibly easy to have your functions executed on a schedule. The default **Time Interval** is set to pull
	the last ten (10) minutes of data.
	```
	
## Post Deployment Steps
1. After successful deployment go to your Resource Group and search for storage account, named - `docusign<<uniqueid>>` and upload previously edited json files under "docusign-monitor" container 
	```
	ORGS.json
	lastrun-Monitor.json
	```

2. DocuSignAccessToken and Workspace Key will be placed as "Secrets" in the Azure KeyVault `docusignkv<<uniqueid>>` with only Azure Function access policy. If you want to see/update these secrets,

	```
		a. Go to Azure KeyVault "docusignkv<<uniqueid>>"
		b. Click on "Access Policies" under Settings
		c. Click on "Add Access Policy"
			i. Configure from template : Secret Management
			ii. Key Permissions : GET, LIST, SET
			iii. Select Prinicpal : <<Your Account>>
			iv. Add
		d. Click "Save"

	```

3. The `TimerTrigger` makes it incredibly easy to have your functions executed on a schedule. This sample demonstrates a simple use case of calling your function based on your schedule provided while deploying. If the time interval needs to be modified, it is recommended to change the Function App Timer Trigger accordingly update environment variable **"Schedule**" (post deployment) to prevent overlapping data ingestion.
   ```
   a.	Go to your Resource Group --> Click on Function App `docusign<<uniqueid>>`
   b.	Click on Function App "Configuration" under Settings 
   c.	Click on "Schedule" under "Application Settings"
   d.	Update your own schedule using cron expression.
   ```
   **Note: For a `TimerTrigger` to work, you provide a schedule in the form of a [cron expression](https://en.wikipedia.org/wiki/Cron#CRON_expression)(See the link for full details). A cron expression is a string with 6 separate expressions which represent a given schedule via patterns. The pattern we use to represent every 10 minutes is `0 */10 * * * *`. This, in plain text, means: "When seconds is equal to 0, minutes is divisible by 10, for any hour, day of the month, month, day of the week, or year".**

4. Verify Temp folder path
	 ```
	a.	Go to your Resource Group --> Click on Function App `docusign<<uniqueid>>`
	b.	Click on "Advanced Tools" under Development Tools 
	c.	Click on Go --> You will be redirected to Web App --> Check Temp folder path. 
	d.	It can be either C:\local\Temp\ or D:\local\Temp\.
	 ```
5. After finding Temp folder path
	```
	a.	Go to your Resource Group --> Click on Function App `docusign<<uniqueid>>`
	b.	Click on "Configuration" under Settings
	c.	Click on "TMPDIR" under "Application Settings"
	d.	Update Drive (C//D) based on your findings from Step 9.
	```
	**Note: Make sure the value in "TMPDIR" doesnt have "\\" at the end.**

6. **For Azure Gov customers only**, You will see additional environment variable "Azure Tenant" under "Configuration" --> "Application Settings" and its default    
   value is ".us"
   
   Currently this Function App supports "Azure Gov(.US)" tenants
   Ex: https://portal.azure.us
