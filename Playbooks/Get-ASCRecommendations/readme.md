# Get-ASCRecommendations
author: Nicholas DiCola

This playbook will take each Host entity and If its an Azure Resource, query ASC API to get any ASC recommendations.  It will add a tag and comment if any unhealthy recommendations are found for the resource.

**NOTE:  This playbook uses a managed identity to access the API.  You will need to add the playbook to the subscriptions or management group with Security Reader Role**

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-ASCRecommendations%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-ASCRecommendations%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>
