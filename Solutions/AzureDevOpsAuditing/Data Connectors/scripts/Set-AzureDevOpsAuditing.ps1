[CmdletBinding()]
param (
    [Parameter(Mandatory = $false,
        Position = 0)]
    [string]$WorkspaceId,

    [Parameter(Mandatory = $false,
        Position = 1)]
    [string]$WorkspaceKey,

    [Parameter(Mandatory = $true,
        Position = 2)]
    [string]$Organization,

    [Parameter(Mandatory = $false,
        Position = 3)]
    [string]$PersonalAccessToken,

    [Parameter(Mandatory = $false)]
    [string]$workspaceName,

    [Parameter(Mandatory = $false)]
    [string]$VaultName
)

Write-Output "Validating if required module is installed"
$AzModule = Get-Module -Name Az.Accounts -ErrorAction SilentlyContinue

if ($null -eq $AzModule) {
    Write-Warning "The Az PowerShell module is not found"
    #check for Admin Privleges
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())

    if (-not ($currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))) {
        #Not an Admin, install to current user
        Write-Warning -Message "Can not install the Az module. You are not running as Administrator"
        Write-Warning -Message "Installing Az module to current user Scope"
        Install-Module Az -Scope CurrentUser -Force -Repository PSGallery
    }
    else {
        #Admin, install to all users
        Write-Warning -Message "Installing the Az module to all users"
        Install-Module -Name Az -Force -Repository PSGallery
        Import-Module -Name Az -Force
    }
}

if ($workspaceName) {
    Write-Output "Retrieving Log Analytics workspace [$($WorkspaceName)]"

    try {
    Write-Output "Looking for requested workspace [$($WorkspaceName)]"
    $workspace = Get-AzResource `
        -Name "$WorkspaceName" `
        -ResourceType 'Microsoft.OperationalInsights/workspaces'

    Write-Output "Workspace properties: $($workspace.name)"

        $_resourceGroupName  = $workspace.ResourceGroupName
        $_workspaceName      = $workspace.Name

        Write-Output "retrieving Workspace Id"
        $workspaceId = (Get-AzOperationalInsightsWorkspace -ResourceGroupName $_resourceGroupName -Name $_workspaceName).CustomerId.Guid

        Write-Output "workspaceId found $($workspaceId)"

       # Ignoring the message for now.
        Set-Item Env:\SuppressAzurePowerShellBreakingChangeWarnings "true"
        $workspaceKey = (Get-AzOperationalInsightsWorkspaceSharedKeys -ResourceGroupName $_resourceGroupName -Name $_workspaceName).PrimarySharedKey

        $PersonalAccessToken = Get-AzKeyVaultSecret -VaultName $VaultName -Name PersonalAccessToken -AsPlainText
    }
    catch {
        Write-Warning -Message "Log Analytics workspace [$($WorkspaceName)] not found in the current context"
        break
    }
}

# Creating POST request for Azure DevOps
$uri = 'https://auditservice.dev.azure.com/{0}/_apis/audit/streams?daysToBackfill=0&api-version=6.0-preview.1' -f $organization

$headers = @{
    "Authorization" = "Basic $([System.Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(":$PersonalAccessToken")))"
    "Content-Type"  = "application/json"
}

    $payload = @{
        consumerType   = 'AzureMonitorLogs'
        consumerInputs = @{
            WorkspaceId = $WorkspaceId
            SharedKey   = $workspaceKey
        }
    } | ConvertTo-Json -Depth 10

$defaultHttpSettings = @{
    useBasicParsing = $true
    contentType     = "application/json"
    Uri             = $uri
    headers         = $headers
    Method          = "POST"
}

Invoke-RestMethod @defaultHttpSettings -Body $payload
