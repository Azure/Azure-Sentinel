Connect-AzAccount -UseDeviceAuthentication 


function Get-ResourceGroupName {
    param (
        [string]$promptMessage
    )
    $automationResourceGroupName = Read-Host -Prompt $promptMessage
    return $automationResourceGroupName.Trim()
}


function Get-CurrentSP {
    param (
        [string]$keyVaultName
    )

    # Authenticate to Azure
    Connect-AzAccount -UseDeviceAuthentication

    # Get the Key Vault
    $keyVault = Get-AzKeyVault -VaultName $keyVaultName -ErrorAction SilentlyContinue
    if (-not $keyVault) {
        Write-Host "Key Vault $keyVaultName not found. Exiting."
        return
    }

    # Fetch the environment-endpoint-url secret
    $environmentEndpointUrlSecret = Get-AzKeyVaultSecret -VaultName $keyVaultName -Name "environment-endpoint-url"
    $environmentEndpointUrl = $environmentEndpointUrlSecret.SecretValueText
    Write-Host "Fetched environment endpoint URL: $environmentEndpointUrl"

    # Fetch the access-token secret
    $accessTokenSecret = Get-AzKeyVaultSecret -VaultName $keyVaultName -Name "access-token"
    $accessToken = $accessTokenSecret.SecretValueText
    Write-Host "Fetched access token."

    # Set headers
    $headers = @{ "Authorization" = "Bearer $accessToken" }

    # Make the GET request to fetch the current service point
    $commservUrl = "$environmentEndpointUrl/CommServ"
    try {
        $response = Invoke-RestMethod -Uri $commservUrl -Headers $headers -Method Get
        if ($response -and $response.currentSPVersion) {
            Write-Host "Current Service Point Version: $($response.currentSPVersion)"
            return $response.currentSPVersion
        } else {
            Write-Host "Failed to fetch current service point version."
        }
    } catch {
        Write-Host "Error fetching current service point: $_"
    }
}


function New-AccessToken {
    param (
        [string]$keyVaultName
    )

    # Authenticate to Azure
    Connect-AzAccount -UseDeviceAuthentication

    # Get the Key Vault
    $keyVault = Get-AzKeyVault -VaultName $keyVaultName -ErrorAction SilentlyContinue
    if (-not $keyVault) {
        Write-Host "Key Vault $keyVaultName not found. Exiting."
        return
    }

    # Fetch the environment-endpoint-url secret
    $environmentEndpointUrlSecret = Get-AzKeyVaultSecret -VaultName $keyVaultName -Name "environment-endpoint-url"
    $environmentEndpointUrl = $environmentEndpointUrlSecret.SecretValueText
    Write-Host "Fetched environment endpoint URL: $environmentEndpointUrl"

    # Fetch the access-token secret
    $accessTokenSecret = Get-AzKeyVaultSecret -VaultName $keyVaultName -Name "access-token"
    $accessToken = $accessTokenSecret.SecretValueText
    Write-Host "Fetched access token."

    # Fetch the current service point (SP)
    $currentSP = Get-CurrentSP -keyVaultName $keyVaultName
    if (-not $currentSP) {
        Write-Host "Failed to fetch current service point version."
        return
    }

    if ($currentSP -ge 38) {
        # Create a new access token
        $createTokenUrl = "$environmentEndpointUrl/V4/AccessToken"
        $tokenName = "$($keyVaultName)-token"
        $renewableUntil = [int]((Get-Date).AddYears(1).ToUniversalTime() -as [DateTime]).ToFileTimeUtc()
        $tokenBody = @{ "renewableUntilTimestamp" = $renewableUntil; "tokenName" = $tokenName } | ConvertTo-Json -Depth 10

        $headers = @{ "Authorization" = "Bearer $accessToken" }
        $tokenResponse = Invoke-RestMethod -Uri $createTokenUrl -Headers $headers -Method Post -Body $tokenBody -ContentType "application/json"
        if ($tokenResponse -and $tokenResponse.tokenInfo) {
            $newAccessToken = $tokenResponse.tokenInfo.accessToken
            $newRefreshToken = $tokenResponse.tokenInfo.refreshToken            
            Set-AzKeyVaultSecret -VaultName $keyVaultName -Name "access-token" -SecretValue (ConvertTo-SecureString $newAccessToken -AsPlainText -Force)
            Set-AzKeyVaultSecret -VaultName $keyVaultName -Name "refresh-token" -SecretValue (ConvertTo-SecureString $newRefreshToken -AsPlainText -Force)
            Write-Host "New access token created and stored in Key Vault."
        } else {
            Write-Host "Failed to create a new access token."
        }
    } else {
        Write-Host "Service Point version is less than 38. No ne access token created."
    }
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

$LogAnalyticsResourceGroupName = Get-ResourceGroupName -promptMessage "Enter the resource group name for the Log Analytics workspace"

# Using the same resource group for automation account , as the log analytics workspace
$automationResourceGroupName = $LogAnalyticsResourceGroupName

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


$workspaces = Get-AzOperationalInsightsWorkspace -ResourceGroupName $LogAnalyticsResourceGroupName
$workspaces | ForEach-Object -Begin { $script:i = 0 } -Process { Write-Host "$($script:i): $($_.Name)"; $script:i++ }


$workspaceIndex = Read-Host -Prompt "Enter the number of the Log Analytics workspace used, for Commvault Cloud sentinel solution"
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

$keyVaultName = Read-Host -Prompt "Enter the Key Vault name, that is used to setup Commvault sentinel data connector"
$selectedKeyVault = Get-AzKeyVault -VaultName $keyVaultName -ErrorAction SilentlyContinue

if (-not $selectedKeyVault) {
    Write-Host "Key Vault $keyVaultName not found."
    $keyVaultSubscriptionId = Read-Host -Prompt "Enter the subscription ID of the Key Vault"
    $keyVaultResourceGroupName = Read-Host -Prompt "Enter the resource group name of the Key Vault"

    $selectedKeyVault = Get-AzKeyVault -VaultName $keyVaultName -SubscriptionId $keyVaultSubscriptionId -ResourceGroupName $keyVaultResourceGroupName -ErrorAction SilentlyContinue

    if (-not $selectedKeyVault) {
        Write-Host "Key Vault $keyVaultName does not exist in the provided subscription and resource group. Exiting."
        exit
    }
}

Write-Host "Key Vault $keyVaultName found."

New-AccessToken -keyVaultName $keyVaultName

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

Write-Host "Table creation process completed." -ForegroundColor Cyan


