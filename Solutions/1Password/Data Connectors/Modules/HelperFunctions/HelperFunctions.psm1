Function Get-AuditLogs {
    <#
    .SYNOPSIS
        This function retrieves data from an API and performs some transformations on the results.
    .DESCRIPTION
        The function takes in parameters for lastRunTime, cursor, and api. It uses these parameters to construct the API request and retrieve data from the API.
        The retrieved data is then processed and transformed. The function adds a log source value, renames reserved Microsoft Sentinel column names, and outputs the results.
    .PARAMETER lastRunTime
        The last run time of the function. This parameter is optional.
    .PARAMETER cursor
        The cursor value for pagination. This parameter is optional.
    .PARAMETER api
        The API endpoint to retrieve data from. This parameter is optional.
    .OUTPUTS
        The function returns an array of results retrieved from the API.
    .EXAMPLE
        $results = Get-AuditLogs -lastRunTime "2022-01-01T00:00:00" -cursor "abc123" -api "https://api.example.com"

        This example retrieves data from the API with the specified last run time, cursor, and API endpoint.
    #>

    param (
        [Parameter(Mandatory = $false)]
        [string]$lastRunTime,

        [Parameter(Mandatory = $false)]
        [string]$cursor,

        [Parameter(Mandatory = $false)]
        [string]$api
    )

    $results = @()

    $headers = @{
        'Authorization' = "Bearer $env:APIKey"
        'ContentType'   = 'Application/Json'
    }

    if (!($cursor -or $cursor -eq "none")) {
        Write-Host "Processing Time Stamp"
        $payload = @{
            'start_time' = $lastRunTime
            'limit'      = 100
        }
    }
    else {
        Write-Host "Processing cursor"
        $payload = @{
            'cursor' = $cursor
        }
        Write-Verbose $payload
    }

    try {
        $uri = "$($env:apiEndpoint)/api/v1/$api"
        Do {
            $apiResponse = (Invoke-RestMethod -Method POST -Uri $uri -Headers $headers -body ($payload | ConvertTo-Json))
            $results += $apiResponse.items

            $payload = @{
                "cursor" = $apiResponse.cursor
            }
        } Until ($apiResponse.has_more -eq $false)

        # Add Log source value
        if ($results) {
            Write-Verbose "Adding Log Source '$($api)'"
            $results | add-member "log_source" -NotePropertyValue "$api"
        }
        #rename reserved Microsoft Sentinel column names [uuid and type]
        if ($results.uuid) {
            $results | ForEach-Object {
                $_ | add-member "uuid_s" -NotePropertyValue $_."uuid"
                $_.psobject.properties.remove("uuid")
            }
        }

        if ($results.type) {
            $results | ForEach-Object {
                $_ | add-member "action_type" -NotePropertyValue $_."type"
                $_.psobject.properties.remove("type")
            }
        }
        Write-Host "Results found: $($results.count)"
    }
    catch {
        # Write-Warning "Unable to connect to API [$($env:apiEndpoint)]"
    }
    if ($apiResponse.cursor) {
        Set-Cursor -cursor $api -cursorValue $apiResponse.cursor @storagePayload
    } else {
        Set-Cursor -cursor $api -cursorValue 'none' @storagePayload
    }


    return $results
}

Function Set-Cursor {
    <#
    .SYNOPSIS
        Sets the cursor value for a given cursor.
    .DESCRIPTION
        This function sets the cursor value for a given cursor. The cursor value is saved in a JSON file in the temp folder and then uploaded to Azure Blob Storage.
    .PARAMETER cursor
        The name of the cursor to set.
    .PARAMETER cursorValue
        The value to set the cursor to.
    .PARAMETER AzureWebJobsStorage
        The connection string for the Azure Blob Storage account.
    .PARAMETER storageAccountContainer
        The name of the container in the Azure Blob Storage account to store the cursor file in.
    .EXAMPLE
        Set-Cursor -cursor 'myCursor' -cursorValue '12345' -AzureWebJobsStorage $AzureWebJobsStorage -storageAccountContainer 'myContainer'
    #>
    param (
        [Parameter(Mandatory = $false)]
        [string]$cursor,

        [Parameter(Mandatory = $true)]
        [string]$cursorValue,

        [Parameter(Mandatory = $true)]
        [string]$AzureWebJobsStorage,

        [Parameter(Mandatory = $true)]
        [string]$storageAccountContainer
    )

    $body = @{
        "cursor" = $cursorValue
    }

    $body | ConvertTo-Json | Out-File "$env:temp\$cursor.json"

    try {
        Write-Verbose "Selecting Storage Context"
        $storageAccountContext = New-AzStorageContext -ConnectionString $AzureWebJobsStorage
    }
    catch {
        return 'Unable to connect to Storage Context'
    }

    Write-Verbose 'Saving new cursor'
    try {
        $null = Set-AzStorageBlobContent `
            -Blob "$cursor.json" `
            -Container $storageAccountContainer `
            -Context $storageAccountContext `
            -File "$env:temp\$cursor.json" `
            -Force
    }
    catch {
        return "Unable to create new $cursor"
    }
}

Function Get-Cursor {
    <#
    .SYNOPSIS
        Retrieves the cursor value from a JSON file stored in Azure Blob Storage.
    .DESCRIPTION
        This function retrieves the cursor value from a JSON file stored in Azure Blob Storage. The cursor value is used to keep track of the last processed event in the 1Password data connector.
    .PARAMETER AzureWebJobsStorage
        The connection string for the Azure Blob Storage account.
    .PARAMETER storageAccountContainer
        The name of the container in the Azure Blob Storage account where the JSON file is stored.
    .PARAMETER cursor
        The name of the JSON file containing the cursor value.
    .EXAMPLE
        Get-Cursor -AzureWebJobsStorage $AzureWebJobsStorage -storageAccountContainer "1password" -cursor "1password_cursor"
    .NOTES
        Author: Rogier Dijkman
    #>

    param (
        [Parameter(Mandatory = $true)]
        [string]$AzureWebJobsStorage,

        [Parameter(Mandatory = $true)]
        [string]$storageAccountContainer,

        [Parameter(Mandatory = $true)]
        [string]$cursor
    )

    $storageAccountContext = New-AzStorageContext -ConnectionString $AzureWebJobsStorage

    try {
        Write-Verbose "Get Blob Context"
        $blobContext = Get-AzStorageBlob `
            -Blob "$cursor.json" `
            -Container $storageAccountContainer `
            -Context $storageAccountContext
    }
    catch {
        Write-Output "Unable to access [$cursor.json]"
    }

    if (![string]::IsNullOrEmpty($blobContext)) {
        Write-Verbose "Get Blob File"
        try {
            $null = Get-AzStorageBlobContent `
                -Blob "$cursor.json" `
                -Container $storageAccountContainer `
                -Context $storageAccountContext `
                -Destination "$env:temp\$cursor.json" `
                -Force

            Write-Verbose "Get File Content"
            $lastRunAuditContext = Get-Content "$env:temp\$cursor.json" | ConvertFrom-Json
            if ($null -ne $lastRunAuditContext) {
                $cursorValue = ($lastRunAuditContext.cursor)
                return $cursorValue
            }
            else {
                Write-Warning "[!] No context was found for cursor [$cursor]"
                Set-TimeStamp -AzureWebJobsStorage $AzureWebJobsStorage -storageAccountContainer $storageAccountContainer
            }
        }
        catch {
            Write-Warning "[! An error has occured fetching the cursor for '$cursor']"
        }
    }
}

Function Send-Data {
    <#
    .SYNOPSIS
    Sends data to a specified endpoint using an Azure access token.
    .DESCRIPTION
    This function sends data to a specified endpoint using an Azure access token. The access token is obtained using the Get-AzAccessToken cmdlet.
    .PARAMETER body
    The data to be sent to the endpoint.
    .EXAMPLE
    $body = @{
        "key1" = "value1"
        "key2" = "value2"
    }
    Send-Data -body $body
    .NOTES
    This function requires the Get-AzAccessToken cmdlet to be installed. It also requires the $env:dataCollectionEndpoint environment variable to be set to the desired endpoint URL.
    #>
    param (
        [Parameter(Mandatory = $true)]
        [object]$body
    )

    $uri = "$env:dataCollectionEndpoint"
    $token = Get-AzAccessToken -ResourceUrl https://monitor.azure.com

    $requestHeader = @{
        "Token"          = ($token.token | ConvertTo-SecureString -AsPlainText -Force)
        "Authentication" = 'OAuth'
        "Method"         = 'POST'
        "ContentType"    = 'application/json'
    }

    try {
        Invoke-RestMethod -Uri "$uri" -Body $body @requestHeader
    } catch {
        Write-Warning "Unable to sent data. Validate if the account '$($token.UserId)' has Access to the Data Collection Rule"
    }

}

Function Set-TimeStamp {
    <#
    .SYNOPSIS
        Sets a timestamp for the last run of a function and saves it to Azure Storage Blob.
    .DESCRIPTION
        This function sets a timestamp for the last run of a function and saves it to Azure Storage Blob. If no previous timestamp is provided, the current timestamp is used. The timestamp is saved as a JSON file in the temp folder and then uploaded to the specified Azure Storage Blob container.
    .PARAMETER lastRun
        The timestamp of the last run of the function. If not provided, the current timestamp is used.
    .PARAMETER AzureWebJobsStorage
        The connection string for the Azure Storage Account.
    .PARAMETER storageAccountContainer
        The name of the Azure Storage Blob container where the timestamp file will be saved.
    .EXAMPLE
        Set-TimeStamp -AzureWebJobsStorage $AzureWebJobsStorage -storageAccountContainer $storageAccountContainer
    #>
    param (
        [Parameter(Mandatory = $false)]
        [string]$lastRun,

        [Parameter(Mandatory = $true)]
        [string]$AzureWebJobsStorage,

        [Parameter(Mandatory = $true)]
        [string]$storageAccountContainer
    )

    if ([string]::IsNullOrEmpty($lastRun)) {
        $lastRun = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
    } else {
        ([datetime]$lastRun).ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
    }

    $lastRunAudit = @{
        "lastRun" = $lastRun
    }

    $lastRunAudit | ConvertTo-Json | Out-File "$env:temp\timestamp.json"

    try {
        Write-Verbose "Selecting Storage Context"
        $storageAccountContext = New-AzStorageContext -ConnectionString $AzureWebJobsStorage
    }
    catch {
        return 'Unable to connect to Storage Context'
    }

    Write-Verbose 'Saving new timestamp'
    try {
        $null = Set-AzStorageBlobContent `
            -Blob "timestamp.json" `
            -Container $storageAccountContainer `
            -Context $storageAccountContext `
            -File "$env:temp\timestamp.json" `
            -Force
    }
    catch {
        return 'Unable to create new timestamp'
    }
    return $lastRun
}

Function Get-TimeStamp {
    <#
    .SYNOPSIS
        This function retrieves the timestamp of the last run of a script from a JSON file stored in an Azure Storage Account.
    .DESCRIPTION
        This function retrieves the timestamp of the last run of a script from a JSON file stored in an Azure Storage Account. If the JSON file is not found or is empty, the function sets the timestamp to the current time and writes it to the JSON file.
    .PARAMETER AzureWebJobsStorage
        The connection string for the Azure Storage Account.
    .PARAMETER storageAccountContainer
        The name of the container in the Azure Storage Account where the JSON file is stored.
    .EXAMPLE
        Get-TimeStamp -AzureWebJobsStorage $AzureWebJobsStorage -storageAccountContainer $storageAccountContainer
    #>
    param (
        [Parameter(Mandatory = $true)]
        [string]$AzureWebJobsStorage,

        [Parameter(Mandatory = $true)]
        [string]$storageAccountContainer
    )

    $storageAccountContext = New-AzStorageContext -ConnectionString $AzureWebJobsStorage

    $storageAccountContext = New-AzStorageContext -ConnectionString $AzureWebJobsStorage
    $blobs = Get-AzStorageBlob -Container $storageAccountContainer -Context $storageAccountContext | Select-Object Name
    if ($null -eq $blobs) {
        Set-TimeStamp @storagePayload
    }

    try {
        Write-Verbose "Get Blob Context"
        $blobContext = Get-AzStorageBlob `
            -Blob "timestamp.json" `
            -Container $storageAccountContainer `
            -Context $storageAccountContext
    }
    catch {
        Write-Host "Unable to access [timestamp.json]"
        $timestamp = Set-TimeStamp @storagePayload
    }

    if (![string]::IsNullOrEmpty($blobContext)) {
        Write-Verbose "Get Blob File"
        try {
            $null = Get-AzStorageBlobContent `
                -Blob "timestamp.json" `
                -Container $storageAccountContainer `
                -Context $storageAccountContext `
                -Destination "$env:temp\timestamp.json" `
                -Force

            Write-Verbose "Get File Content"
            $lastRunAuditContext = Get-Content "$env:temp\timestamp.json" | ConvertFrom-Json
            if ($null -ne $lastRunAuditContext) {
                $timestamp = ($lastRunAuditContext.lastRun).ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
            }
            else {
                $timestamp = Set-TimeStamp @storagePayload
            }
        }
        catch {
            $timestamp = Set-TimeStamp @storagePayload
        }
        return $timestamp
    }
}

Function Get-Variables {
    $global:storagePayload = @{
        'AzureWebJobsStorage'     = $env:AzureWebJobsStorage
        'storageAccountContainer' = "cursors"
    }
}
