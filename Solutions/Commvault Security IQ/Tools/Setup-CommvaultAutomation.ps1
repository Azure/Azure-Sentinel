function Write-LogMessage {
    param (
        [string]$message,
        [string]$type = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($type) {
        "INFO" { "White" }
        "WARNING" { "Yellow" }
        "ERROR" { "Red" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    
    Write-Host "[$timestamp] [$type] $message" -ForegroundColor $color
}

Write-LogMessage "Clearing any existing Azure context" 
Disable-AzContextAutosave -Scope Process

function Connect-ToAzure {
    Write-LogMessage "Authenticating to Azure using device authentication..."
    
    try {
        Connect-AzAccount -UseDeviceAuthentication -ErrorAction Stop
        Write-LogMessage "Authentication successful" "SUCCESS"
        return $true
    }
    catch {
        Write-LogMessage "Authentication failed: $_" "ERROR"
        return $false
    }
}

function Get-ResourceGroupName {
    param (
        [string]$promptMessage
    )
    
    $resourceGroupName = Read-Host -Prompt $promptMessage
    $resourceGroupName = $resourceGroupName.Trim()
    
    try {
        $resourceGroup = Get-AzResourceGroup -Name $resourceGroupName -ErrorAction Stop
        Write-LogMessage "Resource group '$resourceGroupName' found in location: $($resourceGroup.Location)" "SUCCESS"
        return $resourceGroupName
    }
    catch {
        Write-LogMessage "Resource group '$resourceGroupName' not found. Please verify the resource group exists." "ERROR"
        $retry = Read-Host "Would you like to try another resource group name? (Y/N)"
        if ($retry -eq "Y" -or $retry -eq "y") {
            return Get-ResourceGroupName -promptMessage $promptMessage
        }
        else {
            Write-LogMessage "Exiting script as resource group validation failed" "ERROR"
            exit
        }
    }
}

function New-AndPublish-Runbook {
    param (
        [string]$runbookName,
        [string]$githubFileUrl,
        [string]$automationAccountName,
        [string]$automationResourceGroupName
    )

    try {
        $existingRunbook = Get-AzAutomationRunbook -AutomationAccountName $automationAccountName `
                                                 -ResourceGroupName $automationResourceGroupName `
                                                 -Name $runbookName -ErrorAction SilentlyContinue
        if ($existingRunbook) {
            $overwrite = Read-Host "Do you want to overwrite the existing runbook? (Y/N)"
            if ($overwrite -ne "Y" -and $overwrite -ne "y") {
                return $true
            }
        }
    }
    catch {
        Write-LogMessage "Error checking for existing runbook: $_" "ERROR"
    }
    try {
        $pythonScriptContent = Invoke-WebRequest -Uri $githubFileUrl -UseBasicParsing -ErrorAction Stop
        $pythonScriptContent = $pythonScriptContent.Content
    }
    catch {
        Write-LogMessage "Failed to download script from GitHub: $_" "ERROR"
        Write-LogMessage "Please check internet connectivity and URL validity" "WARNING"
        return $false
    }
    if (-not $existingRunbook) {
        try {
            New-AzAutomationRunbook -AutomationAccountName $automationAccountName `
                                  -ResourceGroupName $automationResourceGroupName `
                                  -Name $runbookName `
                                  -Type "Python3" `
                                  -Description "Runbook to handle $runbookName in Commvault" -ErrorAction Stop | Out-Null
        }
        catch {
            Write-LogMessage "Failed to create runbook: $_" "ERROR"
            Write-LogMessage "Manual steps: Create a Python3 runbook named '$runbookName' in automation account '$automationAccountName'" "WARNING"
            return $false
        }
    }
    $runbookPath = "$runbookName.py"
    try {
        $pythonScriptContent | Out-File -FilePath $runbookPath -Encoding utf8 -ErrorAction Stop
    }
    catch {
        Write-LogMessage "Failed to save script to file: $_" "ERROR"
        return $false
    }
    try {
        Import-AzAutomationRunbook -AutomationAccountName $automationAccountName `
                                 -ResourceGroupName $automationResourceGroupName `
                                 -Name $runbookName `
                                 -Path $runbookPath `
                                 -Type "Python3" -Force -ErrorAction Stop | Out-Null
    }
    catch {
        Write-LogMessage "Failed to import script: $_" "ERROR"
        Write-LogMessage "Manual steps: Upload the script from $runbookPath to the runbook '$runbookName'" "WARNING"
        return $false
    }
    try {
        Publish-AzAutomationRunbook -AutomationAccountName $automationAccountName `
                                  -ResourceGroupName $automationResourceGroupName `
                                  -Name $runbookName -ErrorAction Stop
        return $true
    }
    catch {
        Write-LogMessage "Failed to publish runbook: $_" "ERROR"
        Write-LogMessage "Manual steps: Publish the runbook '$runbookName' in the Azure portal" "WARNING"
        return $false
    }
}

Write-LogMessage "Starting Commvault Security IQ integration setup script" "INFO"
Write-LogMessage "------------------------------------------------" "INFO"

$azContext = Get-AzContext
if (-not $azContext -or -not $azContext.Account) {
    $authSuccess = Connect-ToAzure
    if (-not $authSuccess) {
        Write-LogMessage "Authentication failed. Exiting script." "ERROR"
        exit
    }
} else {
    Write-LogMessage "Already authenticated to Azure as $($azContext.Account.Id)" "SUCCESS"
    Write-LogMessage "Current subscription: $($azContext.Subscription.Name) ($($azContext.Subscription.Id))" "INFO"
    $confirmContext = Read-Host "Is this the correct subscription/context? (Y/N)"
    if ($confirmContext -ne "Y" -and $confirmContext -ne "y") {
        Write-LogMessage "Re-authenticating to Azure as per user request..." "INFO"
        $authSuccess = Connect-ToAzure
        if (-not $authSuccess) {
            Write-LogMessage "Authentication failed. Exiting script." "ERROR"
            exit
        }
        $azContext = Get-AzContext
        Write-LogMessage "Authenticated as $($azContext.Account.Id) with subscription $($azContext.Subscription.Name) ($($azContext.Subscription.Id))" "SUCCESS"
    }
}

Write-LogMessage "Checking for available subscriptions..."
$selectedSubscription = Get-AzContext | Select-Object -ExpandProperty Subscription

if (-not $selectedSubscription) {
    $subscriptions = Get-AzSubscription
    
    if (-not $subscriptions -or $subscriptions.Count -eq 0) {
        Write-LogMessage "No subscriptions found for the authenticated account. Exiting script." "ERROR"
        exit
    }
    
    Write-LogMessage "Available subscriptions:" "INFO"
    $subscriptions | ForEach-Object -Begin { $script:i = 0 } -Process { Write-LogMessage "$($script:i): $($_.Name) ($($_.Id))" "INFO"; $script:i++ }
    
    $subscriptionIndex = Read-Host -Prompt "Enter the number of the subscription you want to use"
    
    if ($subscriptionIndex -ge 0 -and $subscriptionIndex -lt $subscriptions.Count) {
        $selectedSubscription = $subscriptions[$subscriptionIndex]
        Write-LogMessage "Selected subscription: $($selectedSubscription.Name)" "SUCCESS"
    } else {
        Write-LogMessage "Invalid subscription number. Please run the script again and enter a valid subscription number." "ERROR"
        exit
    }
}
else {
    Write-LogMessage "Using current subscription: $($selectedSubscription.Name)" "INFO"
}

try {
    Set-AzContext -SubscriptionId $selectedSubscription.Id -ErrorAction Stop | Out-Null
    Write-LogMessage "Subscription context set successfully" "SUCCESS"
}
catch {
    Write-LogMessage "Failed to set subscription context: $_" "ERROR"
    Write-LogMessage "Please ensure the subscription is accessible with your current credentials" "WARNING"
    exit
}

$resourceGroupName = Get-ResourceGroupName -promptMessage "Enter the resource group name for the Automation Account"

$automationResourceGroupName = $resourceGroupName
Write-LogMessage "Using '$automationResourceGroupName' for the Automation Account" "INFO"

$automationAccountName = "Commvault-Automation-Account"
Write-LogMessage "Checking for Automation Account: $automationAccountName"

try {
    $automationAccount = Get-AzAutomationAccount -ResourceGroupName $automationResourceGroupName -Name $automationAccountName -ErrorAction SilentlyContinue
    
    if (-not $automationAccount) {
        Write-LogMessage "Automation account '$automationAccountName' not found. Creating new account..." "INFO"
        
        try {
            $location = (Get-AzResourceGroup -Name $automationResourceGroupName).Location
            New-AzAutomationAccount -ResourceGroupName $automationResourceGroupName -Name $automationAccountName -Location $location -ErrorAction Stop
            Write-LogMessage "Automation account '$automationAccountName' created successfully" "SUCCESS"
        }
        catch {
            Write-LogMessage "Failed to create automation account: $_" "ERROR"
            Write-LogMessage "Manual steps: Create an automation account named '$automationAccountName' in resource group '$automationResourceGroupName'" "WARNING"
        }
    }
    else {
        Write-LogMessage "Automation account '$automationAccountName' already exists" "SUCCESS"
    }
}
catch {
    Write-LogMessage "Error checking for automation account: $_" "ERROR"
    Write-LogMessage "Manual steps: Create an automation account named '$automationAccountName' in resource group '$automationResourceGroupName'" "WARNING"
}

Write-LogMessage "Creating and publishing runbooks..."
New-AndPublish-Runbook -runbookName "Commvault_Disable_IDP" `
    -githubFileUrl "https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/Solutions/Commvault%20Security%20IQ/Playbooks/Runbooks/Commvault_Disable_IDP.py" `
    -automationAccountName $automationAccountName `
    -automationResourceGroupName $automationResourceGroupName

New-AndPublish-Runbook -runbookName "Commvault_Disable_User" `
    -githubFileUrl "https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/Solutions/Commvault%20Security%20IQ/Playbooks/Runbooks/Commvault_Disable_User.py" `
    -automationAccountName $automationAccountName `
    -automationResourceGroupName $automationResourceGroupName

New-AndPublish-Runbook -runbookName "Commvault_Disable_Data_Aging" `
    -githubFileUrl "https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/Solutions/Commvault%20Security%20IQ/Playbooks/Runbooks/Commvault_Disable_Data_Aging.py" `
    -automationAccountName $automationAccountName `
    -automationResourceGroupName $automationResourceGroupName

Write-LogMessage "Commvault Security IQ automation setup completed successfully" "SUCCESS"