# Close-SelectiveBulkIncidents
authors: Priscila Viana, Nathan Swift

This Logic App will use a KQL query to discover Azure Sentinel Security Incidents through the SecurityIncident table you wish to bulk change on. It also includes a path for using the API to bulk change all

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FClose-SelectiveBulkIncidents%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FClose-SelectiveBulkIncidents%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

**Additional Post Install Notes:**

The Logic App requires the SecurityIncident Table preview | You need to change the KQL Query within the action to close selective Security incidents else it will bulk close all Incidents creates. There is a seprate path as well so if you want to bulk close all security incidents via API you can, need to turn on MSI and assign RBAC 'Reader' role to the Logic App at the RG of the Azure Sentinel Workspace.