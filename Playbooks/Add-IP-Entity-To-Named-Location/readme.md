# Add-IP-Entity-To-Named-Location

author: Brian Delaney

This playbook will execute using an incident based trigger and add the IP entities to a Conditional Access Named Location

## Quick Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAdd-IP-Entity-To-Named-Location%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAdd-IP-Entity-To-Named-Location%2Fazuredeploy.json)

## Prerequisites

- None

## After Deployment

- Grant the Logic App Managed Identity access to the Mirosoft Graph Policy.Read.All & Policy.ReadWrite.ConditionalAccess which can be done with the included PowerShell script [AddApiPermissions.ps1](./AddApiPermissions.ps1)
- Attach this playbook to an **automation rule** so it runs when specified incidents are created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)
                                                                                                                                     
## Screenshots
![Designer](./images/designer-light.jpg)
