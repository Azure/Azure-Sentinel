function Get-ResourceGroupName {
    param (
        [string]$promptMessage
    )
    $automationResourceGroupName = Read-Host -Prompt $promptMessage
    return $automationResourceGroupName.Trim()
}

$logicAppNames = @('logic-app-disable-data-aging', 'logic-app-disable-saml-provider', 'logic-app-disable-user')
Connect-AzAccount -UseDeviceAuthentication 

$selectedSubscription = Get-AzContext | Select-Object -ExpandProperty Subscription

if (-not $selectedSubscription) {
    $subscriptions = Get-AzSubscription
    $subscriptions | ForEach-Object -Begin { $script:i = 0 } -Process { Write-Host "$($script:i): $($_.Name)"; $script:i++ }

    $subscriptionIndex = Get-ResourceGroupName -Prompt "Enter the number of the subscription you want to use"
    $selectedSubscription = $subscriptions[$subscriptionIndex]
}

if (-not $selectedSubscription) {
    Write-Host "Invalid subscription number. Please run the script again and enter a valid subscription number."
    exit
}

Set-AzContext -SubscriptionId $selectedSubscription.Id

$keyVaultName = Get-ResourceGroupName -Prompt "Enter the name of the key vault"
$selectedKeyVault = Get-AzKeyVault -VaultName $keyVaultName

if (-not $selectedKeyVault) {
    Write-Host "Invalid key vault number. Please run the script again and enter a valid key vault number."
    exit
}

$automationResourceGroupName = Get-ResourceGroupName -promptMessage "Enter the resource group name for the Log Analytics workspace"

foreach ($logicAppName in $logicAppNames) {
    $AllLogicApps = (Get-AzResource -ResourceType "Microsoft.Logic/workflows" | Where-Object { $_.Name -eq $logicAppName })
    foreach ($selectedLogicApp in $AllLogicApps){
        try {
            $roleDefinition = Get-AzRoleDefinition -Name "Automation Job Operator"

            $automationAccountName = "Commvault-Automation-Account"
            
            New-AzRoleAssignment -ObjectId $selectedLogicApp.Identity.PrincipalId -RoleDefinitionId $roleDefinition.Id -Scope "/subscriptions/$($selectedSubscription.Id)/resourceGroups/$automationResourceGroupName/providers/Microsoft.Automation/automationAccounts/$automationAccountName"

            $isRbacEnabled = (Get-AzKeyVault -VaultName $selectedKeyVault.VaultName).EnableRbacAuthorization
            if($isRbacEnabled) {
                $keyVaultId = (Get-AzKeyVault -VaultName $selectedKeyVault.VaultName).ResourceId
                New-AzRoleAssignment -ObjectId $selectedLogicApp.Identity.PrincipalId -RoleDefinitionName "Key Vault Secrets User" -Scope $keyVaultId
            }
            else {
                Set-AzKeyVaultAccessPolicy -VaultName $keyVaultName -ObjectId $selectedLogicApp.Identity.PrincipalId -PermissionsToSecrets get
            }

        }
        catch {
            Write-Host "An error occurred: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}
