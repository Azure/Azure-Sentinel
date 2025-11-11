<#
.SYNOPSIS
    Assign RBAC roles to the Logic App's Managed Identity at the root of a Tenant.

.DESCRIPTION
    Assign RBAC roles to the Logic App's Managed Identity at the root of a Tenant.
    This script can be modified to assign RBAC roles MG at a more granular level by changing the $Scope variable.

    DIRECTIONS:
    ----------
    1. Open in PowerShell ISE.
    2. Update the variables in 'Variables' section to match your environment per the accompanying documentation.
    3. Select text and run (F8) applicable portions of the script in an interactive manner.
    
    NOTE: Rollback Procedures are also provided if the RBAC roles are to be removed.
#>

###########################################################################################################
# VARIABLES: Update to match your environment
###########################################################################################################
$AzEnvironment = "AzureCloud"                              # Adjust to match target Azure fabric: (Get-AzEnvironment).Name
$DFIRSubscription = "98765432-10fe-9876-fedc-ba0987654321" # DFIR Subscription hosting the snapshots
$LogicApp = "SOC-Isolate-AzVM"                             # Name of the Logic App that was created
$RoleName = "Disk Snapshot Initiator"                      # Name of the custom Azure role to be created for snapshot initiation

###########################################################################################################
# Implementation Procedures
###########################################################################################################

# 1. Connect to Azure
# ---------------------------------------------------------------------------------------------------------

Import-Module Az.Resources
Get-AzEnvironment
Connect-AzAccount -Environment $AzEnvironment
Get-AzContext
$Tenant = (Get-AzContext).Tenant
$Scope = "/providers/Microsoft.Management/managementGroups/$Tenant" # Target scope for where the roles will be assigned

# 2. Create custom Azure role with least privileges to initiate snapshots
# ---------------------------------------------------------------------------------------------------------
# https://learn.microsoft.com/en-us/azure/virtual-machines/disks-restrict-import-export-overview

Write-Host "Creating custom Azure role: $RoleName" -ForegroundColor Yellow

# Initialize the role definition
$role = [Microsoft.Azure.Commands.Resources.Models.Authorization.PSRoleDefinition]::new()
$role.Name = $RoleName
$role.Description = 'Allows access to initiate disk snapshots.'
$role.IsCustom = $true

# Initialize the Actions property
$role.Actions = @(
    "Microsoft.Compute/disks/beginGetAccess/action",     # Get Disk SAS URI
    "Microsoft.Compute/disks/endGetAccess/action",       # Revoke Disk SAS URI
    "Microsoft.Compute/snapshots/beginGetAccess/action", # Get Snapshot SAS URI
    "Microsoft.Compute/snapshots/endGetAccess/action"    # Revoke Snapshot SAS URI
)

# Initialize the AssignableScopes property
$role.AssignableScopes = @("$Scope")

# Create the custom role definition
New-AzRoleDefinition -Role $role

# Verify custom role creation (but first wait up to 60 seconds as there's a slight delay between creation and public view)
Get-AzRoleDefinition -Name "$RoleName" -Scope $Scope

# 3. Assign RBAC roles to the Logic App's Managed Identity
# ---------------------------------------------------------------------------------------------------------

$MI = Get-AzADServicePrincipal -DisplayName $LogicApp
Write-Host "Assigning RBAC roles to" $MI.DisplayName -ForegroundColor Yellow
New-AzRoleAssignment -ObjectId $MI.Id -Scope $Scope -RoleDefinitionName "Reader"
New-AzRoleAssignment -ObjectId $MI.Id -Scope $Scope -RoleDefinitionName "Network Contributor"
New-AzRoleAssignment -ObjectId $MI.Id -Scope $Scope -RoleDefinitionName "Virtual Machine Contributor"
New-AzRoleAssignment -ObjectId $MI.Id -Scope $Scope -RoleDefinitionName "$RoleName"
New-AzRoleAssignment -ObjectId $MI.Id -Scope "/subscriptions/$DFIRSubscription" -RoleDefinitionName "Disk Snapshot Contributor"

# Check RBAC role assignments
Write-Host $MI.DisplayName "now has the following roles:" -ForegroundColor Yellow
Get-AzRoleAssignment -ObjectId $MI.Id -Scope $Scope | Select-Object RoleDefinitionName, Scope
Get-AzRoleAssignment -ObjectId $MI.Id -Scope "/subscriptions/$DFIRSubscription" | Select-Object RoleDefinitionName, Scope | Format-Table -AutoSize



###########################################################################################################
# Rollback Procedures
###########################################################################################################

# 1. Connect to Azure
# ---------------------------------------------------------------------------------------------------------

Import-Module Az.Resources
Get-AzEnvironment
Connect-AzAccount -Environment $AzEnvironment
Get-AzContext
$Tenant = (Get-AzContext).Tenant
$Scope = "/providers/Microsoft.Management/managementGroups/$Tenant" # Target scope for where the roles were assigned

# 2. Remove RBAC roles from the Logic App's Managed Identity
# ---------------------------------------------------------------------------------------------------------
$MI = Get-AzADServicePrincipal -DisplayName $LogicApp
Write-Host "Removing RBAC roles for" $MI.DisplayName -ForegroundColor Yellow
Remove-AzRoleAssignment -ObjectId $MI.Id -Scope $Scope -RoleDefinitionName "Reader"
Remove-AzRoleAssignment -ObjectId $MI.Id -Scope $Scope -RoleDefinitionName "Network Contributor"
Remove-AzRoleAssignment -ObjectId $MI.Id -Scope $Scope -RoleDefinitionName "Virtual Machine Contributor" 
Remove-AzRoleAssignment -ObjectId $MI.Id -Scope $Scope -RoleDefinitionName "$RoleName"
Remove-AzRoleAssignment -ObjectId $MI.Id -Scope "/subscriptions/$DFIRSubscription" -RoleDefinitionName "Disk Snapshot Contributor"

# Check RBAC role removal
Get-AzRoleAssignment -ObjectId $MI.Id

# 3. Remove custom Azure role with least privileges to initiate snapshots
# ---------------------------------------------------------------------------------------------------------
Write-Host "Removing custom Azure role: $RoleName" -ForegroundColor Yellow
Get-AzRoleDefinition -Name "$RoleName" -Scope $Scope | Remove-AzRoleDefinition -Force

