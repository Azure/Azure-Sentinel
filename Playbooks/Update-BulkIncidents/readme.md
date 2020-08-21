# Update-BulkIncidents
authors: Priscila Viana, Nathan Swift

This Logic App will act as listner, you can pass json object to a HTTP Endpoint to use KQL query to discover Azure Sentinel Security Incidents through the SecurityIncident table you wish to bulk change on. It includes a method to slective update by array []. It also includes a method to bulk change all

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FUpdate-BulkIncidents%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FUpdate-BulkIncidents%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

**Additional Post Install Notes:**

The Logic App requires the SecurityIncident Table preview | You need to change the KQL Query within the action to close selective Security incidents else it will bulk close all Incidents creates. There is a seprate path as well so if you want to bulk close all security incidents via API you can, need to turn on MSI and assign RBAC 'Reader' role to the Logic App at the RG of the Azure Sentinel Workspace.

**Usage Notes**

You can use Postman, PowerShell, or your favorite shell to send a JSON body to the Logic App Endpoint. Below are some code examples of usage.

At this time the Logic App can only bulk update the Status of Azure Sentinel Incidents.

```
<#

    Object parameters accepted are:

    operationtype - acceptable values are 'kql' or 'ids' or 'all' | 'kql' = you will pass a parameter 'operationquery' with the kql language, those results will be passed to bulk update incidents | 'ids' = use an array list in parameter 'operationids'
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
        "operationstatus": "InProgress"
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
        "operationstatus": "New"
    }
}
"@
```

```
## Example 3 Bulk update all incidents

$json = @"
{  "bulkoperation": {
        "operationtype": "all",
        "operationstatus": "Closed"
    }
}
"@
```

```
# Invoke call to Logic App
Invoke-WebRequest -Uri $uri -Method Post -Body $json -Headers $header
```