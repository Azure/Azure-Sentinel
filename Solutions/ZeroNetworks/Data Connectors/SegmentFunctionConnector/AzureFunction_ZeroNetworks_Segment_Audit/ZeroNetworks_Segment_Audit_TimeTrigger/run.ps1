<#  
    Title:          Azure Function App Zero Networks Segment Audit API Ingestion to Azure Sentinel   
    Language:       PowerShell
    Version:        1.1
    Last Modified:  10/24/2022
    Comment:        Update product name

    DESCRIPTION:    The following PowerShell Function App code is a generic data connector to pull logs from your Zero Networks Segment Audit API, transform the data logs into a Azure Sentinel acceptable format (JSON) and POST the logs to the 
                    Azure Sentinel workspace using the Azure Log Analytics Data Collector API. Use this generic template and replace with specific code needed to authenticate to the Zero Networks Segment Audit API and format the data received into JSON format.  

#>

# Azure Function App Defaults:
# Input bindings are passed in via param block.
param($Timer)
# Get the current universal time in the default string format
$currentUTCtime = (Get-Date).ToUniversalTime()
# The 'IsPastDue' property is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late! $($Timer.ScheduledStatus.Last)"
}

# Define the application settings (environmental variables) for the Workspace ID, Workspace Key, Zero Networks Segment Audit API Key(s) or Token, URI, and/or Other variables. Reference (https://docs.microsoft.com/azure/azure-functions/functions-reference-powershell#environment-variables)for more information 
$apiToken = $env:apiToken
$uri = $env:uri


# The following variables are required by the Log Analytics Data Collector API functions below
$CustomerId = $env:workspaceId
$SharedKey = $env:workspaceKey
$TimeStampField = $env:TimeStampField
$LogType = $env:tableName     
$logAnalyticsUri = $env:logAnalyticsUri

if ([string]::IsNullOrEmpty($logAnalyticsUri))
{
    $logAnalyticsUri = "https://" + $customerId + ".ods.opinsights.azure.com"
}

# Returning if the Log Analytics Uri is in incorrect format.
# Sample format supported: https://" + $customerId + ".ods.opinsights.azure.com
if($logAnalyticsUri -notmatch 'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$')
{
    throw "Invalid Log Analytics Uri."
}

#Build Headers
$headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
$headers.Add("Authorization", $apiToken)

#Get the data
$now =  (Get-Date).ToUniversalTime()
$nowCursor = ([DateTimeOffset]$now).ToUnixTimeMilliseconds()
$ago = (Get-Date).AddMinutes(-5).ToUniversalTime()
$agoCursor = ([DateTimeOffset]$ago).ToUnixTimeMilliseconds() 
$url = $uri + "?_limit=400&order=desc&from=$agoCursor&to=$nowCursor"
$response = $null

$response = Invoke-RestMethod $url -Method 'GET' -Headers $headers
If($response.items.Count -ne 0){
    $allItems += $response.items
    [int64]$cursor = $response.scrollCursor
    $Logging = "Count: "+($response.Count)+" Items:"+$allItems.Count+" Cursor:"+$cursor+" AgoCursor:"+$agoCursor+" Delta:"+($agoCursor-$cursor)
    Write-Host $Logging
    do {
        $url = $uri + "?_limit=400&order=desc&from=$agoCursor&to=$nowCursor&_cursor=$cursor"
        $response = Invoke-RestMethod $url -Method 'GET' -Headers $headers
        $allItems += $response.items
        [int64]$cursor = $response.scrollCursor
        $Logging = "Count: "+($response.Count)+" Items:"+$allItems.Count+" Cursor:"+$cursor+" AgoCursor:"+$agoCursor+" Delta:"+($agoCursor-$cursor)
        Write-Host $Logging
    } until ($response.scrollCursor -eq "")
    $json = $allItems | ConvertTo-Json -Compress -Depth 10
}
else {
    Write-host "No new Audit logs"
}
# Required Function to build the Authorization signature for the Azure Log Analytics Data Collector API. Reference: https://docs.microsoft.com/azure/azure-monitor/platform/data-collector-api
Function Build-Signature ($customerId, $sharedKey, $date, $contentLength, $method, $contentType, $resource)
{
    $xHeaders = "x-ms-date:" + $date
    $stringToHash = $method + "`n" + $contentLength + "`n" + $contentType + "`n" + $xHeaders + "`n" + $resource

    $bytesToHash = [Text.Encoding]::UTF8.GetBytes($stringToHash)
    $keyBytes = [Convert]::FromBase64String($sharedKey)

    $sha256 = New-Object System.Security.Cryptography.HMACSHA256
    $sha256.Key = $keyBytes
    $calculatedHash = $sha256.ComputeHash($bytesToHash)
    $encodedHash = [Convert]::ToBase64String($calculatedHash)
    $authorization = 'SharedKey {0}:{1}' -f $customerId,$encodedHash
    
    # Dispose SHA256 from heap before return.
    $sha256.Dispose()

    return $authorization
}

# Required Function to create and invoke an API POST request to the Azure Log Analytics Data Collector API. References: https://docs.microsoft.com/azure/azure-monitor/platform/data-collector-api and https://docs.microsoft.com/azure/azure-functions/functions-reference-powershell#environment-variables
Function Post-LogAnalyticsData($customerId, $sharedKey, $body, $logType)
{
    $method = "POST"
    $contentType = "application/json"
    $resource = "/api/logs"
    $rfc1123date = [DateTime]::UtcNow.ToString("r")
    $contentLength = $body.Length
    $signature = Build-Signature `
        -customerId $customerId `
        -sharedKey $sharedKey `
        -date $rfc1123date `
        -contentLength $contentLength `
        -method $method `
        -contentType $contentType `
        -resource $resource
    
    $logAnalyticsUri = $logAnalyticsUri + $resource + "?api-version=2016-04-01"

    $headers = @{
        "Authorization" = $signature;
        "Log-Type" = $logType;
        "x-ms-date" = $rfc1123date;
        "time-generated-field" = $TimeStampField;
    }

    try {
        $response = Invoke-WebRequest -Uri $logAnalyticsUri -Method $method -ContentType $contentType -Headers $headers -Body $body -UseBasicParsing
    }
    catch {
        Write-Error "Error during sending logs to Azure Sentinel: $_.Exception.Message"
        # Exit out of context
        Exit
    }
    if ($response.StatusCode -eq 200) {
        Write-Host "Logs have been successfully sent to Azure Sentinel."
    }
    else {
        Write-Host "Error during sending logs to Azure Sentinel. Response code : $response.StatusCode"
    }

    return $response.StatusCode
}

if($json.Length -gt 0) {
    Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($json)) -logType $LogType
}
else {
    Write-Output "No records were found."
}

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"
