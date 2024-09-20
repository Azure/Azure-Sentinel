# Isolate-AzureVMtoNSG
author: Nathan Swift

This playbook will take host entites from triggered incident and search for matches in the enterprises subscriptions. An email for approval will be sent to isolate Azure VM. Upon approval a new NSG Deny All is created and applied to the Azure VM, The Azure VM is restarted to remove any persisted connections.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FIsolate-AzureVMtoNSG%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FIsolate-AzureVMtoNSG%2Fazuredeploy.json)

**Additional Post Install Notes:**

The Logic App creates and uses a Managed System Identity (MSI) to search the Azure Resource Graph, Generate a NSG, Update the VM with NSG, and Restart the VM. 

Assign RBAC 'Reader' role to the Logic App at the root Management Group level.
Assign RBAC 'Network Contributor' role to the Logic App at the root Management Group level.
Assign RBAC 'Virtual Machine Contributor' role to the Logic App at the root Management Group level.