$logicAppNames = @('logic-app-disable-data-aging', 'logic-app-disable-saml-provider', 'logic-app-disable-user')
Connect-AzAccount -UseDeviceAuthentication 

$selectedSubscription = Get-AzContext | Select-Object -ExpandProperty Subscription

if (-not $selectedSubscription) {
    Connect-AzAccount -UseDeviceAuthentication 
    # List all subscriptions and assign a number to each subscription
    $subscriptions = Get-AzSubscription
    $subscriptions | ForEach-Object -Begin { $script:i = 0 } -Process { Write-Host "$($script:i): $($_.Name)"; $script:i++ }

    # Prompt user to select a subscription by number
    $subscriptionIndex = Read-Host -Prompt "Enter the number of the subscription you want to use"
    $selectedSubscription = $subscriptions[$subscriptionIndex]
}

if (-not $selectedSubscription) {
    Write-Host "Invalid subscription number. Please run the script again and enter a valid subscription number."
    exit
}

# Set the selected subscription
Set-AzContext -SubscriptionId $selectedSubscription.Id
# List all resource groups in the selected subscription and assign a number to each resource group
$resourceGroups = Get-AzResourceGroup
$resourceGroups | ForEach-Object -Begin { $script:i = 0 } -Process { Write-Host "$($script:i): $($_.ResourceGroupName)"; $script:i++ }

# Prompt user to select a resource group by number
$resourceGroupIndex = Read-Host -Prompt "Enter the number of the resource group you want to use"
$selectedResourceGroup = $resourceGroups[$resourceGroupIndex]

if (-not $selectedResourceGroup) {
    Write-Host "Invalid resource group number. Please run the script again and enter a valid resource group number."
    exit
}

# Set the resource group name
$resourceGroupName = $selectedResourceGroup.ResourceGroupName

# List all key vaults in the selected resource group and assign a number to each key vault
$keyVaults = Get-AzKeyVault -ResourceGroupName $resourceGroupName
$keyVaults | ForEach-Object -Begin { $script:i = 0 } -Process { Write-Host "$($script:i): $($_.VaultName)"; $script:i++ }

# Prompt user to select a key vault by number
$keyVaultIndex = Read-Host -Prompt "Enter the number of the key vault you want to use"
$selectedKeyVault = $keyVaults[$keyVaultIndex]

if (-not $selectedKeyVault) {
    Write-Host "Invalid key vault number. Please run the script again and enter a valid key vault number."
    exit
}

# Set the key vault name
$keyVaultName = $selectedKeyVault.VaultName

foreach ($logicAppName in $logicAppNames) {
    $selectedLogicApp = (Get-AzResource -ResourceGroupName $resourceGroupName -ResourceType "Microsoft.Logic/workflows" | Where-Object { $_.Name -eq $logicAppName })[0]

    if (-not $selectedLogicApp) {
        Write-Host "Logic app $logicAppName not found in the resource group $resourceGroupName."
        continue
    }

    if (-not $selectedLogicApp) {
        Write-Host "Logic app $logicAppName not found in the resource group $resourceGroupName."
        continue
    }

    # Assign the role "Automation Job Operator" to the selected logic app on the automation account
    $roleDefinition = Get-AzRoleDefinition -Name "Automation Job Operator"

    # Retrieve the object ID of the selected logic app using the Azure Resource Manager
    $logicAppResource = Get-AzResource -ResourceId $selectedLogicApp.ResourceId

    $automationAccountName = "Commvault-Automation-Account"

    New-AzRoleAssignment -ObjectId $logicAppResource.Identity.PrincipalId -RoleDefinitionId $roleDefinition.Id -Scope "/subscriptions/$($selectedSubscription.Id)/resourceGroups/$resourceGroupName/providers/Microsoft.Automation/automationAccounts/$automationAccountName"

    Set-AzKeyVaultAccessPolicy -VaultName $keyVaultName -ObjectId $logicAppResource.Identity.PrincipalId -PermissionsToSecrets get

}
