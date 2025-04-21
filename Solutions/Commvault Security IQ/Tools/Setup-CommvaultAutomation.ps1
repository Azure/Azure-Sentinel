
Connect-AzAccount -UseDeviceAuthentication 


function Get-ResourceGroupName {
    param (
        [string]$promptMessage
    )
    $automationResourceGroupName = Read-Host -Prompt $promptMessage
    return $automationResourceGroupName.Trim()
}


$selectedSubscription = Get-AzContext | Select-Object -ExpandProperty Subscription

if (-not $selectedSubscription) {
    $subscriptions = Get-AzSubscription
    $subscriptions | ForEach-Object -Begin { $script:i = 0 } -Process { Write-Host "$($script:i): $($_.Name)"; $script:i++ }
    $subscriptionIndex = Read-Host -Prompt "Enter the number of the subscription you want to use"
    $selectedSubscription = $subscriptions[$subscriptionIndex]
}

if (-not $selectedSubscription) {
    Write-Host "Invalid subscription number. Please run the script again and enter a valid subscription number."
    exit
}


Set-AzContext -SubscriptionId $selectedSubscription.Id


$automationResourceGroupName = Get-ResourceGroupName -promptMessage "Enter the resource group name for the Automation Account"


$automationAccountName = "Commvault-Automation-Account"
$automationAccount = Get-AzAutomationAccount -ResourceGroupName $automationResourceGroupName -Name $automationAccountName -ErrorAction SilentlyContinue

if (-not $automationAccount) {
    New-AzAutomationAccount -ResourceGroupName $automationResourceGroupName -Name $automationAccountName -Location (Get-AzResourceGroup -Name $automationResourceGroupName).Location -Verbose
} else {
    Write-Host "Automation account $automationAccountName already exists."
}
function New-AndPublish-Runbook {
    param (
        [string]$runbookName,
        [string]$githubFileUrl
    )

    $existingRunbook = Get-AzAutomationRunbook -AutomationAccountName $automationAccountName `
                                               -ResourceGroupName $automationResourceGroupName `
                                               -Name $runbookName -ErrorAction SilentlyContinue

    if (-not $existingRunbook) {
        $pythonScriptContent = Invoke-WebRequest -Uri $githubFileUrl -UseBasicParsing
        $pythonScriptContent = $pythonScriptContent.Content

        New-AzAutomationRunbook -AutomationAccountName $automationAccountName `
                                -ResourceGroupName $automationResourceGroupName `
                                -Name $runbookName `
                                -Type "Python3" `
                                -Description "Runbook to disable $runbookName in Commvault" -Verbose | Out-Null

        $runbookPath = "$runbookName.py"
        $pythonScriptContent | Out-File -FilePath $runbookPath -Encoding utf8
        Import-AzAutomationRunbook -AutomationAccountName $automationAccountName `
                                   -ResourceGroupName $automationResourceGroupName `
                                   -Name $runbookName `
                                   -Path $runbookPath `
                                   -Type "Python3" -Force -Verbose | Out-Null

        Publish-AzAutomationRunbook -AutomationAccountName $automationAccountName `
                                    -ResourceGroupName $automationResourceGroupName `
                                    -Name $runbookName -Verbose
    } else {
        Write-Host "Runbook $runbookName already exists."
    }
}


New-AndPublish-Runbook -runbookName "Commvault_Disable_IDP" -githubFileUrl "https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/Solutions/Commvault%20Security%20IQ/Playbooks/Runbooks/Commvault_Disable_IDP.py"
New-AndPublish-Runbook -runbookName "Commvault_Disable_User" -githubFileUrl "https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/Solutions/Commvault%20Security%20IQ/Playbooks/Runbooks/Commvault_Disable_User.py"
New-AndPublish-Runbook -runbookName "Commvault_Disable_Data_Aging" -githubFileUrl "https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/Solutions/Commvault%20Security%20IQ/Playbooks/Runbooks/Commvault_Disable_Data_Aging.py"



$LogAnalyticsResourceGroupName = Get-ResourceGroupName -promptMessage "Enter the resource group name for the Log Analytics workspace"



$workspaces = Get-AzOperationalInsightsWorkspace -ResourceGroupName $LogAnalyticsResourceGroupName
$workspaces | ForEach-Object -Begin { $script:i = 0 } -Process { Write-Host "$($script:i): $($_.Name)"; $script:i++ }


$workspaceIndex = Read-Host -Prompt "Enter the number of the Log Analytics workspace you want to use, for Commvault Cloud sentinel solution"
$workspace = $workspaces[$workspaceIndex]

if (-not $workspace) {
    Write-Host "Invalid workspace number. Please run the script again and enter a valid workspace number."
    exit
}

$tableName = "CommvaultSecurityIQ_CL"

Write-Host "Starting table creation process..." -ForegroundColor Cyan


Write-Output "Getting Log Analytics workspace details..."
$workspaceId = $workspace.CustomerId
$workspaceName = $workspace.Name
$workspaceKey = (Get-AzOperationalInsightsWorkspaceSharedKey -ResourceGroupName $LogAnalyticsResourceGroupName -Name $workspaceName).PrimarySharedKey

Write-Output "Workspace ID: $workspaceId"
Write-Output "Workspace key retrieved successfully."

try {
   $sampleData = @(
        @{
            SourceSystem            = ""
            MG                      = ""
            ManagementGroupName     = ""
            TimeGenerated           = [DateTime]::Now
            Computer                = ""
            RawData                 = ""
            subclient_id          = 0
            files_list            = @()
            scanned_folder_list   = @()
            anomaly_sub_type      = ""
            severity              = ""
            originating_client    = ""
            user_id               = 0
            username              = ""
            affected_files_count  = 0
            job_start_time        = ""
            job_end_time          = ""
            job_id                = 0
            external_link         = ""
            description           = ""
            _ResourceId             = ""
        }
    )

    $jsonData = ConvertTo-Json -InputObject $sampleData -Compress

    $date = [DateTime]::UtcNow.ToString("r")
    $contentLength = $jsonData.Length
    $method = "POST"
    $contentType = "application/json"
    $resource = "/api/logs"

    $stringToHash = $method + "`n" + $contentLength + "`n" + $contentType + "`n" + "x-ms-date:" + $date + "`n" + $resource
    $bytesToHash = [Text.Encoding]::UTF8.GetBytes($stringToHash)
    $keyBytes = [Convert]::FromBase64String($workspaceKey)
    $hmacsha256 = New-Object System.Security.Cryptography.HMACSHA256
    $hmacsha256.Key = $keyBytes
    $calculatedHash = $hmacsha256.ComputeHash($bytesToHash)
    $encodedHash = [Convert]::ToBase64String($calculatedHash)
    $authorization = "SharedKey {0}:{1}" -f $workspaceId, $encodedHash

    $uri = "https://" + $workspaceId + ".ods.opinsights.azure.com/api/logs?api-version=2016-04-01"
    $headers = @{
        "Authorization" = $authorization
        "Log-Type" = $TableName
        "x-ms-date" = $date
        "time-generated-field" = "TimeGenerated"
    }

    $response = Invoke-RestMethod -Uri $uri -Method POST -ContentType $contentType -Headers $headers -Body $jsonData
    Write-Output "Response from Data Collector API: $($response | ConvertTo-Json -Compress)"
    Write-Output "Table created successfully using Data Collector API."
}
catch {
    Write-Output "Using alternative method to create table..."
}



$FunctionAppResourceGroupName = Get-ResourceGroupName -promptMessage "Enter the resource group name for the Function App"

Write-Host "Table creation process completed." -ForegroundColor Cyan


$functionApps = Get-AzFunctionApp -ResourceGroupName $FunctionAppResourceGroupName
$functionApps | ForEach-Object -Begin { $script:i = 0 } -Process { Write-Host "$($script:i): $($_.Name)"; $script:i++ }


$functionAppIndex = Read-Host -Prompt "Enter the number of the function app created when installing the Commvault solution in Sentinel"
$selectedFunctionApp = $functionApps[$functionAppIndex]

if (-not $selectedFunctionApp) {
    Write-Host "Invalid function app number. Please run the script again and enter a valid function app number."
    exit
}

$principalId = (Get-AzADUser -UserPrincipalName (Get-AzContext).Account.Id).Id

$roleDefinitionId = (Get-AzRoleDefinition -Name "Reader").Id

$existingRoleAssignment = Get-AzRoleAssignment -ObjectId $principalId -Scope "/subscriptions/$($selectedSubscription.Id)/resourceGroups/$($selectedFunctionApp.ResourceGroup)/providers/Microsoft.Web/sites/$($selectedFunctionApp.Name)" -ErrorAction SilentlyContinue

if (-not $existingRoleAssignment) {
    New-AzRoleAssignment -ObjectId $principalId -RoleDefinitionId $roleDefinitionId -Scope "/subscriptions/$($selectedSubscription.Id)/resourceGroups/$($selectedFunctionApp.ResourceGroup)/providers/Microsoft.Web/sites/$($selectedFunctionApp.Name)" -Verbose
}


$scope = "/subscriptions/$($selectedSubscription.Id)/resourceGroups/$($selectedFunctionApp.ResourceGroup)/providers/Microsoft.Web/sites/$($selectedFunctionApp.Name)/config/appsettings"
$existingScopeRoleAssignment = Get-AzRoleAssignment -ObjectId $principalId -Scope $scope -ErrorAction SilentlyContinue

if (-not $existingScopeRoleAssignment) {
    New-AzRoleAssignment -ObjectId $principalId -RoleDefinitionId $roleDefinitionId -Scope $scope -Verbose
}

az functionapp identity assign --name $selectedFunctionApp.Name --resource-group $selectedFunctionApp.ResourceGroup --subscription $selectedFunctionApp.subscriptionId --verbose


$principalId = (az functionapp identity show --name $selectedFunctionApp.Name --resource-group $selectedFunctionApp.ResourceGroup --subscription $selectedFunctionApp.subscriptionId | ConvertFrom-Json).principalId


$keyVaultName = (az functionapp config appsettings list --name $selectedFunctionApp.Name --resource-group $selectedFunctionApp.ResourceGroup --subscription $selectedFunctionApp.subscriptionId | ConvertFrom-Json | Where-Object { $_.name -eq "KeyVaultName" }).value

if (-not $keyVaultName) {
    Write-Host "Key Vault name not found in function app settings. Please ensure the setting 'KeyVaultName' exists."
    exit
}


$selectedKeyVault = Get-AzKeyVault -VaultName $keyVaultName 

if (-not $selectedKeyVault) {
    Write-Host "Key Vault $keyVaultName not found ."
    exit
}

$isRbacEnabled = (Get-AzKeyVault -VaultName $selectedKeyVault.VaultName).EnableRbacAuthorization
if($isRbacEnabled) {
    $keyVaultId = (Get-AzKeyVault -VaultName $selectedKeyVault.VaultName).ResourceId
    New-AzRoleAssignment -ObjectId $principalId -RoleDefinitionName "Key Vault Secrets User" -Scope $keyVaultId
}
else{
    Set-AzKeyVaultAccessPolicy -VaultName $selectedKeyVault.VaultName -ObjectId $principalId -PermissionsToSecrets get
}

$storageAccountName = (az functionapp config appsettings list --name $selectedFunctionApp.Name --resource-group $selectedFunctionApp.ResourceGroup --subscription $selectedFunctionApp.subscriptionId | ConvertFrom-Json | Where-Object { $_.name -eq "AzureWebJobsStorage" }).value -replace ".*AccountName=([^;]+);.*", '$1'

if (-not $storageAccountName) {
    Write-Host "Storage account name not found in function app settings. Please ensure the setting 'AzureWebJobsStorage' exists."
    exit
}


$storageAccountKey = (Get-AzStorageAccountKey -ResourceGroupName $FunctionAppResourceGroupName -Name $storageAccountName)[0].Value


$storageContext = New-AzStorageContext -StorageAccountName $storageAccountName -StorageAccountKey $storageAccountKey


$containerName = "sentinelcontainer"
New-AzStorageContainer -Name $containerName -Context $storageContext -ErrorAction SilentlyContinue -Verbose

if ($?) {
    Write-Host "Container '$containerName' created successfully in storage account '$storageAccountName'."
} else {
    Write-Host "Failed to create container '$containerName' in storage account '$storageAccountName'."
}
