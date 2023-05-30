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

function Write-Log {
    param ([string]$message, [switch]$isError)

    $severityLevel = if ($isError) {2} else {4} 
    $appinsightsTraceBody = @"
{
    "name": "Microsoft.ApplicationInsights.Event",
    "time": "$(Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffffffZ")",
    "iKey": "84e09db4-d430-41e8-97a6-c6a821010cc6",
    "tags":{
    },
    "data": {
       "baseType": "MessageData",
       "baseData": {
          "ver": 2,
          "message": "$message",
          "severityLevel": $severityLevel,
          "properties": {
                "WorkspaceId": "$WorkspaceId",
                "SubscriptionId": "$SubscriptionId"
           }
        }
    }
}
"@
    try { # Send trace to Appinsights
        Invoke-WebRequest -Uri https://dc.services.visualstudio.com/v2/track -Method POST -Body $appinsightsTraceBody | out-null -SilentlyContinue
    } catch {}

	if ($isError)
    {
        Write-Host $message -ForegroundColor Red
    }
    else
    {
        Write-Host $message
    }
}

function TryRegisterProviders {
        param ([string]$userName)
    try
    {
        $providers = Get-AzResourceProvider -ProviderNamespace Microsoft.CloudShell,Microsoft.KeyVault
        $cloudSehllRegistered = ($providers | Where {$_.ProviderName -eq "Microsoft.CloudShell" && $_.RegistrationState -eq "Registered"}).Count -gt 0
        $keyVaultRegistered = ($providers | Where {$_.ProviderName -eq "Microsoft.KeyVault" && $_.RegistrationState -eq "Registered"}).Count -gt 0
        Write-Log "Resource Providers registrations validaion result: CloudShell Registered - $cloudSehllRegistered; KeyVault Registered - $keyVaultRegistered"

        if ($cloudSehllRegistered -ne $true || $keyVaultRegistered -ne $true) { # One of the registrations is missing. Try to Register.
            if((Get-AzRoleAssignment  -RoleDefinitionName "Contributor" -SignInName $userName -ExpandPrincipalGroups| Where-Object {$_.Scope -eq "/subscriptions/$SubscriptionId"}).Count -gt 0) {
                $cloudShellProvider = Register-AzResourceProvider -ProviderNamespace Microsoft.CloudShell | out-null
                $keyValutProvider = Register-AzResourceProvider -ProviderNamespace Microsoft.KeyVault | out-null
                Write-Log "Initiated CloudShell and KeyVault registreation. This might take some time. If the KeyVault deployment fails, try running the script again in a few minutes "
            } else {  # user doesn't have permissions to perform the registrations
                Write-Log "Resource Provider Registrations are missing and the user lacks Contributor Role over the subscription to perform the registrations. Deployment may fail until registrations are performed. Contant SentinelWidgets@microsoft.com for support" -isError
            }
        } 
    } catch {
        Write-Log "TryRegisterProviders Filed with exception: $_" -isError
    }
}

##############################################################################################
####  Main
##############################################################################################
$sub = Select-AzSubscription $SubscriptionId
Write-Log "Selected a subscription. Name - '$($($sub.Subscription).Name)'; Id - '$($($sub.Subscription).Id)'"
$userName = az account show --query user.name --output tsv

TryRegisterProviders $userName

$workspace = Get-AzOperationalInsightsWorkspace | where CustomerId -eq $WorkspaceId
if ($workspace -eq $null) {
    Write-Log "Failed to find a workspace with id '$WorkspaceId'. Fix the WorkspaceId or contant SentinelWidgets@microsoft.com for support. Aborting." -isError
    return
}

# Create the KV
$keyVaultName = Get-WigdetsKeyVaultName -workspaceId $WorkspaceId
if ((Get-AzKeyVault -Name $keyVaultName) -eq $null) { # KeyVault doesn't exist
    Write-Log "KeyValut Deployment in progress, please wait.."

    $wsResourceGroup = $workspace.ResourceGroupName;
     if((Get-AzRoleAssignment  -RoleDefinitionName "Contributor" -SignInName $userName -ExpandPrincipalGroups| Where-Object {$_.Scope -eq "/subscriptions/$SubscriptionId/resourceGroups/$wsResourceGroup"}).Count -gt 0) {
        Write-Log "User does not have a Contributor Role on the Resource Group '$wsResourceGroup' and can't create a KeyVault. Contant SentinelWidgets@microsoft.com for support. Aborting." -isError
        return
     }

    $keyVault = New-AzKeyVault -Name $keyVaultName -ResourceGroupName $wsResourceGroup -Location $workspace.Location -Tag @{WorkspaceId=$WorkspaceId} -WarningAction SilentlyContinue
    if ($keyVault -ne $null) {
	    Write-Log "Successfully Created a KeyValut named '$keyVaultName' for Sentinel Widgets"
    } else {
	   Write-Log "Failed to create a KeyValut named '$keyVaultName'. Contant SentinelWidgets@microsoft.com for support. Aborting." -isError
       return
  	}
}
else { # KeyVault Exists.
    Write-Log "KeyVault named '$keyVaultName' already exists, skipping to add Sentinel access to it"
}

Write-Log "Adding Access for Sentinel on the KeyVault.."
$sentinelAppObjectId = Get-SentinelApplicationObjectId
Write-Log "Sentinel's App ObjectId is '$sentinelAppObjectId'"

if ($sentinelAppObjectId -eq $null) {
	Write-Log "Failed to fetch Sentinel's App ObjectId and set access on the widgtes KeyValut to Sentinel. Contant SentinelWidgets@microsoft.com for support. Aborting." -isError
	return
}

# Add Access to Sentinel on the KeyVault
Set-AzKeyVaultAccessPolicy -VaultName $keyVaultName -ObjectId $sentinelAppObjectId -PermissionsToSecrets get,list

if ((Get-AzKeyVault -Name $keyVaultName | where {$_.AccessPolicies.ObjectId  -eq $sentinelAppObjectId}).Count -eq 1) {	
	Write-Log "Successfully Added AccessPolicy on your widgets' KeyVault to Sentinel"
} else {
    Write-Log "Failed to Add AccessPolicy on your widgets' KeyVault to Sentinel. Contant SentinelWidgets@microsoft.com for support. Aborting." -isError
}

# Add Access to the user on the KeyVault
Set-AzKeyVaultAccessPolicy -VaultName $keyVaultName -UserPrincipalName $userName -PermissionsToSecrets set,get,delete,list

if ((Get-AzKeyVault -Name $keyVaultName | where {$_.AccessPolicies.DisplayName -match $userName}).Count -eq 1) {	
	Write-Log "Successfully Added AccessPolicy on your widgets' KeyVault to the user"
} else {
    Write-Log "Failed to Add AccessPolicy on your widgets' KeyVault to the user. Contant SentinelWidgets@microsoft.com for support. Aborting." -isError
}