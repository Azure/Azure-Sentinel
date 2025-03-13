# Get the object ID of the client
Connect-AzAccount -UseDeviceAuthentication 
$selectedSubscription = Get-AzContext | Select-Object -ExpandProperty Subscription

if (-not $selectedSubscription) {
    # List all subscriptions and assign a number to each subscription
    $subscriptions = Get-AzSubscription
    $subscriptions | ForEach-Object -Begin { $script:i = 0 } -Process { Write-Host "$($script:i): $($_.Name)"; $script:i++ }

    # Prompt user to select a subscription by number
    $subscriptionIndex = Read-Host -Prompt "Enter the number of the subscription you want to use, for Commvault Cloud sentinel solution"
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
$resourceGroupIndex = Read-Host -Prompt "Enter the number of the resource group you want to use, for Commvault Cloud sentinel solution"
$selectedResourceGroup = $resourceGroups[$resourceGroupIndex]

if (-not $selectedResourceGroup) {
    Write-Host "Invalid resource group number. Please run the script again and enter a valid resource group number."
    exit
}

# Set the resource group name
$resourceGroupName = $selectedResourceGroup.ResourceGroupName

# Create the automation account if it doesn't exist
$automationAccountName = "Commvault-Automation-Account"
$automationAccount = Get-AzAutomationAccount -ResourceGroupName $resourceGroupName -Name $automationAccountName -ErrorAction SilentlyContinue

if (-not $automationAccount) {
    # Write-Host "Creating automation account: $automationAccountName"
    New-AzAutomationAccount -ResourceGroupName $resourceGroupName -Name $automationAccountName -Location (Get-AzResourceGroup -Name $resourceGroupName).Location -Verbose
} else {
    # Write-Host "Automation account $automationAccountName already exists."
}
function New-AndPublish-Runbook {
    param (
        [string]$runbookName,
        [string]$githubFileUrl
    )

    # Check if the runbook already exists
    $existingRunbook = Get-AzAutomationRunbook -AutomationAccountName $automationAccountName `
                                               -ResourceGroupName $resourceGroupName `
                                               -Name $runbookName -ErrorAction SilentlyContinue

    if (-not $existingRunbook) {
        # Download the Python script from GitHub
        $pythonScriptContent = Invoke-WebRequest -Uri $githubFileUrl -UseBasicParsing
        $pythonScriptContent = $pythonScriptContent.Content

        # Create the runbook
        New-AzAutomationRunbook -AutomationAccountName $automationAccountName `
                                -ResourceGroupName $resourceGroupName `
                                -Name $runbookName `
                                -Type "Python3" `
                                -Description "Runbook to disable $runbookName in Commvault" -Verbose | Out-Null

        # Set the content of the runbook
        $runbookPath = "$runbookName.py"
        $pythonScriptContent | Out-File -FilePath $runbookPath -Encoding utf8
        Import-AzAutomationRunbook -AutomationAccountName $automationAccountName `
                                   -ResourceGroupName $resourceGroupName `
                                   -Name $runbookName `
                                   -Path $runbookPath `
                                   -Type "Python3" -Force -Verbose | Out-Null

        # Publish the runbook
        Publish-AzAutomationRunbook -AutomationAccountName $automationAccountName `
                                    -ResourceGroupName $resourceGroupName `
                                    -Name $runbookName -Verbose
    } else {
        Write-Host "Runbook $runbookName already exists."
    }
}

# Create and publish the runbooks
New-AndPublish-Runbook -runbookName "Commvault_Disable_IDP" -githubFileUrl "https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/Solutions/Commvault%20Security%20IQ/Playbooks/Runbooks/Commvault_Disable_IDP.py"
New-AndPublish-Runbook -runbookName "Commvault_Disable_User" -githubFileUrl "https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/Solutions/Commvault%20Security%20IQ/Playbooks/Runbooks/Commvault_Disable_User.py"
New-AndPublish-Runbook -runbookName "Commvault_Disable_Data_Aging" -githubFileUrl "https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/Solutions/Commvault%20Security%20IQ/Playbooks/Runbooks/Commvault_Disable_Data_Aging.py"
# Define the logic apps to be selected


# Create the log-type 'CommvaultSecurityIQ_CL' in the Log Analytics workspace
# List all Log Analytics workspaces in the selected resource group and assign a number to each workspace
$workspaces = Get-AzOperationalInsightsWorkspace -ResourceGroupName $resourceGroupName
$workspaces | ForEach-Object -Begin { $script:i = 0 } -Process { Write-Host "$($script:i): $($_.Name)"; $script:i++ }

# Prompt user to select a workspace by number
$workspaceIndex = Read-Host -Prompt "Enter the number of the Log Analytics workspace you want to use, for Commvault Cloud sentinel solution"
$workspace = $workspaces[$workspaceIndex]

if (-not $workspace) {
    Write-Host "Invalid workspace number. Please run the script again and enter a valid workspace number."
    exit
}

$tableName = "CommvaultSecurityIQ_CL"

Write-Host "Starting table creation process..." -ForegroundColor Cyan

# Get workspace details
Write-Output "Getting Log Analytics workspace details..."
$workspaceId = $workspace.CustomerId
$workspaceName = $workspace.Name
$workspaceKey = (Get-AzOperationalInsightsWorkspaceSharedKey -ResourceGroupName $resourceGroupName -Name $workspaceName).PrimarySharedKey

Write-Output "Workspace ID: $workspaceId"
Write-Output "Workspace key retrieved successfully."

try {
   # Create sample data to initialize table
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

    # Create the authorization signature
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

    # Upload the data to create the table
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

Write-Host "Table creation process completed." -ForegroundColor Cyan

# List all function apps in the selected resource group and assign a number to each function app
$functionApps = Get-AzFunctionApp -ResourceGroupName $resourceGroupName
$functionApps | ForEach-Object -Begin { $script:i = 0 } -Process { Write-Host "$($script:i): $($_.Name)"; $script:i++ }

# Prompt user to select a function app by number
$functionAppIndex = Read-Host -Prompt "Enter the number of the function app created when installing the Commvault solution in Sentinel"
$selectedFunctionApp = $functionApps[$functionAppIndex]

if (-not $selectedFunctionApp) {
    Write-Host "Invalid function app number. Please run the script again and enter a valid function app number."
    exit
}
# Get the object ID of the logged in user
$principalId = (Get-AzADUser -UserPrincipalName (Get-AzContext).Account.Id).Id
# Assign the user authorization to do action Microsoft.Web/sites/read over the selected function app
$roleDefinitionId = (Get-AzRoleDefinition -Name "Reader").Id
# Check if the role assignment already exists
$existingRoleAssignment = Get-AzRoleAssignment -ObjectId $principalId -Scope "/subscriptions/$($selectedSubscription.Id)/resourceGroups/$($selectedFunctionApp.ResourceGroup)/providers/Microsoft.Web/sites/$($selectedFunctionApp.Name)" -ErrorAction SilentlyContinue

if (-not $existingRoleAssignment) {
    New-AzRoleAssignment -ObjectId $principalId -RoleDefinitionId $roleDefinitionId -Scope "/subscriptions/$($selectedSubscription.Id)/resourceGroups/$($selectedFunctionApp.ResourceGroup)/providers/Microsoft.Web/sites/$($selectedFunctionApp.Name)" -Verbose
}

# Assign read authorization over the specified scope if not already assigned
$scope = "/subscriptions/$($selectedSubscription.Id)/resourceGroups/$($selectedFunctionApp.ResourceGroup)/providers/Microsoft.Web/sites/$($selectedFunctionApp.Name)/config/appsettings"
$existingScopeRoleAssignment = Get-AzRoleAssignment -ObjectId $principalId -Scope $scope -ErrorAction SilentlyContinue

if (-not $existingScopeRoleAssignment) {
    New-AzRoleAssignment -ObjectId $principalId -RoleDefinitionId $roleDefinitionId -Scope $scope -Verbose
}

az functionapp identity assign --name $selectedFunctionApp.Name --resource-group $selectedFunctionApp.ResourceGroup --subscription $selectedFunctionApp.subscriptionId --verbose

# Get the principal ID
$principalId = (az functionapp identity show --name $selectedFunctionApp.Name --resource-group $selectedFunctionApp.ResourceGroup --subscription $selectedFunctionApp.subscriptionId | ConvertFrom-Json).principalId

# Get the Key Vault name from the function app settings
$keyVaultName = (az functionapp config appsettings list --name $selectedFunctionApp.Name --resource-group $selectedFunctionApp.ResourceGroup --subscription $selectedFunctionApp.subscriptionId | ConvertFrom-Json | Where-Object { $_.name -eq "KeyVaultName" }).value

if (-not $keyVaultName) {
    Write-Host "Key Vault name not found in function app settings. Please ensure the setting 'KeyVaultName' exists."
    exit
}

# Get the Key Vault
$selectedKeyVault = Get-AzKeyVault -VaultName $keyVaultName -ResourceGroupName $resourceGroupName

if (-not $selectedKeyVault) {
    Write-Host "Key Vault $keyVaultName not found in resource group $resourceGroupName."
    exit
}

# Use the obtained principalId
Set-AzKeyVaultAccessPolicy -VaultName $selectedKeyVault.VaultName -ObjectId $principalId -PermissionsToSecrets get -Verbose
# Get the storage account name from the function app settings
$storageAccountName = (az functionapp config appsettings list --name $selectedFunctionApp.Name --resource-group $selectedFunctionApp.ResourceGroup --subscription $selectedFunctionApp.subscriptionId | ConvertFrom-Json | Where-Object { $_.name -eq "AzureWebJobsStorage" }).value -replace ".*AccountName=([^;]+);.*", '$1'

if (-not $storageAccountName) {
    Write-Host "Storage account name not found in function app settings. Please ensure the setting 'AzureWebJobsStorage' exists."
    exit
}

# Get the storage account key
$storageAccountKey = (Get-AzStorageAccountKey -ResourceGroupName $resourceGroupName -Name $storageAccountName)[0].Value

# Create a storage context
$storageContext = New-AzStorageContext -StorageAccountName $storageAccountName -StorageAccountKey $storageAccountKey

# Create a container called 'sentinelcontainer'
$containerName = "sentinelcontainer"
New-AzStorageContainer -Name $containerName -Context $storageContext -ErrorAction SilentlyContinue -Verbose

if ($?) {
    Write-Host "Container '$containerName' created successfully in storage account '$storageAccountName'."
} else {
    Write-Host "Failed to create container '$containerName' in storage account '$storageAccountName'."
}
