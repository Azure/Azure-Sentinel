# Ingest GitHub AuditLog and API Data
Author: Nicholas DiCola

Get-GitHubAuditEntry playbook ingests GitHub AuditLog via [GraphQL](https://developer.github.com/v4/interface/auditentry/) events and writes them to a custom log table called GitHub_CL.  Get-GitHubRepoLogs playbook ingests GitHub [Traffic Logs](https://developer.github.com/v3/repos/traffic/) data and writes them to a custom log table called GitHubRepoLogs_CL. Get-GitHubVulnerabilityAlerts playbook ingests GitHub [Security Vulnerability](https://developer.github.com/v4/object/securityvulnerability/) data and writes them to a custom log table called GitHubRepoLogs_CL

There are a number of configuration steps required to deploy the Logic App playbooks.

## Configuration Steps
1. Generate a GitHub [Personal Access Token](https://github.com/settings/tokens).  GitHub user settings -> Developer settings -> Personal access tokens.
2. Get the objectId for a user that the Logic App can use.  Azure Portal -> Azure Active Directory -> Users -> User.
This user will be used to grant access to the Key Vault secret.
3. Deploy the ARM template and fill in the parameters.
```
"PersonalAccessToken": This is the GITHUB PAT​
"UserName": A user that will be granted access to the key vault​
"principalId": The user object ID​ for the user
"workspaceId": The Sentinel Workspace ID​
"workSpaceKey": The Sentinel Workspace Key
 ```
4. There are two json files (`ORGS.json` and `lastrun-Audit.json`).
5. Edit the `ORGS.json` file and update `"org": "sampleorg"` and replace sample org with your org name.  If you have addtional orgs, add another line `{"org": "sampleorg"}` for each org.
6. Upload the `ORGS.json`, and `lastrun-Audit.json` to the storage account githublogicapp container.
7. Go to the `keyvault-GitHubPlaybooks` connection resource.
8. Click Edit API Connection.
9. Click Authorize.  Sign in as the user.  Click Save.
10. The playbooks are deployed as disabled since the json files and connection has to be authorized.  Go to each playbook and click Enable.

Note: there are two parsers [here](https://github.com/Azure/Azure-Sentinel/tree/master/Parsers/GitHub) to make the logs useful

## Deploy the Logic App template
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FGitHub%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FGitHub%2Fazuredeploy.json)
