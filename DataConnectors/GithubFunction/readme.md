# Ingest GitHub AuditLog and API Data
Author: Nicholas DiCola, Sreedhar Ande

 GitHubLogs Azure Function ingests the following logs from GitHub
 1. AuditLog via (GraphQL)[https://developer.github.com/v4/interface/auditentry/] events and writes them to a custom log table called GitHub_CL.  
 2. Traffic Logs [https://developer.github.com/v3/repos/traffic/] data and writes them to a custom log table called GitHubRepoLogs_CL. 
 3. Security Vulnerability logs [https://developer.github.com/v4/object/securityvulnerability/] data and writes them to a custom log table called GitHubRepoLogs_CL

Following are the configuration steps to deploy Function App.

## Configuration Steps
1. Generate a GitHub (Personal Access Token)[https://github.com/settings/tokens].  GitHub user settings -> Developer settings -> Personal access tokens.
2. Deploy the ARM template and fill in the parameters.
```
"PersonalAccessToken": This is the GITHUB PAT​
"Workspace Id": The Sentinel Log Analytics Workspace Id​
"Workspace Key": The Sentinel Log Analytics Workspace Key
 ```
4. There are two json files (ORGS.json and lastrun-Audit.json).
5. Edit the ORGS.json file and update "org": "sampleorg" and replace sample org with your org name.  If you have addtional orgs, add another line 
```
{"org": "sampleorg1"} 
{"org": "sampleorg2"}
.
.
.
```
for each org.

6. Upload the following files to the storage account "github-repo-logs" container.
```
ORGS.json
lastrun-Audit.json
```

7. PersonalAccessToken and Workspace Key will be placed as "Secrets" in the Azure KeyVault "githubkv<uniqueid>" with only Azure Function access policy. If you want to see/update these secrets,

```
    a. Go to Azure KeyVault "githubkv<uniqueid>"
    b. Click on "Access Policies" under Settings
    c. Click on "Add Access Policy"
        i. Configure from template : Secret Management
        ii. Key Permissions : GET, LIST, SET
        iii. Select Prinicpal : <<Your Account>>
        iv. Add
    d. Click "Save"

```

8. The `TimerTrigger` makes it incredibly easy to have your functions executed on a schedule. This sample demonstrates a simple use case of calling your function every 5 minutes.

9. For a `TimerTrigger` to work, you provide a schedule in the form of a [cron expression](https://en.wikipedia.org/wiki/Cron#CRON_expression)(See the link for full details). A cron expression is a string with 6 separate expressions which represent a given schedule via patterns. The pattern we use to represent every 5 minutes is `0 */5 * * * *`. This, in plain text, means: "When seconds is equal to 0, minutes is divisible by 5, for any hour, day of the month, month, day of the week, or year".


Note: there are two parsers (here)[https://github.com/Azure/Azure-Sentinel/tree/master/Parsers/GitHub] to make the logs useful

## Deploy the Logic App template
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FGithubFunction%2Fazuredeploy_GitHubFunctionApp.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FGithubFunction%2Fazuredeploy_GitHubFunctionApp.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>
