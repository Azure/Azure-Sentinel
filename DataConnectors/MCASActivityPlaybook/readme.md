# Ingest MCAS (Microsoft Cloud App Security) Activities
Author: Nicholas DiCola

Get-MCASActivity playbook ingests MCAS Activities via (API)[https://docs.microsoft.com/cloud-app-security/api-activities-list] and writes them to a custom log table called MCASActivity_CL.

There are a number of configuration steps required to deploy the Logic App playbooks.

## Configuration Steps
1. Generate a MCAS (API Token)[https://docs.microsoft.com/cloud-app-security/api-authentication].  Settings -> Security Extensions -> API tokens.
2. Deploy the ARM template and fill in the parameters.
```
"APIToken": This is the MCAS API Token​
"MCASURL": This is the MCAS URL.  See About in the portal for specfici url.
"workspaceId": The Sentinel Workspace ID​
"workSpaceKey": The Sentinel Workspace Key
 ```
3. There is a json file (lastrun-MCAS.json).
4. Upload the lastrun-MCAS.json to the storage account mcasactivitylogicapp container.
5. Get the Storage Access Key
6. Go to the azureblob-MCASActivity connection resource.
7. Click Edit API Connection.
8. Enter the storage account name and access key.  Click Save.
9. The playbooks are deployed as disabled since the json file and connection has to be authorized.  Go to the playbook and click Enable.

Note: there is a parsers (here)[https://github.com/Azure/Azure-Sentinel/tree/master/Parsers/MCAS] to make the logs more readable

## Deploy the Logic App template
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)]("https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FMCASActivityPlaybook%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)]("https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FMCASActivityPlaybook%2Fazuredeploy.json)