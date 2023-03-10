# This script grants the necessary Microsoft Graph API permissions to the Service Principal.
# Before running, change the $TenantID (line5) to your AAD Tenant ID and the $DisplayNameofMSI (line6) to the name of your Logic App
# This script requires the AzureAD Powershell Module,  Install-Module AzureAD

$TenantID=""  #AAD Tenant Id
$DisplayNameOfMSI="Add-IP-Entity-To-Named-Location" # Name of the managed identity

Connect-AzureAD -TenantId $TenantID

$MSI = (Get-AzureADServicePrincipal -Filter "displayName eq '$DisplayNameOfMSI'")

Start-Sleep -Seconds 5

#Microsoft Graph API - Policy.Read.All
$GraphAppId = "00000003-0000-0000-c000-000000000000"
$PermissionName = "Policy.Read.All" 
$GraphServicePrincipal = Get-AzureADServicePrincipal -Filter "appId eq '$GraphAppId'"
$AppRole = $GraphServicePrincipal.AppRoles | Where-Object {$_.Value -eq $PermissionName -and $_.AllowedMemberTypes -contains "Application"}
New-AzureAdServiceAppRoleAssignment -ObjectId $MSI.ObjectId -PrincipalId $MSI.ObjectId -ResourceId $GraphServicePrincipal.ObjectId -Id $AppRole.Id

Start-Sleep -Seconds 5

#Microsoft Graph API - Policy.ReadWrite.ConditionalAccess
$GraphAppId = "00000003-0000-0000-c000-000000000000"
$PermissionName = "Policy.ReadWrite.ConditionalAccess" 
$GraphServicePrincipal = Get-AzureADServicePrincipal -Filter "appId eq '$GraphAppId'"
$AppRole = $GraphServicePrincipal.AppRoles | Where-Object {$_.Value -eq $PermissionName -and $_.AllowedMemberTypes -contains "Application"}
New-AzureAdServiceAppRoleAssignment -ObjectId $MSI.ObjectId -PrincipalId $MSI.ObjectId -ResourceId $GraphServicePrincipal.ObjectId -Id $AppRole.Id

#  Disconnect-AzureAD
