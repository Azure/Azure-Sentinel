# Id of Azure Automation Account's Managed Identity
Param (
    $MIIDParam = $null,
    $TenantId = $null,
    [switch] $InteractiveAuth
)

$MI_ID = "XXXXXXXXXXX"
if ($TenantId) { Write-Warning "Trying to connect to Graph API using Tenant $TenantId."}
else { Write-Warning "TenantId parameter is not filled. Connexion to Graph API without explicitly target a tenant."}

if ($InteractiveAuth) 
{ 
    if ($null -eq $TenantId) { Connect-MgGraph -Scopes AppRoleAssignment.ReadWrite.All,Application.Read.All}
    else { Connect-MgGraph -Scopes AppRoleAssignment.ReadWrite.All,Application.Read.All -TenantId $TenantId }
} 
else
{
    if ($null -eq $TenantId) { Connect-MgGraph -Scopes AppRoleAssignment.ReadWrite.All,Application.Read.All -UseDeviceAuthentication }
    else { Connect-MgGraph -Scopes AppRoleAssignment.ReadWrite.All,Application.Read.All -UseDeviceAuthentication -TenantId $TenantId }
}

if ($null -ne $MIIDParam) { $MI_ID = $MIIDParam }

$GraphAppId = "00000003-0000-0000-c000-000000000000"
$ExchangeAppId = "00000002-0000-0ff1-ce00-000000000000"

$GraphServicePrincipal = Get-MgServicePrincipal -Filter "appId eq '$GraphAppId'"
$ResourceID = Get-MgServicePrincipal -Filter "AppId eq '$ExchangeAppId'"

# Graph API
$AzureRoleIDs = ($GraphServicePrincipal.AppRoles | Where-Object {
        $_.Value -match "^user.read.all" -or $_.Value -match "group.read.all" -or $_.Value -match "AuditLog.Read.All"
    }) | select id, @{label='scopeId';Expression={$GraphServicePrincipal.Id}}


# Exchange Online
$AppRoleID = "dc50a0fb-09a3-484d-be87-e023b12c6440"
$AzureRoleIDs += [PSCustomObject]@{'Id'=$AppRoleID;'scopeId'=$ResourceID.Id}

# Permissions Assignment
$AzureRoleIDs | ForEach-Object{
    New-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $MI_ID -PrincipalId $MI_ID `
        -ResourceId $_.ScopeId -AppRoleId $_.Id
}