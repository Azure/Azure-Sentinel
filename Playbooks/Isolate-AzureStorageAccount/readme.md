# Isolate-AzureStorageAccount
author: Ryan Graham

This playbook will take Storage Account host entites from triggered incident and search for matches in the enterprises subscriptions. An email for approval will be sent to isolate Azure Storage Account. Upon approval, the Storage Account firewall virtualNetworkRules and ipRules will be cleared, bypass rule set to None, and defaultAction set to Deny.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FIsolate-AzureStorageAccount%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FIsolate-AzureStorageAccount%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

**Additional Post Install Notes:**

The Logic App creates and uses a Managed System Identity (MSI) to search the Azure Resource Graph and update the Storage Account.

Assign RBAC 'Reader' role to the Logic App at the root Management Group level.
Assign RBAC 'Storage Account Contributor' role to the Logic App at the root Management Group level.