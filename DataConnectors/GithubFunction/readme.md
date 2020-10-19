# Ingest GitHub AuditLog and API Data
Author: Nicholas DiCola, Sreedhar Ande

 Get-GitHubData Azure Function ingests the following logs from GitHub
 1. AuditLog via (GraphQL)[https://developer.github.com/v4/interface/auditentry/] events and writes them to a custom log table called GitHub_CL.  
 2. Traffic Logs [https://developer.github.com/v3/repos/traffic/] data and writes them to a custom log table called GitHubRepoLogs_CL. 
 3. Security Vulnerability logs [https://developer.github.com/v4/object/securityvulnerability/] data and writes them to a custom log table called GitHubRepoLogs_CL

Following are the configuration steps to deploy Function App.

## Configuration Steps
1. Generate a GitHub (Personal Access Token)[https://github.com/settings/tokens].  GitHub user settings -> Developer settings -> Personal access tokens.
2. Deploy the ARM template and fill in the parameters.
```
"PersonalAccessToken": This is the GITHUB PAT​
"workspaceId": The Sentinel Workspace ID​
"workSpaceKey": The Sentinel Workspace Key
"TimeInterval": Time Interval
 ```
4. There are two json files (ORGS.json and lastrun-Audit.json).
5. Edit the ORGS.json file and update "org": "sampleorg" and replace sample org with your org name.  If you have addtional orgs, add another line {"org": "sampleorg"} for each org.
6. Upload the ORGS.json, and lastrun-Audit.json to the storage account githublogicapp container.
7. The Azure Function got deployed as disabled since the json files has to be uploaded into the Storage Account.  Go to Function App and click Enable.

Note: there are two parsers (here)[https://github.com/Azure/Azure-Sentinel/tree/master/Parsers/GitHub] to make the logs useful

## Deploy the Logic App template
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fandedevsecops%2FAzure-Sentinel%2Faz-func-github-dataconnector%2FDataConnectors%2FGithubFunction%2Fazuredeploy_GitHubData.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fandedevsecops%2FAzure-Sentinel%2Faz-func-github-dataconnector%2FDataConnectors%2FGithubFunction%2Fazuredeploy_GitHubData.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>
