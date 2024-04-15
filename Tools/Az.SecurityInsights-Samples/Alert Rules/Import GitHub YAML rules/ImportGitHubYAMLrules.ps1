param (
    #The subscription that holds your Azure Sentinel workspace
    [parameter(Mandatory = $true)]
    [string] $subscriptionId,
    # The resource group name which holds your Azure Sentinel workspace
    [parameter(Mandatory = $true)]
    # The Azure Sentinel workspace name
    [string] $resourceGroupName,
    [parameter(Mandatory = $true)]
    [string] $workspaceName,
    # The import folder name where your rule files are in, for example C:\SentinelRules\Import
    [parameter(Mandatory = $true)]
    [string] $YAMLimportPath,
    # The full GitHub path, for example: https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Detections/ (notice the end backslash)
    [parameter(Mandatory = $true)]
    [string] $GitHubPath
)

$ErrorActionPreference = "Stop"

#Array - containing GitHub detection rules yaml files download - please the subfolder as well
$GitHubYAMLRulesToExport = @(
    "W3CIISLog/HAFNIUMSuspiciousExchangeRequestPattern.yaml",
    "MultipleDataSources/HAFNIUMUmServiceSuspiciousFile.yaml",
    "SecurityEvent/HAFNIUMNewUMServiceChildProcess.yaml",
    "SecurityEvent/HAFNIUMSuspiciousIMServiceError.yaml"
)

# Check powershell version, needs to be 5 or higher
if ($host.Version.Major -lt 5) {
    Write-Warning "Supported PowerShell version for this script is 5 or above"
    Write-Warning "Aborting...."
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
$AzAccountsModule = Get-Module -Name Az.Accounts
if ($AzAccountsModule -eq $null) {
    Write-Warning "Az.Accounts module has not been imported, trying to import...."
    Import-Module -Name Az.Accounts -Force
}

$subIdContext = (Get-AzContext).Subscription.Id 
if ($subIdContext -ne $subscriptionId) {
    $setSub = Set-AzContext -SubscriptionName $subscriptionId -ErrorAction SilentlyContinue
    if ($setSub -eq $Null) {
        Write-Warning "$subscriptionId is not set, please login"
        Login-AzAccount
        Set-AzContext -SubscriptionName $subscriptionId -ErrorAction SilentlyContinue
    }
}

# If not installed, import the PowerShell-YAML community module, installed from https://www.powershellgallery.com/packages/powershell-yaml/0.4.2
$powershellYamlModule = Get-Module -Name "powershell-yaml" -ErrorAction SilentlyContinue
if ($powershellYamlModule -eq $null) {
    Write-Warning "The PowerShell-YAML module is not found"
        #check for Admin Privleges
        $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())

        if (-not ($currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))) {
            #Not an Admin, install to current user
            Write-Warning -Message "Can not install the PowerShell-YAML module. You are not running as Administrator"
            Write-Warning -Message "Installing the PowerShell-YAML module to current user Scope"
            Install-Module powershell-yaml -Scope CurrentUser -Force
        }
        Else {
            #Admin, install to all users
            Write-Warning -Message "Installing the powershell-yaml module to all users"
            Install-Module -Name powershell-yaml -Force
            Import-Module -Name powershell-yaml -Force
        }
}

# Import the Az.SecurityInsights module
Import-Module -Name Az.SecurityInsights

# Create YAML import folder if it does not exist
if (!(Test-Path -Path $YAMLimportPath))
{
    Write-Warning ("Folder " + $YAMLimportPath + " does not exist, creating the folder for you....")
    New-Item -itemType Directory -Path $YAMLimportPath
}

# Save the GitHub YAML files separately to a folder as YAML files
foreach ($GitHubRule in $GitHubYAMLRulesToExport) {
    $GitHubRuleShortName = $GitHubRule.Substring($GitHubRule.IndexOf('/')+1)
    $myRuleObjectYAML = (New-Object System.Net.WebClient).DownloadString($GitHubPath + $GitHubRule)
    $myRuleObject = $myRuleObjectYAML | ConvertFrom-Yaml
    $myRuleObjectYAML | Out-File ($YAMLimportPath + "\" + $GitHubRuleShortName) -Force -Verbose
}
#endregion

#region Import local GitHub rules
$myNewRules = Get-ChildItem $YAMLimportPath -Filter *.yaml
#Stop if we don't have YAML rules found to import
if ($myNewRules -eq $null) {
    Write-Warning "Cannot find YAML rules to import, is your path correct?"
    break
}

foreach ($myNewRule in $myNewRules) {
    $myRuleObject = [pscustomobject](Get-Content $myNewRule.FullName -Raw | ConvertFrom-Yaml)
    $myRuleObject | Add-Member -MemberType NoteProperty -Name DisplayName -Value $myRuleObject.name

    #Since rules need to be created in the ISO 8601 duration format, we need to do conversion
    #Taking the last character, which represent the day, hr or minute unit
    $QueryFrequencyUnit = $myRuleObject.QueryFrequency.Substring($myRuleObject.QueryFrequency.Length - 1, 1)
    
    if ($QueryFrequencyUnit.EndsWith("d")){
        $QueryFrequencyValue = $myRuleObject.QueryFrequency.TrimEnd($QueryFrequencyUnit)
        #converting to minutes
        $QueryFrequencyValue = [int]$QueryFrequencyValue
        $QueryFrequencyValue = ($QueryFrequencyValue * 24) * 60

    }
     elseif ($QueryFrequencyUnit.EndsWith("h")) {
        $QueryFrequencyValue = $myRuleObject.QueryFrequency.TrimEnd($QueryFrequencyUnit)
        #converting to minutes
        $QueryFrequencyValue = [int]$QueryFrequencyValue
        $QueryFrequencyValue = ($QueryFrequencyValue * 60)

    }
     elseif ($QueryFrequencyUnit.EndsWith("m")) {
        $QueryFrequencyValue = $myRuleObject.QueryFrequency.TrimEnd($QueryFrequencyUnit)
    }
    #creating the ISO 8601 ticks value
    $QueryFrequencyTicks = New-TimeSpan -Minutes $QueryFrequencyValue 
    Write-Host ("Query Frequency: " + $QueryFrequencyTicks + "For rule: " + $myRuleObject.name)
    $QueryFrequencyTicks

    #QueryPeriodUnit
    $queryPeriodUnit = $myRuleObject.QueryPeriod.Substring($myRuleObject.queryPeriod.Length - 1, 1)

    if ($queryPeriodUnit.EndsWith("d")){
        $queryPeriodUnitValue = $myRuleObject.queryPeriod.TrimEnd($queryPeriodUnit)
        #converting to minutes
        $queryPeriodUnitValue = [int]$queryPeriodUnitValue
        $queryPeriodUnitValue = ($queryPeriodUnitValue * 24) * 60

    }
     elseif ($queryPeriodUnit.EndsWith("h")) {
        $queryPeriodUnitValue = $myRuleObject.queryPeriod.TrimEnd($queryPeriodUnit)
        #converting to minutes
        $queryPeriodUnitValue = [int]$queryPeriodUnitValue
        $queryPeriodUnitValue = ($queryPeriodUnitValue * 60)

    }
     elseif ($queryPeriodUnit.EndsWith("m")) {
        $queryPeriodUnitValue = $myRuleObject.queryPeriod.TrimEnd($queryPeriodUnit)
    }
    #creating the ISO 8601 ticks value
    $QueryPeriodTicks = New-TimeSpan -Minutes $queryPeriodUnitValue 
    Write-Host ("Query Period: " + $QueryPeriodTicks + "For rule: " + $myRuleObject.name)

    New-AzSentinelAlertRule -ResourceGroupName $resourceGroupName -WorkspaceName $workspaceName `
    -Scheduled -DisplayName $myRuleObject.DisplayName -Description $myRuleObject.Description -Query $myRuleObject.Query `
    -QueryFrequency $QueryFrequencyTicks -QueryPeriod $QueryPeriodTicks -Severity $myRuleObject.Severity -TriggerThreshold $myRuleObject.TriggerThreshold -Enabled
}
#endregion