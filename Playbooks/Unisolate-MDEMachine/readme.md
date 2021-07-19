# Unisolate-MDEMachine
author: Nicholas DiCola

This playbook will release a machine from isolation in Microsoft Defender for Endpoint.

## Quick Deployment
**Deploy with incident trigger** (recommended)

After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)]("https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FUnisolate-MDEMachine%2Fincident-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)]("https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FUnisolate-MDEMachine%2Fincident-trigger%2Fazuredeploy.json)

**Deploy with alert trigger**

After deployment, you can run this playbook manually on an alert or attach it to an **analytics rule** so it will rune when an alert is created.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)]("https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FUnisolate-MDEMachine%2Falert-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)]("https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FUnisolate-MDEMachine%2Falert-trigger%2Fazuredeploy.json)

## Prerequisites

- You will need to grant Machine.Isolate permissions to the managed identity.  Run the following code replacing the managed identity object id.  You find the managed identity object id on the Identity blade under Settings for the Logic App.
```powershell
$MIGuid = "<Enter your managed identity guid here>"
$MI = Get-AzureADServicePrincipal -ObjectId $MIGuid

$MDEAppId = "fc780465-2017-40d4-a0c5-307022471b92"
$PermissionName = "Machine.Isolate" 

$MDEServicePrincipal = Get-AzureADServicePrincipal -Filter "appId eq '$MDEAppId'"
$AppRole = $MDEServicePrincipal.AppRoles | Where-Object {$_.Value -eq $PermissionName -and $_.AllowedMemberTypes -contains "Application"}
New-AzureAdServiceAppRoleAssignment -ObjectId $MI.ObjectId -PrincipalId $MI.ObjectId `
-ResourceId $MDEServicePrincipal.ObjectId -Id $AppRole.Id
```

## Screenshots
**Incident Trigger**<br>
![Incident Trigger](./incident-trigger/images/designerLight.png)<br>
**Alert Trigger**<br>
![Alert Trigger](./alert-trigger/images/Unisolate-MDEMachine_alert.png)<br>
