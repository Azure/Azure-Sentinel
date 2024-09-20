<#  
    Title:          Okta Data Connector
    Language:       PowerShell
    Version:        1.2
    Author(s):      Microsoft
    Last Modified:  08/03/2020
    Comment:        Added Domain field to log record

    DESCRIPTION
    This Function App calls the Okta System Log API (https://developer.okta.com/docs/reference/api/system-log/) to pull the Okta System logs. The response from the Okta API is recieved in JSON format. This function will build the signature and authorization header 
    needed to post the data to the Log Analytics workspace via the HTTP Data Connector API. The Function App will post the Okta logs to the Okta_CL table in the Log Analytics workspace.
#>

# Input bindings are passed in via param block.
param($Timer)
# Get the current universal time in the default string format
$currentUTCtime = (Get-Date).ToUniversalTime()
# The 'IsPastDue' porperty is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}

# Build the headers for the Okta API request
$apiToken = $env:apiToken
$time = $env:timeInterval
$uri = $env:uri

$startDate = [System.DateTime]::UtcNow.AddMinutes(-$($time)).ToString("yyyy-MM-dd'T'HH:mm:sssZ")
$headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
$headers.Add("Content-Type", "application/json")
$headers.Add("Authorization", "SSWS $apiToken")
$response = Invoke-RestMethod -uri "$uri$($startDate)"  -Method 'GET' -Headers $headers -Body $body

# Define the Log Analytics Workspace ID and Key and Custom Table Name
$customerId = $env:workspaceId
$sharedKey =  $env:workspaceKey
$LogType = "Okta"
$TimeStampField = "DateValue"

# Function to create the authorization signature
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
    return $authorization
}

# Function to create and post the request
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

$recordCount = $response.Count

if ($recordCount -gt 0) {
    Write-Output "$recordCount record(s) are avaliable as of $startDate"
    $domain = [regex]::matches($uri, 'https:\/\/([\w\.\-]+)\/').captures.groups[1].value
    $response | Add-Member -MemberType NoteProperty -Name "Domain" -Value $domain
    $json = $response | ConvertTo-Json -Depth 5
    Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($json)) -logType $LogType  
}
else{

    Write-Output "No new Okta logs are avaliable as of $startDate"
}

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"

