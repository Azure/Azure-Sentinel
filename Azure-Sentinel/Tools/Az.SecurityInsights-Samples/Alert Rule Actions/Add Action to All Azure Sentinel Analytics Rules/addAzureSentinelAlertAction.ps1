param (
    [parameter(Mandatory = $true)]
    #The subscription that holds your Azure Sentinel workspace
    [string] $subscriptionId,
    [parameter(Mandatory = $true)]
    # The resource group name which holds your Azure Sentinel workspace
    [string] $sentinelRG,
    [parameter(Mandatory = $true)]
    # The Azure Sentinel workspace name
    [string] $workspaceName,
    [parameter(Mandatory = $true)]
    # The name of the Logic App to use for the rules
    [string] $logicAppName,
    [parameter(Mandatory = $false)]
    # The resource group name which holds your Logic App. If not specified, the Sentinel resource group name is assumed.
    [string] $logicAppRG = $sentinelRG,
    [parameter(Mandatory = $false)]
    # The name of the Logic App trigger. If not specified, the default trigger name "When_a_response_to_an_Azure_Sentinel_alert_is_triggered" is used.
    [string] $triggerName = "When_a_response_to_an_Azure_Sentinel_alert_is_triggered"
)

# PowerShell version detection, module detection, and subscription context logic used from: 
# https://github.com/Azure/Azure-Sentinel/blob/master/Tools/Az.SecurityInsights-Samples/Alert%20Rules/Export%20Analytics%20Rules/exportAzureSentinelRules.ps1

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

try {
    #Get the Logic App and its trigger URI
    $logicapp = Get-AzLogicApp -ResourceGroupName $logicAppRG -Name $logicAppName
    $triggerUri = Get-AzLogicAppTriggerCallbackUrl -ResourceGroupName $logicAppRG -Name $logicAppName -TriggerName $triggerName

    #Get the active rules from the Sentinel workspace
    $rules = Get-AzSentinelAlertRule -ResourceGroupName $sentinelRG -WorkspaceName $workspaceName
    foreach($rule in $rules)
    {
        #Don't try to add the action to rules where Kind==Error
        if($rule.Kind -eq "Error")
        {
            Write-Warning "Skipping rule $($rule.Name) because rule is of kind Error"
        }
        else
        {
            #Check to make sure the rule doesn't already have an action for this app, since each rule can only have one instance of an action
            $applyAction = $true
            $actions = Get-AzSentinelAlertRuleAction -ResourceGroupName $sentinelRG -WorkspaceName $workspaceName -AlertRuleId $($rule.Name)
            foreach($action in $actions)
            {
                if($($action.LogicAppResourceId) -eq $($logicapp.Id)) {
                    Write-Warning "Skipping rule $($rule.Name) because it already contains an action for this Logic App."
                    $applyAction = $false
                    break
                }
            }
            
            if($applyAction) {
                #Apply the action to the rule
                Write-Host "Adding action to $($rule.Name)"
                New-AzSentinelAlertRuleAction -ResourceGroupName $sentinelRG -WorkspaceName $workspaceName -AlertRuleId $($rule.Name) -LogicAppResourceId $($logicapp.Id) -TriggerUri $($triggerUri.Value)
            }
        }
    }
}
catch {
    Write-Warning "An error occured while trying to add actions: $($_.Exception.Message)"
    break
}
