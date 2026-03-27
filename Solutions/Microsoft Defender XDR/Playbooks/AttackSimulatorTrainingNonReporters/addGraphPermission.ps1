#Requires -Module Microsoft.Graph.Authentication,Microsoft.Graph.Applications

# This script grants the necessary Microsoft Graph API permissions to the Service Principal after initial installation
# Install the required modules using: Install-Module -Name Microsoft.Graph.Authentication,Microsoft.Graph.Applications

# Variables
$ManagedIdentity = "" # Enter the Name or GUID of the Managed Identity on the Logic App here, otherwise it will prompted to be entered during execution


# Begin Script
Connect-MgGraph -ContextScope Process -Scopes 'Application.ReadWrite.All' | Out-Null
Write-Host "Connected to Graph" -ForegroundColor Green

# Prompt for the details of the managed identity from the logic app if not already provided
if ($ManagedIdentity -eq "") {
    Write-Host ""
    $ManagedIdentity = Read-Host -Prompt "Enter the DisplayName (default: TriggerASTNonReporting) or GUID of the Managed Identity"
}

# Match whether it's a GUID which can be easily retrieved from the Logic App itself. Otherwise assume that what has been entered is a string for the Display Name.
if ($ManagedIdentity -match '(?im)^[{(]?[0-9A-F]{8}[-]?(?:[0-9A-F]{4}[-]?){3}[0-9A-F]{12}[)}]?$') {
    $MI = Get-MgServicePrincipal -Filter "Id eq '$ManagedIdentity'"
} else {
    $MI = Get-MgServicePrincipal -Filter "DisplayName eq '$ManagedIdentity'"
}


If ($MI) {
    # Get Microsoft Graph SPN
    $GraphSPN = Get-MgServicePrincipal -Filter "AppId eq '00000003-0000-0000-c000-000000000000'"
    Write-Host ""

    $PermissionName = "SecurityIncident.Read.All"
    Write-Host "Adding $PermissionName to Service Principal"
    $AppRole = $GraphSPN.AppRoles | Where-Object {$_.Value -eq $PermissionName -and $_.AllowedMemberTypes -contains "Application"}
    Try { New-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $MI.Id -PrincipalId $MI.Id -ResourceId $GraphSPN.Id -AppRoleId $AppRole.Id -ErrorAction Stop | Out-Null } Catch {}


    $PermissionName = "SecurityAlert.Read.All"
    Write-Host "Adding $PermissionName to Service Principal"
    $AppRole = $GraphSPN.AppRoles | Where-Object {$_.Value -eq $PermissionName -and $_.AllowedMemberTypes -contains "Application"}
    Try { New-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $MI.Id -PrincipalId $MI.Id -ResourceId $GraphSPN.Id -AppRoleId $AppRole.Id -ErrorAction Stop | Out-Null } Catch {}


    $PermissionName = "ThreatHunting.Read.All"
    Write-Host "Adding $PermissionName to Service Principal"
    $AppRole = $GraphSPN.AppRoles | Where-Object {$_.Value -eq $PermissionName -and $_.AllowedMemberTypes -contains "Application"}
    Try { New-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $MI.Id -PrincipalId $MI.Id -ResourceId $GraphSPN.Id -AppRoleId $AppRole.Id -ErrorAction Stop | Out-Null } Catch {}


    $PermissionName = "AttackSimulation.ReadWrite.All"
    Write-Host "Adding $PermissionName to Service Principal"
    $AppRole = $GraphSPN.AppRoles | Where-Object {$_.Value -eq $PermissionName -and $_.AllowedMemberTypes -contains "Application"}
    Try { New-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $MI.Id -PrincipalId $MI.Id -ResourceId $GraphSPN.Id -AppRoleId $AppRole.Id -ErrorAction Stop | Out-Null } Catch {}

    Write-Host ""
    Write-Host "Complete. Disconnecting from Graph." -ForegroundColor Green

    Disconnect-MgGraph | Out-Null

} else {
    Write-Error "Get-MgServicePrincipal was unable to retrieve the Service Principal"
}
