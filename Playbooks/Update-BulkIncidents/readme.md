# Update-BulkIncidents
authors: Priscila Viana, Nathan Swift

This Logic App will act as listener, you can pass json object to a HTTP Endpoint to use KQL query to discover Azure Sentinel Security Incidents through the SecurityIncident table you wish to bulk change on. It includes a method to selective update by array [].

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)]("https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FUpdate-BulkIncidents%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)]("https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FUpdate-BulkIncidents%2Fazuredeploy.json)

**Additional Post Install Notes:**

The Logic App requires the SecurityIncident Table preview

**Usage Notes**

To obtain your Logic App URI to make POST calls to, go to the Logic App designer mode and the first action and copy the URI 

<img src="https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/Update-BulkIncidents/images/logicappedit.png"/>

<img src="https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/Update-BulkIncidents/images/logicappuri.png"/>

You can use Postman, PowerShell, or your favorite shell to send a JSON body to the Logic App Endpoint. Below are some PowerShell code examples of usage.

At this time the Logic App can only bulk update the Status of Azure Sentinel Incidents.

```
<#

    Object parameters accepted are:

    operationtype - acceptable values are 'kql' or 'ids' | 'kql' = you will pass a parameter 'operationquery' with the kql language, those results will be passed to bulk update incidents | 'ids' = use an array list in parameter 'operationids'
    operationstatus - Closed, New, InProgress  
    operationkql - use a kql query to send results of Azure Sentinel Incidents to bulk update
    operationids - using an array list of Azure Sentinel Incident Ids/case numbers to bulk update

    See below for examples

#>

# Your URI from the Deployed LogicApp - 
$uri = "https://prod-38.eastus.logic.azure.com:443/workflows/r794bb6/triggers/request/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Frequest%2Frun&sv=1.0&sig=b_7K3GTyGxvJ2V"

# Header should be JSON
$header = @{'Content-Type' = 'application/json'}
```

```
## Example 1 using the KQL query to bulk update incidents

$json = @"
{  "bulkoperation": {
        "operationtype": "kql",
        "operationquery": "SecurityIncident | where TimeGenerated >= ago(7d) | where Status == 'New'",
        "operationstatus": "Closed"
    }
}
"@
```

```
## Example 2 using an array of incidents you want to update

$json = @"
{  "bulkoperation": {
        "operationtype": "ids",
        "operationids": [933, 934, 935, 935, 936],
        "operationstatus": "Closed"
    }
}
"@
```
