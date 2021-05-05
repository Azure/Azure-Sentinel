using namespace System.Net

# Input bindings are passed in via param block.
param($Request, $TriggerMetadata)


# The 'IsPastDue' porperty is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}

# param

$TimeStampField = (Get-Date)
$CustomerId = $env:workspaceId
$SharedKey = $env:workspaceKey
$LogType = $env:customLogName



# Create the function to create the authorization signature
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
 
# Create the function to create and post the request
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
#        "x-ms-AzureResourceId" = $resourceId;
    }
 
   # $response = Invoke-WebRequest -Uri $uri -Method $method -ContentType $contentType -Headers $headers -Body $body -UseBasicParsing
    #return $response.StatusCode

    $response = Invoke-WebRequest -Uri $uri -Method $method -ContentType $ContentType -Headers $headers -Body $body -UseBasicParsing
            Write-Verbose -message ('Post Function Return Code ' + $response)
            return $response
 
}

 Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($event)) -logType $logType  

Write-Host "PowerShell HTTP trigger function processed a request."
$currentUTCtime = (Get-Date).ToUniversalTime()
$headers = $Request.Headers
$event = $Request.Body

# Write logs to OMS Workspace
#$writeResult = Write-OMSLogfile $currentUTCtime $env:customLogName $event $env:workspaceId $env:workspaceKey

# Return Write-OMSLogfile response to output binding
Push-OutputBinding -Name Response -Value ([HttpResponseContext]@{
    StatusCode = $writeResult
    Body = ""
})


{Write-Host "Invalid Source"}
