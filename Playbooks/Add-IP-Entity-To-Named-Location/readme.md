# Add-IP-Entity-To-Named-Location

author: Brian Delaney

This playbook will execute using an incident based trigger and add the IP entities to a Conditional Access Named Location

## Quick Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FPlaybooks%2FAdd-IP-Entity-To-Named-Location%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Frefs%2Fheads%2Fmaster%2FPlaybooks%2FAdd-IP-Entity-To-Named-Location%2Fazuredeploy.json)

## Prerequisites

- None

## After Deployment

- Grant the Logic App Managed Identity access to the Microsoft Graph Policy.Read.All & Policy.ReadWrite.ConditionalAccess which can be done with the included PowerShell script [AddApiPermissions.ps1](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Standalone/Playbooks/Add-IP-Entity-To-Named-Location/AddApiPermissions.ps1)
- Attach this playbook to an **automation rule** so it runs when specified incidents are created.

[Learn more about automation rules](https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/Playbooks/Add-IP-Entity-To-Named-Location/AddApiPermissions.ps1)
  
## Screenshots
![Designer](https://github.com/Azure/Azure-Sentinel/blob/1b9d62978fc39278c2debbe8bc720b1d08d233d2/Playbooks/Add-IP-Entity-To-Named-Location/images/designer-light.jpg?raw=true)
