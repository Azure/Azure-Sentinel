<#  
    Title:          Azure Function App TEMPLATE - <Data Source> API Ingestion to Azure Sentinel API 
    Language:       PowerShell
    Version:        1.0
    Last Modified:  5/15/2020
    Comment:        Inital Release

    DESCRIPTION:    The following PowerShell Function App code is a generic data connector to pull logs from your <Data Source> API, transform the data logs into a Azure Sentinel acceptable format (JSON) and POST the logs the 
                    Azure Sentil workspace via the Log Analytics Data Connector API.

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

# Define the application settings (environmental variables) for the Workspace ID, Workspace Key, <Data Source> API Key(s) or Token, URI, and/or Other variables. Reference (https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell#environment-variables)for more information 
$username = $env:apiUserName 
$password = $env:apiPassword
$uri = $env:uri

# The following variables are required by the Log Analytics Data Collector API functions below
$CustomerId = $env:workspaceId 
$SharedKey = $env:workspaceKey 
$TimeStampField = "DateValue"  
$LogType = $env:tableName      

<# Used this block to build the <Data Source> REQUEST header needed to call the API. Refer to the <Data Source> API Documentation.

    For example:
    $base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(("{0}:{1}" -f $username,$password)))
    $headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
    $headers.Add("au", "")
    $headers.Add("Authorization", "Basic " + $base64AuthInfo)

#>

<# Used this block to send a GET REQUEST to the <Data Source> API. Refer to the <Data Source> API Documentation.

    For example:
    $response = Invoke-RestMethod $uri -Method 'GET' -Headers $headers

#>

<# Used this block to transform the data recieved from the <Data Source> API into JSON format, which is acceptable format for the Log Anlaytics Data Collector API

    For example:
    $json = $response | ConvertTo-Json -Compress -Depth 3 

#>

# Required Function to build the Authorization signature for the Log Analytics Data Connector API. Reference: https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell#environment-variables
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

# Required Function to create and invoke an API POST request to the Log Analytics Data Connector API. Reference: https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-powershell#environment-variables
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
    $uri = "https://" + $customerId + ".ods.opinsights.azure.com" + $resource + "?api-version=2016-04-01"

    $headers = @{
        "Authorization" = $signature;
        "Log-Type" = $logType;
        "x-ms-date" = $rfc1123date;
        "time-generated-field" = $TimeStampField;
    }

    $response = Invoke-WebRequest -Uri $uri -Method $method -ContentType $contentType -Headers $headers -Body $body -UseBasicParsing
    return $response.StatusCode

}

<# Use this block to post the JSON formated data into Log Analytics via the Log Analytics Data Connector API

    For example:
    if($json.Length -gt 0) {
    Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($json)) -logType $LogType"
    }
    else {
        Write-Output "No records were found."
    }
            
#>

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"
