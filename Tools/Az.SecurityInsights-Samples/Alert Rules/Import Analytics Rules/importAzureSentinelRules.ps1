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
    # The import folder name where your rule files are in, for example C:\SentinelRules\Import
    [string] $ruleImportPath,
    [parameter(Mandatory = $true)]
    # The filename of your Scheduled rules, like Scheduled.json
    [string] $ScheduleRules,
    [parameter(Mandatory = $true)]
    # The filename of your Fusion rules, like Fusion.json
    [string] $FusionRules,
    [parameter(Mandatory = $true)]
    # The filename for your Microsoft Security Incident Creation Rules, like SecurityIncidentCreationRules.json
    [string] $SecurityIncidentCreationRules
)

$ErrorActionPreference = "Stop"

# Check powershell version, needs to be 5 or higher
if ($host.Version.Major -lt 5) {
    Write-Warning "Supported PowerShell version for this script is 5 or above"
    Write-Warning "Aborting...."
    break
}

#Check if the Az.SecurityInsights module is installed, if not install it
# This will auto install the Az.Accounts module if it is not installed
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

#region - Import Scheduled Rules
Write-Host "Trying to import Scheduled rules..." -ForegroundColor Yellow

$scheduledRulesExist = $false
try {
    $newScheduledRules = Get-Content ($ruleImportPath + "\" + $ScheduleRules) -Raw | ConvertFrom-Json
    $scheduledRulesExist = $true
}
catch {
    Write-Warning $_.Exception.Message
    Write-Warning "Skipping Scheduled rules...."
    
}

if ($scheduledRulesExist -eq $true) {
    Write-Host ("Importing Scheduled rules from: " + ($ruleImportPath + "\" + $ScheduleRules)) -ForegroundColor Yellow

    foreach ($newScheduledRule in $newScheduledRules) {
 
        $NewRuleObject = @{
            DisplayName = $newScheduledRule.DisplayName
            Query = $newScheduledRule.Query
            QueryPeriod = $newScheduledRule.QueryPeriod.Ticks
            QueryFrequency = $newScheduledRule.QueryFrequency.Ticks
            TriggerThreshold = $newScheduledRule.TriggerThreshold
            Severity = $newScheduledRule.Severity
            SuppressionDuration = $newScheduledRule.SuppressionDuration.Ticks
            SuppressionEnabled = $newScheduledRule.SuppressionEnabled
            TriggerOperator = $newScheduledRule.TriggerOperator
            Scheduled = $true
            Enabled = $newScheduledRule.Enabled
        }
    
        if ($newScheduledRule.Description -ne "") {
            $NewRuleObject += @{Description = $newScheduledRule.Description}
        }

        #creating an array to store Tactics
        [System.Collections.Generic.List[System.String]]$TacticObject = @()
        foreach ($Tactic in $newScheduledRule.Tactics) {
            $TacticObject.Add($Tactic)
        }

        #Check if no Tactics are configured, if not we don't passs the -Tactic parameter
        Write-Host ("Adding rule: " + $newScheduledRule.DisplayName) -ForegroundColor Yellow
        if ($TacticObject.Count -eq 0) {
            write-host "No Tactics found" -ForegroundColor Green
            New-AzSentinelAlertRule -ResourceGroupName $resourceGroupName -WorkspaceName $workspaceName @NewRuleObject
        }
        else {
            New-AzSentinelAlertRule -ResourceGroupName $resourceGroupName -WorkspaceName $workspaceName @NewRuleObject -Tactic $TacticObject
        }
    }
}
#endregion

#region - Import MicrosoftSecurityIncidentCreation Rules
Write-Host "Trying to import Microsoft Security Incident rules..." -ForegroundColor Yellow
$SecurityIncidentCreationRulesExist = $false
try {
    $newIncidentCreationRules = Get-Content ($ruleImportPath + "\" + $SecurityIncidentCreationRules) -Raw | ConvertFrom-Json
    $SecurityIncidentCreationRulesExist = $true
}
catch {
    Write-Warning $_.Exception.Message
    Write-Warning "Skipping Microsoft Security Incident rules...."
}
if ($SecurityIncidentCreationRulesExist -eq $true) {
    Write-Host ("Importing MicrosoftSecurityIncidentCreation rules from: " + ($ruleImportPath + "\" + $SecurityIncidentCreationRules)) -ForegroundColor Yellow
    foreach ($newIncidentCreationRule in $newIncidentCreationRules) {
     
        $NewRuleObject = @{
            DisplayName                       = $newIncidentCreationRule.DisplayName
            ProductFilter                     = $newIncidentCreationRule.ProductFilter
            MicrosoftSecurityIncidentCreation = $true
            Enabled                           = $true
        }
        if ($Description) { $NewRuleObject.Description = $Description } #Only add value if not null or empty
        if ($DisplayNamesFilter) { $NewRuleObject.DisplayNamesFilter = $DisplayNamesFilter } #Only add value if not null or empty
        if ($DisplayNamesExcludeFilter) { $NewRuleObject.DisplayNamesExcludeFilter = $DisplayNamesExcludeFilter } #Only add value if not null or empty
        if ($SeveritiesFilter) { $NewRuleObject.SeveritiesFilter = $SeveritiesFilter = @() } #Only add value if not null or empty
        if ($AlertRuleTemplateName) { $NewRuleObject.AlertRuleTemplateName = $AlertRuleTemplateName } #Only add value if not null or empty
    
        Write-Host ("Adding rule: " + $newIncidentCreationRule.DisplayName) -ForegroundColor Yellow
        New-AzSentinelAlertRule -ResourceGroupName $resourceGroupName -WorkspaceName $workspaceName @NewRuleObject
    }
}
#endregion

#region - Import Fusion Rules
Write-Host "Trying to import Fusion rules..." -ForegroundColor Yellow
$FusionRulesExist = $false
try {
    $newFusionRules = Get-Content ($ruleImportPath + "/" + $FusionRules) -Raw | ConvertFrom-Json
    $FusionRulesExist = $true
}
catch {
    Write-Warning $_.Exception.Message
    Write-Warning "Skipping Fusion rules...."
    
}

if ($FusionRulesExist -eq $true) {
    Write-Host ("Importing Fusion rules from: " + ($ruleImportPath + "/" + $FusionRules)) -ForegroundColor Yellow
    foreach ($newFusionRule in $newFusionRules) {
     
        $NewRuleObject = @{
            alertRuleTemplateName = $newFusionRule.AlertRuleTemplateName
            AlertRuleId           = (New-Guid)
            Fusion                = $true
            Enabled               = $true
        }
        if ($Description) { $NewRuleObject.Description = $Description } #Only add value if not null or empty
    
        Write-Host ("Adding rule: " + $newFusionRule.DisplayName) -ForegroundColor Yellow
        New-AzSentinelAlertRule -ResourceGroupName $resourceGroupName -WorkspaceName $workspaceName @NewRuleObject
    }
}
#endregion
Write-Host "Done!" -ForegroundColor Yellow
