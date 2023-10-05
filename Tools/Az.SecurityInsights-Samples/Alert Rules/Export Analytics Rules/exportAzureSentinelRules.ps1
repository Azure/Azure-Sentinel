param (
    [parameter(Mandatory = $true)]
    #The subscription that holds your Azure Sentinel workspace
    [string] $subscriptionId,
    [parameter(Mandatory = $true)]
    # The resource group name which holds your Azure Sentinel workspace
    [string] $resourceGroupName,
    [parameter(Mandatory = $true)]
    # The Azure Sentinel workspace name
    [string] $workspaceName,
    [parameter(Mandatory = $true)]
    # The export folder name where your rules will be exported to, for example C:\SentinelRules\Export
    [string] $ruleExportPath
)

$ErrorActionPreference = "Stop"

# Check powershell version, needs to be 5 or higher
if ($host.Version.Major -lt 5) {
    Write-Host "Supported PowerShell version for this script is 5 or above" -ForegroundColor Red
    Write-Host "Aborting...." -ForegroundColor Red
    break
}

#Check if the Az.SecurityInsights module is installed, if not install it
#This will auto install the Az.Accounts module if it is not installed
$AzSecurityInsightsModule = Get-InstalledModule -Name Az.SecurityInsights -ErrorAction SilentlyContinue
if ($AzSecurityInsightsModule -eq $null) {
    Write-Warning "The Az.SecurityInsights PowerShell module is not found"
        #check for Admin Privleges
        $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())

        if (-not ($currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))) {
            #Not an Admin, install to current user
            Write-Warning -Message "Can not install the Az.SecurityInsights module. You are not running as Administrator"
            Write-Warning -Message "Installing Az.SecurityInsights module to current user Scope"
            Install-Module Az.SecurityInsights -Scope CurrentUser -Force
        }
        Else {
            #Admin, install to all users
            Write-Warning -Message "Installing the Az.SecurityInsights module to all users"
            Install-Module -Name Az.SecurityInsights -Force
            Import-Module -Name Az.SecurityInsights -Force
        }
}

#Check the Azure subscription context
$subIdContext = (Get-AzContext).Subscription.Id 
if ($subIdContext -ne $subscriptionId) {
    $setSub = Set-AzContext -SubscriptionName $subscriptionId -ErrorAction SilentlyContinue
    if ($setSub -eq $Null) {
        Write-Warning "$subscriptionId is not set, please login and run this script again"
        Login-AzAccount
        break
    }
}

# Create folder if it does not exist
if (!(Test-Path -Path $ruleExportPath))
{
    Write-Warning ("Folder " + $ruleExportPath + " does not exist, creating the folder for you....")
    New-Item -itemType Directory -Path $ruleExportPath
}

# Export Scheduled Rules
try {
    $rules = Get-AzSentinelAlertRule -ResourceGroupName $resourceGroupName -WorkspaceName $workspaceName | Where-Object {$_.Kind -eq "Scheduled"} 
    Write-Host ("Exporting " + $rules.count + " Scheduled rules...") -ForegroundColor Yellow
    $rules | ConvertTo-Json -Depth 15 | Out-File ($ruleExportPath + "\" + "Scheduled.json") -Force
}
catch {
    Write-Warning "Either your Azure connection is invalid or your Azure Sentinel settings are incorrect"
    Write-Warning $_.Exception.Message
    break
}


# Export Fusion Rules
try {
    $rules = Get-AzSentinelAlertRule -ResourceGroupName $resourceGroupName -WorkspaceName $workspaceName | Where-Object {$_.Kind -eq "Fusion"} 
    Write-Host ("Exporting " + $rules.count + " Fusion rules...") -ForegroundColor Yellow
    $rules | ConvertTo-Json -Depth 15 | Out-File ($ruleExportPath + "\" + "Fusion.json") -Force
}
catch {
    Write-Warning "Either your Azure connection is invalid or your Azure Sentinel settings are incorrect"
    Write-Warning $_.Exception.Message
    break
}

# Export MicrosoftSecurityIncidentCreation Rules
try {
    $rules = Get-AzSentinelAlertRule -ResourceGroupName $resourceGroupName -WorkspaceName $workspaceName | Where-Object {$_.Kind -eq "MicrosoftSecurityIncidentCreation"} 
    Write-Host ("Exporting " + $rules.count + " MicrosoftSecurityIncidentCreation rules...") -ForegroundColor Yellow
    $rules | ConvertTo-Json -Depth 15 | Out-File ($ruleExportPath + "\" + "MicrosoftSecurityIncidentCreation.json") -Force
}
catch {
    Write-Warning "Either your Azure connection is invalid or your Azure Sentinel settings are incorrect"
    Write-Warning $_.Exception.Message
    break
}

Write-Host ("Azure Analytics Rules are exported to " + $ruleExportPath) -ForegroundColor Yellow