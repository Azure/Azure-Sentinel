<#  
    Title:          Proofpoint Targeted Attack Project (TAP) Data Connector
    Language:       PowerShell
    Version:        1.0
    Author(s):      Microsoft
    Last Modified:  5/12/2020
    Comment:        Inital Release

    DESCRIPTION
    This Function App calls the Proofpoint Targeted Attack Protection (TAP) API (https://help.proofpoint.com/Threat_Insight_Dashboard/API_Documentation/SIEM_API) to pull the Proofpoint
    Message Blocked, Message Delivered, Clicks Blocked, and Clicks Permitted logs. The response from the Proofpoint API is recieved in JSON format. This function will build the signature and authorization header 
    needed to post the data to the Log Analytics workspace via the HTTP Data Connector API. The Function App will post each log type to their individual tables in Log Analytics, for example,
    ProofPointMessageBlocked_CL, ProofPointMessageDelivered_CL, ProofPointClicksPermitted_CL, ProofPointClicksBlocked_CL.
#>

# Input bindings are passed in via param block.
param($Timer)
# Get the current universal time in the default string format
$currentUTCtime = (Get-Date).ToUniversalTime()
$logAnalyticsUri = $env:logAnalyticsUri

# The 'IsPastDue' property is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late! $($Timer.ScheduledStatus.Last)"
    
}

# Define the different ProofPoint Log Types. These values are set by the ProofPoint API and required to seperate the log types into the respective Log Analytics tables
$ProofPointlogTypes = @(
    "ClicksBlocked", 
    "ClicksPermitted",
    "MessagesBlocked", 
    "MessagesDelivered")

# Build the headers for the ProofPoint API request
$username = $env:apiUserName
$password = $env:apiPassword
$uri = $env:uri
$base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(("{0}:{1}" -f $username,$password)))
$headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
$headers.Add("au", "")
$headers.Add("Authorization", "Basic " + $base64AuthInfo)

# Invoke the API Request and assign the response to a variable ($response)
$response = Invoke-RestMethod $uri -Method 'GET' -Headers $headers

# Define the Log Analytics Workspace ID and Key
$CustomerId = $env:workspaceId
$SharedKey = $env:workspaceKey
$TimeStampField = "DateValue"

if ([string]::IsNullOrEmpty($logAnalyticsUri))
{
    $logAnalyticsUri = "https://" + $CustomerId + ".ods.opinsights.azure.com"
}

# Returning if the Log Analytics Uri is in incorrect format.
# Sample format supported: https://" + $customerId + ".ods.opinsights.azure.com
if($logAnalyticsUri -notmatch 'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$')
{
    throw "Proofpoint TAP: Invalid Log Analytics Uri."
}

# Function to build the Authorization signature for the Log Analytics Data Connector API
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

# Function to create and invoke an API POST request to the Log Analytics Data Connector API
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

    $response = Invoke-WebRequest -Uri $logAnalyticsUri -Method $method -ContentType $contentType -Headers $headers -Body $body -UseBasicParsing
    return $response.StatusCode

}
# Iterate through the ProofPoint API response and if there are log events present, POST the events to the Log Analytics API into the respective tables.
ForEach ($PPLogType in $ProofpointLogTypes) {
    if ($response.$PPLogType.Length -eq 0 ){ 
        Write-Host ("ProofPointTAP$($PPLogType) reported no new logs for the time interval configured.")
    }
    else {
        if($response.$PPLogType -eq $null) {                            # if the log entry is a null, this occurs on the last line of each LogType. Should only be one per log type
            Write-Host ("ProofPointTAP$($PPLogType) null line excluded")    # exclude it from being posted
        } else {            
            $json = $response.$PPLogType | ConvertTo-Json -Depth 3                # convert each log entry and post each entry to the Log Analytics API
            Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($json)) -logType "ProofPointTAP$($PPLogType)"
            }
        }
}
# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"
