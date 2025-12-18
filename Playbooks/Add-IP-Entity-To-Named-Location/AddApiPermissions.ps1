# This script grants the necessary Microsoft Graph API permissions to the Service Principal.
# Before running, change the $TenantID (line5) to your Entra ID Tenant ID and the $DisplayNameofMSI (line6) to the name of your Logic App
# This script requires the Microsoft.Graph PowerShell Module: Install-Module Microsoft.Graph -Scope CurrentUser

$TenantID=""  #Entra ID Tenant Id
$DisplayNameOfMSI="Add-IP-Entity-To-Named-Location" # Name of the managed identity

Connect-MgGraph -TenantId $TenantID -Scopes "Application.Read.All", "AppRoleAssignment.ReadWrite.All"

$MSI = Get-MgServicePrincipal -Filter "displayName eq '$DisplayNameOfMSI'"

Start-Sleep -Seconds 5

#Microsoft Graph API - Policy.Read.All
$GraphAppId = "00000003-0000-0000-c000-000000000000"
$PermissionName = "Policy.Read.All" 
$GraphServicePrincipal = Get-MgServicePrincipal -Filter "appId eq '$GraphAppId'"
$AppRole = $GraphServicePrincipal.AppRoles | Where-Object {$_.Value -eq $PermissionName -and $_.AllowedMemberTypes -contains "Application"}
New-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $MSI.Id -PrincipalId $MSI.Id -ResourceId $GraphServicePrincipal.Id -AppRoleId $AppRole.Id

Start-Sleep -Seconds 5

#Microsoft Graph API - Policy.ReadWrite.ConditionalAccess
$GraphAppId = "00000003-0000-0000-c000-000000000000"
$PermissionName = "Policy.ReadWrite.ConditionalAccess" 
$GraphServicePrincipal = Get-MgServicePrincipal -Filter "appId eq '$GraphAppId'"
$AppRole = $GraphServicePrincipal.AppRoles | Where-Object {$_.Value -eq $PermissionName -and $_.AllowedMemberTypes -contains "Application"}
New-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $MSI.Id -PrincipalId $MSI.Id -ResourceId $GraphServicePrincipal.Id -AppRoleId $AppRole.Id

Disconnect-MgGraph
