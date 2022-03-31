# Block-AADUserOrAdmin
author: Benjamin Kovacevic

This playbook will disable the user in Azure Active Directory and add a comment to the incident. There is an option for incident and alert trigger below.<br>
If user have active admin assigment, approval process will be sent to selected email/emails. For users with eligible admin assigment, disabling process will be the same as for the regular user.<br>
Note: Admin user will be disabled and approval will be sent after admin is disabled to approve or reject disabling process. Reject will re-enable admin, while Approve will leave admin disabled. If approval/rejection is not confirmed in 30 minutes, admin user will be disabled and notification will be sent.<br>
If admin or regular user have manager, manager will be notified that user/admin has been disabled in Azure AD.<br><br>
Note: This playbook will have high privilages and will be able to disable all admins, including the Global Admins in the process. Be careful not to lock yourself out!<br>
If you don't want that playbook have option to disable admin users, please use Block-AADUser playbook!

## Quick Deployment
**Deploy with incident trigger** (recommended)

After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FBlock-AADUserOrAdmin%2Fincident-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FBlock-AADUserOrAdmin%2Fincident-trigger%2Fazuredeploy.json)

**Deploy with alert trigger**

After deployment, you can run this playbook manually on an alert or attach it to an **analytics rule** so it will rune when an alert is created.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FBlock-AADUserOrAdmin%2Falert-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FBlock-AADUserOrAdmin%2Falert-trigger%2Fazuredeploy.json)<br><br>

## Prerequisites
Available email account to whom approval to confirm or reject admin isolation will be sent. 

## Post-deployment
1. Assign Microsoft Sentinel Responder role to the Playbook's managed identity - https://docs.microsoft.com/azure/logic-apps/create-managed-service-identity?tabs=consumption#assign-managed-identity-role-based-access-in-the-azure-portal
2. Assign API permissions to the managed identity so that we can search for user's manager. You can find the managed identity object ID on the Identity blade under Settings for the Logic App. If you don't have Azure AD PowerShell module, you will have to install it and connect to Azure AD PowerShell module. https://docs.microsoft.com/powershell/azure/active-directory/install-adv2?view=azureadps-2.0
```powershell
$MIGuid = "<Enter your managed identity guid here>"
$MI = Get-AzureADServicePrincipal -ObjectId $MIGuid

$GraphAppId = "00000003-0000-0000-c000-000000000000"
$PermissionName1 = "User.Read.All"
$PermissionName2 = "User.ReadWrite.All"
$PermissionName3 = "Directory.Read.All"
$PermissionName4 = "Directory.ReadWrite.All"

$GraphServicePrincipal = Get-AzureADServicePrincipal -Filter "appId eq '$GraphAppId'"
$AppRole1 = $GraphServicePrincipal.AppRoles | Where-Object {$_.Value -eq $PermissionName1 -and $_.AllowedMemberTypes -contains "Application"}
New-AzureAdServiceAppRoleAssignment -ObjectId $MI.ObjectId -PrincipalId $MI.ObjectId `
-ResourceId $GraphServicePrincipal.ObjectId -Id $AppRole1.Id

$AppRole2 = $GraphServicePrincipal.AppRoles | Where-Object {$_.Value -eq $PermissionName2 -and $_.AllowedMemberTypes -contains "Application"}
New-AzureAdServiceAppRoleAssignment -ObjectId $MI.ObjectId -PrincipalId $MI.ObjectId `
-ResourceId $GraphServicePrincipal.ObjectId -Id $AppRole2.Id

$AppRole3 = $GraphServicePrincipal.AppRoles | Where-Object {$_.Value -eq $PermissionName3 -and $_.AllowedMemberTypes -contains "Application"}
New-AzureAdServiceAppRoleAssignment -ObjectId $MI.ObjectId -PrincipalId $MI.ObjectId `
-ResourceId $GraphServicePrincipal.ObjectId -Id $AppRole3.Id

$AppRole4 = $GraphServicePrincipal.AppRoles | Where-Object {$_.Value -eq $PermissionName4 -and $_.AllowedMemberTypes -contains "Application"}
New-AzureAdServiceAppRoleAssignment -ObjectId $MI.ObjectId -PrincipalId $MI.ObjectId `
-ResourceId $GraphServicePrincipal.ObjectId -Id $AppRole4.Id
```

3. Assign Global Administrator role to the managed identity. From Azure Active Directory > Roles and administrators, search for Global Administrator and assign role to the playbook Managed Identity (Block-AADUserOrAdmin-Incident or Block-AADUserOrAdmin-Alert)
4. Open the playbook in the Logic App Designer and authorize Azure AD and Office 365 Outlook Logic App connections<br><br>

## Screenshots
**Incident Trigger**<br>
![Incident Trigger](./incident-trigger/images/IncidentTriggerDark.png)
![Incident Trigger light](./incident-trigger/images/IncidentTriggerLight.png)<br><br>
**Alert Trigger**<br>
![Alert Trigger](./alert-trigger/images/AlertTriggerDark.png)
![Alert Trigger light](./alert-trigger/images/AlertTriggerLight.png)<br><br>
**Email notification to manager**<br>
![Manager notification](./images/managerNotificationDark.png)
![Manager notification light](./images/managerNotificationLight.png)