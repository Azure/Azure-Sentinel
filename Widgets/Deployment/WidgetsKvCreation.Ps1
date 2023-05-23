# This script is part of "Sentinel's Widgets" onboarding process, and should be ran by the user within Azure Cloud Shell.
# The script creates a KeyVault under the customer subscription, and provides Sentinel access to the KeyVault.
# The KeyVault will hold the customr keys, that are required to fetch the data which is presented in the sidgets.

param (
        # The Sentinel's subscription Id (Guid). Can be found under Sentinel instance => "Settings" => "Workspace settings" => "Essentials"
        [Parameter(Mandatory = $true)]
        [string]$SubscriptionId,
        
        # The Sentinel's workspace Id (Guid). Can be found under Sentinel instance => "Settings" => "Workspace settings" => "Essentials"
        [Parameter(Mandatory = $true)]
        [string]$WorkspaceId
    )

function Get-WigdetsKeyVaultName {
    param ([string]$workspaceId)

    $hash = [System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($workspaceId))
    $uniqueHash = [System.BitConverter]::ToString($hash) -replace "-", ""
    $keyVaultName = "widgets-$($uniqueHash.Substring(0, 16))".ToLower()
	
    return $keyVaultName
}

function Get-SentinelApplicationObjectId {
    $sentinelAppId = "98785600-1bb7-4fb9-b9fa-19afe2c8a360" 
    # 'Connect-AzureAD' throws errors when runs in Cloud shell form Ps1 script - https://github.com/Azure/CloudShell/issues/72
    import-module AzureAD.Standard.Preview
    AzureAD.Standard.Preview\Connect-AzureAD -Identity -TenantID $env:ACC_TID | out-null

    $sentinelAppObjectId = ((Get-AzureADServicePrincipal -Filter "AppId eq  '$sentinelAppId'") ?? (New-AzureADServicePrincipal -AppId $sentinelAppId)).ObjectId

    return $sentinelAppObjectId
}

function Print-Error {
    param ([string]$text)
	Write-Host $text -ForegroundColor Red
}

##############################################################################################
####  Main
##############################################################################################
$sub = Select-AzSubscription $SubscriptionId
Register-AzResourceProvider -ProviderNamespace Microsoft.CloudShell | out-null

"Selected a subscription. Name - '$($($sub.Subscription).Name)'; Id - '$($($sub.Subscription).Id)'"
$workspace = Get-AzOperationalInsightsWorkspace | where CustomerId -eq $WorkspaceId
if ($workspace -eq $null) {
    Print-Error "Failed to find a workspace with id '$WorkspaceId'. Fix the WorkspaceId or contant SentinelWidgets@microsoft.com for support. Aborting."
    return
} 

$keyVaultName = Get-WigdetsKeyVaultName -workspaceId $WorkspaceId
if ((Get-AzKeyVault -Name $keyVaultName) -eq $null) { # KeyVault doesn't exist
    "KeyValut Deployment in progress, please wait.."
    $keyVault = New-AzKeyVault -Name $keyVaultName -ResourceGroupName $workspace.ResourceGroupName -Location $workspace.Location -Tag @{WorkspaceId=$WorkspaceId} -WarningAction SilentlyContinue
    if ($keyVault -ne $null) {
	    "Successfully Created a KeyValut named '$keyVaultName' for Sentinel Widgets"
    } else {
		Print-Error "Failed to create a KeyValut named '$keyVaultName'. Contant SentinelWidgets@microsoft.com for support. Aborting."
       return
  	}
}
else { # KeyVault Exists.
    "KeyVault named '$keyVaultName' already exists, skipping to add Sentinel access to it"
}

"Adding Access for Sentinel on the KeyVault.."
$sentinelAppObjectId = Get-SentinelApplicationObjectId
"Sentinel's App ObjectId is '$sentinelAppObjectId'"

if ($sentinelAppObjectId -eq $null) {
	Print-Error "Failed to fetch Sentinel's App ObjectId and set access on the widgtes KeyValut to Sentinel. Contant SentinelWidgets@microsoft.com for support. Aborting.."
	return
}

Set-AzKeyVaultAccessPolicy -VaultName $keyVaultName -ObjectId $sentinelAppObjectId  -PermissionsToSecrets get,list

if ((Get-AzKeyVault -Name $keyVaultName | where {$_.AccessPolicies.ObjectId  -eq $sentinelAppObjectId}).Count -eq 1) {	
	"Successfully Added AccessPolicy on your widgets KeyVault to Sentinel"
}
else {
    Print-Error "Failed to Add AccessPolicy on your widgets KeyVault to Sentinel. Contant SentinelWidgets@microsoft.com for support. Aborting.."
}

