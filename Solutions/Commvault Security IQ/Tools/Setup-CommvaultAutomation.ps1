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

function Get-CurrentSP {
    param (
        [string]$keyVaultName
    )

    try {
        $keyVault = Get-AzKeyVault -VaultName $keyVaultName -ErrorAction Stop
    }
    catch {
        Write-LogMessage "Key Vault '$keyVaultName' not found or you don't have access. Error: $_" "ERROR"
        return $null
    }

    try {
        $environmentEndpointUrlSecret = Get-AzKeyVaultSecret -VaultName $keyVaultName -Name "environment-endpoint-url" -ErrorAction Stop
        $environmentEndpointUrl = ($environmentEndpointUrlSecret.SecretValue | ConvertFrom-SecureString -AsPlainText)
    }
    catch {
        Write-LogMessage "Failed to fetch environment-endpoint-url secret: $_" "ERROR"
        Write-LogMessage "Please make sure the secret 'environment-endpoint-url' exists in the Key Vault" "WARNING"
        return $null
    }

    try {
        $accessTokenSecret = Get-AzKeyVaultSecret -VaultName $keyVaultName -Name "access-token" -ErrorAction Stop
        $accessToken = ($accessTokenSecret.SecretValue | ConvertFrom-SecureString -AsPlainText)
    }
    catch {
        Write-LogMessage "Failed to fetch access-token secret: $_" "ERROR"
        Write-LogMessage "Please make sure the secret 'access-token' exists in the Key Vault" "WARNING"
        return $null
    }

    $headers = @{ 
        "Authorization" = "Bearer $accessToken"
        "Accept" = "application/json"
    }

    $commservUrl = "$environmentEndpointUrl/CommServ"
    try {
        $response = Invoke-RestMethod -Uri $commservUrl -Headers $headers -Method Get -ErrorAction Stop
        Write-Host "CommServ API Response: $($response | ConvertTo-Json -Depth 10)"
        
        if ($null -ne $response.currentSPVersion) {
            Write-Host "Found currentSPVersion in response: $($response.currentSPVersion)"
            return [int]$response.currentSPVersion
        }
        elseif ($null -ne $response.spVersion) {
            return [int]$response.spVersion
        }
        elseif ($null -ne $response.version) {
            return [int]$response.version
        }
        else {
            Write-LogMessage "Could not automatically detect version in response" "WARNING"
            $manualVersion = Read-Host -Prompt "Please enter the Service Pack version manually (from the API response)"
            if ($manualVersion -match '^\d+$') {
                return [int]$manualVersion
            }
            return $null
        }
    } 
    catch {
        Write-LogMessage "Error fetching current Service Pack: $_" "ERROR"
        Write-LogMessage "This could be due to an expired/invalid access token or network issues" "WARNING"
        return $null
    }
}

function New-AccessToken {
    param (
        [string]$keyVaultName
    )

    try {
        $keyVault = Get-AzKeyVault -VaultName $keyVaultName -ErrorAction Stop
    }
    catch {
        Write-LogMessage "Key Vault '$keyVaultName' not found or you don't have access. Error: $_" "ERROR"
        Write-LogMessage "Please ensure the Key Vault exists and you have proper permissions before running this function again" "WARNING"
        return $false
    }

    try {
        $environmentEndpointUrlSecret = Get-AzKeyVaultSecret -VaultName $keyVaultName -Name "environment-endpoint-url" -ErrorAction Stop
        $environmentEndpointUrl = ($environmentEndpointUrlSecret.SecretValue | ConvertFrom-SecureString -AsPlainText)
    }
    catch {
        Write-LogMessage "Failed to fetch environment-endpoint-url secret: $_" "ERROR"
        Write-LogMessage "Please make sure the secret 'environment-endpoint-url' exists in the Key Vault" "WARNING"
        return $false
    }

    try {
        $accessTokenSecret = Get-AzKeyVaultSecret -VaultName $keyVaultName -Name "access-token" -ErrorAction Stop
        $accessToken = ($accessTokenSecret.SecretValue | ConvertFrom-SecureString -AsPlainText)
    }
    catch {
        Write-LogMessage "Failed to fetch access-token secret: $_" "ERROR"
        Write-LogMessage "Please make sure the secret 'access-token' exists in the Key Vault" "WARNING"
        return $false
    }

    $currentSP = Get-CurrentSP -keyVaultName $keyVaultName
    if (-not $currentSP) {
        Write-LogMessage "Failed to fetch current Service Pack version. Cannot proceed with token creation." "ERROR"
        return $false
    }
    
    Write-Host "Current Service Pack Version: $currentSP"
    
    if ($currentSP -ge 38) {
        $createTokenUrl = "$environmentEndpointUrl/V4/AccessToken"
        $timestamp = [int]([datetime]::UtcNow - [datetime]'1970-01-01').TotalSeconds
        $tokenName = "$($keyVaultName)-token-$timestamp"
        $renewableUntil = [int]([datetimeoffset](Get-Date).AddYears(1).ToUniversalTime()).ToUnixTimeSeconds()
        $tokenBody = @{ "renewableUntilTimestamp" = $renewableUntil; "tokenName" = $tokenName } | ConvertTo-Json -Depth 10
        $headers = @{ 
            "Authorization" = "Bearer $accessToken"
            "Accept" = "application/json"
        }
        try {   
            $tokenResponse = Invoke-RestMethod -Uri $createTokenUrl -Headers $headers -Method Post -Body $tokenBody -ContentType "application/json" -ErrorAction Stop
            if ($tokenResponse -and $tokenResponse.tokenInfo) {
                $newAccessToken = $tokenResponse.tokenInfo.accessToken
                $newRefreshToken = $tokenResponse.tokenInfo.refreshToken
                $tokenExpiryTimestamp = $tokenResponse.tokenInfo.tokenExpiryTimestamp
                try {
                    $secretNames = @("access-token", "refresh-token", "token-expiry-timestamp")
                    foreach ($secretName in $secretNames) {
                        $existingSecret = Get-AzKeyVaultSecret -VaultName $keyVaultName -Name $secretName -ErrorAction SilentlyContinue
                        if ($existingSecret) {
                            Write-LogMessage "Purging old secret: $secretName" "INFO"
                            Remove-AzKeyVaultSecret -VaultName $keyVaultName -Name $secretName -Force -ErrorAction SilentlyContinue
                            $waitTime = 0
                            $maxWait = 60
                            while ($waitTime -lt $maxWait) {
                                $deleted = Get-AzKeyVaultSecret -VaultName $keyVaultName -Name $secretName -InRemovedState -ErrorAction SilentlyContinue
                                if ($deleted) { break }
                                Start-Sleep -Seconds 2
                                $waitTime += 2
                            }
                            try {
                                Write-LogMessage "Attempting to purge deleted secret: $secretName" "INFO"
                                Remove-AzKeyVaultSecret -VaultName $keyVaultName -Name $secretName -Force -InRemovedState -ErrorAction SilentlyContinue
                            } catch {}
                            $waitTime = 0
                            while ($waitTime -lt $maxWait) {
                                $deleted = Get-AzKeyVaultSecret -VaultName $keyVaultName -Name $secretName -InRemovedState -ErrorAction SilentlyContinue
                                if (-not $deleted) { break }
                                Start-Sleep -Seconds 2
                                $waitTime += 2
                            }
                        } else {
                            Write-LogMessage "Secret $secretName does not exist. Skipping deletion." "INFO"
                        }
                    }
                    Set-AzKeyVaultSecret -VaultName $keyVaultName -Name "access-token" -SecretValue (ConvertTo-SecureString $newAccessToken -AsPlainText -Force) -ErrorAction Stop
                    Set-AzKeyVaultSecret -VaultName $keyVaultName -Name "refresh-token" -SecretValue (ConvertTo-SecureString $newRefreshToken -AsPlainText -Force) -ErrorAction Stop
                    Set-AzKeyVaultSecret -VaultName $keyVaultName -Name "token-expiry-timestamp" -SecretValue (ConvertTo-SecureString $tokenExpiryTimestamp -AsPlainText -Force) -ErrorAction Stop

                    Write-LogMessage "Successfully created, purged old, and stored new access token" "SUCCESS"
                    return $true
                }
                catch {
                    Write-LogMessage "Failed to store new tokens in Key Vault: $_" "ERROR"
                    Write-LogMessage "Please ensure you have proper permissions to set secrets in the Key Vault" "WARNING"
                    return $false
                }
            } 
            else {
                Write-LogMessage "Failed to create a new acess token / refresh token. Invalid response from API." "ERROR"
                return $false
            }
        } 
        catch {
            Write-LogMessage "Error creating new acess token / refresh token: $_" "ERROR"
            Write-LogMessage "This could be due to an expired token, insufficient permissions, or API changes" "WARNING"
            return $false
        }
    } 
    else {
        Write-LogMessage "Service Pack version is $currentSP (< 38). No new refresh token created." "WARNING"
        Write-LogMessage "This version doesn't support the refresh token creation API. Please upgrade to SP version 38 or later" "INFO"
        return $true
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

function New-LogAnalyticsTable {
    param (
        [string]$workspaceId,
        [string]$workspaceKey,
        [string]$tableName
    )

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
            "Log-Type" = $tableName
            "x-ms-date" = $date
            "time-generated-field" = "TimeGenerated"
        }
        Invoke-RestMethod -Uri $uri -Method POST -ContentType $contentType -Headers $headers -Body $jsonData -ErrorAction Stop
        return $true
    }
    catch {
        Write-LogMessage "Failed to create table using Data Collector API: $_" "ERROR"
        Write-LogMessage "This error can sometimes be expected if the table already exists or if there are permission issues" "WARNING"
        Write-LogMessage "Manual steps: Create a custom table named '$tableName' in the Log Analytics workspace" "WARNING"
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

$LogAnalyticsResourceGroupName = Get-ResourceGroupName -promptMessage "Enter the resource group name for the Log Analytics workspace"

$automationResourceGroupName = $LogAnalyticsResourceGroupName
Write-LogMessage "Using '$automationResourceGroupName' for both Log Analytics workspace and Automation Account" "INFO"

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

Write-LogMessage "Retrieving Log Analytics workspaces in resource group '$LogAnalyticsResourceGroupName'"
try {
    $workspaces = Get-AzOperationalInsightsWorkspace -ResourceGroupName $LogAnalyticsResourceGroupName -ErrorAction Stop
    
    if (-not $workspaces -or $workspaces.Count -eq 0) {
        Write-LogMessage "No Log Analytics workspaces found in resource group '$LogAnalyticsResourceGroupName'" "ERROR"
        Write-LogMessage "Please create a Log Analytics workspace in this resource group before running this script" "WARNING"
        exit
    }
    
    Write-LogMessage "Available Log Analytics workspaces:" "INFO"
    $workspaces | ForEach-Object -Begin { $script:i = 0 } -Process { Write-Host "$($script:i): $($_.Name)" ; $script:i++ }
    
    $workspaceIndex = Read-Host -Prompt "Enter the number of the Log Analytics workspace used for Commvault Cloud sentinel solution"
    
    if ($workspaceIndex -ge 0 -and $workspaceIndex -lt $workspaces.Count) {
        $workspace = $workspaces[$workspaceIndex]
        Write-LogMessage "Selected workspace: $($workspace.Name)" "SUCCESS"
        $tableName = "CommvaultSecurityIQ_CL"
        Write-LogMessage "Will create table: $tableName" "INFO"
        Write-LogMessage "Getting Log Analytics workspace details..."

        try {
            $workspaceId = $workspace.CustomerId
            $workspaceName = $workspace.Name
            
            Write-LogMessage "Workspace ID: $workspaceId"
            Write-LogMessage "Creating Log Analytics table: $tableName"
            try {
                $workspaceKey = (Get-AzOperationalInsightsWorkspaceSharedKey -ResourceGroupName $LogAnalyticsResourceGroupName -Name $workspaceName -ErrorAction Stop).PrimarySharedKey
                Write-LogMessage "Workspace key retrieved successfully" "SUCCESS"
            }
            catch {
                Write-LogMessage "Failed to retrieve workspace key: $_" "ERROR"
                Write-LogMessage "Please ensure you have sufficient permissions to access workspace shared keys" "WARNING"
                $manualContinue = Read-Host "Do you want to continue with the rest of the script? (Y/N)"
                if ($manualContinue -ne "Y" -and $manualContinue -ne "y") {
                    Write-LogMessage "Exiting script as requested" "INFO"
                    exit
                }
            }
            if ($workspaceId -and $workspaceKey) {
                $tableCreated = New-LogAnalyticsTable -workspaceId $workspaceId -workspaceKey $workspaceKey -tableName $tableName
                if ($tableCreated) {
                    Write-LogMessage "Log Analytics table creation completed successfully" "SUCCESS"
                }
                else {
                    Write-LogMessage "Table creation might have encountered issues" "WARNING"
                    Write-LogMessage "Manual steps: Verify table '$tableName' exists in Log Analytics workspace '$workspaceName'" "WARNING"
                }
            }
            else {
                Write-LogMessage "Cannot create Log Analytics table due to missing workspace details" "ERROR"
                Write-LogMessage "Manual steps: Create a custom table named '$tableName' in the Log Analytics workspace" "WARNING"
            }
        }
        catch {
            Write-LogMessage "Error getting workspace details: $_" "ERROR"
            exit
        }
    }
    else {
        Write-LogMessage "Invalid workspace number. Please run the script again and enter a valid workspace number." "ERROR"
        exit
    }
}
catch {
    Write-LogMessage "Error retrieving Log Analytics workspaces: $_" "ERROR"
    exit
}



$keyVaultName = Read-Host -Prompt "Enter the Key Vault name that is used to setup Commvault sentinel data connector"
Write-LogMessage "Searching for Key Vault: $keyVaultName" "INFO"

try {
    $selectedKeyVault = Get-AzKeyVault -VaultName $keyVaultName -ErrorAction SilentlyContinue
    
    if (-not $selectedKeyVault) {
        Write-LogMessage "Key Vault '$keyVaultName' not found in subscription: $($selectedSubscription.Name)" "WARNING"
        Write-LogMessage "Attempting to find it in other subscriptions..." "INFO"
        
        $keyVaultSubscriptionId = Read-Host -Prompt "Enter the subscription ID of the Key Vault"
        $keyVaultResourceGroupName = Read-Host -Prompt "Enter the resource group name of the Key Vault"
        
        $currentSubscriptionId = (Get-AzContext).Subscription.Id
        
        try {
            Set-AzContext -SubscriptionId $keyVaultSubscriptionId -ErrorAction Stop | Out-Null
            Write-LogMessage "Switched to subscription with ID: $keyVaultSubscriptionId" "SUCCESS"
            
            try {
                $selectedKeyVault = Get-AzKeyVault -VaultName $keyVaultName -ResourceGroupName $keyVaultResourceGroupName -ErrorAction Stop
                Write-LogMessage "Key Vault '$keyVaultName' found in subscription: $keyVaultSubscriptionId" "SUCCESS"
            }
            catch {
                Write-LogMessage "Key Vault '$keyVaultName' not found in the provided subscription and resource group: $_" "ERROR"
                Write-LogMessage "Please verify the Key Vault name, subscription ID, and resource group" "WARNING"
                Write-LogMessage "Restoring original subscription context" "INFO"
                Set-AzContext -SubscriptionId $currentSubscriptionId | Out-Null
                exit
            }
            
            Set-AzContext -SubscriptionId $currentSubscriptionId | Out-Null
            $restoredContext = Get-AzContext
            Write-LogMessage "Restored original subscription context: $($restoredContext.Subscription.Name)" "INFO"
        }
        catch {
            Write-LogMessage "Failed to set context to subscription with ID '$keyVaultSubscriptionId': $_" "ERROR"
            Write-LogMessage "Restoring original subscription context" "INFO"
            Set-AzContext -Context $currentContext | Out-Null
            exit
        }
    }
    else {
        Write-LogMessage "Key Vault '$keyVaultName' found in current subscription" "SUCCESS"
    }
}
catch {
    Write-LogMessage "Error searching for Key Vault: $_" "ERROR"
    exit
}

$tokenSuccess = New-AccessToken -keyVaultName $keyVaultName

if ($tokenSuccess) {
    Write-LogMessage "refresh token creation completed successfully" "SUCCESS"
}
else { 
    Write-LogMessage "New Access token/ Refresh token creation failed" "WARNING"
    Write-LogMessage "Manual steps: Check Key Vault secrets and refresh access tokens if needed" "WARNING"
    
    Write-LogMessage "Troubleshooting steps:" "INFO"
    Write-LogMessage "1. Verify your access token is valid" "INFO"
    Write-LogMessage "2. Check that the environment-endpoint-url in Key Vault is correct" "INFO"
    Write-LogMessage "3. Ensure you have proper permissions to the Key Vault and API endpoints" "INFO"
}

