<#  
    Title:          VMware Carbon Black Cloud - Endpoint Standard Data Connector
    Language:       PowerShell
    Version:        1.0
    Author:         Microsoft
    Last Modified:  5/19/2020
    Comment:        Inital Release

    DESCRIPTION
    This Function App calls the VMware Carbon Black Cloud - Endpoint Standard (formerly CB Defense) REST API (https://developer.carbonblack.com/reference/carbon-black-cloud/cb-defense/latest/rest-api/) to pull the Carbon Black
    Audit, Notification and Event logs. The response from the CarbonBlack API is recieved in JSON format. This function will build the signature and authorization header 
    needed to post the data to the Log Analytics workspace via the HTTP Data Connector API. The Function App will post each log type to their individual tables in Log Analytics, for example,
    CarbonBlackAuditLogs_CL, CarbonBlackNotifications_CL and CarbonBlackEvents_CL.
#>
# Input bindings are passed in via param block.
param($Timer)

# Get the current universal time in the default string format
$currentUTCtime = (Get-Date).ToUniversalTime()
$logAnalyticsUri = $env:logAnalyticsUri

# The 'IsPastDue' property is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}

# The function will call the Carbon Black API and retrieve the Audit, Event, and Notifications Logs
function CarbonBlackAPI()
{
    $workspaceId = $env:workspaceId
    $workspaceSharedKey = $env:workspaceKey
    $hostName = $env:uri
    $apiSecretKey = $env:apiKey
    $apiId = $env:apiId
    $SIEMapiKey = $env:SIEMapiKey
    $SIEMapiId = $env:SIEMapiId
    $time = $env:timeInterval
    $AuditLogTable = "CarbonBlackAuditLogs"
    $EventLogTable = "CarbonBlackEvents"
    $NotificationTable  = "CarbonBlackNotifications"

    $startTime = [System.DateTime]::UtcNow.AddMinutes(-$($time)).ToString("yyyy-MM-ddTHH:mm:ssZ")
    $now = [System.DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")

    if ([string]::IsNullOrEmpty($logAnalyticsUri))
    {
        $logAnalyticsUri = "https://" + $workspaceId + ".ods.opinsights.azure.com"
    }
    
    # Returning if the Log Analytics Uri is in incorrect format.
    # Sample format supported: https://" + $customerId + ".ods.opinsights.azure.com
    if($logAnalyticsUri -notmatch 'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$')
    {
        throw "VMware Carbon Black: Invalid Log Analytics Uri."
    }    

    $authHeaders = @{
        "X-Auth-Token" = "$($apiSecretKey)/$($apiId)"
    }
    $auditLogsResult = Invoke-RestMethod -Headers $authHeaders -Uri ([System.Uri]::new("$($hostName)/integrationServices/v3/auditlogs"))
    $eventsResult = Invoke-RestMethod -Headers $authHeaders -Uri ([System.Uri]::new("$($hostName)/integrationServices/v3/event?startTime=$($startTime)&endTime=$($now)"))

    if ($auditLogsResult.success -eq $true)
    {
        $AuditLogsJSON = $auditLogsResult.notifications | ConvertTo-Json -Depth 5
        if (-not([string]::IsNullOrWhiteSpace($AuditLogsJSON)))
        {
            Post-LogAnalyticsData -customerId $workspaceId -sharedKey $workspaceSharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($AuditLogsJSON)) -logType $AuditLogTable;
        }
        else
        {
            Write-Host "No new Carbon Black Audit Events as of $([DateTime]::UtcNow)"
        }
    }
    if ($eventsResult.success -eq $true)
    {
        $EventLogsJSON = $eventsResult.results | ConvertTo-Json -Depth 5
        if (-not([string]::IsNullOrWhiteSpace($EventLogsJSON)))
        {
            Post-LogAnalyticsData -customerId $workspaceId -sharedKey $workspaceSharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($EventLogsJSON)) -logType $EventLogTable;
        }
        else
        {
            Write-Host "No new Carbon Black Events as of $([DateTime]::UtcNow)"
        }
      }

    if($SIEMapiKey -eq '<Optional>' -or  $SIEMapiId -eq '<Optional>'  -or [string]::IsNullOrWhitespace($SIEMapiKey) -or  [string]::IsNullOrWhitespace($SIEMapiId))
    {   
         Write-Host "No SIEM API ID and/or Key value was defined."   
    }
    else
    {                
        $authHeaders = @{"X-Auth-Token" = "$($SIEMapiKey)/$($SIEMapiId)"}
        $notifications = Invoke-RestMethod -Headers $authHeaders -Uri ([System.Uri]::new("$($hostName)/integrationServices/v3/notification"))
        if ($notifications.success -eq $true)
        {                
            $NotifLogJson = $notifications.notifications | ConvertTo-Json -Depth 5       
            if (-not([string]::IsNullOrWhiteSpace($NotifLogJson)))
            {
                Post-LogAnalyticsData -customerId $workspaceId -sharedKey $workspaceSharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($NotifLogJson)) -logType $NotificationTable;
            }
            else
            {
                    Write-Host "No new Carbon Black Notifications as of $([DateTime]::UtcNow)"
            }
                 
        }      
    }    
}

# Create the function to create the authorization signature
function Build-Signature ($customerId, $sharedKey, $date, $contentLength, $method, $contentType, $resource)
{
    $xHeaders = "x-ms-date:" + $date;
    $stringToHash = $method + "`n" + $contentLength + "`n" + $contentType + "`n" + $xHeaders + "`n" + $resource;
    $bytesToHash = [Text.Encoding]::UTF8.GetBytes($stringToHash);
    $keyBytes = [Convert]::FromBase64String($sharedKey);
    $sha256 = New-Object System.Security.Cryptography.HMACSHA256;
    $sha256.Key = $keyBytes;
    $calculatedHash = $sha256.ComputeHash($bytesToHash);
    $encodedHash = [Convert]::ToBase64String($calculatedHash);
    $authorization = 'SharedKey {0}:{1}' -f $customerId,$encodedHash;
    return $authorization;
}

# Create the function to create and post the request
function Post-LogAnalyticsData($customerId, $sharedKey, $body, $logType)
{
    $TimeStampField = "DateValue"
    $method = "POST";
    $contentType = "application/json";
    $resource = "/api/logs";
    $rfc1123date = [DateTime]::UtcNow.ToString("r");
    $contentLength = $body.Length;
    $signature = Build-Signature -customerId $customerId -sharedKey $sharedKey -date $rfc1123date -contentLength $contentLength -method $method -contentType $contentType -resource $resource;
    $logAnalyticsUri = $logAnalyticsUri + $resource + "?api-version=2016-04-01"
    $headers = @{
        "Authorization" = $signature;
        "Log-Type" = $logType;
        "x-ms-date" = $rfc1123date;
        "time-generated-field" = $TimeStampField;
    };
    $response = Invoke-WebRequest -Body $body -Uri $logAnalyticsUri -Method $method -ContentType $contentType -Headers $headers -UseBasicParsing
    return $response.StatusCode
}

# Execute the Function to Pull CarbonBlack data and Post to the Log Analytics Workspace
CarbonBlackAPI

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"
